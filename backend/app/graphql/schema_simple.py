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
from .economico_resolvers import EconomicoQuery
from .categoria_fiscal_resolvers import CategoriaFiscalQuery
from .categorizacion_resolvers import CategorizacionQuery
from .presupuesto_resolvers import PresupuestoQuery
from .secretaria_resolvers import SecretariaQuery, SecretariaResolverMutation
from .comunicacion_resolvers import ComunicacionQuery
from .chat_resolvers import ChatQuery
from .membresia_resolvers import MembresiaQuery
from .socios_resolvers import SociosQuery
from .vinculaciones_resolvers import VinculacionesQuery
from .types_auto import *  # Importar todos los tipos generados
from .inputs_auto import *  # Importar inputs y filtros


@strawberry.type
class Query(AuthQuery, ConfiguracionOrganizacionQuery, EconomicoQuery, CategoriaFiscalQuery, CategorizacionQuery, PresupuestoQuery, SecretariaQuery, ComunicacionQuery, ChatQuery, MembresiaQuery, SociosQuery, VinculacionesQuery):
    """Queries GraphQL del sistema SIGA con generación automática.

    IMPORTANTE: Todos los nombres usan camelCase para consistencia con GraphQL.
    Strawberry convierte automáticamente los campos de los tipos a camelCase.
    """

    # === ACCESO: roles, transacciones, funcionalidades, cargos ===
    roles: list[RolType] = strawchemy.field(filter_input=RolFilter)
    cargos: list[CargoType] = strawchemy.field(filter_input=CargoFilter)
    cargos_roles: list[CargoRolType] = strawchemy.field(filter_input=CargoRolFilter)
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
    estadosActividad: list[EstadoAccionType] = strawchemy.field(filter_input=EstadoAccionFilter)
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
    ambitosGeograficos: list[AmbitoGeograficoType] = strawchemy.field(filter_input=AmbitoGeograficoFilter)
    nivelesOrganizativos: list[NivelOrganizativoType] = strawchemy.field(filter_input=NivelOrganizativoFilter)
    paises: list[PaisType] = strawchemy.field(filter_input=PaisFilter)
    provincias: list[ProvinciaType] = strawchemy.field(filter_input=ProvinciaFilter)
    municipios: list[MunicipioType] = strawchemy.field(filter_input=MunicipioFilter)
    direcciones: list[DireccionType] = strawchemy.field()
    unidadesOrganizativas: list[UnidadOrganizativaType] = strawchemy.field(filter_input=UnidadOrganizativaFilter)

    # === NOTIFICACIONES ===
    tiposNotificacion: list[TipoNotificacionType] = strawchemy.field(filter_input=TipoNotificacionFilter)
    notificaciones: list[NotificacionType] = strawchemy.field(filter_input=NotificacionFilter)
    preferenciasNotificacion: list[PreferenciaNotificacionType] = strawchemy.field(filter_input=PreferenciaNotificacionFilter)
    plantillasEmail: list[PlantillaEmailType] = strawchemy.field(filter_input=PlantillaEmailFilter)

    # === FINANCIERO - Tesorería ===
    cuentasBancarias: list[CuentaBancariaType] = strawchemy.field(filter_input=CuentaBancariaFilter)
    apuntesCaja: list[ApunteCajaType] = strawchemy.field(filter_input=ApunteCajaFilter)
    extractosBancarios: list[ExtractoBancarioType] = strawchemy.field(filter_input=ExtractoBancarioFilter)
    movimientosTesoreria: list[MovimientoTesoreriaType] = strawchemy.field(filter_input=MovimientoTesoreriaFilter)
    conciliacionesBancarias: list[ConciliacionBancariaType] = strawchemy.field(filter_input=ConciliacionBancariaFilter)

    # === FINANCIERO - Contabilidad ===
    cuentasContables: list[CuentaContableType] = strawchemy.field(filter_input=CuentaContableFilter)
    asientosContables: list[AsientoContableType] = strawchemy.field(filter_input=AsientoContableFilter)
    apuntesContables: list[ApunteContableType] = strawchemy.field(filter_input=ApunteContableFilter)
    reglasContables: list[ReglaContableType] = strawchemy.field(filter_input=ReglaContableFilter)

    # === FINANCIERO - Cuotas/Donaciones/Presupuesto ===
    importesCuotaAnio: list[ImporteCuotaAnioType] = strawchemy.field(filter_input=ImporteCuotaAnioFilter)
    formasPago: list[FormaPagoType] = strawchemy.field(filter_input=FormaPagoFilter)
    cuotasAnuales: list[CuotaAnualType] = strawchemy.field(filter_input=CuotaAnualFilter)
    # Flujo 1 — catálogo de motivos de reducción
    motivosReduccionCuota: list[MotivoReduccionCuotaType] = strawchemy.field(filter_input=MotivoReduccionCuotaFilter)
    donacionConceptos: list[DonacionConceptoType] = strawchemy.field(filter_input=DonacionConceptoFilter)
    donaciones: list[DonacionType] = strawchemy.field(filter_input=DonacionFilter)
    remesas: list[RemesaType] = strawchemy.field(filter_input=RemesaFilter)
    ordenesCobro: list[OrdenCobroType] = strawchemy.field(filter_input=OrdenCobroFilter)
    recibos: list[ReciboType] = strawchemy.field(filter_input=ReciboFilter)
    justificantesGasto: list[JustificanteGastoType] = strawchemy.field(filter_input=JustificanteGastoFilter)
    solicitudesReduccionCuota: list[SolicitudReduccionCuotaType] = strawchemy.field(filter_input=SolicitudReduccionCuotaFilter)
    estadosPlanificacion: list[EstadoPlanificacionType] = strawchemy.field()
    categoriasPartida: list[CategoriaPartidaType] = strawchemy.field()
    # `partidasPresupuestarias` lo sirve el resolver de PresupuestoQuery (filtra por
    # planificacionId y tipo); no se declara aquí para no tapar ese resolver.
    compromisos_presupuestarios: list[CompromisoPresupuestarioType] = strawchemy.field(filter_input=CompromisoPresupuestarioFilter)
    planificacionesAnuales: list[PlanificacionAnualType] = strawchemy.field()

    # === COLABORACIONES ===
    # Módulo `organizaciones` obsoleto; los convenios de secretaría se consultan
    # vía SecretariaQuery (resolvers propios).

    # === MIEMBROS ===
    tiposMiembro: list[TipoMiembroType] = strawchemy.field(filter_input=TipoMiembroFilter)
    estadosMiembro: list[EstadoMiembroType] = strawchemy.field(filter_input=EstadoMiembroFilter)
    motivosBaja: list[MotivoBajaType] = strawchemy.field(filter_input=MotivoBajaFilter)
    contactos: list[ContactoType] = strawchemy.field(filter_input=ContactoFilter)

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
    # rolesParticipante / participantesCampania disueltos en Contacto + Participacion + Vinculacion.
    tiposMetaCampania: list[TipoMetaType] = strawchemy.field(filter_input=TipoMetaFilter)
    tiposCanalDifusion: list[TipoCanalDifusionType] = strawchemy.field(filter_input=TipoCanalDifusionFilter)
    plantillasCampania: list[PlantillaCampaniaType] = strawchemy.field(filter_input=PlantillaCampaniaFilter)

    # === ACTIVIDADES ===
    tiposActividad: list[TipoActividadType] = strawchemy.field(filter_input=TipoActividadFilter)
    actividades: list[ActividadType] = strawchemy.field(filter_input=ActividadFilter)
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
    requisitosRecurso: list[RequisitoRecursoType] = strawchemy.field(filter_input=RequisitoRecursoFilter)
    aportacionesHoras: list[AportacionHorasType] = strawchemy.field(filter_input=AportacionHorasFilter)

    # === VOLUNTARIADO ===
    categoriasCompetencia: list[CategoriaCompetenciaType] = strawchemy.field(filter_input=CategoriaCompetenciaFilter)
    competencias: list[CompetenciaType] = strawchemy.field(filter_input=CompetenciaFilter)
    nivelesCompetencia: list[NivelCompetenciaType] = strawchemy.field(filter_input=NivelCompetenciaFilter)
    miembrosCompetencia: list[MiembroCompetenciaType] = strawchemy.field(filter_input=MiembroCompetenciaFilter)
    tiposDocumentoVoluntario: list[TipoDocumentoVoluntarioType] = strawchemy.field(filter_input=TipoDocumentoVoluntarioFilter)
    documentosMiembro: list[DocumentoMiembroType] = strawchemy.field(filter_input=DocumentoMiembroFilter)
    tiposFormacion: list[TipoFormacionType] = strawchemy.field(filter_input=TipoFormacionFilter)
    formacionesMiembro: list[FormacionMiembroType] = strawchemy.field(filter_input=FormacionMiembroFilter)

    # === SECRETARÍA — PLATAFORMAS TELEMÁTICAS ===
    plataformasTelematicas: list[PlataformaTelematicaType] = strawchemy.field(filter_input=PlataformaTelematicaFilter)

    # === PROTECCIÓN DE DATOS (RGPD) ===
    rgpdEncargados: list[EncargadoTratamientoType] = strawchemy.field(filter_input=EncargadoTratamientoFilter)
    rgpdActividadesTratamiento: list[ActividadTratamientoType] = strawchemy.field(filter_input=ActividadTratamientoFilter)
    rgpdActividadesEncargados: list[ActividadTratamientoEncargadoType] = strawchemy.field(filter_input=ActividadTratamientoEncargadoFilter)
    rgpdClausulas: list[ClausulaInformativaType] = strawchemy.field(filter_input=ClausulaInformativaFilter)
    rgpdConsentimientos: list[ConsentimientoType] = strawchemy.field(filter_input=ConsentimientoFilter)
    rgpdSolicitudesDerechos: list[SolicitudDerechoRGPDType] = strawchemy.field(filter_input=SolicitudDerechoRGPDFilter)
    rgpdBrechasSeguridad: list[BrechaSeguridadType] = strawchemy.field(filter_input=BrechaSeguridadFilter)
    rgpdAuditoriaAccesos: list[AuditoriaAccesoDatosType] = strawchemy.field(filter_input=AuditoriaAccesoDatosFilter)


# Importar mutations
from .mutations import Mutation


# Schema principal con queries y mutations
# Strawberry usa camelCase por defecto para campos de tipos
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
