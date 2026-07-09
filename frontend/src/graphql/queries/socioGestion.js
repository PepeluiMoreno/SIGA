// Queries y mutations de gestión de socios añadidas en el MVP GSH→SIGA:
// estadísticas de altas/bajas, ciclo de vida (suspender/baja/reactivar),
// conversión simpatizante→socio, traslados y avisos de cobro.

// ─── Estadísticas de altas/bajas ─────────────────────────────────────────────
export const GET_ESTADISTICAS_ALTAS_BAJAS = `
  query EstadisticasAltasBajas($anioDesde: Int!, $anioHasta: Int!, $agrupacionId: UUID) {
    estadisticasAltasBajas(anioDesde: $anioDesde, anioHasta: $anioHasta, agrupacionId: $agrupacionId) {
      anio
      agrupacionId
      agrupacionNombre
      altas
      bajas
      neto
    }
  }
`

// ─── Ciclo de vida del socio ─────────────────────────────────────────────────
export const SUSPENDER_SOCIO = `
  mutation SuspenderSocio($contactoId: UUID!) {
    suspenderSocio(contactoId: $contactoId) { id estado }
  }
`

export const REACTIVAR_SOCIO = `
  mutation ReactivarSocio($contactoId: UUID!) {
    reactivarSocio(contactoId: $contactoId) { id estado }
  }
`

export const DAR_DE_BAJA_SOCIO = `
  mutation DarDeBajaSocio($contactoId: UUID!, $fechaBaja: Date, $motivoBajaId: UUID, $motivoBajaTexto: String) {
    darDeBajaSocio(contactoId: $contactoId, fechaBaja: $fechaBaja, motivoBajaId: $motivoBajaId, motivoBajaTexto: $motivoBajaTexto) {
      id estado
    }
  }
`

export const CONVERTIR_SIMPATIZANTE_EN_SOCIO = `
  mutation ConvertirSimpatizanteEnSocio($contactoId: UUID!, $numeroSocio: String, $cuotaMensual: Float, $iban: String, $swiftBic: String, $formaPagoId: UUID, $agrupacionId: UUID) {
    convertirSimpatizanteEnSocio(contactoId: $contactoId, numeroSocio: $numeroSocio, cuotaMensual: $cuotaMensual, iban: $iban, swiftBic: $swiftBic, formaPagoId: $formaPagoId, agrupacionId: $agrupacionId) {
      id estado
    }
  }
`

// ─── Traslados entre agrupaciones ────────────────────────────────────────────
export const GET_SOLICITUDES_TRASLADO = `
  query SolicitudesTraslado {
    solicitudesTraslado {
      id
      estado
      motivo
      fechaSolicitud
      fechaEfectivaDeseada
      agrupacionOrigenId
      agrupacionDestinoId
      aprobadoOrigen
      aprobadoDestino
      motivoRechazo
      miembro { id nombre apellido1 apellido2 }
    }
  }
`

export const SOLICITAR_TRASLADO = `
  mutation SolicitarTraslado($miembroId: UUID!, $agrupacionDestinoId: UUID!, $motivo: String!, $fechaEfectivaDeseada: Date) {
    solicitarTraslado(miembroId: $miembroId, agrupacionDestinoId: $agrupacionDestinoId, motivo: $motivo, fechaEfectivaDeseada: $fechaEfectivaDeseada) {
      id estado
    }
  }
`

export const APROBAR_TRASLADO_ORIGEN = `
  mutation AprobarTrasladoOrigen($solicitudId: UUID!, $observaciones: String) {
    aprobarTrasladoOrigen(solicitudId: $solicitudId, observaciones: $observaciones) { id estado }
  }
`

export const APROBAR_TRASLADO_DESTINO = `
  mutation AprobarTrasladoDestino($solicitudId: UUID!, $observaciones: String) {
    aprobarTrasladoDestino(solicitudId: $solicitudId, observaciones: $observaciones) { id estado }
  }
`

export const RECHAZAR_TRASLADO = `
  mutation RechazarTraslado($solicitudId: UUID!, $motivo: String!, $lado: String!) {
    rechazarTraslado(solicitudId: $solicitudId, motivo: $motivo, lado: $lado) { id estado }
  }
`

export const CANCELAR_TRASLADO = `
  mutation CancelarTraslado($solicitudId: UUID!) {
    cancelarTraslado(solicitudId: $solicitudId) { id estado }
  }
`

export const EJECUTAR_TRASLADO = `
  mutation EjecutarTraslado($solicitudId: UUID!) {
    ejecutarTraslado(solicitudId: $solicitudId) { id estado }
  }
`

// ─── Avisos de cobro ─────────────────────────────────────────────────────────
export const ENVIAR_AVISOS_PROXIMO_COBRO = `
  mutation EnviarAvisosProximoCobro($remesaId: UUID!) {
    enviarAvisosProximoCobro(remesaId: $remesaId)
  }
`

export const ENVIAR_AVISOS_CUOTA_PENDIENTE = `
  mutation EnviarAvisosCuotaPendiente($ejercicio: Int!, $soloSinDomiciliacion: Boolean!) {
    enviarAvisosCuotaPendiente(ejercicio: $ejercicio, soloSinDomiciliacion: $soloSinDomiciliacion)
  }
`
