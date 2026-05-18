"""Balance contable de sumas y saldos (para reportes)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, Numeric, DateTime, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .....infrastructure.base_model import BaseModel


class BalanceContable(BaseModel):
    """Balance de sumas y saldos generado para un ejercicio."""
    __tablename__ = "balances_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    total_debe: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    total_haber: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<BalanceContable(ejercicio={self.ejercicio}, debe={self.total_debe}, haber={self.total_haber})>"

    @property
    def esta_equilibrado(self) -> bool:
        return self.total_debe == self.total_haber
