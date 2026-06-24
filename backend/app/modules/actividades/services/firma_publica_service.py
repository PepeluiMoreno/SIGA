"""Servicio de recogida pública de firmas de campaña (formulario web externo).

Flujo:
  1. registrar_firma(): valida que la campaña admite firmas, hace upsert del
     Contacto (persona física) por email, crea la Participacion (tipo FIRMA) y su
     satélite FirmaCampania como NO verificada y envía un correo de doble opt-in
     con un token firmado.
  2. verificar_firma(): valida el token y marca la firma como verificada.

El registro de personas y el consentimiento viven SIEMPRE aquí (SIGA es la
fuente única). WordPress solo presenta el formulario y reenvía los datos.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.email_service import EmailService
from app.modules.actividades.models.campana import Campania, FirmaCampania
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.participacion import Participacion

logger = logging.getLogger(__name__)

_TOKEN_PURPOSE = "firma_verify"
_TOKEN_HORAS_VALIDEZ = 72


class EstadoRegistro(str, Enum):
    PENDIENTE_VERIFICACION = "pendiente_verificacion"
    YA_FIRMADA_PENDIENTE = "ya_firmada_pendiente"
    YA_VERIFICADA = "ya_verificada"
    CAMPANIA_NO_DISPONIBLE = "campania_no_disponible"


class EstadoVerificacion(str, Enum):
    VERIFICADA = "verificada"
    YA_VERIFICADA = "ya_verificada"
    TOKEN_INVALIDO = "token_invalido"
    NO_ENCONTRADA = "no_encontrada"


@dataclass
class ResultadoRegistro:
    estado: EstadoRegistro
    mensaje: str


@dataclass
class ResultadoVerificacion:
    estado: EstadoVerificacion
    mensaje: str
    redirect_url: Optional[str] = None


def _firmar_token(firma_id: uuid.UUID) -> str:
    settings = get_settings()
    payload = {
        "sub": str(firma_id),
        "purpose": _TOKEN_PURPOSE,
        "exp": datetime.now(timezone.utc) + timedelta(hours=_TOKEN_HORAS_VALIDEZ),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _leer_token(token: str) -> Optional[uuid.UUID]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        logger.info("Token de firma inválido o expirado: %s", exc)
        return None
    if payload.get("purpose") != _TOKEN_PURPOSE:
        return None
    try:
        return uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        return None


class FirmaPublicaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------ alta
    async def registrar_firma(
        self,
        *,
        campania_id: uuid.UUID,
        nombre: str,
        apellidos: str,
        email: str,
        codigo_postal: Optional[str] = None,
        pais_id: Optional[uuid.UUID] = None,
        documento: Optional[str] = None,
        tipo_documento: Optional[str] = None,
        acepta_comunicaciones: bool = False,
        ip_origen: Optional[str] = None,
    ) -> ResultadoRegistro:
        email = email.strip().lower()

        campania = await self._campania_abierta(campania_id)
        if campania is None:
            return ResultadoRegistro(
                EstadoRegistro.CAMPANIA_NO_DISPONIBLE,
                "La campaña no existe o ya no admite firmas.",
            )

        contacto = await self._upsert_contacto(
            nombre=nombre,
            apellidos=apellidos,
            email=email,
            codigo_postal=codigo_postal,
            pais_id=pais_id,
            documento=documento,
            tipo_documento=tipo_documento,
            acepta_comunicaciones=acepta_comunicaciones,
        )

        firma = await self._firma_existente(campania.id, contacto.id)
        if firma is not None:
            if firma.verificado:
                return ResultadoRegistro(
                    EstadoRegistro.YA_VERIFICADA,
                    "Esta dirección ya ha firmado y verificado esta campaña.",
                )
            # Reenviamos el correo de verificación de la firma pendiente.
            await self._enviar_email_verificacion(contacto, campania, firma)
            return ResultadoRegistro(
                EstadoRegistro.YA_FIRMADA_PENDIENTE,
                "Ya había una firma pendiente. Te hemos reenviado el correo de confirmación.",
            )

        # Modelo CRM: la firma es el satélite de una Participacion (tipo FIRMA)
        # del Contacto que firma.
        participacion = Participacion(
            contacto_id=contacto.id, tipo="FIRMA", estado="registrada",
        )
        self.session.add(participacion)
        await self.session.flush()

        firma = FirmaCampania(
            participacion_id=participacion.id,
            campania_id=campania.id,
            contacto_id=contacto.id,
            acepta_terminos=True,
            verificado=False,
            ip_origen=(ip_origen or "")[:50] or None,
        )
        self.session.add(firma)
        await self.session.flush()  # obtener firma.id antes de firmar el token

        await self._enviar_email_verificacion(contacto, campania, firma)
        await self.session.commit()

        return ResultadoRegistro(
            EstadoRegistro.PENDIENTE_VERIFICACION,
            "Firma registrada. Revisa tu correo para confirmarla.",
        )

    # ----------------------------------------------------------- verificación
    async def verificar_firma(self, token: str) -> ResultadoVerificacion:
        settings = get_settings()
        redirect = settings.firmas_gracias_url or settings.app_url or None

        firma_id = _leer_token(token)
        if firma_id is None:
            return ResultadoVerificacion(
                EstadoVerificacion.TOKEN_INVALIDO,
                "El enlace de confirmación no es válido o ha caducado.",
                redirect_url=redirect,
            )

        firma = await self.session.get(FirmaCampania, firma_id)
        if firma is None or firma.eliminado:
            return ResultadoVerificacion(
                EstadoVerificacion.NO_ENCONTRADA,
                "No encontramos la firma asociada a este enlace.",
                redirect_url=redirect,
            )

        if firma.verificado:
            return ResultadoVerificacion(
                EstadoVerificacion.YA_VERIFICADA,
                "Esta firma ya estaba confirmada. ¡Gracias!",
                redirect_url=redirect,
            )

        firma.verificado = True
        firma.fecha_verificacion = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.commit()

        return ResultadoVerificacion(
            EstadoVerificacion.VERIFICADA,
            "¡Firma confirmada! Gracias por tu apoyo.",
            redirect_url=redirect,
        )

    # ---------------------------------------------------------------- conteo
    async def contar_firmas_verificadas(self, campania_id: uuid.UUID) -> int:
        from sqlalchemy import func

        total = await self.session.scalar(
            select(func.count(FirmaCampania.id)).where(
                FirmaCampania.campania_id == campania_id,
                FirmaCampania.verificado.is_(True),
                FirmaCampania.eliminado.is_(False),
            )
        )
        return int(total or 0)

    # --------------------------------------------------------------- helpers
    async def _campania_abierta(self, campania_id: uuid.UUID) -> Optional[Campania]:
        campania = await self.session.get(Campania, campania_id)
        if campania is None or campania.eliminado:
            return None
        estado = campania.estado  # lazy='selectin'
        if estado is not None and estado.codigo in Campania.CODIGOS_ESTADO_CERRADO:
            return None
        return campania

    async def _upsert_contacto(
        self,
        *,
        nombre: str,
        apellidos: str,
        email: str,
        codigo_postal: Optional[str],
        pais_id: Optional[uuid.UUID],
        documento: Optional[str],
        tipo_documento: Optional[str],
        acepta_comunicaciones: bool,
    ) -> Contacto:
        """Crea o actualiza el Contacto (persona física) que firma.

        En el modelo CRM, un firmante es un Contacto PF identificado por email.
        Si ya existe (sea por firmas previas o por ser miembro), se reutiliza.

        NOTA (pendiente RGPD): `acepta_comunicaciones` no tiene aún campo en
        Contacto; el consentimiento de comunicaciones debe registrarse en el
        módulo proteccion_datos cuando se reconduzca a Contacto. De momento no
        se persiste aquí para no inventar esquema.
        """
        existente = await self.session.scalar(
            select(Contacto).where(
                Contacto.email == email,
                Contacto.tipo == "PERSONA_FISICA",
                Contacto.eliminado.is_(False),
            )
        )
        if existente is not None:
            # Actualizamos datos básicos (corrección de erratas).
            existente.nombre = nombre.strip()
            existente.apellido1 = apellidos.strip()
            if codigo_postal:
                existente.codigo_postal = codigo_postal.strip()
            if pais_id:
                existente.pais_domicilio_id = pais_id
            if documento:
                existente.numero_documento = documento.strip()
                existente.tipo_documento = tipo_documento
            await self.session.flush()
            return existente

        contacto = Contacto(
            tipo="PERSONA_FISICA",
            nombre=nombre.strip(),
            apellido1=apellidos.strip(),
            email=email,
            codigo_postal=codigo_postal.strip() if codigo_postal else None,
            pais_domicilio_id=pais_id,
            numero_documento=documento.strip() if documento else None,
            tipo_documento=tipo_documento,
        )
        self.session.add(contacto)
        await self.session.flush()
        return contacto

    async def _firma_existente(
        self, campania_id: uuid.UUID, contacto_id: uuid.UUID
    ) -> Optional[FirmaCampania]:
        return await self.session.scalar(
            select(FirmaCampania).where(
                FirmaCampania.campania_id == campania_id,
                FirmaCampania.contacto_id == contacto_id,
                FirmaCampania.eliminado.is_(False),
            )
        )

    async def _enviar_email_verificacion(
        self, contacto: Contacto, campania: Campania, firma: FirmaCampania
    ) -> None:
        settings = get_settings()
        base_api = (settings.siga_api_url or settings.app_url or "").rstrip("/")
        token = _firmar_token(firma.id)
        enlace = f"{base_api}/api/publico/firmas/verificar?token={token}"

        asunto = f"Confirma tu firma — {campania.nombre}"
        cuerpo_html = (
            f"<p>Hola {contacto.nombre},</p>"
            f"<p>Has firmado la campaña <strong>{campania.nombre}</strong>. "
            f"Para que tu firma cuente, confírmala pulsando aquí:</p>"
            f'<p><a href="{enlace}">Confirmar mi firma</a></p>'
            f"<p>Si no has sido tú, ignora este mensaje y no se registrará nada.</p>"
            f"<p>El enlace caduca en {_TOKEN_HORAS_VALIDEZ} horas.</p>"
        )
        cuerpo_texto = (
            f"Hola {contacto.nombre},\n\n"
            f"Has firmado la campaña \"{campania.nombre}\". Confirma tu firma abriendo este enlace:\n"
            f"{enlace}\n\n"
            f"Si no has sido tú, ignora este mensaje. El enlace caduca en {_TOKEN_HORAS_VALIDEZ} horas."
        )

        try:
            await EmailService(self.session).enviar(
                destinatario=contacto.email,
                asunto=asunto,
                cuerpo_html=cuerpo_html,
                cuerpo_texto=cuerpo_texto,
            )
        except Exception as exc:  # noqa: BLE001 — el alta no debe caerse por un fallo SMTP
            logger.error("No se pudo enviar el email de verificación a %s: %s", contacto.email, exc)
