"""Catálogo de tipos de unidades organizativas."""
import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Enum, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.base_model import BaseModel


class NaturalezaUnidad(PyEnum):
    TERRITORIAL    = "TERRITORIAL"
    FUNCIONAL      = "FUNCIONAL"
    PROGRAMATICA   = "PROGRAMATICA"
    ADMINISTRATIVA = "ADMINISTRATIVA"


class VinculoUnidad(PyEnum):
    INTERNA  = "INTERNA"
    FILIAL   = "FILIAL"
    FEDERADA = "FEDERADA"


class NivelOrganizativo(BaseModel):
    __tablename__ = "niveles_organizativos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    naturaleza: Mapped[NaturalezaUnidad] = mapped_column(
        Enum(NaturalezaUnidad, name='naturalezaunidad', create_type=False), nullable=False, index=True
    )
    vinculo: Mapped[VinculoUnidad] = mapped_column(
        Enum(VinculoUnidad, name='vinculounidad', create_type=False), nullable=False, index=True
    )
    # nivel derivado de la profundidad en el árbol (1=raíz, 2=hijo, …)
    nivel: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    padre_tipo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_organizativos.id', ondelete='SET NULL'),
        nullable=True, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
