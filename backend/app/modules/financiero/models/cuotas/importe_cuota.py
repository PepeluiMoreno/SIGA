"""Tarifas de cuota por tipo de miembro y ejercicio fiscal."""

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Numeric, Text, Uuid, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class ImporteCuotaAnio(BaseModel):
    """Importe de cuota por tipo de miembro y año."""
    __tablename__ = "importes_cuota_anio"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tipo_miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tipos_miembro.id"), nullable=False, index=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    nombre_cuota: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_miembro = relationship('TipoMiembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ImporteCuotaAnio(ejercicio={self.ejercicio}, importe={self.importe})>"
