// Queries y Mutations GraphQL para el módulo de parametrización
// Catálogos del sistema (tipos, estados, etc.)
//
// IMPORTANTE: Strawberry usa camelCase automáticamente
// - Query names: tiposMiembro, estadosCuota, etc.
// - Field names: requiereCuota, puedeVotar, etc.
// - NO usar campos 'codigo' - solo se identifican por UUID

// =============================================
// MIEMBROS
// =============================================

export const GET_TIPOS_MIEMBRO = `
  query TiposMiembro {
    tiposMiembro {
      id
      nombre
      descripcion
      requiereCuota
      puedeVotar
      activo
    }
  }
`

export const CREATE_TIPO_MIEMBRO = `
  mutation CrearTipoMiembro($data: TipoMiembroCreateInput!) {
    crearTipoMiembro(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_MIEMBRO = `
  mutation ActualizarTipoMiembro($data: TipoMiembroUpdateInput!) {
    actualizarTipoMiembro(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_MIEMBRO = `
  mutation EliminarTipoMiembro($filter: TipoMiembroFilter!) {
    eliminarTiposMiembro(filter: $filter) {
      id
    }
  }
`

export const GET_ESTADOS_MIEMBRO = `
  query EstadosMiembro {
    estadosMiembro {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_MIEMBRO = `
  mutation CrearEstadoMiembro($data: EstadoMiembroCreateInput!) {
    crearEstadoMiembro(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_MIEMBRO = `
  mutation ActualizarEstadoMiembro($data: EstadoMiembroUpdateInput!) {
    actualizarEstadoMiembro(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_MIEMBRO = `
  mutation EliminarEstadoMiembro($filter: EstadoMiembroFilter!) {
    eliminarEstadosMiembro(filter: $filter) {
      id
    }
  }
`

export const GET_MOTIVOS_BAJA = `
  query MotivosBaja {
    motivosBaja {
      id
      nombre
      descripcion
      requiereDocumentacion
      activo
    }
  }
`

export const CREATE_MOTIVO_BAJA = `
  mutation CrearMotivoBaja($data: MotivoBajaCreateInput!) {
    crearMotivoBaja(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_MOTIVO_BAJA = `
  mutation ActualizarMotivoBaja($data: MotivoBajaUpdateInput!) {
    actualizarMotivoBaja(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_MOTIVO_BAJA = `
  mutation EliminarMotivoBaja($filter: MotivoBajaFilter!) {
    eliminarMotivosBaja(filter: $filter) {
      id
    }
  }
`

// =============================================
// FINANCIERO
// =============================================

export const GET_ESTADOS_CUOTA = `
  query EstadosCuota {
    estadosCuota {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_CUOTA = `
  mutation CrearEstadoCuota($data: EstadoCuotaCreateInput!) {
    crearEstadoCuota(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_CUOTA = `
  mutation ActualizarEstadoCuota($data: EstadoCuotaUpdateInput!) {
    actualizarEstadoCuota(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_CUOTA = `
  mutation EliminarEstadoCuota($filter: EstadoCuotaFilter!) {
    eliminarEstadosCuota(filter: $filter) {
      id
    }
  }
`

export const GET_ESTADOS_DONACION = `
  query EstadosDonacion {
    estadosDonacion {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_DONACION = `
  mutation CrearEstadoDonacion($data: EstadoDonacionCreateInput!) {
    crearEstadoDonacion(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_DONACION = `
  mutation ActualizarEstadoDonacion($data: EstadoDonacionUpdateInput!) {
    actualizarEstadoDonacion(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_DONACION = `
  mutation EliminarEstadoDonacion($filter: EstadoDonacionFilter!) {
    eliminarEstadosDonacion(filter: $filter) {
      id
    }
  }
`

export const GET_ESTADOS_REMESA = `
  query EstadosRemesa {
    estadosRemesa {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_REMESA = `
  mutation CrearEstadoRemesa($data: EstadoRemesaCreateInput!) {
    crearEstadoRemesa(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_REMESA = `
  mutation ActualizarEstadoRemesa($data: EstadoRemesaUpdateInput!) {
    actualizarEstadoRemesa(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_REMESA = `
  mutation EliminarEstadoRemesa($filter: EstadoRemesaFilter!) {
    eliminarEstadosRemesa(filter: $filter) {
      id
    }
  }
`

export const GET_DONACION_CONCEPTOS = `
  query DonacionConceptos {
    donacionConceptos {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_DONACION_CONCEPTO = `
  mutation CrearDonacionConcepto($data: DonacionConceptoCreateInput!) {
    crearDonacionConcepto(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_DONACION_CONCEPTO = `
  mutation ActualizarDonacionConcepto($data: DonacionConceptoUpdateInput!) {
    actualizarDonacionConcepto(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_DONACION_CONCEPTO = `
  mutation EliminarDonacionConcepto($filter: DonacionConceptoFilter!) {
    eliminarDonacionConceptos(filter: $filter) {
      id
    }
  }
`

// =============================================
// CAMPAÑAS
// =============================================

export const GET_TIPOS_CAMPANIA = `
  query TiposCampania {
    tiposCampania {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_TIPO_CAMPANIA = `
  mutation CrearTipoCampania($data: TipoCampaniaCreateInput!) {
    crearTipoCampania(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_CAMPANIA = `
  mutation ActualizarTipoCampania($data: TipoCampaniaUpdateInput!) {
    actualizarTipoCampania(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_CAMPANIA = `
  mutation EliminarTipoCampania($filter: TipoCampaniaFilter!) {
    eliminarTiposCampania(filter: $filter) {
      id
    }
  }
`

export const GET_ESTADOS_CAMPANIA = `
  query EstadosCampania {
    estadosCampania {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_CAMPANIA = `
  mutation CrearEstadoCampania($data: EstadoCampaniaCreateInput!) {
    crearEstadoCampania(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_CAMPANIA = `
  mutation ActualizarEstadoCampania($data: EstadoCampaniaUpdateInput!) {
    actualizarEstadoCampania(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_CAMPANIA = `
  mutation EliminarEstadoCampania($filter: EstadoCampaniaFilter!) {
    eliminarEstadosCampania(filter: $filter) {
      id
    }
  }
`

export const GET_ROLES_PARTICIPANTE = `
  query RolesParticipante {
    rolesParticipante {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_ROL_PARTICIPANTE = `
  mutation CrearRolParticipante($data: RolParticipanteCreateInput!) {
    crearRolParticipante(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ROL_PARTICIPANTE = `
  mutation ActualizarRolParticipante($data: RolParticipanteUpdateInput!) {
    actualizarRolParticipante(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ROL_PARTICIPANTE = `
  mutation EliminarRolParticipante($filter: RolParticipanteFilter!) {
    eliminarRolesParticipante(filter: $filter) {
      id
    }
  }
`

// =============================================
// ACTIVIDADES
// =============================================

export const GET_TIPOS_ACTIVIDAD = `
  query TiposActividad {
    tiposActividad {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_TIPO_ACTIVIDAD = `
  mutation CrearTipoActividad($data: TipoActividadCreateInput!) {
    crearTipoActividad(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_ACTIVIDAD = `
  mutation ActualizarTipoActividad($data: TipoActividadUpdateInput!) {
    actualizarTipoActividad(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_ACTIVIDAD = `
  mutation EliminarTipoActividad($filter: TipoActividadFilter!) {
    eliminarTiposActividad(filter: $filter) {
      id
    }
  }
`

export const GET_ESTADOS_ACTIVIDAD = `
  query EstadosActividad {
    estadosActividad {
      id
      nombre
      descripcion
      color
      orden
      esInicial
      activo
    }
  }
`

export const CREATE_ESTADO_ACTIVIDAD = `
  mutation CrearEstadoActividad($data: EstadoActividadCreateInput!) {
    crearEstadoActividad(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_ACTIVIDAD = `
  mutation ActualizarEstadoActividad($data: EstadoActividadUpdateInput!) {
    actualizarEstadoActividad(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_ACTIVIDAD = `
  mutation EliminarEstadoActividad($filter: EstadoActividadFilter!) {
    eliminarEstadosActividad(filter: $filter) {
      id
    }
  }
`

export const GET_TIPOS_RECURSO = `
  query TiposRecurso {
    tiposRecurso {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_TIPO_RECURSO = `
  mutation CrearTipoRecurso($data: TipoRecursoCreateInput!) {
    crearTipoRecurso(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_RECURSO = `
  mutation ActualizarTipoRecurso($data: TipoRecursoUpdateInput!) {
    actualizarTipoRecurso(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_RECURSO = `
  mutation EliminarTipoRecurso($filter: TipoRecursoFilter!) {
    eliminarTiposRecurso(filter: $filter) {
      id
    }
  }
`

export const GET_TIPOS_KPI = `
  query TiposKPI {
    tiposKpi {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_TIPO_KPI = `
  mutation CrearTipoKPI($data: TipoKPICreateInput!) {
    crearTipoKpi(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_KPI = `
  mutation ActualizarTipoKPI($data: TipoKPIUpdateInput!) {
    actualizarTipoKpi(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_KPI = `
  mutation EliminarTipoKPI($filter: TipoKPIFilter!) {
    eliminarTiposKpi(filter: $filter) {
      id
    }
  }
`

// =============================================
// GRUPOS
// =============================================

export const GET_TIPOS_GRUPO = `
  query TiposGrupo {
    tiposGrupo {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_TIPO_GRUPO = `
  mutation CrearTipoGrupo($data: TipoGrupoCreateInput!) {
    crearTipoGrupo(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_GRUPO = `
  mutation ActualizarTipoGrupo($data: TipoGrupoUpdateInput!) {
    actualizarTipoGrupo(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_GRUPO = `
  mutation EliminarTipoGrupo($filter: TipoGrupoFilter!) {
    eliminarTiposGrupo(filter: $filter) {
      id
    }
  }
`

export const GET_ROLES_GRUPO = `
  query RolesGrupo {
    rolesGrupo {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_ROL_GRUPO = `
  mutation CrearRolGrupo($data: RolGrupoCreateInput!) {
    crearRolGrupo(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ROL_GRUPO = `
  mutation ActualizarRolGrupo($data: RolGrupoUpdateInput!) {
    actualizarRolGrupo(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ROL_GRUPO = `
  mutation EliminarRolGrupo($filter: RolGrupoFilter!) {
    eliminarRolesGrupo(filter: $filter) {
      id
    }
  }
`

// =============================================
// GEOGRÁFICO
// =============================================

export const GET_PAISES = `
  query Paises {
    paises {
      id
      codigo
      nombre
      activo
    }
  }
`

export const CREATE_PAIS = `
  mutation CrearPais($data: PaisCreateInput!) {
    crearPais(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_PAIS = `
  mutation ActualizarPais($data: PaisUpdateInput!) {
    actualizarPais(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_PAIS = `
  mutation EliminarPais($filter: PaisFilter!) {
    eliminarPaises(filter: $filter) {
      id
    }
  }
`

export const GET_PROVINCIAS = `
  query Provincias {
    provincias {
      id
      nombre
      comunidadAutonoma
      pais {
        id
        nombre
      }
      activo
    }
  }
`

export const CREATE_PROVINCIA = `
  mutation CrearProvincia($data: ProvinciaCreateInput!) {
    crearProvincia(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_PROVINCIA = `
  mutation ActualizarProvincia($data: ProvinciaUpdateInput!) {
    actualizarProvincia(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_PROVINCIA = `
  mutation EliminarProvincia($filter: ProvinciaFilter!) {
    eliminarProvincias(filter: $filter) {
      id
    }
  }
`

export const GET_MUNICIPIOS = `
  query Municipios($provinciaId: UUID) {
    municipios(filter: {provinciaId: {eq: $provinciaId}}) {
      id
      nombre
      codigoPostal
      provinciaId
      activo
    }
  }
`

export const GET_AGRUPACIONES_TERRITORIALES = `
  query AgrupacionesTerritoriales {
    agrupacionesTerritoriales {
      id
      nombre
      nombreCorto
      tipoId
      tipoUnidad { id nombre naturaleza vinculo nivel }
      agrupacionPadreId
      paisId
      provinciaId
      telefono
      email
      web
      nif
      fechaConstitucion
      registroOficial
      activo
    }
    coordinacionesTerritoriales {
      agrupacionId
      miembro { id nombre apellido1 fotoUrl }
    }
    miembros {
      agrupacionId
      esVoluntario
      activo
    }
  }
`

export const GET_TIPOS_UNIDADES_ORGANIZATIVAS = `
  query TiposUnidadesOrganizativas {
    tiposUnidadesOrganizativas(filter: { activo: { eq: true } }) {
      id nombre naturaleza vinculo nivel padreTipoId activo
    }
  }
`

export const CREATE_TIPO_UNIDAD_ORGANIZATIVA = `
  mutation CrearTipoUnidadOrganizativa(
    $nombre: String!, $naturaleza: String!, $vinculo: String!,
    $nivel: Int, $padreTipoId: UUID, $activo: Boolean!
  ) {
    crearTipoUnidadOrganizativa(
      nombre: $nombre, naturaleza: $naturaleza, vinculo: $vinculo,
      nivel: $nivel, padreTipoId: $padreTipoId, activo: $activo
    )
  }
`

export const UPDATE_TIPO_UNIDAD_ORGANIZATIVA = `
  mutation ActualizarTipoUnidadOrganizativa($data: TipoUnidadOrganizativaUpdateInput!) {
    actualizarTipoUnidadOrganizativa(data: $data) { id nombre naturaleza vinculo nivel padreTipoId activo }
  }
`

export const DELETE_TIPO_UNIDAD_ORGANIZATIVA = `
  mutation EliminarTipoUnidadOrganizativa($filter: TipoUnidadOrganizativaFilter!) {
    eliminarTiposUnidadesOrganizativas(filter: $filter) { id }
  }
`

export const CREATE_AGRUPACION_TERRITORIAL = `
  mutation CrearAgrupacionTerritorial($data: AgrupacionTerritorialCreateInput!) {
    crearAgrupacionTerritorial(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_AGRUPACION_TERRITORIAL = `
  mutation ActualizarAgrupacionTerritorial($data: AgrupacionTerritorialUpdateInput!) {
    actualizarAgrupacionTerritorial(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_AGRUPACION_TERRITORIAL = `
  mutation EliminarAgrupacionTerritorial($filter: AgrupacionTerritorialFilter!) {
    eliminarAgrupacionesTerritoriales(filter: $filter) {
      id
    }
  }
`

// ── Convenios de colaboración ─────────────────────────────────────────────────

export const GET_ESTADOS_CONVENIO = `
  query EstadosConvenio {
    estadosConvenio {
      id
      nombre
      descripcion
      orden
      activo
    }
  }
`

export const CREATE_ESTADO_CONVENIO = `
  mutation CrearEstadoConvenio($data: EstadoConvenioCreateInput!) {
    crearEstadoConvenio(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_ESTADO_CONVENIO = `
  mutation ActualizarEstadoConvenio($data: EstadoConvenioUpdateInput!) {
    actualizarEstadoConvenio(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_ESTADO_CONVENIO = `
  mutation EliminarEstadoConvenio($filter: EstadoConvenioFilter!) {
    eliminarEstadosConvenio(filter: $filter) {
      id
    }
  }
`

// ── Formas de pago ────────────────────────────────────────────────────────────

export const GET_FORMAS_PAGO_CATALOGO = `
  query FormasPago {
    formasPago {
      id codigo nombre descripcion activo
    }
  }
`

export const CREATE_FORMA_PAGO = `
  mutation CrearFormaPago($data: FormaPagoCreateInput!) {
    crearFormaPago(data: $data) { id nombre }
  }
`

export const UPDATE_FORMA_PAGO = `
  mutation ActualizarFormaPago($data: FormaPagoUpdateInput!) {
    actualizarFormaPago(data: $data) { id nombre }
  }
`

export const DELETE_FORMA_PAGO = `
  mutation EliminarFormasPago($filter: FormaPagoFilter!) {
    eliminarFormasPago(filter: $filter) { id }
  }
`

// ── Tipos de vinculación (Usuarios) ──────────────────────────────────────────

export const GET_TIPOS_VINCULACION_CATALOGO = `
  query TiposVinculacion {
    tiposVinculacion {
      id
      nombre
      requiereEntidad
      activo
    }
  }
`

export const CREATE_TIPO_VINCULACION = `
  mutation CrearTipoVinculacion($data: TipoVinculacionCreateInput!) {
    crearTipoVinculacion(data: $data) { id nombre }
  }
`

export const UPDATE_TIPO_VINCULACION = `
  mutation ActualizarTipoVinculacion($data: TipoVinculacionUpdateInput!) {
    actualizarTipoVinculacion(data: $data) { id nombre }
  }
`

export const DELETE_TIPO_VINCULACION = `
  mutation EliminarTiposVinculacion($filter: TipoVinculacionFilter!) {
    eliminarTiposVinculacion(filter: $filter) { id }
  }
`

// ── Habilidades (Socios/as) ───────────────────────────────────────────────────

export const GET_CATEGORIAS_HABILIDAD = `
  query CategoriasHabilidad {
    categoriasHabilidad {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const CREATE_CATEGORIA_HABILIDAD = `
  mutation CrearCategoriaHabilidad($data: CategoriaHabilidadCreateInput!) {
    crearCategoriaHabilidad(data: $data) { id nombre }
  }
`

export const UPDATE_CATEGORIA_HABILIDAD = `
  mutation ActualizarCategoriaHabilidad($data: CategoriaHabilidadUpdateInput!) {
    actualizarCategoriaHabilidad(data: $data) { id nombre }
  }
`

export const DELETE_CATEGORIA_HABILIDAD = `
  mutation EliminarCategoriasHabilidad($filter: CategoriaHabilidadFilter!) {
    eliminarCategoriasHabilidad(filter: $filter) { id }
  }
`

export const GET_HABILIDADES_CATALOGO = `
  query Habilidades {
    habilidades {
      id
      nombre
      descripcion
      categoriaId
      categoria { id nombre }
      activo
    }
  }
`

export const CREATE_HABILIDAD = `
  mutation CrearHabilidad($data: HabilidadCreateInput!) {
    crearHabilidad(data: $data) { id nombre }
  }
`

export const UPDATE_HABILIDAD = `
  mutation ActualizarHabilidad($data: HabilidadUpdateInput!) {
    actualizarHabilidad(data: $data) { id nombre }
  }
`

export const DELETE_HABILIDAD = `
  mutation EliminarHabilidades($filter: HabilidadFilter!) {
    eliminarHabilidades(filter: $filter) { id }
  }
`

export const GET_NIVELES_ESTUDIOS = `
  query NivelesEstudios {
    nivelesEstudios(filter: { activo: { eq: true } }) { id nombre descripcion orden activo }
  }
`
export const CREATE_NIVEL_ESTUDIOS = `
  mutation CrearNivelEstudios($data: NivelEstudiosCreateInput!) {
    crearNivelEstudios(data: $data) { id nombre }
  }
`
export const UPDATE_NIVEL_ESTUDIOS = `
  mutation ActualizarNivelEstudios($data: NivelEstudiosUpdateInput!, $filter: NivelEstudiosFilter!) {
    actualizarNivelesEstudios(data: $data, filter: $filter) { id nombre }
  }
`
export const DELETE_NIVEL_ESTUDIOS = `
  mutation EliminarNivelesEstudios($filter: NivelEstudiosFilter!) {
    eliminarNivelesEstudios(filter: $filter) { id }
  }
`

export const GET_NIVELES_HABILIDAD = `
  query NivelesHabilidad {
    nivelesHabilidad(filter: { activo: { eq: true } }) { id nombre descripcion orden activo }
  }
`
export const CREATE_NIVEL_HABILIDAD = `
  mutation CrearNivelHabilidad($data: NivelHabilidadCreateInput!) {
    crearNivelHabilidad(data: $data) { id nombre }
  }
`
export const UPDATE_NIVEL_HABILIDAD = `
  mutation ActualizarNivelHabilidad($data: NivelHabilidadUpdateInput!, $filter: NivelHabilidadFilter!) {
    actualizarNivelesHabilidad(data: $data, filter: $filter) { id nombre }
  }
`
export const DELETE_NIVEL_HABILIDAD = `
  mutation EliminarNivelesHabilidad($filter: NivelHabilidadFilter!) {
    eliminarNivelesHabilidad(filter: $filter) { id }
  }
`
