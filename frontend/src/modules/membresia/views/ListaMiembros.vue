<template>
  <AppLayout :title="orgConfig.Miembros" subtitle="Gestión, colaboración y disponibilidad" fluid>
    <!-- Acción principal en el topbar (estándar global) -->
    <template v-if="tienePermiso('MEMBRESIA_MIEMBRO_CREAR')" #actions>
      <router-link to="/miembros/nuevo"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nuevo {{ orgConfig.miembro }}
      </router-link>
    </template>

    <!-- Layout piloto: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">
    <FilterRail storage-key="miembros">
    <FilterBar
      vertical
      v-model="filters"
      v-model:search="searchQuery"
      :search-placeholder="`Buscar por nombre, apellido o email…`"
      :fields="filterFields"
      @clear="limpiarFiltros">

      <!-- Situación: dropdown personalizado con sub-selección de motivo de baja -->
      <template #dropdown-estados="{ filters: f, setFilters }">
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
            <input type="checkbox"
              :checked="f.estados.length === 0"
              @change="setFilters({ estados: [] })"
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

      <template #filters-prefix>
        <AmbitoTerritorialSelect v-model="filters.agrupacion" :agrupaciones="agrupaciones" />
      </template>

    </FilterBar>
    </FilterRail>

    <!-- Columna de resultados -->
    <div class="flex-1 min-w-0 w-full">
    <!-- Subtítulo dinámico de la consulta, compuesto según los filtros activos -->
    <p v-if="descripcionBusqueda" class="text-base font-medium text-slate-600 mb-3 first-letter:uppercase">{{ descripcionBusqueda }}</p>
    <!-- Estado de carga -->
    <EstadoCarga v-if="loading" mensaje="Cargando registros de militancia..." />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <p class="text-red-700 font-medium">Error al cargar datos</p>
      <p class="text-red-600 text-sm mt-1">{{ error.message || error }}</p>
      <button @click="loadMiembros" class="mt-3 text-red-600 hover:text-red-800 text-sm font-medium">
        Reintentar
      </button>
    </div>

    <!-- Resultados -->
    <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- Sin resultados -->
      <div v-if="miembros.length === 0" class="p-12 text-center text-gray-500">
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
          <div class="flex items-center gap-4">
            <button v-if="tienePermiso('SOC_EXPORT') && miembros.length"
              @click="exportarExcel" :disabled="exportando"
              class="inline-flex items-center gap-1.5 text-sm font-medium text-green-700 hover:text-green-900 disabled:opacity-50">
              <ArrowDownTrayIcon class="w-4 h-4" />
              {{ exportando ? 'Exportando…' : 'Exportar a Excel' }}
            </button>
            <button @click="limpiarFiltros" class="text-sm text-purple-600 hover:text-purple-800">Limpiar filtros</button>
          </div>
        </div>

        <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-200">
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
                    <ChevronRightIcon class="w-3.5 h-3.5 text-purple-400 shrink-0 transition-transform" />
                    <span class="text-sm font-semibold text-purple-800">{{ fila.agrupacion.nombre }}</span>
                    <span class="text-xs text-purple-400 font-normal">{{ fila.countTotal }} miembro{{ fila.countTotal !== 1 ? 's' : '' }}</span>
                  </div>
                </td>
              </tr>

              <!-- Fila de miembro -->
              <tr v-else class="hover:bg-purple-50 cursor-pointer"
                @click="abrirFicha(fila.miembro, false)">
                <td class="py-3 pr-4" :style="{ paddingLeft: (fila.depth * 20 + 16) + 'px' }">
                  <div class="flex items-center gap-3">
                    <AvatarImg
                      :src="fila.miembro.fotoUrl"
                      :nombre="fila.miembro.nombre"
                      :apellido="fila.miembro.apellido1"
                      size="sm"
                    />
                    <div>
                      <div class="text-sm font-medium text-gray-900">
                        {{ fila.miembro.apellido1 }}{{ fila.miembro.apellido2 ? ' ' + fila.miembro.apellido2 : '' }}, {{ fila.miembro.nombre }}
                      </div>
                      <div class="flex items-center gap-2 mt-0.5">
                        <span v-if="fila.miembro.tipoMiembro" class="text-xs text-gray-400">{{ fila.miembro.tipoMiembro.nombre }}</span>
                        <span v-if="fila.miembro.estado && fila.miembro.estado.nombre !== 'Alta'"
                          class="text-xs px-1.5 py-0.5 rounded-full font-medium"
                          :style="estadoBadgeStyle(fila.miembro.estado)">
                          {{ fila.miembro.estado.nombre }}
                        </span>
                        <span v-if="fila.miembro.esVoluntario" class="text-xs bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded-full">Voluntario</span>
                        <span v-if="fila.miembro.usuario?.activo" title="Tiene acceso a la aplicación"
                          class="inline-flex items-center gap-0.5 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">
                          <UserIcon class="w-3 h-3" />
                          App
                        </span>
                        <span v-for="n in (nombramientosMap[fila.miembro.id] || [])" :key="n.id"
                          :title="n.agrupacion?.nombre ? `Cargo en ${n.agrupacion.nombre}` : n.rol?.nombre"
                          class="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">
                          {{ n.rol?.nombre }}
                        </span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="text-xs text-gray-400 mb-1">Datos de contacto</p>
                  <div class="flex items-center gap-1.5 text-sm text-gray-700">
                    <EnvelopeIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" />
                    <span>{{ fila.miembro.email || '—' }}</span>
                  </div>
                  <div v-if="fila.miembro.telefono" class="flex items-center gap-1.5 text-xs text-gray-500 mt-0.5">
                    <PhoneIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" />
                    <span>{{ fila.miembro.telefono }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="text-xs text-gray-400 mb-1">Es socio desde</p>
                  <p class="text-sm text-gray-600">{{ formatDate(fila.miembro.fechaAlta) }}</p>
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button type="button" @click.stop="abrirFicha(fila.miembro, false)"
                      class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      title="Ver ficha">
                      <EyeIcon class="w-4 h-4" />
                    </button>
                    <button type="button" @click.stop="abrirFicha(fila.miembro, true)"
                      class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      title="Editar">
                      <PencilIcon class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>

            </template>
          </tbody>
        </table></div>
      </template>
    </div>
    </div><!-- /columna resultados -->
    </div><!-- /flex filtro + resultados -->

  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import { EyeIcon, PencilIcon , ChevronRightIcon, UserIcon} from '@heroicons/vue/24/outline'
import { useGraphQL } from '@/composables/useGraphQL.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_MIEMBROS, GET_AGRUPACIONES, GET_TIPOS_MIEMBRO, GET_ESTADOS_MIEMBRO, GET_MOTIVOS_BAJA, GET_NOMBRAMIENTOS_ACTIVOS } from '@/graphql/queries/miembros.js'
import AmbitoTerritorialSelect from '@/components/common/AmbitoTerritorialSelect.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
const toast = useToast()
const router = useRouter()

// ── Navegación a la ficha (vista completa) ──────────────────────────────────
function abrirFicha(m, editar) {
  router.push(editar
    ? { path: `/miembros/${m.id}`, query: { modo: 'editar' } }
    : `/miembros/${m.id}`)
}
const { loading, error, query, mutation } = useGraphQL()
const orgConfig = useOrgConfigStore()
const { tienePermiso } = usePermisos()

// Datos
const miembros = ref([])
const allMiembros = ref([])
const agrupaciones = ref([])
const tiposMiembro = ref([])
const estadosMiembro = ref([])
const motivosBaja = ref([])
const nombramientosActivos = ref([])

// Mapa miembroId → nombramientos activos (para badges)
const nombramientosMap = computed(() => {
  const map = {}
  for (const n of nombramientosActivos.value) {
    if (!n.miembroId) continue
    if (!map[n.miembroId]) map[n.miembroId] = []
    map[n.miembroId].push(n)
  }
  return map
})

// Estado UI
const searchQuery = ref('')
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
  cargo: '',       // '' = todos, 'SIN_CARGO' = sin cargo, o codigo de rol
  soloVoluntarios: false,
  soloConAcceso: false,
  incluirBajas: false,  // por defecto los dados de baja no se listan
})

