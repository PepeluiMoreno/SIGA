// Queries y mutations GraphQL del módulo de Secretaría
// Los resolvers SEC_* usan tipos inline (no strawchemy), camelCase manual

// ── TIPOS DE REUNIÓN ────────────────────────────────────────────────────────

export const GET_TIPOS_REUNION = `
  query TiposReunion {
    tiposReunion {
      id
      nombre
      tipoOrganoId
      tipoOrganoNombre
      descripcion
      quorumPrimeraConvocatoria
      quorumSegundaConvocatoria
      antelacionMinimaDias
      activo
      orden
    }
  }
`

// ── PLATAFORMAS TELEMÁTICAS ──────────────────────────────────────────────────

export const GET_PLATAFORMAS_TELEMATICAS = `
  query PlataformasTelematicas {
    plataformasTelematicas(filter: { eliminado: { eq: false } }) {
      id
      codigo
      nombre
      descripcion
      icono
      activa
      orden
      urlBase
      camposEsquema
      esInmutable
    }
  }
`

export const CREATE_PLATAFORMA_TELEMATICA = `
  mutation CreatePlataformaTelematica($data: PlataformaTelematicaCreateInput!) {
    crearPlataformaTelematica(data: $data) { id }
  }
`

export const UPDATE_PLATAFORMA_TELEMATICA = `
  mutation UpdatePlataformaTelematica($data: PlataformaTelematicaUpdateInput!) {
    actualizarPlataformaTelematica(data: $data) { id }
  }
`

export const DELETE_PLATAFORMAS_TELEMATICAS = `
  mutation DeletePlataformasTelematicas($filter: PlataformaTelematicaFilter!) {
    eliminarPlataformasTelematicas(filter: $filter) { id }
  }
`

// ── REUNIONES ────────────────────────────────────────────────────────────────

export const GET_REUNIONES = `
  query Reuniones($anio: Int, $tipoReunionId: UUID, $estadoCodigo: String) {
    reuniones(anio: $anio, tipoReunionId: $tipoReunionId, estadoCodigo: $estadoCodigo) {
      id
      tipoReunionId
      agrupacionId
      organoId
      numeroConvocatoria
      anio
      fechaConvocatoria
      fechaCelebracion
      lugar
      esTelematica
      plataformaTelematica
      plataformaTelematicaId
      datosConexionTelematica
      tieneSegundaConvocatoria
      convocatoriaUtilizada
      sociosTotales
      sociosPresentes
      sociosRepresentados
      hayQuorum
      estadoCodigo
      estadoId
      observaciones
    }
  }
`

export const CONVOCAR_REUNION = `
  mutation ConvocarReunion($data: ConvocarReunionInput!) {
    convocarReunion(data: $data) {
      id
      numeroConvocatoria
      anio
      fechaConvocatoria
      fechaCelebracion
      lugar
      esTelematica
      estadoCodigo
    }
  }
`

export const REGISTRAR_CELEBRACION = `
  mutation RegistrarCelebracionReunion($data: RegistrarCelebracionInput!) {
    registrarCelebracionReunion(data: $data) {
      id
      estadoCodigo
      sociosTotales
      sociosPresentes
      sociosRepresentados
      hayQuorum
      convocatoriaUtilizada
    }
  }
`

export const CANCELAR_REUNION = `
  mutation CancelarReunion($reunionId: UUID!, $motivo: String) {
    cancelarReunion(reunionId: $reunionId, motivo: $motivo) {
      id
      estadoCodigo
    }
  }
`

// ── ORDEN DEL DÍA ────────────────────────────────────────────────────────────

export const GET_PUNTOS_ORDEN_DIA = `
  query PuntosOrdenDia($reunionId: UUID!) {
    puntosOrdenDia(reunionId: $reunionId) {
      id
      reunionId
      orden
      titulo
      descripcion
      tipo
    }
  }
`

export const AGREGAR_PUNTO_ORDEN_DIA = `
  mutation AgregarPuntoOrdenDia($reunionId: UUID!, $titulo: String!, $descripcion: String, $orden: Int, $tipo: String!) {
    agregarPuntoOrdenDia(reunionId: $reunionId, titulo: $titulo, descripcion: $descripcion, orden: $orden, tipo: $tipo) {
      id
      reunionId
      orden
      titulo
      descripcion
      tipo
    }
  }
`

// ── ASISTENTES ───────────────────────────────────────────────────────────────

export const GET_ASISTENTES_REUNION = `
  query AsistentesReunion($reunionId: UUID!) {
    asistentesDeReunion(reunionId: $reunionId) {
      id
      reunionId
      miembroId
      tipoAsistencia
      representadoPorId
      cargo
    }
  }
`

