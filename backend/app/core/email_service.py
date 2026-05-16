"""Servicio de envío de email vía SMTP asíncrono.

Carga la configuración SMTP desde la tabla de configuraciones en cada envío,
de modo que los cambios en parámetros se aplican sin reiniciar el servidor.
"""
from __future__ import annotations

import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.configuracion.models.configuracion import Configuracion
from app.core.config import get_settings

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
        self.fuente   = cfg.get('_fuente', 'bd')

    @property
    def configured(self) -> bool:
        return bool(self.host and self.usuario and self.password and self.from_)

    @property
    def campos_faltantes(self) -> list[str]:
        """Lista de parámetros SMTP obligatorios que faltan."""
        faltantes = []
        if not self.host:
            faltantes.append('smtp.host (servidor SMTP)')
        if not self.usuario:
            faltantes.append('smtp.usuario (usuario/login SMTP)')
        if not self.password:
            faltantes.append('smtp.password (contraseña SMTP)')
        if not self.from_:
            faltantes.append('smtp.from o smtp.usuario (dirección remitente)')
        return faltantes


def _smtp_config_from_env() -> Optional[SmtpConfig]:
    """Construye SmtpConfig desde variables de entorno si smtp_host está definido."""
    s = get_settings()
    if not s.smtp_host:
        return None
    enc = s.smtp_encryption.lower()
    return SmtpConfig({
        'smtp.host':     s.smtp_host,
        'smtp.port':     str(s.smtp_port),
        'smtp.usuario':  s.smtp_username,
        'smtp.password': s.smtp_password,
        'smtp.from':     s.smtp_from or s.smtp_username,
        'smtp.tls':      'true' if enc == 'tls' else 'false',
        'smtp.ssl':      'true' if enc == 'ssl' else 'false',
        '_fuente':       'env',
    })


async def _load_smtp_config(session: AsyncSession) -> SmtpConfig:
    """Prioridad: .env / secreto del orquestador > tabla configuracion en BD."""
    env_cfg = _smtp_config_from_env()
    if env_cfg is not None:
        logger.debug("SMTP config cargada desde variables de entorno")
        return env_cfg

    result = await session.execute(
        select(Configuracion).where(Configuracion.clave.like('smtp.%'))
    )
    cfg = {c.clave: c.valor for c in result.scalars()}
    logger.debug("SMTP config cargada desde BD")
    return SmtpConfig(cfg)


async def ping_smtp(config: SmtpConfig, timeout: float = 5.0) -> str:
    """Conecta y envía EHLO sin autenticar. Devuelve 'ok', 'timeout' o 'error'."""
    try:
        smtp = aiosmtplib.SMTP(
            hostname=config.host,
            port=config.port,
            use_tls=config.ssl,
            timeout=timeout,
        )
        await asyncio.wait_for(smtp.connect(), timeout=timeout)
        if config.tls and not config.ssl:
            await asyncio.wait_for(smtp.starttls(), timeout=timeout)
        await smtp.quit()
        return 'ok'
    except asyncio.TimeoutError:
        return 'timeout'
    except Exception as exc:
        logger.debug("SMTP ping fallido: %s", exc)
        return 'error'


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
            faltantes = config.campos_faltantes
            detalle = ', '.join(faltantes) if faltantes else 'parámetros incompletos'
            raise ValueError(
                f"El servidor SMTP no está configurado. "
                f"Faltan: {detalle}. "
                f"Configúralo en Parámetros Generales → Autenticación y Email."
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
            raise ValueError(f"Error al enviar el email: {exc}") from exc
