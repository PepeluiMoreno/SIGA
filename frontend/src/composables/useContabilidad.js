import { ref, computed } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_PLAN_CUENTAS,
  GET_ASIENTOS_CONTABLES,
  GET_APUNTES_CUENTA,
  GET_BALANCE_CONTABLE,
  GET_SALDO_CUENTA,
  CREATE_CUENTA_CONTABLE,
  CREATE_ASIENTO_CONTABLE,
  CREATE_APUNTE_CONTABLE,
  CONFIRMAR_ASIENTO,
  ANULAR_ASIENTO,
  GENERAR_BALANCE,
} from '@/graphql/queries/contabilidad'

export function useContabilidad() {
  const { query, mutation, loading, error } = useGraphQL()
  
  const planCuentas = ref([])
  const asientos = ref([])
  const apuntes = ref([])
  const balances = ref([])
  const asientoActual = ref(null)
  const ejercicioActual = ref(new Date().getFullYear())

  // Obtener plan de cuentas
  const obtenerPlanCuentas = async (tipo = null) => {
    try {
      const data = await query(GET_PLAN_CUENTAS, { tipo })
      planCuentas.value = data.cuentasContables
      return data.cuentasContables
    } catch (err) {
      console.error('Error al obtener plan de cuentas:', err)
      throw err
    }
  }

  // Obtener asientos contables
  const obtenerAsientos = async (ejercicio, fechaInicio = null, fechaFin = null, estado = null) => {
    try {
      const data = await query(GET_ASIENTOS_CONTABLES, {
        ejercicio,
        fechaInicio,
        fechaFin,
        estado,
      })
      asientos.value = data.asientosContables
      return data.asientosContables
    } catch (err) {
      console.error('Error al obtener asientos:', err)
      throw err
    }
  }

  // Obtener apuntes de una cuenta
  const obtenerApuntes = async (cuentaId, ejercicio = null, fechaInicio = null, fechaFin = null) => {
    try {
      const data = await query(GET_APUNTES_CUENTA, {
        cuentaId,
        ejercicio,
        fechaInicio,
        fechaFin,
      })
      apuntes.value = data.apuntesContables
      return data.apuntesContables
    } catch (err) {
      console.error('Error al obtener apuntes:', err)
      throw err
    }
  }

  // Obtener balance contable
  const obtenerBalance = async (ejercicio, fechaFin) => {
    try {
      const data = await query(GET_BALANCE_CONTABLE, { ejercicio, fechaFin })
      return data.balanceContable
    } catch (err) {
      console.error('Error al obtener balance:', err)
      throw err
    }
  }

  // Obtener saldo de una cuenta
  const obtenerSaldoCuenta = async (cuentaId, fechaFin = null, ejercicio = null) => {
    try {
      const data = await query(GET_SALDO_CUENTA, {
        cuentaId,
        fechaFin,
        ejercicio,
      })
      return data.saldoCuenta
    } catch (err) {
      console.error('Error al obtener saldo de cuenta:', err)
      throw err
    }
  }

  // Crear cuenta contable
  const crearCuentaContable = async (payload) => {
    try {
      const data = await mutation(CREATE_CUENTA_CONTABLE, payload)
      planCuentas.value.push(data.crearCuentaContable)
      return data.crearCuentaContable
    } catch (err) {
      console.error('Error al crear cuenta contable:', err)
      throw err
    }
  }

  // Crear asiento contable
  const crearAsiento = async (payload) => {
    try {
      const data = await mutation(CREATE_ASIENTO_CONTABLE, payload)
      asientoActual.value = data.crearAsientoContable
      return data.crearAsientoContable
    } catch (err) {
      console.error('Error al crear asiento:', err)
      throw err
    }
  }

  // Crear apunte contable
  const crearApunte = async (payload) => {
    try {
      const data = await mutation(CREATE_APUNTE_CONTABLE, payload)
      if (asientoActual.value) {
        asientoActual.value.apuntes.push(data.crearApunteContable)
      }
      return data.crearApunteContable
    } catch (err) {
      console.error('Error al crear apunte:', err)
      throw err
    }
  }

  // Confirmar asiento
  const confirmarAsiento = async (asientoId) => {
    try {
      const data = await mutation(CONFIRMAR_ASIENTO, { asientoId })
      const index = asientos.value.findIndex(a => a.id === asientoId)
      if (index >= 0) {
        asientos.value[index].estado = 'CONFIRMADO'
      }
      return data.confirmarAsiento
    } catch (err) {
      console.error('Error al confirmar asiento:', err)
      throw err
    }
  }

  // Anular asiento
  const anularAsiento = async (asientoId) => {
    try {
      const data = await mutation(ANULAR_ASIENTO, { asientoId })
      const index = asientos.value.findIndex(a => a.id === asientoId)
      if (index >= 0) {
        asientos.value[index].estado = 'ANULADO'
      }
      return data.anularAsiento
    } catch (err) {
      console.error('Error al anular asiento:', err)
      throw err
    }
  }

  // Generar balance
  const generarBalance = async (ejercicio, fechaFin) => {
    try {
      const data = await mutation(GENERAR_BALANCE, { ejercicio, fechaFin })
      balances.value.push(data.generarBalance)
      return data.generarBalance
    } catch (err) {
      console.error('Error al generar balance:', err)
      throw err
    }
  }

  // Calcular totales del asiento actual
  const totalesAsientoActual = computed(() => {
    if (!asientoActual.value || !asientoActual.value.apuntes) {
      return { totalDebe: 0, totalHaber: 0, diferencia: 0 }
    }
    const totalDebe = asientoActual.value.apuntes.reduce((sum, a) => sum + parseFloat(a.debe || 0), 0)
    const totalHaber = asientoActual.value.apuntes.reduce((sum, a) => sum + parseFloat(a.haber || 0), 0)
    return {
      totalDebe,
      totalHaber,
      diferencia: totalDebe - totalHaber,
      estaCuadrado: totalDebe === totalHaber,
    }
  })

  // Obtener cuentas por tipo
  const cuentasPorTipo = computed(() => {
    const tipos = {}
    planCuentas.value.forEach(cuenta => {
      if (!tipos[cuenta.tipo]) {
        tipos[cuenta.tipo] = []
      }
      tipos[cuenta.tipo].push(cuenta)
    })
    return tipos
  })

  // Obtener asientos por estado
  const asientosPorEstado = computed(() => {
    const estados = {}
    asientos.value.forEach(asiento => {
      if (!estados[asiento.estado]) {
        estados[asiento.estado] = []
      }
      estados[asiento.estado].push(asiento)
    })
    return estados
  })

  return {
    planCuentas,
    asientos,
    apuntes,
    balances,
    asientoActual,
    ejercicioActual,
    loading,
    error,
    obtenerPlanCuentas,
    obtenerAsientos,
    obtenerApuntes,
    obtenerBalance,
    obtenerSaldoCuenta,
    crearCuentaContable,
    crearAsiento,
    crearApunte,
    confirmarAsiento,
    anularAsiento,
    generarBalance,
    totalesAsientoActual,
    cuentasPorTipo,
    asientosPorEstado,
  }
}
