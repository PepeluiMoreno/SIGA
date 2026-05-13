<template>
  <AppLayout title="Grupos de Trabajo" subtitle="Gestión de grupos y equipos">
    <!-- Filtros -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar grupos…"
      create-label="Nuevo Grupo"
      create-route="/grupos/nuevo"
      :fields="filterFields"
      :lazy="true"
      :loading="loading"
      class="mb-6"
      @apply="aplicarFiltros"
    />

    <!-- Loading -->
    <EstadoCarga v-if="loading" mensaje="Cargando grupos..." />

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
      <div v-if="!filtersApplied" class="bg-white rounded-lg shadow">
        <EstadoPendiente />
      </div>
      <div v-else-if="gruposFiltrados.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <span class="text-4xl">👥</span>
        <h3 class="text-sm font-medium text-gray-900 mt-4">No hay grupos</h3>
        <p class="text-sm text-gray-500 mt-1">Prueba con otros filtros.</p>
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
                  <span>{{ grupo.miembros?.length ?? 0 }} {{ orgConfig.miembros }}</span>
                </div>
                <div v-if="grupo.fechaCreacion" class="flex items-center">
                  <span class="mr-1">📅</span>
                  <span>Desde {{ formatDate(grupo.fechaCreacion) }}</span>
                </div>
              </div>
            </div>

            <div class="mt-4 md:mt-0 md:ml-6">
              <RowActions
                :show-view="true"
                :show-edit="true"
                confirm-title="¿Eliminar este grupo?"
                :confirm-text="`«${grupo.nombre}» será eliminado permanentemente.`"
                @view="$router.push(`/grupos/${grupo.id}`)"
                @edit="$router.push(`/grupos/${grupo.id}`)"
                @delete="eliminarGrupo(grupo)"
              />
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
import FilterBar from '@/components/common/FilterBar.vue'
import RowActions from '@/components/common/RowActions.vue'
import { graphqlClient, executeQuery } from '@/graphql/client'
import { GET_GRUPOS, GET_TIPOS_GRUPO, ELIMINAR_GRUPO } from '@/graphql/queries/grupos.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'

const orgConfig = useOrgConfigStore()
const loading = ref(false)
const error = ref('')
const grupos = ref([])
const tiposGrupo = ref([])
const searchQuery = ref('')
const filtersApplied = ref(false)

const filters = ref({ tipo: '', activo: '' })

const filterFields = computed(() => [
  {
    key: 'tipo', label: 'Tipo', type: 'select', allLabel: 'Todos los tipos',
    options: tiposGrupo.value.map(t => ({ value: t.id, label: t.nombre })),
  },
  {
    key: 'activo', label: 'Estado', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }],
    isActive: (v) => v !== '',
  },
])

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
    tiposGrupo.value = (dataTipos?.tiposGrupo || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando grupos'
  } finally {
    loading.value = false
  }
}

async function aplicarFiltros() {
  await cargar()
  filtersApplied.value = true
}

async function eliminarGrupo(grupo) {
  try {
    await graphqlClient.request(ELIMINAR_GRUPO, { id: grupo.id })
    grupos.value = grupos.value.filter(g => g.id !== grupo.id)
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando grupo')
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

onMounted(() => {})
</script>
