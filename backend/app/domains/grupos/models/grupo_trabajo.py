"""Modelos de grupos de trabajo."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoGrupo(BaseModel):
    """Tipos de grupos de trabajo."""
    __tablename__ = 'tipos_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    es_permanente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    grupos = relationship('GrupoTrabajo', back_populates='tipo_grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoGrupo(codigo='{self.codigo}', nombre='{self.nombre}')>"


class RolGrupo(BaseModel):
    """Roles que pueden tener los miembros en un grupo."""
    __tablename__ = 'roles_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Permisos
    es_coordinador: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_editar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_aprobar_gastos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    miembros_grupo = relationship('MiembroGrupo', back_populates='rol_grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<RolGrupo(codigo='{self.codigo}', nombre='{self.nombre}')>"


class GrupoTrabajo(BaseModel):
    """Grupo de trabajo de la organización."""
    __tablename__ = 'grupos_trabajo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo
    tipo_grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_grupo.id'), nullable=False, index=True)

    # Campaña asociada (si aplica)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Campania

    # Temporalidad
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    objetivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Presupuesto
    presupuesto_asignado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)

    # Estado y ubicación
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=True, index=True)

    # Relaciones
    tipo_grupo = relationship('TipoGrupo', back_populates='grupos', lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')
    miembros = relationship('MiembroGrupo', back_populates='grupo', lazy='selectin')
    tareas = relationship('TareaGrupo', back_populates='grupo', lazy='selectin')
    reuniones = relationship('ReunionGrupo', back_populates='grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoTrabajo(codigo='{self.codigo}', nombre='{self.nombre}')>"

    @property
    def presupuesto_disponible(self) -> Optional[Decimal]:
        if self.presupuesto_asignado is None:
            return None
        return self.presupuesto_asignado - self.presupuesto_ejecutado


class MiembroGrupo(BaseModel):
    """Miembro participante en un grupo de trabajo."""
    __tablename__ = 'miembros_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    rol_grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('roles_grupo.id'), nullable=False, index=True)

    fecha_incorporacion: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    responsabilidades: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    grupo = relationship('GrupoTrabajo', back_populates='miembros', lazy='selectin')
    rol_grupo = relationship('RolGrupo', back_populates='miembros_grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MiembroGrupo(miembro_id='{self.miembro_id}', grupo_id='{self.grupo_id}')>"


class TareaGrupo(BaseModel):
    """Tarea asignada a un grupo de trabajo."""
    __tablename__ = 'tareas_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asignado_a_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # FK a Miembro
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_tarea.id'), nullable=False, index=True)
    prioridad: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1=Alta, 2=Media, 3=Baja

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_completada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    horas_estimadas: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    horas_reales: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # Relaciones
    grupo = relationship('GrupoTrabajo', back_populates='tareas', lazy='selectin')
    estado = relationship('EstadoTarea', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<TareaGrupo(titulo='{self.titulo}', grupo_id='{self.grupo_id}')>"


class ReunionGrupo(BaseModel):
    """Reunión de un grupo de trabajo."""
    __tablename__ = 'reuniones_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Formato HH:MM
    hora_fin: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    orden_del_dia: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    realizada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    grupo = relationship('GrupoTrabajo', back_populates='reuniones', lazy='selectin')
    asistentes = relationship('AsistenteReunion', back_populates='reunion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ReunionGrupo(titulo='{self.titulo}', fecha='{self.fecha}')>"


class AsistenteReunion(BaseModel):
    """Asistente a una reunión de grupo."""
    __tablename__ = 'asistentes_reunion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    reunion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('reuniones_grupo.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro

    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    reunion = relationship('ReunionGrupo', back_populates='asistentes', lazy='selectin')

    def __repr__(self) -> str:
        return f"<AsistenteReunion(miembro_id='{self.miembro_id}', reunion_id='{self.reunion_id}')>"
