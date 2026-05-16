"""Modelo de plantillas de correo electrónico editables."""

import uuid
from typing import Optional

from sqlalchemy import String, Text, Boolean, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class PlantillaEmail(BaseModel):
    """Plantilla de correo electrónico editable por los coordinadores.

    El cuerpo_html puede contener variables con la sintaxis {{ variable }}.
    Las variables disponibles se documentan en variables_disponibles (JSON).
    """
    __tablename__ = 'plantillas_email'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # campanias, actividades, ...

    asunto: Mapped[str] = mapped_column(String(300), nullable=False)
    cuerpo_html: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadatos de variables disponibles, p.e.:
    # [{"clave": "nombre_miembro", "descripcion": "Nombre del destinatario"}]
    variables_disponibles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<PlantillaEmail(codigo='{self.codigo}', nombre='{self.nombre}')>"
