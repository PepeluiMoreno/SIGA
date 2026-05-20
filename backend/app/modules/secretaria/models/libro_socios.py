"""Snapshot del Libro de Socios.

La Ley Orgánica 1/2002 obliga a mantener un Libro de Socios actualizado.
En SIGA los datos vivos están en el módulo de membresía; este modelo
registra los cierres periódicos (fecha de corte + metadata) para
tener trazabilidad de la generación del libro oficial.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Boolean, Uuid, Date, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class LibroSociosSnapshot(BaseModel):
    """Registro de cada generación oficial del Libro de Socios.

    No duplica datos de miembros; guarda metadata del snapshot
    y la ruta al PDF generado para trazabilidad legal.
    """
    __tablename__ = 'sec_libro_socios_snapshots'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Fecha de corte del snapshot
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Estadísticas en el momento del corte
    total_socios_activos: Mapped[int] = mapped_column(Integer, nullable=False)
    total_socios_baja: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_socios_historico: Mapped[int] = mapped_column(Integer, nullable=False)

    # Motivo de la generación
    motivo: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True,
        comment="Ej: Asamblea anual, Inspección registral, Cierre de ejercicio"
    )

    # Documento
    ruta_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hash_pdf: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="SHA-256 del PDF para verificación de integridad"
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<LibroSociosSnapshot(fecha_corte='{self.fecha_corte}', socios={self.total_socios_activos})>"
