"""Log de auditoría del sistema."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Uuid, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ....core.database import Base


class TipoAccion(str, enum.Enum):
    CREAR = "CREAR"
    EDITAR = "EDITAR"
    ELIMINAR = "ELIMINAR"
    VER = "VER"
    APROBAR = "APROBAR"
    RECHAZAR = "RECHAZAR"
    EXPORTAR = "EXPORTAR"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    OTRO = "OTRO"


class LogAuditoria(Base):
    """Registro inmutable de acciones realizadas en el sistema.

    Hereda de Base (no de BaseModel) porque el log de auditoría no debe
    tener soft-delete ni auditarse a sí mismo.
    """
    __tablename__ = 'logs_auditoria'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('usuarios.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    username_snapshot: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    transaccion_codigo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    accion: Mapped[TipoAccion] = mapped_column(
        Enum(TipoAccion, name='tipo_accion_auditoria'),
        nullable=False,
        index=True,
    )
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    entidad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    entidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)

    datos_anteriores: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    datos_nuevos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    exitoso: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    mensaje_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<LogAuditoria(accion='{self.accion}', usuario_id='{self.usuario_id}', fecha='{self.fecha_hora}')>"
