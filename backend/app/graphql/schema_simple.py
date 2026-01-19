"""
Schema GraphQL con generación automática de Strawchemy.

Strawchemy genera automáticamente:
- Queries con filtrado, ordenamiento y paginación
- Mutations CRUD (Create, Read, Update, Delete)
- Resolvers optimizados con N+1 prevention
"""

import strawberry

from . import strawchemy
from .types_auto import *  # Importar todos los tipos generados

from ..domains.usuarios.models import Usuario, UsuarioRol
from ..domains.core.models import (
    Configuracion, ReglaValidacionConfig, HistorialConfiguracion,
    EstadoCuota, EstadoCampania, EstadoTarea,
    EstadoParticipante, EstadoOrdenCobro, EstadoRemesa, EstadoDonacion,
    HistorialEstado, Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso
)
from ..domains.geografico.models import Pais, Provincia, Municipio, Direccion, AgrupacionTerritorial
from ..domains.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion
from ..domains.financiero.models import (
    ImporteCuotaAnio, CuotaAnual, DonacionConcepto, Donacion,
    Remesa, OrdenCobro, EstadoPlanificacion, CategoriaPartida,
    PartidaPresupuestaria, PlanificacionAnual
)
from ..domains.colaboraciones.models import Asociacion, TipoAsociacion, Convenio, EstadoConvenio
from ..domains.miembros.models import TipoMiembro, Miembro
from ..domains.campanas.models import (
    TipoCampania, Campania, RolParticipante, ParticipanteCampania
)
from ..domains.actividades.models import (
    TipoActividad, EstadoActividad, EstadoPropuesta, TipoRecurso, TipoKPI,
    PropuestaActividad, TareaPropuesta, RecursoPropuesta, GrupoPropuesta,
    Actividad, TareaActividad, RecursoActividad, GrupoActividad, ParticipanteActividad,
    KPI, KPIActividad, MedicionKPI
)
from ..domains.grupos.models import (
    TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, TareaGrupo, ReunionGrupo, AsistenteReunion
)
from ..domains.voluntariado.models import (
    CategoriaCompetencia, Competencia, NivelCompetencia, MiembroCompetencia,
    TipoDocumentoVoluntario, DocumentoMiembro, TipoFormacion, FormacionMiembro
)


