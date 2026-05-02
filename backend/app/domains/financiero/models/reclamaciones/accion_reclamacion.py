"""Acciones ejecutadas dentro de un proceso de reclamación."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Uuid, Text, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class AccionReclamacion(BaseModel):
    """Acción ejecutada en un proceso de reclamación.

    Ejemplos: notificación automática, llamada telefónica, carta certificada, cesión a gestoría.
    """
    __tablename__ = "acciones_reclamacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    reclamacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reclamaciones.id"), nullable=False, index=True
    )

    # tipo_accion: FK a tipos_accion_reclamacion (catálogo: NOTIFICACION, LLAMADA, CARTA, GESTORIA)
    tipo_accion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tipos_accion_reclamacion.id"), nullable=False, index=True
    )

    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    resultado: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # usuario que ejecutó la acción (null si fue automática)
    ejecutado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True, index=True
    )

    reclamacion = relationship('Reclamacion', back_populates='acciones', lazy='selectin')
    tipo_accion = relationship('TipoAccionReclamacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<AccionReclamacion(reclamacion_id='{self.reclamacion_id}')>"
