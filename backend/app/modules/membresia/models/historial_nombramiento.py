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

ESTADOS_NOMBRAMIENTO = ('PENDIENTE', 'EN_REVISION', 'ACTIVO', 'RECHAZADO', 'FINALIZADO')


class HistorialNombramiento(BaseModel):
    """Registro histórico de un cargo orgánico asignado a un miembro.

    Estados:
      PENDIENTE   → creado, pendiente de aprobación (si cargo.requiere_aprobacion)
      EN_REVISION → enviado al aprobador
      ACTIVO      → vigente, los UsuarioRol derivados están activos
      RECHAZADO   → denegado por el aprobador
      FINALIZADO  → cesado, los UsuarioRol derivados están cerrados
    """
    __tablename__ = 'historial_nombramientos'
    __table_args__ = (
        Index('ix_hist_nombr_miembro', 'miembro_id'),
        Index('ix_hist_nombr_agrupacion', 'agrupacion_id'),
        Index('ix_hist_nombr_cargo', 'cargo_id'),
        Index('ix_hist_nombr_estado', 'estado'),
        Index('ix_hist_nombr_vigente', 'miembro_id', 'fecha_inicio', 'fecha_fin'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Entidades principales
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='RESTRICT'), nullable=False
    )
    # Cargo orgánico (catálogo) — nuevo campo; rol_id se mantiene por compatibilidad
    cargo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('cargos.id', ondelete='RESTRICT'), nullable=True, index=True
    )
    # FK a roles (rol organizacional legacy; usar cargo_id en código nuevo)
    rol_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('roles.id', ondelete='RESTRICT'), nullable=True
    )

    # Ámbito organizativo (NULL si es cargo global de la organización)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('unidades_organizativas.id', ondelete='SET NULL'), nullable=True
    )

    # Período
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Estado del flujo de aprobación
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default='ACTIVO', server_default='ACTIVO', index=True
    )
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Trazabilidad
    tipo_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship('Miembro', lazy='selectin')
    cargo = relationship('Cargo', back_populates='nombramientos', lazy='selectin')
    rol = relationship('Rol', lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    aprobado_por = relationship('Usuario', foreign_keys=[aprobado_por_id], lazy='selectin')

    @property
    def es_vigente(self) -> bool:
        return self.estado == 'ACTIVO' and self.fecha_fin is None

    def __repr__(self) -> str:
        return (
            f"<HistorialNombramiento("
            f"miembro_id='{self.miembro_id}', "
            f"cargo_id='{self.cargo_id}', "
            f"estado='{self.estado}', "
            f"inicio={self.fecha_inicio})>"
        )
