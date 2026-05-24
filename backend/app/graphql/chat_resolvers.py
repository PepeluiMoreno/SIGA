"""Resolvers GraphQL del chat interno.

SIGA expone SOLO lo suyo: el estado de los canales del usuario y la administración
del vínculo (reintentar sincronización, archivar). El envío y la lectura de
mensajes NO pasan por aquí: los hace el cliente (Conversations) directamente
contra ejabberd. La creación de canales es automática (evento de grupo), no manual.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import strawberry

from app.graphql.permissions import RequireAuthenticated, RequireTransaction
from app.modules.core.comunicacion.mensajeria.chat_bridge_service import ChatBridgeService
from app.modules.core.comunicacion.mensajeria.models import CanalChat


@strawberry.type
class CanalChatType:
    """Estado de un canal de chat (vínculo SIGA ↔ sala XMPP)."""
    id: uuid.UUID
    origen: str
    origen_id: uuid.UUID
    sala_jid: str
    nombre: Optional[str]
    estado_sync: str
    ultimo_sync: Optional[datetime]
    ultimo_error: Optional[str]
    fecha_archivado: Optional[datetime]
    archivado: bool

    @classmethod
    def from_model(cls, c: CanalChat) -> "CanalChatType":
        return cls(
            id=c.id,
            origen=c.origen.value if hasattr(c.origen, "value") else str(c.origen),
            origen_id=c.origen_id,
            sala_jid=c.sala_jid,
            nombre=c.nombre,
            estado_sync=c.estado_sync.value if hasattr(c.estado_sync, "value") else str(c.estado_sync),
            ultimo_sync=c.ultimo_sync,
            ultimo_error=c.ultimo_error,
            fecha_archivado=c.fecha_archivado,
            archivado=c.fecha_archivado is not None,
        )


@strawberry.type
class ResultadoOperacionCanal:
    exito: bool
    mensaje: str = ""
    canal: Optional[CanalChatType] = None


@strawberry.type
class ChatQuery:

    @strawberry.field(permission_classes=[RequireAuthenticated])
    async def mis_canales_chat(self, info: strawberry.Info) -> list[CanalChatType]:
        """Canales de los grupos de trabajo a los que pertenece el usuario."""
        user = info.context.user
        if user is None:
            return []
        bridge = ChatBridgeService(info.context.session)
        canales = await bridge.mis_canales(user)
        return [CanalChatType.from_model(c) for c in canales]


@strawberry.type
class ChatMutation:

    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def reintentar_sync_canal(
        self, info: strawberry.Info, canal_id: uuid.UUID
    ) -> ResultadoOperacionCanal:
        """Reintenta la sincronización de un canal en estado ERROR."""
        bridge = ChatBridgeService(info.context.session)
        canal = await bridge.reintentar_sync(canal_id)
        if canal is None:
            return ResultadoOperacionCanal(exito=False, mensaje="Canal no encontrado")
        ok = canal.estado_sync.value == "OK" if hasattr(canal.estado_sync, "value") else str(canal.estado_sync) == "OK"
        return ResultadoOperacionCanal(
            exito=ok,
            mensaje="Sincronización correcta" if ok else f"Sincronización falló: {canal.ultimo_error or ''}",
            canal=CanalChatType.from_model(canal),
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("GRUPO_ASIGNAR_MIEMBRO")])
    async def sincronizar_canal_grupo(
        self, info: strawberry.Info, grupo_id: uuid.UUID
    ) -> ResultadoOperacionCanal:
        """Asegura el canal del grupo y sincroniza su membresía con ejabberd.

        Pensada para invocarse desde el frontend tras alta/baja de miembros de un
        grupo (hoy CRUD autogeneradas, sin evento propio). Quien puede asignar
        miembros (GRUPO_ASIGNAR_MIEMBRO) puede sincronizar el canal.
        """
        from sqlalchemy import select
        from app.modules.actividades.models.grupo import GrupoTrabajo

        session = info.context.session
        grupo = (await session.execute(
            select(GrupoTrabajo).where(GrupoTrabajo.id == grupo_id)
        )).scalar_one_or_none()
        if grupo is None:
            return ResultadoOperacionCanal(exito=False, mensaje="Grupo no encontrado")

        bridge = ChatBridgeService(session)
        canal = await bridge.asegurar_canal_grupo(grupo)
        await bridge.sincronizar_membresia_grupo(grupo_id)
        await session.refresh(canal)
        ok = (canal.estado_sync.value if hasattr(canal.estado_sync, "value") else str(canal.estado_sync)) == "OK"
        return ResultadoOperacionCanal(
            exito=ok,
            mensaje="Canal sincronizado" if ok else f"Sincronización con incidencias: {canal.ultimo_error or ''}",
            canal=CanalChatType.from_model(canal),
        )
