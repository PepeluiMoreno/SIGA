"""Resolvers GraphQL del módulo de Comunicación.

Queries y mutations para que cada usuario consulte y gestione SUS notificaciones
in-app. La creación/emisión de avisos NO se expone aquí como operación de
usuario: la disparan los flujos de trabajo a través de NotificacionService.emitir().
Por eso este resolver solo cubre lectura y gestión del estado propio.

Se apoya en el NotificacionService ya existente y reutiliza el NotificacionType
autogenerado por strawchemy (no se declara un tipo nuevo).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import strawberry

from app.graphql.types_auto import NotificacionType
from app.graphql.permissions import RequireAuthenticated
from app.infrastructure.services.notificacion_service import NotificacionService


@strawberry.type
class ResultadoOperacionNotificacion:
    """Resultado de una mutación sobre notificaciones del propio usuario."""
    exito: bool
    afectadas: int = 0
    mensaje: str = ""


@strawberry.type(name="MensajeEnviado")
class MensajeEnviadoType:
    """Un mensaje de email enviado desde la app (histórico del módulo Comunicación)."""
    id: uuid.UUID
    enviado_en: datetime
    asunto: str
    cuerpo_html: str
    para: str
    cc: Optional[str]
    cco: Optional[str]
    enviados: int
    total: int
    errores: Optional[str]
    remitente_nombre: Optional[str] = None


@strawberry.type
class ComunicacionQuery:

    @strawberry.field(permission_classes=[RequireAuthenticated])
    async def mis_notificaciones(
        self,
        info: strawberry.Info,
        solo_no_leidas: bool = False,
        incluir_archivadas: bool = False,
        limite: int = 50,
        offset: int = 0,
    ) -> list[NotificacionType]:
        """Notificaciones del usuario autenticado, más recientes primero."""
        user = info.context.user
        if user is None:
            return []
        limite = max(1, min(limite, 100))  # cota defensiva de paginación
        service = NotificacionService(info.context.session)
        notificaciones = await service.obtener_notificaciones_usuario(
            usuario_id=user.id,
            solo_no_leidas=solo_no_leidas,
            solo_no_archivadas=not incluir_archivadas,
            limite=limite,
            offset=offset,
        )
        return notificaciones  # strawchemy mapea Notificacion → NotificacionType

    @strawberry.field(permission_classes=[RequireAuthenticated])
    async def firmas_verificadas_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID
    ) -> int:
        """Nº de firmas verificadas (doble opt-in) de una campaña de recogida
        de firmas. Reutiliza el servicio del formulario público para que la
        vista de campaña muestre el progreso de la recogida."""
        from app.modules.actividades.services.firma_publica_service import (
            FirmaPublicaService,
        )

        service = FirmaPublicaService(info.context.session)
        return await service.contar_firmas_verificadas(campania_id)

    @strawberry.field(permission_classes=[RequireAuthenticated])
    async def mensajes_enviados(
        self,
        info: strawberry.Info,
        limite: int = 50,
        offset: int = 0,
    ) -> list[MensajeEnviadoType]:
        """Histórico de mensajes de email enviados desde la app (módulo Comunicación, MVP),
        más recientes primero. Incluye el nombre del remitente (usuario que lo envió)."""
        from sqlalchemy import select
        from app.modules.core.comunicacion.mensajeria import MensajeEnviado
        from app.modules.acceso.models import Usuario
        from app.modules.membresia.models.contacto import Contacto

        session = info.context.session
        limite = max(1, min(limite, 100))  # cota defensiva de paginación
        # Nombre del remitente: el del contacto ligado al usuario; si no lo hay,
        # su username/email (usuarios técnicos sin contacto).
        rows = (await session.execute(
            select(MensajeEnviado, Contacto.nombre, Usuario.username, Usuario.email)
            .outerjoin(Usuario, Usuario.id == MensajeEnviado.remitente_id)
            .outerjoin(Contacto, Contacto.id == Usuario.contacto_id)
            .order_by(MensajeEnviado.enviado_en.desc())
            .limit(limite).offset(max(0, offset))
        )).all()
        return [
            MensajeEnviadoType(
                id=m.id, enviado_en=m.enviado_en, asunto=m.asunto, cuerpo_html=m.cuerpo_html,
                para=m.para, cc=m.cc, cco=m.cco, enviados=m.enviados, total=m.total,
                errores=m.errores, remitente_nombre=(nombre or username or email),
            )
            for m, nombre, username, email in rows
        ]

    @strawberry.field(permission_classes=[RequireAuthenticated])
    async def mis_notificaciones_no_leidas(self, info: strawberry.Info) -> int:
        """Contador de notificaciones no leídas (para el badge del frontend)."""
        user = info.context.user
        if user is None:
            return 0
        service = NotificacionService(info.context.session)
        return await service.contar_no_leidas(user.id)


@strawberry.type
class ComunicacionMutation:

    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def marcar_notificacion_leida(
        self, info: strawberry.Info, notificacion_id: uuid.UUID
    ) -> ResultadoOperacionNotificacion:
        """Marca como leída una notificación propia."""
        user = info.context.user
        service = NotificacionService(info.context.session)
        ok = await service.marcar_como_leida(notificacion_id, user.id)
        return ResultadoOperacionNotificacion(
            exito=ok,
            afectadas=1 if ok else 0,
            mensaje="Notificación marcada como leída" if ok
                    else "Notificación no encontrada",
        )

    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def marcar_todas_notificaciones_leidas(
        self, info: strawberry.Info
    ) -> ResultadoOperacionNotificacion:
        """Marca como leídas todas las notificaciones no leídas del usuario."""
        user = info.context.user
        service = NotificacionService(info.context.session)
        n = await service.marcar_todas_como_leidas(user.id)
        return ResultadoOperacionNotificacion(
            exito=True, afectadas=n,
            mensaje=f"{n} notificaciones marcadas como leídas",
        )

    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def archivar_notificacion(
        self, info: strawberry.Info, notificacion_id: uuid.UUID
    ) -> ResultadoOperacionNotificacion:
        """Archiva una notificación propia (deja de contar como no leída)."""
        user = info.context.user
        service = NotificacionService(info.context.session)
        ok = await service.archivar_notificacion(notificacion_id, user.id)
        return ResultadoOperacionNotificacion(
            exito=ok,
            afectadas=1 if ok else 0,
            mensaje="Notificación archivada" if ok else "Notificación no encontrada",
        )
