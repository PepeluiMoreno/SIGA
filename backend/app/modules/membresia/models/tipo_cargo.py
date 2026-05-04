"""Tipos de cargo en la junta directiva."""

import uuid
from typing import Optional, List

from sqlalchemy import String, Integer, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoCargo(BaseModel):
    """Tipos de cargo en la junta directiva.

    Cargos protegidos del sistema:
    - PRESIDENTE: Presidente de la organización
    - VICEPRESIDENTE: Vicepresidente
    - SECRETARIO: Secretario/a
    - TESORERO: Tesorero/a
    - VOCAL: Vocal de la junta (permite_multiples=True → varias posiciones)

    Los miembros con cargo_id asignado pertenecen a la junta directiva.
    """
    __tablename__ = 'tipos_cargo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Si True, la junta puede tener varias posiciones de este cargo (ej: VOCAL)
    permite_multiples: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    miembros = relationship('Miembro', back_populates='cargo', lazy='selectin')
    roles_automaticos: Mapped[List["TipoCargoRol"]] = relationship(
        back_populates="tipo_cargo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TipoCargo(codigo='{self.codigo}', nombre='{self.nombre}')>"
