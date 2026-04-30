"""Modelo de solicitudes de traslado territorial."""

import uuid
import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Uuid, ForeignKey, Date, DateTime, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class EstadoTraslado(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO_ORIGEN = "APROBADO_ORIGEN"
    APROBADO_DESTINO = "APROBADO_DESTINO"
    APROBADO = "APROBADO"
    RECHAZADO_ORIGEN = "RECHAZADO_ORIGEN"
    RECHAZADO_DESTINO = "RECHAZADO_DESTINO"
    EJECUTADO = "EJECUTADO"
    CANCELADO = "CANCELADO"


class SolicitudTraslado(BaseModel):
    """Solicitud de traslado de un miembro entre agrupaciones territoriales.

    Flujo: PENDIENTE → APROBADO_ORIGEN + APROBADO_DESTINO → APROBADO → EJECUTADO
           En cualquier punto → RECHAZADO_ORIGEN / RECHAZADO_DESTINO / CANCELADO
    """
    __tablename__ = 'solicitudes_traslado'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=False, index=True
    )
    agrupacion_origen_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=False
    )
    agrupacion_destino_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=False
    )

    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default=EstadoTraslado.PENDIENTE, nullable=False, index=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_efectiva_deseada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Aprobación coordinador de origen
    aprobado_origen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_aprobacion_origen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    coordinador_origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id'), nullable=True
    )
    observaciones_origen: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aprobación coordinador de destino
    aprobado_destino: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_aprobacion_destino: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    coordinador_destino_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id'), nullable=True
    )
    observaciones_destino: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Ejecución
    fecha_ejecucion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    usuario_ejecutor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id'), nullable=True
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship('Miembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<SolicitudTraslado(miembro={self.miembro_id}, estado='{self.estado}')>"
