import { ref } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_PLAN_CUENTAS,
  GET_ASIENTOS_CONTABLES,
  GET_BALANCES_CONTABLES,
  CREATE_CUENTA_CONTABLE,
  CREATE_ASIENTO_CONTABLE,
  CONFIRMAR_ASIENTO,
  ANULAR_ASIENTO,
  GENERAR_BALANCE,
} from '@/graphql/queries/contabilidad'

export function useContabilidad() {
  const { query, mutation, loading, error } = useGraphQL()

  const cuentasContables = ref([])
  const asientosContables = ref([])
  const balancesContables = ref([])

  const obtenerPlanCuentas = async (tipo = null) => {
    const data = await query(GET_PLAN_CUENTAS, { tipo })
    cuentasContables.value = (data.cuentasContables ?? []).sort((a, b) => a.codigo.localeCompare(b.codigo))
    return cuentasContables.value
  }

  const obtenerAsientos = async (ejercicio = null, estado = null) => {
    const data = await query(GET_ASIENTOS_CONTABLES, { ejercicio, estado })
    asientosContables.value = data.asientosContables ?? []
    return asientosContables.value
  }

  const obtenerBalances = async (ejercicio = null) => {
    const data = await query(GET_BALANCES_CONTABLES, { ejercicio })
    balancesContables.value = data.balancesContables ?? []
    return balancesContables.value
  }

  const crearCuentaContable = async (payload) => {
    const data = await mutation(CREATE_CUENTA_CONTABLE, { input: payload })
    return data.crearCuentaContable
  }

  const crearAsiento = async (payload) => {
    const data = await mutation(CREATE_ASIENTO_CONTABLE, { input: payload })
    const nuevo = data.crearAsientoContable
    asientosContables.value.unshift(nuevo)
    return nuevo
  }

  const confirmarAsientoContable = async (asientoId) => {
    const data = await mutation(CONFIRMAR_ASIENTO, { asientoId })
    const idx = asientosContables.value.findIndex(a => a.id === asientoId)
    if (idx >= 0) asientosContables.value[idx].estado = 'CONFIRMADO'
    return data.confirmarAsientoContable
  }

  const anularAsientoContable = async (asientoId) => {
    const data = await mutation(ANULAR_ASIENTO, { asientoId })
    const idx = asientosContables.value.findIndex(a => a.id === asientoId)
    if (idx >= 0) asientosContables.value[idx].estado = 'ANULADO'
    return data.anularAsientoContable
  }

  const generarBalanceContable = async (ejercicio, fechaFin = null) => {
    const data = await mutation(GENERAR_BALANCE, { ejercicio, fechaFin })
    return data.generarBalanceContable
  }

  return {
    cuentasContables,
    asientosContables,
    balancesContables,
    loading,
    error,
    obtenerPlanCuentas,
    obtenerAsientos,
    obtenerBalances,
    crearCuentaContable,
    crearAsiento,
    confirmarAsientoContable,
    anularAsientoContable,
    generarBalanceContable,
  }
}
