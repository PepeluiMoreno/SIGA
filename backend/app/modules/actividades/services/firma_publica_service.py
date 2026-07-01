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
        campania_id: Optional[uuid.UUID] = None,
        actividad_id: Optional[uuid.UUID] = None,
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

        # La firma se pide sobre una ACTIVIDAD de recogida de firmas online y se
        # ancla a ella. La campaña queda como contexto denormalizado (nullable).
        # Se admite el anclaje directo por campania_id (compatibilidad).
        actividad = None
        if actividad_id is not None:
            actividad = await self._actividad_firmas_activa(actividad_id)
            if actividad is None:
                return ResultadoRegistro(
                    EstadoRegistro.CAMPANIA_NO_DISPONIBLE,
                    "La actividad no existe o ya no admite firmas.",
                )
            campania_id = actividad.campania_id

        campania = await self._campania_abierta(campania_id) if campania_id is not None else None

        # Debe haber un ancla válido: actividad activa o campaña abierta.
        if actividad is None and campania is None:
            return ResultadoRegistro(
                EstadoRegistro.CAMPANIA_NO_DISPONIBLE,
                "No se ha indicado una actividad de firmas válida.",
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

        # Firmar NO crea vinculación: "firmante/participante" es una condición
        # DERIVADA de tener firmas (Participacion FIRMA). El consentimiento de
        # comunicaciones, si lo dio, es de la persona → se registra en
        # proteccion_datos (modelo Consentimiento), no como satélite ni vínculo.
        if acepta_comunicaciones:
            await self._registrar_consentimiento_comunicaciones(contacto, ip_origen)
        # Commit para que contacto (+ consentimiento) persistan en TODAS las rutas
        # (incluidas las de "ya firmada", que retornan sin el commit final).
        await self.session.commit()

        titulo = actividad.nombre if actividad is not None else campania.nombre

        firma = await self._firma_existente(
            actividad.id if actividad is not None else None,
            campania.id if campania is not None else None,
            contacto.id,
        )
        if firma is not None:
            if firma.verificado:
                return ResultadoRegistro(
                    EstadoRegistro.YA_VERIFICADA,
                    "Esta dirección ya ha firmado y verificado esta recogida.",
                )
            # Reenviamos el correo de verificación de la firma pendiente.
            await self._enviar_email_verificacion(contacto, titulo, firma)
            return ResultadoRegistro(
                EstadoRegistro.YA_FIRMADA_PENDIENTE,
                "Ya había una firma pendiente. Te hemos reenviado el correo de confirmación.",
            )

        # La firma es el satélite de una Participacion (tipo FIRMA). "Firmante"
        # es una condición derivada de tener firmas; no se crea vinculación.
        participacion = Participacion(
            contacto_id=contacto.id, tipo="FIRMA", estado="registrada",
        )
        self.session.add(participacion)
        await self.session.flush()

        firma = FirmaCampania(
            participacion_id=participacion.id,
            actividad_id=actividad.id if actividad is not None else None,
            campania_id=campania.id if campania is not None else campania_id,
            contacto_id=contacto.id,
            acepta_terminos=True,
            verificado=False,
            ip_origen=(ip_origen or "")[:50] or None,
        )
        self.session.add(firma)
        await self.session.flush()  # obtener firma.id antes de firmar el token

        await self._enviar_email_verificacion(contacto, titulo, firma)
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

    # ------------------------------------------------------------ listado
    # Estados de EstadoAccion que NO admiten firmas: aún no iniciada (Propuesta)
    # o ya cerrada (Finalizada/Cancelada). EstadoAccion no tiene `codigo`
    # (hereda de EstadoBase), así que de momento se filtra por nombre; ver la
    # decisión (A) en docs/REDISENO_FIRMAS_ACTIVIDAD.md.
    _ESTADOS_ACCION_NO_ACTIVOS = frozenset({"propuesta", "finalizada", "cancelada"})

    def _actividad_esta_activa(self, actividad) -> bool:
        """True si la actividad está iniciada y no cerrada."""
        estado = actividad.estado  # lazy='selectin'
        nombre = (getattr(estado, "nombre", "") or "").strip().lower()
        return nombre not in self._ESTADOS_ACCION_NO_ACTIVOS

    async def listar_actividades_firmas_activas(self) -> list:
        """Actividades de recogida de firmas web activas, para el desplegable.

        Criterio: la actividad es ONLINE, está iniciada y no cerrada, y tiene una
        META propia en firmas (una MetaActividad cuyo TipoMeta.unidad_medida ==
        "firmas"). La meta vive ya en la actividad (Fase 1)."""
        from sqlalchemy import func

        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.campana import MetaActividad, TipoMeta

        stmt = (
            select(Actividad)
            .join(MetaActividad, MetaActividad.actividad_id == Actividad.id)
            .join(TipoMeta, MetaActividad.tipo_meta_id == TipoMeta.id)
            .where(
                Actividad.eliminado.is_(False),
                Actividad.es_online.is_(True),
                func.lower(TipoMeta.unidad_medida) == "firmas",
            )
            .order_by(Actividad.nombre)
            .distinct()
        )
        candidatas = (await self.session.scalars(stmt)).all()
        # Estados (actividad y campaña) por relación selectin: filtramos en memoria.
        return [
            a
            for a in candidatas
            if self._actividad_esta_activa(a)
            and not (a.campania is not None and a.campania.esta_cerrada)
        ]

    async def _actividad_firmas_activa(self, actividad_id: uuid.UUID):
        """Devuelve la Actividad si existe, es online y está activa; si no, None."""
        from app.modules.actividades.models.actividad import Actividad

        actividad = await self.session.get(Actividad, actividad_id)
        if actividad is None or actividad.eliminado or not actividad.es_online:
            return None
        if not self._actividad_esta_activa(actividad):
            return None
        if actividad.campania is not None and actividad.campania.esta_cerrada:
            return None
        return actividad

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

        Desduplicación por identidad:
        - **Con NIF (DNI/NIE)**: clave fuerte → se busca por `numero_documento`
          normalizado. Una misma persona no se duplica aunque firme con emails
          distintos, y si ya existe (p. ej. socio) se reutiliza.
        - **Sin NIF (extranjero)**: clave blanda por **nombre+apellidos
          normalizados**; si no hay coincidencia clara, NO se fusiona (se crea
          aparte) para no unir por error a dos personas distintas.

        El consentimiento de comunicaciones NO se persiste aquí: es de la persona
        y se registra en proteccion_datos (ver `_registrar_consentimiento_*`).
        """
        from app.core.documento import normalizar_documento

        nif = normalizar_documento(documento)

        if nif:
            existente = await self.session.scalar(
                select(Contacto).where(
                    Contacto.numero_documento == nif,
                    Contacto.tipo == "PERSONA_FISICA",
                    Contacto.eliminado.is_(False),
                )
            )
        else:
            # Extranjero sin NIF: dedup blanda por nombre+apellidos normalizados.
            existente = await self._buscar_por_nombre(nombre, apellidos)

        if existente is not None:
            # Actualizamos datos básicos (corrección de erratas). El NIF es la
            # identidad, no se toca; el email se refresca al último usado.
            existente.nombre = nombre.strip()
            existente.apellido1 = apellidos.strip()
            if email:
                existente.email = email
            if codigo_postal:
                existente.codigo_postal = codigo_postal.strip()
            if pais_id:
                existente.pais_domicilio_id = pais_id
            if tipo_documento:
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
            numero_documento=nif or None,
            tipo_documento=tipo_documento if nif else None,
        )
        self.session.add(contacto)
        await self.session.flush()
        return contacto

    async def _buscar_por_nombre(self, nombre: str, apellidos: str) -> Optional[Contacto]:
        """Dedup blanda para firmantes SIN NIF (extranjeros): coincidencia exacta
        de nombre+apellidos (normalizado a minúsculas) entre contactos PF que
        tampoco tienen NIF. No fusiona con contactos que sí tienen NIF."""
        from sqlalchemy import func

        n = (nombre or "").strip().lower()
        a = (apellidos or "").strip().lower()
        if not n or not a:
            return None
        return await self.session.scalar(
            select(Contacto)
            .where(
                func.lower(Contacto.nombre) == n,
                func.lower(Contacto.apellido1) == a,
                Contacto.tipo == "PERSONA_FISICA",
                Contacto.numero_documento.is_(None),
                Contacto.eliminado.is_(False),
            )
            .limit(1)
        )

    async def _registrar_consentimiento_comunicaciones(
        self, contacto: Contacto, ip_origen: Optional[str]
    ) -> None:
        """Registra el consentimiento de comunicaciones del firmante (art. 7 RGPD).

        Reutiliza el modelo `Consentimiento` de proteccion_datos, enlazado a la
        cláusula vigente `COMUNICACIONES_INFORMATIVAS`. El consentimiento es de la
        PERSONA (no del rol). Si no hay cláusula vigente, no rompe el alta: deja
        aviso en log (la firma se registra igual).
        """
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
                "Sin cláusula COMUNICACIONES_INFORMATIVAS vigente; no se registra "
                "el consentimiento de comunicaciones del firmante %s.", contacto.id
            )
            return

        # Idempotencia razonable: si ya hay un consentimiento OTORGADO de esa
        # cláusula para el contacto, no duplicamos.
        ya = await self.session.scalar(
            select(Consentimiento.id).where(
                Consentimiento.miembro_id == contacto.id,
                Consentimiento.clausula_id == clausula_id,
                Consentimiento.estado == "OTORGADO",
                Consentimiento.eliminado.is_(False),
            )
        )
        if ya is not None:
            return

        self.session.add(
            Consentimiento(
                miembro_id=contacto.id,
                clausula_id=clausula_id,
                estado="OTORGADO",
                fecha_otorgamiento=datetime.now(timezone.utc).replace(tzinfo=None),
                canal="WEB",
                prueba=(f"ip={ip_origen}" if ip_origen else None),
            )
        )
        await self.session.flush()

    async def _firma_existente(
        self,
        actividad_id: Optional[uuid.UUID],
        campania_id: Optional[uuid.UUID],
        contacto_id: uuid.UUID,
    ) -> Optional[FirmaCampania]:
        """Dedup de firma por (ancla, contacto): por actividad si la hay, si no
        por campaña. Evita firmas duplicadas de la misma persona a la misma
        recogida."""
        cond = (
            FirmaCampania.actividad_id == actividad_id
            if actividad_id is not None
            else FirmaCampania.campania_id == campania_id
        )
        return await self.session.scalar(
            select(FirmaCampania).where(
                cond,
                FirmaCampania.contacto_id == contacto_id,
                FirmaCampania.eliminado.is_(False),
            )
        )

    async def _enviar_email_verificacion(
        self, contacto: Contacto, titulo: str, firma: FirmaCampania
    ) -> None:
        settings = get_settings()
        base_api = (settings.siga_api_url or settings.app_url or "").rstrip("/")
        token = _firmar_token(firma.id)
        enlace = f"{base_api}/api/publico/firmas/verificar?token={token}"

        asunto = f"Confirma tu firma — {titulo}"
        cuerpo_html = (
            f"<p>Hola {contacto.nombre},</p>"
            f"<p>Has firmado <strong>{titulo}</strong>. "
            f"Para que tu firma cuente, confírmala pulsando aquí:</p>"
            f'<p><a href="{enlace}">Confirmar mi firma</a></p>'
            f"<p>Si no has sido tú, ignora este mensaje y no se registrará nada.</p>"
            f"<p>El enlace caduca en {_TOKEN_HORAS_VALIDEZ} horas.</p>"
        )
        cuerpo_texto = (
            f"Hola {contacto.nombre},\n\n"
            f"Has firmado \"{titulo}\". Confirma tu firma abriendo este enlace:\n"
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
