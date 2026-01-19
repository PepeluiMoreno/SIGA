"""Modelos de presupuesto y planificación anual."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Date, Numeric, Boolean, Text, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .mixins import SoftDeleteMixin, AuditoriaMixin


class EstadoPlanificacion(Base):
    """Estados de planificación: BORRADOR, APROBADO, EN_EJECUCION, CERRADO."""
    __tablename__ = "estado_planificacion"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
   codigo: Mapped[str] = mapped_column(String(20), unique=True)
   nombre: Mapped[str] = mapped_column(String(100))
   orden: Mapped[int] = mapped_column(Integer, default=0)
   color: Mapped[str | None] = mapped_column(String(7))  # Hex color
   es_final: Mapped[bool] = mapped_column(Boolean, default=False)
   activo: Mapped[bool] = mapped_column(Boolean, default=True)


class CategoriaPartida(Base):
    """Categorías de partida presupuestaria: PERSONAL, INFRAESTRUCTURA, CAMPAÑAS, etc."""
    __tablename__ = "categoria_partida"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
   codigo: Mapped[str] = mapped_column(String(20), unique=True)
   nombre: Mapped[str] = mapped_column(String(100))
   descripcion: Mapped[str | None] = mapped_column(String(500))
   activo: Mapped[bool] = mapped_column(Boolean, default=True)


class PartidaPresupuestaria(Base, SoftDeleteMixin, AuditoriaMixin):
    """Partida presupuestaria para asignar dotación económica a actividades."""
    __tablename__ = "partida_presupuestaria"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)  # Ej: "2025-CAMP-001"
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Clasificación
    ejercicio: Mapped[int] = mapped_column(Integer)  # Año fiscal: 2025, 2026...
    tipo: Mapped[str] = mapped_column(String(10))  # INGRESO, GASTO
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categoria_partida.id"))

    # Importes
    importe_presupuestado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    importe_comprometido: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Asignado a propuestas
    importe_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Gastado real

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Vinculación a planificación
    planificacion_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("planificacion_anual.id"))

    # Relaciones
    categoria: Mapped["CategoriaPartida | None"] = relationship()
    planificacion: Mapped["PlanificacionAnual | None"] = relationship(back_populates="partidas")

    @property
    def importe_disponible(self) -> Decimal:
        """Calcula el importe disponible (presupuestado - comprometido)."""
        return self.importe_presupuestado - self.importe_comprometido


class PlanificacionAnual(Base, SoftDeleteMixin, AuditoriaMixin):
    """Planificación anual de actividades de la organización."""
    __tablename__ = "planificacion_anual"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, unique=True)  # Año: 2025
    nombre: Mapped[str] = mapped_column(String(200))  # "Plan Anual 2025"
    descripcion: Mapped[str | None] = mapped_column(Text)
    objetivos: Mapped[str | None] = mapped_column(Text)

    # Estado
    estado_id: Mapped[int] = mapped_column(ForeignKey("estado_planificacion.id"))
    fecha_aprobacion: Mapped[date | None] = mapped_column(Date)

    # Presupuesto global del ejercicio
    presupuesto_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    # Relaciones
    estado: Mapped["EstadoPlanificacion"] = relationship()
    partidas: Mapped[list["PartidaPresupuestaria"]] = relationship(back_populates="planificacion")
    propuestas: Mapped[list["PropuestaActividad"]] = relationship(back_populates="planificacion")


# Forward refs
from .actividad import PropuestaActividad  # noqa: E402,F401
