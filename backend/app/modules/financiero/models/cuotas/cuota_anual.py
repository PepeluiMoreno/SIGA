"""Obligación de pago anual de un socio."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class CuotaAnual(BaseModel):
    """Cuota anual de un socio. Representa la obligación, no el pago en caja."""
    __tablename__ = "cuotas_anuales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("agrupaciones_territoriales.id"), nullable=False, index=True)
    importe_cuota_anio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("importes_cuota_anio.id"), nullable=True, index=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    importe_pagado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    gastos_gestion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_cuota.id"), nullable=False, index=True)

    # modo_ingreso: FK a modos_ingreso (catálogo), no enum hardcodeado
    modo_ingreso_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("modos_ingreso.id"), nullable=True, index=True)

    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', foreign_keys=[agrupacion_id], lazy='selectin')
    importe_cuota_anio = relationship('ImporteCuotaAnio', foreign_keys=[importe_cuota_anio_id], lazy='selectin')
    estado = relationship('EstadoCuota', foreign_keys=[estado_id], lazy='selectin')
    modo_ingreso = relationship('ModoIngreso', foreign_keys=[modo_ingreso_id], lazy='selectin')
    ordenes_cobro = relationship('OrdenCobro', back_populates='cuota', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CuotaAnual(miembro_id='{self.miembro_id}', ejercicio={self.ejercicio})>"

    @property
    def esta_pagada(self) -> bool:
        return self.importe_pagado >= self.importe

    @property
    def saldo_pendiente(self) -> Decimal:
        return self.importe - self.importe_pagado
