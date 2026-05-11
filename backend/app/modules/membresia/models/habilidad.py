"""Catálogo de habilidades de interés para la asociación."""

import uuid
from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Uuid, Boolean, UniqueConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .categoria_habilidad import CategoriaHabilidad
    from .nivel_habilidad import NivelHabilidad


class Habilidad(BaseModel):
    """Habilidad del catálogo de la asociación."""
    __tablename__ = 'habilidades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('categorias_habilidad.id', ondelete='SET NULL'), nullable=True, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    categoria: Mapped[Optional['CategoriaHabilidad']] = relationship(
        'CategoriaHabilidad', back_populates='habilidades', lazy='selectin'
    )

    miembro_habilidades: Mapped[list['MiembroHabilidad']] = relationship(
        'MiembroHabilidad', back_populates='habilidad', lazy='noload'
    )

    def __repr__(self) -> str:
        return f"<Habilidad(nombre='{self.nombre}', categoria='{self.categoria}')>"


class MiembroHabilidad(BaseModel):
    """Habilidad declarada o validada de un miembro."""
    __tablename__ = 'miembros_habilidades'
    __table_args__ = (
        UniqueConstraint('miembro_id', 'habilidad_id', name='uq_miembro_habilidad'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False, index=True
    )
    habilidad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('habilidades.id', ondelete='CASCADE'), nullable=False, index=True
    )

    nivel_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_habilidad.id', ondelete='SET NULL'), nullable=True, index=True
    )
    validado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )
    fecha_validacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    habilidad: Mapped['Habilidad'] = relationship(
        'Habilidad', back_populates='miembro_habilidades', lazy='selectin'
    )
    nivel_habilidad: Mapped[Optional['NivelHabilidad']] = relationship(
        'NivelHabilidad', back_populates='miembro_habilidades', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<MiembroHabilidad(miembro={self.miembro_id}, habilidad={self.habilidad_id})>"
