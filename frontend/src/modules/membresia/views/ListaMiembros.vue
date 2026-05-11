<template>
  <AppLayout :title="orgConfig.Miembros" subtitle="Gestión, colaboración y disponibilidad">
    <!-- Panel de Filtros -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      :search-placeholder="`Buscar por nombre, apellido o email…`"
      :create-label="`Nuevo ${orgConfig.miembro}`"
      create-route="/miembros/nuevo"
      :fields="filterFields"
      :description="descripcionBusqueda"
      :lazy="true"
      :loading="loading"
      class="mb-4"
      @apply="aplicarFiltros"
      @clear="limpiarFiltros">

      <!-- Situación: dropdown personalizado con sub-selección de motivo de baja -->
      <template #dropdown-estados="{ filters: f, setFilters }">
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
            <input type="checkbox"
              :checked="f.estados.length === estadosMiembro.length"
              :indeterminate.prop="f.estados.length > 0 && f.estados.length < estadosMiembro.length"
              @change="setFilters({ estados: $event.target.checked ? estadosMiembro.map(e => e.id) : [] })"
              class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
            <span class="text-sm font-medium text-gray-900">Cualquiera</span>
          </label>
          <template v-for="estado in estadosMiembroOrdenados" :key="estado.id">
            <div v-if="estado.nombre === 'Baja'" class="space-y-1">
              <label class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
                <input type="checkbox"
                  :checked="f.estados.includes(estado.id)"
                  @change="setFilters({ estados: $event.target.checked ? [...f.estados, estado.id] : f.estados.filter(id => id !== estado.id) })"
                  class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
                <span class="text-sm text-gray-700">Baja</span>
              </label>
              <select v-if="f.estados.includes(estado.id)"
                :value="f.motivoBaja"
                @change="setFilters({ motivoBaja: $event.target.value })"
                class="ml-6 w-[calc(100%-1.5rem)] text-sm border border-gray-300 rounded px-2 py-1">
                <option value="">Cualquier causa</option>
                <option v-for="motivo in motivosBajaOrdenados" :key="motivo.id" :value="motivo.id">{{ motivo.nombre }}</option>
              </select>
            </div>
            <label v-else class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
              <input type="checkbox"
                :checked="f.estados.includes(estado.id)"
                @change="setFilters({ estados: $event.target.checked ? [...f.estados, estado.id] : f.estados.filter(id => id !== estado.id) })"
                class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
              <span class="text-sm text-gray-700">{{ estado.nombre }}</span>
            </label>
          </template>
        </div>
      </template>

    </FilterBar>

    <!-- Estado de carga -->
    <EstadoCarga v-if="loading" mensaje="Cargando registros de militancia..." />

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
      <div v-else-if="miembros.length === 0" class="p-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg">No se encontraron miembros</p>
        <p class="text-sm mt-1">Prueba con otros filtros</p>
      </div>

      <!-- Tabla jerárquica de resultados -->
      <template v-else>
        <!-- Barra de resultados -->
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            <strong>{{ total }}</strong> {{ tituloDescriptivo }}
          </span>
          <button @click="limpiarFiltros" class="text-sm text-purple-600 hover:text-purple-800">Limpiar filtros</button>
        </div>

        <table class="min-w-full divide-y divide-gray-200">
          <tbody class="bg-white divide-y divide-gray-100">
            <template v-for="fila in filasJerarquicas" :key="fila.type === 'agrupacion' ? 'ag-' + fila.agrupacion.id : 'mb-' + fila.miembro.id">

              <!-- Fila cabecera de agrupación -->
              <tr
                v-if="fila.type === 'agrupacion'"
                class="cursor-pointer select-none bg-purple-50 hover:bg-purple-100 border-t border-purple-100"
                @click="toggleAgrupacion(fila.agrupacion.id)"
              >
                <td colspan="4" class="py-2 pr-4" :style="{ paddingLeft: (fila.depth * 20 + 16) + 'px' }">
                  <div class="flex items-center gap-2">
                    <svg class="w-3.5 h-3.5 text-purple-400 shrink-0 transition-transform"
                         :class="colapsadas.has(fila.agrupacion.id) ? '' : 'rotate-90'"
                         fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                    <span class="text-sm font-semibold text-purple-800">{{ fila.agrupacion.nombre }}</span>
                    <span class="text-xs text-purple-400 font-normal">{{ fila.countTotal }} miembro{{ fila.countTotal !== 1 ? 's' : '' }}</span>
                  </div>
                </td>
              </tr>

              <!-- Fila de miembro -->
              <tr v-else class="hover:bg-gray-50">
                <td class="py-3 pr-4" :style="{ paddingLeft: (fila.depth * 20 + 16) + 'px' }">
                  <div class="flex items-center gap-3">
                    <div class="h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-white text-xs font-medium bg-purple-500">
                      {{ getInitials(fila.miembro.nombre, fila.miembro.apellido1) }}
                    </div>
                    <div>
                      <div class="text-sm font-medium text-gray-900">
                        {{ fila.miembro.apellido1 }}{{ fila.miembro.apellido2 ? ' ' + fila.miembro.apellido2 : '' }}, {{ fila.miembro.nombre }}
                      </div>
                      <div class="flex items-center gap-2 mt-0.5">
                        <span v-if="fila.miembro.tipoMiembro" class="text-xs text-gray-400">{{ fila.miembro.tipoMiembro.nombre }}</span>
                        <span v-if="fila.miembro.esVoluntario" class="text-xs bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded-full">Voluntario</span>
                        <span v-if="fila.miembro.usuario?.activo" title="Tiene acceso a la aplicación"
                          class="inline-flex items-center gap-0.5 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                          </svg>
                          App
                        </span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="text-xs text-gray-400 mb-1">Datos de contacto</p>
                  <div class="flex items-center gap-1.5 text-sm text-gray-700">
                    <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    <span>{{ fila.miembro.email || '—' }}</span>
                  </div>
                  <div v-if="fila.miembro.telefono" class="flex items-center gap-1.5 text-xs text-gray-500 mt-0.5">
                    <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    <span>{{ fila.miembro.telefono }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="text-xs text-gray-400 mb-1">Es socio desde</p>
                  <p class="text-sm text-gray-600">{{ formatDate(fila.miembro.fechaAlta) }}</p>
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <router-link :to="`/miembros/${fila.miembro.id}`"
                      class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      title="Ver ficha">
                      <EyeIcon class="w-4 h-4" />
                    </router-link>
                    <router-link :to="`/miembros/${fila.miembro.id}?modo=editar`"
                      class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      title="Editar">
                      <PencilIcon class="w-4 h-4" />
                    </router-link>
                  </div>
                </td>
              </tr>

            </template>
          </tbody>
        </table>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { EyeIcon, PencilIcon } from '@heroicons/vue/24/outline'
import { useGraphQL } from '@/composables/useGraphQL.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { GET_MIEMBROS, GET_AGRUPACIONES, GET_TIPOS_MIEMBRO, GET_ESTADOS_MIEMBRO, GET_MOTIVOS_BAJA } from '@/graphql/queries/miembros.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'
const { loading, error, query } = useGraphQL()
const orgConfig = useOrgConfigStore()

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
const colapsadas = ref(new Set())

// Filtros
const filters = ref({
  estados: [],
  motivoBaja: '',  // '' = cualquier causa, UUID = motivo específico (solo aplica a Baja)
  tipos: [],
  agrupacion: '',
  soloVoluntarios: false,
  soloConAcceso: false,
})

// Limpiar resultados al cambiar cualquier filtro
watch(filters, () => {
  if (filtersApplied.value) {
    miembros.value = []
    allMiembros.value = []
    filtersApplied.value = false
    total.value = 0
    currentPage.value = 1
  }
}, { deep: true })

// Búsqueda en tiempo real sobre datos ya cargados
watch(searchQuery, () => {
  if (allMiembros.value.length > 0) {
    currentPage.value = 1
    applyClientFilters()
  }
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
  [...estadosMiembro.value].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
)

// Computed: "Cualquiera" para estados — también usado en applyClientFilters
const todosEstadosSeleccionados = computed(() =>
  estadosMiembro.value.length > 0 && filters.value.estados.length === estadosMiembro.value.length
)

// Computed: ordenar tipos y motivos alfabéticamente
const tiposMiembroOrdenados = computed(() =>
  [...tiposMiembro.value].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
)
const motivosBajaOrdenados = computed(() =>
  [...motivosBaja.value].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
)

// Computed: agrupaciones en árbol jerárquico
const agrupacionesJerarquicas = computed(() => {
  const lista = agrupaciones.value
  if (!lista.length) return []

  const buildTree = (padreId = null, nivel = 0) => {
    const hijos = lista
      .filter(a => a.agrupacionPadreId === padreId)
      .sort((a, b) => {
        const nA = a.tipoUnidad?.nivel || 99
        const nB = b.tipoUnidad?.nivel || 99
        if (nA !== nB) return nA - nB
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

// Computed: campos del FilterBar
const filterFields = computed(() => [
  {
    key: 'agrupacion',
    label: 'Agrupación',
    type: 'select',
    options: agrupacionesJerarquicas.value.map(a => ({ value: a.id, label: a.displayNombre })),
    allLabel: 'Todas las agrupaciones',
    width: 'w-72',
  },
  {
    key: 'estados',
    label: 'Situación',
    type: 'custom',
    defaultValue: [],
    isActive: (val) => val?.length > 0 && val.length < estadosMiembro.value.length,
    pillLabel: (val) => {
      if (!val?.length || val.length === estadosMiembro.value.length) return 'Situación'
      return `Situación · ${val.length}`
    },
  },
  {
    key: 'tipos',
    label: 'Tipo',
    type: 'multiselect',
    options: tiposMiembroOrdenados.value.map(t => ({ value: t.id, label: t.nombre })),
    allLabel: 'Todos',
    width: 'w-56',
  },
  {
    key: 'soloVoluntarios',
    label: 'Solo voluntarios',
    type: 'toggle',
  },
  {
    key: 'soloConAcceso',
    label: 'Con acceso a la app',
    type: 'toggle',
  },
  { key: 'motivoBaja', type: 'custom', hidden: true, defaultValue: '' },
])

// Computed: literal descriptivo del criterio de búsqueda
const descripcionBusqueda = computed(() => {
  // Tipos
  let tipoStr
  const tiposSeleccionados = filters.value.tipos
    .map(id => tiposMiembro.value.find(t => t.id === id)?.nombre)
    .filter(Boolean)
  if (tiposSeleccionados.length === 0 || tiposSeleccionados.length === tiposMiembro.value.length) {
    tipoStr = 'socios'
  } else if (tiposSeleccionados.length === 1) {
    tipoStr = tiposSeleccionados[0]
  } else {
    tipoStr = tiposSeleccionados.slice(0, -1).join(', ') + ' y ' + tiposSeleccionados.slice(-1)
  }

  // Situación
  let situacionStr
  const estadosSeleccionados = filters.value.estados
    .map(id => {
      const e = estadosMiembro.value.find(e => e.id === id)
      if (!e) return null
      if (e.nombre === 'Baja' && filters.value.motivoBaja) {
        const m = motivosBaja.value.find(m => m.id === filters.value.motivoBaja)
        return m ? `baja por ${m.nombre.toLowerCase()}` : 'baja'
      }
      return e.nombre.toLowerCase()
    })
    .filter(Boolean)
  if (estadosSeleccionados.length === 0 || estadosSeleccionados.length === estadosMiembro.value.length) {
    situacionStr = 'en cualquier situación'
  } else if (estadosSeleccionados.length === 1) {
    situacionStr = `en situación ${estadosSeleccionados[0]}`
  } else {
    situacionStr = `en situación ${estadosSeleccionados.slice(0, -1).join(', ')} o ${estadosSeleccionados.slice(-1)}`
  }

  // Agrupación
  let agrupStr
  if (filters.value.agrupacion) {
    const agrup = agrupaciones.value.find(a => a.id === filters.value.agrupacion)
    agrupStr = agrup ? `pertenecientes a ${agrup.nombre}` : ''
  } else {
    agrupStr = 'de todas las agrupaciones'
  }

  // Voluntarios
  const volStr = filters.value.soloVoluntarios ? ', solo voluntarios' : ''

  return `${tipoStr} ${situacionStr} ${agrupStr}${volStr}`
})

// Toggle colapso de agrupación en la tabla jerárquica
const toggleAgrupacion = (id) => {
  const s = new Set(colapsadas.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  colapsadas.value = s
}

// Mapa agrupacionId → miembros directos en el resultado filtrado
const miembrosPorAgrupacion = computed(() => {
  const map = {}
  miembros.value.forEach(m => {
    const key = m.agrupacion?.id ?? '__sin__'
    if (!map[key]) map[key] = []
    map[key].push(m)
  })
  return map
})

// Lista plana de filas { type, agrupacion|miembro, depth, countTotal } para la tabla jerárquica
const filasJerarquicas = computed(() => {
  const rows = []
  const mapa = miembrosPorAgrupacion.value
  const alpha = (a, b) => a.nombre.localeCompare(b.nombre, 'es')
  const alphaM = (a, b) => {
    const c = (a.apellido1 || '').localeCompare(b.apellido1 || '', 'es')
    if (c !== 0) return c
    return (a.apellido2 || '').localeCompare(b.apellido2 || '', 'es')
  }

  // Cuenta miembros (directos + descendientes) con datos ya filtrados
  const contarTotal = (agrupId) => {
    const ids = getDescendantIds(agrupId)
    return miembros.value.filter(m => m.agrupacion?.id && ids.has(m.agrupacion.id)).length
  }

  const walk = (agrup, depth) => {
    const total = contarTotal(agrup.id)
    if (total === 0) return

    const colapsada = colapsadas.value.has(agrup.id)
    rows.push({ type: 'agrupacion', agrupacion: agrup, depth, countTotal: total, colapsada })

    if (!colapsada) {
      const directos = (mapa[agrup.id] || []).slice().sort(alphaM)
      directos.forEach(m => rows.push({ type: 'miembro', miembro: m, depth: depth + 1 }))

      agrupaciones.value
        .filter(a => a.agrupacionPadreId === agrup.id)
        .sort(alpha)
        .forEach(hijo => walk(hijo, depth + 1))
    }
  }

  // Raíces: sin padre, o el nodo seleccionado en el filtro
  const raices = filters.value.agrupacion
    ? agrupaciones.value.filter(a => a.id === filters.value.agrupacion)
    : agrupaciones.value.filter(a => !a.agrupacionPadreId).sort(alpha)

  raices.forEach(r => walk(r, 0))

  // Miembros sin agrupación asignada
  const sinAgrup = (mapa['__sin__'] || []).slice().sort(alphaM)
  if (sinAgrup.length > 0) {
    const sinId = '__sin__'
    const colapsada = colapsadas.value.has(sinId)
    rows.push({ type: 'agrupacion', agrupacion: { id: sinId, nombre: 'Sin agrupación asignada' }, depth: 0, countTotal: sinAgrup.length, colapsada })
    if (!colapsada) {
      sinAgrup.forEach(m => rows.push({ type: 'miembro', miembro: m, depth: 1 }))
    }
  }

  return rows
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
      colapsadas.value = new Set([...agrupaciones.value.map(a => a.id), '__sin__'])
    }
  } catch (err) {
    console.error('Error al cargar miembros:', err)
  }
}

// Devuelve un Set con el ID dado y todos sus descendientes en el árbol de agrupaciones
const getDescendantIds = (rootId) => {
  const ids = new Set()
  const queue = [rootId]
  while (queue.length) {
    const id = queue.shift()
    ids.add(id)
    agrupaciones.value
      .filter(a => a.agrupacionPadreId === id)
      .forEach(a => queue.push(a.id))
  }
  return ids
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

  // Filtro por estados — si todos seleccionados o ninguno, no filtrar
  if (filters.value.estados.length > 0 && !todosEstadosSeleccionados.value) {
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

  // Filtro por agrupación (incluye todos los descendientes)
  if (filters.value.agrupacion) {
    const idsDescendientes = getDescendantIds(filters.value.agrupacion)
    filtered = filtered.filter(m => m.agrupacion?.id && idsDescendientes.has(m.agrupacion.id))
  }

  // Filtro solo voluntarios
  if (filters.value.soloVoluntarios) {
    filtered = filtered.filter(m => m.esVoluntario === true)
  }

  // Filtro con acceso a la aplicación (tiene usuario vinculado, activo o no)
  if (filters.value.soloConAcceso) {
    filtered = filtered.filter(m => m.tieneAcceso === true)
  }

  filtered.sort((a, b) => {
    const ap1 = (a.apellido1 || '').localeCompare(b.apellido1 || '', 'es')
    if (ap1 !== 0) return ap1
    const ap2 = (a.apellido2 || '').localeCompare(b.apellido2 || '', 'es')
    if (ap2 !== 0) return ap2
    return (a.nombre || '').localeCompare(b.nombre || '', 'es')
  })

  total.value = filtered.length
  miembros.value = filtered
}

// Limpiar filtros
const limpiarFiltros = () => {
  filters.value = {
    estados: [],
    motivoBaja: '',
    tipos: [],
    agrupacion: '',
    soloVoluntarios: false,
    soloConAcceso: false,
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
