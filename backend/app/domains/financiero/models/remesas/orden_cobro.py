"""Orden individual dentro de una remesa SEPA."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class OrdenCobro(BaseModel):
    __tablename__ = "ordenes_cobro"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    remesa_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("remesas.id"), nullable=False, index=True)
    cuota_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cuotas_anuales.id"), nullable=False, index=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    referencia_mandato: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)

    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_orden_cobro.id"), nullable=False, index=True)
    fecha_procesamiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    codigo_rechazo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    remesa: Mapped["Remesa"] = relationship(back_populates="ordenes", lazy="selectin")
    cuota = relationship('CuotaAnual', foreign_keys=[cuota_id], back_populates='ordenes_cobro', lazy='selectin')
    estado = relationship('EstadoOrdenCobro', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<OrdenCobro(cuota_id='{self.cuota_id}', importe={self.importe})>"
