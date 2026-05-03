"""Histórico de agrupaciones territoriales por las que ha pasado un miembro."""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Uuid, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class HistorialAgrupacion(BaseModel):
    """Registro de pertenencia de un miembro a una agrupación territorial.

    fecha_fin=None significa la agrupación actual.
    """
    __tablename__ = 'historial_agrupaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False, index=True
    )
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=False, index=True
    )

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    miembro = relationship('Miembro', lazy='selectin')

    def __repr__(self) -> str:
        fin = self.fecha_fin or 'actual'
        return f"<HistorialAgrupacion(miembro={self.miembro_id}, {self.fecha_inicio}→{fin})>"
