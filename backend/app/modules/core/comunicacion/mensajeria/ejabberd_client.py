"""Cliente de la API ReST de ejabberd.

SIGA administra ejabberd (crear salas MUC, gestionar afiliaciones, provisionar
cuentas) vía su API ReST autenticada con bearer token de scope `ejabberd:admin`.
Ver docs/DISENO_CHAT_INTERNO.md §6 y la doc oficial de ejabberd (mod_http_api).

⚠️ VERIFICACIÓN PENDIENTE (no probado contra un ejabberd real):
  - Nombres y parámetros exactos de los comandos pueden variar según versión de
    ejabberd y módulos habilitados (mod_muc_admin, mod_admin_extra). Los usados
    aquí siguen la API estándar documentada, pero deben confirmarse en pruebas.
  - La emisión de token de usuario (`sasl_auth`) sin contraseña del usuario está
    PENDIENTE de verificar (ver §7 del diseño); este cliente deja el hueco pero
    no asume que funcione.

Configuración esperada (parámetros de SIGA, a añadir en configuracion):
  chat.ejabberd_api_url   p. ej. http://ejabberd:5280/api
  chat.ejabberd_admin_token  bearer token con scope ejabberd:admin
  chat.xmpp_dominio       dominio XMPP, p. ej. "siga.local"
  chat.muc_servicio       servicio MUC, p. ej. "conference.siga.local"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class EjabberdError(Exception):
    """Fallo al hablar con la API de ejabberd."""


@dataclass
class EjabberdConfig:
    api_url: str
    admin_token: str
    dominio: str
    muc_servicio: str

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.admin_token and self.dominio and self.muc_servicio)


class EjabberdClient:
    """Cliente fino sobre la API ReST de ejabberd.

    Cada método mapea un comando de la API. Las respuestas de ejabberd para
    comandos sin retorno suelen ser `0` (éxito) o un objeto de error.
    """

    def __init__(self, config: EjabberdConfig, timeout: float = 10.0) -> None:
        self._cfg = config
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._cfg.admin_token}"}

    async def _call(self, command: str, payload: dict[str, Any]) -> Any:
        """Invoca POST {api_url}/{command} con JSON. Lanza EjabberdError si falla."""
        if not self._cfg.configured:
            raise EjabberdError("ejabberd no configurado")
        url = f"{self._cfg.api_url.rstrip('/')}/{command}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(url, json=payload, headers=self._headers())
        except httpx.HTTPError as exc:
            raise EjabberdError(f"error de red al llamar {command}: {exc}") from exc
        if resp.status_code >= 400:
            raise EjabberdError(f"{command} devolvió {resp.status_code}: {resp.text[:300]}")
        try:
            return resp.json()
        except ValueError:
            return resp.text

    # ── Salas MUC ─────────────────────────────────────────────────────────

    async def crear_sala(self, nombre_sala: str, *, persistente: bool = True) -> None:
        """Crea una sala MUC. `nombre_sala` es la parte local (sin @servicio).

        Comando ejabberd: create_room (y opcionalmente change_room_option para
        persistencia/miembros-solo). VERIFICAR opciones exactas en pruebas.
        """
        await self._call("create_room", {
            "name": nombre_sala,
            "service": self._cfg.muc_servicio,
            "host": self._cfg.dominio,
        })
        if persistente:
            # Sala persistente y solo-miembros (la afiliación la controla SIGA).
            for option, value in (("persistent", "true"), ("members_only", "true")):
                await self._call("change_room_option", {
                    "name": nombre_sala,
                    "service": self._cfg.muc_servicio,
                    "option": option,
                    "value": value,
                })

    async def destruir_sala(self, nombre_sala: str) -> None:
        await self._call("destroy_room", {
            "name": nombre_sala,
            "service": self._cfg.muc_servicio,
        })

    async def set_afiliacion(self, nombre_sala: str, jid_usuario: str, afiliacion: str) -> None:
        """Da o quita acceso de un usuario a la sala.

        afiliacion: 'member' (acceso), 'none' (quitar), 'admin', 'owner', 'outcast'.
        Comando ejabberd: set_room_affiliation.
        """
        await self._call("set_room_affiliation", {
            "name": nombre_sala,
            "service": self._cfg.muc_servicio,
            "jid": jid_usuario,
            "affiliation": afiliacion,
        })

    # ── Cuentas de usuario (provisión) ────────────────────────────────────

    async def usuario_existe(self, localpart: str) -> bool:
        res = await self._call("check_account", {
            "user": localpart, "host": self._cfg.dominio,
        })
        # check_account devuelve 0 si existe, 1 si no.
        return res == 0

    async def crear_usuario(self, localpart: str, password: str) -> None:
        await self._call("register", {
            "user": localpart, "host": self._cfg.dominio, "password": password,
        })

    async def eliminar_usuario(self, localpart: str) -> None:
        await self._call("unregister", {
            "user": localpart, "host": self._cfg.dominio,
        })

    # ── Token de login del usuario (PENDIENTE de verificar) ───────────────

    async def emitir_token_usuario(self, localpart: str, ttl_segundos: int = 31536000) -> str:
        """Emite un token XMPP (scope sasl_auth) para que el usuario haga login
        sin contraseña vía SASL X-OAUTH2.

        ⚠️ PENDIENTE: confirmar que oauth_issue_token (o equivalente) permite emitir
        un token sasl_auth para OTRO usuario desde el lado admin, sin que ese
        usuario teclee su contraseña. Si no fuera posible, el plan B es provisionar
        contraseña por usuario (gestionada por SIGA) — ver §7 del diseño.
        """
        raise NotImplementedError(
            "emitir_token_usuario: pendiente de verificar el flujo sasl_auth admin "
            "contra un ejabberd real (ver docs/DISENO_CHAT_INTERNO.md §7)."
        )
