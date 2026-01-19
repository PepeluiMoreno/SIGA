"""Modelos relacionados con donaciones."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Boolean, Text, Uuid, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel
from .cuotas import ModoIngreso


class DonacionConcepto(BaseModel):
    """Conceptos de donación predefinidos."""
    __tablename__ = "donaciones_conceptos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    donaciones = relationship('Donacion', back_populates='concepto', lazy='selectin')

    def __repr__(self) -> str:
        return f"<DonacionConcepto(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Donacion(BaseModel):
    """Donaciones de miembros o externos."""
    __tablename__ = "donaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # TODO: ForeignKey("miembros.id")
    concepto_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("donaciones_conceptos.id"), nullable=True, index=True)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # TODO: ForeignKey("campanias.id")

    # Datos del donante externo (si no es miembro)
    donante_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    donante_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    donante_telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    donante_dni: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Importes
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    gastos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    # Información de pago
    fecha: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)
    modo_ingreso: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Estado (FK a EstadoDonacion)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_donacion.id"), nullable=False, index=True)

    # Certificado fiscal
    certificado_emitido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_certificado: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    # TODO: Descomentar cuando existan los modelos
    # miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    concepto = relationship('DonacionConcepto', back_populates='donaciones', lazy='selectin')
    # campania = relationship('Campania', foreign_keys=[campania_id], lazy='selectin')
    estado = relationship('EstadoDonacion', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Donacion(importe={self.importe}, fecha={self.fecha}, estado_id='{self.estado_id}')>"

    @property
    def importe_neto(self) -> Decimal:
        """Calcula el importe neto después de gastos."""
        return self.importe - self.gastos

    @property
    def es_deducible(self) -> bool:
        """Verifica si la donación es deducible fiscalmente."""
        # Una donación es deducible si tiene DNI del donante y no es anónima
        return bool(self.donante_dni or (self.miembro_id and not self.anonima))

    def emitir_certificado(self) -> None:
        """Marca la donación como certificada."""
        if not self.certificado_emitido:
            self.certificado_emitido = True
            self.fecha_certificado = date.today()
            # TODO: self.estado_id = # buscar estado 'CERTIFICADA'
