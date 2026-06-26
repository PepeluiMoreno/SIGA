"""Catálogo de tipos de unidades organizativas y ámbitos geográficos."""
import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Enum, Uuid, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class AmbitoGeografico(BaseModel):
    """
    Catálogo de ámbitos geográficos: Nacional, CCAA, Provincia, Comarca, Municipio…
    Extensible: añadir una fila en Parámetros Generales basta para introducir un
    nuevo nivel geográfico sin cambiar código.
    """
    __tablename__ = "ambitos_geograficos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # granularidad: 1 = más amplio (supranacional) … N = más fino (barrio)
    granularidad: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)

    niveles_organizativos: Mapped[list["NivelOrganizativo"]] = relationship(
        "NivelOrganizativo", back_populates="ambito_geografico", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<AmbitoGeografico(nombre='{self.nombre}', granularidad={self.granularidad})>"


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
    nivel: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    padre_tipo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_organizativos.id', ondelete='SET NULL'),
        nullable=True, index=True
    )
    ambito_geografico_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('ambitos_geograficos.id', ondelete='SET NULL'),
        nullable=True, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)

    # Denominación interna de la organización para una unidad de este nivel/ámbito
    # (p.ej. nivel "Provincia" → "Agrupación Provincial" / "Agrupaciones Provinciales").
    # Es la etiqueta que usa la UI para las unidades de este nivel (no hardcodear).
    denominacion_singular: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    denominacion_plural: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    ambito_geografico: Mapped[Optional[AmbitoGeografico]] = relationship(
        "AmbitoGeografico", back_populates="niveles_organizativos", lazy="selectin"
    )
