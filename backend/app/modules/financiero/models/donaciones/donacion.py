"""Donaciones nominativas y anónimas."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Boolean, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class Donacion(BaseModel):
    """Donación. Representa el hecho de negocio, no el apunte de caja."""
    __tablename__ = "donaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=True, index=True)
    concepto_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("donaciones_conceptos.id"), nullable=True, index=True)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("campanias.id"), nullable=True, index=True)

    donante_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    donante_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    donante_telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    donante_dni: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    gastos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    fecha: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)

    # modo_ingreso: FK a modos_ingreso (catálogo), no string libre
    modo_ingreso_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("modos_ingreso.id"), nullable=True, index=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_donacion.id"), nullable=False, index=True)

    certificado_emitido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_certificado: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    concepto = relationship('DonacionConcepto', back_populates='donaciones', lazy='selectin')
    campania = relationship('Campania', foreign_keys=[campania_id], lazy='selectin')
    estado = relationship('EstadoDonacion', foreign_keys=[estado_id], lazy='selectin')
    modo_ingreso = relationship('ModoIngreso', foreign_keys=[modo_ingreso_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Donacion(importe={self.importe}, fecha={self.fecha})>"

    @property
    def importe_neto(self) -> Decimal:
        return self.importe - self.gastos

    @property
    def es_deducible(self) -> bool:
        return bool(self.donante_dni or (self.miembro_id and not self.anonima))
