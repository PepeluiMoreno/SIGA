"""Plan de cuentas contables (PCESFL 2013)."""

import uuid
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Text, Uuid, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoCuentaContable(PyEnum):
    """Tipos de cuentas contables según PCESFL 2013."""
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    GASTO = "GASTO"


class CuentaContable(BaseModel):
    """Plan de cuentas (PCESFL 2013)."""
    __tablename__ = "cuentas_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Código contable (ej: "57200001")
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Jerarquía del plan de cuentas
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=grupo, 2=subgrupo, 3=cuenta
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("cuentas_contables.id"), nullable=True, index=True)

    # Tipo de cuenta
    tipo: Mapped[str] = mapped_column(Enum(TipoCuentaContable), nullable=False, index=True)

    # Características
    permite_asiento: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    es_dotacion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    padre = relationship('CuentaContable', remote_side=[id], foreign_keys=[padre_id], lazy='selectin')
    hijas: Mapped[List["CuentaContable"]] = relationship(back_populates='padre', lazy='selectin')
    apuntes: Mapped[List["ApunteContable"]] = relationship(back_populates="cuenta", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo='{self.codigo}', nombre='{self.nombre}', tipo='{self.tipo}')>"

    @property
    def es_cuenta_hoja(self) -> bool:
        """Verifica si es una cuenta de último nivel (hoja)."""
        return self.nivel == 3 and self.permite_asiento
