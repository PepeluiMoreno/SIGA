"""Modelos relacionados con seguridad del sistema."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Text, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Sesion(BaseModel):
    """Modelo para gestión de sesiones de usuario."""
    __tablename__ = 'sesiones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(500), unique=True, nullable=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ultima_actividad: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    dispositivo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Tipo de dispositivo (mobile, desktop, tablet)
    navegador: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sistema_operativo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ubicacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Ciudad/País aproximado

    # Relaciones
    usuario = relationship('Usuario', foreign_keys=[usuario_id], back_populates='sesiones', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Sesion(usuario_id='{self.usuario_id}', ip='{self.ip_address}', activa={self.activa})>"

    def es_valida(self) -> bool:
        """Verifica si la sesión es válida."""
        return self.activa and datetime.utcnow() < self.fecha_expiracion

    def cerrar(self) -> None:
        """Cierra la sesión."""
        self.activa = False


class HistorialSeguridad(BaseModel):
    """Registro de eventos de seguridad del sistema."""
    __tablename__ = 'historial_seguridad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # LOGIN, LOGOUT, LOGIN_FALLIDO, BLOQUEO, etc.
    severidad: Mapped[str] = mapped_column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    datos_adicionales: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON con datos extra
    fecha_evento: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    exitoso: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    codigo_error: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relaciones
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')

    def __repr__(self) -> str:
        return (f"<HistorialSeguridad(tipo='{self.evento_tipo}', "
                f"severidad='{self.severidad}', exitoso={self.exitoso})>")


class IPBloqueada(BaseModel):
    """Registro de IPs bloqueadas temporalmente."""
    __tablename__ = 'ips_bloqueadas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ip_address: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    motivo: Mapped[str] = mapped_column(String(200), nullable=False)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fecha_bloqueo: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_desbloqueo: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    bloqueado_permanente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bloqueado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True)

    # Relaciones
    bloqueado_por = relationship('Usuario', foreign_keys=[bloqueado_por_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<IPBloqueada(ip='{self.ip_address}', permanente={self.bloqueado_permanente})>"

    def esta_bloqueada(self) -> bool:
        """Verifica si la IP está actualmente bloqueada."""
        if self.bloqueado_permanente:
            return True
        if self.fecha_desbloqueo:
            return datetime.utcnow() < self.fecha_desbloqueo
        return False

    def desbloquear(self, usuario_id: Optional[uuid.UUID] = None) -> None:
        """Desbloquea la IP."""
        self.fecha_desbloqueo = datetime.utcnow()
        self.bloqueado_permanente = False
        if usuario_id:
            self.modificado_por_id = usuario_id


class IntentoAcceso(BaseModel):
    """Registro de intentos de acceso al sistema (exitosos y fallidos)."""
    __tablename__ = 'intentos_acceso'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    identificador: Mapped[str] = mapped_column(String(200), nullable=False, index=True)  # email, username, etc.
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_intento: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    exitoso: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    motivo_fallo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # USUARIO_NO_EXISTE, PASSWORD_INCORRECTO, etc.
    bloqueado_tras_intento: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')

    def __repr__(self) -> str:
        return (f"<IntentoAcceso(identificador='{self.identificador}', "
                f"ip='{self.ip_address}', exitoso={self.exitoso})>")
