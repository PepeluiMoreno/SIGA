<template>
  <AppLayout title="Grupos de Trabajo" subtitle="Gestión de grupos y equipos">
    <!-- Filtros y búsqueda -->
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar grupos..."
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
          <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            + Nuevo Grupo
          </button>
        </div>
      </div>

      <!-- Filtros avanzados -->
      <div v-if="showFilters" class="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="filters.tipo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todos</option>
              <option v-for="t in tiposGrupo" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select v-model="filters.activo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
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
      <p class="mt-2 text-gray-600">Cargando grupos...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <span class="text-red-400 mr-3">⚠️</span>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al cargar grupos</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Lista de grupos -->
    <div v-else class="space-y-4">
      <div v-if="gruposFiltrados.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <span class="text-4xl">👥</span>
        <h3 class="text-sm font-medium text-gray-900 mt-4">No hay grupos</h3>
        <p class="text-sm text-gray-500 mt-1">Aún no hay grupos de trabajo registrados.</p>
      </div>

      <div
        v-for="grupo in gruposFiltrados"
        :key="grupo.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">{{ grupo.nombre }}</h3>
                <span :class="getTipoClass(grupo.tipo?.nombre)">{{ grupo.tipo?.nombre }}</span>
                <span v-if="!grupo.activo" class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                  Inactivo
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-3">{{ grupo.descripcion }}</p>

              <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                <div v-if="grupo.coordinador" class="flex items-center">
                  <span class="mr-1">👤</span>
                  <span>Coordinador: {{ grupo.coordinador.nombre }} {{ grupo.coordinador.apellido1 }}</span>
                </div>
                <div class="flex items-center">
                  <span class="mr-1">👥</span>
                  <span>{{ grupo.miembros?.length ?? 0 }} miembros</span>
                </div>
                <div v-if="grupo.fechaCreacion" class="flex items-center">
                  <span class="mr-1">📅</span>
                  <span>Desde {{ formatDate(grupo.fechaCreacion) }}</span>
                </div>
              </div>
            </div>

            <div class="mt-4 md:mt-0 md:ml-6 flex space-x-2">
              <router-link
                :to="`/grupos/${grupo.id}`"
                class="px-3 py-2 text-sm text-purple-600 hover:text-purple-800 font-medium"
              >
                Ver detalle
              </router-link>
            </div>
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
import { GET_GRUPOS, GET_TIPOS_GRUPO } from '@/graphql/queries/grupos.js'

const loading = ref(false)
const error = ref('')
const grupos = ref([])
const tiposGrupo = ref([])
const searchQuery = ref('')
const showFilters = ref(false)

const filters = ref({
  tipo: '',
  activo: '',
})

const gruposFiltrados = computed(() => {
  let result = grupos.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(g =>
      g.nombre?.toLowerCase().includes(q) ||
      g.descripcion?.toLowerCase().includes(q)
    )
  }
  if (filters.value.tipo) {
    result = result.filter(g => g.tipo?.id === filters.value.tipo)
  }
  if (filters.value.activo !== '') {
    const activo = filters.value.activo === 'true'
    result = result.filter(g => g.activo === activo)
  }
  return result
})

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const [dataGrupos, dataTipos] = await Promise.all([
      executeQuery(GET_GRUPOS),
      executeQuery(GET_TIPOS_GRUPO),
    ])
    grupos.value = dataGrupos.gruposTrabajo || []
    tiposGrupo.value = dataTipos.tiposGrupo || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando grupos'
  } finally {
    loading.value = false
  }
}

function getTipoClass(nombre) {
  if (!nombre) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
  const n = nombre.toUpperCase()
  if (n.includes('PERMANENTE')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800'
  if (n.includes('TEMPORAL')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800'
  return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', { month: 'short', year: 'numeric' })
}

onMounted(cargar)
</script>
