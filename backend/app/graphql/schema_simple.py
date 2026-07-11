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
from .permissions import RequireTransaction, campo
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
    roles: list[RolType] = campo(filter_input=RolFilter)
    cargos: list[CargoType] = campo(filter_input=CargoFilter)
    cargos_roles: list[CargoRolType] = campo(filter_input=CargoRolFilter)
    tipos_organo: list[TipoOrganoType] = campo(filter_input=TipoOrganoFilter)
    tipos_organo_cargos: list[TipoOrganoCargoType] = campo(filter_input=TipoOrganoCargoFilter)
    organos: list[OrganoType] = campo(filter_input=OrganoFilter)
    transacciones: list[TransaccionType] = campo(filter_input=TransaccionFilter)
    rolesTransacciones: list[RolTransaccionType] = campo(filter_input=RolTransaccionFilter)
    logsAuditoria: list[LogAuditoriaType] = campo()
    funcionalidades: list[FuncionalidadType] = campo(filter_input=FuncionalidadFilter)
    rolesFuncionalidades: list[RolFuncionalidadType] = campo(filter_input=RolFuncionalidadFilter)
    funcionalidadesTransacciones: list[FuncionalidadTransaccionType] = campo(filter_input=FuncionalidadTransaccionFilter)
    flujos_aprobacion: list[FlujoAprobacionType] = campo()

    # === USUARIOS ===
    tipos_vinculacion: list[TipoVinculacionType] = campo()
    usuarios: list[UsuarioType] = campo()
    usuarioRoles: list[UsuarioRolType] = campo(filter_input=UsuarioRolFilter)

    # === CORE ===
    configuraciones: list[ConfiguracionType] = campo()
    reglasValidacionConfig: list[ReglaValidacionConfigType] = campo()
    historialConfiguracion: list[HistorialConfiguracionType] = campo()
    estadosCuota: list[EstadoCuotaType] = campo(filter_input=EstadoCuotaFilter)
    estadosCampania: list[EstadoCampaniaType] = campo(filter_input=EstadoCampaniaFilter)
    estadosAccion: list[EstadoAccionType] = campo(filter_input=EstadoAccionFilter)
    estadosActividad: list[EstadoAccionType] = campo(filter_input=EstadoAccionFilter)
    estadosTarea: list[EstadoTareaType] = campo(filter_input=EstadoTareaFilter)
    estadosParticipante: list[EstadoParticipanteType] = campo(filter_input=EstadoParticipanteFilter)
    estadosOrdenCobro: list[EstadoOrdenCobroType] = campo(filter_input=EstadoOrdenCobroFilter)
    estadosRemesa: list[EstadoRemesaType] = campo(filter_input=EstadoRemesaFilter)
    estadosDonacion: list[EstadoDonacionType] = campo(filter_input=EstadoDonacionFilter)
    estadosNotificacion: list[EstadoNotificacionType] = campo(filter_input=EstadoNotificacionFilter)
    historialEstado: list[HistorialEstadoType] = campo()
    sesiones: list[SesionType] = campo()
    historialSeguridad: list[HistorialSeguridadType] = campo()
    ipsBloqueadas: list[IPBloqueadaType] = campo()
    intentosAcceso: list[IntentoAccesoType] = campo()

    # === TEMAS UI ===
    temasUi: list[TemaUIType] = campo()

    # === GEOGRÁFICO ===
    ambitosGeograficos: list[AmbitoGeograficoType] = campo(filter_input=AmbitoGeograficoFilter)
    nivelesOrganizativos: list[NivelOrganizativoType] = campo(filter_input=NivelOrganizativoFilter)
    paises: list[PaisType] = campo(filter_input=PaisFilter)
    provincias: list[ProvinciaType] = campo(filter_input=ProvinciaFilter)
    municipios: list[MunicipioType] = campo(filter_input=MunicipioFilter)
    entidades_geograficas: list[EntidadGeograficaType] = campo(filter_input=EntidadGeograficaFilter)
    direcciones: list[DireccionType] = campo()
    unidadesOrganizativas: list[UnidadOrganizativaType] = campo(filter_input=UnidadOrganizativaFilter)

    # === NOTIFICACIONES ===
    tiposNotificacion: list[TipoNotificacionType] = campo(filter_input=TipoNotificacionFilter)
    notificaciones: list[NotificacionType] = campo(filter_input=NotificacionFilter)
    preferenciasNotificacion: list[PreferenciaNotificacionType] = campo(filter_input=PreferenciaNotificacionFilter)
    plantillasEmail: list[PlantillaEmailType] = campo(filter_input=PlantillaEmailFilter)

    # === FINANCIERO - Tesorería ===
    cuentasBancarias: list[CuentaBancariaType] = campo(permission_classes=[RequireTransaction("ECO_CUENTA_LISTAR")], filter_input=CuentaBancariaFilter)
    apuntesCaja: list[ApunteCajaType] = campo(permission_classes=[RequireTransaction("ECO_CONCILIACION_LISTAR")], filter_input=ApunteCajaFilter)
    extractosBancarios: list[ExtractoBancarioType] = campo(permission_classes=[RequireTransaction("ECO_CONCILIACION_LISTAR")], filter_input=ExtractoBancarioFilter)
    movimientosTesoreria: list[MovimientoTesoreriaType] = campo(permission_classes=[RequireTransaction("ECO_CONCILIACION_LISTAR")], filter_input=MovimientoTesoreriaFilter)
    conciliacionesBancarias: list[ConciliacionBancariaType] = campo(permission_classes=[RequireTransaction("ECO_CONCILIACION_LISTAR")], filter_input=ConciliacionBancariaFilter)

    # === FINANCIERO - Contabilidad ===
    cuentasContables: list[CuentaContableType] = campo(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")], filter_input=CuentaContableFilter)
    asientosContables: list[AsientoContableType] = campo(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")], filter_input=AsientoContableFilter)
    apuntesContables: list[ApunteContableType] = campo(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")], filter_input=ApunteContableFilter)
    reglasContables: list[ReglaContableType] = campo(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")], filter_input=ReglaContableFilter)

    # === FINANCIERO - Cuotas/Donaciones/Presupuesto ===
    importesCuotaAnio: list[ImporteCuotaAnioType] = campo(filter_input=ImporteCuotaAnioFilter)
    formasPago: list[FormaPagoType] = campo(filter_input=FormaPagoFilter)
    cuotasAnuales: list[CuotaAnualType] = campo(permission_classes=[RequireTransaction("ECO_CUOTA_LISTAR")], filter_input=CuotaAnualFilter)
    # Flujo 1 — catálogo de motivos de reducción
    motivosReduccionCuota: list[MotivoReduccionCuotaType] = campo(filter_input=MotivoReduccionCuotaFilter)
    donacionConceptos: list[DonacionConceptoType] = campo(filter_input=DonacionConceptoFilter)
    donaciones: list[DonacionType] = campo(permission_classes=[RequireTransaction("ECO_DONACION_LISTAR")], filter_input=DonacionFilter)
    remesas: list[RemesaType] = campo(permission_classes=[RequireTransaction("ECO_REMESA_LISTAR")], filter_input=RemesaFilter)
    ordenesCobro: list[OrdenCobroType] = campo(permission_classes=[RequireTransaction("ECO_REMESA_LISTAR")], filter_input=OrdenCobroFilter)
    recibos: list[ReciboType] = campo(permission_classes=[RequireTransaction("ECO_RECIBO_LISTAR")], filter_input=ReciboFilter)
    justificantesGasto: list[JustificanteGastoType] = campo(permission_classes=[RequireTransaction("ECO_JUSTIFICANTE_LISTAR")], filter_input=JustificanteGastoFilter)
    solicitudesReduccionCuota: list[SolicitudReduccionCuotaType] = campo(permission_classes=[RequireTransaction("ECO_CUOTA_LISTAR")], filter_input=SolicitudReduccionCuotaFilter)
    estadosPlanificacion: list[EstadoPlanificacionType] = campo()
    categoriasPartida: list[CategoriaPartidaType] = campo()
    # `partidasPresupuestarias` lo sirve el resolver de PresupuestoQuery (filtra por
    # planificacionId y tipo); no se declara aquí para no tapar ese resolver.
    compromisos_presupuestarios: list[CompromisoPresupuestarioType] = campo(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")], filter_input=CompromisoPresupuestarioFilter)
    planificacionesAnuales: list[PlanificacionAnualType] = campo(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")], )

    # === COLABORACIONES ===
    # Módulo `organizaciones` obsoleto; los convenios de secretaría se consultan
    # vía SecretariaQuery (resolvers propios).

    # === MIEMBROS ===
    tiposMiembro: list[TipoMiembroType] = campo(filter_input=TipoMiembroFilter)
    estadosMiembro: list[EstadoMiembroType] = campo(filter_input=EstadoMiembroFilter)
    motivosBaja: list[MotivoBajaType] = campo(filter_input=MotivoBajaFilter)
    motivosTraslado: list[MotivoTrasladoType] = campo(filter_input=MotivoTrasladoFilter)
    estadosTraslado: list[EstadoTrasladoCatalogoType] = campo(filter_input=EstadoTrasladoCatalogoFilter)
    contactos: list[ContactoType] = campo(filter_input=ContactoFilter)

    # === COORDINACIONES TERRITORIALES ===
    coordinacionesTerritoriales: list[CoordinacionTerritorialType] = campo(filter_input=CoordinacionTerritorialFilter)

    # === NOMBRAMIENTOS ===
    historialNombramientos: list[HistorialNombramientoType] = campo(filter_input=HistorialNombramientoFilter)

    # === MILITANCIA ===
    niveles_estudios: list[NivelEstudiosType] = campo(filter_input=NivelEstudiosFilter)
    niveles_habilidad: list[NivelHabilidadType] = campo(filter_input=NivelHabilidadFilter)
    categorias_habilidad: list[CategoriaHabilidadType] = campo(filter_input=CategoriaHabilidadFilter)
    habilidades: list[HabilidadType] = campo(filter_input=HabilidadFilter)
    miembrosHabilidades: list[MiembroHabilidadType] = campo(filter_input=MiembroHabilidadFilter)
    franjasDisponibilidad: list[FranjaDisponibilidadType] = campo(filter_input=FranjaDisponibilidadFilter)
    historialAgrupaciones: list[HistorialAgrupacionType] = campo(filter_input=HistorialAgrupacionFilter)
    solicitudesTraslado: list[SolicitudTrasladoType] = campo(filter_input=SolicitudTrasladoFilter)

    # === CAMPAÑAS ===
    tiposCampania: list[TipoCampaniaType] = campo(filter_input=TipoCampaniaFilter)
    campanias: list[CampaniaType] = campo(filter_input=CampaniaFilter)
    # rolesParticipante / participantesCampania disueltos en Contacto + Participacion + Vinculacion.
    tiposMetaCampania: list[TipoMetaType] = campo(filter_input=TipoMetaFilter)
    tiposCanalDifusion: list[TipoCanalDifusionType] = campo(filter_input=TipoCanalDifusionFilter)
    plantillasCampania: list[PlantillaCampaniaType] = campo(filter_input=PlantillaCampaniaFilter)

    # === RELACIONES (contacto ↔ contacto) ===
    tiposRelacion: list[TipoRelacionType] = campo(filter_input=TipoRelacionFilter)
    relaciones: list[RelacionType] = campo(filter_input=RelacionFilter)

    # === ETIQUETAS (tags de contacto) ===
    etiquetas: list[EtiquetaType] = campo(filter_input=EtiquetaFilter)
    contactosEtiquetas: list[ContactoEtiquetaType] = campo(filter_input=ContactoEtiquetaFilter)

    # === ACTIVIDADES ===
    tiposActividad: list[TipoActividadType] = campo(filter_input=TipoActividadFilter)
    actividades: list[ActividadType] = campo(filter_input=ActividadFilter)
    tareas: list[TareaType] = campo(filter_input=TareaFilter)
    participaciones: list[ParticipacionType] = campo(filter_input=ParticipacionFilter)

    # === GRUPOS ===
    tiposGrupo: list[TipoGrupoType] = campo(filter_input=TipoGrupoFilter)
    rolesGrupo: list[RolGrupoType] = campo(filter_input=RolGrupoFilter)
    gruposTrabajo: list[GrupoTrabajoType] = campo(filter_input=GrupoTrabajoFilter)
    miembrosGrupo: list[MiembroGrupoType] = campo(filter_input=MiembroGrupoFilter)
    gruposIniciativa: list[GrupoIniciativaType] = campo(filter_input=GrupoIniciativaFilter)
    reunionesGrupo: list[ReunionGrupoType] = campo()
    asistentesReunion: list[AsistenteReunionType] = campo()
    requisitosRecurso: list[RequisitoRecursoType] = campo(filter_input=RequisitoRecursoFilter)
    aportacionesHoras: list[AportacionHorasType] = campo(filter_input=AportacionHorasFilter)

    # === VOLUNTARIADO ===
    categoriasCompetencia: list[CategoriaCompetenciaType] = campo(filter_input=CategoriaCompetenciaFilter)
    competencias: list[CompetenciaType] = campo(filter_input=CompetenciaFilter)
    nivelesCompetencia: list[NivelCompetenciaType] = campo(filter_input=NivelCompetenciaFilter)
    miembrosCompetencia: list[MiembroCompetenciaType] = campo(filter_input=MiembroCompetenciaFilter)
    tiposDocumentoVoluntario: list[TipoDocumentoVoluntarioType] = campo(filter_input=TipoDocumentoVoluntarioFilter)
    documentosMiembro: list[DocumentoMiembroType] = campo(filter_input=DocumentoMiembroFilter)
    tiposFormacion: list[TipoFormacionType] = campo(filter_input=TipoFormacionFilter)
    formacionesMiembro: list[FormacionMiembroType] = campo(filter_input=FormacionMiembroFilter)

    # === SECRETARÍA — PLATAFORMAS TELEMÁTICAS ===
    plataformasTelematicas: list[PlataformaTelematicaType] = campo(filter_input=PlataformaTelematicaFilter)

    # === PROTECCIÓN DE DATOS (RGPD) ===
    rgpdEncargados: list[EncargadoTratamientoType] = campo(filter_input=EncargadoTratamientoFilter)
    rgpdActividadesTratamiento: list[ActividadTratamientoType] = campo(filter_input=ActividadTratamientoFilter)
    rgpdActividadesEncargados: list[ActividadTratamientoEncargadoType] = campo(filter_input=ActividadTratamientoEncargadoFilter)
    rgpdClausulas: list[ClausulaInformativaType] = campo(filter_input=ClausulaInformativaFilter)
    rgpdConsentimientos: list[ConsentimientoType] = campo(filter_input=ConsentimientoFilter)
    rgpdSolicitudesDerechos: list[SolicitudDerechoRGPDType] = campo(filter_input=SolicitudDerechoRGPDFilter)
    rgpdBrechasSeguridad: list[BrechaSeguridadType] = campo(filter_input=BrechaSeguridadFilter)
    rgpdAuditoriaAccesos: list[AuditoriaAccesoDatosType] = campo(filter_input=AuditoriaAccesoDatosFilter)


# Importar mutations
from .mutations import Mutation


# Schema principal con queries y mutations
# Strawberry usa camelCase por defecto para campos de tipos
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
