"""Modelo Presentacion182 — Flujo 11.

Trazabilidad de las presentaciones del Modelo 182 (AEAT) por ejercicio.
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Date, Numeric, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class Presentacion182(BaseModel):
    """Registro de cada presentación del Modelo 182 a la AEAT."""
    __tablename__ = "presentaciones_modelo_182"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    fecha_envio: Mapped[date] = mapped_column(Date, nullable=False)
    codigo_aeat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    n_donantes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    importe_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    archivo_acuse: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Presentacion182(ejercicio={self.ejercicio}, fecha={self.fecha_envio})>"
