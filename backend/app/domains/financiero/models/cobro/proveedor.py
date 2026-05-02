"""Proveedores de pago (pasarelas externas)."""

import uuid
from typing import Optional

from sqlalchemy import String, Boolean, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .....infrastructure.base_model import BaseModel


class ProveedorPago(BaseModel):
    """Catálogo de pasarelas de pago disponibles (PayPal, Bizum, Stripe...)."""
    __tablename__ = "proveedores_pago"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<ProveedorPago(nombre='{self.nombre}')>"
