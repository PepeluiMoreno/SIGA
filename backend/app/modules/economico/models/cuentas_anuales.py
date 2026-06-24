"""Modelo CuentasAnuales — Flujo 10.

Snapshot inmutable de las cuentas anuales depositadas (Balance PCESFL,
Cuenta de Resultados, Memoria) tras el cierre del ejercicio.

Workflow: BORRADOR → APROBADAS (por junta) → DEPOSITADAS (ante registro).
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class CuentasAnuales(BaseModel):
    """Cuentas Anuales depositadas (o en preparación) de un ejercicio."""
    __tablename__ = "cuentas_anuales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)

    # Estado: BORRADOR | APROBADAS | DEPOSITADAS
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="BORRADOR", index=True)

    # Snapshots (D10.1)
    balance_pcesfl: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    cuenta_resultados: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    memoria: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    excedente: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)

    # Aprobación por junta (D10.3)
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id"), nullable=True, index=True
    )
    acta_referencia: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Depósito ante registro (D10.3)
    fecha_deposito: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    archivo_acuse_recibo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    aprobador = relationship("Contacto", foreign_keys=[aprobado_por_id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<CuentasAnuales(ejercicio={self.ejercicio}, estado={self.estado})>"

    @property
    def es_borrador(self) -> bool:
        return self.estado == "BORRADOR"

    @property
    def es_aprobada(self) -> bool:
        return self.estado == "APROBADAS"

    @property
    def es_depositada(self) -> bool:
        return self.estado == "DEPOSITADAS"


# Estructura de Memoria con los 12 apartados PCESFL 2013 (RD 1491/2011)
APARTADOS_MEMORIA = [
    ("apartado_1",  "Actividad de la entidad"),
    ("apartado_2",  "Bases de presentación de las cuentas anuales"),
    ("apartado_3",  "Excedente del ejercicio"),
    ("apartado_4",  "Normas de registro y valoración"),
    ("apartado_5",  "Inmovilizado material, intangible e inversiones inmobiliarias"),
    ("apartado_6",  "Usuarios y otros deudores de la actividad propia"),
    ("apartado_7",  "Beneficiarios-acreedores"),
    ("apartado_8",  "Activos y pasivos financieros"),
    ("apartado_9",  "Fondos propios"),
    ("apartado_10", "Situación fiscal"),
    ("apartado_11", "Subvenciones, donaciones y legados"),
    ("apartado_12", "Aplicación de elementos patrimoniales a fines propios"),
]


def memoria_vacia() -> dict[str, str]:
    """Devuelve un dict con todos los apartados de Memoria con texto vacío."""
    return {clave: "" for clave, _ in APARTADOS_MEMORIA}
