<template>
  <AppLayout title="Militancia" subtitle="Gestión de miembros, colaboración y disponibilidad">
    <!-- Barra superior con búsqueda y botón nuevo -->
    <div class="mb-4 flex items-center justify-between gap-4">
      <div class="relative flex-1 max-w-md">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nombre, apellido o email de un miembro..."
          class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          @keyup.enter="aplicarFiltros"
        />
        <span class="absolute left-3 top-2.5 text-gray-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
      </div>
      <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo miembro
      </button>
    </div>

    <!-- Panel de Filtros -->
    <div class="mb-4 bg-white border border-gray-200 rounded-lg p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">

        <!-- Situación (EstadoMiembro) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Situación</label>
          <div class="space-y-1 max-h-48 overflow-y-auto">
            <template v-if="estadosMiembro.length > 0">
              <!-- Estados que NO son Baja -->
              <template v-for="estado in estadosMiembroOrdenados" :key="estado.id">
                <label
                  v-if="estado.nombre !== 'Baja'"
                  class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                >
                  <input
                    type="checkbox"
                    :value="estado.id"
                    v-model="filters.estados"
                    class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <span class="text-sm text-gray-700">{{ estado.nombre }}</span>
                </label>
              </template>

              <!-- Baja con desplegable de motivos -->
              <div class="flex items-center gap-2 p-1">
                <input
                  type="checkbox"
                  :value="estadoBajaId"
                  v-model="filters.estados"
                  class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span class="text-sm text-gray-700">Baja por</span>
                <select
                  v-model="filters.motivoBaja"
                  :disabled="!filters.estados.includes(estadoBajaId)"
                  class="flex-1 text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:text-gray-400"
                >
                  <option value="">Cualquier causa</option>
                  <option v-for="motivo in motivosBaja" :key="motivo.id" :value="motivo.id">
                    {{ motivo.nombre }}
                  </option>
                </select>
              </div>
            </template>
            <p v-else class="text-sm text-gray-400 italic p-1">Cargando...</p>
          </div>
        </div>

        <!-- Tipo de miembro -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tipo de miembro</label>
          <div class="space-y-1 max-h-40 overflow-y-auto">
            <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
              <input
                type="checkbox"
                :checked="todosTiposSeleccionados"
                :indeterminate="algunTipoSeleccionado && !todosTiposSeleccionados"
                @change="toggleTodosTipos"
                class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <span class="text-sm font-medium text-gray-900">Todos</span>
            </label>
            <template v-if="tiposMiembro.length > 0">
              <label
                v-for="tipo in tiposMiembroOrdenados"
                :key="tipo.id"
                class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
              >
                <input
                  type="checkbox"
                  :value="tipo.id"
                  v-model="filters.tipos"
                  class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span class="text-sm text-gray-700">{{ tipo.nombre }}</span>
              </label>
            </template>
            <p v-else class="text-sm text-gray-400 italic p-1">Cargando...</p>
          </div>
        </div>

        <!-- Agrupación Territorial -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Agrupación Territorial</label>
          <select
            v-model="filters.agrupacion"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="">Todas las agrupaciones</option>
            <template v-if="agrupaciones.length > 0">
              <option v-for="agrup in agrupacionesJerarquicas" :key="agrup.id" :value="agrup.id">
                {{ agrup.displayNombre }}
              </option>
            </template>
          </select>

          <!-- Checkbox voluntarios -->
          <label class="flex items-center gap-2 cursor-pointer mt-4 hover:bg-gray-50 p-1 rounded">
            <input
              type="checkbox"
              v-model="filters.soloVoluntarios"
              class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
            />
            <span class="text-sm text-gray-700">Solo voluntarios</span>
          </label>
        </div>

        <!-- Botones de acción -->
        <div class="flex flex-col justify-end gap-2">
          <button
            @click="aplicarFiltros"
            :disabled="loading"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Buscando...' : 'Buscar' }}
          </button>
          <button
            @click="limpiarFiltros"
            class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="bg-white border border-gray-200 rounded-lg p-12 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent mb-3"></div>
      <p class="text-gray-600">Cargando registros de militancia...</p>
    </div>

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
      <div v-if="!filtersApplied" class="p-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        <p class="text-lg">Configura los filtros y pulsa "Buscar"</p>
      </div>

      <!-- Sin resultados -->
      <div v-else-if="miembros.length === 0" class="p-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg">No se encontraron miembros</p>
        <p class="text-sm mt-1">Prueba con otros filtros</p>
      </div>

      <!-- Tabla de resultados -->
      <template v-else>
        <!-- Barra de resultados con título descriptivo -->
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            <strong>{{ total }}</strong> {{ tituloDescriptivo }}
          </span>
          <button @click="limpiarFiltros" class="text-sm text-purple-600 hover:text-purple-800">
            Limpiar filtros
          </button>
        </div>

        <!-- Tabla -->
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Miembro</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agrupación</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Alta</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="miembro in miembros" :key="miembro.id" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <div
                    class="h-9 w-9 rounded-full flex items-center justify-center mr-3 text-white text-sm font-medium"
                    :class="miembro.activo ? 'bg-purple-500' : 'bg-gray-400'"
                  >
                    {{ getInitials(miembro.nombre, miembro.apellido1) }}
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ miembro.nombre }} {{ miembro.apellido1 }} {{ miembro.apellido2 || '' }}
                    </div>
                    <div v-if="miembro.esVoluntario" class="text-xs text-purple-600">Voluntario</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-700">
                {{ miembro.agrupacion?.nombre || '-' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-500">
                {{ formatDate(miembro.fechaAlta) }}
              </td>
              <td class="px-4 py-3 text-right text-sm space-x-2">
                <button @click="editarMiembro(miembro)" class="text-purple-600 hover:text-purple-900">Editar</button>
                <button @click="verDetalle(miembro)" class="text-gray-500 hover:text-gray-700">Ver</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación -->
        <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-200 bg-gray-50 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            Mostrando {{ from }}-{{ to }} de {{ total }}
          </span>
          <div class="flex gap-2">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Anterior
            </button>
            <span class="px-3 py-1 text-sm text-gray-600">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Siguiente
            </button>
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
import { useGraphQL } from '@/composables/useGraphQL.js'
import { GET_MIEMBROS, GET_AGRUPACIONES, GET_TIPOS_MIEMBRO, GET_ESTADOS_MIEMBRO, GET_MOTIVOS_BAJA } from '@/graphql/queries/miembros.js'

const router = useRouter()
const { loading, error, query } = useGraphQL()

// Datos
const miembros = ref([])
const allMiembros = ref([])
const agrupaciones = ref([])
const tiposMiembro = ref([])
const estadosMiembro = ref([])
const motivosBaja = ref([])

// Estado UI
const searchQuery = ref('')
const filtersApplied = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Filtros
const filters = ref({
  estados: [],
  motivoBaja: '',  // '' = cualquier causa, UUID = motivo específico (solo aplica a Baja)
  tipos: [],
  agrupacion: '',
  soloVoluntarios: false
})

// Computed: paginación
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const from = computed(() => total.value === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1)
const to = computed(() => Math.min(currentPage.value * pageSize.value, total.value))

// Computed: ID del estado Baja para el filtro especial
const estadoBajaId = computed(() =>
  estadosMiembro.value.find(e => e.nombre === 'Baja')?.id
)

// Computed: ordenar estados por campo 'orden'
const estadosMiembroOrdenados = computed(() =>
  [...estadosMiembro.value].sort((a, b) => (a.orden ?? 999) - (b.orden ?? 999))
)

// Computed: checkbox "Todos" para tipos
const todosTiposSeleccionados = computed(() =>
  tiposMiembro.value.length > 0 && filters.value.tipos.length === tiposMiembro.value.length
)
const algunTipoSeleccionado = computed(() => filters.value.tipos.length > 0)

// Computed: ordenar tipos alfabéticamente
const tiposMiembroOrdenados = computed(() =>
  [...tiposMiembro.value].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
)

// Computed: agrupaciones en árbol jerárquico
const agrupacionesJerarquicas = computed(() => {
  const lista = agrupaciones.value
  if (!lista.length) return []

  const tipoOrden = { ESTATAL: 1, AUTONOMICA: 2, PROVINCIAL: 3, LOCAL: 4 }

  const buildTree = (padreId = null, nivel = 0) => {
    const hijos = lista
      .filter(a => a.agrupacionPadreId === padreId)
      .sort((a, b) => {
        const ordenA = tipoOrden[a.tipo] || 99
        const ordenB = tipoOrden[b.tipo] || 99
        if (ordenA !== ordenB) return ordenA - ordenB
        return a.nombre.localeCompare(b.nombre, 'es')
      })

    const resultado = []
    for (const agrup of hijos) {
      const indent = '\u00A0\u00A0'.repeat(nivel)
      resultado.push({ ...agrup, displayNombre: indent + agrup.nombre })
      resultado.push(...buildTree(agrup.id, nivel + 1))
    }
    return resultado
  }

  return buildTree(null, 0)
})

// Computed: título descriptivo para resultados (ej: "miembros activos", "miembros, simpatizantes de baja")
const tituloDescriptivo = computed(() => {
  // Obtener nombres de tipos seleccionados
  let nombresTipos = []
  if (filters.value.tipos.length > 0 && filters.value.tipos.length < tiposMiembro.value.length) {
    nombresTipos = filters.value.tipos.map(id => {
      const tipo = tiposMiembro.value.find(t => t.id === id)
      return tipo ? pluralizar(tipo.nombre) : ''
    }).filter(Boolean)
  } else {
    // Todos o ninguno seleccionado = mostrar genérico
    nombresTipos = [total.value === 1 ? 'miembro' : 'miembros']
  }

  // Obtener nombres de estados seleccionados
  let nombresEstados = []
  if (filters.value.estados.length > 0) {
    nombresEstados = filters.value.estados.map(id => {
      const estado = estadosMiembro.value.find(e => e.id === id)
      if (!estado) return ''

      // Caso especial para Baja con motivo
      if (estado.nombre === 'Baja' && filters.value.motivoBaja) {
        const motivo = motivosBaja.value.find(m => m.id === filters.value.motivoBaja)
        return motivo ? `de baja por ${motivo.nombre.toLowerCase()}` : 'de baja'
      }

      return estadoEnPlural(estado.nombre)
    }).filter(Boolean)
  }

  // Obtener agrupación seleccionada
  let agrupacionStr = ''
  if (filters.value.agrupacion) {
    const agrup = agrupaciones.value.find(a => a.id === filters.value.agrupacion)
    if (agrup) {
      agrupacionStr = `en ${agrup.nombre}`
    }
  }

  // Componer título
  const tiposStr = nombresTipos.join(', ')
  const estadosStr = nombresEstados.join(', ')

  let resultado = tiposStr
  if (estadosStr) {
    resultado = `${tiposStr} ${estadosStr}`
  }
  if (agrupacionStr) {
    resultado = `${resultado} ${agrupacionStr}`
  }
  return resultado
})

// Helpers para pluralizar
const pluralizar = (nombre) => {
  const lower = nombre.toLowerCase()
  // Reglas básicas de pluralización en español
  if (lower === 'miembro') return total.value === 1 ? 'miembro' : 'miembros'
  if (lower === 'simpatizante') return total.value === 1 ? 'simpatizante' : 'simpatizantes'
  if (lower === 'colaborador') return total.value === 1 ? 'colaborador' : 'colaboradores'
  if (lower === 'voluntario') return total.value === 1 ? 'voluntario' : 'voluntarios'
  if (lower === 'benefactor') return total.value === 1 ? 'benefactor' : 'benefactores'
  // Por defecto, añadir 's' si no termina en 's'
  if (lower.endsWith('s')) return nombre
  return total.value === 1 ? nombre : nombre + 's'
}

const estadoEnPlural = (nombre) => {
  const lower = nombre.toLowerCase()
  if (lower === 'activo') return total.value === 1 ? 'activo' : 'activos'
  if (lower === 'suspendido') return total.value === 1 ? 'suspendido' : 'suspendidos'
  if (lower === 'pendiente aprobación' || lower === 'pendiente de aprobación') {
    return total.value === 1 ? 'pendiente de aprobación' : 'pendientes de aprobación'
  }
  if (lower === 'baja') return 'de baja'
  return nombre.toLowerCase()
}

// Toggle todos tipos
const toggleTodosTipos = () => {
  if (todosTiposSeleccionados.value) {
    filters.value.tipos = []
  } else {
    filters.value.tipos = tiposMiembro.value.map(t => t.id)
  }
}

// Cargar catálogos al montar
const loadCatalogos = async () => {
  try {
    // Cargar secuencialmente para evitar errores de concurrencia
    const agrupData = await query(GET_AGRUPACIONES)
    agrupaciones.value = agrupData?.agrupacionesTerritoriales || []

    const tiposData = await query(GET_TIPOS_MIEMBRO)
    tiposMiembro.value = tiposData?.tiposMiembro || []

    const estadosData = await query(GET_ESTADOS_MIEMBRO)
    estadosMiembro.value = estadosData?.estadosMiembro || []

    const motivosData = await query(GET_MOTIVOS_BAJA)
    motivosBaja.value = motivosData?.motivosBaja || []
  } catch (err) {
    console.error('Error al cargar catálogos:', err)
  }
}

// Aplicar filtros y buscar
const aplicarFiltros = async () => {
  filtersApplied.value = true
  currentPage.value = 1

  try {
    const data = await query(GET_MIEMBROS)
    if (data?.miembros) {
      allMiembros.value = data.miembros
      applyClientFilters()
    }
  } catch (err) {
    console.error('Error al cargar miembros:', err)
  }
}

// Filtrar en cliente
const applyClientFilters = () => {
  let filtered = [...allMiembros.value]

  // Búsqueda por texto
  if (searchQuery.value.trim()) {
    const search = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(m =>
      m.nombre?.toLowerCase().includes(search) ||
      m.apellido1?.toLowerCase().includes(search) ||
      m.apellido2?.toLowerCase().includes(search) ||
      m.email?.toLowerCase().includes(search)
    )
  }

  // Filtro por estados (con caso especial para Baja + motivo)
  if (filters.value.estados.length > 0) {
    const estadosSeleccionados = filters.value.estados
    const motivoBaja = filters.value.motivoBaja
    const incluyeBaja = estadoBajaId.value && estadosSeleccionados.includes(estadoBajaId.value)

    filtered = filtered.filter(m => {
      const estadoMiembro = m.estado?.id
      if (!estadoMiembro) return false

      // Si el miembro está en estado Baja y hay filtro de motivo
      if (estadoMiembro === estadoBajaId.value && incluyeBaja) {
        if (motivoBaja) {
          return m.motivoBajaRel?.id === motivoBaja
        }
        return true
      }

      // Para otros estados, verificar si está en la lista
      return estadosSeleccionados.includes(estadoMiembro)
    })
  }

  // Filtro por tipos (OR)
  if (filters.value.tipos.length > 0) {
    filtered = filtered.filter(m => m.tipoMiembro && filters.value.tipos.includes(m.tipoMiembro.id))
  }

  // Filtro por agrupación
  if (filters.value.agrupacion) {
    filtered = filtered.filter(m => m.agrupacion?.id === filters.value.agrupacion)
  }

  // Filtro solo voluntarios
  if (filters.value.soloVoluntarios) {
    filtered = filtered.filter(m => m.esVoluntario === true)
  }

  total.value = filtered.length
  const start = (currentPage.value - 1) * pageSize.value
  miembros.value = filtered.slice(start, start + pageSize.value)
}

// Limpiar filtros
const limpiarFiltros = () => {
  filters.value = {
    estados: [],
    motivoBaja: '',
    tipos: [],
    agrupacion: '',
    soloVoluntarios: false
  }
  searchQuery.value = ''
  filtersApplied.value = false
  miembros.value = []
  allMiembros.value = []
  total.value = 0
  currentPage.value = 1
}

// Paginación
const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    applyClientFilters()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    applyClientFilters()
  }
}

// Acciones
const editarMiembro = (miembro) => router.push(`/miembros/${miembro.id}`)
const verDetalle = (miembro) => router.push(`/miembros/${miembro.id}`)

// Utilidades
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

const getInitials = (nombre, apellido1) => {
  return `${nombre?.[0] || ''}${apellido1?.[0] || ''}`.toUpperCase()
}

// Montar
onMounted(() => loadCatalogos())
</script>
