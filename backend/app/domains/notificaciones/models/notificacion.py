"""Modelos de notificaciones del sistema."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Text, DateTime, Uuid, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoNotificacion(BaseModel):
    """Tipos de notificaciones disponibles en el sistema."""
    __tablename__ = 'tipos_notificacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SISTEMA, FINANCIERO, CAMPANA, TAREA, etc.

    # Canales disponibles
    permite_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    permite_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    permite_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    permite_inapp: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Configuración
    prioridad: Mapped[str] = mapped_column(String(20), default='NORMAL', nullable=False)  # BAJA, NORMAL, ALTA, URGENTE
    requiere_accion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Template
    template_asunto: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Para email
    template_cuerpo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_sms: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Icono y color para UI
    icono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relaciones
    notificaciones = relationship('Notificacion', back_populates='tipo', lazy='selectin')
    preferencias = relationship('PreferenciaNotificacion', back_populates='tipo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoNotificacion(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Notificacion(BaseModel):
    """Notificaciones enviadas a usuarios."""
    __tablename__ = 'notificaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tipo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_notificacion.id'), nullable=False, index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=False, index=True)

    # Contenido
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    datos_adicionales: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Datos extra en JSON

    # Canal y estado
    canal: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # EMAIL, SMS, PUSH, INAPP
    estado: Mapped[str] = mapped_column(String(20), default='PENDIENTE', nullable=False, index=True)  # PENDIENTE, ENVIADA, LEIDA, ERROR

    # Timestamps
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    fecha_envio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_lectura: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_expiracion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Control
    leida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    archivada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Para acciones
    requiere_accion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accion_completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    url_accion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata de envío
    intentos_envio: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ultimo_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones a entidades relacionadas (genérico)
    entidad_tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # Tipo de entidad relacionada
    entidad_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # ID de entidad relacionada

    # Relaciones
    tipo = relationship('TipoNotificacion', back_populates='notificaciones', lazy='selectin')
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Notificacion(titulo='{self.titulo}', usuario_id='{self.usuario_id}', estado='{self.estado}')>"

    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.utcnow()

    def archivar(self) -> None:
        """Archiva la notificación."""
        self.archivada = True

    def esta_expirada(self) -> bool:
        """Verifica si la notificación ha expirado."""
        if self.fecha_expiracion:
            return datetime.utcnow() > self.fecha_expiracion
        return False


class PreferenciaNotificacion(BaseModel):
    """Preferencias de notificación de usuarios."""
    __tablename__ = 'preferencias_notificacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=False, index=True)
    tipo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_notificacion.id'), nullable=False, index=True)

    # Canales habilitados
    email_habilitado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_habilitado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    push_habilitado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inapp_habilitado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Frecuencia
    frecuencia: Mapped[str] = mapped_column(String(20), default='INMEDIATO', nullable=False)  # INMEDIATO, DIARIO, SEMANAL, NUNCA

    # Horario preferido (para resúmenes)
    hora_preferida: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-23

    # Relaciones
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')
    tipo = relationship('TipoNotificacion', back_populates='preferencias', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PreferenciaNotificacion(usuario_id='{self.usuario_id}', tipo_id='{self.tipo_id}')>"
