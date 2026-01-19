"""Modelos de campañas y acciones."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoCampania(BaseModel):
    """Tipos de campañas disponibles."""
    __tablename__ = 'tipos_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    campanias = relationship('Campania', back_populates='tipo_campania', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoCampania(codigo='{self.codigo}', nombre='{self.nombre}')>"


class RolParticipante(BaseModel):
    """Roles que pueden tener los participantes en una campaña."""
    __tablename__ = 'roles_participante'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # Características del rol
    es_voluntario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_coordinador: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_donante: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    participantes = relationship('ParticipanteCampania', back_populates='rol_participante', lazy='selectin')

    def __repr__(self) -> str:
        return f"<RolParticipante(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Campania(BaseModel):
    """Campaña de la organización."""
    __tablename__ = 'campanias'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion_corta: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    descripcion_larga: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo y estado
    tipo_campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_campania.id'), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_campania.id'), nullable=False, index=True)

    # Fechas planificadas y reales
    fecha_inicio_plan: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_plan: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_inicio_real: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_real: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Objetivos
    objetivo_principal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_recaudacion: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    meta_participantes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Responsable y ubicación organizativa
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Miembro
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=True, index=True)

    # Relaciones
    tipo_campania = relationship('TipoCampania', back_populates='campanias', lazy='selectin')
    estado = relationship('EstadoCampania', foreign_keys=[estado_id], lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')
    actividades = relationship('Actividad', back_populates='campania', lazy='selectin')
    participantes = relationship('ParticipanteCampania', back_populates='campania', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Campania(codigo='{self.codigo}', nombre='{self.nombre}', estado_id='{self.estado_id}')>"


class ParticipanteCampania(BaseModel):
    """Participantes en una campaña con su rol."""
    __tablename__ = 'participantes_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    rol_participante_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('roles_participante.id'), nullable=False, index=True)

    # Participación
    horas_aportadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Fechas
    fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_confirmacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Observaciones
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    campania = relationship('Campania', back_populates='participantes', lazy='selectin')
    rol_participante = relationship('RolParticipante', back_populates='participantes', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ParticipanteCampania(miembro_id='{self.miembro_id}', rol='{self.rol_participante_id}', confirmado={self.confirmado})>"
