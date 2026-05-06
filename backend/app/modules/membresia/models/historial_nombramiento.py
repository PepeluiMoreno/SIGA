"""Histórico universal de nombramientos de cargos a miembros.

Registra TODAS las asignaciones de cargos (junta directiva, coordinadores
territoriales, etc.) con trazabilidad completa: quién, qué cargo, dónde
(agrupación), desde cuándo, hasta cuándo y por qué motivo.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Uuid, Date, Text, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class HistorialNombramiento(BaseModel):
    """Registro histórico de un cargo asignado a un miembro.

    Cubre todos los tipos de cargo:
    - Junta directiva (presidente, secretario, tesorero, vocal…)
    - Coordinador territorial / autonómico
    - Cualquier otro cargo definido en TipoCargo

    La relación con el modelo específico (JuntaDirectiva, CoordinacionTerritorial,
    etc.) es opcional y se mantiene mediante tipo_origen + origen_id.
    """
    __tablename__ = 'historial_nombramientos'
    __table_args__ = (
        Index('ix_hist_nombr_miembro', 'miembro_id'),
        Index('ix_hist_nombr_agrupacion', 'agrupacion_id'),
        Index('ix_hist_nombr_vigente', 'miembro_id', 'fecha_inicio', 'fecha_fin'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Entidades principales
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='RESTRICT'), nullable=False
    )
    tipo_cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('tipos_cargo.id', ondelete='RESTRICT'), nullable=False
    )

    # Ámbito territorial (NULL si es cargo global de la organización)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('agrupaciones_territoriales.id', ondelete='SET NULL'), nullable=True
    )

    # Período
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Trazabilidad: origen del nombramiento
    tipo_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # 'JUNTA', 'COORDINACION', 'MANUAL', 'MIGRACION'
    origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)

    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship('Miembro', lazy='selectin')
    tipo_cargo = relationship('TipoCargo', lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')

    @property
    def es_vigente(self) -> bool:
        """True si el nombramiento está actualmente activo."""
        return self.fecha_fin is None

    def __repr__(self) -> str:
        return (
            f"<HistorialNombramiento("
            f"miembro_id='{self.miembro_id}', "
            f"cargo='{self.tipo_cargo_id}', "
            f"inicio={self.fecha_inicio})>"
        )
