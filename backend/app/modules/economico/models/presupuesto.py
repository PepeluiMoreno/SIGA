"""Modelos de presupuesto y planificación anual."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Boolean, Text, Integer, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class EstadoPlanificacion(BaseModel):
    """Estados de planificación presupuestaria."""
    __tablename__ = "estados_planificacion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color
    es_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    planificaciones = relationship('PlanificacionAnual', back_populates='estado', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EstadoPlanificacion(codigo='{self.codigo}', nombre='{self.nombre}')>"


class CategoriaPartida(BaseModel):
    """Categorías de partida presupuestaria."""
    __tablename__ = "categorias_partida"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    partidas = relationship('PartidaPresupuestaria', back_populates='categoria', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CategoriaPartida(codigo='{self.codigo}', nombre='{self.nombre}')>"


class PartidaPresupuestaria(BaseModel):
    """Partida presupuestaria para asignar dotación económica a actividades."""
    __tablename__ = "partidas_presupuestarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # Ej: "2025-CAMP-001"
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Clasificación
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # Año fiscal: 2025, 2026...
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # INGRESO, GASTO
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("categorias_partida.id"), nullable=True, index=True)

    # Importes
    # importe_inicial: lo aprobado, congelado al aprobar el presupuesto (Fase 2).
    # importe_presupuestado: el VIGENTE = inicial + modificaciones presupuestarias.
    importe_inicial: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    importe_presupuestado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    importe_comprometido: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)  # Asignado a propuestas
    importe_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)  # Gastado real

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Vinculación a planificación
    planificacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("planificaciones_anuales.id"), nullable=True, index=True)

    # Vinculación a la taxonomía de actividad (presupuesto por programas).
    # Opcional: una partida puede ser genérica (sin actividad ni campaña) o estar
    # afecta a una actividad o campaña concreta para seguimiento por proyecto.
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("actividades.id"), nullable=True, index=True
    )
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("campanias.id"), nullable=True, index=True
    )

    # Relaciones
    categoria: Mapped[Optional["CategoriaPartida"]] = relationship(back_populates='partidas', lazy='selectin')
    planificacion: Mapped[Optional["PlanificacionAnual"]] = relationship(back_populates='partidas', lazy='selectin')
    actividad = relationship('Actividad', foreign_keys=[actividad_id], lazy='selectin')
    campania = relationship('Campania', foreign_keys=[campania_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<PartidaPresupuestaria(codigo='{self.codigo}', tipo='{self.tipo}', importe={self.importe_presupuestado})>"

    @property
    def importe_disponible(self) -> Decimal:
        """Calcula el importe disponible (presupuestado - comprometido)."""
        return self.importe_presupuestado - self.importe_comprometido

    @property
    def porcentaje_comprometido(self) -> float:
        """Calcula el porcentaje comprometido sobre el presupuestado."""
        if self.importe_presupuestado == 0:
            return 0.0
        return float((self.importe_comprometido / self.importe_presupuestado) * 100)

    @property
    def porcentaje_ejecutado(self) -> float:
        """Calcula el porcentaje ejecutado sobre el presupuestado."""
        if self.importe_presupuestado == 0:
            return 0.0
        return float((self.importe_ejecutado / self.importe_presupuestado) * 100)

    @property
    def saldo_disponible_ejecucion(self) -> Decimal:
        """Disponible real de ejecución: vigente - ejecutado (Fase 2)."""
        return self.importe_presupuestado - self.importe_ejecutado

    @property
    def esta_sobreejecutada(self) -> bool:
        """True si lo ejecutado supera el presupuesto vigente."""
        return self.importe_ejecutado > self.importe_presupuestado

    @property
    def esta_agotada(self) -> bool:
        """True si no queda disponible de ejecución (vigente totalmente consumido)."""
        return self.importe_presupuestado > 0 and self.saldo_disponible_ejecucion <= 0

    @property
    def importe_modificaciones(self) -> Decimal:
        """Diferencia entre el vigente y el inicial (efecto neto de las modificaciones)."""
        return self.importe_presupuestado - self.importe_inicial

    def comprometer_importe(self, importe: Decimal) -> bool:
        """
        Compromete un importe de la partida.

        Returns:
            True si hay fondos suficientes, False si no.
        """
        if self.importe_disponible >= importe:
            self.importe_comprometido += importe
            return True
        return False

    def liberar_importe(self, importe: Decimal) -> None:
        """Libera un importe previamente comprometido."""
        self.importe_comprometido -= importe
        if self.importe_comprometido < 0:
            self.importe_comprometido = Decimal('0.00')

    def ejecutar_gasto(self, importe: Decimal) -> None:
        """Registra un gasto ejecutado."""
        self.importe_ejecutado += importe


class CompromisoPresupuestario(BaseModel):
    """Compromiso de una partida presupuestaria para una campaña o actividad concreta.

    Se crea en fase de Preparación. Incrementa PartidaPresupuestaria.importe_comprometido.
    """
    __tablename__ = "compromisos_presupuestarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    partida_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("partidas_presupuestarias.id"), nullable=False, index=True
    )

    # Exactamente uno de los dos debe estar presente:
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    importe_comprometido: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    concepto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fecha_compromiso: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='activo')
    # 'activo' → comprometido; 'liberado' → devuelto a disponible; 'ejecutado' → gasto real registrado

    partida: Mapped["PartidaPresupuestaria"] = relationship(lazy='selectin')

    def __repr__(self) -> str:
        return f"<CompromisoPresupuestario(partida_id='{self.partida_id}', importe={self.importe_comprometido})>"


class PlanificacionAnual(BaseModel):
    """Planificación anual de actividades de la organización."""
    __tablename__ = "planificaciones_anuales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)  # Año: 2025
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)  # "Plan Anual 2025"
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objetivos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Estado
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_planificacion.id"), nullable=False, index=True)
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Presupuesto global del ejercicio
    presupuesto_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal('0.00'), nullable=False)

    # Control de disponibilidad (Fase 2): si está activo, imputar un gasto que supere
    # el disponible de la partida se bloquea; si está inactivo, solo se avisa.
    control_disponibilidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    estado: Mapped["EstadoPlanificacion"] = relationship(back_populates='planificaciones', lazy='selectin')
    partidas: Mapped[List["PartidaPresupuestaria"]] = relationship(back_populates='planificacion', lazy='selectin')
    # propuestas: Mapped[List["PropuestaActividad"]] = relationship(back_populates='planificacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PlanificacionAnual(ejercicio={self.ejercicio}, estado_id='{self.estado_id}')>"

    @property
    def presupuesto_ingresos(self) -> Decimal:
        """Calcula el total de ingresos presupuestados."""
        return sum(
            p.importe_presupuestado
            for p in self.partidas
            if p.tipo == 'INGRESO' and not p.eliminado
        )

    @property
    def presupuesto_gastos(self) -> Decimal:
        """Calcula el total de gastos presupuestados."""
        return sum(
            p.importe_presupuestado
            for p in self.partidas
            if p.tipo == 'GASTO' and not p.eliminado
        )

    @property
    def saldo_presupuestado(self) -> Decimal:
        """Calcula el saldo presupuestado (ingresos - gastos)."""
        return self.presupuesto_ingresos - self.presupuesto_gastos

    @property
    def gastos_ejecutados(self) -> Decimal:
        """Calcula el total de gastos ejecutados."""
        return sum(
            p.importe_ejecutado
            for p in self.partidas
            if p.tipo == 'GASTO' and not p.eliminado
        )

    @property
    def porcentaje_ejecucion(self) -> float:
        """Calcula el porcentaje de ejecución del presupuesto."""
        if self.presupuesto_gastos == 0:
            return 0.0
        return float((self.gastos_ejecutados / self.presupuesto_gastos) * 100)

    def aprobar(self, estado_aprobado_id: uuid.UUID, fecha_aprobacion: Optional[date] = None) -> None:
        """Marca la planificación como aprobada. El estado lo resuelve el servicio."""
        self.estado_id = estado_aprobado_id
        self.fecha_aprobacion = fecha_aprobacion or date.today()

    def iniciar_ejecucion(self, estado_ejecucion_id: uuid.UUID) -> None:
        """Pone la planificación en ejecución."""
        self.estado_id = estado_ejecucion_id

    def cerrar(self, estado_cerrado_id: uuid.UUID) -> None:
        """Cierra la planificación."""
        self.estado_id = estado_cerrado_id


class TipoModificacionPresupuestaria(str, PyEnum):
    """Tipos de modificación presupuestaria."""
    TRANSFERENCIA = "TRANSFERENCIA"  # mueve importe de una partida a otra (suma cero)
    AMPLIACION = "AMPLIACION"        # aumenta una partida (más ingreso del previsto lo habilita)
    SUPLEMENTO = "SUPLEMENTO"        # aumenta una partida con cargo a remanente/reservas


class ModificacionPresupuestaria(BaseModel):
    """Modificación formal de un presupuesto aprobado (Fase 2).

    El presupuesto aprobado no se edita a mano: los cambios se registran como
    modificaciones tipificadas y trazables que ajustan el importe vigente
    (PartidaPresupuestaria.importe_presupuestado) sin alterar el inicial.
    """
    __tablename__ = "modificaciones_presupuestarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    planificacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("planificaciones_anuales.id"), nullable=False, index=True
    )
    tipo: Mapped[TipoModificacionPresupuestaria] = mapped_column(
        Enum(TipoModificacionPresupuestaria), nullable=False
    )

    # Partida destino (siempre). Partida origen solo en TRANSFERENCIA.
    partida_destino_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("partidas_presupuestarias.id"), nullable=False, index=True
    )
    partida_origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("partidas_presupuestarias.id"), nullable=True, index=True
    )

    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)

    # Quién la registró (auditoría ligera; el aprobado formal es acto de gobierno)
    registrada_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id"), nullable=True
    )

    planificacion = relationship('PlanificacionAnual', lazy='selectin')
    partida_destino = relationship(
        'PartidaPresupuestaria', foreign_keys=[partida_destino_id], lazy='selectin'
    )
    partida_origen = relationship(
        'PartidaPresupuestaria', foreign_keys=[partida_origen_id], lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<ModificacionPresupuestaria(tipo={self.tipo}, importe={self.importe})>"
