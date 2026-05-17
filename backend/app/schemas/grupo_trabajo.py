import strawberry
from datetime import date, datetime
from decimal import Decimal

from .tipos_base import UnidadOrganizativa
from .miembro import Miembro
from .usuario import Usuario
from .campania import Campania


@strawberry.type
class TipoGrupo:
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    es_permanente: bool
    activo: bool


@strawberry.type
class RolGrupo:
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    es_coordinador: bool
    puede_editar: bool
    puede_aprobar_gastos: bool
    activo: bool


@strawberry.type
class EstadoTarea:
    id: int
    codigo: str
    nombre: str
    orden: int
    color: str | None
    es_final: bool
    activo: bool


@strawberry.type
class MiembroGrupo:
    miembro: Miembro
    rol_grupo: RolGrupo
    fecha_incorporacion: date
    fecha_baja: date | None
    activo: bool
    responsabilidades: str | None
    observaciones: str | None


@strawberry.type
class TareaGrupo:
    id: int
    titulo: str
    descripcion: str | None
    asignado_a: Miembro | None
    estado: EstadoTarea
    prioridad: int
    fecha_creacion: datetime
    fecha_limite: date | None
    fecha_completada: datetime | None
    horas_estimadas: Decimal | None
    horas_reales: Decimal | None

    @strawberry.field
    def prioridad_texto(self) -> str:
        prioridades = {1: "Alta", 2: "Media", 3: "Baja"}
        return prioridades.get(self.prioridad, "Media")


@strawberry.type
class AsistenteReunion:
    miembro: Miembro
    confirmado: bool
    asistio: bool | None
    observaciones: str | None


@strawberry.type
class ReunionGrupo:
    id: int
    titulo: str
    descripcion: str | None
    fecha: date
    hora_inicio: str | None
    hora_fin: str | None
    lugar: str | None
    url_online: str | None
    orden_del_dia: str | None
    acta: str | None
    realizada: bool
    asistentes: list[AsistenteReunion]


@strawberry.type
class GrupoTrabajo:
    id: int
    codigo: str
    nombre: str
    descripcion: str | None

    tipo_grupo: TipoGrupo
    campania: Campania | None

    fecha_inicio: date | None
    fecha_fin: date | None
    objetivo: str | None

    presupuesto_asignado: Decimal | None
    presupuesto_ejecutado: Decimal

    activo: bool
    agrupacion: UnidadOrganizativa | None

    created_at: datetime
    creador: Usuario
    updated_at: datetime | None

    miembros: list[MiembroGrupo]
    tareas: list[TareaGrupo]
    reuniones: list[ReunionGrupo]

    @strawberry.field
    def presupuesto_disponible(self) -> Decimal | None:
        if self.presupuesto_asignado is None:
            return None
        return self.presupuesto_asignado - self.presupuesto_ejecutado

    @strawberry.field
    def es_permanente(self) -> bool:
        return self.tipo_grupo.es_permanente

    @strawberry.field
    def total_miembros_activos(self) -> int:
        return len([m for m in self.miembros if m.activo])

    @strawberry.field
    def tareas_pendientes(self) -> int:
        return len([t for t in self.tareas if not t.estado.es_final])


# --- Input Types ---

@strawberry.input
class GrupoTrabajoInput:
    codigo: str
    nombre: str
    descripcion: str | None = None
    tipo_grupo_id: int
    campania_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    objetivo: str | None = None
    presupuesto_asignado: Decimal | None = None
    agrupacion_id: int | None = None


@strawberry.input
class GrupoTrabajoUpdateInput:
    nombre: str | None = None
    descripcion: str | None = None
    tipo_grupo_id: int | None = None
    campania_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    objetivo: str | None = None
    presupuesto_asignado: Decimal | None = None
    agrupacion_id: int | None = None
    activo: bool | None = None


@strawberry.input
class MiembroGrupoInput:
    grupo_id: int
    miembro_id: int
    rol_grupo_id: int
    responsabilidades: str | None = None
    observaciones: str | None = None


@strawberry.input
class MiembroGrupoUpdateInput:
    rol_grupo_id: int | None = None
    responsabilidades: str | None = None
    observaciones: str | None = None
    activo: bool | None = None


@strawberry.input
class TareaGrupoInput:
    grupo_id: int
    titulo: str
    descripcion: str | None = None
    asignado_a_id: int | None = None
    prioridad: int = 2
    fecha_limite: date | None = None
    horas_estimadas: Decimal | None = None


@strawberry.input
class TareaGrupoUpdateInput:
    titulo: str | None = None
    descripcion: str | None = None
    asignado_a_id: int | None = None
    estado_id: int | None = None
    prioridad: int | None = None
    fecha_limite: date | None = None
    horas_estimadas: Decimal | None = None
    horas_reales: Decimal | None = None


@strawberry.input
class ReunionGrupoInput:
    grupo_id: int
    titulo: str
    descripcion: str | None = None
    fecha: date
    hora_inicio: str | None = None
    hora_fin: str | None = None
    lugar: str | None = None
    url_online: str | None = None
    orden_del_dia: str | None = None


@strawberry.input
class ReunionGrupoUpdateInput:
    titulo: str | None = None
    descripcion: str | None = None
    fecha: date | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    lugar: str | None = None
    url_online: str | None = None
    orden_del_dia: str | None = None
    acta: str | None = None
    realizada: bool | None = None
