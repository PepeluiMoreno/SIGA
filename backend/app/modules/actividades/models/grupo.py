"""Modelos de grupos de trabajo."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin

if TYPE_CHECKING:
    from ...membresia.models.contacto import Contacto


class TipoGrupo(InmutableMixin, BaseModel):
    """Tipos de grupos de trabajo."""
    __tablename__ = 'tipos_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    es_permanente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    grupos = relationship('GrupoTrabajo', back_populates='tipo_grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoGrupo(nombre='{self.nombre}')>"


class RolGrupo(BaseModel):
    """Roles que pueden tener los miembros en un grupo."""
    __tablename__ = 'roles_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    es_coordinador: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_editar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    puede_aprobar_gastos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    miembros_grupo = relationship('MiembroGrupo', back_populates='rol_grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<RolGrupo(nombre='{self.nombre}')>"


class GrupoTrabajo(BaseModel):
    """Grupo de trabajo de la organización."""
    __tablename__ = 'grupos_trabajo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_grupo.id'), nullable=False, index=True)

    # Coordinador principal del grupo (miembro responsable)
    coordinador_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('contactos.id', name='fk_grupos_trabajo_coordinador_id'), nullable=True, index=True
    )

    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)

    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    objetivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    presupuesto_asignado: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('unidades_organizativas.id'), nullable=True, index=True
    )

    tipo_grupo = relationship('TipoGrupo', back_populates='grupos', lazy='selectin')
    coordinador = relationship('Contacto', foreign_keys=[coordinador_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    miembros = relationship('MiembroGrupo', back_populates='grupo', lazy='selectin')
    tareas = relationship('Tarea', back_populates='grupo', foreign_keys='Tarea.grupo_id', lazy='selectin')
    reuniones = relationship('ReunionGrupo', back_populates='grupo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoTrabajo(nombre='{self.nombre}')>"

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
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('contactos.id', ondelete='CASCADE'), nullable=False, index=True
    )
    rol_grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('roles_grupo.id'), nullable=False, index=True)

    fecha_incorporacion: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    responsabilidades: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    grupo = relationship('GrupoTrabajo', back_populates='miembros', lazy='selectin')
    rol_grupo = relationship('RolGrupo', back_populates='miembros_grupo', lazy='selectin')
    miembro: Mapped['Contacto'] = relationship('Contacto', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<MiembroGrupo(miembro_id='{self.miembro_id}', grupo_id='{self.grupo_id}')>"


class GrupoIniciativa(BaseModel):
    """Asociación explícita entre un GrupoTrabajo y una Campaña."""
    __tablename__ = 'grupo_iniciativa'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)
    campania_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('campanias.id'), nullable=False, index=True)
    rol: Mapped[str] = mapped_column(String(50), nullable=False, default='colaborador')

    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<GrupoIniciativa(grupo_id='{self.grupo_id}', campania_id='{self.campania_id}')>"


class RequisitoRecurso(BaseModel):
    """Bolsa de horas necesarias de una especialidad/nivel para un grupo en una campaña o actividad."""
    __tablename__ = 'requisitos_recurso'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)

    # Referencia a la especialidad del catálogo (habilidad o competencia)
    especialidad_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    nivel_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    horas_necesarias: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    grupo = relationship('GrupoTrabajo', foreign_keys=[grupo_id], lazy='selectin')
    aportaciones = relationship('AportacionHoras', back_populates='requisito', lazy='selectin')

    @property
    def horas_cubiertas(self) -> Decimal:
        return sum(
            (a.horas_comprometidas for a in self.aportaciones if a.confirmado),
            Decimal('0.00'),
        )

    @property
    def horas_pendientes(self) -> Decimal:
        return max(self.horas_necesarias - self.horas_cubiertas, Decimal('0.00'))

    def __repr__(self) -> str:
        return f"<RequisitoRecurso(grupo_id='{self.grupo_id}', horas={self.horas_necesarias})>"


class AportacionHoras(BaseModel):
    """Compromiso de horas de un voluntario para cubrir un RequisitoRecurso."""
    __tablename__ = 'aportaciones_horas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    requisito_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('requisitos_recurso.id'), nullable=False, index=True
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('contactos.id', ondelete='CASCADE'), nullable=False, index=True
    )

    horas_comprometidas: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    horas_reales: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal('0.00'), nullable=False)
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_compromiso: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    requisito = relationship('RequisitoRecurso', back_populates='aportaciones', lazy='selectin')
    miembro = relationship('Contacto', foreign_keys=[miembro_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<AportacionHoras(miembro_id='{self.miembro_id}', horas={self.horas_comprometidas})>"


class ReunionGrupo(BaseModel):
    """Reunión de un grupo de trabajo."""
    __tablename__ = 'reuniones_grupo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('grupos_trabajo.id'), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    hora_fin: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    lugar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    url_online: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    orden_del_dia: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    realizada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    grupo = relationship('GrupoTrabajo', back_populates='reuniones', lazy='selectin')
    asistentes = relationship('AsistenteReunion', back_populates='reunion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ReunionGrupo(titulo='{self.titulo}', fecha='{self.fecha}')>"


class AsistenteReunion(BaseModel):
    """Asistente a una reunión de grupo."""
    __tablename__ = 'asistentes_reunion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    reunion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('reuniones_grupo.id'), nullable=False, index=True)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    asistio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reunion = relationship('ReunionGrupo', back_populates='asistentes', lazy='selectin')

    def __repr__(self) -> str:
        return f"<AsistenteReunion(miembro_id='{self.miembro_id}', reunion_id='{self.reunion_id}')>"
