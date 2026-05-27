"""Catálogo de plataformas de videoreunión soportadas.

Cada plataforma declara qué campos necesita para conectar (URL, sala,
contraseña, código…) mediante `campos_esquema` (JSON). El frontend
renderiza el formulario dinámicamente a partir de ese esquema, así una
reunión telemática deja de ser un input de texto libre.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Text, Boolean, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel, InmutableMixin


class PlataformaTelematica(InmutableMixin, BaseModel):
    """Plataforma de videoreunión que puede usarse en reuniones telemáticas."""
    __tablename__ = 'sec_plataformas_telematicas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, index=True,
        comment='JITSI, ZOOM, MEET, TEAMS, INDICO, OTRA…'
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icono: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment='Emoji o nombre de icono (ej. 📹, jitsi.svg…)'
    )

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    url_base: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True,
        comment='URL base de la plataforma, p.ej. https://meet.jit.si/'
    )

    campos_esquema: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='JSON con la definición de campos requeridos. Cada item: '
                '{key, label, tipo (url|text|password|number), requerido, placeholder?}'
    )

    def __repr__(self) -> str:
        return f"<PlataformaTelematica(codigo='{self.codigo}', activa={self.activa})>"
