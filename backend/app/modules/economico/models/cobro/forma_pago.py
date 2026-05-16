"""Catálogo de formas de pago preferidas de miembros."""

import uuid
from typing import Optional

from sqlalchemy import String, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .....infrastructure.base_model import BaseModel, InmutableMixin


class FormaPago(InmutableMixin, BaseModel):
    """Catálogo de formas de pago (transferencia, tarjeta, efectivo, domiciliación...)."""
    __tablename__ = "formas_pago"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # TRANSFERENCIA, TARJETA, EFECTIVO, DOMICILIACION, OTRO
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<FormaPago(codigo='{self.codigo}', nombre='{self.nombre}')>"
