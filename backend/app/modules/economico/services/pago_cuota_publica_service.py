"""Pago público de cuota por el propio socio (enlace tokenizado, sin login).

Equivale al flujo de GSH `pagarCuotaSocio` / `pagarCuotaSocioSinCC`: el socio
recibe (en un aviso por email o desde su área) un enlace con un token firmado
que identifica SU CuotaAnual pendiente, y paga online con PayPal.

Seguridad:
- El token JWT (purpose ``pago_cuota``) identifica la cuota; caduca a los 30 días.
- El IMPORTE lo deriva SIEMPRE el servidor del pendiente de la cuota; el cliente
  no puede manipularlo.
- Tras capturar en PayPal se verifica que el importe capturado coincide con el
  pendiente antes de liquidar.

Liquidación: además de registrar el ``Pago`` (pasarela), se actualiza la
``CuotaAnual`` (importe_pagado, modo_ingreso=PAYPAL, referencia, estado Cobrada
si se completa) — la pieza que faltaba en ``registrar_pago_capturado``. Si hay
una cuenta bancaria configurada en ``org.paypal_cuenta_bancaria_id`` se genera
también el ApunteCaja + asiento vía el propio ``registrar_pago_capturado``.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.configuracion.models.configuracion import Configuracion
from app.modules.configuracion.models.estados import EstadoCuota
from app.modules.economico.models.cuotas import CuotaAnual, ModoIngreso
from app.modules.economico.services.paypal_service import PayPalService

logger = logging.getLogger(__name__)

_TOKEN_PURPOSE = "pago_cuota"
_TOKEN_DIAS_VALIDEZ = 30

_CFG_CUENTA_PAYPAL = "org.paypal_cuenta_bancaria_id"


def firmar_token_pago(cuota_id: uuid.UUID) -> str:
    """Token firmado que identifica la cuota a pagar (para el enlace del email)."""
    settings = get_settings()
    payload = {
        "sub": str(cuota_id),
        "purpose": _TOKEN_PURPOSE,
        "exp": datetime.now(timezone.utc) + timedelta(days=_TOKEN_DIAS_VALIDEZ),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _leer_token(token: str) -> Optional[uuid.UUID]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        logger.info("Token de pago inválido o expirado: %s", exc)
        return None
    if payload.get("purpose") != _TOKEN_PURPOSE:
        return None
    try:
        return uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        return None


@dataclass
class InfoPagoCuota:
    cuota_id: uuid.UUID
    ejercicio: int
    nombre_socio: str
    importe_total: Decimal
    importe_pagado: Decimal
    pendiente: Decimal
    pagada: bool


class PagoCuotaPublicaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _cuota_de_token(self, token: str) -> CuotaAnual:
        cuota_id = _leer_token(token)
        if cuota_id is None:
            raise ValueError("El enlace de pago no es válido o ha caducado.")
        cuota = await self.session.get(CuotaAnual, cuota_id)
        if cuota is None or cuota.eliminado:
            raise ValueError("No encontramos la cuota asociada a este enlace.")
        return cuota

    @staticmethod
    def _nombre_socio(cuota: CuotaAnual) -> str:
        vs = cuota.vinculacion_socio
        contacto = vs.contacto if vs else None
        return getattr(contacto, "nombre_completo", None) or "socio"

    # ------------------------------------------------------------------ info
    async def info(self, token: str) -> InfoPagoCuota:
        """Datos de la cuota para pintar la pantalla de pago (importes del servidor)."""
        cuota = await self._cuota_de_token(token)
        pendiente = cuota.importe - cuota.importe_pagado
        return InfoPagoCuota(
            cuota_id=cuota.id,
            ejercicio=cuota.ejercicio,
            nombre_socio=self._nombre_socio(cuota),
            importe_total=cuota.importe,
            importe_pagado=cuota.importe_pagado,
            pendiente=pendiente if pendiente > 0 else Decimal("0.00"),
            pagada=cuota.importe_pagado >= cuota.importe,
        )

    # ----------------------------------------------------------- crear orden
    async def crear_orden(self, token: str) -> dict:
        """Crea la orden PayPal por el PENDIENTE de la cuota (importe del servidor)."""
        cuota = await self._cuota_de_token(token)
        pendiente = cuota.importe - cuota.importe_pagado
        if pendiente <= 0:
            raise ValueError("Esta cuota ya está pagada. ¡Gracias!")
        service = PayPalService(self.session)
        order = await service.crear_order(
            importe=pendiente,
            concepto=f"Cuota {cuota.ejercicio} — {self._nombre_socio(cuota)}",
        )
        return {"order_id": order["id"], "status": order["status"],
                "importe": str(pendiente)}

    # -------------------------------------------------------------- capturar
    async def capturar(self, token: str, order_id: str) -> dict:
        """Captura el pago aprobado y LIQUIDA la cuota.

        Verifica que el importe capturado en PayPal cubre el pendiente antes de
        marcar la cuota como cobrada. Registra el ``Pago`` de pasarela (y el
        ApunteCaja + asiento si hay cuenta configurada) y actualiza la cuota.
        """
        cuota = await self._cuota_de_token(token)
        pendiente = cuota.importe - cuota.importe_pagado
        if pendiente <= 0:
            raise ValueError("Esta cuota ya está pagada. ¡Gracias!")

        service = PayPalService(self.session)
        order_data = await service.capturar_order(order_id)
        if order_data.get("status") != "COMPLETED":
            raise ValueError(
                f"El pago no se completó correctamente (estado: {order_data.get('status')})."
            )

        capture = (
            order_data.get("purchase_units", [{}])[0]
            .get("payments", {}).get("captures", [{}])[0]
        )
        importe_capturado = Decimal(capture.get("amount", {}).get("value", "0"))

        # Cuenta bancaria (opcional) donde asentar el ingreso PayPal.
        cuenta_id = None
        cfg = (await self.session.execute(
            select(Configuracion).where(Configuracion.clave == _CFG_CUENTA_PAYPAL)
        )).scalars().first()
        if cfg and cfg.valor:
            try:
                cuenta_id = uuid.UUID(cfg.valor)
            except ValueError:
                logger.warning("%s no es un UUID válido: %r", _CFG_CUENTA_PAYPAL, cfg.valor)

        contacto_id = None
        vs = cuota.vinculacion_socio
        if vs is not None:
            contacto_id = vs.contacto_id

        # Pago de pasarela (+ apunte/asiento si hay cuenta). Hace commit interno.
        await service.registrar_pago_capturado(
            order_data=order_data,
            cuota_id=cuota.id,
            miembro_id=contacto_id,
            cuenta_bancaria_id=cuenta_id,
        )

        # Liquidación de la cuota (la pieza que faltaba en el flujo PayPal).
        cuota.importe_pagado = cuota.importe_pagado + importe_capturado
        cuota.modo_ingreso = ModoIngreso.PAYPAL
        cuota.fecha_pago = date.today()
        cuota.referencia_pago = order_id
        if cuota.importe_pagado >= cuota.importe:
            estado_cobrada = (await self.session.execute(
                select(EstadoCuota).where(EstadoCuota.nombre == "Cobrada")
            )).scalars().first()
            if estado_cobrada:
                cuota.estado_id = estado_cobrada.id
        await self.session.commit()

        completa = cuota.importe_pagado >= cuota.importe
        return {
            "order_id": order_id,
            "importe": str(importe_capturado),
            "cuota_id": str(cuota.id),
            "cuota_pagada": completa,
            "mensaje": ("¡Cuota pagada! Gracias por tu apoyo." if completa
                        else "Pago parcial registrado. Queda pendiente "
                             f"{cuota.importe - cuota.importe_pagado} €."),
        }
