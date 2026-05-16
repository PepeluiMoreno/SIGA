"""Modelo de Actividad — unidad operativa de la ONG (reemplaza Accion)."""

import uuid
from datetime import date, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class TipoActividad(InmutableMixin, BaseModel):
    """Catálogo de tipos de actividad (evento público, reunión, taller, etc.)."""
    __tablename__ = 'tipos_accion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tiene_lugar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tiene_participantes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    actividades = relationship('Actividad', back_populates='tipo_actividad', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoActividad(nombre='{self.nombre}')>"


# Alias de compatibilidad — el catálogo sigue llamándose TipoAccion en muchos sitios
TipoAccion = TipoActividad


class Actividad(BaseModel):
    """Unidad operativa: cualquier actividad concreta que organiza la ONG.

    Si campania_id está presente, es una actividad de campaña (externa/divulgativa).
    Si campania_id es None, es una actividad interna (reunión, asamblea, coordinación).

    Si es_recurrente=True y padre_id=None, es una plantilla de actividad recurrente.
    Si padre_id apunta a otra Actividad, es una instancia de esa plantilla.
    """
    __tablename__ = 'actividades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('tipos_accion.id'), nullable=False, index=True
    )
    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('estados_accion.id'), nullable=False, index=True
    )

    # Recurrencia (auto-referencia)
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=True, index=True
    )
    es_recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodicidad: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 'diaria','semanal','mensual','trimestral','anual','continua'

    # Campaña (si presente → actividad de campaña externa)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('campanias.id'), nullable=True, index=True
    )

    # Grupo de trabajo responsable (opcional)
    grupo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('grupos_trabajo.id'), nullable=True, index=True
    )
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True, index=True
    )

    # Temporal
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    hora_inicio: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    hora_fin: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Presencia física
    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    aforo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    es_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Económico
    presupuesto_estimado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal('0.00'), nullable=False
    )
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal('0.00'), nullable=False
    )

    # Aprobación formal
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas_aprobacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Valoración final
    valoracion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objetivos_cumplidos: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    asistencia_real: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    tipo_actividad = relationship('TipoActividad', back_populates='actividades', lazy='selectin')
    estado = relationship('EstadoAccion', foreign_keys=[estado_id], lazy='selectin')
    aprobado_por = relationship('Usuario', foreign_keys=[aprobado_por_id], lazy='selectin')
    campania = relationship('Campania', foreign_keys=[campania_id], back_populates='actividades', lazy='selectin')
    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    padre = relationship(
        'Actividad', remote_side='Actividad.id',
        foreign_keys=[padre_id], lazy='selectin',
    )
    hijos = relationship(
        'Actividad', back_populates='padre',
        foreign_keys=[padre_id], lazy='selectin',
    )
    tareas = relationship(
        'Tarea', back_populates='actividad',
        foreign_keys='Tarea.actividad_id', lazy='selectin',
    )
    participaciones = relationship('Participacion', back_populates='actividad', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Actividad(nombre='{self.nombre}')>"


# Alias de compatibilidad
Accion = Actividad


class Participacion(BaseModel):
    """Participación de una persona (socio o externo) en una actividad."""
    __tablename__ = 'participaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=False, index=True
    )

    # Uno de los dos debe estar poblado:
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True, index=True
    )
    nombre_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    rol: Mapped[str] = mapped_column(String(50), nullable=False, default='asistente')
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    horas_aportadas: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=Decimal('0.00'), nullable=False
    )

    actividad = relationship('Actividad', back_populates='participaciones', lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Participacion(actividad_id='{self.actividad_id}', rol='{self.rol}')>"
