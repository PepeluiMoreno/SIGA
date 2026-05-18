import { ref, computed } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_CUENTAS_BANCARIAS,
  GET_APUNTES_CAJA,
  GET_CONCILIACIONES_BANCARIAS,
  CREATE_CUENTA_BANCARIA,
  REGISTRAR_APUNTE_CAJA,
  MARCAR_APUNTE_CONCILIADO,
  CREATE_CONCILIACION_BANCARIA,
  CONFIRMAR_CONCILIACION,
} from '@/graphql/queries/tesoreria'

export function useTesoreria() {
  const { query, mutation, loading, error } = useGraphQL()

  const cuentasBancarias = ref([])
  const apuntesCaja = ref([])
  const conciliaciones = ref([])

  const obtenerCuentasBancarias = async () => {
    const data = await query(GET_CUENTAS_BANCARIAS)
    cuentasBancarias.value = data.cuentasBancarias ?? []
    return cuentasBancarias.value
  }

  const obtenerApuntesCaja = async (cuentaId, opciones = {}) => {
    const data = await query(GET_APUNTES_CAJA, { cuentaId, ...opciones })
    apuntesCaja.value = data.apuntesCaja ?? []
    return apuntesCaja.value
  }

  const obtenerConciliaciones = async (cuentaId) => {
    const data = await query(GET_CONCILIACIONES_BANCARIAS, { cuentaId })
    conciliaciones.value = data.conciliacionesBancarias ?? []
    return conciliaciones.value
  }

  const crearCuentaBancaria = async (payload) => {
    const data = await mutation(CREATE_CUENTA_BANCARIA, { input: payload })
    const nueva = data.crearCuentaBancaria
    cuentasBancarias.value.unshift(nueva)
    return nueva
  }

  const registrarApunte = async (payload) => {
    const data = await mutation(REGISTRAR_APUNTE_CAJA, payload)
    return data.registrarApunteCaja
  }

  const marcarApunteConciliado = async (apunteId) => {
    const data = await mutation(MARCAR_APUNTE_CONCILIADO, { apunteId })
    const apunte = apuntesCaja.value.find(a => a.id === apunteId)
    if (apunte) apunte.conciliado = true
    return data.marcarApunteConciliado
  }

  const crearConciliacion = async (payload) => {
    const data = await mutation(CREATE_CONCILIACION_BANCARIA, { input: payload })
    const nueva = data.crearConciliacionBancaria
    conciliaciones.value.unshift(nueva)
    return nueva
  }

  const confirmarConciliacionPeriodo = async (conciliacionId) => {
    const data = await mutation(CONFIRMAR_CONCILIACION, { conciliacionId })
    const conc = conciliaciones.value.find(c => c.id === conciliacionId)
    if (conc) conc.conciliado = true
    return data.confirmarConciliacionPeriodo
  }

  const saldoTotal = computed(() =>
    cuentasBancarias.value.reduce((sum, c) => sum + parseFloat(c.saldoActual ?? 0), 0)
  )

  const calcularTotales = computed(() => ({
    totalIngresos: apuntesCaja.value
      .filter(m => m.tipo === 'INGRESO')
      .reduce((s, m) => s + parseFloat(m.importe), 0),
    totalGastos: apuntesCaja.value
      .filter(m => m.tipo === 'GASTO')
      .reduce((s, m) => s + parseFloat(m.importe), 0),
    totalConciliados: apuntesCaja.value.filter(m => m.conciliado).length,
    totalNoConciliados: apuntesCaja.value.filter(m => !m.conciliado).length,
  }))

  return {
    cuentasBancarias,
    apuntesCaja,
    conciliaciones,
    loading,
    error,
    obtenerCuentasBancarias,
    obtenerApuntesCaja,
    obtenerConciliaciones,
    crearCuentaBancaria,
    registrarApunte,
    marcarApunteConciliado,
    crearConciliacion,
    confirmarConciliacionPeriodo,
    saldoTotal,
    calcularTotales,
  }
}
