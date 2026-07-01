"""Etiquetas libres de contactos (tipo CiviCRM `Tag`).

Clasificación libre y transversal de contactos: "simpatizante", "prensa",
"patrocinador", "ponente", etc. A diferencia de una `Vinculacion` (afiliación)
o un `GrupoTrabajo`, una etiqueta es solo una marca para segmentar.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class Etiqueta(BaseModel):
    """Etiqueta libre para segmentar contactos."""

    __tablename__ = "etiquetas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Etiqueta(nombre='{self.nombre}')>"


class ContactoEtiqueta(BaseModel):
    """Asignación de una etiqueta a un contacto (N:M)."""

    __tablename__ = "contactos_etiquetas"
    __table_args__ = (
        UniqueConstraint("contacto_id", "etiqueta_id", name="uq_contacto_etiqueta"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contacto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contactos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    etiqueta_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("etiquetas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    etiqueta = relationship("Etiqueta", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ContactoEtiqueta(contacto={self.contacto_id}, etiqueta={self.etiqueta_id})>"
