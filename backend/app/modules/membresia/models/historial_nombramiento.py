"""Histórico universal de nombramientos de cargos (roles organizacionales) a miembros.

Cada nombramiento apunta directamente a un Rol de tipo ORGANIZACION,
eliminando la duplicidad con TipoCargo/CargoJunta.

Modelo simplificado:
  - UsuarioRol con rol organizacional = nombramiento activo
  - HistorialNombramiento = traza de todos los cambios (altas, bajas, reasignaciones)
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Uuid, Date, Text, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class HistorialNombramiento(BaseModel):
    """Registro histórico de un cargo (rol organizacional) asignado a un miembro.

    Cubre todos los tipos de cargo a través de roles:
    - Junta directiva (presidente, secretario, tesorero, vocal…)
    - Coordinador territorial / autonómico
    - Cualquier otro rol de tipo ORGANIZACION

    La vigencia se determina por fecha_fin IS NULL.
    """
    __tablename__ = 'historial_nombramientos'
    __table_args__ = (
        Index('ix_hist_nombr_miembro', 'miembro_id'),
        Index('ix_hist_nombr_agrupacion', 'agrupacion_id'),
        Index('ix_hist_nombr_rol', 'rol_id'),
        Index('ix_hist_nombr_vigente', 'miembro_id', 'fecha_inicio', 'fecha_fin'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Entidades principales
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='RESTRICT'), nullable=False
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False
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
    # 'JUNTA', 'MANUAL', 'MIGRACION', 'SEED'
    origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)

    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship('Miembro', lazy='selectin')
    rol = relationship('Rol', lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')

    @property
    def es_vigente(self) -> bool:
        """True si el nombramiento está actualmente activo."""
        return self.fecha_fin is None

    def __repr__(self) -> str:
        return (
            f"<HistorialNombramiento("
            f"miembro_id='{self.miembro_id}', "
            f"rol='{self.rol_id}', "
            f"inicio={self.fecha_inicio})>"
        )
