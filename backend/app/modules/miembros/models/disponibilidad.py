"""Franjas de disponibilidad semanal de los miembros."""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class FranjaDisponibilidad(BaseModel):
    """Franja horaria semanal en que un miembro está disponible.

    dia_semana: 0=Lunes, 1=Martes, ..., 6=Domingo
    """
    __tablename__ = 'franjas_disponibilidad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False, index=True
    )

    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)
    hora_inicio: Mapped[str] = mapped_column(String(5), nullable=False)
    hora_fin: Mapped[str] = mapped_column(String(5), nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        dia = dias[self.dia_semana] if 0 <= self.dia_semana <= 6 else '?'
        return f"<FranjaDisponibilidad(miembro={self.miembro_id}, {dia} {self.hora_inicio}-{self.hora_fin})>"
