"""Junta directiva por agrupación territorial, cargos y su histórico.

Modelo:
  AgrupacionTerritorial → JuntaDirectiva (una activa por agrupación)
  JuntaDirectiva → CargoJunta (composición actual con soporte de vocalías variables)
  JuntaDirectiva → HistorialCargoJunta (trazabilidad completa)
  TipoCargo → TipoCargoRol → Rol (roles que se asignan automáticamente al ostentar un cargo)

Vocalías variables:
  TipoCargo.permite_multiples = True permite que un mismo cargo (VOCAL) tenga
  varias posiciones (1, 2, 3…) en la misma junta. La unicidad se garantiza con
  (junta_id, tipo_cargo_id, posicion), donde posicion = 0 para cargos únicos.
"""

import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import (
    String, Boolean, Uuid, ForeignKey, Date, Text,
    UniqueConstraint, Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class JuntaDirectiva(BaseModel):
    """Junta directiva de una agrupación territorial.

    Puede haber varias juntas en el tiempo (renovaciones),
    pero solo una activa simultáneamente por agrupación.
    """
    __tablename__ = 'juntas_directivas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    agrupacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('agrupaciones_territoriales.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_constitucion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_disolucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cargos: Mapped[List["CargoJunta"]] = relationship(
        back_populates="junta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    historial: Mapped[List["HistorialCargoJunta"]] = relationship(
        back_populates="junta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<JuntaDirectiva(agrupacion_id='{self.agrupacion_id}', activa={self.activa})>"


class CargoJunta(BaseModel):
    """Cargo actual en una junta directiva.

    Para cargos únicos (Presidente, Tesorero…) posicion = 0.
    Para vocalías, posicion = 1, 2, 3… según el número de vocalías que tenga la junta.
    La unicidad es (junta_id, tipo_cargo_id, posicion).
    """
    __tablename__ = 'cargos_junta'
    __table_args__ = (
        UniqueConstraint(
            'junta_id', 'tipo_cargo_id', 'posicion',
            name='uq_cargo_junta_posicion',
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    junta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('juntas_directivas.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    tipo_cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('tipos_cargo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('miembros.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    # 0 para cargos únicos; 1, 2, 3… para vocalías adicionales
    posicion: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    junta: Mapped["JuntaDirectiva"] = relationship(back_populates="cargos", lazy="selectin")
    tipo_cargo: Mapped["TipoCargo"] = relationship(lazy="selectin")
    miembro: Mapped["Miembro"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<CargoJunta("
            f"tipo_cargo='{self.tipo_cargo_id}', "
            f"posicion={self.posicion}, "
            f"miembro='{self.miembro_id}')>"
        )


class HistorialCargoJunta(BaseModel):
    """Registro inmutable de todos los cambios en cargos de junta.

    Proporciona trazabilidad completa: quién ocupó qué cargo, desde cuándo y
    hasta cuándo, con el motivo del cambio.
    """
    __tablename__ = 'historial_cargos_junta'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    junta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('juntas_directivas.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    tipo_cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('tipos_cargo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('miembros.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    posicion: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_cambio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    junta: Mapped["JuntaDirectiva"] = relationship(back_populates="historial", lazy="selectin")
    tipo_cargo: Mapped["TipoCargo"] = relationship(lazy="selectin")
    miembro: Mapped["Miembro"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<HistorialCargoJunta("
            f"tipo_cargo='{self.tipo_cargo_id}', "
            f"posicion={self.posicion}, "
            f"miembro='{self.miembro_id}', "
            f"inicio={self.fecha_inicio})>"
        )


class TipoCargoRol(BaseModel):
    """Roles asignados automáticamente al ostentar un tipo de cargo.

    Al asignar un cargo a un miembro, el sistema crea UsuarioRol para cada
    Rol aquí definido, con ámbito en la agrupación de la junta correspondiente.
    """
    __tablename__ = 'tipos_cargo_roles'
    __table_args__ = (
        UniqueConstraint('tipo_cargo_id', 'rol_id', name='uq_tipo_cargo_rol'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    tipo_cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('tipos_cargo.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('roles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    tipo_cargo: Mapped["TipoCargo"] = relationship(back_populates="roles_automaticos", lazy="selectin")
    rol: Mapped["Rol"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<TipoCargoRol(tipo_cargo_id='{self.tipo_cargo_id}', rol_id='{self.rol_id}')>"
