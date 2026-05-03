"""Modelos relacionados con tesorería: cuentas bancarias y movimientos."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Enum, Text, Uuid, Integer, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoMovimientoTesoreria(PyEnum):
    """Tipos de movimiento en tesorería."""
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    TRASPASO = "TRASPASO"


class CuentaBancaria(BaseModel):
    """Cuenta bancaria de la organización."""
    __tablename__ = "cuentas_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    iban: Mapped[str] = mapped_column(String(500), nullable=False)  # Encriptado
    bic_swift: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    banco_nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("agrupaciones_territoriales.id"), nullable=True, index=True)

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    agrupacion = relationship('AgrupacionTerritorial', foreign_keys=[agrupacion_id], lazy='selectin')
    movimientos: Mapped[List["MovimientoTesoreria"]] = relationship(back_populates="cuenta", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CuentaBancaria(nombre='{self.nombre}', iban='{self.iban[-4:]}', saldo={self.saldo_actual})>"

    @property
    def saldo_disponible(self) -> Decimal:
        return self.saldo_actual


class MovimientoTesoreria(BaseModel):
    """Movimiento de efectivo en una cuenta bancaria."""
    __tablename__ = "movimientos_tesoreria"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuenta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tipo: Mapped[str] = mapped_column(Enum(TipoMovimientoTesoreria), nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)

    referencia_externa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Referencia polimórfica al evento de negocio origen
    entidad_origen_tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entidad_origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_conciliacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    asiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("asientos_contables.id"), nullable=True, index=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuenta = relationship('CuentaBancaria', back_populates="movimientos", lazy='selectin')
    asiento = relationship('AsientoContable', foreign_keys=[asiento_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<MovimientoTesoreria(fecha={self.fecha}, tipo='{self.tipo}', importe={self.importe})>"

    @property
    def es_ingreso(self) -> bool:
        return self.tipo == TipoMovimientoTesoreria.INGRESO

    @property
    def es_gasto(self) -> bool:
        return self.tipo == TipoMovimientoTesoreria.GASTO


class ConciliacionBancaria(BaseModel):
    """Registro de conciliación bancaria por período."""
    __tablename__ = "conciliaciones_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuenta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cuentas_bancarias.id"), nullable=False, index=True)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)

    saldo_inicial_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_extracto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_inicial_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_final_sistema: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    conciliado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_conciliacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    diferencia: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuenta = relationship('CuentaBancaria', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ConciliacionBancaria(cuenta={self.cuenta_id}, {self.fecha_inicio}/{self.fecha_fin}, conciliado={self.conciliado})>"

    @property
    def esta_equilibrada(self) -> bool:
        return self.diferencia == Decimal('0.00')
