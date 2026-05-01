<template>
  <AppLayout title="Gestión Económico-Financiera" subtitle="Recaudación, presupuestos y control de gastos">
    <!-- Resumen financiero -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">💰</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Ingresos del mes</p>
            <p class="text-xl font-bold text-green-600">{{ formatCurrency(resumen.ingresosMes) }}</p>
          </div>
        </div>
      </div>
      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">📋</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Cuotas cobradas</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.cuotasCobradas }}</p>
          </div>
        </div>
      </div>
      <div class="bg-yellow-50 rounded-lg shadow p-4 border border-yellow-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-yellow-100 flex items-center justify-center mr-3">
            <span class="text-lg">⏳</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Cuotas pendientes</p>
            <p class="text-xl font-bold text-yellow-600">{{ resumen.cuotasPendientes }}</p>
          </div>
        </div>
      </div>
      <div class="bg-blue-50 rounded-lg shadow p-4 border border-blue-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">📊</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Presupuesto ejecutado</p>
            <p class="text-xl font-bold text-blue-600">{{ resumen.presupuestoEjecutado }}%</p>
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

    <!-- Contenido de tabs -->

    <!-- Tab: Control Presupuestario -->
    <div v-if="activeTab === 'presupuesto'" class="space-y-6">
      <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Presupuesto Anual 2025</h3>
          <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm">
            Editar Presupuesto
          </button>
        </div>

        <!-- Partidas presupuestarias -->
        <div class="space-y-4">
          <div v-for="partida in partidasPresupuesto" :key="partida.id" class="border border-gray-200 rounded-lg p-4 bg-white">
            <div class="flex justify-between items-center mb-2">
              <div class="flex items-center">
                <span class="mr-2">{{ partida.icono }}</span>
                <span class="font-medium text-gray-900">{{ partida.nombre }}</span>
              </div>
              <div class="text-right">
                <span class="text-sm text-gray-500">{{ formatCurrency(partida.ejecutado) }} / {{ formatCurrency(partida.presupuestado) }}</span>
              </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div
                :class="getProgressClass(partida.porcentaje)"
                class="h-3 rounded-full transition-all duration-300"
                :style="{ width: Math.min(partida.porcentaje, 100) + '%' }"
              ></div>
            </div>
            <div class="flex justify-between mt-1 text-xs text-gray-500">
              <span>{{ partida.porcentaje }}% ejecutado</span>
              <span>Restante: {{ formatCurrency(partida.presupuestado - partida.ejecutado) }}</span>
            </div>
          </div>
        </div>

        <!-- Resumen totales -->
        <div class="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-sm text-gray-500">Total Presupuestado</p>
            <p class="text-xl font-bold text-gray-900">{{ formatCurrency(totalPresupuestado) }}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-500">Total Ejecutado</p>
            <p class="text-xl font-bold text-purple-600">{{ formatCurrency(totalEjecutado) }}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-500">Disponible</p>
            <p class="text-xl font-bold text-green-600">{{ formatCurrency(totalPresupuestado - totalEjecutado) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Gestión de Cobros -->
    <div v-if="activeTab === 'cobros'" class="space-y-6">
      <!-- Filtros y búsqueda -->
      <div class="bg-gray-50 p-4 rounded-lg shadow border border-gray-200">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex-1">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar transacciones..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                @input="onSearch"
              />
              <div class="absolute left-3 top-2.5">
                <span>🔍</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="showFilters = !showFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Filtros
            </button>
            <button @click="generarRemesa" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              Generar Remesa SEPA
            </button>
            <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              + Nueva Transacción
            </button>
          </div>
        </div>

        <!-- Filtros avanzados -->
        <div v-if="showFilters" class="mt-4 p-4 border border-gray-200 rounded-lg bg-white">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select v-model="filters.tipo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Todos</option>
                <option value="CUOTA">Cuota</option>
                <option value="DONACION">Donación</option>
                <option value="GASTO">Gasto</option>
                <option value="SUBVENCION">Subvención</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
              <select v-model="filters.estado" class="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Todos</option>
                <option value="COBRADA">Cobrada</option>
                <option value="PENDIENTE">Pendiente</option>
                <option value="DEVUELTA">Devuelta</option>
                <option value="ANULADA">Anulada</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Desde</label>
              <input type="date" v-model="filters.fechaDesde" class="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Hasta</label>
              <input type="date" v-model="filters.fechaHasta" class="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p class="mt-2 text-gray-600">Cargando transacciones...</p>
      </div>

      <!-- Tabla de transacciones -->
      <div v-else class="bg-gray-50 rounded-lg shadow overflow-hidden border border-gray-200">
        <div v-if="transacciones.length === 0" class="text-center py-12">
          <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
            <span class="text-4xl">💳</span>
          </div>
          <h3 class="text-sm font-medium text-gray-900">No hay transacciones</h3>
          <p class="text-sm text-gray-500 mt-1">No se encontraron transacciones con los filtros seleccionados.</p>
        </div>

        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Concepto</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Miembro</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Importe</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="transaccion in transacciones" :key="transaccion.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(transaccion.fecha) }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900">{{ transaccion.concepto }}</div>
                <div v-if="transaccion.referencia" class="text-xs text-gray-500">Ref: {{ transaccion.referencia }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ transaccion.miembro }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getTipoClass(transaccion.tipo)">{{ transaccion.tipo }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getEstadoClass(transaccion.estado)">{{ transaccion.estado }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <span :class="transaccion.tipo === 'GASTO' ? 'text-red-600' : 'text-green-600'" class="font-medium">
                  {{ transaccion.tipo === 'GASTO' ? '-' : '+' }}{{ formatCurrency(transaccion.importe) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button @click="verDetalle(transaccion)" class="text-purple-600 hover:text-purple-800 mr-2">Ver</button>
                <button v-if="transaccion.estado === 'PENDIENTE'" @click="marcarCobrada(transaccion)" class="text-green-600 hover:text-green-800">
                  Cobrar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: Plataformas de Cobro -->
    <div v-if="activeTab === 'plataformas'" class="space-y-6">
      <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Plataformas y Métodos de Pago</h3>
          <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm">
            + Añadir Plataforma
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Cuenta Bancaria Principal -->
          <div v-for="plataforma in plataformasCobro" :key="plataforma.id"
               class="border rounded-lg p-4 hover:shadow-md transition-shadow"
               :class="plataforma.activa ? 'border-green-200 bg-white' : 'border-gray-200 bg-gray-50'">
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center">
                <span class="text-2xl mr-3">{{ plataforma.icono }}</span>
                <div>
                  <h4 class="font-medium text-gray-900">{{ plataforma.nombre }}</h4>
                  <p class="text-xs text-gray-500">{{ plataforma.tipo }}</p>
                </div>
              </div>
              <span :class="plataforma.activa ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
                    class="text-xs px-2 py-1 rounded-full">
                {{ plataforma.activa ? 'Activa' : 'Inactiva' }}
              </span>
            </div>

            <div class="space-y-2 text-sm text-gray-600">
              <div v-if="plataforma.identificador" class="flex items-center">
                <span class="text-gray-400 mr-2">ID:</span>
                <span class="font-mono text-xs">{{ plataforma.identificador }}</span>
              </div>
              <div v-if="plataforma.saldo !== undefined" class="flex items-center">
                <span class="text-gray-400 mr-2">Saldo:</span>
                <span class="font-medium text-green-600">{{ formatCurrency(plataforma.saldo) }}</span>
              </div>
              <div v-if="plataforma.ultimaActividad" class="flex items-center">
                <span class="text-gray-400 mr-2">Última actividad:</span>
                <span>{{ plataforma.ultimaActividad }}</span>
              </div>
            </div>

            <div class="flex gap-2 mt-4 pt-3 border-t border-gray-100">
              <button @click="configurarPlataforma(plataforma)" class="text-sm text-purple-600 hover:text-purple-800">
                Configurar
              </button>
              <button @click="verMovimientos(plataforma)" class="text-sm text-gray-600 hover:text-gray-800">
                Ver movimientos
              </button>
            </div>
          </div>
        </div>

        <!-- Información de integración -->
        <div class="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-lg">
          <div class="flex items-start">
            <span class="text-blue-500 mr-3">ℹ️</span>
            <div class="text-sm text-blue-800">
              <p class="font-medium mb-1">Integración con plataformas de pago</p>
              <p class="text-blue-700">Conecta tus cuentas de PayPal, Patreon o Bizum para sincronizar automáticamente los pagos recibidos. La sincronización se realiza cada 24 horas.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Tesorería -->
    <div v-if="activeTab === 'tesoreria'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Saldos de cuentas -->
        <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Saldos de Cuentas</h3>
          <div class="space-y-4">
            <div v-for="cuenta in cuentasTesoreria" :key="cuenta.id" class="flex justify-between items-center p-3 bg-white rounded-lg border border-gray-100">
              <div class="flex items-center">
                <span class="text-xl mr-3">{{ cuenta.icono }}</span>
                <div>
                  <p class="font-medium text-gray-900">{{ cuenta.nombre }}</p>
                  <p class="text-xs text-gray-500">{{ cuenta.entidad }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-bold" :class="cuenta.saldo >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ formatCurrency(cuenta.saldo) }}
                </p>
                <p class="text-xs text-gray-500">{{ cuenta.ultimaActualizacion }}</p>
              </div>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
            <span class="font-medium text-gray-700">Total disponible</span>
            <span class="text-xl font-bold text-green-600">{{ formatCurrency(totalTesoreria) }}</span>
          </div>
        </div>

        <!-- Flujo de caja -->
        <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Flujo de Caja - Últimos 6 meses</h3>
          <div class="space-y-3">
            <div v-for="mes in flujoCaja" :key="mes.mes" class="flex items-center">
              <span class="w-20 text-sm text-gray-500">{{ mes.mes }}</span>
              <div class="flex-1 flex items-center gap-2">
                <div class="w-20 text-right text-sm text-green-600">+{{ formatCurrency(mes.ingresos) }}</div>
                <div class="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden flex">
                  <div class="bg-green-400 h-full" :style="{ width: (mes.ingresos / maxFlujo * 50) + '%' }"></div>
                  <div class="bg-red-400 h-full" :style="{ width: (mes.gastos / maxFlujo * 50) + '%' }"></div>
                </div>
                <div class="w-20 text-left text-sm text-red-600">-{{ formatCurrency(mes.gastos) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Remesas SEPA -->
      <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Remesas SEPA Generadas</h3>
          <button @click="generarRemesa" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
            + Nueva Remesa
          </button>
        </div>
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Referencia</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Recibos</th>
              <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Importe</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="remesa in remesasSEPA" :key="remesa.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm">{{ formatDate(remesa.fechaCreacion) }}</td>
              <td class="px-4 py-3 text-sm font-mono">{{ remesa.referencia }}</td>
              <td class="px-4 py-3 text-sm">{{ remesa.numOrdenes }} recibos</td>
              <td class="px-4 py-3 text-sm text-right font-medium">{{ formatCurrency(remesa.importeTotal) }}</td>
              <td class="px-4 py-3">
                <span :class="getRemesaEstadoClass(remesa.estado?.nombre)" class="text-xs px-2 py-1 rounded-full">
                  {{ remesa.estado?.nombre }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm">
                <button class="text-purple-600 hover:text-purple-800 mr-2">Descargar</button>
                <button class="text-gray-600 hover:text-gray-800">Ver detalle</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_CUOTAS_ANUALES, GET_DONACIONES, GET_REMESAS } from '@/graphql/queries/financiero.js'

const loading = ref(false)
const activeTab = ref('cobros')
const cuotas = ref([])
const donaciones = ref([])
const remesasSEPA = ref([])
const searchQuery = ref('')
const showFilters = ref(false)

const tabs = [
  { id: 'cobros', name: 'Gestión de Cobros', icon: '💳' },
  { id: 'tesoreria', name: 'Remesas SEPA', icon: '💰' },
  { id: 'presupuesto', name: 'Control Presupuestario', icon: '📊' },
  { id: 'plataformas', name: 'Plataformas de Cobro', icon: '🏦' },
]

const transacciones = computed(() => {
  const rows = []
  for (const c of cuotas.value) {
    rows.push({
      id: `c-${c.id}`,
      fecha: c.fechaPago || c.fechaCreacion,
      concepto: `Cuota ${c.ejercicio}`,
      miembro: c.miembro ? `${c.miembro.nombre} ${c.miembro.apellido1}` : '—',
      tipo: 'CUOTA',
      estado: c.estado?.nombre?.toUpperCase() || '—',
      importe: c.importe,
    })
  }
  for (const d of donaciones.value) {
    rows.push({
      id: `d-${d.id}`,
      fecha: d.fecha,
      concepto: d.concepto?.nombre || 'Donación',
      miembro: d.anonima ? 'Anónimo' : (d.donanteNombre || '—'),
      tipo: 'DONACION',
      estado: d.estado?.nombre?.toUpperCase() || '—',
      importe: d.importe,
    })
  }
  return rows.sort((a, b) => (b.fecha || '').localeCompare(a.fecha || ''))
})

const resumen = computed(() => ({
  ingresosMes: 0,
  cuotasCobradas: cuotas.value.filter(c => c.estado?.nombre?.toLowerCase().includes('cobrad')).length,
  cuotasPendientes: cuotas.value.filter(c => c.estado?.nombre?.toLowerCase().includes('pendiente')).length,
  presupuestoEjecutado: 0,
}))

const filters = ref({
  tipo: '',
  estado: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Presupuesto y tesorería — pendiente de modelo en backend
const partidasPresupuesto = ref([])
const totalPresupuestado = computed(() => 0)
const totalEjecutado = computed(() => 0)
const plataformasCobro = ref([])
const cuentasTesoreria = ref([])
const totalTesoreria = computed(() => 0)
const flujoCaja = ref([])
const maxFlujo = computed(() => 1)

async function cargar() {
  loading.value = true
  try {
    const [dataCuotas, dataDonaciones, dataRemesas] = await Promise.all([
      executeQuery(GET_CUOTAS_ANUALES),
      executeQuery(GET_DONACIONES),
      executeQuery(GET_REMESAS),
    ])
    cuotas.value = dataCuotas.cuotasAnuales || []
    donaciones.value = dataDonaciones.donaciones || []
    remesasSEPA.value = dataRemesas.remesas || []
  } catch (e) {
    console.error('Error cargando financiero:', e?.response?.errors?.[0]?.message || e)
  } finally {
    loading.value = false
  }
}

onMounted(cargar)

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES')
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(amount)
}

const getProgressClass = (porcentaje) => {
  if (porcentaje >= 90) return 'bg-red-500'
  if (porcentaje >= 70) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getTipoClass = (tipo) => {
  const classes = {
    'CUOTA': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    'DONACION': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    'GASTO': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    'SUBVENCION': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  }
  return classes[tipo] || 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
}

const getEstadoClass = (estado) => {
  const classes = {
    'COBRADA': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    'PENDIENTE': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    'DEVUELTA': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    'ANULADA': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
  }
  return classes[estado] || 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
}

const getRemesaEstadoClass = (estado) => {
  const classes = {
    'Enviada': 'bg-blue-100 text-blue-800',
    'Cobrada': 'bg-green-100 text-green-800',
    'Parcial': 'bg-yellow-100 text-yellow-800',
    'Rechazada': 'bg-red-100 text-red-800'
  }
  return classes[estado] || 'bg-gray-100 text-gray-800'
}

function generarRemesa() {}
function verDetalle() {}
function marcarCobrada() {}
function configurarPlataforma() {}
function verMovimientos() {}
</script>