// Refiltrado reactivo: cualquier cambio de filtro re-aplica sobre los datos ya
// cargados (no hay recarga al servidor — todo el filtrado es en cliente).
watch(filters, () => {
  currentPage.value = 1
  applyClientFilters()
}, { deep: true })

// Si los catálogos llegan después de los miembros (por una recarga, caché,
// etc.), re-aplicamos los filtros: el filtro de bajas depende del id del
// estado Baja resuelto desde el catálogo.
watch(estadosMiembro, () => {
  if (allMiembros.value.length) applyClientFilters()
}, { deep: false })

// Búsqueda en tiempo real. Al buscar se despliegan todas las agrupaciones para
// que los resultados sean visibles; al vaciar la búsqueda se vuelven a colapsar.
watch(searchQuery, () => {
  currentPage.value = 1
  colapsadas.value = searchQuery.value.trim()
    ? new Set()
    : new Set([...agrupaciones.value.map(a => a.id), '__sin__'])
  applyClientFilters()
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

// Cargos únicos presentes en los nombramientos activos (para el filtro)
const cargosDisponibles = computed(() => {
  const seen = new Set()
  return nombramientosActivos.value
    .map(n => n.rol)
    .filter(r => r && !seen.has(r.codigo) && seen.add(r.codigo))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
})

// Computed: campos del FilterBar (el filtro geográfico va en AgrupacionCascada aparte)
const filterFields = computed(() => [
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
    key: 'cargo',
    label: 'Cargo',
    type: 'select',
    options: [
      { value: 'SIN_CARGO', label: 'Sin cargo' },
      ...cargosDisponibles.value.map(r => ({ value: r.codigo, label: r.nombre })),
    ],
    allLabel: 'Todos los cargos',
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
  {
    key: 'incluirBajas',
    label: 'Incluir las bajas',
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
    agrupaciones.value = agrupData?.unidadesOrganizativas || []

    const tiposData = await query(GET_TIPOS_MIEMBRO)
    tiposMiembro.value = tiposData?.tiposMiembro || []

    const estadosData = await query(GET_ESTADOS_MIEMBRO)
    estadosMiembro.value = estadosData?.estadosMiembro || []

    const motivosData = await query(GET_MOTIVOS_BAJA)
    motivosBaja.value = motivosData?.motivosBaja || []

    const nombramientosData = await query(GET_NOMBRAMIENTOS_ACTIVOS)
    nombramientosActivos.value = nombramientosData?.historialNombramientos || []
  } catch (err) {
    console.error('Error al cargar catálogos:', err)
  }
}

// Cargar todos los socios (una sola vez). El filtrado posterior es en cliente.
const loadMiembros = async () => {
  try {
    const data = await query(GET_MIEMBROS)
    allMiembros.value = data?.miembros || []
    // La situación ya no cuelga del catálogo EstadoMiembro: es `estado_socio`
    // (Activo/Suspendido/Baja). Las opciones del filtro salen de los estados
    // realmente presentes en los datos (cada uno con su id estable del backend).
    const situaciones = new Map()
    for (const m of allMiembros.value) {
      const e = m.estado
      if (e && e.id && !situaciones.has(e.id)) {
        situaciones.set(e.id, { id: e.id, nombre: e.nombre, color: e.color })
      }
    }
    if (situaciones.size) {
      estadosMiembro.value = [...situaciones.values()]
    }
    colapsadas.value = new Set([...agrupaciones.value.map(a => a.id), '__sin__'])
    applyClientFilters()
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

  // Los dados de baja se ocultan salvo que se marque "Incluir las bajas".
  // Si los catálogos aún no han cargado, `estadoBajaId.value` puede ser
  // undefined; en ese caso filtramos por nombre como fallback para no dejar
  // que cuelen los de baja sin querer.
  if (!filters.value.incluirBajas) {
    const bajaId = estadoBajaId.value
    filtered = filtered.filter(m => bajaId
      ? m.estado?.id !== bajaId
      : m.estado?.nombre !== 'Baja')
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

  // Filtro por cargo
  if (filters.value.cargo) {
    if (filters.value.cargo === 'SIN_CARGO') {
      filtered = filtered.filter(m => !nombramientosMap.value[m.id]?.length)
    } else {
      filtered = filtered.filter(m =>
        nombramientosMap.value[m.id]?.some(n => n.rol?.codigo === filters.value.cargo)
      )
    }
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

// Limpiar filtros — los watchers re-aplican el filtrado sobre los datos cargados.
const limpiarFiltros = () => {
  filters.value = {
    estados: [],
    motivoBaja: '',
    tipos: [],
    agrupacion: '',
    cargo: '',
    soloVoluntarios: false,
    soloConAcceso: false,
    incluirBajas: false,
  }
  searchQuery.value = ''
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

// Estilo del badge de situación, teñido con el color del estado del catálogo.
const estadoBadgeStyle = (estado) => {
  const hex = (estado?.color || '#64748b').replace('#', '')
  const r = parseInt(hex.slice(0, 2), 16) || 100
  const g = parseInt(hex.slice(2, 4), 16) || 116
  const b = parseInt(hex.slice(4, 6), 16) || 139
  return { background: `rgba(${r},${g},${b},0.15)`, color: estado?.color || '#64748b' }
}

// ── Exportación a Excel ───────────────────────────────────────────────────────
const exportando = ref(false)
const EXPORTAR_MIEMBROS_XLSX = `
  mutation ExportarMiembros($ids: [UUID!]!) {
    exportarMiembrosXlsx(ids: $ids)
  }
`
const exportarExcel = async () => {
  if (!miembros.value.length) return
  exportando.value = true
  try {
    const ids = miembros.value.map(m => m.id)
    const data = await mutation(EXPORTAR_MIEMBROS_XLSX, { ids })
    const bytes = Uint8Array.from(atob(data.exportarMiembrosXlsx), c => c.charCodeAt(0))
    const blob = new Blob([bytes], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `socios_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Error exportando:', e)
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo exportar el listado.')
  } finally {
    exportando.value = false
  }
}

// Montar — cargar catálogos y socios de inmediato (sin pantalla de espera).
onMounted(async () => {
  await loadCatalogos()
  await loadMiembros()
})
</script>
