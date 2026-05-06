"""Servicio de reset de contraseña.

Responsabilidades:
  - Generar y almacenar token de un solo uso (30 min de validez)
  - Rate limiting por email: mínimo 5 min entre solicitudes
  - Validar token y aplicar nueva contraseña
  - Construir y enviar el email mediante EmailService
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email_service import EmailService
from app.core.security import hash_password
from app.core.config import get_settings
from app.modules.acceso.models.usuario import Usuario

_TOKEN_TTL_MINUTOS = 30
_COOLDOWN_MINUTOS  = 5   # tiempo mínimo entre solicitudes del mismo usuario


def _ahora() -> datetime:
    return datetime.utcnow()


def _html_reset(nombre: str, url: str, ttl: int) -> str:
    return f"""
    <p>Hola{' ' + nombre if nombre else ''},</p>
    <p>Has solicitado restablecer tu contraseña en SIGA.
       Haz clic en el enlace siguiente (válido durante {ttl} minutos):</p>
    <p><a href="{url}" style="padding:10px 20px;background:#7c3aed;color:#fff;
       border-radius:6px;text-decoration:none;font-weight:bold;">
       Restablecer contraseña</a></p>
    <p>Si no lo solicitaste, ignora este mensaje. Tu contraseña no cambiará.</p>
    <p style="color:#9ca3af;font-size:12px;">
       El enlace expirará el {(_ahora() + timedelta(minutes=ttl)).strftime('%d/%m/%Y %H:%M')} UTC.
    </p>
    """


class PasswordResetService:
    """Orquesta el flujo completo de olvido y restablecimiento de contraseña."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._email   = EmailService(session)

    async def solicitar_reset(self, email: str) -> None:
        """Genera un token y envía el email de reset.

        Silencia errores de "email no encontrado" para no revelar qué emails
        existen en el sistema. Sí lanza si el SMTP no está configurado.
        """
        usuario = await self._buscar_usuario_activo(email)
        if usuario is None:
            # No revelar si el email existe — simplemente no hacer nada
            return

        ahora = _ahora()

        # Rate limiting: no generar token si ya hay uno reciente
        if (
            usuario.reset_token_solicitado_en
            and ahora - usuario.reset_token_solicitado_en < timedelta(minutes=_COOLDOWN_MINUTOS)
        ):
            raise ValueError(
                f"Ya se envió un enlace recientemente. "
                f"Espera {_COOLDOWN_MINUTOS} minutos antes de solicitarlo de nuevo."
            )

        token = secrets.token_urlsafe(48)
        usuario.reset_token              = token
        usuario.reset_token_expira_en    = ahora + timedelta(minutes=_TOKEN_TTL_MINUTOS)
        usuario.reset_token_solicitado_en = ahora
        await self._session.flush()

        settings  = get_settings()
        reset_url = f"{settings.app_url}/reset-password?token={token}"

        await self._email.enviar(
            destinatario=email,
            asunto="Restablecer contraseña — SIGA",
            cuerpo_html=_html_reset('', reset_url, _TOKEN_TTL_MINUTOS),
            cuerpo_texto=(
                f"Para restablecer tu contraseña visita: {reset_url}\n"
                f"El enlace expira en {_TOKEN_TTL_MINUTOS} minutos."
            ),
        )

    async def confirmar_reset(self, token: str, nueva_password: str) -> None:
        """Valida el token y aplica la nueva contraseña.

        Raises:
            ValueError: token inválido, expirado o ya usado.
        """
        if len(nueva_password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")

        usuario = await self._buscar_por_token(token)
        if usuario is None or not usuario.reset_token_expira_en:
            raise ValueError("El enlace de restablecimiento es inválido o ha expirado.")

        if _ahora() > usuario.reset_token_expira_en:
            raise ValueError("El enlace de restablecimiento ha expirado. Solicita uno nuevo.")

        usuario.password_hash              = hash_password(nueva_password)
        usuario.reset_token                = None
        usuario.reset_token_expira_en      = None
        usuario.reset_token_solicitado_en  = None
        await self._session.flush()

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    async def _buscar_usuario_activo(self, email: str) -> Optional[Usuario]:
        result = await self._session.execute(
            select(Usuario).where(
                Usuario.email == email,
                Usuario.activo == True,    # noqa: E712
                Usuario.eliminado == False,
            )
        )
        return result.scalar_one_or_none()

    async def _buscar_por_token(self, token: str) -> Optional[Usuario]:
        result = await self._session.execute(
            select(Usuario).where(
                Usuario.reset_token == token,
                Usuario.eliminado == False,
            )
        )
        return result.scalar_one_or_none()
