"""Catálogo de conceptos de donación."""

import uuid
from typing import Optional

from sqlalchemy import String, Boolean, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class DonacionConcepto(BaseModel):
    __tablename__ = "donaciones_conceptos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    donaciones = relationship('Donacion', back_populates='concepto', lazy='selectin')

    def __repr__(self) -> str:
        return f"<DonacionConcepto(nombre='{self.nombre}')>"
