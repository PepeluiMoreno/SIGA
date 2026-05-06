"""Junta directiva por agrupación territorial.

JuntaDirectiva representa el mandato/legislatura de una agrupación territorial.
Los cargos se gestionan vía UsuarioRol (roles de tipo ORGANIZACION) y
HistorialNombramiento (trazabilidad).
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Boolean, Uuid, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class JuntaDirectiva(BaseModel):
    """Mandato/legislatura de una agrupación territorial.

    Puede haber varias juntas en el tiempo (renovaciones),
    pero solo una activa simultáneamente por agrupación.

    La composición actual se consulta vía UsuarioRol + Rol tipo ORGANIZACION.
    El histórico se consulta vía HistorialNombramiento.
    """
    __tablename__ = 'juntas_directivas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    agrupacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('agrupaciones_territoriales.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_constitucion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_disolucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')

    def __repr__(self) -> str:
        return f"<JuntaDirectiva(agrupacion_id='{self.agrupacion_id}', activa={self.activa})>"
