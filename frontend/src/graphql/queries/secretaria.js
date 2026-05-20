// Queries y mutations GraphQL del módulo de Secretaría
// Los resolvers SEC_* usan tipos inline (no strawchemy), camelCase manual

// ── TIPOS DE REUNIÓN ────────────────────────────────────────────────────────

export const GET_TIPOS_REUNION = `
  query TiposReunion {
    tiposReunion {
      id
      nombre
      organo
      descripcion
      quorumPrimeraConvocatoria
      quorumSegundaConvocatoria
      antelacionMinimaDias
      activo
      orden
    }
  }
`

// ── REUNIONES ────────────────────────────────────────────────────────────────

export const GET_REUNIONES = `
  query Reuniones($anio: Int, $tipoReunionId: UUID, $estado: String) {
    reuniones(anio: $anio, tipoReunionId: $tipoReunionId, estado: $estado) {
      id
      tipoReunionId
      agrupacionId
      numeroConvocatoria
      anio
      fechaConvocatoria
      fechaCelebracion
      lugar
      esTelematica
      tienSegundaConvocatoria
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
      estado
    }
  }
`

export const REGISTRAR_CELEBRACION = `
  mutation RegistrarCelebracionReunion($data: RegistrarCelebracionInput!) {
    registrarCelebracionReunion(data: $data) {
      id
      estado
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
      estado
    }
  }
`

// ── ACUERDOS ─────────────────────────────────────────────────────────────────

export const GET_ACUERDOS_PENDIENTES = `
  query AcuerdosPendientes($agrupacionId: UUID) {
    acuerdosPendientes(agrupacionId: $agrupacionId) {
      id
      puntOrdenDiaId
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
      numero
      descripcion
      resultado
      estadoEjecucion
    }
  }
`

export const ACTUALIZAR_SEGUIMIENTO = `
  mutation ActualizarSeguimientoAcuerdo($data: ActualizarSeguimientoInput!) {
    actualizarSeguimientoAcuerdo(data: $data) {
      id
      estadoEjecucion
      observacionesEjecucion
    }
  }
`

// ── ACTAS ─────────────────────────────────────────────────────────────────────

export const GET_ACTAS = `
  query Actas($anio: Int, $estado: String) {
    actas(anio: $anio, estado: $estado) {
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
      estado
    }
  }
`

export const CREAR_ACTA_BORRADOR = `
  mutation CrearActaBorrador($data: CrearActaInput!) {
    crearActaBorrador(data: $data) {
      id
      numero
      anio
      estado
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

export const FIRMAR_ACTA = `
  mutation FirmarActa($actaId: UUID!, $secretarioId: UUID!, $presidenteId: UUID!) {
    firmarActa(actaId: $actaId, secretarioId: $secretarioId, presidenteId: $presidenteId) {
      id
      estado
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
    miembros(filter: { eliminado: { eq: false }, activo: { eq: true } }) {
      id
      nombre
      apellido1
      apellido2
      email
    }
  }
`
