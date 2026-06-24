"""Modelos de usuario y roles."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import String, Boolean, ForeignKey, DateTime, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin

if TYPE_CHECKING:
    from app.modules.membresia.models.contacto import Contacto


class TipoVinculacion(InmutableMixin, BaseModel):
    """Catálogo de tipos de vinculación de un usuario con la organización."""
    __tablename__ = "tipos_vinculacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    requiere_entidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    usuarios: Mapped[List["Usuario"]] = relationship(
        back_populates="tipo_vinculacion",
        foreign_keys="[Usuario.tipo_vinculacion_id]",
    )

    def __repr__(self) -> str:
        return f"<TipoVinculacion('{self.nombre}')>"


class Usuario(BaseModel):
    """Usuario del sistema con autenticación."""
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Contacto (persona) asociado (1:1, nullable: usuarios técnicos pueden no ser contactos)
    contacto_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id", ondelete="SET NULL"),
        nullable=True, unique=True, index=True,
    )

    # DEPRECADO: tipo_vinculacion ahora vive en Contacto.vinculaciones
    # Se mantienen por compatibilidad temporal; dejar vacíos en nuevas cuentas.
    tipo_vinculacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("tipos_vinculacion.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    entidad_vinculacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Campos adicionales de seguridad
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    intentos_login: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado_hasta: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Reset de contraseña (token de un solo uso, expira en 30 min)
    reset_token: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    reset_token_expira_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reset_token_solicitado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    roles: Mapped[List["UsuarioRol"]] = relationship(
        back_populates="usuario",
        foreign_keys="[UsuarioRol.usuario_id]",
        lazy="selectin"
    )
    contacto: Mapped[Optional["Contacto"]] = relationship(
        "Contacto", foreign_keys=[contacto_id], lazy="selectin"
    )
    tipo_vinculacion: Mapped[Optional["TipoVinculacion"]] = relationship(
        back_populates="usuarios",
        foreign_keys=[tipo_vinculacion_id],
        lazy="selectin",
    )
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

    # Ámbito del rol (NULL = global; si tiene valor, restringe al subárbol de esa unidad)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id"), nullable=True, index=True
    )

    # Nombramiento que originó esta asignación (NULL = asignación manual directa)
    nombramiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("historial_nombramientos.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    # Permite desactivar la asignación sin eliminarla (útil para suspensiones temporales)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

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
