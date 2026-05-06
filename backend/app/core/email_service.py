"""Servicio de envío de email vía SMTP asíncrono.

Carga la configuración SMTP desde la tabla de configuraciones en cada envío,
de modo que los cambios en parámetros se aplican sin reiniciar el servidor.
"""
from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.configuracion.models.configuracion import Configuracion

logger = logging.getLogger(__name__)


class SmtpConfig:
    def __init__(self, cfg: dict) -> None:
        self.host     = cfg.get('smtp.host', '')
        self.port     = int(cfg.get('smtp.port', '587') or '587')
        self.usuario  = cfg.get('smtp.usuario', '')
        self.password = cfg.get('smtp.password', '')
        self.from_    = cfg.get('smtp.from', '') or self.usuario
        self.tls      = str(cfg.get('smtp.tls', 'true')).lower() == 'true'
        self.ssl      = str(cfg.get('smtp.ssl', 'false')).lower() == 'true'

    @property
    def configured(self) -> bool:
        return bool(self.host and self.from_)


async def _load_smtp_config(session: AsyncSession) -> SmtpConfig:
    result = await session.execute(
        select(Configuracion).where(Configuracion.clave.like('smtp.%'))
    )
    cfg = {c.clave: c.valor for c in result.scalars()}
    return SmtpConfig(cfg)


class EmailService:
    """Servicio de email. Instanciar por request con la sesión DB activa."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def enviar(
        self,
        *,
        destinatario: str,
        asunto: str,
        cuerpo_html: str,
        cuerpo_texto: Optional[str] = None,
    ) -> None:
        """Envía un email.

        Raises:
            RuntimeError: si SMTP no está configurado o el envío falla.
        """
        config = await _load_smtp_config(self._session)
        if not config.configured:
            raise RuntimeError(
                "El servidor SMTP no está configurado. "
                "Configúralo en Parámetros Generales → Autenticación y Email."
            )

        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From']    = config.from_
        msg['To']      = destinatario

        if cuerpo_texto:
            msg.attach(MIMEText(cuerpo_texto, 'plain', 'utf-8'))
        msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))

        try:
            await aiosmtplib.send(
                msg,
                hostname=config.host,
                port=config.port,
                username=config.usuario or None,
                password=config.password or None,
                use_tls=config.ssl,
                start_tls=config.tls and not config.ssl,
            )
            logger.info("Email enviado a %s — asunto: %s", destinatario, asunto)
        except Exception as exc:
            logger.error("Error enviando email a %s: %s", destinatario, exc)
            raise RuntimeError(f"Error al enviar el email: {exc}") from exc
