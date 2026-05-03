"""Roles del sistema (RBAC)."""

import enum
import uuid
from typing import List, Optional

from sqlalchemy import String, Integer, Boolean, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoRol(str, enum.Enum):
    SISTEMA = "SISTEMA"
    ORGANIZACION = "ORGANIZACION"
    TERRITORIAL = "TERRITORIAL"
    FUNCIONAL = "FUNCIONAL"
    PERSONALIZADO = "PERSONALIZADO"


class Rol(BaseModel):
    """Rol asignable a usuarios. Agrupa transacciones permitidas."""
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    tipo: Mapped[TipoRol] = mapped_column(
        Enum(TipoRol, name='tipo_rol'),
        default=TipoRol.PERSONALIZADO,
        nullable=False,
    )
    nivel: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    es_territorial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nivel_territorial: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    transacciones: Mapped[List["RolTransaccion"]] = relationship(
        back_populates="rol",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    funcionalidades: Mapped[List["RolFuncionalidad"]] = relationship(
        back_populates="rol",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Rol(codigo='{self.codigo}', nivel={self.nivel})>"
