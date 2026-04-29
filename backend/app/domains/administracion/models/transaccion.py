"""Catálogo de transacciones (operaciones del sistema sujetas a permisos)."""

import uuid
from typing import List, Optional

from sqlalchemy import String, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Transaccion(BaseModel):
    """Operación del sistema que puede asignarse a un rol vía RBAC.

    El `codigo` es la clave natural usada por la capa de seguridad para
    referenciar la transacción en decoradores y middlewares.
    """
    __tablename__ = 'transacciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    modulo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    sistema: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    roles: Mapped[List["RolTransaccion"]] = relationship(
        back_populates="transaccion",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Transaccion(codigo='{self.codigo}', modulo='{self.modulo}')>"
