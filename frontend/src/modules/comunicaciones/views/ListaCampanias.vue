<template>
  <AppLayout title="Campañas" subtitle="Gestión de campañas y actividades">
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar por nombre o lema…"
      create-label="Nueva Campaña"
      create-route="/campanias/nueva"
      :fields="filterFields"
      :lazy="true"
      :loading="loading"
      :description="filtersApplied ? tituloDescriptivo : ''"
      class="mb-4"
      @apply="aplicarFiltros"
      @clear="limpiarFiltros"
    />

    <!-- Estado de carga -->
    <EstadoCarga v-if="loading" mensaje="Cargando campañas..." />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <p class="text-red-700 font-medium">Error al cargar datos</p>
      <p class="text-red-600 text-sm mt-1">{{ error.message || error }}</p>
      <button @click="aplicarFiltros" class="mt-3 text-red-600 hover:text-red-800 text-sm font-medium">
        Reintentar
      </button>
    </div>

    <!-- Resultados -->
    <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- Mensaje inicial -->
      <EstadoPendiente v-if="!filtersApplied" />

      <!-- Sin resultados -->
      <div v-else-if="campaniasFiltradas.length === 0" class="p-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg">No se encontraron campañas</p>
        <p class="text-sm mt-1">Prueba con otros filtros</p>
      </div>

      <!-- Grid de campañas -->
      <template v-else>
        <!-- Barra de resultados -->
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            <strong>{{ campaniasFiltradas.length }}</strong> {{ tituloDescriptivo }}
          </span>
          <button @click="limpiarFiltros" class="text-sm text-purple-600 hover:text-purple-800">
            Limpiar filtros
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          <div
            v-for="campania in campaniasFiltradas"
            :key="campania.id"
            class="bg-purple-50 rounded-lg shadow hover:shadow-md transition-shadow border border-purple-100 hover:border-purple-200 group cursor-pointer"
            @click="verDetalles(campania)"
          >
            <div class="p-6">
              <div class="flex justify-between items-start mb-3">
                <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full border"
                  :style="badgeStyle(campania.estado?.color)">
                  {{ campania.estado?.nombre || 'Sin estado' }}
                </span>
                <span v-if="campania.tipoCampania" class="text-xs text-purple-600 bg-purple-100 px-2 py-0.5 rounded">
                  {{ campania.tipoCampania.nombre }}
                </span>
              </div>

              <h3 class="text-lg font-semibold text-gray-900 mb-1 group-hover:text-purple-700 transition-colors">
                {{ campania.nombre }}
              </h3>
              <p v-if="campania.lema" class="text-sm text-gray-500 mb-2">Lema: "{{ campania.lema }}"</p>
              <p class="text-sm text-gray-600 mb-4 line-clamp-2">{{ campania.descripcionCorta }}</p>

              <div class="space-y-2 text-sm text-gray-500">
                <div v-if="campania.responsable" class="flex items-center">
                  <span class="mr-2">👤</span>
                  <span>Coordinador: {{ campania.responsable.nombre }} {{ campania.responsable.apellido1 }}</span>
                </div>
                <div v-if="campania.fechaInicioPlan || campania.fechaFinPlan" class="flex items-center">
                  <span class="mr-2">📅</span>
                  <span>{{ formatDate(campania.fechaInicioPlan) }} - {{ formatDate(campania.fechaFinPlan) }}</span>
                </div>
                <div v-if="campania.metaRecaudacion" class="flex items-center">
                  <span class="mr-2">🎯</span>
                  <span>Meta: {{ formatCurrency(campania.metaRecaudacion) }}</span>
                </div>
                <div v-if="campania.metaFirmas" class="flex items-center">
                  <span class="mr-2">✍️</span>
                  <span>Objetivo: {{ campania.metaFirmas.toLocaleString() }} firmas</span>
                </div>
              </div>

              <!-- URL externa -->
              <div v-if="campania.urlExterna" class="mt-3">
                <a
                  :href="campania.urlExterna"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs text-purple-600 hover:text-purple-800 flex items-center gap-1"
                  @click.stop
                >
                  <span>🔗</span>
                  <span>Ver en laicismo.org</span>
                </a>
              </div>
            </div>

            <div class="px-6 py-3 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
              <div class="text-xs text-gray-500">
                <span v-if="campania.metaParticipantes">🎯 {{ campania.metaParticipantes }} participantes</span>
              </div>
              <router-link :to="`/campanias/${campania.id}`"
                class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded-md transition-colors"
                title="Ver detalles"
                @click.stop>
                <EyeIcon class="w-4 h-4" />
              </router-link>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { EyeIcon } from '@heroicons/vue/24/outline'
import { executeQuery } from '@/graphql/client'
import { GET_CAMPANIAS, GET_TIPOS_CAMPANIA, GET_ESTADOS_CAMPANIA } from '@/graphql/queries/campanias'
import { badgeStyle } from '@/utils/badge'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'

const router = useRouter()

// Datos
const allCampanias = ref([])
const tiposCampania = ref([])
const estadosCampania = ref([])
const searchQuery = ref('')
const loading = ref(false)
const error = ref(null)
const filtersApplied = ref(false)

// Filtros
const filters = ref({
  estados: [],
  tipos: [],
  anios: []
})

// Computed: años disponibles (año actual y 5 años hacia atrás)
const aniosDisponibles = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = currentYear; y >= currentYear - 5; y--) {
    years.push(y)
  }
  return years
})

// Computed: ordenar estados por orden
const estadosCampaniaOrdenados = computed(() =>
  [...estadosCampania.value].sort((a, b) => (a.orden ?? 999) - (b.orden ?? 999))
)

