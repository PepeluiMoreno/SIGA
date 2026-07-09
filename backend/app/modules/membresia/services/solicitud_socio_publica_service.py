"""Auto-alta pública de socios (formulario web externo, p. ej. WordPress).

Flujo de doble opt-in, calcado del de recogida de firmas:

  1. registrar_solicitud(): valida los datos, hace upsert del Contacto (persona
     física) por NIF (o por nombre si es extranjero), crea la Vinculacion
     SOCIO_ASPIRANTE en estado ``pendiente_verificacion`` con su satélite Socio
     (para conservar el IBAN/forma de pago elegidos) y envía un correo de
     confirmación con un token firmado.
  2. verificar_solicitud(): valida el token y pasa la vinculación a ``activa``.
     A partir de ese momento la solicitud aparece en la bandeja de secretaría
     (query ``solicitudes_socio_pendientes``) para su aprobación definitiva, que
     ya existe (``aprobar_solicitud_socio`` → SOCIO_ASPIRANTE se convierte en
     SOCIO).

SIGA es la fuente única: WordPress solo presenta el formulario y reenvía datos.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.documento import normalizar_documento, normalizar_iban
from app.core.email_service import EmailService
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.membresia.models.vinculacion import Socio, Vinculacion

logger = logging.getLogger(__name__)

_TOKEN_PURPOSE = "socio_aspirante_verify"
_TOKEN_HORAS_VALIDEZ = 72

# Estados de la vinculación SOCIO_ASPIRANTE en el flujo público:
#  - pendiente_verificacion: alta creada, email aún sin confirmar (no visible en bandeja)
#  - activa: email confirmado; la solicitud entra en la bandeja de secretaría
_ESTADO_PENDIENTE = "pendiente_verificacion"
_ESTADO_ACTIVA = "activa"


class EstadoSolicitud(str, Enum):
    PENDIENTE_VERIFICACION = "pendiente_verificacion"
    YA_SOLICITADA_PENDIENTE = "ya_solicitada_pendiente"
    YA_ES_SOCIO = "ya_es_socio"
    DATOS_INVALIDOS = "datos_invalidos"


class EstadoVerificacion(str, Enum):
    VERIFICADA = "verificada"
    YA_VERIFICADA = "ya_verificada"
    TOKEN_INVALIDO = "token_invalido"
    NO_ENCONTRADA = "no_encontrada"


@dataclass
class ResultadoSolicitud:
    estado: EstadoSolicitud
    mensaje: str


@dataclass
class ResultadoVerificacion:
    estado: EstadoVerificacion
    mensaje: str
    redirect_url: Optional[str] = None


def _firmar_token(vinculacion_id: uuid.UUID) -> str:
    settings = get_settings()
    payload = {
        "sub": str(vinculacion_id),
        "purpose": _TOKEN_PURPOSE,
        "exp": datetime.now(timezone.utc) + timedelta(hours=_TOKEN_HORAS_VALIDEZ),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _leer_token(token: str) -> Optional[uuid.UUID]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        logger.info("Token de aspirante inválido o expirado: %s", exc)
        return None
    if payload.get("purpose") != _TOKEN_PURPOSE:
        return None
    try:
        return uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        return None


class SolicitudSocioPublicaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------ alta
    async def registrar_solicitud(
        self,
        *,
        nombre: str,
        apellido1: str,
        apellido2: Optional[str] = None,
        email: str,
        telefono: Optional[str] = None,
        documento: Optional[str] = None,
        tipo_documento: Optional[str] = None,
        pais_documento_id: Optional[uuid.UUID] = None,
        fecha_nacimiento: Optional[date] = None,
        sexo: Optional[str] = None,
        direccion: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        localidad: Optional[str] = None,
        provincia_id: Optional[uuid.UUID] = None,
        pais_domicilio_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        iban: Optional[str] = None,
        swift_bic: Optional[str] = None,
        forma_pago_id: Optional[uuid.UUID] = None,
        acepta_comunicaciones: bool = False,
        ip_origen: Optional[str] = None,
    ) -> ResultadoSolicitud:
        email = email.strip().lower()

        contacto = await self._upsert_contacto(
            nombre=nombre, apellido1=apellido1, apellido2=apellido2, email=email,
            telefono=telefono, documento=documento, tipo_documento=tipo_documento,
            pais_documento_id=pais_documento_id, fecha_nacimiento=fecha_nacimiento,
            sexo=sexo, direccion=direccion, codigo_postal=codigo_postal,
            localidad=localidad, provincia_id=provincia_id,
            pais_domicilio_id=pais_domicilio_id, agrupacion_id=agrupacion_id,
        )
        await self.session.flush()

        # Si ya es SOCIO de pleno derecho (vinculación SOCIO no cerrada), no se
        # crea una solicitud: se le indica que ya es socio.
        if await self._tiene_socio_vigente(contacto.id):
            await self.session.commit()
            return ResultadoSolicitud(
                EstadoSolicitud.YA_ES_SOCIO,
                "Esta persona ya figura como socio. Si necesitas ayuda, contacta con la organización.",
            )

        # Si ya hay una solicitud de aspirante (pendiente o verificada), no se
        # duplica: se reenvía el correo de confirmación si aún está pendiente.
        aspirante = await self._aspirante_existente(contacto.id)
        if aspirante is not None:
            if aspirante.estado == _ESTADO_PENDIENTE:
                await self._enviar_email_verificacion(contacto, aspirante)
                await self.session.commit()
                return ResultadoSolicitud(
                    EstadoSolicitud.YA_SOLICITADA_PENDIENTE,
                    "Ya había una solicitud pendiente. Te hemos reenviado el correo de confirmación.",
                )
            await self.session.commit()
            return ResultadoSolicitud(
                EstadoSolicitud.YA_SOLICITADA_PENDIENTE,
                "Tu solicitud ya está confirmada y pendiente de revisión por la organización.",
            )

        asp_tipo_id = await self._tipo_vinc_id("SOCIO_ASPIRANTE")
        vinc = Vinculacion(
            contacto_id=contacto.id,
            tipo_vinculacion_id=asp_tipo_id,
            fecha_inicio=date.today(),
            estado=_ESTADO_PENDIENTE,
            agrupacion_id=agrupacion_id,
        )
        self.session.add(vinc)
        await self.session.flush()

        # Satélite Socio con los datos económicos elegidos en el formulario. Se
        # conserva a través de la aprobación (aprobar_solicitud_socio no lo pisa).
        self.session.add(Socio(
            vinculacion_id=vinc.id,
            iban=normalizar_iban(iban) or None,
            swift_bic=(swift_bic or "").strip().upper() or None,
            forma_pago_id=forma_pago_id,
            estado_socio="aspirante",
        ))
        await self.session.flush()

        if acepta_comunicaciones:
            await self._registrar_consentimiento_comunicaciones(contacto, ip_origen)

        await self._enviar_email_verificacion(contacto, vinc)
        await self.session.commit()

        return ResultadoSolicitud(
            EstadoSolicitud.PENDIENTE_VERIFICACION,
            "Solicitud registrada. Revisa tu correo para confirmarla.",
        )

    # ----------------------------------------------------------- verificación
    async def verificar_solicitud(self, token: str) -> ResultadoVerificacion:
        settings = get_settings()
        redirect = settings.app_url or None

        vinc_id = _leer_token(token)
        if vinc_id is None:
            return ResultadoVerificacion(
                EstadoVerificacion.TOKEN_INVALIDO,
                "El enlace de confirmación no es válido o ha caducado.",
                redirect_url=redirect,
            )

        vinc = await self.session.get(Vinculacion, vinc_id)
        if vinc is None or vinc.eliminado:
            return ResultadoVerificacion(
                EstadoVerificacion.NO_ENCONTRADA,
                "No encontramos la solicitud asociada a este enlace.",
                redirect_url=redirect,
            )

        if vinc.estado == _ESTADO_ACTIVA:
            return ResultadoVerificacion(
                EstadoVerificacion.YA_VERIFICADA,
                "Tu solicitud ya estaba confirmada. La organización la revisará en breve.",
                redirect_url=redirect,
            )

        vinc.estado = _ESTADO_ACTIVA
        vinc.fecha_inicio = date.today()
        await self.session.commit()

        return ResultadoVerificacion(
            EstadoVerificacion.VERIFICADA,
            "¡Solicitud confirmada! La organización la revisará y te dará de alta como socio.",
            redirect_url=redirect,
        )

    # --------------------------------------------------------------- helpers
    async def _tipo_vinc_id(self, codigo: str) -> uuid.UUID:
        return await self.session.scalar(
            select(TipoVinculacion.id).where(TipoVinculacion.codigo == codigo)
        )

    async def _tiene_socio_vigente(self, contacto_id: uuid.UUID) -> bool:
        socio_id = await self._tipo_vinc_id("SOCIO")
        vinc = await self.session.scalar(
            select(Vinculacion).where(
                Vinculacion.contacto_id == contacto_id,
                Vinculacion.tipo_vinculacion_id == socio_id,
                Vinculacion.estado == _ESTADO_ACTIVA,
                Vinculacion.eliminado.is_(False),
            )
        )
        return vinc is not None

    async def _aspirante_existente(self, contacto_id: uuid.UUID) -> Optional[Vinculacion]:
        asp_id = await self._tipo_vinc_id("SOCIO_ASPIRANTE")
        return await self.session.scalar(
            select(Vinculacion)
            .where(
                Vinculacion.contacto_id == contacto_id,
                Vinculacion.tipo_vinculacion_id == asp_id,
                Vinculacion.estado.in_([_ESTADO_PENDIENTE, _ESTADO_ACTIVA]),
                Vinculacion.eliminado.is_(False),
            )
            .order_by(Vinculacion.fecha_inicio.desc())
        )

    async def _upsert_contacto(
        self, *, nombre: str, apellido1: str, apellido2: Optional[str], email: str,
        telefono: Optional[str], documento: Optional[str], tipo_documento: Optional[str],
        pais_documento_id: Optional[uuid.UUID], fecha_nacimiento: Optional[date],
        sexo: Optional[str], direccion: Optional[str], codigo_postal: Optional[str],
        localidad: Optional[str], provincia_id: Optional[uuid.UUID],
        pais_domicilio_id: Optional[uuid.UUID], agrupacion_id: Optional[uuid.UUID],
    ) -> Contacto:
        """Crea o reutiliza el Contacto (persona física). Desdup por NIF si se
        aporta; si no, por nombre+apellido1 normalizados (extranjeros sin NIF)."""
        from sqlalchemy import func

        nif = normalizar_documento(documento)
        existente = None
        if nif:
            existente = await self.session.scalar(
                select(Contacto).where(
                    Contacto.numero_documento == nif,
                    Contacto.tipo == "PERSONA_FISICA",
                    Contacto.eliminado.is_(False),
                )
            )
        elif nombre.strip() and apellido1.strip():
            existente = await self.session.scalar(
                select(Contacto).where(
                    func.lower(Contacto.nombre) == nombre.strip().lower(),
                    func.lower(Contacto.apellido1) == apellido1.strip().lower(),
                    Contacto.tipo == "PERSONA_FISICA",
                    Contacto.numero_documento.is_(None),
                    Contacto.eliminado.is_(False),
                ).limit(1)
            )

        if existente is not None:
            # Completa datos vacíos sin pisar los ya existentes (salvo email/tfno,
            # que se refrescan al último aportado).
            existente.nombre = nombre.strip()
            existente.apellido1 = apellido1.strip()
            if apellido2:
                existente.apellido2 = apellido2.strip()
            if email:
                existente.email = email
            if telefono:
                existente.telefono = telefono.strip()
            for attr, val in (
                ("fecha_nacimiento", fecha_nacimiento), ("sexo", sexo),
                ("direccion", direccion), ("codigo_postal", codigo_postal),
                ("localidad", localidad), ("provincia_id", provincia_id),
                ("pais_domicilio_id", pais_domicilio_id), ("agrupacion_id", agrupacion_id),
                ("pais_documento_id", pais_documento_id),
            ):
                if val and not getattr(existente, attr, None):
                    setattr(existente, attr, val)
            return existente

        contacto = Contacto(
            tipo="PERSONA_FISICA",
            nombre=nombre.strip(),
            apellido1=apellido1.strip(),
            apellido2=(apellido2 or "").strip() or None,
            email=email,
            telefono=(telefono or "").strip() or None,
            numero_documento=nif or None,
            tipo_documento=tipo_documento if nif else None,
            pais_documento_id=pais_documento_id,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            direccion=(direccion or "").strip() or None,
            codigo_postal=(codigo_postal or "").strip() or None,
            localidad=(localidad or "").strip() or None,
            provincia_id=provincia_id,
            pais_domicilio_id=pais_domicilio_id,
            agrupacion_id=agrupacion_id,
        )
        self.session.add(contacto)
        return contacto

    async def _registrar_consentimiento_comunicaciones(
        self, contacto: Contacto, ip_origen: Optional[str]
    ) -> None:
        """Consentimiento de comunicaciones (art. 7 RGPD), enlazado a la cláusula
        vigente COMUNICACIONES_INFORMATIVAS. Si no hay cláusula, no rompe el alta."""
        from app.modules.proteccion_datos.models.clausula import ClausulaInformativa
        from app.modules.proteccion_datos.models.consentimiento import Consentimiento

        clausula_id = await self.session.scalar(
            select(ClausulaInformativa.id).where(
                ClausulaInformativa.codigo == "COMUNICACIONES_INFORMATIVAS",
                ClausulaInformativa.vigente.is_(True),
                ClausulaInformativa.eliminado.is_(False),
            )
        )
        if clausula_id is None:
            logger.warning(
                "Sin cláusula COMUNICACIONES_INFORMATIVAS vigente; no se registra el "
                "consentimiento de comunicaciones del aspirante %s.", contacto.id
            )
            return
        ya = await self.session.scalar(
            select(Consentimiento.id).where(
                Consentimiento.contacto_id == contacto.id,
                Consentimiento.clausula_id == clausula_id,
                Consentimiento.estado == "OTORGADO",
                Consentimiento.eliminado.is_(False),
            )
        )
        if ya is not None:
            return
        self.session.add(Consentimiento(
            contacto_id=contacto.id,
            clausula_id=clausula_id,
            estado="OTORGADO",
            fecha_otorgamiento=datetime.now(timezone.utc).replace(tzinfo=None),
            canal="WEB",
            prueba=(f"ip={ip_origen}" if ip_origen else None),
        ))

    async def _enviar_email_verificacion(
        self, contacto: Contacto, vinc: Vinculacion
    ) -> None:
        settings = get_settings()
        base_api = (settings.siga_api_url or settings.app_url or "").rstrip("/")
        token = _firmar_token(vinc.id)
        enlace = f"{base_api}/api/publico/socios/verificar?token={token}"

        asunto = "Confirma tu solicitud de alta como socio"
        cuerpo_html = (
            f"<p>Hola {contacto.nombre},</p>"
            f"<p>Hemos recibido tu solicitud para hacerte socio. "
            f"Para confirmarla, pulsa aquí:</p>"
            f'<p><a href="{enlace}">Confirmar mi solicitud</a></p>'
            f"<p>Si no has sido tú, ignora este mensaje y no se registrará nada.</p>"
            f"<p>El enlace caduca en {_TOKEN_HORAS_VALIDEZ} horas.</p>"
        )
        cuerpo_texto = (
            f"Hola {contacto.nombre},\n\n"
            f"Hemos recibido tu solicitud para hacerte socio. Confírmala abriendo este enlace:\n"
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
        except Exception as exc:  # noqa: BLE001 — el alta no debe caerse por SMTP
            logger.error(
                "No se pudo enviar el email de confirmación de alta a %s: %s",
                contacto.email, exc,
            )
