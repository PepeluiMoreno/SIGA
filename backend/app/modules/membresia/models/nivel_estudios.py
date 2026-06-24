"""Catálogo de niveles de estudios."""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel, InmutableMixin


class NivelEstudios(InmutableMixin, BaseModel):
    __tablename__ = 'niveles_estudios'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)


    def __repr__(self) -> str:
        return f"<NivelEstudios(nombre='{self.nombre}')>"
