// Queries y Mutations GraphQL para el módulo de Tesorería

// Query para obtener todas las cuentas bancarias
export const GET_CUENTAS_BANCARIAS = `
  query CuentasBancarias {
    cuentasBancarias {
      id
      nombre
      iban
      bicSwift
      bancoNombre
      saldoActual
      activa
      agrupacion {
        id
        nombre
      }
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener una cuenta bancaria específica
export const GET_CUENTA_BANCARIA = `
  query CuentaBancaria($id: UUID!) {
    cuentaBancaria(id: $id) {
      id
      nombre
      iban
      bicSwift
      bancoNombre
      saldoActual
      activa
      agrupacion {
        id
        nombre
      }
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener movimientos de tesorería
export const GET_MOVIMIENTOS_TESORERIA = `
  query MovimientosTesoreria($cuentaId: UUID, $fechaInicio: Date, $fechaFin: Date) {
    movimientosTesoreria(filter: {
      cuentaId: {eq: $cuentaId}
      fecha: {gte: $fechaInicio, lte: $fechaFin}
    }) {
      id
      cuenta {
        id
        nombre
      }
      fecha
      importe
      tipo
      concepto
      referenciaExterna
      entidadOrigenTipo
      entidadOrigenId
      conciliado
      fechaConciliacion
      asiento {
        id
        numeroAsiento
      }
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener movimientos no conciliados
export const GET_MOVIMIENTOS_NO_CONCILIADOS = `
  query MovimientosNoConciliados($cuentaId: UUID!) {
    movimientosTesoreria(filter: {
      cuentaId: {eq: $cuentaId}
      conciliado: {eq: false}
    }) {
      id
      fecha
      importe
      tipo
      concepto
      referenciaExterna
      observaciones
    }
  }
`

// Query para obtener conciliaciones bancarias
export const GET_CONCILIACIONES_BANCARIAS = `
  query ConciliacionesBancarias($cuentaId: UUID!) {
    conciliacionesBancarias(filter: {cuentaId: {eq: $cuentaId}}) {
      id
      cuenta {
        id
        nombre
      }
      fechaInicio
      fechaFin
      saldoInicialExtracto
      saldoFinalExtracto
      saldoInicialSistema
      saldoFinalSistema
      diferencia
      conciliado
      fechaConciliacion
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener una conciliación específica
export const GET_CONCILIACION_BANCARIA = `
  query ConciliacionBancaria($id: UUID!) {
    conciliacionBancaria(id: $id) {
      id
      cuenta {
        id
        nombre
      }
      fechaInicio
      fechaFin
      saldoInicialExtracto
      saldoFinalExtracto
      saldoInicialSistema
      saldoFinalSistema
      diferencia
      conciliado
      fechaConciliacion
      observaciones
    }
  }
`

// Mutation para crear una cuenta bancaria
export const CREATE_CUENTA_BANCARIA = `
  mutation CrearCuentaBancaria(
    $nombre: String!
    $iban: String!
    $bancoNombre: String!
    $bicSwift: String
    $agrupacionId: UUID
    $observaciones: String
  ) {
    crearCuentaBancaria(
      nombre: $nombre
      iban: $iban
      bancoNombre: $bancoNombre
      bicSwift: $bicSwift
      agrupacionId: $agrupacionId
      observaciones: $observaciones
    ) {
      id
      nombre
      iban
      bancoNombre
      saldoActual
      activa
    }
  }
`

// Mutation para registrar un movimiento
export const CREATE_MOVIMIENTO_TESORERIA = `
  mutation CrearMovimientoTesoreria(
    $cuentaId: UUID!
    $fecha: Date!
    $importe: Decimal!
    $tipo: String!
    $concepto: String!
    $referenciaExterna: String
    $entidadOrigenTipo: String
    $entidadOrigenId: UUID
    $observaciones: String
  ) {
    crearMovimientoTesoreria(
      cuentaId: $cuentaId
      fecha: $fecha
      importe: $importe
      tipo: $tipo
      concepto: $concepto
      referenciaExterna: $referenciaExterna
      entidadOrigenTipo: $entidadOrigenTipo
      entidadOrigenId: $entidadOrigenId
      observaciones: $observaciones
    ) {
      id
      fecha
      importe
      tipo
      concepto
      conciliado
    }
  }
`

// Mutation para marcar movimiento como conciliado
export const MARCAR_MOVIMIENTO_CONCILIADO = `
  mutation MarcarMovimientoConciliado(
    $movimientoId: UUID!
    $fechaConciliacion: Date
  ) {
    marcarMovimientoConciliado(
      movimientoId: $movimientoId
      fechaConciliacion: $fechaConciliacion
    ) {
      id
      conciliado
      fechaConciliacion
    }
  }
`

// Mutation para crear conciliación bancaria
export const CREATE_CONCILIACION_BANCARIA = `
  mutation CrearConciliacionBancaria(
    $cuentaId: UUID!
    $fechaInicio: Date!
    $fechaFin: Date!
    $saldoInicialExtracto: Decimal!
    $saldoFinalExtracto: Decimal!
  ) {
    crearConciliacionBancaria(
      cuentaId: $cuentaId
      fechaInicio: $fechaInicio
      fechaFin: $fechaFin
      saldoInicialExtracto: $saldoInicialExtracto
      saldoFinalExtracto: $saldoFinalExtracto
    ) {
      id
      diferencia
      conciliado
    }
  }
`

// Mutation para confirmar conciliación
export const CONFIRMAR_CONCILIACION = `
  mutation ConfirmarConciliacion($conciliacionId: UUID!) {
    confirmarConciliacion(conciliacionId: $conciliacionId) {
      id
      conciliado
      fechaConciliacion
    }
  }
`
