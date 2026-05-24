"""Mensajería interna (chat) — vínculo entre entidades de SIGA y salas de ejabberd.

SIGA NO almacena los mensajes (viven en ejabberd). Solo guarda el VÍNCULO entre
una entidad de SIGA (grupo de trabajo, unidad organizativa) y su sala XMPP, más el
estado de la última sincronización, para trazabilidad y reintento.

Ver docs/DISENO_CHAT_INTERNO.md.
"""

from .models import (
    CanalChat,
    OrigenCanal,
    EstadoSync,
)

__all__ = ["CanalChat", "OrigenCanal", "EstadoSync"]
