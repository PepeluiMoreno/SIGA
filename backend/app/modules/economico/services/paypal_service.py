"""Integración con PayPal REST API v2.

Flujo:
  1. Frontend llama POST /api/paypal/create-order → recibe order_id de PayPal
  2. Frontend muestra el botón de PayPal SDK con ese order_id
  3. Socio aprueba el pago en PayPal
  4. Frontend llama POST /api/paypal/capture-order/{order_id}
  5. Backend captura, registra Pago + ApunteCaja + Asiento contable
  6. PayPal envía webhooks a POST /api/paypal/webhook (verificados con firma)

Requiere variables de entorno:
  PAYPAL_CLIENT_ID     — Client ID de la app PayPal
  PAYPAL_CLIENT_SECRET — Secret de la app PayPal
  PAYPAL_MODE          — "sandbox" | "live"
  PAYPAL_WEBHOOK_ID    — ID del webhook configurado en el Dashboard PayPal
"""
import hashlib
import hmac
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.economico.models.cobro import ProveedorPago, Pago, EventoPago
from app.modules.economico.models.tesoreria import TipoApunte, OrigenApunte
from app.modules.economico.services.tesoreria_service import TesoreriaService
from app.modules.economico.services.registro_contable import RegistroContable


PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID", "")

_BASE_URL = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live":    "https://api-m.paypal.com",
}


class PayPalService:
    """Cliente para la API REST de PayPal v2."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.base_url = _BASE_URL.get(PAYPAL_MODE, _BASE_URL["sandbox"])

    # ─── Auth ─────────────────────────────────────────────────────────────────

    async def _get_access_token(self) -> str:
        """Obtiene un access token OAuth2 de PayPal."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                data={"grant_type": "client_credentials"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    async def _headers(self) -> dict:
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    # ─── Orders API v2 ────────────────────────────────────────────────────────

    async def crear_order(
        self,
        importe: Decimal,
        concepto: str,
        moneda: str = "EUR",
        return_url: str = "https://siga.intramuros.org/paypal/return",
        cancel_url: str = "https://siga.intramuros.org/paypal/cancel",
    ) -> dict:
        """Crea una orden de pago en PayPal. Devuelve el objeto order completo."""
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": moneda,
                        "value": str(importe),
                    },
                    "description": concepto[:127],  # PayPal max 127 chars
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "brand_name": "Intramuros Jerez",
                "locale": "es-ES",
                "user_action": "PAY_NOW",
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                headers=await self._headers(),
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

    async def capturar_order(self, order_id: str) -> dict:
        """Captura el pago de una orden aprobada por el pagador."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers=await self._headers(),
                json={},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

    async def obtener_order(self, order_id: str) -> dict:
        """Consulta el estado de una orden PayPal."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v2/checkout/orders/{order_id}",
                headers=await self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()

    # ─── Webhook verification ─────────────────────────────────────────────────

    async def verificar_webhook(
        self,
        headers: dict,
        body_raw: bytes,
        body_parsed: dict,
    ) -> bool:
        """Verifica la autenticidad de un webhook de PayPal usando la API de verificación."""
        payload = {
            "auth_algo":         headers.get("PAYPAL-AUTH-ALGO", ""),
            "cert_url":          headers.get("PAYPAL-CERT-URL", ""),
            "transmission_id":   headers.get("PAYPAL-TRANSMISSION-ID", ""),
            "transmission_sig":  headers.get("PAYPAL-TRANSMISSION-SIG", ""),
            "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME", ""),
            "webhook_id":        PAYPAL_WEBHOOK_ID,
            "webhook_event":     body_parsed,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                headers=await self._headers(),
                json=payload,
                timeout=10,
            )
            if resp.status_code != 200:
                return False
            return resp.json().get("verification_status") == "SUCCESS"

    # ─── Registro en SIGA ─────────────────────────────────────────────────────

    async def _obtener_o_crear_proveedor_paypal(self) -> ProveedorPago:
        result = await self.session.execute(
            select(ProveedorPago).where(ProveedorPago.nombre == "PayPal")
        )
        proveedor = result.scalars().first()
        if not proveedor:
            proveedor = ProveedorPago(nombre="PayPal", descripcion="Pasarela de pago PayPal")
            self.session.add(proveedor)
            await self.session.commit()
            await self.session.refresh(proveedor)
        return proveedor

    async def registrar_pago_capturado(
        self,
        order_data: dict,
        cuota_id: Optional[UUID] = None,
        miembro_id: Optional[UUID] = None,
        cuenta_bancaria_id: Optional[UUID] = None,
    ) -> Pago:
        """Registra en SIGA un pago capturado correctamente en PayPal.

        Crea:
          - Registro Pago en la tabla pagos
          - ApunteCaja (si se proporciona cuenta_bancaria_id)
          - AsientoContable automático (versión COMPLETA)
        """
        proveedor = await self._obtener_o_crear_proveedor_paypal()

        # Extraer datos de la capture
        capture = (
            order_data.get("purchase_units", [{}])[0]
            .get("payments", {})
            .get("captures", [{}])[0]
        )
        importe_str = capture.get("amount", {}).get("value", "0")
        moneda = capture.get("amount", {}).get("currency_code", "EUR")
        capture_id = capture.get("id", "")
        order_id = order_data.get("id", "")
        email_pagador = (
            order_data.get("payer", {}).get("email_address")
        )

        pago = Pago(
            proveedor_id=proveedor.id,
            importe=Decimal(importe_str),
            moneda=moneda,
            email_pagador=email_pagador,
            miembro_id=miembro_id,
            id_externo_principal=order_id,
            id_externo_secundario=capture_id,
            datos_externos=order_data,
            fecha_completado=datetime.utcnow(),
        )
        self.session.add(pago)
        await self.session.commit()
        await self.session.refresh(pago)

        # Registrar apunte en tesorería si hay cuenta bancaria configurada
        if cuenta_bancaria_id:
            concepto = (
                order_data.get("purchase_units", [{}])[0]
                .get("description", "Pago PayPal")
            )
            tesoreria = TesoreriaService(self.session)
            apunte = await tesoreria.registrar_apunte(
                cuenta_id=cuenta_bancaria_id,
                fecha=datetime.utcnow().date(),
                importe=Decimal(importe_str),
                tipo=TipoApunte.INGRESO,
                concepto=concepto,
                origen=OrigenApunte.PAGO,
                referencia_externa=order_id,
            )
            # Asiento contable automático
            registro = RegistroContable(self.session)
            await registro.generar_asiento_para_apunte(apunte)

        return pago

    async def registrar_evento_webhook(
        self, proveedor_id: UUID, evento_tipo: str, payload: dict
    ) -> None:
        """Persiste un evento webhook de PayPal para auditoría."""
        evento = EventoPago(
            proveedor_id=proveedor_id,
            id_evento_externo=payload.get("id"),
            payload=payload,
        )
        self.session.add(evento)
        await self.session.commit()
