"""Endpoints públicos de auto-alta de socios (formulario web externo).

  POST /api/publico/socios            → registra una solicitud de alta (doble opt-in)
  GET  /api/publico/socios/verificar  → confirma la solicitud vía token del email
  GET  /api/publico/socios/config     → catálogos para el formulario (países, agrupaciones)

Defensa anti-abuso: captcha (server-side) + honeypot + rate-limit por IP y email.
No requiere autenticación; junto a firmas, es superficie de escritura pública.
Al confirmar el email la solicitud entra en la bandeja de secretaría
(``solicitudes_socio_pendientes``) para su aprobación definitiva.
"""
from __future__ import annotations

import re
import uuid
from datetime import date
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.captcha import verificar_captcha
from app.core.database import get_db
from app.core.documento import validar_iban, validar_nif
from app.core.ratelimit import limiter_socios_email, limiter_socios_ip
from app.modules.membresia.services.solicitud_socio_publica_service import (
    EstadoVerificacion,
    SolicitudSocioPublicaService,
)

router = APIRouter(prefix="/api/publico/socios", tags=["publico-socios"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SolicitudSocioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido1: str = Field(min_length=1, max_length=100)
    apellido2: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(min_length=3, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=30)
    # Documento (DNI/NIE): opcional para admitir extranjeros. Si se aporta, se valida.
    documento: Optional[str] = Field(default=None, max_length=255)
    tipo_documento: Optional[str] = Field(default="DNI", max_length=20)
    pais_documento_id: Optional[uuid.UUID] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = Field(default=None, max_length=20)
    direccion: Optional[str] = Field(default=None, max_length=255)
    codigo_postal: Optional[str] = Field(default=None, max_length=20)
    localidad: Optional[str] = Field(default=None, max_length=120)
    provincia_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    agrupacion_id: Optional[uuid.UUID] = None
    # Datos de domiciliación (opcionales; el tesorero los completa/valida al aprobar).
    iban: Optional[str] = Field(default=None, max_length=40)
    swift_bic: Optional[str] = Field(default=None, max_length=11)
    forma_pago_id: Optional[uuid.UUID] = None
    acepta_terminos: bool = False
    acepta_comunicaciones: bool = False
    captcha_token: str = Field(default="", max_length=4000)
    # Honeypot: debe llegar vacío. Si un bot lo rellena, se descarta en silencio.
    website: str = ""


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@router.post("", summary="Registrar una solicitud de alta de socio (doble opt-in)")
async def registrar_solicitud(
    datos: SolicitudSocioIn,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    ip = _client_ip(request)

    # 1. Honeypot: respondemos como si todo fuera bien, sin almacenar nada.
    if datos.website:
        return {"estado": "pendiente_verificacion",
                "mensaje": "Solicitud registrada. Revisa tu correo para confirmarla."}

    # 2. Validaciones básicas de entrada.
    email = datos.email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Email no válido.")
    if not datos.acepta_terminos:
        raise HTTPException(status_code=422, detail="Debes aceptar los términos para solicitar el alta.")
    if datos.documento and datos.documento.strip() and not validar_nif(datos.documento):
        raise HTTPException(status_code=422, detail="El NIF (DNI/NIE) no es válido.")
    if datos.iban and datos.iban.strip() and not validar_iban(datos.iban):
        raise HTTPException(status_code=422, detail="El IBAN no es válido.")

    # 3. Rate-limit (segunda barrera tras el captcha).
    if not limiter_socios_ip.permitido(ip):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtalo más tarde.")
    if not limiter_socios_email.permitido(email):
        raise HTTPException(status_code=429, detail="Demasiados intentos para este correo.")

    # 4. Captcha server-side.
    if not await verificar_captcha(datos.captcha_token, ip):
        raise HTTPException(status_code=400, detail="Verificación anti-bot fallida.")

    # 5. Alta de la solicitud.
    service = SolicitudSocioPublicaService(session)
    resultado = await service.registrar_solicitud(
        nombre=datos.nombre, apellido1=datos.apellido1, apellido2=datos.apellido2,
        email=email, telefono=datos.telefono, documento=datos.documento,
        tipo_documento=datos.tipo_documento, pais_documento_id=datos.pais_documento_id,
        fecha_nacimiento=datos.fecha_nacimiento, sexo=datos.sexo,
        direccion=datos.direccion, codigo_postal=datos.codigo_postal,
        localidad=datos.localidad, provincia_id=datos.provincia_id,
        pais_domicilio_id=datos.pais_domicilio_id, agrupacion_id=datos.agrupacion_id,
        iban=datos.iban, swift_bic=datos.swift_bic, forma_pago_id=datos.forma_pago_id,
        acepta_comunicaciones=datos.acepta_comunicaciones, ip_origen=ip,
    )
    return {"estado": resultado.estado.value, "mensaje": resultado.mensaje}


@router.get("/verificar", summary="Confirmar la solicitud desde el enlace del email")
async def verificar_solicitud(
    token: str,
    session: AsyncSession = Depends(get_db),
):
    service = SolicitudSocioPublicaService(session)
    resultado = await service.verificar_solicitud(token)

    if resultado.redirect_url:
        sep = "&" if "?" in resultado.redirect_url else "?"
        destino = f"{resultado.redirect_url}{sep}{urlencode({'alta_socio': resultado.estado.value})}"
        return RedirectResponse(url=destino, status_code=303)

    ok = resultado.estado in (EstadoVerificacion.VERIFICADA, EstadoVerificacion.YA_VERIFICADA)
    html = (
        f"<!doctype html><html lang='es'><meta charset='utf-8'>"
        f"<title>Confirmación de solicitud</title>"
        f"<body style='font-family:sans-serif;max-width:40rem;margin:4rem auto;text-align:center'>"
        f"<h1>{'✔ Solicitud confirmada' if ok else 'No se pudo confirmar'}</h1>"
        f"<p>{resultado.mensaje}</p></body></html>"
    )
    return HTMLResponse(content=html, status_code=200 if ok else 400)


@router.get("/config", summary="Catálogos para el formulario de alta (países y agrupaciones)")
async def config_formulario(session: AsyncSession = Depends(get_db)):
    """Datos públicos que necesita el formulario externo: países (para documento y
    domicilio) y agrupaciones territoriales activas (para el desplegable). Solo
    lectura; expone id/nombre, datos ya públicos del formulario."""
    from app.modules.core.geografico.direccion import Pais, UnidadOrganizativa

    paises = (await session.execute(
        select(Pais.id, Pais.codigo, Pais.nombre)
        .where(Pais.activo.is_(True))
        .order_by(Pais.nombre)
    )).all()
    agrupaciones = (await session.execute(
        select(UnidadOrganizativa.id, UnidadOrganizativa.nombre)
        .where(UnidadOrganizativa.activo.is_(True))
        .order_by(UnidadOrganizativa.nombre)
    )).all()
    return {
        "paises": [{"id": str(i), "codigo": c, "nombre": n} for i, c, n in paises],
        "agrupaciones": [{"id": str(i), "nombre": n} for i, n in agrupaciones],
    }
