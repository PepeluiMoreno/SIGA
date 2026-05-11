"""Modelo raíz JTI para el Plan de Actividades.

PlanActividad es la entidad base unificada que representa cualquier
actividad planificada: campaña, evento o sesión. Las entidades hijas
(Campania, Evento) se vinculan vía plan_id FK única.

Esto permite el Plan Anual de Actividades como una sola query sobre
plan_actividades filtrada por año, mientras cada tipo mantiene sus
campos específicos en su propia tabla.
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Uuid, ForeignKey, Date, Numeric, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class PlanActividad(BaseModel):
    """Registro unificado del Plan de Actividades — raíz JTI.

    Cada campaña, evento o sesión planificada tiene exactamente una fila
    en esta tabla con los campos de planificación comunes. Los campos
    específicos de cada tipo viven en sus tablas especializadas.
    """
    __tablename__ = 'plan_actividades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Discriminador de tipo
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
        # valores: 'campania' | 'evento' | 'sesion'
    )

    # Campos de planificación comunes
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Modalidad temporal
    modalidad: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
        # valores: 'permanente' | 'recurrente' | 'determinada' | 'puntual'
    )

    # Estado de alto nivel del plan (independiente del estado workflow específico)
    estado_plan: Mapped[str] = mapped_column(
        String(20), nullable=False, default='planificado', server_default='planificado'
        # valores: 'planificado' | 'en_curso' | 'finalizado' | 'suspendido' | 'cancelado'
    )

    # Fechas (nullable para actividades permanentes)
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)

    # Organización
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='SET NULL'), nullable=True, index=True
    )
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('agrupaciones_territoriales.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Jerarquía: evento adscrito a campaña, o sub-actividad
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('plan_actividades.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Presupuesto asignado en planificación
    presupuesto_asignado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal('0.00'), server_default='0.00'
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', foreign_keys=[agrupacion_id], lazy='selectin')

    parent: Mapped[Optional['PlanActividad']] = relationship(
        'PlanActividad',
        foreign_keys=[parent_id],
        remote_side='PlanActividad.id',
        back_populates='hijos',
        lazy='selectin',
    )
    hijos: Mapped[List['PlanActividad']] = relationship(
        'PlanActividad',
        foreign_keys=[parent_id],
        back_populates='parent',
        lazy='selectin',
    )

    # Especialización 1:1 (uselist=False porque plan_id es UNIQUE en hijas)
    campania = relationship(
        'Campania', back_populates='plan', uselist=False, lazy='selectin'
    )
    evento = relationship(
        'Evento', back_populates='plan', uselist=False, lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<PlanActividad(tipo='{self.tipo}', nombre='{self.nombre}')>"
