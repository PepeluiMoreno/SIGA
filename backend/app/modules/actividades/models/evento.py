"""Modelos del dominio de Eventos."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoEvento(BaseModel):
    """Tipos de eventos que organiza la asociación."""
    __tablename__ = 'tipos_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requiere_inscripcion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requiere_aforo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    eventos = relationship('Evento', back_populates='tipo_evento', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoEvento(nombre='{self.nombre}')>"


class EstadoEvento(BaseModel):
    """Estados del ciclo de vida de un evento."""
    __tablename__ = 'estados_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    es_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    eventos = relationship('Evento', back_populates='estado', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EstadoEvento(nombre='{self.nombre}')>"


class Evento(BaseModel):
    """Evento organizado por la asociación.

    Puede ser un acto puntual o una edición de un evento recurrente (p.ej. Asamblea General).
    Tiene presupuesto propio con gastos y grupos de trabajo que preparan tareas.
    """
    __tablename__ = 'eventos'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion_corta: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    descripcion_larga: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo y estado
    tipo_evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_evento.id'), nullable=False, index=True)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_evento.id'), nullable=False, index=True)

    # Recurrencia (p.ej. Asamblea General que se celebra cada año)
    recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodo_recurrencia: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # ANUAL, SEMESTRAL, MENSUAL
    evento_plantilla_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=True, index=True)
    # ↑ Si es una instancia de un evento recurrente, apunta al evento-plantilla original

    # Programación
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    hora_inicio: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    hora_fin: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    es_todo_el_dia: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Lugar de celebración
    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    es_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Capacidad e inscripciones
    aforo_maximo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requiere_inscripcion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_limite_inscripcion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Presupuesto
    dotacion_economica: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    partida_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a PartidaPresupuestaria

    # Responsable principal
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('miembros.id'), nullable=True, index=True)

    # Campaña de divulgación asociada (opcional — p.ej. campaña en redes para el evento)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=True, index=True)

    # Ámbito territorial
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=True, index=True)

    # Observaciones internas
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    tipo_evento = relationship('TipoEvento', back_populates='eventos', lazy='selectin')
    estado = relationship('EstadoEvento', back_populates='eventos', lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    campania = relationship('Campania', foreign_keys=[campania_id], lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', foreign_keys=[agrupacion_id], lazy='selectin')
    evento_plantilla = relationship('Evento', remote_side='Evento.id', foreign_keys=[evento_plantilla_id], lazy='selectin')
    instancias = relationship('Evento', foreign_keys=[evento_plantilla_id], lazy='selectin')
    participantes = relationship('ParticipanteEvento', back_populates='evento', lazy='selectin')
    materiales = relationship('MaterialEvento', back_populates='evento', lazy='selectin')
    grupos = relationship('GrupoEvento', back_populates='evento', lazy='selectin')
    tareas = relationship('TareaEvento', back_populates='evento', lazy='selectin')
    gastos = relationship('GastoEvento', back_populates='evento', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Evento(nombre='{self.nombre}', fecha='{self.fecha_inicio}')>"

    @property
    def num_inscritos(self) -> int:
        return len(self.participantes)

    @property
    def gasto_total(self) -> Decimal:
        return sum((g.importe for g in self.gastos), Decimal('0.00'))

    @property
    def plazas_disponibles(self) -> Optional[int]:
        if self.aforo_maximo is None:
            return None
        return max(0, self.aforo_maximo - self.num_inscritos)


class ParticipanteEvento(BaseModel):
    """Inscripción de un miembro en un evento."""
    __tablename__ = 'participantes_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('miembros.id'), nullable=False, index=True)

    rol: Mapped[str] = mapped_column(String(50), nullable=False, default='ASISTENTE')
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    evento = relationship('Evento', back_populates='participantes', lazy='selectin')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<ParticipanteEvento(evento_id='{self.evento_id}', miembro_id='{self.miembro_id}')>"


class MaterialEvento(BaseModel):
    """Material gráfico o documental de un evento (cartel, infografía, programa)."""
    __tablename__ = 'materiales_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=False, index=True)

    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones
    evento = relationship('Evento', back_populates='materiales', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MaterialEvento(tipo='{self.tipo}', nombre='{self.nombre}')>"


class GrupoEvento(BaseModel):
    """Grupo de trabajo asignado a la organización de un evento."""
    __tablename__ = 'grupos_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=False, index=True)
    grupo_trabajo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)

    responsabilidades: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    evento = relationship('Evento', back_populates='grupos', lazy='selectin')
    grupo_trabajo = relationship('GrupoTrabajo', foreign_keys=[grupo_trabajo_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoEvento(evento_id='{self.evento_id}', grupo_id='{self.grupo_trabajo_id}')>"


class TareaEvento(BaseModel):
    """Tarea preparatoria de un evento, asignada a un grupo o miembro."""
    __tablename__ = 'tareas_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=False, index=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Asignación
    grupo_trabajo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=True, index=True)
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('miembros.id'), nullable=True, index=True)

    # Estado y fechas
    completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    evento = relationship('Evento', back_populates='tareas', lazy='selectin')
    grupo_trabajo = relationship('GrupoTrabajo', foreign_keys=[grupo_trabajo_id], lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<TareaEvento(nombre='{self.nombre}', evento_id='{self.evento_id}')>"


class GastoEvento(BaseModel):
    """Gasto con cargo al presupuesto de un evento."""
    __tablename__ = 'gastos_evento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('eventos.id'), nullable=False, index=True)

    concepto: Mapped[str] = mapped_column(String(500), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Proveedor y factura (FK a entidades del dominio de proveedores, opcional)
    proveedor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)
    factura_referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    pagado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    evento = relationship('Evento', back_populates='gastos', lazy='selectin')

    def __repr__(self) -> str:
        return f"<GastoEvento(concepto='{self.concepto}', importe={self.importe})>"
