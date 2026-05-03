import { ref, computed } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_CUENTAS_BANCARIAS,
  GET_MOVIMIENTOS_TESORERIA,
  GET_MOVIMIENTOS_NO_CONCILIADOS,
  GET_CONCILIACIONES_BANCARIAS,
  CREATE_CUENTA_BANCARIA,
  CREATE_MOVIMIENTO_TESORERIA,
  CREATE_CONCILIACION_BANCARIA,
  CONFIRMAR_CONCILIACION,
} from '@/graphql/queries/tesoreria'

export function useTesoreria() {
  const { query, mutation, loading, error } = useGraphQL()
  
  const cuentasBancarias = ref([])
  const movimientos = ref([])
  const conciliaciones = ref([])
  const cuentaSeleccionada = ref(null)

  // Obtener todas las cuentas bancarias
  const obtenerCuentasBancarias = async () => {
    try {
      const data = await query(GET_CUENTAS_BANCARIAS)
      cuentasBancarias.value = data.cuentasBancarias
      return data.cuentasBancarias
    } catch (err) {
      console.error('Error al obtener cuentas bancarias:', err)
      throw err
    }
  }

  // Obtener movimientos de una cuenta
  const obtenerMovimientos = async (cuentaId, fechaInicio = null, fechaFin = null) => {
    try {
      const data = await query(GET_MOVIMIENTOS_TESORERIA, {
        cuentaId,
        fechaInicio,
        fechaFin,
      })
      movimientos.value = data.movimientosTesoreria
      return data.movimientosTesoreria
    } catch (err) {
      console.error('Error al obtener movimientos:', err)
      throw err
    }
  }

  // Obtener movimientos no conciliados
  const obtenerMovimientosNoConciliados = async (cuentaId) => {
    try {
      const data = await query(GET_MOVIMIENTOS_NO_CONCILIADOS, { cuentaId })
      return data.movimientosTesoreria
    } catch (err) {
      console.error('Error al obtener movimientos no conciliados:', err)
      throw err
    }
  }

  // Obtener conciliaciones de una cuenta
  const obtenerConciliaciones = async (cuentaId) => {
    try {
      const data = await query(GET_CONCILIACIONES_BANCARIAS, { cuentaId })
      conciliaciones.value = data.conciliacionesBancarias
      return data.conciliacionesBancarias
    } catch (err) {
      console.error('Error al obtener conciliaciones:', err)
      throw err
    }
  }

  // Crear una nueva cuenta bancaria
  const crearCuentaBancaria = async (payload) => {
    try {
      const data = await mutation(CREATE_CUENTA_BANCARIA, payload)
      cuentasBancarias.value.push(data.crearCuentaBancaria)
      return data.crearCuentaBancaria
    } catch (err) {
      console.error('Error al crear cuenta bancaria:', err)
      throw err
    }
  }

  // Registrar un movimiento
  const registrarMovimiento = async (payload) => {
    try {
      const data = await mutation(CREATE_MOVIMIENTO_TESORERIA, payload)
      movimientos.value.push(data.crearMovimientoTesoreria)
      return data.crearMovimientoTesoreria
    } catch (err) {
      console.error('Error al registrar movimiento:', err)
      throw err
    }
  }

  // Crear conciliación bancaria
  const crearConciliacion = async (payload) => {
    try {
      const data = await mutation(CREATE_CONCILIACION_BANCARIA, payload)
      conciliaciones.value.push(data.crearConciliacionBancaria)
      return data.crearConciliacionBancaria
    } catch (err) {
      console.error('Error al crear conciliación:', err)
      throw err
    }
  }

  // Confirmar conciliación
  const confirmarConciliacion = async (conciliacionId) => {
    try {
      const data = await mutation(CONFIRMAR_CONCILIACION, { conciliacionId })
      const index = conciliaciones.value.findIndex(c => c.id === conciliacionId)
      if (index >= 0) {
        conciliaciones.value[index] = data.confirmarConciliacion
      }
      return data.confirmarConciliacion
    } catch (err) {
      console.error('Error al confirmar conciliación:', err)
      throw err
    }
  }

  // Calcular totales
  const calcularTotales = computed(() => {
    return {
      totalIngresos: movimientos.value
        .filter(m => m.tipo === 'INGRESO')
        .reduce((sum, m) => sum + parseFloat(m.importe), 0),
      totalGastos: movimientos.value
        .filter(m => m.tipo === 'GASTO')
        .reduce((sum, m) => sum + parseFloat(m.importe), 0),
      totalConciliados: movimientos.value
        .filter(m => m.conciliado)
        .length,
      totalNoConciliados: movimientos.value
        .filter(m => !m.conciliado)
        .length,
    }
  })

  // Obtener saldo total de todas las cuentas
  const saldoTotal = computed(() => {
    return cuentasBancarias.value.reduce((sum, cuenta) => sum + parseFloat(cuenta.saldoActual), 0)
  })

  return {
    cuentasBancarias,
    movimientos,
    conciliaciones,
    cuentaSeleccionada,
    loading,
    error,
    obtenerCuentasBancarias,
    obtenerMovimientos,
    obtenerMovimientosNoConciliados,
    obtenerConciliaciones,
    crearCuentaBancaria,
    registrarMovimiento,
    crearConciliacion,
    confirmarConciliacion,
    calcularTotales,
    saldoTotal,
  }
}
