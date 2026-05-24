"""Handlers de eventos de dominio para el chat interno.

Conecta los eventos de SIGA (grupos de trabajo) con el ChatBridgeService, que
sincroniza la sala XMPP. Desacoplado: actividades publica el evento, aquí se
reacciona. Registro: `wire_chat_handlers(async_session)` en el lifespan.

Estado de la sincronización de MEMBRESÍA (altas/bajas de miembros del grupo):
hoy las mutaciones de MiembroGrupo son CRUD autogeneradas por strawchemy, sin un
método de servicio donde publicar evento (mismo límite de coherencia que membresía).
Por eso aquí solo se engancha la CREACIÓN del grupo → creación del canal. La
sincronización de membresía se invoca vía ChatBridgeService.sincronizar_membresia_grupo
(manual / job / futura mutation custom). Ver docs/DISENO_CHAT_INTERNO.md.
"""

from __future__ import annotations

import logging
from typing import Callable
from uuid import UUID

from app.core.events import event_bus, GrupoTrabajoCreado

logger = logging.getLogger(__name__)


def wire_chat_handlers(session_factory: Callable) -> None:
    """Suscribe los handlers del chat al event bus."""

    from app.modules.actividades.models.grupo import GrupoTrabajo
    from app.modules.core.comunicacion.mensajeria.chat_bridge_service import ChatBridgeService
    from sqlalchemy import select

    async def _on_grupo_creado(ev: GrupoTrabajoCreado) -> None:
        try:
            gid = UUID(ev.grupo_id)
        except (ValueError, TypeError):
            logger.warning("GrupoTrabajoCreado con grupo_id inválido: %r", ev.grupo_id)
            return
        try:
            async with session_factory() as session:
                bridge = ChatBridgeService(session)
                # Feature flag: si el chat no está activo, el módulo es inerte.
                if not await bridge.chat_activo():
                    return
                grupo = (await session.execute(
                    select(GrupoTrabajo).where(GrupoTrabajo.id == gid)
                )).scalar_one_or_none()
                if grupo is None:
                    logger.warning("GrupoTrabajoCreado: grupo %s no encontrado", gid)
                    return
                await bridge.asegurar_canal_grupo(grupo)
                await bridge.sincronizar_membresia_grupo(gid)
        except Exception:
            logger.exception("Fallo creando el canal de chat del grupo %s", ev.grupo_id)

    event_bus.subscribe(GrupoTrabajoCreado, _on_grupo_creado)
    logger.info("Chat: handlers de eventos suscritos al event bus.")
