"""Modelo de miembros (miembros) de la organización."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .nivel_estudios import NivelEstudios

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Boolean, Text, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from ....infrastructure.base_model import BaseModel, InmutableMixin


# Constantes para segmentación
EDAD_JOVEN_LIMITE = 30  # Menores de 30 años se consideran jóvenes


class TipoMiembro(InmutableMixin, BaseModel):
    """Tipos de miembro (miembro, simpatizante, colaborador, etc.)."""
    __tablename__ = 'tipos_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Características del tipo
    requiere_cuota: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    puede_votar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Flujo 1 D1.2: motivo de reducción aplicado por defecto al generar CuotaAnual
    motivo_reduccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('motivos_reduccion_cuota.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Relaciones
    motivo_reduccion = relationship(
        'MotivoReduccionCuota', foreign_keys=[motivo_reduccion_id], lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<TipoMiembro(nombre='{self.nombre}')>"


