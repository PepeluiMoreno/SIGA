"""Extractos bancarios y conciliación."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class MetodoConciliacion(PyEnum):
    AUTOMATICO = "AUTOMATICO"
    MANUAL = "MANUAL"


class ExtractoBancario(BaseModel):
    """Línea importada del CSV/MT940 del banco."""
    __tablename__ = "extractos_bancarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuenta_bancaria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True
    )

    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    concepto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referencia: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    cuenta_bancaria = relationship('CuentaBancaria', back_populates='extractos', lazy='selectin')
    conciliaciones = relationship('Conciliacion', back_populates='extracto', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ExtractoBancario(fecha={self.fecha}, importe={self.importe})>"


class Conciliacion(BaseModel):
    """Vincula un ApunteCaja con un ExtractoBancario."""
    __tablename__ = "conciliaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    apunte_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("apuntes_caja.id"), nullable=False, index=True
    )
    extracto_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("extractos_bancarios.id"), nullable=False, index=True
    )

    metodo: Mapped[MetodoConciliacion] = mapped_column(Enum(MetodoConciliacion), nullable=False)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True, index=True
    )

    apunte = relationship('ApunteCaja', lazy='selectin')
    extracto = relationship('ExtractoBancario', back_populates='conciliaciones', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Conciliacion(apunte_id='{self.apunte_id}', metodo={self.metodo})>"
