"""Modelos de usuario y roles."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, ForeignKey, DateTime, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Usuario(BaseModel):
    """Usuario del sistema con autenticación."""
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Campos adicionales de seguridad
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    intentos_login: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado_hasta: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    roles: Mapped[List["UsuarioRol"]] = relationship(
        back_populates="usuario",
        foreign_keys="[UsuarioRol.usuario_id]",
        lazy="selectin"
    )
    # miembro: Mapped[Optional["Miembro"]] = relationship(back_populates="usuario", lazy="selectin")
    sesiones: Mapped[List["Sesion"]] = relationship(
        back_populates="usuario",
        foreign_keys="[Sesion.usuario_id]",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Usuario(email='{self.email}', activo={self.activo})>"


class UsuarioRol(BaseModel):
    """Un usuario puede tener múltiples roles, opcionalmente con ámbito territorial."""
    __tablename__ = "usuarios_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=False, index=True
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("roles.id"), nullable=False, index=True
    )

    # Ámbito del rol (ej: coordinador de agrupación X)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("agrupaciones_territoriales.id"), nullable=True, index=True
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="roles",
        foreign_keys=[usuario_id],
        lazy="selectin"
    )
    rol: Mapped["Rol"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<UsuarioRol(usuario_id='{self.usuario_id}', rol_id='{self.rol_id}')>"


# Forward refs para type hints
from .rol import Rol  # noqa: E402,F401
from .seguridad import Sesion  # noqa: E402,F401