@strawberry.type
class Query:
    """Queries GraphQL del sistema AIEL con generación automática."""

    # === USUARIOS ===
    usuarios: list[UsuarioType] = strawchemy.field(lambda: Usuario)
    usuario_roles: list[UsuarioRolType] = strawchemy.field(lambda: UsuarioRol)

    # === CORE ===
    configuraciones: list[ConfiguracionType] = strawchemy.field(lambda: Configuracion)
    reglas_validacion_config: list[ReglaValidacionConfigType] = strawchemy.field(lambda: ReglaValidacionConfig)
    historial_configuracion: list[HistorialConfiguracionType] = strawchemy.field(lambda: HistorialConfiguracion)
    estados_cuota: list[EstadoCuotaType] = strawchemy.field(lambda: EstadoCuota)
    estados_campania: list[EstadoCampaniaType] = strawchemy.field(lambda: EstadoCampania)
    estados_tarea: list[EstadoTareaType] = strawchemy.field(lambda: EstadoTarea)
    estados_participante: list[EstadoParticipanteType] = strawchemy.field(lambda: EstadoParticipante)
    estados_orden_cobro: list[EstadoOrdenCobroType] = strawchemy.field(lambda: EstadoOrdenCobro)
    estados_remesa: list[EstadoRemesaType] = strawchemy.field(lambda: EstadoRemesa)
    estados_donacion: list[EstadoDonacionType] = strawchemy.field(lambda: EstadoDonacion)
    historial_estado: list[HistorialEstadoType] = strawchemy.field(lambda: HistorialEstado)
    sesiones: list[SesionType] = strawchemy.field(lambda: Sesion)
    historial_seguridad: list[HistorialSeguridadType] = strawchemy.field(lambda: HistorialSeguridad)
    ips_bloqueadas: list[IPBloqueadaType] = strawchemy.field(lambda: IPBloqueada)
    intentos_acceso: list[IntentoAccesoType] = strawchemy.field(lambda: IntentoAcceso)

    # === GEOGRÁFICO ===
    paises: list[PaisType] = strawchemy.field(lambda: Pais)
    provincias: list[ProvinciaType] = strawchemy.field(lambda: Provincia)
    municipios: list[MunicipioType] = strawchemy.field(lambda: Municipio)
    direcciones: list[DireccionType] = strawchemy.field(lambda: Direccion)
    agrupaciones_territoriales: list[AgrupacionTerritorialType] = strawchemy.field(lambda: AgrupacionTerritorial)

    # === NOTIFICACIONES ===
    tipos_notificacion: list[TipoNotificacionType] = strawchemy.field(lambda: TipoNotificacion)
    notificaciones: list[NotificacionType] = strawchemy.field(lambda: Notificacion)
    preferencias_notificacion: list[PreferenciaNotificacionType] = strawchemy.field(lambda: PreferenciaNotificacion)

    # === FINANCIERO ===
    importes_cuota_anio: list[ImporteCuotaAnioType] = strawchemy.field(lambda: ImporteCuotaAnio)
    cuotas_anuales: list[CuotaAnualType] = strawchemy.field(lambda: CuotaAnual)
    donacion_conceptos: list[DonacionConceptoType] = strawchemy.field(lambda: DonacionConcepto)
    donaciones: list[DonacionType] = strawchemy.field(lambda: Donacion)
    remesas: list[RemesaType] = strawchemy.field(lambda: Remesa)
    ordenes_cobro: list[OrdenCobroType] = strawchemy.field(lambda: OrdenCobro)
    estados_planificacion: list[EstadoPlanificacionType] = strawchemy.field(lambda: EstadoPlanificacion)
    categorias_partida: list[CategoriaPartidaType] = strawchemy.field(lambda: CategoriaPartida)
    partidas_presupuestarias: list[PartidaPresupuestariaType] = strawchemy.field(lambda: PartidaPresupuestaria)
    planificaciones_anuales: list[PlanificacionAnualType] = strawchemy.field(lambda: PlanificacionAnual)

    # === COLABORACIONES ===
    tipos_asociacion: list[TipoAsociacionType] = strawchemy.field(lambda: TipoAsociacion)
    asociaciones: list[AsociacionType] = strawchemy.field(lambda: Asociacion)
    estados_convenio: list[EstadoConvenioType] = strawchemy.field(lambda: EstadoConvenio)
    convenios: list[ConvenioType] = strawchemy.field(lambda: Convenio)

    # === MIEMBROS ===
    tipos_miembro: list[TipoMiembroType] = strawchemy.field(lambda: TipoMiembro)
    miembros: list[MiembroType] = strawchemy.field(lambda: Miembro)

    # === CAMPAÑAS ===
    tipos_campania: list[TipoCampaniaType] = strawchemy.field(lambda: TipoCampania)
    campanias: list[CampaniaType] = strawchemy.field(lambda: Campania)
    roles_participante: list[RolParticipanteType] = strawchemy.field(lambda: RolParticipante)
    participantes_campania: list[ParticipanteCampaniaType] = strawchemy.field(lambda: ParticipanteCampania)

    # === ACTIVIDADES ===
    tipos_actividad: list[TipoActividadType] = strawchemy.field(lambda: TipoActividad)
    estados_actividad: list[EstadoActividadType] = strawchemy.field(lambda: EstadoActividad)
    estados_propuesta: list[EstadoPropuestaType] = strawchemy.field(lambda: EstadoPropuesta)
    tipos_recurso: list[TipoRecursoType] = strawchemy.field(lambda: TipoRecurso)
    tipos_kpi: list[TipoKPIType] = strawchemy.field(lambda: TipoKPI)
    propuestas_actividad: list[PropuestaActividadType] = strawchemy.field(lambda: PropuestaActividad)
    tareas_propuesta: list[TareaPropuestaType] = strawchemy.field(lambda: TareaPropuesta)
    recursos_propuesta: list[RecursoPropuestaType] = strawchemy.field(lambda: RecursoPropuesta)
    grupos_propuesta: list[GrupoPropuestaType] = strawchemy.field(lambda: GrupoPropuesta)
    actividades: list[ActividadType] = strawchemy.field(lambda: Actividad)
    tareas_actividad: list[TareaActividadType] = strawchemy.field(lambda: TareaActividad)
    recursos_actividad: list[RecursoActividadType] = strawchemy.field(lambda: RecursoActividad)
    grupos_actividad: list[GrupoActividadType] = strawchemy.field(lambda: GrupoActividad)
    participantes_actividad: list[ParticipanteActividadType] = strawchemy.field(lambda: ParticipanteActividad)
    kpis: list[KPIType] = strawchemy.field(lambda: KPI)
    kpis_actividad: list[KPIActividadType] = strawchemy.field(lambda: KPIActividad)
    mediciones_kpi: list[MedicionKPIType] = strawchemy.field(lambda: MedicionKPI)

    # === GRUPOS ===
    tipos_grupo: list[TipoGrupoType] = strawchemy.field(lambda: TipoGrupo)
    roles_grupo: list[RolGrupoType] = strawchemy.field(lambda: RolGrupo)
    grupos_trabajo: list[GrupoTrabajoType] = strawchemy.field(lambda: GrupoTrabajo)
    miembros_grupo: list[MiembroGrupoType] = strawchemy.field(lambda: MiembroGrupo)
    tareas_grupo: list[TareaGrupoType] = strawchemy.field(lambda: TareaGrupo)
    reuniones_grupo: list[ReunionGrupoType] = strawchemy.field(lambda: ReunionGrupo)
    asistentes_reunion: list[AsistenteReunionType] = strawchemy.field(lambda: AsistenteReunion)

    # === VOLUNTARIADO ===
    categorias_competencia: list[CategoriaCompetenciaType] = strawchemy.field(lambda: CategoriaCompetencia)
    competencias: list[CompetenciaType] = strawchemy.field(lambda: Competencia)
    niveles_competencia: list[NivelCompetenciaType] = strawchemy.field(lambda: NivelCompetencia)
    miembros_competencia: list[MiembroCompetenciaType] = strawchemy.field(lambda: MiembroCompetencia)
    tipos_documento_voluntario: list[TipoDocumentoVoluntarioType] = strawchemy.field(lambda: TipoDocumentoVoluntario)
    documentos_miembro: list[DocumentoMiembroType] = strawchemy.field(lambda: DocumentoMiembro)
    tipos_formacion: list[TipoFormacionType] = strawchemy.field(lambda: TipoFormacion)
    formaciones_miembro: list[FormacionMiembroType] = strawchemy.field(lambda: FormacionMiembro)


# Importar mutations
from .mutations import Mutation


# Schema principal con queries y mutations
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
