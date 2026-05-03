"""Pagos y eventos de pago registrados desde pasarelas externas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Numeric, Text, Uuid, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoPago(BaseModel):
    """Catálogo de tipos de pago (donación, cuota, suscripción...)."""
    __tablename__ = "tipos_pago"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(
        __import__('sqlalchemy').Boolean, default=True, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<TipoPago(nombre='{self.nombre}')>"


class Pago(BaseModel):
    """Transacción registrada en una pasarela externa.

    Cuando estado pasa a COMPLETADO, genera un ApunteCaja en tesorería.
    """
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    proveedor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("proveedores_pago.id"), nullable=False, index=True)
    tipo_pago_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("tipos_pago.id"), nullable=True, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_pago.id"), nullable=False, index=True)
    suscripcion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("suscripciones.id"), nullable=True, index=True)

    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    email_pagador: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=True, index=True)

    id_externo_principal: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    id_externo_secundario: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    datos_externos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    fecha_completado: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    proveedor = relationship('ProveedorPago', lazy='selectin')
    tipo_pago = relationship('TipoPago', lazy='selectin')
    estado = relationship('EstadoPago', foreign_keys=[estado_id], lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    suscripcion = relationship('Suscripcion', back_populates='pagos', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Pago(importe={self.importe}, proveedor_id='{self.proveedor_id}')>"


class EventoPago(BaseModel):
    """Webhook o evento recibido desde una pasarela."""
    __tablename__ = "eventos_pago"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pago_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("pagos.id"), nullable=True, index=True)
    proveedor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("proveedores_pago.id"), nullable=False, index=True)
    tipo_evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tipos_evento_pago.id"), nullable=False, index=True)

    id_evento_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    proveedor = relationship('ProveedorPago', lazy='selectin')
    tipo_evento = relationship('TipoEventoPago', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EventoPago(proveedor_id='{self.proveedor_id}')>"
