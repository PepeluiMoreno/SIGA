"""Verificación de captcha para endpoints públicos (anti-bot).

Soporta Cloudflare Turnstile (por defecto) y hCaptcha; ambos comparten el
mismo contrato de `siteverify`. El secreto se lee de Settings (env / orquestador).

Si no hay secreto configurado, `verificar_captcha` devuelve False salvo que se
active explícitamente el modo desarrollo (`captcha_provider == "disabled"`),
para que un despliegue mal configurado no quede abierto por accidente.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_ENDPOINTS = {
    "turnstile": "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    "hcaptcha": "https://api.hcaptcha.com/siteverify",
}


async def verificar_captcha(token: Optional[str], ip_remota: Optional[str] = None) -> bool:
    """Valida el token del captcha contra el proveedor configurado.

    Devuelve True solo si el proveedor confirma el reto. Falla cerrado:
    sin secreto o sin token → False (excepto modo 'disabled' explícito).
    """
    settings = get_settings()
    proveedor = (settings.captcha_provider or "turnstile").lower()

    if proveedor == "disabled":
        logger.warning("Captcha DESACTIVADO (captcha_provider='disabled'). Solo para desarrollo.")
        return True

    if not settings.captcha_secret:
        logger.error("Captcha sin secreto configurado (captcha_secret vacío). Se rechaza el envío.")
        return False

    if not token:
        return False

    endpoint = _ENDPOINTS.get(proveedor)
    if not endpoint:
        logger.error("Proveedor de captcha desconocido: %s", proveedor)
        return False

    data = {"secret": settings.captcha_secret, "response": token}
    if ip_remota:
        data["remoteip"] = ip_remota

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(endpoint, data=data)
            resp.raise_for_status()
            payload = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.error("Error verificando captcha (%s): %s", proveedor, exc)
        return False

    ok = bool(payload.get("success"))
    if not ok:
        logger.info("Captcha rechazado: %s", payload.get("error-codes"))
    return ok
