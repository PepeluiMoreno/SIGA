"""TipoVinculacion: catálogo de tipos de vínculo persona↔organización.

Define los tipos de vínculo (socio, voluntario, firmante…) y los metadatos que
gobiernan cómo se gestiona cada uno: ámbito (territorial/central), responsable, etc.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .vinculacion import Vinculacion


class TipoVinculacion(BaseModel):
    """Tipo de vínculo: firmante, socio, voluntario, donante, etc.
    
    Cada tipo declara:
    - codigo: identificador estable (SOCIO, VOLUNTARIO, etc.)
    - ambito: 'territorial' o 'central' (quién lo gestiona)
    - area_responsable: transacción RBAC que lo gobierna (ej. MEMBRESIA_SOCIO_GESTIONAR)
    - requiere_satelite: si este tipo necesita una tabla satélite con datos propios
    """

    __tablename__ = "tipos_vinculacion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    # Gobernanza
    ambito: Mapped[str] = mapped_column(
        String(20), default="central", nullable=False, index=True
    )  # 'territorial' o 'central'
    area_responsable: Mapped[str] = mapped_column(String(200), nullable=True)  # Ej. MEMBRESIA_SOCIO_GESTIONAR

    # Estructura
    requiere_satelite: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Si True, existe tabla satélite

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    vinculaciones: Mapped[list[Vinculacion]] = relationship(
        back_populates="tipo_vinculacion",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<TipoVinculacion('{self.nombre}', codigo='{self.codigo}')>"
