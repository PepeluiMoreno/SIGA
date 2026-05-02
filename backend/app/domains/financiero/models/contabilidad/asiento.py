"""Asientos contables de partida doble. Solo versión COMPLETA."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Integer, Uuid, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class Asiento(BaseModel):
    """Cabecera del asiento contable."""
    __tablename__ = "asientos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lineas: Mapped[List["LineaAsiento"]] = relationship(
        back_populates='asiento', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<Asiento(numero={self.numero}, ejercicio={self.ejercicio}, fecha={self.fecha})>"

    @property
    def esta_cuadrado(self) -> bool:
        """Verifica que el asiento cuadra (suma debe == suma haber)."""
        debe = sum(l.importe_debe or Decimal('0') for l in self.lineas)
        haber = sum(l.importe_haber or Decimal('0') for l in self.lineas)
        return debe == haber


class LineaAsiento(BaseModel):
    """Línea debe/haber de un asiento contable."""
    __tablename__ = "lineas_asiento"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    asiento_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("asientos.id"), nullable=False, index=True
    )
    cuenta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_contables.id"), nullable=False, index=True
    )

    importe_debe: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    importe_haber: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    concepto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    asiento = relationship('Asiento', back_populates='lineas', lazy='selectin')
    cuenta = relationship('CuentaContable', lazy='selectin')

    def __repr__(self) -> str:
        return f"<LineaAsiento(cuenta_id='{self.cuenta_id}', debe={self.importe_debe}, haber={self.importe_haber})>"
