"""Proceso de reclamación de impago sobre una cuota."""

import uuid
from typing import Optional

from sqlalchemy import String, Boolean, Integer, ForeignKey, Uuid, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class EstadoReclamacion(BaseModel):
    """Estados del proceso de reclamación (ABIERTA, RESUELTA, CERRADA...)."""
    __tablename__ = "estados_reclamacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    es_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<EstadoReclamacion(codigo='{self.codigo}')>"


class Reclamacion(BaseModel):
    """Proceso de reclamación abierto sobre una CuotaAnual impagada."""
    __tablename__ = "reclamaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuota_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuotas_anuales.id"), nullable=False, index=True
    )

    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("estados_reclamacion.id"), nullable=False, index=True
    )

    gestor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True, index=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuota = relationship('CuotaAnual', lazy='selectin')
    estado = relationship('EstadoReclamacion', foreign_keys=[estado_id], lazy='selectin')
    acciones = relationship('AccionReclamacion', back_populates='reclamacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Reclamacion(cuota_id='{self.cuota_id}', nivel={self.nivel})>"
