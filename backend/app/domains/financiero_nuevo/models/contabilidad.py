"""Modelos relacionados con contabilidad: plan de cuentas y asientos contables (PCESFL 2013)."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Enum, Text, Uuid, Integer, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoCuentaContable(PyEnum):
    """Tipos de cuentas contables según PCESFL 2013."""
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    GASTO = "GASTO"


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


class CuentaContable(BaseModel):
    """Plan de cuentas (PCESFL 2013)."""
    __tablename__ = "cuentas_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Código contable (ej: "57200001")
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Jerarquía del plan de cuentas
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=grupo, 2=subgrupo, 3=cuenta
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("cuentas_contables.id"), nullable=True, index=True)
    
    # Tipo de cuenta
    tipo: Mapped[str] = mapped_column(Enum(TipoCuentaContable), nullable=False, index=True)
    
    # Características
    permite_asiento: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Solo cuentas de último nivel
    es_dotacion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Elementos de dotación fundacional
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Relaciones
    padre = relationship('CuentaContable', remote_side=[id], foreign_keys=[padre_id], lazy='selectin')
    hijas: Mapped[List["CuentaContable"]] = relationship(back_populates='padre', lazy='selectin')
    apuntes: Mapped[List["ApunteContable"]] = relationship(back_populates="cuenta", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo='{self.codigo}', nombre='{self.nombre}', tipo='{self.tipo}')>"

    @property
    def es_cuenta_hoja(self) -> bool:
        """Verifica si es una cuenta de último nivel (hoja)."""
        return self.nivel == 3 and self.permite_asiento


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


class BalanceContable(BaseModel):
    """Balance de sumas y saldos (para reportes)."""
    __tablename__ = "balances_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Período
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    # Datos del balance
    total_debe: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    total_haber: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    
    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<BalanceContable(ejercicio={self.ejercicio}, debe={self.total_debe}, haber={self.total_haber})>"

    @property
    def esta_equilibrado(self) -> bool:
        """Verifica si el balance está equilibrado."""
        return self.total_debe == self.total_haber


en vivo

Saltar a en vivo
