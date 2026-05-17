import strawberry
from datetime import date, datetime
from decimal import Decimal

from .tipos_base import UnidadOrganizativa
from .miembro import Miembro
from .usuario import Usuario


@strawberry.type
class TipoCampania:
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool


@strawberry.type
class EstadoCampania:
    id: int
    codigo: str
    nombre: str
    orden: int
    color: str | None
    activo: bool


@strawberry.type
class RolParticipante:
    id: int
    codigo: str
    nombre: str
    es_voluntario: bool
    es_coordinador: bool
    es_donante: bool
    activo: bool


@strawberry.type
class AccionCampania:
    id: int
    nombre: str
    descripcion: str | None
    fecha: date
    hora_inicio: str | None
    hora_fin: str | None
    lugar: str | None
    direccion: str | None
    voluntarios_necesarios: int
    voluntarios_confirmados: int
    materiales_necesarios: str | None
    observaciones: str | None
    completada: bool

    @strawberry.field
    def plazas_disponibles(self) -> int:
        return self.voluntarios_necesarios - self.voluntarios_confirmados


@strawberry.type
class ParticipanteCampania:
    miembro: Miembro
    rol_participante: RolParticipante
    horas_aportadas: Decimal | None
    confirmado: bool
    asistio: bool | None
    fecha_inscripcion: datetime
    fecha_confirmacion: datetime | None
    observaciones: str | None


@strawberry.type
class Campania:
    id: int
    codigo: str
    nombre: str
    descripcion_corta: str | None
    descripcion_larga: str | None

    tipo_campania: TipoCampania
    estado_campania: EstadoCampania

    fecha_inicio_plan: date | None
    fecha_fin_plan: date | None
    fecha_inicio_real: date | None
    fecha_fin_real: date | None

    objetivo_principal: str | None
    meta_recaudacion: Decimal | None
    meta_participantes: int | None

    responsable: Miembro | None
    agrupacion: UnidadOrganizativa | None

    created_at: datetime
    creador: Usuario
    updated_at: datetime | None

    acciones: list[AccionCampania]
    participantes: list[ParticipanteCampania]


# --- Input Types ---

@strawberry.input
class CampaniaInput:
    codigo: str
    nombre: str
    descripcion_corta: str | None = None
    descripcion_larga: str | None = None

    tipo_campania_id: int
    estado_campania_id: int | None = None  # Por defecto PLANIFICADA

    fecha_inicio_plan: date | None = None
    fecha_fin_plan: date | None = None

    objetivo_principal: str | None = None
    meta_recaudacion: Decimal | None = None
    meta_participantes: int | None = None

    responsable_id: int | None = None
    agrupacion_id: int | None = None


@strawberry.input
class CampaniaUpdateInput:
    nombre: str | None = None
    descripcion_corta: str | None = None
    descripcion_larga: str | None = None
    tipo_campania_id: int | None = None
    estado_campania_id: int | None = None
    fecha_inicio_plan: date | None = None
    fecha_fin_plan: date | None = None
    fecha_inicio_real: date | None = None
    fecha_fin_real: date | None = None
    objetivo_principal: str | None = None
    meta_recaudacion: Decimal | None = None
    meta_participantes: int | None = None
    responsable_id: int | None = None
    agrupacion_id: int | None = None


@strawberry.input
class AccionCampaniaInput:
    nombre: str
    descripcion: str | None = None
    fecha: date
    hora_inicio: str | None = None
    hora_fin: str | None = None
    lugar: str | None = None
    direccion: str | None = None
    voluntarios_necesarios: int = 0
    materiales_necesarios: str | None = None
    observaciones: str | None = None


@strawberry.input
class AccionCampaniaUpdateInput:
    nombre: str | None = None
    descripcion: str | None = None
    fecha: date | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    lugar: str | None = None
    direccion: str | None = None
    voluntarios_necesarios: int | None = None
    materiales_necesarios: str | None = None
    observaciones: str | None = None
    completada: bool | None = None


@strawberry.input
class InscripcionCampaniaInput:
    campania_id: int
    miembro_id: int
    rol_participante_id: int
    observaciones: str | None = None
