"""Modelo de vínculo SIGA ↔ sala XMPP.

`CanalChat` es la única tabla del módulo en SIGA: asocia una entidad de SIGA
(grupo de trabajo, unidad organizativa) con su sala MUC en ejabberd y registra el
estado de la última sincronización. Los mensajes y la membresía operativa viven en
ejabberd; esta tabla es el índice de trazabilidad y el punto de reintento.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Uuid, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.base_model import BaseModel


class OrigenCanal(str, enum.Enum):
    """De qué entidad de SIGA deriva la membresía del canal."""
    GRUPO_TRABAJO = "GRUPO_TRABAJO"
    UNIDAD_ORGANIZATIVA = "UNIDAD_ORGANIZATIVA"


class EstadoSync(str, enum.Enum):
    """Estado de la última sincronización con ejabberd."""
    PENDIENTE = "PENDIENTE"   # creado en SIGA, aún no propagado a ejabberd
    OK = "OK"                 # última sincronización correcta
    ERROR = "ERROR"           # última sincronización falló (reintentar)


class CanalChat(BaseModel):
    """Vínculo entre una entidad de SIGA y su sala XMPP en ejabberd."""
    __tablename__ = "canales_chat"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Origen: de qué entidad de SIGA deriva este canal.
    origen: Mapped[OrigenCanal] = mapped_column(String(30), nullable=False, index=True)
    # ID de la entidad de origen (grupo_trabajo.id o unidad_organizativa.id).
    origen_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Identidad de la sala en ejabberd: JID del MUC (p. ej. "grupo-<uuid>@conference.dominio").
    sala_jid: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Estado de sincronización con ejabberd.
    estado_sync: Mapped[EstadoSync] = mapped_column(
        String(20), nullable=False, default=EstadoSync.PENDIENTE, index=True
    )
    ultimo_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ultimo_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Archivado: el grupo terminó; la sala se conserva como histórico.
    fecha_archivado: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        # Un canal por entidad de origen.
        UniqueConstraint("origen", "origen_id", name="uq_canal_origen"),
        Index("ix_canal_origen", "origen", "origen_id"),
    )

    def __repr__(self) -> str:
        return f"<CanalChat(origen={self.origen}, origen_id={self.origen_id}, jid={self.sala_jid!r})>"
