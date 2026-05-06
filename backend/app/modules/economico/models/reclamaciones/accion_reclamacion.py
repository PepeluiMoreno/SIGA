"""Acciones ejecutadas dentro de un proceso de reclamación."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Uuid, Text, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class TipoAccionReclamacion(BaseModel):
    """Catálogo de tipos de acción en reclamaciones (NOTIFICACION, LLAMADA, CARTA, GESTORIA...)."""
    __tablename__ = "tipos_accion_reclamacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<TipoAccionReclamacion(codigo='{self.codigo}')>"


class AccionReclamacion(BaseModel):
    """Acción ejecutada en un proceso de reclamación.

    Ejemplos: notificación automática, llamada telefónica, carta certificada, cesión a gestoría.
    """
    __tablename__ = "acciones_reclamacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    reclamacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reclamaciones.id"), nullable=False, index=True
    )
    tipo_accion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tipos_accion_reclamacion.id"), nullable=False, index=True
    )

    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    resultado: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ejecutado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True, index=True
    )

    reclamacion = relationship('Reclamacion', back_populates='acciones', lazy='selectin')
    tipo_accion = relationship('TipoAccionReclamacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<AccionReclamacion(reclamacion_id='{self.reclamacion_id}')>"