export const REGISTRAR_ASISTENTE_REUNION = `
  mutation RegistrarAsistenteReunion($reunionId: UUID!, $miembroId: UUID!, $tipoAsistencia: String!, $representadoPorId: UUID, $cargo: String) {
    registrarAsistenteReunion(reunionId: $reunionId, miembroId: $miembroId, tipoAsistencia: $tipoAsistencia, representadoPorId: $representadoPorId, cargo: $cargo) {
      id
      reunionId
      miembroId
      tipoAsistencia
      representadoPorId
      cargo
    }
  }
`

// ── ACUERDOS ─────────────────────────────────────────────────────────────────

export const GET_ACUERDOS_DE_REUNION = `
  query AcuerdosDeReunion($reunionId: UUID!) {
    acuerdosDeReunion(reunionId: $reunionId) {
      id
      puntoOrdenDiaId
      numero
      descripcion
      tipoMayoria
      resultado
      responsableId
      fechaLimiteEjecucion
      estadoEjecucionCodigo
      observacionesEjecucion
    }
  }
`

// El acuerdo produce el mandato: primero se le adjunta a QUIÉN nombra/cesa y para
// qué cargo (fijar), y después se le da efecto (ejecutar).
export const FIJAR_NOMBRAMIENTO_DE_ACUERDO = `
  mutation FijarNombramientoDeAcuerdo(
    $acuerdoId: UUID!, $miembroId: UUID!, $cargoId: UUID!, $fechaInicio: Date!,
    $agrupacionId: UUID, $fechaFin: Date, $tipoCodigo: String!
  ) {
    fijarNombramientoDeAcuerdo(
      acuerdoId: $acuerdoId, miembroId: $miembroId, cargoId: $cargoId, fechaInicio: $fechaInicio,
      agrupacionId: $agrupacionId, fechaFin: $fechaFin, tipoCodigo: $tipoCodigo
    )
  }
`

export const EJECUTAR_ACUERDO = `
  mutation EjecutarAcuerdo($acuerdoId: UUID!, $exigirActaAprobada: Boolean!) {
    ejecutarAcuerdo(acuerdoId: $acuerdoId, exigirActaAprobada: $exigirActaAprobada)
  }
`

export const GET_ACUERDOS_PENDIENTES = `
  query AcuerdosPendientes($agrupacionId: UUID) {
    acuerdosPendientes(agrupacionId: $agrupacionId) {
      id
      puntoOrdenDiaId
      numero
      descripcion
      tipoMayoria
      resultado
      responsableId
      fechaLimiteEjecucion
      estadoEjecucionCodigo
      estadoEjecucionId
      observacionesEjecucion
    }
  }
`

export const REGISTRAR_ACUERDO = `
  mutation RegistrarAcuerdo($data: RegistrarAcuerdoInput!) {
    registrarAcuerdo(data: $data) {
      id
      puntoOrdenDiaId
      numero
      descripcion
      tipoMayoria
      resultado
      estadoEjecucionCodigo
    }
  }
`

export const ACTUALIZAR_SEGUIMIENTO = `
  mutation ActualizarSeguimientoAcuerdo($data: ActualizarSeguimientoInput!) {
    actualizarSeguimientoAcuerdo(data: $data) {
      id
      estadoEjecucionCodigo
      observacionesEjecucion
    }
  }
`

// ── ACTAS ─────────────────────────────────────────────────────────────────────

export const GET_ACTAS = `
  query Actas($anio: Int, $estadoCodigo: String, $agrupacionId: UUID, $tipoReunionId: UUID) {
    actas(anio: $anio, estadoCodigo: $estadoCodigo, agrupacionId: $agrupacionId, tipoReunionId: $tipoReunionId) {
      id
      reunionId
      numero
      anio
      estadoCodigo
      estadoId
      fechaAprobacion
      secretarioId
      presidenteId
      fechaFirma
    }
  }
`

export const GET_ACTAS_PENDIENTES = `
  query ActasPendientesAprobacion {
    actasPendientesAprobacion {
      id
      reunionId
      numero
      anio
      estadoCodigo
    }
  }
`

export const CREAR_ACTA_BORRADOR = `
  mutation CrearActaBorrador($data: CrearActaInput!) {
    crearActaBorrador(data: $data) {
      id
      numero
      anio
      estadoCodigo
    }
  }
`

