"""Motivos de baja de miembros."""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class MotivoBaja(BaseModel):
    """Motivos por los que un miembro puede causar baja.

    Códigos estándar:
    - VOLUNTARIA: El miembro solicita la baja
    - IMPAGO: Baja por cuotas impagadas (después de varios ejercicios)
    - FALLECIMIENTO: Baja por defunción
    - EXPULSION: Baja disciplinaria
    """
    __tablename__ = 'motivos_baja'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Características del motivo
    requiere_documentacion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    miembros = relationship('Miembro', back_populates='motivo_baja_rel', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MotivoBaja(codigo='{self.codigo}', nombre='{self.nombre}')>"
