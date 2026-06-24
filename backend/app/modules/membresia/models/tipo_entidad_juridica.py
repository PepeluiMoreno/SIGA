"""TipoEntidadJuridica: catálogo de formas jurídicas para contactos PJ.

Reaprovecha los antiguos `tipos_organizacion` (asociación, fundación, empresa,
administración pública, sindicato, partido…). Tipifica a los Contacto de tipo
PERSONA_JURIDICA: qué clase de entidad externa es.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.base_model import BaseModel


class TipoEntidadJuridica(BaseModel):
    """Forma jurídica de un contacto PJ (asociación, fundación, empresa, etc.).

    Attributes:
        nombre: denominación de la forma jurídica
        codigo: identificador estable (ASOCIACION, FUNDACION, EMPRESA, ADMIN_PUBLICA…)
        permite_convenios: si esta forma puede ser contraparte de convenios
        permite_jerarquia: si admite estructura padre/hijas (federaciones)
    """

    __tablename__ = "tipos_entidad_juridica"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    codigo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    permite_convenios: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    permite_jerarquia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<TipoEntidadJuridica('{self.nombre}')>"
