"""Apunte de caja: movimiento real de dinero en una cuenta bancaria."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoApunte(PyEnum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    TRANSFERENCIA = "TRANSFERENCIA"


# Alias para compatibilidad con el servicio legacy
TipoMovimientoTesoreria = TipoApunte


class OrigenApunte(PyEnum):
    CUOTA = "CUOTA"
    DONACION = "DONACION"
    REMESA = "REMESA"
    ACTIVIDAD = "ACTIVIDAD"
    PAYPAL = "PAYPAL"
    MANUAL = "MANUAL"


class ApunteCaja(BaseModel):
    """Apunte de caja: movimiento de dinero en una cuenta bancaria.

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

    # Referencia polimórfica al evento de negocio origen
    entidad_origen_tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entidad_origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)
    referencia_externa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_conciliacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Solo versión COMPLETA
    asiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("asientos_contables.id"), nullable=True, index=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuenta_bancaria = relationship('CuentaBancaria', back_populates='apuntes', lazy='selectin')
    asiento = relationship('AsientoContable', foreign_keys=[asiento_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<ApunteCaja(tipo={self.tipo}, importe={self.importe}, fecha={self.fecha})>"

    @property
    def es_ingreso(self) -> bool:
        return self.tipo == TipoApunte.INGRESO

    @property
    def es_gasto(self) -> bool:
        return self.tipo == TipoApunte.GASTO


# Alias de compatibilidad con nombre legacy
MovimientoTesoreria = ApunteCaja
