"""Servicio de gestión de notificaciones."""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...domains.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion
from .cache_service import CacheService, get_cache_service, generar_cache_key

logger = logging.getLogger(__name__)


class NotificacionService:
    """Servicio para gestión de notificaciones del sistema."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = get_cache_service()

    async def crear_notificacion(
        self,
        tipo_codigo: str,
        usuario_id: uuid.UUID,
        titulo: str,
        mensaje: str,
        canal: str = 'INAPP',
        datos_adicionales: Optional[Dict[str, Any]] = None,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[str] = None,
        url_accion: Optional[str] = None,
        fecha_expiracion: Optional[datetime] = None
    ) -> Notificacion:
        """
        Crea una nueva notificación para un usuario.

        Args:
            tipo_codigo: Código del tipo de notificación
            usuario_id: ID del usuario destinatario
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            canal: Canal de envío (EMAIL, SMS, PUSH, INAPP)
            datos_adicionales: Datos extra en formato dict
            entidad_tipo: Tipo de entidad relacionada
            entidad_id: ID de entidad relacionada
            url_accion: URL para acción opcional
            fecha_expiracion: Fecha de expiración de la notificación

        Returns:
            Notificación creada
        """
        # Obtener tipo de notificación
        result = await self.session.execute(
            select(TipoNotificacion).where(
                TipoNotificacion.codigo == tipo_codigo,
                TipoNotificacion.activo == True,
                TipoNotificacion.eliminado == False
            )
        )
        tipo = result.scalar_one_or_none()

        if not tipo:
            logger.error(f"Tipo de notificación no encontrado: {tipo_codigo}")
            raise ValueError(f"Tipo de notificación no encontrado: {tipo_codigo}")

        # Verificar que el canal está permitido
        canal_permitido = False
        if canal == 'EMAIL' and tipo.permite_email:
            canal_permitido = True
        elif canal == 'SMS' and tipo.permite_sms:
            canal_permitido = True
        elif canal == 'PUSH' and tipo.permite_push:
            canal_permitido = True
        elif canal == 'INAPP' and tipo.permite_inapp:
            canal_permitido = True

        if not canal_permitido:
            logger.warning(f"Canal {canal} no permitido para tipo {tipo_codigo}, usando INAPP por defecto")
            canal = 'INAPP'

        # Crear notificación
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
            estado='PENDIENTE'
        )

        self.session.add(notificacion)
        await self.session.commit()
        await self.session.refresh(notificacion)

        logger.info(f"Notificación creada: {notificacion.id} para usuario {usuario_id}")

        # Invalidar caché de notificaciones no leídas
        cache_key = generar_cache_key("notificaciones_no_leidas", str(usuario_id))
        self.cache.delete(cache_key)

        return notificacion

    async def obtener_notificaciones_usuario(
        self,
        usuario_id: uuid.UUID,
        solo_no_leidas: bool = False,
        solo_no_archivadas: bool = True,
        limite: int = 50,
        offset: int = 0
    ) -> List[Notificacion]:
        """
        Obtiene las notificaciones de un usuario.

        Args:
            usuario_id: ID del usuario
            solo_no_leidas: Filtrar solo no leídas
            solo_no_archivadas: Filtrar solo no archivadas
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de notificaciones
        """
        filtros = [
            Notificacion.usuario_id == usuario_id,
            Notificacion.eliminado == False
        ]

        if solo_no_leidas:
            filtros.append(Notificacion.leida == False)

        if solo_no_archivadas:
            filtros.append(Notificacion.archivada == False)

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
        """
        Cuenta las notificaciones no leídas de un usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Número de notificaciones no leídas
        """
        cache_key = generar_cache_key("notificaciones_no_leidas", str(usuario_id))
        count = self.cache.get(cache_key)

        if count is not None:
            return count

        stmt = select(func.count(Notificacion.id)).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leida == False,
                Notificacion.archivada == False,
                Notificacion.eliminado == False
            )
        )

        result = await self.session.execute(stmt)
        count = result.scalar() or 0

        # Cachear por 5 minutos
        self.cache.set(cache_key, count, ttl=300)

        return count

    async def marcar_como_leida(self, notificacion_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        """
        Marca una notificación como leída.

        Args:
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario (para validación)

        Returns:
            True si se marcó correctamente
        """
        result = await self.session.execute(
            select(Notificacion).where(
                Notificacion.id == notificacion_id,
                Notificacion.usuario_id == usuario_id
            )
        )
        notificacion = result.scalar_one_or_none()

        if not notificacion:
            logger.warning(f"Notificación {notificacion_id} no encontrada para usuario {usuario_id}")
            return False

        notificacion.marcar_como_leida()
        await self.session.commit()

        # Invalidar caché
        cache_key = generar_cache_key("notificaciones_no_leidas", str(usuario_id))
        self.cache.delete(cache_key)

        logger.info(f"Notificación {notificacion_id} marcada como leída")
        return True

    async def marcar_todas_como_leidas(self, usuario_id: uuid.UUID) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas.

        Args:
            usuario_id: ID del usuario

        Returns:
            Número de notificaciones marcadas
        """
        stmt = select(Notificacion).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leida == False,
                Notificacion.eliminado == False
            )
        )

        result = await self.session.execute(stmt)
        notificaciones = result.scalars().all()

        count = 0
        for notificacion in notificaciones:
            notificacion.marcar_como_leida()
            count += 1

        await self.session.commit()

        # Invalidar caché
        cache_key = generar_cache_key("notificaciones_no_leidas", str(usuario_id))
        self.cache.delete(cache_key)

        logger.info(f"{count} notificaciones marcadas como leídas para usuario {usuario_id}")
        return count

    async def archivar_notificacion(self, notificacion_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        """
        Archiva una notificación.

        Args:
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario (para validación)

        Returns:
            True si se archivó correctamente
        """
        result = await self.session.execute(
            select(Notificacion).where(
                Notificacion.id == notificacion_id,
                Notificacion.usuario_id == usuario_id
            )
        )
        notificacion = result.scalar_one_or_none()

        if not notificacion:
            return False

        notificacion.archivar()
        await self.session.commit()

        logger.info(f"Notificación {notificacion_id} archivada")
        return True

    async def limpiar_notificaciones_antiguas(self, dias: int = 90) -> int:
        """
        Elimina notificaciones antiguas (soft delete).

        Args:
            dias: Días de antigüedad para considerar

        Returns:
            Número de notificaciones eliminadas
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias)

        stmt = select(Notificacion).where(
            and_(
                Notificacion.fecha_creacion < fecha_limite,
                or_(
                    Notificacion.leida == True,
                    Notificacion.archivada == True
                ),
                Notificacion.eliminado == False
            )
        )

        result = await self.session.execute(stmt)
        notificaciones = result.scalars().all()

        count = 0
        for notificacion in notificaciones:
            notificacion.soft_delete()
            count += 1

        await self.session.commit()

        logger.info(f"{count} notificaciones antiguas eliminadas")
        return count

    async def enviar_notificacion_batch(
        self,
        tipo_codigo: str,
        usuarios_ids: List[uuid.UUID],
        titulo: str,
        mensaje: str,
        canal: str = 'INAPP',
        datos_adicionales: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Envía una notificación a múltiples usuarios.

        Args:
            tipo_codigo: Código del tipo de notificación
            usuarios_ids: Lista de IDs de usuarios
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            canal: Canal de envío
            datos_adicionales: Datos extra

        Returns:
            Número de notificaciones creadas
        """
        count = 0
        for usuario_id in usuarios_ids:
            try:
                await self.crear_notificacion(
                    tipo_codigo=tipo_codigo,
                    usuario_id=usuario_id,
                    titulo=titulo,
                    mensaje=mensaje,
                    canal=canal,
                    datos_adicionales=datos_adicionales
                )
                count += 1
            except Exception as e:
                logger.error(f"Error creando notificación para usuario {usuario_id}: {e}")

        logger.info(f"{count} notificaciones creadas en batch")
        return count

    async def obtener_preferencias_usuario(
        self,
        usuario_id: uuid.UUID,
        tipo_codigo: Optional[str] = None
    ) -> List[PreferenciaNotificacion]:
        """
        Obtiene las preferencias de notificación de un usuario.

        Args:
            usuario_id: ID del usuario
            tipo_codigo: Código del tipo (opcional, para filtrar)

        Returns:
            Lista de preferencias
        """
        filtros = [
            PreferenciaNotificacion.usuario_id == usuario_id,
            PreferenciaNotificacion.eliminado == False
        ]

        if tipo_codigo:
            # Obtener tipo
            result = await self.session.execute(
                select(TipoNotificacion).where(TipoNotificacion.codigo == tipo_codigo)
            )
            tipo = result.scalar_one_or_none()
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
        frecuencia: Optional[str] = None
    ) -> PreferenciaNotificacion:
        """
        Actualiza o crea una preferencia de notificación.

        Args:
            usuario_id: ID del usuario
            tipo_codigo: Código del tipo de notificación
            email_habilitado: Habilitar email
            sms_habilitado: Habilitar SMS
            push_habilitado: Habilitar push
            inapp_habilitado: Habilitar in-app
            frecuencia: Frecuencia de envío

        Returns:
            Preferencia actualizada
        """
        # Obtener tipo
        result = await self.session.execute(
            select(TipoNotificacion).where(TipoNotificacion.codigo == tipo_codigo)
        )
        tipo = result.scalar_one_or_none()

        if not tipo:
            raise ValueError(f"Tipo de notificación no encontrado: {tipo_codigo}")

        # Buscar preferencia existente
        result = await self.session.execute(
            select(PreferenciaNotificacion).where(
                and_(
                    PreferenciaNotificacion.usuario_id == usuario_id,
                    PreferenciaNotificacion.tipo_id == tipo.id,
                    PreferenciaNotificacion.eliminado == False
                )
            )
        )
        preferencia = result.scalar_one_or_none()

        if not preferencia:
            # Crear nueva
            preferencia = PreferenciaNotificacion(
                id=uuid.uuid4(),
                usuario_id=usuario_id,
                tipo_id=tipo.id
            )
            self.session.add(preferencia)

        # Actualizar campos
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

        logger.info(f"Preferencia actualizada para usuario {usuario_id}, tipo {tipo_codigo}")
        return preferencia
