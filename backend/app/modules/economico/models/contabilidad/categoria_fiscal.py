"""Categorías fiscales: estructura de clasificación de la contabilidad simplificada.

Es a la contabilidad simplificada lo que el plan de cuentas PCESFL es a la
contabilidad compleja. Cuando org.contabilidad_compleja = false, cada ApunteCaja
se clasifica con una CategoriaFiscal en lugar de generar asiento de partida doble.

Las categorías mapean a las casillas de los modelos tributarios (130/131, 182, 347)
para que el libro de ingresos y gastos cuadre directamente con las obligaciones
fiscales de la asociación, sin necesidad de plan de cuentas.
"""
import uuid
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Boolean, Integer, Text, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .....infrastructure.base_model import BaseModel


class TipoCategoriaFiscal(PyEnum):
    """Naturaleza de la categoría: determina si suma como ingreso o gasto."""
    INGRESO = "INGRESO"
    GASTO = "GASTO"


class CategoriaFiscal(BaseModel):
    """Categoría de clasificación de ingresos y gastos para contabilidad simplificada.

    Un administrador las gestiona desde la misma pantalla que el plan de cuentas,
    pero solo son visibles/editables cuando la organización está en modo simplificado.
    """
    __tablename__ = "categorias_fiscales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True,
        comment="Código de máquina: ING_CUOTAS, GAS_PERSONAL, GAS_SUMINISTROS…"
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo: Mapped[TipoCategoriaFiscal] = mapped_column(
        Enum(TipoCategoriaFiscal), nullable=False, index=True
    )

    # ── Mapeo fiscal ──────────────────────────────────────────────────────────
    # Si la categoría computa para cada modelo tributario
    computa_modelo_182: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="Donativos deducibles — declaración informativa anual (modelo 182)"
    )
    computa_modelo_347: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="Operaciones con terceros > 3.005,06 € (modelo 347)"
    )
    # Casilla concreta del modelo cuando aplique (texto libre, ej. '130-01')
    casilla_modelo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Orden de presentación y estado
    orden: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<CategoriaFiscal(codigo='{self.codigo}', tipo={self.tipo}, nombre='{self.nombre}')>"
