"""Reglas contables configurables: mapeo origen/tipo → cuentas PCESFL.

Sustituye el diccionario hardcodeado en registro_contable.py.
Un administrador puede gestionar estas reglas desde la UI sin modificar código.
"""
import uuid
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Boolean, Integer, Text, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .....infrastructure.base_model import BaseModel


class ReglaContable(BaseModel):
    """Regla de generación automática de asiento a partir de un ApunteCaja.

    Cuando se registra un apunte con (origen, tipo), el RegistroContable
    busca la primera regla activa que coincida y usa sus cuentas debe/haber.
    Si origen es NULL, actúa como comodín para cualquier origen.
    """
    __tablename__ = "reglas_contables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Criterios de activación — NULL en origen = comodín
    origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    tipo_apunte: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Cuentas contables (códigos del plan PCESFL)
    cuenta_debe_codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    cuenta_haber_codigo: Mapped[str] = mapped_column(String(20), nullable=False)

    # Metadatos
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<ReglaContable(origen={self.origen}, tipo={self.tipo_apunte}, "
            f"debe={self.cuenta_debe_codigo}, haber={self.cuenta_haber_codigo})>"
        )
