"""Modelos de actividades, propuestas, tareas, recursos y KPIs."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


# === PROPUESTAS ===

class PropuestaActividad(BaseModel):
    """Propuesta de actividad."""
    __tablename__ = 'propuestas_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    justificacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Proponente y estado
    proponente_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_propuesta.id'), nullable=False, index=True)

    # Fechas
    fecha_presentacion: Mapped[Optional[date]] = mapped_column(Date, server_default=func.now(), nullable=True)
    fecha_resolucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_resolucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Campania
    fecha_inicio_propuesta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_propuesta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Presupuesto
    # VALIDACIÓN: El servicio debe verificar que PartidaPresupuestaria.ejercicio == fecha_inicio_propuesta.year
    presupuesto_solicitado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    presupuesto_aprobado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    partida_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a PartidaPresupuestaria

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    estado = relationship('EstadoPropuesta', back_populates='propuestas', lazy='selectin')
    tareas = relationship('TareaPropuesta', back_populates='propuesta', lazy='selectin')
    recursos = relationship('RecursoPropuesta', back_populates='propuesta', lazy='selectin')
    grupos_asignados = relationship('GrupoPropuesta', back_populates='propuesta', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PropuestaActividad(codigo='{self.codigo}', titulo='{self.titulo}')>"


class TareaPropuesta(BaseModel):
    """Tarea asociada a una propuesta de actividad."""
    __tablename__ = 'tareas_propuesta'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('propuestas_actividad.id'), nullable=False, index=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Asignación
    grupo_trabajo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a GrupoTrabajo
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Miembro

    # Estimaciones
    fecha_inicio_estimada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_estimada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    propuesta = relationship('PropuestaActividad', back_populates='tareas', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TareaPropuesta(nombre='{self.nombre}', propuesta_id='{self.propuesta_id}')>"


class RecursoPropuesta(BaseModel):
    """Recurso necesario para una propuesta."""
    __tablename__ = 'recursos_propuesta'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('propuestas_actividad.id'), nullable=False, index=True)
    tipo_recurso_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_recurso.id'), nullable=False, index=True)

    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Estimación
    importe_unitario_estimado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    importe_total_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    importe_aprobado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    proveedor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    propuesta = relationship('PropuestaActividad', back_populates='recursos', lazy='selectin')
    tipo_recurso = relationship('TipoRecurso', lazy='selectin')

    def __repr__(self) -> str:
        return f"<RecursoPropuesta(descripcion='{self.descripcion}', cantidad={self.cantidad})>"


class GrupoPropuesta(BaseModel):
    """Grupo de trabajo asignado a una propuesta."""
    __tablename__ = 'grupos_propuesta'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    propuesta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('propuestas_actividad.id'), nullable=False, index=True)
    grupo_trabajo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a GrupoTrabajo

    tareas_asignadas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    propuesta = relationship('PropuestaActividad', back_populates='grupos_asignados', lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoPropuesta(propuesta_id='{self.propuesta_id}', grupo_id='{self.grupo_trabajo_id}')>"


# === ACTIVIDADES ===

class Actividad(BaseModel):
    """Actividad de la organización."""
    __tablename__ = 'actividades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Propuesta origen
    propuesta_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('propuestas_actividad.id'), nullable=True, index=True)

    # Tipo y estado
    tipo_actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_actividad.id'), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_actividad.id'), nullable=False, index=True)
    prioridad: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1=Alta, 2=Media, 3=Baja

    # Programación
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    hora_fin: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    es_todo_el_dia: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Ubicación
    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    es_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones organizativas
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=True, index=True)  # FK a Campania (opcional - actividades permanentes)
    coordinador_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro (responsable)
    grupo_trabajo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a GrupoTrabajo (grupo principal)
    es_colectiva: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Presupuesto
    # VALIDACIÓN: El servicio debe verificar que PartidaPresupuestaria.ejercicio == fecha_inicio.year
    partida_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a PartidaPresupuestaria
    dotacion_economica: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    gasto_real: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)

    # Voluntariado
    voluntarios_necesarios: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    voluntarios_confirmados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Finalización
    completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resultados: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    campania = relationship('Campania', back_populates='actividades', lazy='selectin')
    tipo_actividad = relationship('TipoActividad', back_populates='actividades', lazy='selectin')
    estado = relationship('EstadoActividad', back_populates='actividades', lazy='selectin')
    propuesta = relationship('PropuestaActividad', lazy='selectin')
    tareas = relationship('TareaActividad', back_populates='actividad', lazy='selectin')
    recursos = relationship('RecursoActividad', back_populates='actividad', lazy='selectin')
    participantes = relationship('ParticipanteActividad', back_populates='actividad', lazy='selectin')
    grupos_trabajo = relationship('GrupoActividad', back_populates='actividad', lazy='selectin')
    kpis = relationship('KPIActividad', back_populates='actividad', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Actividad(codigo='{self.codigo}', nombre='{self.nombre}')>"

    @property
    def porcentaje_voluntarios(self) -> Decimal:
        if self.voluntarios_necesarios == 0:
            return Decimal("100")
        return (Decimal(self.voluntarios_confirmados) / Decimal(self.voluntarios_necesarios)) * 100


class TareaActividad(BaseModel):
    """Tarea asociada a una actividad."""
    __tablename__ = 'tareas_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id'), nullable=False, index=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Asignación
    grupo_trabajo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a GrupoTrabajo
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Miembro

    # Estado
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_tarea.id'), nullable=False, index=True)

    # Fechas
    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Horas
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    horas_reales: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    actividad = relationship('Actividad', back_populates='tareas', lazy='selectin')
    estado = relationship('EstadoTarea', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<TareaActividad(nombre='{self.nombre}', actividad_id='{self.actividad_id}')>"


class RecursoActividad(BaseModel):
    """Recurso utilizado en una actividad."""
    __tablename__ = 'recursos_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id'), nullable=False, index=True)
    tipo_recurso_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_recurso.id'), nullable=False, index=True)

    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Costes
    importe_presupuestado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    importe_real: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    # Proveedor y facturación
    proveedor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    factura_referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha_factura: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pagado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    actividad = relationship('Actividad', back_populates='recursos', lazy='selectin')
    tipo_recurso = relationship('TipoRecurso', lazy='selectin')

    def __repr__(self) -> str:
        return f"<RecursoActividad(descripcion='{self.descripcion}', cantidad={self.cantidad})>"


class GrupoActividad(BaseModel):
    """Grupo de trabajo participante en una actividad."""
    __tablename__ = 'grupos_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id'), nullable=False, index=True)
    grupo_trabajo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a GrupoTrabajo

    tareas_asignadas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    horas_reales: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    actividad = relationship('Actividad', back_populates='grupos_trabajo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoActividad(actividad_id='{self.actividad_id}', grupo_id='{self.grupo_trabajo_id}')>"


class ParticipanteActividad(BaseModel):
    """Participante en una actividad."""
    __tablename__ = 'participantes_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro

    rol: Mapped[str] = mapped_column(String(50), nullable=False)  # VOLUNTARIO, COORDINADOR, etc.
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    horas_aportadas: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal('0.00'), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    actividad = relationship('Actividad', back_populates='participantes', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ParticipanteActividad(miembro_id='{self.miembro_id}', rol='{self.rol}')>"


# === KPIs ===

class KPI(BaseModel):
    """Indicador clave de rendimiento (KPI) genérico."""
    __tablename__ = 'kpis'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_kpi_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_kpi.id'), nullable=False, index=True)
    unidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    valor_objetivo_defecto: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    valor_minimo: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    tipo_kpi = relationship('TipoKPI', back_populates='kpis', lazy='selectin')

    def __repr__(self) -> str:
        return f"<KPI(codigo='{self.codigo}', nombre='{self.nombre}')>"


class KPIActividad(BaseModel):
    """KPI asociado a una actividad específica."""
    __tablename__ = 'kpis_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id'), nullable=False, index=True)
    kpi_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('kpis.id'), nullable=False, index=True)

    valor_objetivo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    peso: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal('1.00'), nullable=False)
    valor_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    fecha_ultima_medicion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    porcentaje_logro: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    actividad = relationship('Actividad', back_populates='kpis', lazy='selectin')
    kpi = relationship('KPI', lazy='selectin')
    mediciones = relationship('MedicionKPI', back_populates='kpi_actividad', lazy='selectin')

    def __repr__(self) -> str:
        return f"<KPIActividad(kpi_id='{self.kpi_id}', objetivo={self.valor_objetivo})>"


class MedicionKPI(BaseModel):
    """Medición de un KPI en una actividad."""
    __tablename__ = 'mediciones_kpi'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kpi_actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('kpis_actividad.id'), nullable=False, index=True)

    valor_medido: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_medicion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    medido_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Miembro
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    kpi_actividad = relationship('KPIActividad', back_populates='mediciones', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MedicionKPI(valor={self.valor_medido}, fecha='{self.fecha_medicion}')>"
