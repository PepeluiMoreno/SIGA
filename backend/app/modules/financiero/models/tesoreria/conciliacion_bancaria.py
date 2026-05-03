"""Modelo de conciliación bancaria por período.

Distinto de Conciliacion (que es el vínculo línea a línea apunte↔extracto).
ConciliacionBancaria es el registro de cierre de período.
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Date, Numeric, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class ConciliacionBancaria(BaseModel):
    """Registro de conciliación bancaria por período.

    Compara el saldo del extracto bancario con el saldo del sistema
    para un período dado. Se confirma cuando diferencia == 0.
    """
    __tablename__ = "conciliaciones_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuenta_bancaria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True
    )

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)

    saldo_inicial_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_inicial_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    diferencia: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_conciliacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    cuenta_bancaria = relationship("CuentaBancaria", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<ConciliacionBancaria(cuenta={self.cuenta_bancaria_id}, "
            f"{self.fecha_inicio}/{self.fecha_fin}, diff={self.diferencia})>"
        )

    @property
    def esta_equilibrada(self) -> bool:
        return self.diferencia == Decimal("0")
