"""Modelo de Acción — unidad operativa de la ONG."""

import uuid
from datetime import date, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoAccion(BaseModel):
    """Catálogo de tipos de acción (evento público, reunión, taller, etc.)."""
    __tablename__ = 'tipos_accion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tiene_lugar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tiene_participantes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    acciones = relationship('Accion', back_populates='tipo_accion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoAccion(nombre='{self.nombre}')>"


class Accion(BaseModel):
    """Unidad operativa: cualquier acción concreta que organiza la ONG.

    Reemplaza a Evento y Actividad. El tipo_accion discrimina qué campos
    son relevantes (lugar/aforo para eventos públicos, etc.).
    """
    __tablename__ = 'acciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_accion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_accion.id'), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_accion.id'), nullable=False, index=True)

    # Temporal
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    hora_inicio: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    hora_fin: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Presencia física (solo relevante según tipo_accion.tiene_lugar)
    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    aforo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    es_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Económico
    presupuesto_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)

    # Relaciones organizativas
    iniciativa_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('campanias.id'), nullable=True, index=True
    )
    grupo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('grupos_trabajo.id'), nullable=True, index=True
    )
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True, index=True
    )

    # Relaciones
    tipo_accion = relationship('TipoAccion', back_populates='acciones', lazy='selectin')
    estado = relationship('EstadoAccion', foreign_keys=[estado_id], lazy='selectin')
    iniciativa = relationship('Campania', foreign_keys=[iniciativa_id], back_populates='acciones', lazy='selectin')
    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    tareas = relationship('Tarea', back_populates='accion', foreign_keys='Tarea.accion_id', lazy='selectin')
    participaciones = relationship('Participacion', back_populates='accion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Accion(nombre='{self.nombre}')>"


class Participacion(BaseModel):
    """Participación de una persona (socio o externo) en una acción."""
    __tablename__ = 'participaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    accion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('acciones.id'), nullable=False, index=True)

    # Uno de los dos debe estar poblado:
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True, index=True
    )
    nombre_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    rol: Mapped[str] = mapped_column(String(50), nullable=False, default='asistente')
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    horas_aportadas: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal('0.00'), nullable=False)

    accion = relationship('Accion', back_populates='participaciones', lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Participacion(accion_id='{self.accion_id}', rol='{self.rol}')>"
