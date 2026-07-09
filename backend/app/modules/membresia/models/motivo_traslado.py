"""Motivos de traslado de socios entre agrupaciones (catálogo editable)."""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel, InmutableMixin


class MotivoTraslado(InmutableMixin, BaseModel):
    """Motivos por los que se solicita el traslado de un socio de agrupación.

    Códigos estándar sembrados:
    - CAMBIO_DOMICILIO: El socio ha cambiado de domicilio/residencia
    - REORGANIZACION: Reorganización territorial de la asociación
    - PREFERENCIA: Preferencia personal del socio
    - OTRO: Otro motivo (se detalla en el texto libre de la solicitud)
    """
    __tablename__ = 'motivos_traslado'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MotivoTraslado(codigo='{self.codigo}', nombre='{self.nombre}')>"
