// Queries y Mutations GraphQL para el módulo de Contabilidad (PCESFL 2013)

export const GET_PLAN_CUENTAS = `
  query PlanCuentas {
    cuentasContables {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      padreId
      permiteAsiento
      esDotacion
      activa
    }
  }
`

export const GET_SALDOS_CUENTAS = `
  query SaldosCuentas($ejercicio: Int!) {
    saldosCuentas(ejercicio: $ejercicio) {
      codigo
      saldo
    }
  }
`

export const GET_ASIENTOS_CONTABLES = `
  query AsientosContables {
    asientosContables {
      id
      ejercicio
      numeroAsiento
      glosa
      tipoAsiento
      estado
      observaciones
      fechaCreacion
    }
  }
`

export const GET_APUNTES_CONTABLES = `
  query ApuntesContables($asientoId: UUID) {
    apuntesContables(filter: { asientoId: { eq: $asientoId } }) {
      id
      asientoId
      cuentaId
      debe
      haber
      concepto
      actividadId
    }
  }
`

export const GET_BALANCE_SUMAS_SALDOS = `
  query BalanceSumasYSaldos($ejercicio: Int!, $fechaCorte: Date, $soloConSaldo: Boolean) {
    balanceSumasYSaldos(ejercicio: $ejercicio, fechaCorte: $fechaCorte, soloConSaldo: $soloConSaldo) {
      codigo
      nombre
      tipo
      totalDebe
      totalHaber
      saldo
    }
  }
`

export const CREATE_CUENTA_CONTABLE = `
  mutation CrearCuentaContable($input: CuentaContableCreateInput!) {
    crearCuentaContable(data: $input) {
      id
      codigo
      nombre
    }
  }
`

export const UPDATE_CUENTA_CONTABLE = `
  mutation ActualizarCuentaContable($input: CuentaContableUpdateInput!) {
    actualizarCuentaContable(data: $input) {
      id
      codigo
      nombre
      tipo
      nivel
      padreId
      descripcion
      permiteAsiento
      esDotacion
      activa
    }
  }
`

export const CUENTA_TIENE_APUNTES = `
  query CuentaTieneApuntes($cuentaId: UUID!) {
    cuentaTieneApuntesConfirmados(cuentaId: $cuentaId)
  }
`

export const CREATE_ASIENTO_CONTABLE = `
  mutation CrearAsientoContable($input: AsientoContableCreateInput!) {
    crearAsientoContable(data: $input) {
      id
      ejercicio
      numeroAsiento
      estado
    }
  }
`

export const CREATE_APUNTE_CONTABLE = `
  mutation CrearApunteContable($input: ApunteContableCreateInput!) {
    crearApunteContable(data: $input) {
      id
      debe
      haber
    }
  }
`

export const CONFIRMAR_ASIENTO = `
  mutation ConfirmarAsientoContable($asientoId: UUID!) {
    confirmarAsientoContable(asientoId: $asientoId)
  }
`

export const ANULAR_ASIENTO = `
  mutation AnularAsientoContable($asientoId: UUID!) {
    anularAsientoContable(asientoId: $asientoId)
  }
`

