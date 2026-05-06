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
from .configuracion_resolvers import ConfiguracionOrganizacionQuery
from .types_auto import *  # Importar todos los tipos generados
from .inputs_auto import *  # Importar inputs y filtros


@strawberry.type
class Query(AuthQuery, ConfiguracionOrganizacionQuery):
    """Queries GraphQL del sistema SIGA con generación automática.

    IMPORTANTE: Todos los nombres usan camelCase para consistencia con GraphQL.
    Strawberry convierte automáticamente los campos de los tipos a camelCase.
    """

    # === ACCESO: roles, transacciones, funcionalidades ===
    roles: list[RolType] = strawchemy.field(filter_input=RolFilter)
    transacciones: list[TransaccionType] = strawchemy.field(filter_input=TransaccionFilter)
    rolesTransacciones: list[RolTransaccionType] = strawchemy.field(filter_input=RolTransaccionFilter)
    logsAuditoria: list[LogAuditoriaType] = strawchemy.field()
    funcionalidades: list[FuncionalidadType] = strawchemy.field(filter_input=FuncionalidadFilter)
    rolesFuncionalidades: list[RolFuncionalidadType] = strawchemy.field(filter_input=RolFuncionalidadFilter)
    funcionalidadesTransacciones: list[FuncionalidadTransaccionType] = strawchemy.field(filter_input=FuncionalidadTransaccionFilter)
    flujos_aprobacion: list[FlujoAprobacionType] = strawchemy.field()

    # === USUARIOS ===
    usuarios: list[UsuarioType] = strawchemy.field()
    usuarioRoles: list[UsuarioRolType] = strawchemy.field(filter_input=UsuarioRolFilter)

    # === CORE ===
    configuraciones: list[ConfiguracionType] = strawchemy.field()
    reglasValidacionConfig: list[ReglaValidacionConfigType] = strawchemy.field()
    historialConfiguracion: list[HistorialConfiguracionType] = strawchemy.field()
    estadosCuota: list[EstadoCuotaType] = strawchemy.field(filter_input=EstadoCuotaFilter)
    estadosCampania: list[EstadoCampaniaType] = strawchemy.field(filter_input=EstadoCampaniaFilter)
    estadosTarea: list[EstadoTareaType] = strawchemy.field(filter_input=EstadoTareaFilter)
    estadosParticipante: list[EstadoParticipanteType] = strawchemy.field(filter_input=EstadoParticipanteFilter)
    estadosOrdenCobro: list[EstadoOrdenCobroType] = strawchemy.field(filter_input=EstadoOrdenCobroFilter)
    estadosRemesa: list[EstadoRemesaType] = strawchemy.field(filter_input=EstadoRemesaFilter)
    estadosDonacion: list[EstadoDonacionType] = strawchemy.field(filter_input=EstadoDonacionFilter)
    estadosNotificacion: list[EstadoNotificacionType] = strawchemy.field(filter_input=EstadoNotificacionFilter)
    historialEstado: list[HistorialEstadoType] = strawchemy.field()
    sesiones: list[SesionType] = strawchemy.field()
    historialSeguridad: list[HistorialSeguridadType] = strawchemy.field()
    ipsBloqueadas: list[IPBloqueadaType] = strawchemy.field()
    intentosAcceso: list[IntentoAccesoType] = strawchemy.field()

    # === GEOGRÁFICO ===
    paises: list[PaisType] = strawchemy.field(filter_input=PaisFilter)
    provincias: list[ProvinciaType] = strawchemy.field(filter_input=ProvinciaFilter)
    municipios: list[MunicipioType] = strawchemy.field(filter_input=MunicipioFilter)
    direcciones: list[DireccionType] = strawchemy.field()
    agrupacionesTerritoriales: list[AgrupacionTerritorialType] = strawchemy.field(filter_input=AgrupacionTerritorialFilter)

    # === NOTIFICACIONES ===
    tiposNotificacion: list[TipoNotificacionType] = strawchemy.field(filter_input=TipoNotificacionFilter)
    notificaciones: list[NotificacionType] = strawchemy.field(filter_input=NotificacionFilter)
    preferenciasNotificacion: list[PreferenciaNotificacionType] = strawchemy.field(filter_input=PreferenciaNotificacionFilter)

    # === FINANCIERO ===
    importesCuotaAnio: list[ImporteCuotaAnioType] = strawchemy.field(filter_input=ImporteCuotaAnioFilter)
    formasPago: list[FormaPagoType] = strawchemy.field(filter_input=FormaPagoFilter)
    cuotasAnuales: list[CuotaAnualType] = strawchemy.field(filter_input=CuotaAnualFilter)
    donacionConceptos: list[DonacionConceptoType] = strawchemy.field(filter_input=DonacionConceptoFilter)
    donaciones: list[DonacionType] = strawchemy.field(filter_input=DonacionFilter)
    remesas: list[RemesaType] = strawchemy.field(filter_input=RemesaFilter)
    ordenesCobro: list[OrdenCobroType] = strawchemy.field(filter_input=OrdenCobroFilter)
    estadosPlanificacion: list[EstadoPlanificacionType] = strawchemy.field()
    categoriasPartida: list[CategoriaPartidaType] = strawchemy.field()
    partidasPresupuestarias: list[PartidaPresupuestariaType] = strawchemy.field()
    planificacionesAnuales: list[PlanificacionAnualType] = strawchemy.field()

    # === COLABORACIONES ===
    tiposOrganizacion: list[TipoOrganizacionType] = strawchemy.field(filter_input=TipoOrganizacionFilter)
    organizaciones: list[OrganizacionType] = strawchemy.field(filter_input=OrganizacionFilter)
    estadosConvenio: list[EstadoConvenioType] = strawchemy.field(filter_input=EstadoConvenioFilter)
    convenios: list[ConvenioType] = strawchemy.field(filter_input=ConvenioFilter)

    # === MIEMBROS ===
    tiposMiembro: list[TipoMiembroType] = strawchemy.field(filter_input=TipoMiembroFilter)
    estadosMiembro: list[EstadoMiembroType] = strawchemy.field(filter_input=EstadoMiembroFilter)
    motivosBaja: list[MotivoBajaType] = strawchemy.field(filter_input=MotivoBajaFilter)
    tiposCargo: list[TipoCargoType] = strawchemy.field()
    tiposCargoRoles: list[TipoCargoRolType] = strawchemy.field()
    miembros: list[MiembroType] = strawchemy.field(filter_input=MiembroFilter)

    # === JUNTA DIRECTIVA ===
    juntasDirectivas: list[JuntaDirectivaType] = strawchemy.field(filter_input=JuntaDirectivaFilter)
    cargosJunta: list[CargoJuntaType] = strawchemy.field(filter_input=CargoJuntaFilter)
    historialCargosJunta: list[HistorialCargoJuntaType] = strawchemy.field(filter_input=HistorialCargoJuntaFilter)

    # === MILITANCIA ===
    skills: list[SkillType] = strawchemy.field(filter_input=SkillFilter)
    miembrosSkills: list[MiembroSkillType] = strawchemy.field(filter_input=MiembroSkillFilter)
    franjasDisponibilidad: list[FranjaDisponibilidadType] = strawchemy.field(filter_input=FranjaDisponibilidadFilter)
    historialAgrupaciones: list[HistorialAgrupacionType] = strawchemy.field(filter_input=HistorialAgrupacionFilter)
    solicitudesTraslado: list[SolicitudTrasladoType] = strawchemy.field(filter_input=SolicitudTrasladoFilter)

    # === CAMPAÑAS ===
    tiposCampania: list[TipoCampaniaType] = strawchemy.field(filter_input=TipoCampaniaFilter)
    campanias: list[CampaniaType] = strawchemy.field(filter_input=CampaniaFilter)
    rolesParticipante: list[RolParticipanteType] = strawchemy.field(filter_input=RolParticipanteFilter)
    participantesCampania: list[ParticipanteCampaniaType] = strawchemy.field(filter_input=ParticipanteCampaniaFilter)

    # === ACTIVIDADES ===
    tiposActividad: list[TipoActividadType] = strawchemy.field(filter_input=TipoActividadFilter)
    estadosActividad: list[EstadoActividadType] = strawchemy.field(filter_input=EstadoActividadFilter)
    estadosPropuesta: list[EstadoPropuestaType] = strawchemy.field(filter_input=EstadoPropuestaFilter)
    tiposRecurso: list[TipoRecursoType] = strawchemy.field(filter_input=TipoRecursoFilter)
    tiposKpi: list[TipoKPIType] = strawchemy.field(filter_input=TipoKPIFilter)
    propuestasActividad: list[PropuestaActividadType] = strawchemy.field(filter_input=PropuestaActividadFilter)
    tareasPropuesta: list[TareaPropuestaType] = strawchemy.field()
    recursosPropuesta: list[RecursoPropuestaType] = strawchemy.field()
    gruposPropuesta: list[GrupoPropuestaType] = strawchemy.field()
    actividades: list[ActividadType] = strawchemy.field(filter_input=ActividadFilter)
    tareasActividad: list[TareaActividadType] = strawchemy.field(filter_input=TareaActividadFilter)
    recursosActividad: list[RecursoActividadType] = strawchemy.field()
    gruposActividad: list[GrupoActividadType] = strawchemy.field()
    participantesActividad: list[ParticipanteActividadType] = strawchemy.field()
    kpis: list[KPIType] = strawchemy.field()
    kpisActividad: list[KPIActividadType] = strawchemy.field()
    medicionesKpi: list[MedicionKPIType] = strawchemy.field()

    # === GRUPOS ===
    tiposGrupo: list[TipoGrupoType] = strawchemy.field(filter_input=TipoGrupoFilter)
    rolesGrupo: list[RolGrupoType] = strawchemy.field(filter_input=RolGrupoFilter)
    gruposTrabajo: list[GrupoTrabajoType] = strawchemy.field(filter_input=GrupoTrabajoFilter)
    miembrosGrupo: list[MiembroGrupoType] = strawchemy.field(filter_input=MiembroGrupoFilter)
    tareasGrupo: list[TareaGrupoType] = strawchemy.field(filter_input=TareaGrupoFilter)
    reunionesGrupo: list[ReunionGrupoType] = strawchemy.field()
    asistentesReunion: list[AsistenteReunionType] = strawchemy.field()

    # === EVENTOS ===
    tiposEvento: list[TipoEventoType] = strawchemy.field()
    estadosEvento: list[EstadoEventoType] = strawchemy.field()
    eventos: list[EventoType] = strawchemy.field()
    participantesEvento: list[ParticipanteEventoType] = strawchemy.field()
    materialesEvento: list[MaterialEventoType] = strawchemy.field()

    # === VOLUNTARIADO ===
    categoriasCompetencia: list[CategoriaCompetenciaType] = strawchemy.field(filter_input=CategoriaCompetenciaFilter)
    competencias: list[CompetenciaType] = strawchemy.field(filter_input=CompetenciaFilter)
    nivelesCompetencia: list[NivelCompetenciaType] = strawchemy.field(filter_input=NivelCompetenciaFilter)
    miembrosCompetencia: list[MiembroCompetenciaType] = strawchemy.field(filter_input=MiembroCompetenciaFilter)
    tiposDocumentoVoluntario: list[TipoDocumentoVoluntarioType] = strawchemy.field(filter_input=TipoDocumentoVoluntarioFilter)
    documentosMiembro: list[DocumentoMiembroType] = strawchemy.field(filter_input=DocumentoMiembroFilter)
    tiposFormacion: list[TipoFormacionType] = strawchemy.field(filter_input=TipoFormacionFilter)
    formacionesMiembro: list[FormacionMiembroType] = strawchemy.field(filter_input=FormacionMiembroFilter)


# Importar mutations
from .mutations import Mutation


# Schema principal con queries y mutations
# Strawberry usa camelCase por defecto para campos de tipos
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
