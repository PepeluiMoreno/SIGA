"""Cuentas bancarias de la organización."""

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Boolean, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class CuentaBancaria(BaseModel):
    """Cuenta bancaria real de la organización."""
    __tablename__ = "cuentas_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    iban: Mapped[str] = mapped_column(String(34), unique=True, nullable=False, index=True)
    banco: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    titular: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    saldo_conciliado: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    apuntes = relationship('ApunteCaja', back_populates='cuenta_bancaria', lazy='selectin')
    extractos = relationship('ExtractoBancario', back_populates='cuenta_bancaria', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CuentaBancaria(iban='{self.iban}', nombre='{self.nombre}')>"
