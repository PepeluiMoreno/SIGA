"""Modelo de Actividad — unidad operativa de la ONG (reemplaza Accion)."""

import uuid
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, Time, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class TipoActividad(InmutableMixin, BaseModel):
    """Catálogo de tipos de actividad (evento público, reunión, taller, etc.)."""
    __tablename__ = 'tipos_accion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tiene_lugar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tiene_participantes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Cuenta contable por defecto a la que se imputarán los gastos de los justificantes
    # de actividades de este tipo. Si es NULL, el tesorero la elegirá manualmente al pagar.
    cuenta_contable_default_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('cuentas_contables.id', ondelete='SET NULL'), nullable=True, index=True,
    )
    # Actividades de gobierno interno (asambleas, juntas, comisiones)
    es_actividad_gobierno: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="True para actividades de secretaría y presidencia"
    )
    # FK al tipo de reunión de secretaría que genera esta actividad (si aplica)
    tipo_reunion_secretaria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_tipos_reunion.id'), nullable=True,
        comment="Vincula con el TipoReunion de secretaría que crea instancias de este tipo"
    )

    actividades = relationship('Actividad', back_populates='tipo_actividad', lazy='selectin')
    cuenta_contable_default = relationship(
        'CuentaContable', foreign_keys=[cuenta_contable_default_id], lazy='selectin',
    )

    def __repr__(self) -> str:
        return f"<TipoActividad(nombre='{self.nombre}')>"


# Alias de compatibilidad — el catálogo sigue llamándose TipoAccion en muchos sitios
TipoAccion = TipoActividad


class Actividad(BaseModel):
    """Unidad operativa: cualquier actividad concreta que organiza la ONG.

    Si campania_id está presente, es una actividad de campaña (externa/divulgativa).
    Si campania_id es None, es una actividad interna (reunión, asamblea, coordinación).

    Si es_recurrente=True y padre_id=None, es una plantilla de actividad recurrente.
    Si padre_id apunta a otra Actividad, es una instancia de esa plantilla.
    """
    __tablename__ = 'actividades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('tipos_accion.id'), nullable=False, index=True
    )
    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('estados_accion.id'), nullable=False, index=True
    )

    # Recurrencia (auto-referencia)
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=True, index=True
    )
    es_recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodicidad: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 'diaria','semanal','mensual','trimestral','anual','continua'

    # Carácter temporal explícito (taxonomía de 5 categorías):
    #   PUNTUAL    — ocurre una vez con fecha concreta
    #   RECURRENTE — patrón con instancias (plantilla=padre_id NULL, instancia=padre_id NOT NULL)
    #   PERMANENTE — actividad continua agregadora (solo fuera de campaña)
    # Reglas duras:
    #   - PERMANENTE ⇒ campania_id IS NULL, es_recurrente=False, padre_id=NULL.
    #   - Si campania_id IS NOT NULL ⇒ caracter ∈ {PUNTUAL, RECURRENTE}.
    caracter: Mapped[str] = mapped_column(
        String(15), nullable=False, default="PUNTUAL", server_default="PUNTUAL", index=True,
    )

    # Campaña (si presente → actividad de campaña externa)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('campanias.id'), nullable=True, index=True
    )

    # Grupo de trabajo responsable (opcional)
    grupo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('grupos_trabajo.id'), nullable=True, index=True
    )
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True, index=True
    )

    # Temporal
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    hora_inicio: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    hora_fin: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Duración estimada (puede usarse sin fechas concretas en planificación)
    duracion_horas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    duracion_dias: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Presencia física
    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    aforo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    es_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_online: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        comment='Legacy: URL libre. Cuando hay plataforma_telematica_id se prefiere ese catálogo.'
    )
    plataforma_telematica_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_plataformas_telematicas.id'), nullable=True, index=True,
    )
    datos_conexion_telematica: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='JSON con valores de los campos definidos por la plataforma telemática.'
    )

    # Económico
    presupuesto_estimado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal('0.00'), nullable=False
    )
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal('0.00'), nullable=False
    )

    # Aprobación formal
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas_aprobacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Valoración final
    valoracion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objetivos_cumplidos: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    asistencia_real: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    tipo_actividad = relationship('TipoActividad', back_populates='actividades', lazy='selectin')
    estado = relationship('EstadoAccion', foreign_keys=[estado_id], lazy='selectin')
    aprobado_por = relationship('Usuario', foreign_keys=[aprobado_por_id], lazy='selectin')
    campania = relationship('Campania', foreign_keys=[campania_id], back_populates='actividades', lazy='selectin')
    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    padre = relationship(
        'Actividad', remote_side='Actividad.id',
        foreign_keys=[padre_id], lazy='selectin',
    )
    hijos = relationship(
        'Actividad', back_populates='padre',
        foreign_keys=[padre_id], lazy='selectin',
    )
    tareas = relationship(
        'Tarea', back_populates='actividad',
        foreign_keys='Tarea.actividad_id', lazy='selectin',
    )
    asistencias = relationship('AsistenciaActividad', back_populates='actividad', lazy='selectin')
    partidas = relationship('PartidaPresupuestoActividad', back_populates='actividad', lazy='selectin', cascade='all, delete-orphan')
    registros_trabajo = relationship('RegistroTrabajoActividad', back_populates='actividad', lazy='selectin', cascade='all, delete-orphan')
    documentos = relationship('DocumentoActividad', back_populates='actividad', lazy='selectin', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Actividad(nombre='{self.nombre}')>"


# Alias de compatibilidad
Accion = Actividad


class AsistenciaActividad(BaseModel):
    """Asistencia/inscripción de un contacto a una actividad concreta.

    Es una forma de participación: satélite de Participacion (base).
    Otorga/mantiene la vinculación correspondiente (voluntario, o participante).
    El antiguo par nombre_externo/email_externo desaparece: un externo es
    simplemente un Contacto creado al vuelo.
    """
    __tablename__ = 'asistencias_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    participacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('participaciones.id', ondelete='CASCADE'),
        nullable=False, unique=True, index=True
    )
    actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=False, index=True
    )

    rol: Mapped[str] = mapped_column(String(50), nullable=False, default='asistente')
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    horas_aportadas: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=Decimal('0.00'), nullable=False
    )

    actividad = relationship('Actividad', back_populates='asistencias', lazy='selectin')
    participacion = relationship(
        'Participacion', back_populates='asistencia_actividad',
        foreign_keys=[participacion_id], lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<AsistenciaActividad(actividad_id='{self.actividad_id}', rol='{self.rol}')>"


class PartidaPresupuestoActividad(BaseModel):
    """Desglose de presupuesto por partida a nivel de actividad."""
    __tablename__ = 'partidas_presupuesto_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id', ondelete='CASCADE'), nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(200), nullable=False)
    importe_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    importe_real: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tipo_partida: Mapped[str] = mapped_column(String(10), nullable=False, default='gasto')  # 'gasto' | 'ingreso'
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    actividad = relationship('Actividad', back_populates='partidas', lazy='selectin')
    documentos = relationship('DocumentoPartida', back_populates='partida_actividad', lazy='selectin', cascade='all, delete-orphan', foreign_keys='DocumentoPartida.partida_actividad_id')

    def __repr__(self) -> str:
        return f"<PartidaPresupuestoActividad(concepto='{self.concepto}', importe={self.importe_estimado})>"


