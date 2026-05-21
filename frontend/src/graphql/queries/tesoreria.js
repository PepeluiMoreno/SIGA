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

// Bitácora: todos los apuntes de caja del ejercicio con la cuenta asociada y el id del asiento.
// El detalle del asiento (número, estado, ejercicio) se resuelve client-side via map sobre
// asientosContables ya cargados por useContabilidad (evita un non-null issue en la relación).
export const GET_BITACORA_MOVIMIENTOS = `
  query BitacoraMovimientos {
    apuntesCaja {
      id
      tipo
      origen
      importe
      fecha
      concepto
      referenciaExterna
      observaciones
      conciliado
      fechaConciliacion
      asientoId
      actividadId
      campaniaId
      categoriaFiscalId
      cuentaBancaria { id nombre iban }
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
    $actividadId: UUID
    $campaniaId: UUID
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
      actividadId: $actividadId
      campaniaId: $campaniaId
    )
  }
`

export const MARCAR_APUNTE_CONCILIADO = `
  mutation MarcarApunteConciliado($apunteId: UUID!, $fechaConciliacion: Date) {
    marcarApunteConciliado(apunteId: $apunteId, fechaConciliacion: $fechaConciliacion)
  }
`

export const DESMARCAR_APUNTE_CONCILIADO = `
  mutation DesmarcarApunteConciliado($apunteId: UUID!) {
    desmarcarApunteConciliado(apunteId: $apunteId)
  }
`

export const ACTUALIZAR_METADATOS_APUNTE = `
  mutation ActualizarMetadatosApunteCaja(
    $apunteId: UUID!
    $concepto: String
    $observaciones: String
    $actividadId: UUID
    $campaniaId: UUID
    $limpiarActividad: Boolean
  ) {
    actualizarMetadatosApunteCaja(
      apunteId: $apunteId
      concepto: $concepto
      observaciones: $observaciones
      actividadId: $actividadId
      campaniaId: $campaniaId
      limpiarActividad: $limpiarActividad
    )
  }
`

export const ANULAR_APUNTE_CAJA = `
  mutation AnularApunteCaja($apunteId: UUID!, $motivo: String!) {
    anularApunteCaja(apunteId: $apunteId, motivo: $motivo)
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
