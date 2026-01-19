"""Estados de miembros."""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class EstadoMiembro(BaseModel):
    """Estados posibles de un miembro en el sistema.

    Estados del ciclo de vida de un miembro:
    - PENDIENTE_APROBACION: Alta solicitada, pendiente de revisión
    - ACTIVO: Miembro activo en la organización
    - SUSPENDIDO: Miembro temporalmente suspendido
    - BAJA: Miembro dado de baja definitiva
    """
    __tablename__ = 'estados_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default='#6C757D')  # Color hex para UI
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<EstadoMiembro(codigo='{self.codigo}', nombre='{self.nombre}')>"
