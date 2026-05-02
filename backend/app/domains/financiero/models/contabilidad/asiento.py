"""Asientos contables de partida doble. Solo versión COMPLETA."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Integer, Uuid, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoAsientoContable(PyEnum):
    """Tipos de asiento contable según PCESFL 2013."""
    APERTURA = "APERTURA"
    GESTION = "GESTION"
    REGULARIZACION = "REGULARIZACION"
    CIERRE = "CIERRE"


class EstadoAsientoContable(PyEnum):
    """Estados del ciclo de vida de un asiento."""
    BORRADOR = "BORRADOR"
    CONFIRMADO = "CONFIRMADO"
    ANULADO = "ANULADO"


class AsientoContable(BaseModel):
    """Cabecera del asiento contable."""
    __tablename__ = "asientos_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    numero_asiento: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    glosa: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_asiento: Mapped[TipoAsientoContable] = mapped_column(
        Enum(TipoAsientoContable), nullable=False, default=TipoAsientoContable.GESTION
    )
    estado: Mapped[EstadoAsientoContable] = mapped_column(
        Enum(EstadoAsientoContable), nullable=False, default=EstadoAsientoContable.BORRADOR, index=True
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lineas: Mapped[List["ApunteContable"]] = relationship(
        back_populates="asiento", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AsientoContable(numero={self.numero_asiento}, ejercicio={self.ejercicio}, estado={self.estado})>"

    @property
    def total_debe(self) -> Decimal:
        return sum(l.debe or Decimal("0") for l in self.lineas)

    @property
    def total_haber(self) -> Decimal:
        return sum(l.haber or Decimal("0") for l in self.lineas)

    @property
    def esta_cuadrado(self) -> bool:
        return self.total_debe == self.total_haber

    def confirmar(self) -> None:
        if not self.esta_cuadrado:
            raise ValueError(
                f"El asiento no cuadra: debe={self.total_debe}, haber={self.total_haber}"
            )
        if self.estado != EstadoAsientoContable.BORRADOR:
            raise ValueError(f"Solo se pueden confirmar asientos en BORRADOR")
        self.estado = EstadoAsientoContable.CONFIRMADO

    def anular(self) -> None:
        if self.estado == EstadoAsientoContable.ANULADO:
            raise ValueError("El asiento ya está anulado")
        self.estado = EstadoAsientoContable.ANULADO


class ApunteContable(BaseModel):
    """Línea debe/haber de un asiento contable (partida doble)."""
    __tablename__ = "apuntes_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    asiento_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("asientos_contables.id"), nullable=False, index=True
    )
    cuenta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuentas_contables.id"), nullable=False, index=True
    )

    debe: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    haber: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    concepto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Trazabilidad de fines propios vs administración (requisito AEF)
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("actividades.id"), nullable=True, index=True
    )

    asiento: Mapped["AsientoContable"] = relationship(back_populates="lineas", lazy="selectin")
    cuenta = relationship("CuentaContable", lazy="selectin")
    actividad = relationship("Actividad", foreign_keys=[actividad_id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<ApunteContable(cuenta_id='{self.cuenta_id}', debe={self.debe}, haber={self.haber})>"
