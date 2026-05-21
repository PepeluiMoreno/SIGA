"""Reglas de categorización automática de apuntes por concepto.

Permiten autoclasificar los apuntes de caja de origen manual: cuando el
concepto de un apunte coincide con el patrón de una regla, se le asigna
automáticamente la categoría fiscal correspondiente.

Es el equivalente a las "reglas de categorización" de las apps de
contabilidad: el administrador las define una vez ("si el concepto contiene
Endesa → Suministros") y los movimientos recurrentes se clasifican solos.

Orden de resolución de la categoría de un apunte (en CategorizacionService):
  1. Derivación por origen (CUOTA → Cuotas, DONACION → Donativos…)
  2. Primera ReglaCategorizacion activa que case con concepto + tipo
  3. Sin clasificar (pendiente de clasificación masiva o manual)
"""
import uuid
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Boolean, Integer, Text, Uuid, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .....infrastructure.base_model import BaseModel


class TipoCoincidencia(PyEnum):
    """Cómo se compara el patrón con el concepto del apunte."""
    CONTIENE = "CONTIENE"
    EMPIEZA_POR = "EMPIEZA_POR"
    EXACTO = "EXACTO"
    REGEX = "REGEX"


class ReglaCategorizacion(BaseModel):
    """Regla que asigna una categoría fiscal a un apunte según su concepto."""
    __tablename__ = "reglas_categorizacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Patrón de búsqueda en el concepto del apunte
    patron: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo_coincidencia: Mapped[TipoCoincidencia] = mapped_column(
        Enum(TipoCoincidencia), nullable=False, default=TipoCoincidencia.CONTIENE
    )

    # Restricción opcional por tipo de apunte (INGRESO/GASTO).
    # NULL = aplica a ambos. Evita que una regla de gasto clasifique un ingreso.
    tipo_apunte: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    # Categoría fiscal que se asigna cuando la regla coincide
    categoria_fiscal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("categorias_fiscales.id"), nullable=False, index=True
    )

    # Resolución de conflictos: menor orden gana
    orden: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    categoria_fiscal = relationship(
        'CategoriaFiscal', foreign_keys=[categoria_fiscal_id], lazy='selectin'
    )

    def __repr__(self) -> str:
        return (
            f"<ReglaCategorizacion(patron='{self.patron}', "
            f"tipo_coincidencia={self.tipo_coincidencia}, orden={self.orden})>"
        )

    def coincide(self, concepto: str, tipo_apunte: Optional[str] = None) -> bool:
        """Comprueba si esta regla casa con el concepto y tipo dados."""
        if not self.activa or not concepto:
            return False
        # Filtro por tipo de apunte si la regla lo restringe
        if self.tipo_apunte and tipo_apunte and self.tipo_apunte != tipo_apunte:
            return False

        texto = concepto.lower().strip()
        patron = self.patron.lower().strip()

        if self.tipo_coincidencia == TipoCoincidencia.CONTIENE:
            return patron in texto
        if self.tipo_coincidencia == TipoCoincidencia.EMPIEZA_POR:
            return texto.startswith(patron)
        if self.tipo_coincidencia == TipoCoincidencia.EXACTO:
            return texto == patron
        if self.tipo_coincidencia == TipoCoincidencia.REGEX:
            import re
            try:
                return re.search(self.patron, concepto, re.IGNORECASE) is not None
            except re.error:
                return False
        return False
