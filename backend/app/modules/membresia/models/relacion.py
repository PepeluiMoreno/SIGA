"""Relaciones entre contactos (modelo tipo CiviCRM `Relationship`).

Una `Relacion` es un vínculo dirigido **contacto ↔ contacto** (no con la
organización — eso es una `Vinculacion`). Ejemplos: "representante legal de",
"familiar de", "empleado de" (otra empresa), "miembro de la junta de".

El tipo es direccional: `nombre_directo` describe A→B ("Representante legal de")
y `nombre_inverso` describe B→A ("Representado por").
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .contacto import Contacto


class TipoRelacion(BaseModel):
    """Catálogo de tipos de relación entre contactos (direccional)."""

    __tablename__ = "tipos_relacion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    nombre_directo: Mapped[str] = mapped_column(String(100), nullable=False)  # A → B
    nombre_inverso: Mapped[str] = mapped_column(String(100), nullable=False)  # B → A
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    relaciones = relationship("Relacion", back_populates="tipo_relacion", lazy="selectin")

    def __repr__(self) -> str:
        return f"<TipoRelacion(codigo='{self.codigo}')>"


class Relacion(BaseModel):
    """Vínculo dirigido entre dos contactos: A es `tipo.nombre_directo` de B."""

    __tablename__ = "relaciones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    contacto_a_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contactos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contacto_b_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contactos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_relacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tipos_relacion.id"), nullable=False, index=True
    )

    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contacto_a = relationship("Contacto", foreign_keys=[contacto_a_id], lazy="selectin")
    contacto_b = relationship("Contacto", foreign_keys=[contacto_b_id], lazy="selectin")
    tipo_relacion = relationship("TipoRelacion", back_populates="relaciones", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Relacion(a={self.contacto_a_id}, tipo={self.tipo_relacion_id}, b={self.contacto_b_id})>"
