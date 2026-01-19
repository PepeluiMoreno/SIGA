"""Catálogos y tipos para actividades."""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, Uuid, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoActividad(BaseModel):
    """Tipos de actividades."""
    __tablename__ = 'tipos_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Configuración
    requiere_grupo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requiere_presupuesto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    actividades = relationship('Actividad', back_populates='tipo_actividad', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoActividad(codigo='{self.codigo}', nombre='{self.nombre}')>"


class EstadoPropuesta(BaseModel):
    """Estados de propuestas de actividad."""
    __tablename__ = 'estados_propuesta'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    es_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    propuestas = relationship('PropuestaActividad', back_populates='estado', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EstadoPropuesta(codigo='{self.codigo}', nombre='{self.nombre}')>"


class TipoRecurso(BaseModel):
    """Tipos de recursos para actividades."""
    __tablename__ = 'tipos_recurso'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requiere_importe: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<TipoRecurso(codigo='{self.codigo}', nombre='{self.nombre}')>"


class TipoKPI(BaseModel):
    """Tipos de KPIs para medir actividades."""
    __tablename__ = 'tipos_kpi'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    formato: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # NUMERICO, PORCENTAJE, MONEDA
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    kpis = relationship('KPI', back_populates='tipo_kpi', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoKPI(codigo='{self.codigo}', nombre='{self.nombre}')>"
