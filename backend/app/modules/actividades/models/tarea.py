"""Tarea — unidad mínima de trabajo asignable y rastreable."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Tarea(BaseModel):
    """Tarea asignable. Pertenece a una Actividad o directamente a un GrupoTrabajo."""
    __tablename__ = 'tareas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    prioridad: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1=Alta 2=Media 3=Baja
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_tarea.id'), nullable=False, index=True)
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('contactos.id'), nullable=True, index=True
    )

    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    horas_reales: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    habilidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('habilidades.id', ondelete='SET NULL'), nullable=True, index=True
    )
    nivel_habilidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_habilidad.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Al menos uno de los dos debe estar poblado:
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=True, index=True
    )
    grupo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('grupos_trabajo.id'), nullable=True, index=True
    )

    estado = relationship('EstadoTarea', foreign_keys=[estado_id], lazy='selectin')
    responsable = relationship('Contacto', foreign_keys=[responsable_id], lazy='selectin')
    habilidad = relationship('Habilidad', foreign_keys=[habilidad_id], lazy='selectin')
    nivel_habilidad = relationship('NivelHabilidad', foreign_keys=[nivel_habilidad_id], lazy='selectin')
    actividad = relationship('Actividad', back_populates='tareas', foreign_keys=[actividad_id], lazy='selectin')
    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Tarea(titulo='{self.titulo}')>"
