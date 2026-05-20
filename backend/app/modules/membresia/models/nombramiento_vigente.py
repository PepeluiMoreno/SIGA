"""Modelo de SOLO LECTURA sobre la vista `v_nombramientos_vigentes`.

La vista deriva de `historial_nombramientos` (estado ACTIVO, sin fecha de fin):
es la fuente única de verdad, siempre coherente, sin mantenimiento. Sirve para
detectar de forma directa el cargo vigente de cada agrupación (p. ej. el
tesorero regional al que enrutar las solicitudes de reducción de cuota).

NO insertar / actualizar / borrar a través de este modelo: PostgreSQL lo
rechazaría y, conceptualmente, los cambios van siempre a HistorialNombramiento.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Uuid, Date
from sqlalchemy.orm import Mapped, mapped_column

from ....core.database import Base


class NombramientoVigente(Base):
    """Fila de la vista `v_nombramientos_vigentes` (read-only)."""
    __tablename__ = "v_nombramientos_vigentes"

    # La vista no tiene PK formal; el ORM exige una. `id` (el del nombramiento
    # de origen) es único, así que sirve como clave primaria lógica.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    cargo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    fecha_inicio: Mapped[date] = mapped_column(Date)

    def __repr__(self) -> str:
        return f"<NombramientoVigente(miembro_id={self.miembro_id}, cargo_id={self.cargo_id})>"
