<template>
  <AppLayout title="Tesorería" subtitle="Gestión de cuentas bancarias, movimientos y conciliaciones">
    <!-- Resumen de Tesorería -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">💰</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Saldo Total</p>
            <p class="text-xl font-bold text-green-600">{{ formatCurrency(saldoTotal) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-blue-50 rounded-lg shadow p-4 border border-blue-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">📊</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Cuentas Activas</p>
            <p class="text-xl font-bold text-blue-600">{{ cuentasBancarias.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">✅</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Movimientos Conciliados</p>
            <p class="text-xl font-bold text-purple-600">{{ calcularTotales.totalConciliados }}</p>
          </div>
        </div>
      </div>

      <div class="bg-yellow-50 rounded-lg shadow p-4 border border-yellow-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-yellow-100 flex items-center justify-center mr-3">
            <span class="text-lg">⏳</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Por Conciliar</p>
            <p class="text-xl font-bold text-yellow-600">{{ calcularTotales.totalNoConciliados }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs de navegación -->
    <div class="mb-6">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </nav>
      </div>
    </div>

    <!-- Tab: Cuentas Bancarias -->
    <div v-if="activeTab === 'cuentas'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Cuentas Bancarias</h3>
          <button
            @click="showFormularioCuenta = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            + Nueva Cuenta
          </button>
        </div>

        <!-- Listado de cuentas -->
        <div v-if="cuentasBancarias.length > 0" class="space-y-4">
          <div
            v-for="cuenta in cuentasBancarias"
            :key="cuenta.id"
            @click="seleccionarCuenta(cuenta)"
            class="border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900">{{ cuenta.nombre }}</h4>
                <p class="text-sm text-gray-500 mt-1">{{ formatearIban(cuenta.iban) }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ cuenta.bancoNombre }}</p>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold text-gray-900">{{ formatCurrency(cuenta.saldoActual) }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  <span v-if="cuenta.activa" class="text-green-600">● Activa</span>
                  <span v-else class="text-red-600">● Inactiva</span>
                </p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">No hay cuentas bancarias registradas</p>
        </div>
      </div>
    </div>

    <!-- Tab: Movimientos -->
    <div v-if="activeTab === 'movimientos'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Movimientos de Tesorería</h3>
          <button
            v-if="cuentaSeleccionada"
            @click="showFormularioMovimiento = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            + Nuevo Movimiento
          </button>
        </div>

        <!-- Selector de cuenta -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Seleccionar Cuenta</label>
          <select
            v-model="cuentaSeleccionada"
            @change="cargarMovimientos"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option :value="null">-- Selecciona una cuenta --</option>
            <option v-for="cuenta in cuentasBancarias" :key="cuenta.id" :value="cuenta.id">
              {{ cuenta.nombre }} ({{ formatCurrency(cuenta.saldoActual) }})
            </option>
          </select>
        </div>

        <!-- Listado de movimientos -->
        <div v-if="movimientos.length > 0" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Fecha</th>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Concepto</th>
                <th class="px-4 py-3 text-right font-semibold text-gray-900">Importe</th>
                <th class="px-4 py-3 text-center font-semibold text-gray-900">Tipo</th>
                <th class="px-4 py-3 text-center font-semibold text-gray-900">Conciliado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="movimiento in movimientos" :key="movimiento.id" class="border-b border-gray-200 hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-900">{{ formatDate(movimiento.fecha) }}</td>
                <td class="px-4 py-3 text-gray-900">{{ movimiento.concepto }}</td>
                <td class="px-4 py-3 text-right font-semibold" :class="movimiento.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'">
                  {{ movimiento.tipo === 'INGRESO' ? '+' : '-' }}{{ formatCurrency(movimiento.importe) }}
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    movimiento.tipo === 'INGRESO' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ movimiento.tipo }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span v-if="movimiento.conciliado" class="text-green-600">✓</span>
                  <span v-else class="text-gray-400">○</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">{{ cuentaSeleccionada ? 'No hay movimientos' : 'Selecciona una cuenta para ver movimientos' }}</p>
        </div>
      </div>
    </div>

    <!-- Tab: Conciliaciones -->
    <div v-if="activeTab === 'conciliaciones'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Conciliaciones Bancarias</h3>
          <button
            v-if="cuentaSeleccionada"
            @click="showFormularioConciliacion = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            + Nueva Conciliación
          </button>
        </div>

        <!-- Selector de cuenta -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Seleccionar Cuenta</label>
          <select
            v-model="cuentaSeleccionada"
            @change="cargarConciliaciones"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option :value="null">-- Selecciona una cuenta --</option>
            <option v-for="cuenta in cuentasBancarias" :key="cuenta.id" :value="cuenta.id">
              {{ cuenta.nombre }}
            </option>
          </select>
        </div>

        <!-- Listado de conciliaciones -->
        <div v-if="conciliaciones.length > 0" class="space-y-4">
          <div
            v-for="conciliacion in conciliaciones"
            :key="conciliacion.id"
            class="border rounded-lg p-4"
            :class="conciliacion.conciliado ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900">
                  {{ formatDate(conciliacion.fechaInicio) }} - {{ formatDate(conciliacion.fechaFin) }}
                </h4>
                <div class="grid grid-cols-2 gap-4 mt-2 text-sm">
                  <div>
                    <p class="text-gray-600">Saldo Extracto</p>
                    <p class="font-semibold text-gray-900">{{ formatCurrency(conciliacion.saldoFinalExtracto) }}</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Saldo Sistema</p>
                    <p class="font-semibold text-gray-900">{{ formatCurrency(conciliacion.saldoFinalSistema) }}</p>
                  </div>
                </div>
              </div>
              <div class="text-right">
                <p v-if="conciliacion.diferencia === 0" class="text-lg font-bold text-green-600">✓ Conciliada</p>
                <p v-else class="text-lg font-bold text-red-600">Diferencia: {{ formatCurrency(conciliacion.diferencia) }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">{{ cuentaSeleccionada ? 'No hay conciliaciones' : 'Selecciona una cuenta para ver conciliaciones' }}</p>
        </div>
      </div>
    </div>

    <!-- Spinner de carga -->
    <LoadSpinner v-if="loading" />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { useTesoreria } from '@/composables/useTesoreria'

const { 
  cuentasBancarias, 
  movimientos, 
  conciliaciones,
  loading,
  obtenerCuentasBancarias,
  obtenerMovimientos,
  obtenerConciliaciones,
  calcularTotales,
  saldoTotal,
} = useTesoreria()

const activeTab = ref('cuentas')
const cuentaSeleccionada = ref(null)
const showFormularioCuenta = ref(false)
const showFormularioMovimiento = ref(false)
const showFormularioConciliacion = ref(false)

const tabs = [
  { id: 'cuentas', name: 'Cuentas Bancarias', icon: '🏦' },
  { id: 'movimientos', name: 'Movimientos', icon: '💸' },
  { id: 'conciliaciones', name: 'Conciliaciones', icon: '✓' },
]

// Funciones de utilidad
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('es-ES').format(new Date(date))
}

const formatearIban = (iban) => {
  return iban.slice(0, 4) + ' **** **** **** ' + iban.slice(-4)
}

const seleccionarCuenta = (cuenta) => {
  cuentaSeleccionada.value = cuenta.id
  activeTab.value = 'movimientos'
  cargarMovimientos()
}

const cargarMovimientos = async () => {
  if (cuentaSeleccionada.value) {
    await obtenerMovimientos(cuentaSeleccionada.value)
  }
}

const cargarConciliaciones = async () => {
  if (cuentaSeleccionada.value) {
    await obtenerConciliaciones(cuentaSeleccionada.value)
  }
}

// Cargar datos al montar el componente
onMounted(async () => {
  await obtenerCuentasBancarias()
})
</script>
