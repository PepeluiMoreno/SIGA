"""Endpoints públicos de recogida de firmas (formulario web externo).

  POST /api/publico/firmas              → registra una firma (doble opt-in)
  GET  /api/publico/firmas/verificar    → confirma la firma vía token del email
  GET  /api/publico/firmas/contador/{id}→ nº de firmas verificadas (para el front)

Defensa anti-abuso: captcha (server-side) + honeypot + rate-limit por IP y email.
No requiere autenticación; es la ÚNICA superficie de escritura pública.
"""
from __future__ import annotations

import re
import uuid
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.captcha import verificar_captcha
from app.core.database import get_db
from app.core.documento import validar_nif
from app.core.ratelimit import limiter_firmas_email, limiter_firmas_ip
from app.modules.actividades.services.firma_publica_service import (
    EstadoVerificacion,
    FirmaPublicaService,
)

router = APIRouter(prefix="/api/publico/firmas", tags=["publico-firmas"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class FirmaPublicaIn(BaseModel):
    # Se firma sobre una ACTIVIDAD de recogida de firmas. Se mantiene
    # campania_id por compatibilidad; debe llegar al menos uno de los dos.
    actividad_id: Optional[uuid.UUID] = None
    campania_id: Optional[uuid.UUID] = None
    nombre: str = Field(min_length=1, max_length=100)
    apellidos: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=200)
    codigo_postal: Optional[str] = Field(default=None, max_length=20)
    pais_id: Optional[uuid.UUID] = None
    # NIF (DNI/NIE): identidad fuerte por la que se desduplica el firmante. Es
    # opcional para admitir firmantes extranjeros sin NIF (dedup blanda por
    # nombre). Si se aporta, se valida la letra de control server-side.
    documento: Optional[str] = Field(default=None, max_length=255)
    tipo_documento: Optional[str] = Field(default="DNI", max_length=20)
    acepta_terminos: bool = False
    acepta_comunicaciones: bool = False
    captcha_token: str = Field(default="", max_length=4000)
    # Honeypot: debe llegar vacío. Si los bots lo rellenan, se descarta en silencio.
    website: str = ""


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@router.post("", summary="Registrar una firma (doble opt-in)")
async def registrar_firma(
    datos: FirmaPublicaIn,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    ip = _client_ip(request)

    # 1. Honeypot: respondemos como si todo fuera bien, sin almacenar nada.
    if datos.website:
        return {"estado": "pendiente_verificacion",
                "mensaje": "Firma registrada. Revisa tu correo para confirmarla."}

    # 2. Validaciones básicas de entrada.
    email = datos.email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Email no válido.")
    if not datos.acepta_terminos:
        raise HTTPException(status_code=422, detail="Debes aceptar los términos para firmar.")
    if datos.actividad_id is None and datos.campania_id is None:
        raise HTTPException(status_code=422, detail="Falta la actividad de recogida de firmas.")
    # Si aporta NIF, debe ser válido (DNI/NIE). Sin NIF se admite (extranjero).
    if datos.documento and datos.documento.strip() and not validar_nif(datos.documento):
        raise HTTPException(status_code=422, detail="El NIF (DNI/NIE) no es válido.")

    # 3. Rate-limit (segunda barrera tras el captcha).
    if not limiter_firmas_ip.permitido(ip):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtalo más tarde.")
    if not limiter_firmas_email.permitido(email):
        raise HTTPException(status_code=429, detail="Demasiados intentos para este correo.")

    # 4. Captcha server-side.
    if not await verificar_captcha(datos.captcha_token, ip):
        raise HTTPException(status_code=400, detail="Verificación anti-bot fallida.")

    # 5. Alta.
    service = FirmaPublicaService(session)
    resultado = await service.registrar_firma(
        actividad_id=datos.actividad_id,
        campania_id=datos.campania_id,
        nombre=datos.nombre,
        apellidos=datos.apellidos,
        email=email,
        codigo_postal=datos.codigo_postal,
        pais_id=datos.pais_id,
        documento=datos.documento,
        tipo_documento=datos.tipo_documento,
        acepta_comunicaciones=datos.acepta_comunicaciones,
        ip_origen=ip,
    )
    return {"estado": resultado.estado.value, "mensaje": resultado.mensaje}


@router.get("/verificar", summary="Confirmar firma desde el enlace del email")
async def verificar_firma(
    token: str,
    session: AsyncSession = Depends(get_db),
):
    service = FirmaPublicaService(session)
    resultado = await service.verificar_firma(token)

    # Si hay página de gracias configurada, redirigimos con el estado en la URL.
    if resultado.redirect_url:
        sep = "&" if "?" in resultado.redirect_url else "?"
        destino = f"{resultado.redirect_url}{sep}{urlencode({'firma': resultado.estado.value})}"
        return RedirectResponse(url=destino, status_code=303)

    ok = resultado.estado in (EstadoVerificacion.VERIFICADA, EstadoVerificacion.YA_VERIFICADA)
    html = f"<!doctype html><html lang='es'><meta charset='utf-8'>" \
           f"<title>Confirmación de firma</title>" \
           f"<body style='font-family:sans-serif;max-width:40rem;margin:4rem auto;text-align:center'>" \
           f"<h1>{'✔ Firma confirmada' if ok else 'No se pudo confirmar'}</h1>" \
           f"<p>{resultado.mensaje}</p></body></html>"
    return HTMLResponse(content=html, status_code=200 if ok else 400)


@router.get("/actividades", summary="Actividades de recogida de firmas activas (para el desplegable)")
async def listar_actividades(
    session: AsyncSession = Depends(get_db),
):
    """Lista pública (solo lectura) de actividades de recogida de firmas web
    **activas** (iniciadas y no cerradas) cuya campaña incluye en su métrica la
    recogida de firmas. La consume el formulario externo (WordPress) para
    ofrecerlas en un desplegable y no tener que pegar el UUID a mano. Solo
    expone id, nombre y la campaña, datos ya públicos del formulario."""
    service = FirmaPublicaService(session)
    actividades = await service.listar_actividades_firmas_activas()
    return [
        {
            "id": str(a.id),
            "nombre": a.nombre,
            "campania_id": str(a.campania_id) if a.campania_id else None,
            "campania": a.campania.nombre if a.campania is not None else None,
        }
        for a in actividades
    ]


@router.get("/pagina/{actividad_id}", summary="Contenido de la página pública de una recogida de firmas")
async def contenido_pagina(
    actividad_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Contenido (público) para fabricar la página de la recogida en WordPress:
    título, lema, imagen, descripción, manifiesto, destinatario, aviso RGPD, PDF
    y texto para compartir. El plugin lo usa para generar la landing con el
    formulario `[siga_firmas]`. Los textos/imagen salen de la publicación web de
    la actividad y, si faltan, se heredan de su campaña."""
    service = FirmaPublicaService(session)
    contenido = await service.contenido_pagina(actividad_id)
    if contenido is None:
        raise HTTPException(status_code=404, detail="Recogida de firmas no disponible.")
    return contenido


@router.get("/contador/{campania_id}", summary="Nº de firmas verificadas de una campaña")
async def contador_firmas(
    campania_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    service = FirmaPublicaService(session)
    total = await service.contar_firmas_verificadas(campania_id)
    return {"campania_id": str(campania_id), "firmas": total}
