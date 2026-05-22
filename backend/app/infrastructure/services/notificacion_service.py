"""Servicio de gestión de notificaciones.

Responsabilidades:
  - Crear notificaciones in-app (fila `Notificacion`) de forma individual o en lote.
  - Resolver el `estado_id` por código (PENDIENTE/ENVIADA/LEIDA/ERROR), con cache.
  - Enviar por email cuando procede, según la PRIORIDAD del tipo de notificación.
  - Gestionar lectura, archivado, recuento de no leídas y preferencias.
  - Punto de entrada de alto nivel para flujos de trabajo: `emitir(...)`, que
    resuelve la audiencia (rol/cargo/usuario) con DestinatarioResolver, crea las
    notificaciones in-app y dispara los emails que correspondan.

Regla de canal email (decisión por prioridad del tipo)
------------------------------------------------------
El in-app se crea SIEMPRE. El email se añade solo si se cumplen TODAS:
  1. La prioridad del tipo es ALTA o URGENTE.
  2. El tipo admite email (`TipoNotificacion.permite_email`).
  3. La preferencia del usuario no lo veta (`PreferenciaNotificacion.email_habilitado`,
     que por defecto es True si el usuario no tiene preferencia registrada).
  4. SMTP está configurado. Si no lo está, el envío se marca como SIMULADO
     (coherente con el comportamiento de las notificaciones de campaña).
La prioridad PROPONE el email; el tipo y la preferencia pueden RETIRARLO.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Iterable

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...modules.core.comunicacion import (
    TipoNotificacion,
    Notificacion,
    PreferenciaNotificacion,
)
from ...modules.configuracion.models.estados import EstadoNotificacion
from ...modules.acceso.models.usuario import Usuario
from ...core.email_service import EmailService, _load_smtp_config
from .cache_service import get_cache_service, generar_cache_key

logger = logging.getLogger(__name__)

# Prioridades del tipo que proponen envío por email.
_PRIORIDADES_EMAIL = frozenset({"ALTA", "URGENTE"})


class ResultadoEmision:
    """Resultado agregado de una emisión de aviso a una audiencia."""

    def __init__(self) -> None:
        self.inapp_creadas: int = 0
        self.email_enviados: int = 0
        self.email_fallidos: int = 0
        self.email_simulados: int = 0
        self.sin_email: int = 0
        self.destinatarios: int = 0
        self.mensaje: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "destinatarios": self.destinatarios,
            "inapp_creadas": self.inapp_creadas,
            "email_enviados": self.email_enviados,
            "email_fallidos": self.email_fallidos,
            "email_simulados": self.email_simulados,
            "sin_email": self.sin_email,
            "mensaje": self.mensaje,
        }


class NotificacionService:
    """Servicio para gestión de notificaciones del sistema."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = get_cache_service()
        # Cache local (por instancia/request) del mapeo código → estado_id.
        self._estado_ids: Dict[str, uuid.UUID] = {}

    # ------------------------------------------------------------------
    # Resolución de estados por código
    # ------------------------------------------------------------------

    async def _estado_id(self, codigo: str) -> uuid.UUID:
        """Devuelve el id del EstadoNotificacion por código, cacheado por request."""
        if codigo in self._estado_ids:
            return self._estado_ids[codigo]
        result = await self.session.execute(
            select(EstadoNotificacion.id).where(
                EstadoNotificacion.codigo == codigo,
                EstadoNotificacion.eliminado == False,  # noqa: E712
            )
        )
        estado_id = result.scalar_one_or_none()
        if estado_id is None:
            raise ValueError(
                f"EstadoNotificacion '{codigo}' no existe. "
                f"¿Se han sembrado los estados de notificación?"
            )
        self._estado_ids[codigo] = estado_id
        return estado_id

    # ------------------------------------------------------------------
    # Creación in-app
    # ------------------------------------------------------------------

    async def crear_notificacion(
        self,
        tipo_codigo: str,
        usuario_id: uuid.UUID,
        titulo: str,
        mensaje: str,
        canal: str = "INAPP",
        datos_adicionales: Optional[Dict[str, Any]] = None,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[str] = None,
        url_accion: Optional[str] = None,
        fecha_expiracion: Optional[datetime] = None,
        commit: bool = True,
    ) -> Notificacion:
        """Crea una notificación in-app para un usuario.

        Con `commit=False` la notificación se añade a la sesión sin hacer commit,
        útil para creación en lote (un único commit al final).
        """
        tipo = await self._obtener_tipo(tipo_codigo)

        # Verificar que el canal solicitado está permitido por el tipo
        canal = self._canal_permitido(tipo, canal)

        notificacion = Notificacion(
            id=uuid.uuid4(),
            tipo_id=tipo.id,
            usuario_id=usuario_id,
            titulo=titulo,
            mensaje=mensaje,
            canal=canal,
            datos_adicionales=datos_adicionales,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            url_accion=url_accion,
            fecha_expiracion=fecha_expiracion,
            requiere_accion=tipo.requiere_accion,
            estado_id=await self._estado_id("PENDIENTE"),
        )

        self.session.add(notificacion)
        if commit:
            await self.session.commit()
            await self.session.refresh(notificacion)

        self._invalidar_cache_no_leidas(usuario_id)
        logger.info("Notificación creada: %s para usuario %s", notificacion.id, usuario_id)
        return notificacion

    # ------------------------------------------------------------------
    # Punto de entrada de alto nivel para flujos de trabajo
    # ------------------------------------------------------------------

    async def emitir(
        self,
        *,
        tipo_codigo: str,
        audiencia,  # EspecificacionAudiencia | Iterable[EspecificacionAudiencia]
        titulo: str,
        mensaje: str,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[str] = None,
        url_accion: Optional[str] = None,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        cuerpo_html_email: Optional[str] = None,
    ) -> ResultadoEmision:
        """Emite un aviso a una audiencia resuelta por rol/cargo/usuario.

        Crea in-app para todos los destinatarios y, según la prioridad del tipo,
        envía además por email a quienes proceda. Es el método que invocan los
        handlers de eventos de dominio.
        """
        from ...modules.core.comunicacion.services.destinatario_resolver import (
            DestinatarioResolver,
            EspecificacionAudiencia,
        )

        if isinstance(audiencia, EspecificacionAudiencia):
            specs: Iterable[EspecificacionAudiencia] = [audiencia]
        else:
            specs = list(audiencia)

        resolver = DestinatarioResolver(self.session)
        destinatarios = await resolver.resolver(specs)

        resultado = ResultadoEmision()
        resultado.destinatarios = len(destinatarios)
        if not destinatarios:
            resultado.mensaje = "Sin destinatarios para la audiencia indicada."
            return resultado

        tipo = await self._obtener_tipo(tipo_codigo)
        quiere_email = (
            tipo.prioridad in _PRIORIDADES_EMAIL and bool(tipo.permite_email)
        )

        # 1) Crear todas las notificaciones in-app en lote (un solo commit)
        for d in destinatarios:
            await self.crear_notificacion(
                tipo_codigo=tipo_codigo,
                usuario_id=d.usuario_id,
                titulo=titulo,
                mensaje=mensaje,
                canal="INAPP",
                datos_adicionales=datos_adicionales,
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                url_accion=url_accion,
                commit=False,
            )
            resultado.inapp_creadas += 1
        await self.session.commit()
        for d in destinatarios:
            self._invalidar_cache_no_leidas(d.usuario_id)

        # 2) Email, si la prioridad del tipo lo propone
        if not quiere_email:
            resultado.mensaje = (
                f"{resultado.inapp_creadas} avisos in-app creados "
                f"(prioridad {tipo.prioridad}: sin email)."
            )
            return resultado

        smtp = await _load_smtp_config(self.session)
        email_svc = EmailService(self.session)
        asunto = titulo
        cuerpo = cuerpo_html_email or self._cuerpo_email_discreto(titulo, url_accion)

        for d in destinatarios:
            if not await self._email_permitido_para(d.usuario_id, tipo.id):
                resultado.sin_email += 1
                continue
            if not smtp.configured:
                resultado.email_simulados += 1
                continue
            try:
                await email_svc.enviar(
                    destinatario=d.email,
                    asunto=asunto,
                    cuerpo_html=cuerpo.replace("{{ nombre_miembro }}", d.nombre),
                )
                resultado.email_enviados += 1
            except Exception as exc:  # noqa: BLE001
                logger.error("Fallo al enviar email a %s: %s", d.email, exc)
                resultado.email_fallidos += 1

        if not smtp.configured:
            resultado.mensaje = (
                f"{resultado.inapp_creadas} avisos in-app creados. "
                f"Email SIMULADO ({resultado.email_simulados}): SMTP no configurado."
            )
        else:
            resultado.mensaje = (
                f"{resultado.inapp_creadas} avisos in-app; "
                f"{resultado.email_enviados} emails enviados, "
                f"{resultado.email_fallidos} fallidos, "
                f"{resultado.sin_email} sin email (vetado por tipo/preferencia)."
            )
        return resultado

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    async def obtener_notificaciones_usuario(
        self,
        usuario_id: uuid.UUID,
        solo_no_leidas: bool = False,
        solo_no_archivadas: bool = True,
        limite: int = 50,
        offset: int = 0,
    ) -> List[Notificacion]:
        """Obtiene las notificaciones de un usuario (más recientes primero)."""
        filtros = [
            Notificacion.usuario_id == usuario_id,
            Notificacion.eliminado == False,  # noqa: E712
        ]
        if solo_no_leidas:
            filtros.append(Notificacion.leida == False)  # noqa: E712
        if solo_no_archivadas:
            filtros.append(Notificacion.archivada == False)  # noqa: E712

        stmt = (
            select(Notificacion)
            .where(and_(*filtros))
            .order_by(Notificacion.fecha_creacion.desc())
            .limit(limite)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def contar_no_leidas(self, usuario_id: uuid.UUID) -> int:
        """Cuenta notificaciones no leídas y no archivadas (cacheado 5 min)."""
        cache_key = generar_cache_key("notificaciones_no_leidas", str(usuario_id))
        count = self.cache.get(cache_key)
        if count is not None:
            return count

        stmt = select(func.count(Notificacion.id)).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leida == False,       # noqa: E712
                Notificacion.archivada == False,   # noqa: E712
                Notificacion.eliminado == False,   # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        self.cache.set(cache_key, count, ttl=300)
        return count

    # ------------------------------------------------------------------
    # Mutaciones de estado de lectura/archivado
    # ------------------------------------------------------------------

    async def marcar_como_leida(self, notificacion_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        notificacion = await self._obtener_propia(notificacion_id, usuario_id)
        if not notificacion:
            return False
        notificacion.marcar_como_leida()
        notificacion.estado_id = await self._estado_id("LEIDA")
        await self.session.commit()
        self._invalidar_cache_no_leidas(usuario_id)
        return True

    async def marcar_todas_como_leidas(self, usuario_id: uuid.UUID) -> int:
        stmt = select(Notificacion).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leida == False,       # noqa: E712
                Notificacion.eliminado == False,   # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        notificaciones = result.scalars().all()
        estado_leida = await self._estado_id("LEIDA")
        count = 0
        for n in notificaciones:
            n.marcar_como_leida()
            n.estado_id = estado_leida
            count += 1
        await self.session.commit()
        self._invalidar_cache_no_leidas(usuario_id)
        return count

    async def archivar_notificacion(self, notificacion_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        notificacion = await self._obtener_propia(notificacion_id, usuario_id)
        if not notificacion:
            return False
        notificacion.archivar()
        await self.session.commit()
        self._invalidar_cache_no_leidas(usuario_id)
        return True

    async def limpiar_notificaciones_antiguas(self, dias: int = 90) -> int:
        """Soft-delete de notificaciones leídas/archivadas más antiguas que `dias`."""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        stmt = select(Notificacion).where(
            and_(
                Notificacion.fecha_creacion < fecha_limite,
                or_(
                    Notificacion.leida == True,      # noqa: E712
                    Notificacion.archivada == True,  # noqa: E712
                ),
                Notificacion.eliminado == False,     # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        notificaciones = result.scalars().all()
        count = 0
        for n in notificaciones:
            n.soft_delete()
            count += 1
        await self.session.commit()
        logger.info("%s notificaciones antiguas eliminadas", count)
        return count

    # ------------------------------------------------------------------
    # Preferencias
    # ------------------------------------------------------------------

    async def obtener_preferencias_usuario(
        self,
        usuario_id: uuid.UUID,
        tipo_codigo: Optional[str] = None,
    ) -> List[PreferenciaNotificacion]:
        filtros = [
            PreferenciaNotificacion.usuario_id == usuario_id,
            PreferenciaNotificacion.eliminado == False,  # noqa: E712
        ]
        if tipo_codigo:
            tipo = await self._obtener_tipo(tipo_codigo, requerido=False)
            if tipo:
                filtros.append(PreferenciaNotificacion.tipo_id == tipo.id)
        stmt = select(PreferenciaNotificacion).where(and_(*filtros))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def actualizar_preferencia(
        self,
        usuario_id: uuid.UUID,
        tipo_codigo: str,
        email_habilitado: Optional[bool] = None,
        sms_habilitado: Optional[bool] = None,
        push_habilitado: Optional[bool] = None,
        inapp_habilitado: Optional[bool] = None,
        frecuencia: Optional[str] = None,
    ) -> PreferenciaNotificacion:
        tipo = await self._obtener_tipo(tipo_codigo)
        result = await self.session.execute(
            select(PreferenciaNotificacion).where(
                and_(
                    PreferenciaNotificacion.usuario_id == usuario_id,
                    PreferenciaNotificacion.tipo_id == tipo.id,
                    PreferenciaNotificacion.eliminado == False,  # noqa: E712
                )
            )
        )
        preferencia = result.scalar_one_or_none()
        if not preferencia:
            preferencia = PreferenciaNotificacion(
                id=uuid.uuid4(), usuario_id=usuario_id, tipo_id=tipo.id
            )
            self.session.add(preferencia)

        if email_habilitado is not None:
            preferencia.email_habilitado = email_habilitado
        if sms_habilitado is not None:
            preferencia.sms_habilitado = sms_habilitado
        if push_habilitado is not None:
            preferencia.push_habilitado = push_habilitado
        if inapp_habilitado is not None:
            preferencia.inapp_habilitado = inapp_habilitado
        if frecuencia is not None:
            preferencia.frecuencia = frecuencia

        await self.session.commit()
        await self.session.refresh(preferencia)
        return preferencia

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    async def _obtener_tipo(self, tipo_codigo: str, requerido: bool = True) -> Optional[TipoNotificacion]:
        result = await self.session.execute(
            select(TipoNotificacion).where(
                TipoNotificacion.codigo == tipo_codigo,
                TipoNotificacion.activo == True,      # noqa: E712
                TipoNotificacion.eliminado == False,  # noqa: E712
            )
        )
        tipo = result.scalar_one_or_none()
        if tipo is None and requerido:
            raise ValueError(f"Tipo de notificación no encontrado: {tipo_codigo}")
        return tipo

    async def _obtener_propia(
        self, notificacion_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> Optional[Notificacion]:
        result = await self.session.execute(
            select(Notificacion).where(
                Notificacion.id == notificacion_id,
                Notificacion.usuario_id == usuario_id,
            )
        )
        return result.scalar_one_or_none()

    async def _email_permitido_para(self, usuario_id: uuid.UUID, tipo_id: uuid.UUID) -> bool:
        """La preferencia del usuario veta el email; por defecto (sin registro) permite."""
        result = await self.session.execute(
            select(PreferenciaNotificacion.email_habilitado).where(
                PreferenciaNotificacion.usuario_id == usuario_id,
                PreferenciaNotificacion.tipo_id == tipo_id,
                PreferenciaNotificacion.eliminado == False,  # noqa: E712
            )
        )
        pref = result.scalar_one_or_none()
        return True if pref is None else bool(pref)

    @staticmethod
    def _cuerpo_email_discreto(titulo: str, url_accion: Optional[str]) -> str:
        """Cuerpo de email SIN datos personales: solo el título y un enlace.

        El email escapa del control de la aplicación (se reenvía, se ve en la
        pantalla de bloqueo del móvil…), por eso no se vuelca el mensaje in-app,
        que puede contener nombres u otros datos personales. El dato sensible vive
        dentro de la aplicación; el correo solo invita a entrar.
        """
        from app.core.config import get_settings

        partes = [f"<p>{titulo}.</p>"]
        if url_accion:
            base = str(getattr(get_settings(), "app_url", "")).rstrip("/")
            href = url_accion if url_accion.startswith("http") else f"{base}{url_accion}"
            partes.append(
                f'<p>Tienes un aviso pendiente en SIGA. '
                f'<a href="{href}">Entra para verlo</a>.</p>'
            )
        else:
            partes.append("<p>Tienes un aviso pendiente en SIGA. Accede para verlo.</p>")
        return "\n".join(partes)

    @staticmethod
    def _canal_permitido(tipo: TipoNotificacion, canal: str) -> str:
        permitido = {
            "EMAIL": tipo.permite_email,
            "SMS": tipo.permite_sms,
            "PUSH": tipo.permite_push,
            "INAPP": tipo.permite_inapp,
        }.get(canal, False)
        if not permitido:
            logger.warning("Canal %s no permitido para tipo %s; se usa INAPP", canal, tipo.codigo)
            return "INAPP"
        return canal

    def _invalidar_cache_no_leidas(self, usuario_id: uuid.UUID) -> None:
        self.cache.delete(generar_cache_key("notificaciones_no_leidas", str(usuario_id)))
