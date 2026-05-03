"""Lote de cobros SEPA."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class Remesa(BaseModel):
    __tablename__ = "remesas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    referencia: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    fecha_envio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_cobro: Mapped[date] = mapped_column(Date, nullable=False)

    importe_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    gastos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    num_ordenes: Mapped[int] = mapped_column(default=0, nullable=False)

    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_remesa.id"), nullable=False, index=True)
    archivo_sepa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mensaje_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ordenes: Mapped[List["OrdenCobro"]] = relationship(back_populates="remesa", lazy="selectin")
    estado = relationship('EstadoRemesa', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Remesa(referencia='{self.referencia}', importe={self.importe_total})>"

    @property
    def importe_neto(self) -> Decimal:
        return self.importe_total - self.gastos
