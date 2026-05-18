"""Endpoints REST para integración PayPal.

POST /api/paypal/create-order          → crea orden PayPal
POST /api/paypal/capture-order/{id}    → captura pago aprobado
POST /api/paypal/webhook               → recibe eventos PayPal

Documentación PayPal:
  https://developer.paypal.com/docs/api/orders/v2/
"""
import json
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.economico.services.paypal_service import PayPalService

router = APIRouter(prefix="/api/paypal", tags=["paypal"])


# ─── Schemas de request ──────────────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    importe: float
    concepto: str
    moneda: str = "EUR"
    cuota_id: Optional[UUID] = None
    miembro_id: Optional[UUID] = None


class CaptureOrderRequest(BaseModel):
    cuota_id: Optional[UUID] = None
    miembro_id: Optional[UUID] = None
    cuenta_bancaria_id: Optional[UUID] = None


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/create-order", summary="Crear orden de pago PayPal")
async def create_order(
    body: CreateOrderRequest,
    session=Depends(get_db),
):
    """
    Crea una orden en PayPal y devuelve el order_id para el botón JS de PayPal.

    El frontend usa este order_id para inicializar el SDK de PayPal:
    ```js
    paypal.Buttons({ createOrder: () => order_id }).render('#paypal-button')
    ```
    """
    service = PayPalService(session)
    try:
        order = await service.crear_order(
            importe=Decimal(str(body.importe)),
            concepto=body.concepto,
            moneda=body.moneda,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error PayPal: {e}")

    return {
        "order_id": order["id"],
        "status": order["status"],
        "links": order.get("links", []),
    }


@router.post("/capture-order/{order_id}", summary="Capturar pago aprobado")
async def capture_order(
    order_id: str,
    body: CaptureOrderRequest,
    session=Depends(get_db),
):
    """
    Captura el pago tras la aprobación del pagador.
    Si se proporciona cuenta_bancaria_id, genera ApunteCaja y asiento contable.
    """
    service = PayPalService(session)
    try:
        order_data = await service.capturar_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error PayPal: {e}")

    estado = order_data.get("status")
    if estado != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=f"El pago no se completó correctamente. Estado: {estado}",
        )

    pago = await service.registrar_pago_capturado(
        order_data=order_data,
        cuota_id=body.cuota_id,
        miembro_id=body.miembro_id,
        cuenta_bancaria_id=body.cuenta_bancaria_id,
    )

    return {
        "pago_id": str(pago.id),
        "order_id": order_id,
        "status": estado,
        "importe": str(pago.importe),
        "moneda": pago.moneda,
    }


@router.post("/webhook", summary="Recibir eventos webhook de PayPal", status_code=200)
async def paypal_webhook(
    request: Request,
    session=Depends(get_db),
):
    """
    Receptor de webhooks de PayPal. PayPal envía aquí los eventos de pago.

    Eventos procesados:
      - PAYMENT.CAPTURE.COMPLETED  → pago confirmado
      - PAYMENT.CAPTURE.DENIED     → pago denegado
      - PAYMENT.CAPTURE.REVERSED   → devolución
      - BILLING.SUBSCRIPTION.CANCELLED → suscripción cancelada

    Configurar en PayPal Dashboard → Apps & Credentials → Webhooks.
    URL: https://tu-dominio.com/api/paypal/webhook
    """
    body_raw = await request.body()
    try:
        body_parsed = json.loads(body_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Body inválido")

    service = PayPalService(session)

    # Verificar firma del webhook
    headers = dict(request.headers)
    es_valido = await service.verificar_webhook(
        headers=headers,
        body_raw=body_raw,
        body_parsed=body_parsed,
    )
    if not es_valido:
        raise HTTPException(status_code=401, detail="Firma de webhook inválida")

    # Persistir evento para auditoría
    proveedor = await service._obtener_o_crear_proveedor_paypal()
    evento_tipo = body_parsed.get("event_type", "")
    await service.registrar_evento_webhook(proveedor.id, evento_tipo, body_parsed)

    # Procesar eventos relevantes
    if evento_tipo == "PAYMENT.CAPTURE.COMPLETED":
        resource = body_parsed.get("resource", {})
        capture_id = resource.get("id")
        # El pago ya fue capturado vía /capture-order.
        # El webhook es redundante pero útil para reconciliación.
        pass

    elif evento_tipo == "PAYMENT.CAPTURE.REVERSED":
        # Una devolución: en un sistema completo se registraría
        # un ApunteCaja de GASTO para revertir el ingreso.
        pass

    return {"received": True, "event_type": evento_tipo}
