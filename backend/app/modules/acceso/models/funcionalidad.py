"""Funcionalidades del sistema y su relación con roles y transacciones.

Tres capas de autorización:
  1. Rol → RolFuncionalidad → Funcionalidad
  2. Funcionalidad → FuncionalidadTransaccion → Transaccion (con ámbito)
  3. FlujoAprobacion (cadenas de aprobación inter-rol)
"""

import enum
import uuid
from typing import List, Optional

from sqlalchemy import String, Boolean, Uuid, ForeignKey, Enum, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class AmbitoTransaccion(str, enum.Enum):
    """Alcance territorial de una transacción dentro de una funcionalidad."""
    GLOBAL = "GLOBAL"           # sobre cualquier entidad del sistema
    TERRITORIAL = "TERRITORIAL" # solo sobre entidades de su agrupación
    PROPIO = "PROPIO"           # solo sobre entidades con vínculo directo al usuario


class Funcionalidad(BaseModel):
    """Agrupación lógica de transacciones relacionadas.

    Un módulo declara sus funcionalidades en su catalog.py; el servicio de
    sincronización hace upsert sobre esta tabla en arranque.

    Ejemplo: DISENO_CAMPANA agrupa crear_campana, asignar_presupuesto,
    asignar_recursos_humanos, etc.
    """
    __tablename__ = 'funcionalidades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    modulo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[List["RolFuncionalidad"]] = relationship(
        back_populates="funcionalidad",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    transacciones: Mapped[List["FuncionalidadTransaccion"]] = relationship(
        back_populates="funcionalidad",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Funcionalidad(codigo='{self.codigo}', modulo='{self.modulo}')>"


class RolFuncionalidad(BaseModel):
    """Capa 1: asigna una funcionalidad completa a un rol."""
    __tablename__ = 'roles_funcionalidades'
    __table_args__ = (
        UniqueConstraint('rol_id', 'funcionalidad_id', name='uq_rol_funcionalidad'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('roles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    funcionalidad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('funcionalidades.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    rol: Mapped["Rol"] = relationship(back_populates="funcionalidades", lazy="selectin")
    funcionalidad: Mapped["Funcionalidad"] = relationship(back_populates="roles", lazy="selectin")

    def __repr__(self) -> str:
        return f"<RolFuncionalidad(rol_id='{self.rol_id}', funcionalidad_id='{self.funcionalidad_id}')>"


class FuncionalidadTransaccion(BaseModel):
    """Capa 2: vincula transacción a funcionalidad con ámbito territorial."""
    __tablename__ = 'funcionalidades_transacciones'
    __table_args__ = (
        UniqueConstraint(
            'funcionalidad_id', 'transaccion_id',
            name='uq_funcionalidad_transaccion',
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    funcionalidad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('funcionalidades.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    transaccion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('transacciones.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    ambito: Mapped[AmbitoTransaccion] = mapped_column(
        Enum(AmbitoTransaccion, name='ambito_transaccion'),
        default=AmbitoTransaccion.TERRITORIAL,
        nullable=False,
    )

    funcionalidad: Mapped["Funcionalidad"] = relationship(
        back_populates="transacciones", lazy="selectin"
    )
    transaccion: Mapped["Transaccion"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<FuncionalidadTransaccion("
            f"funcionalidad_id='{self.funcionalidad_id}', "
            f"transaccion_id='{self.transaccion_id}', "
            f"ambito='{self.ambito}')>"
        )


class FlujoAprobacion(BaseModel):
    """Capa 3: cadena de aprobación entre roles.

    Ejemplo: el rol DISENADOR_CAMPANA ejecuta PROPONER_PRESUPUESTO_CAMPANA
    que queda en estado pendiente hasta que el rol JUNTA_DIRECTIVA ejecuta
    APROBAR_PRESUPUESTO_CAMPANA (o RECHAZAR_PRESUPUESTO_CAMPANA).

    El campo `entidad` identifica el aggregate raíz afectado por el flujo.
    """
    __tablename__ = 'flujos_aprobacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    transaccion_inicio_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('transacciones.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    transaccion_aprobacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('transacciones.id', ondelete='RESTRICT'),
        nullable=False,
    )
    transaccion_rechazo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('transacciones.id', ondelete='SET NULL'),
        nullable=True,
    )

    rol_aprobador_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('roles.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    entidad: Mapped[str] = mapped_column(String(100), nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    transaccion_inicio: Mapped["Transaccion"] = relationship(
        foreign_keys=[transaccion_inicio_id], lazy="selectin"
    )
    transaccion_aprobacion: Mapped["Transaccion"] = relationship(
        foreign_keys=[transaccion_aprobacion_id], lazy="selectin"
    )
    transaccion_rechazo: Mapped[Optional["Transaccion"]] = relationship(
        foreign_keys=[transaccion_rechazo_id], lazy="selectin"
    )
    rol_aprobador: Mapped["Rol"] = relationship(
        foreign_keys=[rol_aprobador_id], lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<FlujoAprobacion(codigo='{self.codigo}', entidad='{self.entidad}')>"