export const APROBAR_ACTA = `
  mutation AprobarActa($actaId: UUID!, $fechaAprobacion: Date!, $reunionAprobacionId: UUID) {
    aprobarActa(actaId: $actaId, fechaAprobacion: $fechaAprobacion, reunionAprobacionId: $reunionAprobacionId) {
      id
      estadoCodigo
      estadoId
      fechaAprobacion
    }
  }
`

export const ANULAR_APROBACION_ACTA = `
  mutation AnularAprobacionActa($actaId: UUID!, $motivo: String) {
    anularAprobacionActa(actaId: $actaId, motivo: $motivo) {
      id
      estadoCodigo
      estadoId
      fechaAprobacion
    }
  }
`

export const FIRMAR_ACTA = `
  mutation FirmarActa($actaId: UUID!, $secretarioId: UUID!, $presidenteId: UUID!) {
    firmarActa(actaId: $actaId, secretarioId: $secretarioId, presidenteId: $presidenteId) {
      id
      estadoCodigo
      fechaFirma
    }
  }
`

// ── CERTIFICADOS ──────────────────────────────────────────────────────────────

export const GET_CERTIFICADOS = `
  query CertificadosAcuerdo($actaId: UUID, $anio: Int) {
    certificadosAcuerdo(actaId: $actaId, anio: $anio) {
      id
      actaId
      acuerdoId
      numeroCertificado
      fechaEmision
      destinatario
      proposito
    }
  }
`

export const EMITIR_CERTIFICADO = `
  mutation EmitirCertificadoAcuerdo($data: EmitirCertificadoInput!) {
    emitirCertificadoAcuerdo(data: $data) {
      id
      numeroCertificado
      fechaEmision
    }
  }
`

// ── LIBRO DE SOCIOS ───────────────────────────────────────────────────────────

export const GET_LIBRO_SOCIOS_SNAPSHOTS = `
  query LibroSociosSnapshots {
    libroSociosSnapshots {
      id
      fechaCorte
      fechaGeneracion
      totalSociosActivos
      totalSociosBaja
      totalSociosHistorico
      motivo
      tienePdf
    }
  }
`

export const GENERAR_LIBRO_SOCIOS = `
  mutation GenerarLibroSocios($fechaCorte: Date, $motivo: String) {
    generarLibroSocios(fechaCorte: $fechaCorte, motivo: $motivo) {
      id
      fechaCorte
      totalSociosActivos
      totalSociosHistorico
    }
  }
`

// ── CONVENIOS ─────────────────────────────────────────────────────────────────

export const GET_TIPOS_CONVENIO = `
  query TiposConvenio {
    tiposConvenio {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const GET_CONVENIOS = `
  query Convenios($estado: String, $proximosAVencerDias: Int) {
    convenios(estado: $estado, proximosAVencerDias: $proximosAVencerDias) {
      id
      tipoConvenioId
      referencia
      titulo
      entidadContraparte
      cifContraparte
      fechaFirma
      fechaInicio
      fechaFin
      renovacionAutomatica
      estado
      objeto
      firmanteId
    }
  }
`

export const REGISTRAR_CONVENIO = `
  mutation RegistrarConvenio($data: RegistrarConvenioInput!) {
    registrarConvenio(data: $data) {
      id
      referencia
      titulo
      estado
    }
  }
`

export const CAMBIAR_ESTADO_CONVENIO = `
  mutation CambiarEstadoConvenio($convenioId: UUID!, $nuevoEstado: String!) {
    cambiarEstadoConvenio(convenioId: $convenioId, nuevoEstado: $nuevoEstado) {
      id
      estado
    }
  }
`

// ── DELEGACIONES ──────────────────────────────────────────────────────────────

export const GET_DELEGACIONES = `
  query DelegacionesFirma($activasSolo: Boolean) {
    delegacionesFirma(activasSolo: $activasSolo) {
      id
      deleganteId
      delegadoId
      descripcionActos
      limiteImporte
      fechaInicio
      fechaFin
      activa
    }
  }
`

export const CREAR_DELEGACION = `
  mutation CrearDelegacionFirma($data: CrearDelegacionInput!) {
    crearDelegacionFirma(data: $data) {
      id
      descripcionActos
      activa
    }
  }
`

export const REVOCAR_DELEGACION = `
  mutation RevocarDelegacionFirma($delegacionId: UUID!) {
    revocarDelegacionFirma(delegacionId: $delegacionId) {
      id
      activa
    }
  }
`

// ── MIEMBROS (ligero, para selectores) ───────────────────────────────────────

export const GET_MIEMBROS_LIGERO = `
  query MiembrosLigero {
    miembros: socios(activo: true) {
      id
      nombre
      apellido1
      apellido2
      email
    }
  }
`