// Computed: ordenar tipos alfabéticamente
const tiposCampaniaOrdenados = computed(() =>
  [...tiposCampania.value].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
)

// Campos del FilterBar
const filterFields = computed(() => [
  {
    key: 'estados',
    label: 'Estado',
    type: 'multiselect',
    allLabel: 'Todos los estados',
    options: estadosCampaniaOrdenados.value.map(e => ({ value: e.id, label: e.nombre })),
  },
  {
    key: 'tipos',
    label: 'Tipo',
    type: 'multiselect',
    allLabel: 'Todos los tipos',
    options: tiposCampaniaOrdenados.value.map(t => ({ value: t.id, label: t.nombre })),
  },
  {
    key: 'anios',
    label: 'Año',
    type: 'multiselect',
    allLabel: 'Todos los años',
    options: aniosDisponibles.value.map(y => ({ value: y, label: String(y) })),
  },
])

// Computed: campañas filtradas
const campaniasFiltradas = computed(() => {
  if (!filtersApplied.value) return []

  let filtered = [...allCampanias.value]

  // Búsqueda por texto
  if (searchQuery.value.trim()) {
    const search = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(c =>
      c.nombre?.toLowerCase().includes(search) ||
      c.lema?.toLowerCase().includes(search) ||
      c.descripcionCorta?.toLowerCase().includes(search)
    )
  }

  // Filtro por estados (OR)
  if (filters.value.estados.length > 0) {
    filtered = filtered.filter(c =>
      c.estado && filters.value.estados.includes(c.estado.id)
    )
  }

  // Filtro por tipos (OR)
  if (filters.value.tipos.length > 0) {
    filtered = filtered.filter(c =>
      c.tipoCampania && filters.value.tipos.includes(c.tipoCampania.id)
    )
  }

  // Filtro por años (OR entre años seleccionados)
  if (filters.value.anios.length > 0) {
    filtered = filtered.filter(c => {
      const fechaInicio = c.fechaInicioPlan ? new Date(c.fechaInicioPlan).getFullYear() : null
      const fechaFin = c.fechaFinPlan ? new Date(c.fechaFinPlan).getFullYear() : null
      // La campaña coincide si su rango de fechas incluye alguno de los años seleccionados
      return filters.value.anios.some(anio => {
        if (fechaInicio && fechaFin) {
          return fechaInicio <= anio && fechaFin >= anio
        }
        if (fechaInicio) return fechaInicio === anio
        if (fechaFin) return fechaFin === anio
        return false
      })
    })
  }

  return filtered
})

// Computed: título descriptivo
const tituloDescriptivo = computed(() => {
  const total = campaniasFiltradas.value.length
  const base = total === 1 ? 'campaña' : 'campañas'

  // Tipos
  let tiposStr = ''
  if (filters.value.tipos.length > 0 && filters.value.tipos.length < tiposCampania.value.length) {
    const nombres = filters.value.tipos.map(id => {
      const tipo = tiposCampania.value.find(t => t.id === id)
      return tipo ? tipo.nombre.toLowerCase() : ''
    }).filter(Boolean)
    if (nombres.length > 0) {
      tiposStr = ` de ${nombres.join(', ')}`
    }
  }

  // Estados
  let estadosStr = ''
  if (filters.value.estados.length > 0 && filters.value.estados.length < estadosCampania.value.length) {
    const nombres = filters.value.estados.map(id => {
      const estado = estadosCampania.value.find(e => e.id === id)
      return estado ? estado.nombre.toLowerCase() : ''
    }).filter(Boolean)
    if (nombres.length > 0) {
      estadosStr = ` ${nombres.join(', ')}`
    }
  }

  // Años
  let anioStr = ''
  if (filters.value.anios.length > 0 && filters.value.anios.length < aniosDisponibles.value.length) {
    if (filters.value.anios.length <= 2) {
      anioStr = ` en ${filters.value.anios.join(', ')}`
    } else {
      anioStr = ` (${filters.value.anios.length} años)`
    }
  }

  return `${base}${tiposStr}${estadosStr}${anioStr}`
})

// Cargar catálogos al montar
const loadCatalogos = async () => {
  try {
    const [tiposData, estadosData] = await Promise.all([
      executeQuery(GET_TIPOS_CAMPANIA),
      executeQuery(GET_ESTADOS_CAMPANIA),
    ])
    tiposCampania.value = tiposData?.tiposCampania || []
    estadosCampania.value = estadosData?.estadosCampania || []
  } catch (err) {
    console.error('Error al cargar catálogos:', err)
  }
}

// Aplicar filtros y buscar
const aplicarFiltros = async () => {
  filtersApplied.value = true
  loading.value = true
  error.value = null

  try {
    const data = await executeQuery(GET_CAMPANIAS)
    allCampanias.value = data.campanias || []
  } catch (err) {
    error.value = err
    console.error('Error cargando campañas:', err)
  } finally {
    loading.value = false
  }
}

// Limpiar filtros
const limpiarFiltros = () => {
  filters.value = {
    estados: [],
    tipos: [],
    anios: []
  }
  searchQuery.value = ''
  filtersApplied.value = false
  allCampanias.value = []
}


const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

const formatCurrency = (amount) => {
  if (!amount) return '0,00 €'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(amount)
}

const verDetalles = (campania) => {
  router.push(`/campanias/${campania.id}`)
}

// Montar
onMounted(() => loadCatalogos())
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.group {
  transition: all 0.2s ease;
}

.group:hover {
  transform: translateY(-2px);
}
</style>
