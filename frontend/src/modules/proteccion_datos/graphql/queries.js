// Queries y mutations GraphQL del módulo Protección de Datos (RGPD).
// El cliente es graphql-request (ver @/graphql/client.js): las queries son
// strings normales, sin tag `gql` de Apollo.

// ────────────────────────────────────────────────────────────────────────────
// ENCARGADOS DEL TRATAMIENTO (art. 28 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_ENCARGADOS = `
  query GetRgpdEncargados {
    rgpdEncargados(filter: { eliminado: { eq: false } }) {
      id
      nombre
      nif
      servicio
      contactoEmail
      contactoTelefono
      paisAlojamiento
      transferenciaInternacional
      contratoFirmado
      contratoFecha
      contratoDocumentoUrl
      clausulasTipoAepd
      notas
      activo
    }
  }
`

export const CREATE_ENCARGADO = `
  mutation CreateRgpdEncargado($data: EncargadoTratamientoCreateInput!) {
    crearRgpdEncargado(data: $data) { id }
  }
`

export const UPDATE_ENCARGADO = `
  mutation UpdateRgpdEncargado($data: EncargadoTratamientoUpdateInput!) {
    actualizarRgpdEncargado(data: $data) { id }
  }
`

export const DELETE_ENCARGADOS = `
  mutation DeleteRgpdEncargados($filter: EncargadoTratamientoFilter!) {
    eliminarRgpdEncargados(filter: $filter) { id }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// REGISTRO DE ACTIVIDADES DE TRATAMIENTO (RAT, art. 30 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_ACTIVIDADES_TRATAMIENTO = `
  query GetRgpdActividadesTratamiento {
    rgpdActividadesTratamiento(filter: { eliminado: { eq: false } }) {
      id
      nombre
      descripcion
      finalidad
      baseJuridica
      baseJuridicaDetalle
      categoriasInteresados
      categoriasDatos
      datosSensibles
      datosSensiblesDetalle
      destinatariosCesion
      transferenciasInternacionales
      transferenciasPaises
      transferenciasGarantias
      plazoConservacion
      medidasSeguridad
      activa
      fechaAltaActividad
      fechaRevision
      encargadosRel {
        id
        encargado { id nombre servicio }
      }
    }
  }
`

export const CREATE_ACTIVIDAD_TRATAMIENTO = `
  mutation CreateRgpdActividadTratamiento($data: ActividadTratamientoCreateInput!) {
    crearRgpdActividadTratamiento(data: $data) { id }
  }
`

export const UPDATE_ACTIVIDAD_TRATAMIENTO = `
  mutation UpdateRgpdActividadTratamiento($data: ActividadTratamientoUpdateInput!) {
    actualizarRgpdActividadTratamiento(data: $data) { id }
  }
`

export const DELETE_ACTIVIDADES_TRATAMIENTO = `
  mutation DeleteRgpdActividadesTratamiento($filter: ActividadTratamientoFilter!) {
    eliminarRgpdActividadesTratamiento(filter: $filter) { id }
  }
`

export const CREATE_ACTIVIDAD_ENCARGADO = `
  mutation CreateRgpdActividadEncargado($data: ActividadTratamientoEncargadoCreateInput!) {
    crearRgpdActividadEncargado(data: $data) { id }
  }
`

export const DELETE_ACTIVIDAD_ENCARGADO = `
  mutation DeleteRgpdActividadEncargado($filter: ActividadTratamientoEncargadoFilter!) {
    eliminarRgpdActividadesEncargados(filter: $filter) { id }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// CLÁUSULAS INFORMATIVAS (art. 13/14 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_CLAUSULAS = `
  query GetRgpdClausulas {
    rgpdClausulas(filter: { eliminado: { eq: false } }) {
      id
      codigo
      version
      vigente
      fechaVigenciaDesde
      fechaVigenciaHasta
      finalidadCorta
      texto
    }
  }
`

export const CREATE_CLAUSULA = `
  mutation CreateRgpdClausula($data: ClausulaInformativaCreateInput!) {
    crearRgpdClausula(data: $data) { id }
  }
`

export const UPDATE_CLAUSULA = `
  mutation UpdateRgpdClausula($data: ClausulaInformativaUpdateInput!) {
    actualizarRgpdClausula(data: $data) { id }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// CONSENTIMIENTOS (art. 7 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_CONSENTIMIENTOS = `
  query GetRgpdConsentimientos {
    rgpdConsentimientos(filter: { eliminado: { eq: false } }) {
      id
      miembroId
      usuarioId
      emailExterno
      nombreExterno
      clausulaId
      clausula { id codigo version finalidadCorta }
      estado
      fechaOtorgamiento
      fechaRetirada
      canal
      prueba
    }
  }
`

export const RETIRAR_CONSENTIMIENTO = `
  mutation RetirarConsentimientoRGPD($consentimientoId: UUID!) {
    retirarConsentimientoRgpd(consentimientoId: $consentimientoId) {
      id estado fechaRetirada
    }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// SOLICITUDES DE DERECHOS ARSULIPO (art. 15-22 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_SOLICITUDES = `
  query GetRgpdSolicitudesDerechos {
    rgpdSolicitudesDerechos(filter: { eliminado: { eq: false } }) {
      id
      codigoInterno
      tipo
      estado
      miembroId
      usuarioId
      nombreSolicitante
      documentoSolicitante
      emailSolicitante
      telefonoSolicitante
      canalPresentacion
      fechaPresentacion
      fechaLimiteRespuesta
      prorrogada
      fechaLimiteProrroga
      motivoProrroga
      descripcionSolicitud
      fechaResolucion
      resolucion
      documentoResolucionUrl
    }
  }
`

export const REGISTRAR_SOLICITUD = `
  mutation RegistrarSolicitudDerechoRGPD(
    $tipo: String!
    $nombreSolicitante: String!
    $fechaPresentacion: Date!
    $canalPresentacion: String!
    $miembroId: UUID
    $usuarioId: UUID
    $documentoSolicitante: String
    $emailSolicitante: String
    $telefonoSolicitante: String
    $descripcionSolicitud: String
  ) {
    registrarSolicitudDerechoRgpd(
      tipo: $tipo
      nombreSolicitante: $nombreSolicitante
      fechaPresentacion: $fechaPresentacion
      canalPresentacion: $canalPresentacion
      miembroId: $miembroId
      usuarioId: $usuarioId
      documentoSolicitante: $documentoSolicitante
      emailSolicitante: $emailSolicitante
      telefonoSolicitante: $telefonoSolicitante
      descripcionSolicitud: $descripcionSolicitud
    ) {
      id codigoInterno estado fechaLimiteRespuesta
    }
  }
`

export const INICIAR_TRAMITE_SOLICITUD = `
  mutation IniciarTramiteSolicitudRGPD($solicitudId: UUID!) {
    iniciarTramiteSolicitudRgpd(solicitudId: $solicitudId) { id estado }
  }
`

export const PRORROGAR_SOLICITUD = `
  mutation ProrrogarSolicitudRGPD($solicitudId: UUID!, $motivoProrroga: String!) {
    prorrogarSolicitudRgpd(solicitudId: $solicitudId, motivoProrroga: $motivoProrroga) {
      id estado prorrogada fechaLimiteProrroga
    }
  }
`

export const RESOLVER_SOLICITUD = `
  mutation ResolverSolicitudRGPD(
    $solicitudId: UUID!
    $resolucion: String!
    $denegada: Boolean!
    $documentoResolucionUrl: String
  ) {
    resolverSolicitudRgpd(
      solicitudId: $solicitudId
      resolucion: $resolucion
      denegada: $denegada
      documentoResolucionUrl: $documentoResolucionUrl
    ) {
      id estado fechaResolucion resolucion
    }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// BRECHAS DE SEGURIDAD (art. 33 / 34 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_BRECHAS = `
  query GetRgpdBrechasSeguridad {
    rgpdBrechasSeguridad(filter: { eliminado: { eq: false } }) {
      id
      codigoInterno
      fechaDeteccion
      fechaOcurrencia
      descripcion
      origen
      severidad
      datosAfectados
      personasAfectadasNum
      datosSensiblesAfectados
      medidasInmediatas
      medidasCorrectivas
      notificadaAepd
      fechaNotificacionAepd
      referenciaAepd
      notificacionAepdDocumentoUrl
      motivoNoNotificacion
      comunicadaInteresados
      fechaComunicacionInteresados
      medioComunicacionInteresados
      cerrada
      fechaCierre
    }
  }
`

export const REGISTRAR_BRECHA = `
  mutation RegistrarBrechaSeguridad(
    $descripcion: String!
    $origen: String!
    $fechaDeteccion: DateTime!
    $severidad: String!
    $fechaOcurrencia: Date
    $datosAfectados: String
    $personasAfectadasNum: Int
    $datosSensiblesAfectados: Boolean!
    $medidasInmediatas: String
  ) {
    registrarBrechaSeguridad(
      descripcion: $descripcion
      origen: $origen
      fechaDeteccion: $fechaDeteccion
      severidad: $severidad
      fechaOcurrencia: $fechaOcurrencia
      datosAfectados: $datosAfectados
      personasAfectadasNum: $personasAfectadasNum
      datosSensiblesAfectados: $datosSensiblesAfectados
      medidasInmediatas: $medidasInmediatas
    ) {
      id codigoInterno severidad
    }
  }
`

export const NOTIFICAR_BRECHA_AEPD = `
  mutation NotificarBrechaAEPD(
    $brechaId: UUID!
    $fechaNotificacion: DateTime!
    $referenciaAepd: String
    $documentoUrl: String
  ) {
    notificarBrechaAepd(
      brechaId: $brechaId
      fechaNotificacion: $fechaNotificacion
      referenciaAepd: $referenciaAepd
      documentoUrl: $documentoUrl
    ) {
      id notificadaAepd fechaNotificacionAepd
    }
  }
`

export const CERRAR_BRECHA = `
  mutation CerrarBrechaSeguridad($brechaId: UUID!, $medidasCorrectivas: String!) {
    cerrarBrechaSeguridad(brechaId: $brechaId, medidasCorrectivas: $medidasCorrectivas) {
      id cerrada fechaCierre
    }
  }
`

export const UPDATE_BRECHA = `
  mutation UpdateRgpdBrecha($data: BrechaSeguridadUpdateInput!) {
    actualizarRgpdBrecha(data: $data) { id }
  }
`

// ────────────────────────────────────────────────────────────────────────────
// AUDITORÍA DE ACCESOS (art. 5.2 RGPD)
// ────────────────────────────────────────────────────────────────────────────

export const GET_AUDITORIA_ACCESOS = `
  query GetRgpdAuditoriaAccesos {
    rgpdAuditoriaAccesos {
      id
      fechaAcceso
      usuarioId
      usuarioEmailSnapshot
      entidad
      entidadId
      tipoAcceso
      camposAccedidos
      motivo
      ip
      userAgent
    }
  }
`
