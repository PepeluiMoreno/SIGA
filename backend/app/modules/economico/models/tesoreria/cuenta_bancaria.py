"""Modelo CuentaBancaria: cuenta bancaria de la organización."""

import uuid
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Boolean, Numeric, Text, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class CuentaBancaria(BaseModel):
    """Cuenta bancaria de la organización."""
    __tablename__ = "cuentas_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    iban: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)  # 500 por encriptación
    bic_swift: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    banco_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    titular: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    saldo_conciliado: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    # FK a unidad organizativa (opcional — cuenta puede ser global o de una delegación)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id"), nullable=True, index=True
    )

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    apuntes: Mapped[List["ApunteCaja"]] = relationship(
        'ApunteCaja', back_populates='cuenta_bancaria', lazy='selectin'
    )
    extractos: Mapped[List["ExtractoBancario"]] = relationship(
        'ExtractoBancario', back_populates='cuenta_bancaria', lazy='selectin'
    )
    conciliaciones_periodo = relationship(
        'ConciliacionBancaria', back_populates='cuenta_bancaria', lazy='selectin'
    )
    agrupacion = relationship('UnidadOrganizativa', foreign_keys=[agrupacion_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<CuentaBancaria(iban='{self.iban[-4:]}', nombre='{self.nombre}')>"

    @property
    def saldo_disponible(self) -> Decimal:
        return self.saldo_actual
