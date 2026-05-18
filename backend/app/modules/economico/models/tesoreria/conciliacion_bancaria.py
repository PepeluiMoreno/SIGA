"""Conciliación bancaria por período (cierre de período)."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Date, DateTime, Numeric, Text, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class ConciliacionBancaria(BaseModel):
    """Registro de conciliación bancaria por período (comparación extracto vs sistema)."""
    __tablename__ = "conciliaciones_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuenta_bancaria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True
    )

    # Período de conciliación
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)

    # Datos del extracto bancario
    saldo_inicial_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    # Datos del sistema
    saldo_inicial_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    # Estado de conciliación
    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_conciliacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Diferencias
    diferencia: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    cuenta_bancaria = relationship('CuentaBancaria', back_populates='conciliaciones_periodo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ConciliacionBancaria(cuenta={self.cuenta_bancaria_id}, {self.fecha_inicio} a {self.fecha_fin}, conciliado={self.conciliado})>"

    @property
    def esta_equilibrada(self) -> bool:
        """Verifica si la conciliación está equilibrada."""
        return self.diferencia == Decimal('0.00')
