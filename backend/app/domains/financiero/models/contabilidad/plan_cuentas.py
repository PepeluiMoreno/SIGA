"""Plan de cuentas PGC adaptado. Importable/exportable en JSON."""

import uuid
from typing import Optional, List

from sqlalchemy import String, Boolean, Integer, ForeignKey, Uuid, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class CuentaContable(BaseModel):
    """Nodo del árbol del Plan General Contable.

    Estructura jerárquica: grupo (1 dígito) → subgrupo (2) → cuenta (3) → subcuenta (4+).
    Importable/exportable en JSON para configuración inicial.
    """
    __tablename__ = "cuentas_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=grupo, 2=subgrupo, 3=cuenta, 4=subcuenta
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    es_imputable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Solo subcuentas

    # Árbol jerárquico
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuentas_contables.id"), nullable=True, index=True
    )
    hijos: Mapped[List["CuentaContable"]] = relationship(
        back_populates='padre', lazy='selectin'
    )
    padre: Mapped[Optional["CuentaContable"]] = relationship(
        back_populates='hijos', remote_side='CuentaContable.id', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo='{self.codigo}', nombre='{self.nombre}')>"
