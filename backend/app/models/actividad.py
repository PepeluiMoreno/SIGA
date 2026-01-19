"""Modelos de actividades, propuestas, recursos y KPIs."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Date, DateTime, Time, Numeric, Boolean, Text, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .mixins import SoftDeleteMixin, AuditoriaMixin


# =====================
# CATÁLOGOS
# =====================

class TipoActividad(Base):
    """Tipos de actividad: TAREA_CAMPANIA, ACTIVIDAD_ANUAL, REUNION, EVENTO, FORMACION."""
    __tablename__ = "tipo_actividad"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(Text)
    requiere_grupo: Mapped[bool] = mapped_column(Boolean, default=False)
    requiere_presupuesto: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class EstadoActividad(Base):
    """Estados de actividad: PLANIFICADA, EN_CURSO, COMPLETADA, CANCELADA, APLAZADA."""
    __tablename__ = "estado_actividad"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str | None] = mapped_column(String(7))  # Hex color para UI
    es_final: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class EstadoPropuesta(Base):
    """Estados de propuesta: BORRADOR, PENDIENTE, EN_REVISION, APROBADA, RECHAZADA."""
    __tablename__ = "estado_propuesta"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str | None] = mapped_column(String(7))
    es_final: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class TipoRecurso(Base):
    """Tipos de recurso: ECONOMICO, LOCAL, DESPLAZAMIENTO, MATERIAL, CATERING, etc."""
    __tablename__ = "tipo_recurso"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    requiere_importe: Mapped[bool] = mapped_column(Boolean, default=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class TipoKPI(Base):
    """Tipos de medición KPI: NUMERICO, PORCENTAJE, BOOLEANO, MONETARIO."""
    __tablename__ = "tipo_kpi"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    formato: Mapped[str | None] = mapped_column(String(50))  # "{value}%", "€{value}", etc.
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


# =====================
# PROPUESTAS DE ACTIVIDAD
# =====================

class PropuestaActividad(Base, SoftDeleteMixin, AuditoriaMixin):
    """Propuesta de actividad presentada por un miembro con rol de proponente."""
    __tablename__ = "propuesta_actividad"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)  # PRO-2025-001
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)
    justificacion: Mapped[str | None] = mapped_column(Text)  # Por qué se propone

    # Proponente (miembro con rol de presentar propuestas)
    proponente_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembro.id"))

    # Estado de la propuesta
    estado_id: Mapped[int] = mapped_column(ForeignKey("estado_propuesta.id"))
    fecha_presentacion: Mapped[date | None] = mapped_column(Date)
    fecha_resolucion: Mapped[date | None] = mapped_column(Date)
    motivo_resolucion: Mapped[str | None] = mapped_column(Text)  # Motivo aprobación/rechazo

    # Vinculación a planificación o campaña
    planificacion_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("planificacion_anual.id"))
    campania_id: Mapped[int | None] = mapped_column(ForeignKey("campania.id"))

    # Temporalidad propuesta
    fecha_inicio_propuesta: Mapped[date | None] = mapped_column(Date)
    fecha_fin_propuesta: Mapped[date | None] = mapped_column(Date)

    # Dotación económica total solicitada
    presupuesto_solicitado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    presupuesto_aprobado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Partida presupuestaria asignada
    partida_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("partida_presupuestaria.id"))

    # Observaciones
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    proponente: Mapped["Miembro"] = relationship(foreign_keys=[proponente_id])
    estado: Mapped["EstadoPropuesta"] = relationship()
    planificacion: Mapped["PlanificacionAnual | None"] = relationship(back_populates="propuestas")
    campania: Mapped["Campania | None"] = relationship()
    partida: Mapped["PartidaPresupuestaria | None"] = relationship()
    tareas: Mapped[list["TareaPropuesta"]] = relationship(back_populates="propuesta")
    recursos: Mapped[list["RecursoPropuesta"]] = relationship(back_populates="propuesta")
    grupos_asignados: Mapped[list["GrupoPropuesta"]] = relationship(back_populates="propuesta")
    actividad: Mapped["Actividad | None"] = relationship(back_populates="propuesta")


class TareaPropuesta(Base, SoftDeleteMixin):
    """Tareas incluidas en una propuesta de actividad."""
    __tablename__ = "tarea_propuesta"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("propuesta_actividad.id"))

    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    # Asignación de grupo de trabajo
    grupo_trabajo_id: Mapped[int | None] = mapped_column(ForeignKey("grupo_trabajo.id"))
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("miembro.id"))

    # Fechas estimadas
    fecha_inicio_estimada: Mapped[date | None] = mapped_column(Date)
    fecha_fin_estimada: Mapped[date | None] = mapped_column(Date)

    # Horas estimadas
    horas_estimadas: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Relaciones
    propuesta: Mapped["PropuestaActividad"] = relationship(back_populates="tareas")
    grupo_trabajo: Mapped["GrupoTrabajo | None"] = relationship()
    responsable: Mapped["Miembro | None"] = relationship()


class RecursoPropuesta(Base, SoftDeleteMixin):
    """Recursos solicitados en una propuesta (económicos, físicos, materiales)."""
    __tablename__ = "recurso_propuesta"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("propuesta_actividad.id"))

    tipo_recurso_id: Mapped[int] = mapped_column(ForeignKey("tipo_recurso.id"))
    descripcion: Mapped[str] = mapped_column(String(500))
    cantidad: Mapped[int] = mapped_column(Integer, default=1)

    # Importes
    importe_unitario_estimado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    importe_total_estimado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    importe_aprobado: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Proveedor
    proveedor: Mapped[str | None] = mapped_column(String(200))
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    propuesta: Mapped["PropuestaActividad"] = relationship(back_populates="recursos")
    tipo_recurso: Mapped["TipoRecurso"] = relationship()


class GrupoPropuesta(Base):
    """Grupos de trabajo asignados a una propuesta con sus responsabilidades."""
    __tablename__ = "grupo_propuesta"

    # Clave primaria compuesta
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("propuesta_actividad.id"), primary_key=True)
    grupo_trabajo_id: Mapped[int] = mapped_column(ForeignKey("grupo_trabajo.id"), primary_key=True)

    # Qué tareas realizará este grupo
    tareas_asignadas: Mapped[str | None] = mapped_column(Text)  # Descripción de responsabilidades
    horas_estimadas: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Relaciones
    propuesta: Mapped["PropuestaActividad"] = relationship(back_populates="grupos_asignados")
    grupo_trabajo: Mapped["GrupoTrabajo"] = relationship()


# =====================
# ACTIVIDADES (tras aprobación de propuesta)
# =====================

class Actividad(Base, SoftDeleteMixin, AuditoriaMixin):
    """Actividad aprobada, resultado de una propuesta."""
    __tablename__ = "actividad"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)  # ACT-2025-001
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Origen: propuesta aprobada
    propuesta_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("propuesta_actividad.id"))

    # Clasificación
    tipo_actividad_id: Mapped[int] = mapped_column(ForeignKey("tipo_actividad.id"))
    estado_id: Mapped[int] = mapped_column(ForeignKey("estado_actividad.id"))
    prioridad: Mapped[int] = mapped_column(Integer, default=2)  # 1=Alta, 2=Media, 3=Baja

    # Temporalidad
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[time | None] = mapped_column(Time)
    hora_fin: Mapped[time | None] = mapped_column(Time)
    es_todo_el_dia: Mapped[bool] = mapped_column(Boolean, default=True)

    # Ubicación
    lugar: Mapped[str | None] = mapped_column(String(200))
    direccion: Mapped[str | None] = mapped_column(String(300))
    es_online: Mapped[bool] = mapped_column(Boolean, default=False)
    url_online: Mapped[str | None] = mapped_column(String(500))

    # Origen (vinculación a campaña o planificación)
    campania_id: Mapped[int | None] = mapped_column(ForeignKey("campania.id"))
    planificacion_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("planificacion_anual.id"))

    # Responsabilidad
    coordinador_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembro.id"))
    es_colectiva: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dotación económica
    partida_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("partida_presupuestaria.id"))
    dotacion_economica: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    gasto_real: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Recursos humanos
    voluntarios_necesarios: Mapped[int] = mapped_column(Integer, default=0)
    voluntarios_confirmados: Mapped[int] = mapped_column(Integer, default=0)

    # Resultados
    completada: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_completada: Mapped[datetime | None] = mapped_column(DateTime)
    resultados: Mapped[str | None] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    propuesta: Mapped["PropuestaActividad | None"] = relationship(back_populates="actividad")
    tipo_actividad: Mapped["TipoActividad"] = relationship()
    estado: Mapped["EstadoActividad"] = relationship()
    campania: Mapped["Campania | None"] = relationship()
    planificacion: Mapped["PlanificacionAnual | None"] = relationship()
    coordinador: Mapped["Miembro"] = relationship(foreign_keys=[coordinador_id])
    partida: Mapped["PartidaPresupuestaria | None"] = relationship()
    tareas: Mapped[list["TareaActividad"]] = relationship(back_populates="actividad")
    recursos: Mapped[list["RecursoActividad"]] = relationship(back_populates="actividad")
    participantes: Mapped[list["ParticipanteActividad"]] = relationship(back_populates="actividad")
    grupos_trabajo: Mapped[list["GrupoActividad"]] = relationship(back_populates="actividad")
    kpis: Mapped[list["KPIActividad"]] = relationship(back_populates="actividad")


class TareaActividad(Base, SoftDeleteMixin, AuditoriaMixin):
    """Tarea específica dentro de una actividad."""
    __tablename__ = "tarea_actividad"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actividad.id"))

    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    # Asignación
    grupo_trabajo_id: Mapped[int | None] = mapped_column(ForeignKey("grupo_trabajo.id"))
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("miembro.id"))

    # Estado
    estado_id: Mapped[int] = mapped_column(ForeignKey("estado_tarea.id"))

    # Fechas
    fecha_limite: Mapped[date | None] = mapped_column(Date)
    fecha_completada: Mapped[datetime | None] = mapped_column(DateTime)

    # Horas
    horas_estimadas: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    horas_reales: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Relaciones
    actividad: Mapped["Actividad"] = relationship(back_populates="tareas")
    grupo_trabajo: Mapped["GrupoTrabajo | None"] = relationship()
    responsable: Mapped["Miembro | None"] = relationship()
    estado: Mapped["EstadoTarea"] = relationship()


class RecursoActividad(Base, SoftDeleteMixin, AuditoriaMixin):
    """Recurso asignado/utilizado en una actividad."""
    __tablename__ = "recurso_actividad"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actividad.id"))

    tipo_recurso_id: Mapped[int] = mapped_column(ForeignKey("tipo_recurso.id"))
    descripcion: Mapped[str] = mapped_column(String(500))
    cantidad: Mapped[int] = mapped_column(Integer, default=1)

    # Importes
    importe_presupuestado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    importe_real: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Proveedor
    proveedor: Mapped[str | None] = mapped_column(String(200))
    factura_referencia: Mapped[str | None] = mapped_column(String(100))
    fecha_factura: Mapped[date | None] = mapped_column(Date)

    # Estado
    pagado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_pago: Mapped[date | None] = mapped_column(Date)

    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    actividad: Mapped["Actividad"] = relationship(back_populates="recursos")
    tipo_recurso: Mapped["TipoRecurso"] = relationship()


class GrupoActividad(Base):
    """Grupos de trabajo asignados a una actividad."""
    __tablename__ = "grupo_actividad"

    # Clave primaria compuesta
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actividad.id"), primary_key=True)
    grupo_trabajo_id: Mapped[int] = mapped_column(ForeignKey("grupo_trabajo.id"), primary_key=True)

    tareas_asignadas: Mapped[str | None] = mapped_column(Text)
    horas_estimadas: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    horas_reales: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Relaciones
    actividad: Mapped["Actividad"] = relationship(back_populates="grupos_trabajo")
    grupo_trabajo: Mapped["GrupoTrabajo"] = relationship()


class ParticipanteActividad(Base):
    """Participantes (voluntarios) en una actividad."""
    __tablename__ = "participante_actividad"

    # Clave primaria compuesta
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actividad.id"), primary_key=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembro.id"), primary_key=True)

    rol: Mapped[str] = mapped_column(String(20), default="VOLUNTARIO")  # COORDINADOR, VOLUNTARIO, OBSERVADOR
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False)
    asistio: Mapped[bool | None] = mapped_column(Boolean)
    horas_aportadas: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    actividad: Mapped["Actividad"] = relationship(back_populates="participantes")
    miembro: Mapped["Miembro"] = relationship()


# =====================
# KPIs Y MEDICIONES
# =====================

class KPI(Base, SoftDeleteMixin):
    """Indicador clave de rendimiento para medir resultados."""
    __tablename__ = "kpi"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)  # KPI-PART-001
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Tipo de medición
    tipo_kpi_id: Mapped[int] = mapped_column(ForeignKey("tipo_kpi.id"))
    unidad: Mapped[str | None] = mapped_column(String(50))  # "personas", "euros", "%"

    # Valores objetivo (por defecto)
    valor_objetivo_defecto: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    valor_minimo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Umbral mínimo aceptable

    # Fórmula (si aplica)
    formula: Mapped[str | None] = mapped_column(String(500))  # Ej: "(participantes/objetivo)*100"

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    tipo_kpi: Mapped["TipoKPI"] = relationship()


class KPIActividad(Base, SoftDeleteMixin, AuditoriaMixin):
    """KPI asignado a una actividad específica con objetivo y mediciones."""
    __tablename__ = "kpi_actividad"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actividad.id"))
    kpi_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kpi.id"))

    # Objetivo específico para esta actividad
    valor_objetivo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    peso: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=1)  # Peso para cálculo de éxito global

    # Valor actual medido
    valor_actual: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    fecha_ultima_medicion: Mapped[datetime | None] = mapped_column(DateTime)

    # Resultado
    porcentaje_logro: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # (actual/objetivo)*100
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    actividad: Mapped["Actividad"] = relationship(back_populates="kpis")
    kpi: Mapped["KPI"] = relationship()
    mediciones: Mapped[list["MedicionKPI"]] = relationship(back_populates="kpi_actividad")


class MedicionKPI(Base, AuditoriaMixin):
    """Mediciones históricas de un KPI en una actividad."""
    __tablename__ = "medicion_kpi"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kpi_actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kpi_actividad.id"))

    valor_medido: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fecha_medicion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Responsable de la medición
    medido_por_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("miembro.id"))

    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    kpi_actividad: Mapped["KPIActividad"] = relationship(back_populates="mediciones")
    medido_por: Mapped["Miembro | None"] = relationship()


# Forward refs para evitar circular imports
from .miembro import Miembro  # noqa: E402,F401
from .campania import Campania  # noqa: E402,F401
from .grupo_trabajo import GrupoTrabajo, EstadoTarea  # noqa: E402,F401
from .presupuesto import PlanificacionAnual, PartidaPresupuestaria  # noqa: E402,F401