class RegistroTrabajoActividad(BaseModel):
    """Parte de trabajo: horas aportadas por un miembro a una actividad."""
    __tablename__ = 'registros_trabajo_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id', ondelete='CASCADE'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('miembros.id'), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    horas: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default='presencia')  # presencia|teletrabajo|coordinacion|otro
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actividad = relationship('Actividad', back_populates='registros_trabajo', lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<RegistroTrabajoActividad(miembro_id='{self.miembro_id}', horas={self.horas})>"


class DocumentoActividad(BaseModel):
    """Documento adjunto a una actividad (acta, informe, foto, material)."""
    __tablename__ = 'documentos_actividad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('actividades.id', ondelete='CASCADE'), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(300), nullable=False)
    ruta: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_mime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tamanyo: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    tipo_doc: Mapped[str] = mapped_column(String(20), nullable=False, default='otro')  # acta|informe|foto|material|otro
    subido_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actividad = relationship('Actividad', back_populates='documentos', lazy='selectin')
    subido_por = relationship('Usuario', foreign_keys=[subido_por_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<DocumentoActividad(nombre='{self.nombre}', tipo='{self.tipo_doc}')>"


class DocumentoPartida(BaseModel):
    """Justificante contable adjunto a una partida de presupuesto (factura, ticket, etc.)."""
    __tablename__ = 'documentos_partida'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    partida_actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('partidas_presupuesto_actividad.id', ondelete='CASCADE'), nullable=True, index=True)
    partida_campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('partidas_presupuesto_campania.id', ondelete='CASCADE'), nullable=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(300), nullable=False)
    ruta: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_mime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tamanyo: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    tipo_doc: Mapped[str] = mapped_column(String(20), nullable=False, default='otro')  # factura|ticket|presupuesto|otro
    subido_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    partida_actividad = relationship('PartidaPresupuestoActividad', back_populates='documentos', foreign_keys=[partida_actividad_id], lazy='selectin')
    subido_por = relationship('Usuario', foreign_keys=[subido_por_id], lazy='selectin')
