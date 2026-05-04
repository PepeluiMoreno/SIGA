<template>
  <AppLayout title="Voluntarios" subtitle="Gestión del voluntariado de Europa Laica">
    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">❤️</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total voluntarios</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">✅</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Disponibles</p>
            <p class="text-xl font-bold text-green-600">{{ resumen.disponibles }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">🚩</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">En campaña activa</p>
            <p class="text-xl font-bold text-blue-600">{{ resumen.enCampania }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar voluntarios..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
        </div>
      </div>

      <!-- Filtros avanzados -->
      <div v-if="showFilters" class="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Disponibilidad</label>
            <select v-model="filtroDisponibilidad" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todas</option>
              <option value="DISPONIBLE">Disponible</option>
              <option value="OCUPADO">Ocupado en campaña</option>
              <option value="INACTIVO">Inactivo</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select v-model="filtroActivo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todos</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600">Cargando voluntarios...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <span class="text-red-400 mr-3">⚠️</span>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al cargar voluntarios</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Lista de voluntarios -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-if="voluntariosFiltrados.length === 0" class="col-span-full text-center py-12 bg-white rounded-lg shadow">
        <span class="text-4xl">❤️</span>
        <h3 class="text-sm font-medium text-gray-900 mt-4">No hay voluntarios</h3>
        <p class="text-sm text-gray-500 mt-1">No se encontraron voluntarios con los filtros seleccionados.</p>
      </div>

      <div
        v-for="v in voluntariosFiltrados"
        :key="v.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center">
              <div class="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                <span class="text-lg font-medium text-purple-700">{{ iniciales(v) }}</span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ nombreCompleto(v) }}</h3>
                <p v-if="v.profesion" class="text-sm text-gray-500">{{ v.profesion }}</p>
              </div>
            </div>
            <span v-if="v.disponibilidad" :class="getDisponibilidadClass(v.disponibilidad)">
              {{ v.disponibilidad }}
            </span>
          </div>

          <div class="space-y-2 text-sm text-gray-600 mb-4">
            <div v-if="v.email" class="flex items-center">
              <span class="mr-2">📧</span>
              <span>{{ v.email }}</span>
            </div>
            <div v-if="v.telefono" class="flex items-center">
              <span class="mr-2">📱</span>
              <span>{{ v.telefono }}</span>
            </div>
            <div v-if="v.horasDisponiblesSemana" class="flex items-center">
              <span class="mr-2">⏰</span>
              <span>{{ v.horasDisponiblesSemana }} h/semana disponibles</span>
            </div>
          </div>

          <div v-if="v.intereses" class="mb-4">
            <p class="text-xs text-gray-500 mb-1">Intereses:</p>
            <p class="text-sm text-gray-700">{{ v.intereses }}</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_VOLUNTARIOS } from '@/graphql/queries/voluntariado.js'

const loading = ref(false)
const error = ref('')
const voluntarios = ref([])
const searchQuery = ref('')
const showFilters = ref(false)
const filtroDisponibilidad = ref('')
const filtroActivo = ref('')

const resumen = computed(() => ({
  total: voluntarios.value.length,
  disponibles: voluntarios.value.filter(v => v.disponibilidad === 'DISPONIBLE').length,
  enCampania: voluntarios.value.filter(v => v.disponibilidad === 'OCUPADO').length,
}))

const voluntariosFiltrados = computed(() => {
  let result = voluntarios.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(v =>
      v.nombre?.toLowerCase().includes(q) ||
      v.apellido1?.toLowerCase().includes(q) ||
      v.email?.toLowerCase().includes(q)
    )
  }
  if (filtroDisponibilidad.value) {
    result = result.filter(v => v.disponibilidad === filtroDisponibilidad.value)
  }
  if (filtroActivo.value !== '') {
    const activo = filtroActivo.value === 'true'
    result = result.filter(v => v.activo === activo)
  }
  return result
})

function iniciales(v) {
  return `${v.nombre?.[0] ?? ''}${v.apellido1?.[0] ?? ''}`.toUpperCase()
}

function nombreCompleto(v) {
  return [v.nombre, v.apellido1, v.apellido2].filter(Boolean).join(' ')
}

function getDisponibilidadClass(d) {
  const classes = {
    DISPONIBLE: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    OCUPADO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    INACTIVO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return classes[d] || classes.INACTIVO
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await executeQuery(GET_VOLUNTARIOS)
    voluntarios.value = data.miembros || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando voluntarios'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
