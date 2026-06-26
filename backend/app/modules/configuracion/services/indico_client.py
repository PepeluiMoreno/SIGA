"""Cliente HTTP para la integración con Indico (gestión de eventos).

Lee la configuración persistida (`funcion.indico.{activo,url,api_token}`) de la
tabla `configuraciones` y habla con la instancia Indico vía su API REST usando el
token personal como `Authorization: Bearer <token>` (Indico 3.x).

Entregable operativo y verificable por el usuario: `probar_conexion()` valida que
la URL es alcanzable y que el token autentica (golpea `/api/user/`). La creación de
eventos (`sincronizar_actividad`) queda como *best-effort* documentado: el endpoint
y el payload de creación dependen de la versión/categoría de la instancia destino,
así que debe validarse contra el Indico real antes de automatizar (no hay cron).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.configuracion import Configuracion

_GRUPO = "organizacion"
_K_ACTIVO = "funcion.indico.activo"
_K_URL = "funcion.indico.url"
_K_TOKEN = "funcion.indico.api_token"

_TIMEOUT = httpx.Timeout(10.0)


@dataclass
class ResultadoConexion:
    ok: bool
    mensaje: str


@dataclass
class _IndicoConfig:
    activo: bool
    url: str
    token: str


async def _leer_config(session: AsyncSession) -> _IndicoConfig:
    """Lee la config de Indico de `configuraciones` (token SIN enmascarar)."""
    rows = (await session.execute(
        select(Configuracion).where(
            Configuracion.grupo == _GRUPO,
            Configuracion.clave.in_([_K_ACTIVO, _K_URL, _K_TOKEN]),
        )
    )).scalars().all()
    cfg = {c.clave: c.get_valor() for c in rows}
    return _IndicoConfig(
        activo=bool(cfg.get(_K_ACTIVO)),
        url=(cfg.get(_K_URL) or "").strip().rstrip("/"),
        token=(cfg.get(_K_TOKEN) or "").strip(),
    )


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


class IndicoClient:
    """Cliente fino sobre la API REST de Indico, alimentado por la config persistida."""

    def __init__(self, cfg: _IndicoConfig):
        self._cfg = cfg

    @classmethod
    async def desde_config(cls, session: AsyncSession) -> "IndicoClient":
        return cls(await _leer_config(session))

    @property
    def activo(self) -> bool:
        return self._cfg.activo

    async def probar_conexion(self) -> ResultadoConexion:
        """Valida que la URL es alcanzable y que el token autentica."""
        if not self._cfg.url:
            return ResultadoConexion(False, "Falta la URL de Indico.")
        if not self._cfg.token:
            return ResultadoConexion(False, "Falta el API token de Indico.")
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
                # /api/user/ devuelve el usuario del token en Indico 3.x → valida auth.
                resp = await client.get(
                    f"{self._cfg.url}/api/user/", headers=_headers(self._cfg.token)
                )
                if resp.status_code == 200:
                    nombre = ""
                    try:
                        data = resp.json()
                        nombre = data.get("full_name") or data.get("name") or ""
                    except Exception:
                        pass
                    suf = f" (autenticado como {nombre})" if nombre else ""
                    return ResultadoConexion(True, f"Conexión correcta con Indico{suf}.")
                if resp.status_code in (401, 403):
                    return ResultadoConexion(False, "Indico responde pero el API token no es válido.")
                if resp.status_code == 404:
                    # Instancia alcanzable; endpoint distinto (versión antigua).
                    base = await client.get(self._cfg.url, headers=_headers(self._cfg.token))
                    if base.status_code < 500:
                        return ResultadoConexion(
                            True,
                            "Indico es alcanzable, pero no se pudo validar el token vía /api/user/ "
                            "(¿versión antigua?). Revisa el token si la sincronización falla.",
                        )
                return ResultadoConexion(False, f"Indico respondió con código {resp.status_code}.")
        except httpx.ConnectError:
            return ResultadoConexion(False, "No se pudo conectar con la URL de Indico.")
        except httpx.TimeoutException:
            return ResultadoConexion(False, "Tiempo de espera agotado al conectar con Indico.")
        except Exception as e:  # noqa: BLE001 — el mensaje va a la UI, no queremos 500
            return ResultadoConexion(False, f"Error al conectar con Indico: {e}")

    async def sincronizar_actividad(self, actividad) -> ResultadoConexion:
        """Crea/actualiza un evento en Indico a partir de una Actividad de SIGA.

        BEST-EFFORT, NO automatizado: el endpoint de creación y la categoría destino
        dependen de la instancia Indico. Construye el payload y lo deja preparado;
        validar contra el Indico real antes de habilitarlo en producción.
        """
        if not self._cfg.activo:
            return ResultadoConexion(False, "La integración con Indico está desactivada.")
        payload = {
            "title": actividad.nombre,
            "description": actividad.descripcion or "",
            "start_dt": actividad.fecha_inicio.isoformat() if actividad.fecha_inicio else None,
            "end_dt": (actividad.fecha_fin or actividad.fecha_inicio).isoformat()
            if (actividad.fecha_fin or actividad.fecha_inicio) else None,
            "location_name": actividad.lugar or "",
        }
        # Pendiente de validar contra la instancia real (endpoint/categoría/versión).
        return ResultadoConexion(
            False,
            "Sincronización de eventos pendiente de validar contra la instancia Indico "
            f"(payload listo: {payload['title']}).",
        )
