"""Suscripciones de pago recurrente en pasarelas externas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Numeric, Uuid, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class Suscripcion(BaseModel):
    __tablename__ = "suscripciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    proveedor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("proveedores_pago.id"), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_suscripcion.id"), nullable=False, index=True)
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=True, index=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    id_externo: Mapped[str] = mapped_column(String(200), nullable=False)

    fecha_proximo_cobro: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    proveedor = relationship('ProveedorPago', lazy='selectin')
    estado = relationship('EstadoSuscripcion', foreign_keys=[estado_id], lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    pagos = relationship('Pago', back_populates='suscripcion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Suscripcion(id_externo='{self.id_externo}', importe={self.importe})>"
