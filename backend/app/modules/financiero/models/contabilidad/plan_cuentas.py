"""Plan de cuentas PGC adaptado PCESFL 2013. Importable/exportable en JSON."""

import uuid
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, Boolean, Integer, ForeignKey, Uuid, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoCuentaContable(PyEnum):
    """Tipo de cuenta en el plan contable.

    Enum Python: la lógica de balance (activo vs pasivo, ingreso vs gasto)
    está hardcodeada en el código y no es parametrizable dinámicamente.
    """
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    GASTO = "GASTO"


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

    tipo: Mapped[TipoCuentaContable] = mapped_column(Enum(TipoCuentaContable), nullable=False, index=True)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Solo cuentas de nivel más profundo (subcuentas) admiten apuntes
    permite_asiento: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Identifica elementos de dotación fundacional (requisito AEF)
    es_dotacion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Árbol jerárquico
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuentas_contables.id"), nullable=True, index=True
    )
    hijos: Mapped[List["CuentaContable"]] = relationship(
        back_populates="padre",
        foreign_keys="CuentaContable.padre_id",
        lazy="selectin",
    )
    padre: Mapped[Optional["CuentaContable"]] = relationship(
        back_populates="hijos",
        foreign_keys="CuentaContable.padre_id",
        remote_side="CuentaContable.id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo='{self.codigo}', nombre='{self.nombre}', tipo={self.tipo})>"
