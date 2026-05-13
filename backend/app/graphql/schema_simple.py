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
from .financiero_resolvers import FinancieroQuery
from .types_auto import *  # Importar todos los tipos generados
from .inputs_auto import *  # Importar inputs y filtros


@strawberry.type
class Query(AuthQuery, ConfiguracionOrganizacionQuery, FinancieroQuery):
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
    tipos_vinculacion: list[TipoVinculacionType] = strawchemy.field()
    usuarios: list[UsuarioType] = strawchemy.field()
    usuarioRoles: list[UsuarioRolType] = strawchemy.field(filter_input=UsuarioRolFilter)

    # === CORE ===
    configuraciones: list[ConfiguracionType] = strawchemy.field()
    reglasValidacionConfig: list[ReglaValidacionConfigType] = strawchemy.field()
    historialConfiguracion: list[HistorialConfiguracionType] = strawchemy.field()
    estadosCuota: list[EstadoCuotaType] = strawchemy.field(filter_input=EstadoCuotaFilter)
    estadosCampania: list[EstadoCampaniaType] = strawchemy.field(filter_input=EstadoCampaniaFilter)
    estadosAccion: list[EstadoAccionType] = strawchemy.field(filter_input=EstadoAccionFilter)
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

    # === TEMAS UI ===
    temasUi: list[TemaUIType] = strawchemy.field()

    # === GEOGRÁFICO ===
    tiposUnidadesOrganizativas: list[TipoUnidadOrganizativaType] = strawchemy.field(filter_input=TipoUnidadOrganizativaFilter)
    paises: list[PaisType] = strawchemy.field(filter_input=PaisFilter)
    provincias: list[ProvinciaType] = strawchemy.field(filter_input=ProvinciaFilter)
    municipios: list[MunicipioType] = strawchemy.field(filter_input=MunicipioFilter)
    direcciones: list[DireccionType] = strawchemy.field()
    agrupacionesTerritoriales: list[AgrupacionTerritorialType] = strawchemy.field(filter_input=AgrupacionTerritorialFilter)

    # === NOTIFICACIONES ===
    tiposNotificacion: list[TipoNotificacionType] = strawchemy.field(filter_input=TipoNotificacionFilter)
    notificaciones: list[NotificacionType] = strawchemy.field(filter_input=NotificacionFilter)
    preferenciasNotificacion: list[PreferenciaNotificacionType] = strawchemy.field(filter_input=PreferenciaNotificacionFilter)

    # === FINANCIERO - Tesorería ===
    cuentasBancarias: list[CuentaBancariaType] = strawchemy.field(filter_input=CuentaBancariaFilter)
    movimientosTesoreria: list[MovimientoTesoreriaType] = strawchemy.field(filter_input=MovimientoTesoreriaFilter)
    conciliacionesBancarias: list[ConciliacionBancariaType] = strawchemy.field(filter_input=ConciliacionBancariaFilter)

    # === FINANCIERO - Contabilidad ===
    cuentasContables: list[CuentaContableType] = strawchemy.field(filter_input=CuentaContableFilter)
    asientosContables: list[AsientoContableType] = strawchemy.field(filter_input=AsientoContableFilter)
    apuntesContables: list[ApunteContableType] = strawchemy.field(filter_input=ApunteContableFilter)
    balancesContables: list[BalanceContableType] = strawchemy.field()

    # === FINANCIERO - Cuotas/Donaciones/Presupuesto ===
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
    miembros: list[MiembroType] = strawchemy.field(filter_input=MiembroFilter)

    # === JUNTA DIRECTIVA ===
    juntasDirectivas: list[JuntaDirectivaType] = strawchemy.field(filter_input=JuntaDirectivaFilter)

    # === COORDINACIONES TERRITORIALES ===
    coordinacionesTerritoriales: list[CoordinacionTerritorialType] = strawchemy.field(filter_input=CoordinacionTerritorialFilter)

    # === NOMBRAMIENTOS ===
    historialNombramientos: list[HistorialNombramientoType] = strawchemy.field(filter_input=HistorialNombramientoFilter)

    # === MILITANCIA ===
    niveles_estudios: list[NivelEstudiosType] = strawchemy.field(filter_input=NivelEstudiosFilter)
    niveles_habilidad: list[NivelHabilidadType] = strawchemy.field(filter_input=NivelHabilidadFilter)
    categorias_habilidad: list[CategoriaHabilidadType] = strawchemy.field(filter_input=CategoriaHabilidadFilter)
    habilidades: list[HabilidadType] = strawchemy.field(filter_input=HabilidadFilter)
    miembrosHabilidades: list[MiembroHabilidadType] = strawchemy.field(filter_input=MiembroHabilidadFilter)
    franjasDisponibilidad: list[FranjaDisponibilidadType] = strawchemy.field(filter_input=FranjaDisponibilidadFilter)
    historialAgrupaciones: list[HistorialAgrupacionType] = strawchemy.field(filter_input=HistorialAgrupacionFilter)
    solicitudesTraslado: list[SolicitudTrasladoType] = strawchemy.field(filter_input=SolicitudTrasladoFilter)

    # === CAMPAÑAS ===
    tiposCampania: list[TipoCampaniaType] = strawchemy.field(filter_input=TipoCampaniaFilter)
    campanias: list[CampaniaType] = strawchemy.field(filter_input=CampaniaFilter)
    rolesParticipante: list[RolParticipanteType] = strawchemy.field(filter_input=RolParticipanteFilter)
    participantesCampania: list[ParticipanteCampaniaType] = strawchemy.field(filter_input=ParticipanteCampaniaFilter)

    # === ACCIONES (unifica Evento + Actividad) ===
    tiposAccion: list[TipoAccionType] = strawchemy.field(filter_input=TipoAccionFilter)
    acciones: list[AccionType] = strawchemy.field(filter_input=AccionFilter)
    tareas: list[TareaType] = strawchemy.field(filter_input=TareaFilter)
    participaciones: list[ParticipacionType] = strawchemy.field(filter_input=ParticipacionFilter)

    # === GRUPOS ===
    tiposGrupo: list[TipoGrupoType] = strawchemy.field(filter_input=TipoGrupoFilter)
    rolesGrupo: list[RolGrupoType] = strawchemy.field(filter_input=RolGrupoFilter)
    gruposTrabajo: list[GrupoTrabajoType] = strawchemy.field(filter_input=GrupoTrabajoFilter)
    miembrosGrupo: list[MiembroGrupoType] = strawchemy.field(filter_input=MiembroGrupoFilter)
    gruposIniciativa: list[GrupoIniciativaType] = strawchemy.field(filter_input=GrupoIniciativaFilter)
    reunionesGrupo: list[ReunionGrupoType] = strawchemy.field()
    asistentesReunion: list[AsistenteReunionType] = strawchemy.field()

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
