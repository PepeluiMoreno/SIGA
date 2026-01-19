from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, ForeignKey, DateTime, Date, Numeric, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class TipoGrupo(Base):
    """Tipos de grupo: PERMANENTE, TEMPORAL, TECNICO, COMUNICACION, etc."""
    __tablename__ = "tipo_grupo"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    es_permanente: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class GrupoTrabajo(Base):
    """Grupo de trabajo de la ONG."""
    __tablename__ = "grupo_trabajo"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Clasificación
    tipo_grupo_id: Mapped[int] = mapped_column(ForeignKey("tipo_grupo.id"))

    # Vinculación con campaña (solo para grupos temporales)
    campania_id: Mapped[int | None] = mapped_column(ForeignKey("campania.id"))

    # Fechas
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)  # null = grupo permanente activo

    # Objetivos
    objetivo: Mapped[str | None] = mapped_column(Text)

    # Dotación económica (presupuesto operativo)
    presupuesto_asignado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    presupuesto_ejecutado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Agrupación territorial (si aplica)
    agrupacion_id: Mapped[int | None] = mapped_column(ForeignKey("agrupacion_territorial.id"))

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relaciones
    tipo_grupo: Mapped["TipoGrupo"] = relationship()
    campania: Mapped["Campania | None"] = relationship()
    agrupacion: Mapped["AgrupacionTerritorial | None"] = relationship()
    creador: Mapped["Usuario"] = relationship(foreign_keys=[created_by_id])
    miembros: Mapped[list["MiembroGrupo"]] = relationship(back_populates="grupo")
    tareas: Mapped[list["TareaGrupo"]] = relationship(back_populates="grupo")
    reuniones: Mapped[list["ReunionGrupo"]] = relationship(back_populates="grupo")
    # Tareas de actividades asignadas a este grupo
    tareas_actividades: Mapped[list["TareaActividad"]] = relationship(back_populates="grupo_trabajo")
    tareas_propuestas: Mapped[list["TareaPropuesta"]] = relationship(back_populates="grupo_trabajo")


class RolGrupo(Base):
    """Roles dentro de un grupo: COORDINADOR, MIEMBRO, SECRETARIO, etc."""
    __tablename__ = "rol_grupo"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    es_coordinador: Mapped[bool] = mapped_column(Boolean, default=False)
    puede_editar: Mapped[bool] = mapped_column(Boolean, default=False)
    puede_aprobar_gastos: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class MiembroGrupo(Base):
    """Membresía de un miembro en un grupo de trabajo."""
    __tablename__ = "miembro_grupo"

    # Clave primaria compuesta
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_trabajo.id"), primary_key=True)
    miembro_id: Mapped[int] = mapped_column(ForeignKey("miembro.id"), primary_key=True)

    rol_grupo_id: Mapped[int] = mapped_column(ForeignKey("rol_grupo.id"))

    # Fechas de participación
    fecha_incorporacion: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_baja: Mapped[date | None] = mapped_column(Date)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Observaciones
    responsabilidades: Mapped[str | None] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    grupo: Mapped["GrupoTrabajo"] = relationship(back_populates="miembros")
    miembro: Mapped["Miembro"] = relationship()
    rol_grupo: Mapped["RolGrupo"] = relationship()


class EstadoTarea(Base):
    """Estados de tarea: PENDIENTE, EN_PROGRESO, COMPLETADA, CANCELADA."""
    __tablename__ = "estado_tarea"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str | None] = mapped_column(String(7))
    es_final: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class TareaGrupo(Base):
    """Tareas asignadas dentro de un grupo de trabajo."""
    __tablename__ = "tarea_grupo"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_trabajo.id"))

    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Asignación
    asignado_a_id: Mapped[int | None] = mapped_column(ForeignKey("miembro.id"))

    # Estado y prioridad
    estado_id: Mapped[int] = mapped_column(ForeignKey("estado_tarea.id"))
    prioridad: Mapped[int] = mapped_column(Integer, default=2)  # 1=Alta, 2=Media, 3=Baja

    # Fechas
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_limite: Mapped[date | None] = mapped_column(Date)
    fecha_completada: Mapped[datetime | None] = mapped_column(DateTime)

    # Horas
    horas_estimadas: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    horas_reales: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Auditoría
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))

    # Relaciones
    grupo: Mapped["GrupoTrabajo"] = relationship(back_populates="tareas")
    asignado_a: Mapped["Miembro | None"] = relationship()
    estado: Mapped["EstadoTarea"] = relationship()
    creado_por: Mapped["Usuario"] = relationship()


class ReunionGrupo(Base):
    """Reuniones de un grupo de trabajo."""
    __tablename__ = "reunion_grupo"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_trabajo.id"))

    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Fecha y hora
    fecha: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[str | None] = mapped_column(String(5))  # "10:00"
    hora_fin: Mapped[str | None] = mapped_column(String(5))     # "12:00"

    # Ubicación
    lugar: Mapped[str | None] = mapped_column(String(200))
    url_online: Mapped[str | None] = mapped_column(String(500))  # Link videoconferencia

    # Contenido
    orden_del_dia: Mapped[str | None] = mapped_column(Text)
    acta: Mapped[str | None] = mapped_column(Text)

    # Estado
    realizada: Mapped[bool] = mapped_column(Boolean, default=False)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))

    # Relaciones
    grupo: Mapped["GrupoTrabajo"] = relationship(back_populates="reuniones")
    creador: Mapped["Usuario"] = relationship()
    asistentes: Mapped[list["AsistenteReunion"]] = relationship(back_populates="reunion")


class AsistenteReunion(Base):
    """Asistentes a una reunión."""
    __tablename__ = "asistente_reunion"

    # Clave primaria compuesta
    reunion_id: Mapped[int] = mapped_column(ForeignKey("reunion_grupo.id"), primary_key=True)
    miembro_id: Mapped[int] = mapped_column(ForeignKey("miembro.id"), primary_key=True)

    # Estado
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False)
    asistio: Mapped[bool | None] = mapped_column(Boolean)

    # Observaciones
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    reunion: Mapped["ReunionGrupo"] = relationship(back_populates="asistentes")
    miembro: Mapped["Miembro"] = relationship()


# Imports para evitar circular imports
from .campania import Campania  # noqa: E402,F401
from .agrupacion import AgrupacionTerritorial  # noqa: E402,F401
from .usuario import Usuario  # noqa: E402,F401
from .miembro import Miembro  # noqa: E402,F401
from .actividad import TareaActividad, TareaPropuesta  # noqa: E402,F401
