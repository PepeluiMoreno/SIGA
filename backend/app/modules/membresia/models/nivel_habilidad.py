"""Catálogo de niveles de habilidad / experiencia."""

import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .habilidad import MiembroHabilidad


class NivelHabilidad(BaseModel):
    __tablename__ = 'niveles_habilidad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    miembro_habilidades: Mapped[list['MiembroHabilidad']] = relationship(
        'MiembroHabilidad', back_populates='nivel_habilidad', lazy='noload'
    )

    def __repr__(self) -> str:
        return f"<NivelHabilidad(nombre='{self.nombre}')>"
