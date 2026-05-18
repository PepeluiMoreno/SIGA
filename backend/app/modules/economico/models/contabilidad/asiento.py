"""Asientos contables y apuntes (partida doble)."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Date, Numeric, Enum, Text, Uuid, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoAsientoContable(PyEnum):
    """Tipos de asientos contables."""
    APERTURA = "APERTURA"
    GESTION = "GESTION"
    REGULARIZACION = "REGULARIZACION"
    CIERRE = "CIERRE"
    ANULACION = "ANULACION"


class EstadoAsientoContable(PyEnum):
    """Estados de un asiento contable."""
    BORRADOR = "BORRADOR"
    CONFIRMADO = "CONFIRMADO"
    ANULADO = "ANULADO"


class AsientoContable(BaseModel):
    """Asiento contable (partida doble)."""
    __tablename__ = "asientos_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identificación del asiento
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    numero_asiento: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Descripción
    glosa: Mapped[str] = mapped_column(String(500), nullable=False)

    # Tipo de asiento
    tipo_asiento: Mapped[str] = mapped_column(Enum(TipoAsientoContable), nullable=False)

    # Estado
    estado: Mapped[str] = mapped_column(Enum(EstadoAsientoContable), default=EstadoAsientoContable.BORRADOR, nullable=False)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    apuntes: Mapped[List["ApunteContable"]] = relationship(back_populates="asiento", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AsientoContable(ejercicio={self.ejercicio}, numero={self.numero_asiento}, fecha={self.fecha}, estado='{self.estado}')>"

    @property
    def total_debe(self) -> Decimal:
        """Calcula el total del debe."""
        return sum(apunte.debe for apunte in self.apuntes if apunte.debe)

    @property
    def total_haber(self) -> Decimal:
        """Calcula el total del haber."""
        return sum(apunte.haber for apunte in self.apuntes if apunte.haber)

    @property
    def esta_cuadrado(self) -> bool:
        """Verifica si el asiento está cuadrado (debe = haber)."""
        return self.total_debe == self.total_haber

    def confirmar(self) -> None:
        """Confirma el asiento si está cuadrado."""
        if self.esta_cuadrado:
            self.estado = EstadoAsientoContable.CONFIRMADO
        else:
            raise ValueError(f"El asiento no está cuadrado: Debe={self.total_debe}, Haber={self.total_haber}")

    def anular(self) -> None:
        """Anula el asiento."""
        self.estado = EstadoAsientoContable.ANULADO


class ApunteContable(BaseModel):
    """Apunte contable (línea de un asiento)."""
    __tablename__ = "apuntes_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    asiento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("asientos_contables.id"), nullable=False, index=True)
    cuenta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cuentas_contables.id"), nullable=False, index=True)

    # Importe
    debe: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    haber: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    # Concepto
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)

    # Vinculación a actividad (para seguimiento de fines propios)
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    asiento = relationship('AsientoContable', back_populates="apuntes", lazy='selectin')
    cuenta = relationship('CuentaContable', back_populates="apuntes", lazy='selectin')

    def __repr__(self) -> str:
        return f"<ApunteContable(cuenta='{self.cuenta_id}', debe={self.debe}, haber={self.haber})>"

    @property
    def importe_neto(self) -> Decimal:
        """Retorna el importe neto (debe - haber)."""
        return self.debe - self.haber
