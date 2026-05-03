"""Apuntes de caja: registro de movimientos reales de dinero."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoApunte(PyEnum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    TRANSFERENCIA = "TRANSFERENCIA"


class OrigenApunte(PyEnum):
    CUOTA = "CUOTA"
    DONACION = "DONACION"
    REMESA = "REMESA"
    PAGO = "PAGO"
    MANUAL = "MANUAL"


class ApunteCaja(BaseModel):
    """Registro contable de caja.

    Cada euro que entra o sale queda aquí.
    No es el evento de negocio (cuota/donación), sino el movimiento real en cuenta.

    En versión COMPLETA, cada apunte genera automáticamente un Asiento contable.
    """
    __tablename__ = "apuntes_caja"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    cuenta_bancaria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True
    )

    tipo: Mapped[TipoApunte] = mapped_column(Enum(TipoApunte), nullable=False, index=True)
    origen: Mapped[Optional[OrigenApunte]] = mapped_column(Enum(OrigenApunte), nullable=True, index=True)
    origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("estados_apunte.id"), nullable=False, index=True
    )

    importe: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)

    # Solo versión COMPLETA
    asiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuenta_bancaria = relationship('CuentaBancaria', back_populates='apuntes', lazy='selectin')
    estado = relationship('EstadoApunte', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<ApunteCaja(tipo={self.tipo}, importe={self.importe}, fecha={self.fecha})>"
