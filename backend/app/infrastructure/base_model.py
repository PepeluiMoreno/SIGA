"""Modelo base con auditoría y soft delete para arquitectura async + UUID."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Uuid, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship

from ..core.database import Base


class AuditoriaMixin:
    """Mixin que proporciona campos de auditoría estándar."""

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )
    fecha_eliminacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    eliminado: Mapped[bool] = mapped_column(
        Boolean,
        server_default='false',
        nullable=False,
        index=True
    )

    @declared_attr
    def creado_por_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True)

    @declared_attr
    def modificado_por_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True)

    # Relaciones para auditoría (solo en modelos que heredan)
    # creador y modificador se definen en cada modelo según necesidad


class BaseModel(Base, AuditoriaMixin):
    """Modelo base que incluye auditoría y soft delete."""

    __abstract__ = True

    def soft_delete(self, usuario_id: Optional[uuid.UUID] = None) -> None:
        """Realiza soft delete del registro."""
        self.eliminado = True
        self.fecha_eliminacion = datetime.utcnow()
        if usuario_id:
            self.modificado_por_id = usuario_id

    def restore(self, usuario_id: Optional[uuid.UUID] = None) -> None:
        """Restaura un registro eliminado."""
        self.eliminado = False
        self.fecha_eliminacion = None
        if usuario_id:
            self.modificado_por_id = usuario_id

    @property
    def is_deleted(self) -> bool:
        """Verifica si el registro está eliminado."""
        return self.eliminado

    # Nota: query_active se implementa como método de servicio
    # ya que async SQLAlchemy usa select() en lugar de query()
