"""Modelo de coordinaciones territoriales.

Vincula un miembro con las agrupaciones que coordina (relación 1:N).
Un coordinador puede gestionar múltiples agrupaciones (ej: Andalucía → 8 provincias).
"""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class CoordinacionTerritorial(BaseModel):
    """Asignación de un miembro como coordinador de una agrupación territorial."""
    __tablename__ = 'coordinaciones_territoriales'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('contactos.id', ondelete='RESTRICT'), nullable=False, index=True
    )
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('unidades_organizativas.id', ondelete='RESTRICT'), nullable=False, index=True
    )

    fecha_asignacion: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    miembro = relationship('Contacto', lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CoordinacionTerritorial(miembro_id={self.miembro_id}, agrupacion_id={self.agrupacion_id})>"
