<template>
  <AppLayout title="Organización Territorial"
    :subtitle="`Presencia de ${orgConfig.nombre || 'la asociación'} en el territorio`">

    <template v-if="tienePermiso('CFG_TERRITORIO_CREAR')" #actions>
      <button type="button" @click="irANuevaRaiz"
        class="h-8 px-3 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors">
        + Nueva unidad
      </button>
    </template>

    <!-- Filtros -->
    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar unidad organizativa..."
      :fields="filterFields"
      :lazy="true"
      :count-text="filtersApplied ? countText : ''"
      class="mb-4"
      @apply="aplicarFiltros"
      @clear="limpiarFiltros" />

    <!-- Loading / Error -->
    <EstadoCarga v-if="loading" />
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">{{ error }}</div>

    <!-- Controles de vista del árbol -->
    <div v-if="filtersApplied && arbolFiltrado.length" class="flex items-center justify-between mt-3 mb-2 px-1">
      <button
        @click="toggleTodos"
        class="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
        :title="todoExpandido ? 'Colapsar todo' : 'Expandir todo'"
      >
        <span class="inline-block w-3 text-center">{{ todoExpandido ? '▼' : '▶' }}</span>
        {{ todoExpandido ? 'Colapsar todo' : 'Expandir todo' }}
      </button>
      <div class="text-xs text-gray-500">{{ totalUnidadesVisibles }} unidades</div>
    </div>

    <!-- Árbol -->
    <div v-else class="bg-white rounded-lg shadow border border-gray-100 overflow-hidden">
      <EstadoPendiente v-if="!filtersApplied" />
      <div v-else-if="arbolFiltrado.length === 0" class="text-center py-12 text-gray-400 text-sm">
        No hay unidades que coincidan con los filtros
      </div>
    </div>
    <div v-if="filtersApplied && arbolFiltrado.length" class="bg-white rounded-lg shadow border border-gray-100 divide-y divide-gray-50">
      <NodoArbol
        v-for="nodo in arbolFiltrado"
        :key="nodo.id"
        :nodo="nodo"
        :tipos="tipos"
        :profundidad="0"
        :coordinador-map="coordinadorPorAgrupacion"
        :conteo-map="conteoPorAgrupacion"
        @editar="irAEditar"
        @eliminar="confirmarEliminar"
        @anadir-hijo="irAAnadirHijo"
      />
    </div>

    <!-- Modal confirmación eliminar -->
    <div v-if="unidadAEliminar" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
        <h3 class="font-semibold text-gray-900 mb-2">¿Archivar unidad?</h3>
        <p class="text-sm text-gray-600 mb-4">
          "{{ unidadAEliminar.nombre }}" quedará archivada y no aparecerá en el árbol.
          Se puede restaurar desde la papelera.
        </p>
        <ErrorAlert v-if="errorEliminar" :message="errorEliminar" />
        <div class="flex gap-3 justify-end">
          <button @click="unidadAEliminar = null; errorEliminar = ''"
            class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
          <button @click="ejecutarEliminar" :disabled="archivando"
            class="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50">
            {{ archivando ? 'Archivando…' : 'Archivar' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, reactive, computed, onMounted, onActivated, provide } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { usePermisos } from '@/composables/usePermisos.js'
import NodoArbol from './NodoArbol.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'

defineOptions({ name: 'DetalleAgrupacionesTerritoriales' })

const { tipos, unidades, coordinaciones, miembros, loading, error, cargarTipos, cargarArbol, construirArbol, archivarUnidad } = useUnidadesOrganizativas()
const filtersApplied = ref(false)
const orgConfig = useOrgConfigStore()
const router = useRouter()
const { tienePermiso } = usePermisos()

// Crear/editar viven en la vista de detalle (no en modal)
const irAEditar     = (nodo) => router.push(`/agrupaciones/${nodo.id}?edit=1`)
const irAAnadirHijo = (nodo) => router.push({ name: 'NuevaAgrupacion', query: { padre: nodo.id } })
const irANuevaRaiz  = () => router.push({ name: 'NuevaAgrupacion' })

// ── Estado de filtros ──────────────────────────────────────────────────────────
const busqueda = ref('')
const filtros  = ref({ agrupacionId: '' })

// ── Estado de borrado ───────────────────────────────────────────────────────────
const unidadAEliminar   = ref(null)
const errorEliminar     = ref('')
const archivando        = ref(false)

// ── Computeds ─────────────────────────────────────────────────────────────────

const arbolCompleto = computed(() => construirArbol(unidades.value))

const coordinadorPorAgrupacion = computed(() => {
  const map = {}
  coordinaciones.value.forEach(c => { map[c.agrupacionId] = c.miembro })
  return map
})

const conteoPorAgrupacion = computed(() => {
  const map = {}
  miembros.value.forEach(m => {
    if (!m.agrupacionId || !m.activo) return
    if (!map[m.agrupacionId]) map[m.agrupacionId] = { militantes: 0, voluntarios: 0 }
    map[m.agrupacionId].militantes++
    if (m.esVoluntario) map[m.agrupacionId].voluntarios++
  })
  return map
})

// Lista plana con indentación para el selector de agrupación en el filtro
const agrupacionesParaFiltro = computed(() => {
  const flatten = (nodos, nivel = 0) => {
    const result = []
    for (const n of nodos) {
      result.push({ value: n.id, label: '  '.repeat(nivel) + n.nombre })
      result.push(...flatten(n.hijos, nivel + 1))
    }
    return result
  }
  return flatten(arbolCompleto.value)
})

const hayFiltros = computed(() =>
  busqueda.value.trim() || filtros.value.agrupacionId
)

const nodoMatchesFiltros = (nodo) => {
  if (busqueda.value.trim() && !nodo.nombre.toLowerCase().includes(busqueda.value.toLowerCase().trim())) return false
  return true
}

const filtrarArbol = (nodos) => nodos
  .map(n => ({ ...n, hijos: filtrarArbol(n.hijos) }))
  .filter(n => nodoMatchesFiltros(n) || n.hijos.length > 0)

const encontrarSubarbol = (nodos, id) => {
  for (const n of nodos) {
    if (n.id === id) return [n]
    const found = encontrarSubarbol(n.hijos, id)
    if (found) return found
  }
  return null
}

const arbolFiltrado = computed(() => {
  let base = arbolCompleto.value
  if (filtros.value.agrupacionId)
    base = encontrarSubarbol(base, filtros.value.agrupacionId) ?? base
  if (!busqueda.value.trim()) return base
  return filtrarArbol(base)
})

const totalNodos = computed(() => {
  const contar = (nodos) => nodos.reduce((acc, n) => acc + 1 + contar(n.hijos), 0)
  return contar(arbolFiltrado.value)
})

const totalUnidadesVisibles = computed(() => totalNodos.value)

// ── Expandir / colapsar (mismo patrón que el árbol del Plan de Cuentas) ──────
const expandedMap = reactive({})

const toggleNodo = (id) => {
  if (expandedMap[id]) delete expandedMap[id]
  else expandedMap[id] = true
}

const todosIds = (nodes) => {
  const ids = []
  const walk = (xs) => { for (const n of xs) { ids.push(n.id); walk(n.hijos || []) } }
  walk(nodes)
  return ids
}

const totalNodosExpandibles = computed(() => {
  let n = 0
  const walk = (xs) => { for (const x of xs) { if ((x.hijos || []).length) { n++; walk(x.hijos) } } }
  walk(arbolFiltrado.value)
  return n
})

const todoExpandido = computed(() =>
  totalNodosExpandibles.value > 0 &&
  Object.keys(expandedMap).length >= totalNodosExpandibles.value
)

const toggleTodos = () => {
  if (todoExpandido.value) {
    for (const k of Object.keys(expandedMap)) delete expandedMap[k]
  } else {
    for (const id of todosIds(arbolFiltrado.value)) expandedMap[id] = true
  }
}

provide('expandedMap', expandedMap)
provide('toggleNodo', toggleNodo)

// ── FilterBar fields ──────────────────────────────────────────────────────────

const filterFields = computed(() => {
  const nombreTipo = orgConfig.tipoAgrupacion || 'Agrupación'
  const nombreTipoPlural = nombreTipo.endsWith('ón')
    ? nombreTipo.slice(0, -2) + 'ones'
    : nombreTipo.endsWith('n')
      ? nombreTipo + 'es'
      : nombreTipo + 's'
  return [
  {
    key: 'agrupacionId',
    label: nombreTipo,
    type: 'select',
    options: agrupacionesParaFiltro.value,
    allLabel: `Todas las ${nombreTipoPlural.toLowerCase()}`,
    width: 'w-72',
  },
]})

const countText = computed(() => {
  if (!hayFiltros.value) return ''
  return `${totalNodos.value} unidad${totalNodos.value !== 1 ? 'es' : ''}`
})

// ── Helpers ───────────────────────────────────────────────────────────────────

const limpiarFiltros = () => { busqueda.value = '' }

async function aplicarFiltros() {
  if (!filtersApplied.value) {
    await cargarArbol()
  }
  filtersApplied.value = true
}

// ── Borrado ───────────────────────────────────────────────────────────────────

const confirmarEliminar = (nodo) => {
  if (nodo.hijos?.length) return
  errorEliminar.value = ''
  unidadAEliminar.value = nodo
}

const ejecutarEliminar = async () => {
  archivando.value = true
  errorEliminar.value = ''
  try {
    await archivarUnidad(unidadAEliminar.value.id)
    unidadAEliminar.value = null
  } catch (e) {
    errorEliminar.value = e.message || 'No se pudo archivar la unidad.'
  } finally {
    archivando.value = false
  }
}

// ── Carga de datos ────────────────────────────────────────────────────────────

onMounted(async () => {
  await cargarTipos()
  await cargarArbol()
  filtersApplied.value = true
})

onActivated(async () => {
  await cargarTipos()
})
</script>
