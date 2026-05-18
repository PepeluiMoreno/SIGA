// Queries y Mutations GraphQL para el módulo de Contabilidad (PCESFL 2013)

export const GET_PLAN_CUENTAS = `
  query PlanCuentas($tipo: String) {
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

export const GET_ASIENTOS_CONTABLES = `
  query AsientosContables($ejercicio: Int, $estado: String) {
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

export const GET_BALANCES_CONTABLES = `
  query BalancesContables($ejercicio: Int) {
    balancesContables {
      id
      ejercicio
      fechaGeneracion
      totalDebe
      totalHaber
      observaciones
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

export const GENERAR_BALANCE = `
  mutation GenerarBalanceContable($ejercicio: Int!, $fechaFin: Date) {
    generarBalanceContable(ejercicio: $ejercicio, fechaFin: $fechaFin)
  }
`
