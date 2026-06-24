"""Modelos de campañas y acciones."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class TipoCampania(InmutableMixin, BaseModel):
    """Tipos de campañas disponibles."""
    __tablename__ = 'tipos_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    campanias = relationship('Campania', back_populates='tipo_campania', lazy='selectin')
    plantilla = relationship('PlantillaCampania', back_populates='tipo_campania', uselist=False, lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoCampania(nombre='{self.nombre}')>"


# ── Catálogos de metas y canales ─────────────────────────────────────────────

class TipoMeta(InmutableMixin, BaseModel):
    """Catálogo de tipos de objetivo/meta para campañas."""
    __tablename__ = 'tipos_meta_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unidad_medida: Mapped[str] = mapped_column(String(30), nullable=False)  # "€", "personas", "firmas", "visitas"…
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    metas = relationship('MetaCampania', back_populates='tipo_meta', lazy='selectin')
    plantilla_metas = relationship('PlantillaMeta', back_populates='tipo_meta', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoMeta(nombre='{self.nombre}', unidad='{self.unidad_medida}')>"


class TipoCanalDifusion(InmutableMixin, BaseModel):
    """Catálogo de canales de difusión elegibles en el diseño de campaña."""
    __tablename__ = 'tipos_canal_difusion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    canales_campania = relationship('CanalDifusionCampania', back_populates='canal', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoCanalDifusion(nombre='{self.nombre}')>"


# ── Instancias por campaña ────────────────────────────────────────────────────

class MetaCampania(BaseModel):
    """Meta concreta de una campaña (tipo + valor planificado/real)."""
    __tablename__ = 'metas_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo_meta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_meta_campania.id'), nullable=False, index=True)
    valor_planificado: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    valor_real: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)  # se rellena al cierre
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    campania = relationship('Campania', back_populates='metas', lazy='selectin')
    tipo_meta = relationship('TipoMeta', back_populates='metas', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MetaCampania(tipo='{self.tipo_meta_id}', plan={self.valor_planificado})>"


class CanalDifusionCampania(BaseModel):
    """Canal de difusión elegido para una campaña."""
    __tablename__ = 'canales_difusion_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id', ondelete='CASCADE'), nullable=False, index=True)
    canal_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_canal_difusion.id'), nullable=False, index=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    campania = relationship('Campania', back_populates='canales', lazy='selectin')
    canal = relationship('TipoCanalDifusion', back_populates='canales_campania', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CanalDifusionCampania(campania='{self.campania_id}', canal='{self.canal_id}')>"


class PartidaPresupuestoCampania(BaseModel):
    """Partida de presupuesto de una campaña (estimado + real al cierre)."""
    __tablename__ = 'partidas_presupuesto_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id', ondelete='CASCADE'), nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(200), nullable=False)
    importe_estimado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    importe_real: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)  # se rellena al cierre
    tipo_partida: Mapped[str] = mapped_column(String(20), default='gasto', nullable=False)  # 'gasto' | 'ingreso'
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    campania = relationship('Campania', back_populates='partidas_presupuesto', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PartidaPresupuestoCampania(concepto='{self.concepto}', tipo='{self.tipo_partida}')>"


# ── Plantillas (1 por TipoCampania) ──────────────────────────────────────────

class PlantillaCampania(BaseModel):
    """Plantilla de campaña asociada a un tipo (1:1)."""
    __tablename__ = 'plantillas_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tipo_campania_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('tipos_campania.id'), nullable=False, unique=True, index=True
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tipo_campania = relationship('TipoCampania', back_populates='plantilla', lazy='selectin')
    metas = relationship('PlantillaMeta', back_populates='plantilla', cascade='all, delete-orphan', lazy='selectin')
    partidas = relationship('PlantillaPartida', back_populates='plantilla', cascade='all, delete-orphan', lazy='selectin')
    actividades = relationship('PlantillaActividad', back_populates='plantilla', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PlantillaCampania(nombre='{self.nombre}')>"


class PlantillaMeta(BaseModel):
    """Meta predefinida dentro de una plantilla."""
    __tablename__ = 'plantilla_metas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plantilla_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('plantillas_campania.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo_meta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_meta_campania.id'), nullable=False, index=True)
    valor_sugerido: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    plantilla = relationship('PlantillaCampania', back_populates='metas', lazy='selectin')
    tipo_meta = relationship('TipoMeta', back_populates='plantilla_metas', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PlantillaMeta(tipo='{self.tipo_meta_id}', sugerido={self.valor_sugerido})>"


class PlantillaPartida(BaseModel):
    """Partida de presupuesto predefinida dentro de una plantilla."""
    __tablename__ = 'plantilla_partidas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plantilla_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('plantillas_campania.id', ondelete='CASCADE'), nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String(200), nullable=False)
    importe_estimado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tipo_partida: Mapped[str] = mapped_column(String(20), default='gasto', nullable=False)  # 'gasto' | 'ingreso'
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    plantilla = relationship('PlantillaCampania', back_populates='partidas', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PlantillaPartida(concepto='{self.concepto}')>"


class PlantillaActividad(BaseModel):
    """Actividad predefinida dentro de una plantilla de campaña."""
    __tablename__ = 'plantilla_actividades'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plantilla_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('plantillas_campania.id', ondelete='CASCADE'), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('tipos_accion.id'), nullable=True, index=True)
    duracion_dias: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # offset relativo al inicio
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    plantilla = relationship('PlantillaCampania', back_populates='actividades', lazy='selectin')
    tipo_actividad = relationship('TipoActividad', lazy='selectin')
    tareas = relationship('PlantillaTarea', back_populates='actividad', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PlantillaActividad(nombre='{self.nombre}')>"


class PlantillaTarea(BaseModel):
    """Tarea predefinida dentro de una actividad de plantilla."""
    __tablename__ = 'plantilla_tareas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('plantilla_actividades.id', ondelete='CASCADE'), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    habilidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('habilidades.id', ondelete='SET NULL'), nullable=True, index=True)
    nivel_habilidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('niveles_habilidad.id', ondelete='SET NULL'), nullable=True, index=True)

    actividad = relationship('PlantillaActividad', back_populates='tareas', lazy='selectin')
    habilidad = relationship('Habilidad', lazy='selectin', foreign_keys=[habilidad_id])
    nivel_habilidad = relationship('NivelHabilidad', lazy='selectin', foreign_keys=[nivel_habilidad_id])

    def __repr__(self) -> str:
        return f"<PlantillaTarea(titulo='{self.titulo}')>"


# ── Campaña principal ─────────────────────────────────────────────────────────

class Campania(BaseModel):
    """Campaña de la organización."""
    __tablename__ = 'campanias'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    lema: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    descripcion_corta: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    descripcion_larga: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_externa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    foto_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Tipo y estado
    tipo_campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_campania.id'), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_campania.id'), nullable=False, index=True)

    # Fechas planificadas y reales
    fecha_inicio_plan: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_plan: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_inicio_real: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_real: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Objetivo cualitativo (complementa las metas cuantitativas del catálogo)
    objetivo_principal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Presupuesto total (calculado/resumen de partidas)
    presupuesto_estimado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    presupuesto_ejecutado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    # Aprobación formal
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas_aprobacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Valoración final
    valoracion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objetivos_cumplidos: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Responsable y ubicación organizativa
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('miembros.id'), nullable=True, index=True)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('unidades_organizativas.id'), nullable=True, index=True)

    # Notificación a la membresía (flag one-shot)
    notificacion_enviada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Recurrencia
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=True, index=True)
    es_recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodicidad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    anio_edicion: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    tipo_campania = relationship('TipoCampania', back_populates='campanias', lazy='selectin')
    estado = relationship('EstadoCampania', foreign_keys=[estado_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    aprobado_por = relationship('Usuario', foreign_keys=[aprobado_por_id], lazy='selectin')
    padre = relationship('Campania', remote_side='Campania.id', foreign_keys=[padre_id], lazy='selectin')
    ediciones = relationship('Campania', back_populates='padre', foreign_keys=[padre_id], lazy='selectin')
    actividades = relationship('Actividad', back_populates='campania', foreign_keys='Actividad.campania_id', lazy='selectin')
    firmas = relationship('FirmaCampania', back_populates='campania', lazy='selectin')
    metas = relationship('MetaCampania', back_populates='campania', cascade='all, delete-orphan', lazy='selectin')
    canales = relationship('CanalDifusionCampania', back_populates='campania', cascade='all, delete-orphan', lazy='selectin')
    partidas_presupuesto = relationship('PartidaPresupuestoCampania', back_populates='campania', cascade='all, delete-orphan', lazy='selectin')

    # Códigos de estado que indican que la campaña no admite nuevos gastos/ingresos.
    # Convención: el código del estado (estable, no traducible) es la API que consume
    # el backend; el `nombre` puede cambiar libremente.
    CODIGOS_ESTADO_CERRADO = frozenset({"CERRADA", "CANCELADA"})

    @property
    def esta_cerrada(self) -> bool:
        """True si la campaña está cerrada económicamente y no admite nuevos movimientos."""
        return bool(self.estado and getattr(self.estado, "codigo", None) in self.CODIGOS_ESTADO_CERRADO)

    def __repr__(self) -> str:
        return f"<Campania(nombre='{self.nombre}', estado_id='{self.estado_id}')>"


class FirmaCampania(BaseModel):
    """Satélite de Participacion: firma de un contacto a una campaña.

    El antiguo modelo `Firmante` se disolvió: un firmante es un Contacto (PF)
    con al menos una FirmaCampania. Los datos personales viven en Contacto.
    """
    __tablename__ = 'firmas_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    participacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('participaciones.id', ondelete='CASCADE'),
        nullable=False, unique=True, index=True
    )
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=False, index=True)
    contacto_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('contactos.id'), nullable=False, index=True)

    fecha_firma: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    acepta_terminos: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_verificacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    campania = relationship('Campania', back_populates='firmas', lazy='selectin')
    contacto = relationship('Contacto', back_populates='firmas_campania', foreign_keys=[contacto_id], lazy='selectin')
    participacion = relationship('Participacion', back_populates='firma_campania', foreign_keys=[participacion_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<FirmaCampania(campania_id='{self.campania_id}', fecha='{self.fecha_firma}')>"
