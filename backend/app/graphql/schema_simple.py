"""
Schema GraphQL con generación automática de Strawchemy.

Strawchemy genera automáticamente:
- Queries con filtrado, ordenamiento y paginación
- Mutations CRUD (Create, Read, Update, Delete)
- Resolvers optimizados con N+1 prevention
"""

import strawberry

from . import strawchemy
from .auth import AuthQuery
from .types_auto import *  # Importar todos los tipos generados
from .inputs_auto import *  # Importar inputs y filtros


@strawberry.type
class Query(AuthQuery):
    """Queries GraphQL del sistema SIGA con generación automática.

    IMPORTANTE: Todos los nombres usan camelCase para consistencia con GraphQL.
    Strawberry convierte automáticamente los campos de los tipos a camelCase.
    """

    # === ACCESO: roles, transacciones, funcionalidades ===
    roles: list[RolType] = strawchemy.field()
    transacciones: list[TransaccionType] = strawchemy.field()
    rolesTransacciones: list[RolTransaccionType] = strawchemy.field()
    logsAuditoria: list[LogAuditoriaType] = strawchemy.field()
    funcionalidades: list[FuncionalidadType] = strawchemy.field()
    rolesFuncionalidades: list[RolFuncionalidadType] = strawchemy.field()
    funcionalidadesTransacciones: list[FuncionalidadTransaccionType] = strawchemy.field()
    flujos_aprobacion: list[FlujoAprobacionType] = strawchemy.field()

    # === USUARIOS ===
    usuarios: list[UsuarioType] = strawchemy.field()
    usuarioRoles: list[UsuarioRolType] = strawchemy.field()

    # === CORE ===
    configuraciones: list[ConfiguracionType] = strawchemy.field()
    reglasValidacionConfig: list[ReglaValidacionConfigType] = strawchemy.field()
    historialConfiguracion: list[HistorialConfiguracionType] = strawchemy.field()
    estadosCuota: list[EstadoCuotaType] = strawchemy.field()
    estadosCampania: list[EstadoCampaniaType] = strawchemy.field()
    estadosTarea: list[EstadoTareaType] = strawchemy.field()
    estadosParticipante: list[EstadoParticipanteType] = strawchemy.field()
    estadosOrdenCobro: list[EstadoOrdenCobroType] = strawchemy.field()
    estadosRemesa: list[EstadoRemesaType] = strawchemy.field()
    estadosDonacion: list[EstadoDonacionType] = strawchemy.field()
    estadosNotificacion: list[EstadoNotificacionType] = strawchemy.field()
    historialEstado: list[HistorialEstadoType] = strawchemy.field()
    sesiones: list[SesionType] = strawchemy.field()
    historialSeguridad: list[HistorialSeguridadType] = strawchemy.field()
    ipsBloqueadas: list[IPBloqueadaType] = strawchemy.field()
    intentosAcceso: list[IntentoAccesoType] = strawchemy.field()

    # === GEOGRÁFICO ===
    paises: list[PaisType] = strawchemy.field()
    provincias: list[ProvinciaType] = strawchemy.field()
    municipios: list[MunicipioType] = strawchemy.field()
    direcciones: list[DireccionType] = strawchemy.field()
    agrupacionesTerritoriales: list[AgrupacionTerritorialType] = strawchemy.field()

    # === NOTIFICACIONES ===
    tiposNotificacion: list[TipoNotificacionType] = strawchemy.field()
    notificaciones: list[NotificacionType] = strawchemy.field()
    preferenciasNotificacion: list[PreferenciaNotificacionType] = strawchemy.field()

    # === FINANCIERO ===
    importesCuotaAnio: list[ImporteCuotaAnioType] = strawchemy.field()
    cuotasAnuales: list[CuotaAnualType] = strawchemy.field()
    donacionConceptos: list[DonacionConceptoType] = strawchemy.field()
    donaciones: list[DonacionType] = strawchemy.field()
    remesas: list[RemesaType] = strawchemy.field()
    ordenesCobro: list[OrdenCobroType] = strawchemy.field()
    estadosPlanificacion: list[EstadoPlanificacionType] = strawchemy.field()
    categoriasPartida: list[CategoriaPartidaType] = strawchemy.field()
    partidasPresupuestarias: list[PartidaPresupuestariaType] = strawchemy.field()
    planificacionesAnuales: list[PlanificacionAnualType] = strawchemy.field()

    # === COLABORACIONES ===
    tiposAsociacion: list[TipoAsociacionType] = strawchemy.field()
    asociaciones: list[AsociacionType] = strawchemy.field()
    estadosConvenio: list[EstadoConvenioType] = strawchemy.field()
    convenios: list[ConvenioType] = strawchemy.field()

    # === MIEMBROS ===
    tiposMiembro: list[TipoMiembroType] = strawchemy.field()
    estadosMiembro: list[EstadoMiembroType] = strawchemy.field()
    motivosBaja: list[MotivoBajaType] = strawchemy.field()
    tiposCargo: list[TipoCargoType] = strawchemy.field()
    tiposCargoRoles: list[TipoCargoRolType] = strawchemy.field()
    miembros: list[MiembroType] = strawchemy.field(filter_input=MiembroFilter)

    # === JUNTA DIRECTIVA ===
    juntasDirectivas: list[JuntaDirectivaType] = strawchemy.field(filter_input=JuntaDirectivaFilter)
    cargosJunta: list[CargoJuntaType] = strawchemy.field(filter_input=CargoJuntaFilter)
    historialCargosJunta: list[HistorialCargoJuntaType] = strawchemy.field(filter_input=HistorialCargoJuntaFilter)

    # === MILITANCIA ===
    skills: list[SkillType] = strawchemy.field()
    miembrosSkills: list[MiembroSkillType] = strawchemy.field()
    franjasDisponibilidad: list[FranjaDisponibilidadType] = strawchemy.field()
    historialAgrupaciones: list[HistorialAgrupacionType] = strawchemy.field()
    solicitudesTraslado: list[SolicitudTrasladoType] = strawchemy.field()

    # === CAMPAÑAS ===
    tiposCampania: list[TipoCampaniaType] = strawchemy.field(filter_input=TipoCampaniaFilter)
    campanias: list[CampaniaType] = strawchemy.field(filter_input=CampaniaFilter)
    rolesParticipante: list[RolParticipanteType] = strawchemy.field()
    participantesCampania: list[ParticipanteCampaniaType] = strawchemy.field()

    # === ACTIVIDADES ===
    tiposActividad: list[TipoActividadType] = strawchemy.field()
    estadosActividad: list[EstadoActividadType] = strawchemy.field()
    estadosPropuesta: list[EstadoPropuestaType] = strawchemy.field()
    tiposRecurso: list[TipoRecursoType] = strawchemy.field()
    tiposKpi: list[TipoKPIType] = strawchemy.field()
    propuestasActividad: list[PropuestaActividadType] = strawchemy.field()
    tareasPropuesta: list[TareaPropuestaType] = strawchemy.field()
    recursosPropuesta: list[RecursoPropuestaType] = strawchemy.field()
    gruposPropuesta: list[GrupoPropuestaType] = strawchemy.field()
    actividades: list[ActividadType] = strawchemy.field()
    tareasActividad: list[TareaActividadType] = strawchemy.field()
    recursosActividad: list[RecursoActividadType] = strawchemy.field()
    gruposActividad: list[GrupoActividadType] = strawchemy.field()
    participantesActividad: list[ParticipanteActividadType] = strawchemy.field()
    kpis: list[KPIType] = strawchemy.field()
    kpisActividad: list[KPIActividadType] = strawchemy.field()
    medicionesKpi: list[MedicionKPIType] = strawchemy.field()

    # === GRUPOS ===
    tiposGrupo: list[TipoGrupoType] = strawchemy.field()
    rolesGrupo: list[RolGrupoType] = strawchemy.field()
    gruposTrabajo: list[GrupoTrabajoType] = strawchemy.field()
    miembrosGrupo: list[MiembroGrupoType] = strawchemy.field()
    tareasGrupo: list[TareaGrupoType] = strawchemy.field()
    reunionesGrupo: list[ReunionGrupoType] = strawchemy.field()
    asistentesReunion: list[AsistenteReunionType] = strawchemy.field()

    # === EVENTOS ===
    tiposEvento: list[TipoEventoType] = strawchemy.field()
    estadosEvento: list[EstadoEventoType] = strawchemy.field()
    eventos: list[EventoType] = strawchemy.field()
    participantesEvento: list[ParticipanteEventoType] = strawchemy.field()
    materialesEvento: list[MaterialEventoType] = strawchemy.field()

    # === VOLUNTARIADO ===
    categoriasCompetencia: list[CategoriaCompetenciaType] = strawchemy.field()
    competencias: list[CompetenciaType] = strawchemy.field()
    nivelesCompetencia: list[NivelCompetenciaType] = strawchemy.field()
    miembrosCompetencia: list[MiembroCompetenciaType] = strawchemy.field()
    tiposDocumentoVoluntario: list[TipoDocumentoVoluntarioType] = strawchemy.field()
    documentosMiembro: list[DocumentoMiembroType] = strawchemy.field()
    tiposFormacion: list[TipoFormacionType] = strawchemy.field()
    formacionesMiembro: list[FormacionMiembroType] = strawchemy.field()


# Importar mutations
from .mutations import Mutation


# Schema principal con queries y mutations
# Strawberry usa camelCase por defecto para campos de tipos
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
