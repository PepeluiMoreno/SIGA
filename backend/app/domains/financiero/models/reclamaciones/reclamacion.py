"""Proceso de reclamación de impago sobre una cuota."""

import uuid
from typing import Optional

from sqlalchemy import Integer, ForeignKey, Uuid, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class Reclamacion(BaseModel):
    """Proceso de reclamación abierto sobre una CuotaAnual impagada."""
    __tablename__ = "reclamaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cuota_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cuotas_anuales.id"), nullable=False, index=True
    )

    # nivel: 1=Primera, 2=Segunda, 3=Tercera
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # estado: FK a estados_reclamacion (catálogo)
    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("estados_reclamacion.id"), nullable=False, index=True
    )

    # gestor asignado (opcional)
    gestor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True, index=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cuota = relationship('CuotaAnual', lazy='selectin')
    estado = relationship('EstadoReclamacion', foreign_keys=[estado_id], lazy='selectin')
    acciones = relationship('AccionReclamacion', back_populates='reclamacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Reclamacion(cuota_id='{self.cuota_id}', nivel={self.nivel})>"
