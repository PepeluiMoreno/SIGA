import { ref } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_PLAN_CUENTAS,
  GET_SALDOS_CUENTAS,
  GET_ASIENTOS_CONTABLES,
  GET_BALANCE_SUMAS_SALDOS,
  CREATE_CUENTA_CONTABLE,
  UPDATE_CUENTA_CONTABLE,
  CUENTA_TIENE_APUNTES,
  CREATE_ASIENTO_CONTABLE,
  CONFIRMAR_ASIENTO,
  ANULAR_ASIENTO,
} from '@/graphql/queries/contabilidad'

export function useContabilidad() {
  const { query, mutation, loading, error } = useGraphQL()

  const cuentasContables = ref([])
  const asientosContables = ref([])
  const lineasBalanceSumasSaldos = ref([])  // detalle por cuenta
  const saldosCuentas = ref({})  // { codigo: saldo }

  const normalizarTipo = (t) => t ? t.replace(/^TipoCuentaContable\./, '') : t

  const obtenerPlanCuentas = async () => {
    const data = await query(GET_PLAN_CUENTAS)
    cuentasContables.value = (data.cuentasContables ?? [])
      .map(c => ({ ...c, tipo: normalizarTipo(c.tipo) }))
      .sort((a, b) => a.codigo.localeCompare(b.codigo))
    return cuentasContables.value
  }

  const obtenerAsientos = async () => {
    const data = await query(GET_ASIENTOS_CONTABLES)
    asientosContables.value = data.asientosContables ?? []
    return asientosContables.value
  }

  const obtenerSaldosCuentas = async (ejercicio) => {
    const data = await query(GET_SALDOS_CUENTAS, { ejercicio })
    const dict = {}
    for (const s of (data.saldosCuentas ?? [])) {
      dict[s.codigo] = s.saldo
    }
    saldosCuentas.value = dict
    return dict
  }

  const calcularBalanceSumasYSaldos = async (ejercicio, fechaCorte = null, soloConSaldo = true) => {
    const data = await query(GET_BALANCE_SUMAS_SALDOS, {
      ejercicio,
      fechaCorte,
      soloConSaldo,
    })
    lineasBalanceSumasSaldos.value = data.balanceSumasYSaldos ?? []
    return lineasBalanceSumasSaldos.value
  }

  const crearCuentaContable = async (payload) => {
    const data = await mutation(CREATE_CUENTA_CONTABLE, { input: payload })
    return data.crearCuentaContable
  }

  const actualizarCuentaContable = async (payload) => {
    const data = await mutation(UPDATE_CUENTA_CONTABLE, { input: payload })
    return data.actualizarCuentaContable
  }

  const cuentaTieneApuntesConfirmados = async (cuentaId) => {
    const data = await query(CUENTA_TIENE_APUNTES, { cuentaId })
    return !!data.cuentaTieneApuntesConfirmados
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

  return {
    cuentasContables,
    asientosContables,
    lineasBalanceSumasSaldos,
    saldosCuentas,
    loading,
    error,
    obtenerPlanCuentas,
    obtenerSaldosCuentas,
    obtenerAsientos,
    calcularBalanceSumasYSaldos,
    crearCuentaContable,
    actualizarCuentaContable,
    cuentaTieneApuntesConfirmados,
    crearAsiento,
    confirmarAsientoContable,
    anularAsientoContable,
  }
}
