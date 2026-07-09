"""Endpoints públicos de pago de cuota por el socio (enlace tokenizado).

  GET  /api/publico/pago-cuota?token=…            → datos de la cuota a pagar
  POST /api/publico/pago-cuota/crear-orden        → crea la orden PayPal (importe del servidor)
  POST /api/publico/pago-cuota/capturar           → captura el pago y liquida la cuota

El token llega en el enlace del email de aviso (o desde el área del socio). No
requiere autenticación: el token firmado ES la autorización, y solo permite
pagar (nunca leer datos de otros ni alterar importes). Rate-limit por IP.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.ratelimit import limiter_pago_cuota_ip
from app.modules.economico.services.pago_cuota_publica_service import (
    PagoCuotaPublicaService,
)

router = APIRouter(prefix="/api/publico/pago-cuota", tags=["publico-pago-cuota"])


class CrearOrdenIn(BaseModel):
    token: str = Field(min_length=10, max_length=4000)


class CapturarIn(BaseModel):
    token: str = Field(min_length=10, max_length=4000)
    order_id: str = Field(min_length=1, max_length=64)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


def _rate_limit(request: Request) -> None:
    if not limiter_pago_cuota_ip.permitido(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtalo más tarde.")


@router.get("", summary="Datos de la cuota a pagar (desde el enlace del email)")
async def info_pago(
    token: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    _rate_limit(request)
    service = PagoCuotaPublicaService(session)
    try:
        info = await service.info(token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # El client-id de PayPal es público por diseño (va en la URL del SDK JS);
    # exponerlo aquí evita duplicar configuración en el frontend.
    from app.modules.economico.services.paypal_service import (
        PAYPAL_CLIENT_ID, PAYPAL_MODE,
    )
    return {
        "ejercicio": info.ejercicio,
        "nombre_socio": info.nombre_socio,
        "importe_total": str(info.importe_total),
        "importe_pagado": str(info.importe_pagado),
        "pendiente": str(info.pendiente),
        "pagada": info.pagada,
        "paypal_client_id": PAYPAL_CLIENT_ID or "",
        "paypal_mode": PAYPAL_MODE,
    }


@router.post("/crear-orden", summary="Crear la orden PayPal por el pendiente de la cuota")
async def crear_orden(
    body: CrearOrdenIn,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    _rate_limit(request)
    service = PagoCuotaPublicaService(session)
    try:
        return await service.crear_orden(body.token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # error de pasarela
        raise HTTPException(status_code=502, detail=f"Error PayPal: {exc}")


@router.post("/capturar", summary="Capturar el pago aprobado y liquidar la cuota")
async def capturar(
    body: CapturarIn,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    _rate_limit(request)
    service = PagoCuotaPublicaService(session)
    try:
        return await service.capturar(body.token, body.order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # error de pasarela
        raise HTTPException(status_code=502, detail=f"Error PayPal: {exc}")
