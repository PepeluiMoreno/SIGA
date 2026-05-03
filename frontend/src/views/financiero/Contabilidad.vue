<template>
  <AppLayout title="Contabilidad" subtitle="Plan de cuentas, asientos contables y balances">
    <!-- Resumen de Contabilidad -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 rounded-lg shadow p-4 border border-blue-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">📋</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Cuentas Activas</p>
            <p class="text-xl font-bold text-blue-600">{{ planCuentas.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">📝</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Asientos Confirmados</p>
            <p class="text-xl font-bold text-purple-600">{{ asientosPorEstado['CONFIRMADO']?.length || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-yellow-50 rounded-lg shadow p-4 border border-yellow-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-yellow-100 flex items-center justify-center mr-3">
            <span class="text-lg">✏️</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Asientos en Borrador</p>
            <p class="text-xl font-bold text-yellow-600">{{ asientosPorEstado['BORRADOR']?.length || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">✓</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Ejercicio</p>
            <p class="text-xl font-bold text-green-600">{{ ejercicioActual }}</p>
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

    <!-- Tab: Plan de Cuentas -->
    <div v-if="activeTab === 'plan'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Plan de Cuentas (PCESFL 2013)</h3>
          <button
            @click="showFormularioCuenta = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            + Nueva Cuenta
          </button>
        </div>

        <!-- Filtro por tipo -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Filtrar por Tipo</label>
          <select
            v-model="filtroTipo"
            @change="cargarPlanCuentas"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option :value="null">-- Todos los tipos --</option>
            <option value="ACTIVO">Activo</option>
            <option value="PASIVO">Pasivo</option>
            <option value="PATRIMONIO">Patrimonio</option>
            <option value="INGRESO">Ingreso</option>
            <option value="GASTO">Gasto</option>
          </select>
        </div>

        <!-- Listado de cuentas -->
        <div v-if="planCuentas.length > 0" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Código</th>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Nombre</th>
                <th class="px-4 py-3 text-center font-semibold text-gray-900">Tipo</th>
                <th class="px-4 py-3 text-center font-semibold text-gray-900">Nivel</th>
                <th class="px-4 py-3 text-center font-semibold text-gray-900">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cuenta in planCuentas" :key="cuenta.id" class="border-b border-gray-200 hover:bg-gray-50">
                <td class="px-4 py-3 font-mono text-gray-900">{{ cuenta.codigo }}</td>
                <td class="px-4 py-3 text-gray-900">
                  <span :style="{ marginLeft: (cuenta.nivel - 1) * 20 + 'px' }">{{ cuenta.nombre }}</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    getTipoBadgeClass(cuenta.tipo)
                  ]">
                    {{ cuenta.tipo }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center text-gray-600">{{ cuenta.nivel }}</td>
                <td class="px-4 py-3 text-center">
                  <span v-if="cuenta.activa" class="text-green-600">✓ Activa</span>
                  <span v-else class="text-red-600">✗ Inactiva</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">No hay cuentas contables registradas</p>
        </div>
      </div>
    </div>

    <!-- Tab: Asientos Contables -->
    <div v-if="activeTab === 'asientos'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Asientos Contables</h3>
          <button
            @click="showFormularioAsiento = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            + Nuevo Asiento
          </button>
        </div>

        <!-- Filtros -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Ejercicio</label>
            <input
              v-model.number="ejercicioActual"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Estado</label>
            <select
              v-model="filtroEstado"
              @change="cargarAsientos"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option :value="null">-- Todos --</option>
              <option value="BORRADOR">Borrador</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="ANULADO">Anulado</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="cargarAsientos"
              class="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm font-medium"
            >
              Filtrar
            </button>
          </div>
        </div>

        <!-- Listado de asientos -->
        <div v-if="asientos.length > 0" class="space-y-4">
          <div
            v-for="asiento in asientos"
            :key="asiento.id"
            @click="seleccionarAsiento(asiento)"
            class="border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900">
                  Asiento #{{ asiento.numeroAsiento }} - {{ formatDate(asiento.fecha) }}
                </h4>
                <p class="text-sm text-gray-600 mt-1">{{ asiento.glosa }}</p>
                <div class="flex gap-4 mt-2 text-sm">
                  <span class="text-gray-600">Debe: <span class="font-semibold">{{ formatCurrency(asiento.totalDebe) }}</span></span>
                  <span class="text-gray-600">Haber: <span class="font-semibold">{{ formatCurrency(asiento.totalHaber) }}</span></span>
                </div>
              </div>
              <div class="text-right">
                <span :class="[
                  'px-3 py-1 rounded text-xs font-medium',
                  getEstadoBadgeClass(asiento.estado)
                ]">
                  {{ asiento.estado }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">No hay asientos contables registrados</p>
        </div>
      </div>
    </div>

    <!-- Tab: Libro Mayor -->
    <div v-if="activeTab === 'mayor'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">Libro Mayor</h3>

        <!-- Selector de cuenta -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Seleccionar Cuenta</label>
          <select
            v-model="cuentaSeleccionada"
            @change="cargarApuntes"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option :value="null">-- Selecciona una cuenta --</option>
            <option v-for="cuenta in planCuentas.filter(c => c.permiteAsiento)" :key="cuenta.id" :value="cuenta.id">
              {{ cuenta.codigo }} - {{ cuenta.nombre }}
            </option>
          </select>
        </div>

        <!-- Listado de apuntes -->
        <div v-if="apuntes.length > 0" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Fecha</th>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Asiento</th>
                <th class="px-4 py-3 text-left font-semibold text-gray-900">Concepto</th>
                <th class="px-4 py-3 text-right font-semibold text-gray-900">Debe</th>
                <th class="px-4 py-3 text-right font-semibold text-gray-900">Haber</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apunte in apuntes" :key="apunte.id" class="border-b border-gray-200 hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-900">{{ formatDate(apunte.asiento.fecha) }}</td>
                <td class="px-4 py-3 text-gray-900">{{ apunte.asiento.numeroAsiento }}</td>
                <td class="px-4 py-3 text-gray-900">{{ apunte.concepto }}</td>
                <td class="px-4 py-3 text-right font-semibold text-gray-900">
                  {{ apunte.debe > 0 ? formatCurrency(apunte.debe) : '-' }}
                </td>
                <td class="px-4 py-3 text-right font-semibold text-gray-900">
                  {{ apunte.haber > 0 ? formatCurrency(apunte.haber) : '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500">{{ cuentaSeleccionada ? 'No hay apuntes' : 'Selecciona una cuenta para ver el libro mayor' }}</p>
        </div>
      </div>
    </div>

    <!-- Tab: Balance -->
    <div v-if="activeTab === 'balance'" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Balance de Sumas y Saldos</h3>
          <button
            @click="generarBalance"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
          >
            Generar Balance
          </button>
        </div>

        <div class="text-center py-8">
          <p class="text-gray-500">Selecciona "Generar Balance" para crear un balance del ejercicio {{ ejercicioActual }}</p>
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
import { useContabilidad } from '@/composables/useContabilidad'

const {
  planCuentas,
  asientos,
  apuntes,
  ejercicioActual,
  loading,
  obtenerPlanCuentas,
  obtenerAsientos,
  obtenerApuntes,
  generarBalance,
  cuentasPorTipo,
  asientosPorEstado,
} = useContabilidad()

const activeTab = ref('plan')
const cuentaSeleccionada = ref(null)
const filtroTipo = ref(null)
const filtroEstado = ref(null)
const showFormularioCuenta = ref(false)
const showFormularioAsiento = ref(false)

const tabs = [
  { id: 'plan', name: 'Plan de Cuentas', icon: '📋' },
  { id: 'asientos', name: 'Asientos', icon: '📝' },
  { id: 'mayor', name: 'Libro Mayor', icon: '📖' },
  { id: 'balance', name: 'Balance', icon: '⚖️' },
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

const getTipoBadgeClass = (tipo) => {
  const classes = {
    ACTIVO: 'bg-blue-100 text-blue-800',
    PASIVO: 'bg-red-100 text-red-800',
    PATRIMONIO: 'bg-purple-100 text-purple-800',
    INGRESO: 'bg-green-100 text-green-800',
    GASTO: 'bg-orange-100 text-orange-800',
  }
  return classes[tipo] || 'bg-gray-100 text-gray-800'
}

const getEstadoBadgeClass = (estado) => {
  const classes = {
    BORRADOR: 'bg-yellow-100 text-yellow-800',
    CONFIRMADO: 'bg-green-100 text-green-800',
    ANULADO: 'bg-red-100 text-red-800',
  }
  return classes[estado] || 'bg-gray-100 text-gray-800'
}

const cargarPlanCuentas = async () => {
  await obtenerPlanCuentas(filtroTipo.value)
}

const cargarAsientos = async () => {
  await obtenerAsientos(ejercicioActual.value, null, null, filtroEstado.value)
}

const cargarApuntes = async () => {
  if (cuentaSeleccionada.value) {
    await obtenerApuntes(cuentaSeleccionada.value, ejercicioActual.value)
  }
}

const seleccionarAsiento = (asiento) => {
  // Aquí se podría abrir un modal con los detalles del asiento
  console.log('Asiento seleccionado:', asiento)
}

// Cargar datos al montar el componente
onMounted(async () => {
  await obtenerPlanCuentas()
  await obtenerAsientos(ejercicioActual.value)
})
</script>
