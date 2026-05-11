"""Catálogo de categorías de habilidades."""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class CategoriaHabilidad(BaseModel):
    """Categoría que agrupa habilidades del voluntariado."""
    __tablename__ = 'categorias_habilidad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    habilidades: Mapped[list['Habilidad']] = relationship(
        'Habilidad', back_populates='categoria', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<CategoriaHabilidad(nombre='{self.nombre}')>"
