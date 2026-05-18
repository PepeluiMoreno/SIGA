// Queries y Mutations GraphQL para el módulo de Tesorería

export const GET_CUENTAS_BANCARIAS = `
  query CuentasBancarias {
    cuentasBancarias {
      id
      nombre
      iban
      bicSwift
      bancoNombre
      titular
      saldoActual
      saldoConciliado
      activa
      agrupacionId
      descripcion
      fechaCreacion
      agrupacion {
        id
        nombre
      }
    }
  }
`

export const GET_CUENTA_BANCARIA = `
  query CuentaBancaria($id: UUID!) {
    cuentasBancarias(filter: { id: { eq: $id } }) {
      id
      nombre
      iban
      bicSwift
      bancoNombre
      titular
      saldoActual
      saldoConciliado
      activa
      descripcion
    }
  }
`

export const GET_APUNTES_CAJA = `
  query ApuntesCaja($cuentaId: UUID) {
    apuntesCaja(filter: { cuentaBancariaId: { eq: $cuentaId } }) {
      id
      cuentaBancariaId
      tipo
      origen
      importe
      fecha
      concepto
      referenciaExterna
      conciliado
      fechaConciliacion
      asientoId
      observaciones
      fechaCreacion
    }
  }
`

export const GET_EXTRACTOS_BANCARIOS = `
  query ExtractosBancarios($cuentaId: UUID) {
    extractosBancarios(filter: { cuentaBancariaId: { eq: $cuentaId } }) {
      id
      cuentaBancariaId
      fecha
      importe
      concepto
      referencia
      conciliado
    }
  }
`

export const GET_CONCILIACIONES_BANCARIAS = `
  query ConciliacionesBancarias($cuentaId: UUID) {
    conciliacionesBancarias(filter: { cuentaBancariaId: { eq: $cuentaId } }) {
      id
      cuentaBancariaId
      fechaInicio
      fechaFin
      saldoInicialExtracto
    }
  }
`

export const CREATE_CUENTA_BANCARIA = `
  mutation CrearCuentaBancaria($input: CuentaBancariaCreateInput!) {
    crearCuentaBancaria(data: $input) {
      id
      nombre
      iban
      saldoActual
      activa
    }
  }
`

export const UPDATE_CUENTA_BANCARIA = `
  mutation ActualizarCuentaBancaria($input: CuentaBancariaUpdateInput!) {
    actualizarCuentaBancaria(data: $input) {
      id
      nombre
      iban
      activa
    }
  }
`

export const REGISTRAR_APUNTE_CAJA = `
  mutation RegistrarApunteCaja(
    $cuentaId: UUID!
    $fecha: Date!
    $importe: Float!
    $tipo: String!
    $concepto: String!
    $origen: String
    $referenciaExterna: String
    $observaciones: String
  ) {
    registrarApunteCaja(
      cuentaId: $cuentaId
      fecha: $fecha
      importe: $importe
      tipo: $tipo
      concepto: $concepto
      origen: $origen
      referenciaExterna: $referenciaExterna
      observaciones: $observaciones
    )
  }
`

export const MARCAR_APUNTE_CONCILIADO = `
  mutation MarcarApunteConciliado($apunteId: UUID!, $fechaConciliacion: Date) {
    marcarApunteConciliado(apunteId: $apunteId, fechaConciliacion: $fechaConciliacion)
  }
`

export const CREATE_CONCILIACION_BANCARIA = `
  mutation CrearConciliacionBancaria($input: ConciliacionBancariaCreateInput!) {
    crearConciliacionBancaria(data: $input) {
      id
      diferencia
      conciliado
    }
  }
`

export const CONFIRMAR_CONCILIACION = `
  mutation ConfirmarConciliacionPeriodo($conciliacionId: UUID!) {
    confirmarConciliacionPeriodo(conciliacionId: $conciliacionId)
  }
`
