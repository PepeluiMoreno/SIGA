// Queries y Mutations GraphQL para el módulo de Contabilidad

// Query para obtener el plan de cuentas
export const GET_PLAN_CUENTAS = `
  query PlanCuentas($tipo: String) {
    cuentasContables(filter: {tipo: {eq: $tipo}, activa: {eq: true}}) {
      id
      codigo
      nombre
      tipo
      nivel
      padre {
        id
        codigo
        nombre
      }
      permiteAsiento
      esDotacion
      activa
    }
  }
`

// Query para obtener una cuenta contable específica
export const GET_CUENTA_CONTABLE = `
  query CuentaContable($id: UUID!) {
    cuentaContable(id: $id) {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      padre {
        id
        codigo
        nombre
      }
      permiteAsiento
      esDotacion
      activa
    }
  }
`

// Query para obtener cuentas por código
export const GET_CUENTA_POR_CODIGO = `
  query CuentaPorCodigo($codigo: String!) {
    cuentaPorCodigo(codigo: $codigo) {
      id
      codigo
      nombre
      tipo
      nivel
      permiteAsiento
    }
  }
`

// Query para obtener asientos contables
export const GET_ASIENTOS_CONTABLES = `
  query AsientosContables(
    $ejercicio: Int!
    $fechaInicio: Date
    $fechaFin: Date
    $estado: String
  ) {
    asientosContables(filter: {
      ejercicio: {eq: $ejercicio}
      fecha: {gte: $fechaInicio, lte: $fechaFin}
      estado: {eq: $estado}
    }) {
      id
      ejercicio
      numeroAsiento
      fecha
      glosa
      tipoAsiento
      estado
      apuntes {
        id
        cuenta {
          id
          codigo
          nombre
        }
        debe
        haber
        concepto
      }
      fechaCreacion
    }
  }
`

// Query para obtener un asiento específico
export const GET_ASIENTO_CONTABLE = `
  query AsientoContable($id: UUID!) {
    asientoContable(id: $id) {
      id
      ejercicio
      numeroAsiento
      fecha
      glosa
      tipoAsiento
      estado
      apuntes {
        id
        cuenta {
          id
          codigo
          nombre
          tipo
        }
        debe
        haber
        concepto
        actividad {
          id
          nombre
        }
        observaciones
      }
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener apuntes de una cuenta
export const GET_APUNTES_CUENTA = `
  query ApuntesCuenta(
    $cuentaId: UUID!
    $ejercicio: Int
    $fechaInicio: Date
    $fechaFin: Date
  ) {
    apuntesContables(filter: {
      cuentaId: {eq: $cuentaId}
      ejercicio: {eq: $ejercicio}
      fecha: {gte: $fechaInicio, lte: $fechaFin}
    }) {
      id
      asiento {
        id
        numeroAsiento
        fecha
        glosa
      }
      debe
      haber
      concepto
      actividad {
        id
        nombre
      }
    }
  }
`

// Query para obtener balance contable
export const GET_BALANCE_CONTABLE = `
  query BalanceContable($ejercicio: Int!, $fechaFin: Date!) {
    balanceContable(ejercicio: $ejercicio, fechaFin: $fechaFin) {
      id
      ejercicio
      fechaGeneracion
      totalDebe
      totalHaber
      estaEquilibrado
      observaciones
    }
  }
`

// Query para obtener saldo de una cuenta
export const GET_SALDO_CUENTA = `
  query SaldoCuenta(
    $cuentaId: UUID!
    $fechaFin: Date
    $ejercicio: Int
  ) {
    saldoCuenta(
      cuentaId: $cuentaId
      fechaFin: $fechaFin
      ejercicio: $ejercicio
    )
  }
`

// Mutation para crear cuenta contable
export const CREATE_CUENTA_CONTABLE = `
  mutation CrearCuentaContable(
    $codigo: String!
    $nombre: String!
    $tipo: String!
    $nivel: Int!
    $padreId: UUID
    $esDotacion: Boolean
    $descripcion: String
  ) {
    crearCuentaContable(
      codigo: $codigo
      nombre: $nombre
      tipo: $tipo
      nivel: $nivel
      padreId: $padreId
      esDotacion: $esDotacion
      descripcion: $descripcion
    ) {
      id
      codigo
      nombre
      tipo
      nivel
    }
  }
`

// Mutation para crear asiento contable
export const CREATE_ASIENTO_CONTABLE = `
  mutation CrearAsientoContable(
    $ejercicio: Int!
    $numeroAsiento: Int!
    $fecha: Date!
    $glosa: String!
    $tipoAsiento: String!
    $observaciones: String
  ) {
    crearAsientoContable(
      ejercicio: $ejercicio
      numeroAsiento: $numeroAsiento
      fecha: $fecha
      glosa: $glosa
      tipoAsiento: $tipoAsiento
      observaciones: $observaciones
    ) {
      id
      numeroAsiento
      estado
    }
  }
`

// Mutation para crear apunte contable
export const CREATE_APUNTE_CONTABLE = `
  mutation CrearApunteContable(
    $asientoId: UUID!
    $cuentaId: UUID!
    $debe: Decimal
    $haber: Decimal
    $concepto: String!
    $actividadId: UUID
    $observaciones: String
  ) {
    crearApunteContable(
      asientoId: $asientoId
      cuentaId: $cuentaId
      debe: $debe
      haber: $haber
      concepto: $concepto
      actividadId: $actividadId
      observaciones: $observaciones
    ) {
      id
      debe
      haber
      concepto
    }
  }
`

// Mutation para confirmar asiento
export const CONFIRMAR_ASIENTO = `
  mutation ConfirmarAsiento($asientoId: UUID!) {
    confirmarAsiento(asientoId: $asientoId) {
      id
      estado
    }
  }
`

// Mutation para anular asiento
export const ANULAR_ASIENTO = `
  mutation AnularAsiento($asientoId: UUID!) {
    anularAsiento(asientoId: $asientoId) {
      id
      estado
    }
  }
`

// Mutation para generar balance
export const GENERAR_BALANCE = `
  mutation GenerarBalance($ejercicio: Int!, $fechaFin: Date!) {
    generarBalance(ejercicio: $ejercicio, fechaFin: $fechaFin) {
      id
      ejercicio
      totalDebe
      totalHaber
      estaEquilibrado
    }
  }
`
