<template>
  <AppLayout :title="orgConfig.tipoAgrupacion || 'Unidades organizativas'" subtitle="Árbol de unidades de la organización">

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
        @editar="abrirFormulario"
        @eliminar="confirmarEliminar"
        @anadir-hijo="abrirFormularioHijo"
      />
    </div>

    <!-- Modal formulario -->
    <div v-if="mostrarFormulario" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">
            {{ editando ? 'Editar unidad' : (form.agrupacionPadreId ? 'Nueva sub-unidad' : 'Nueva unidad raíz') }}
          </h3>
          <button @click="cerrarFormulario" class="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
              <input v-model="form.nombre" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre corto</label>
              <input v-model="form.nombreCorto" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de unidad *</label>
              <select v-model="form.tipoId" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Seleccionar tipo...</option>
                <option v-for="t in tiposDisponibles" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
              <p v-if="tiposDisponibles.length === 0" class="text-xs text-amber-600 mt-1">
                Define los niveles en Parámetros · Estructura organizativa.
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Depende de</label>
              <select v-model="form.agrupacionPadreId" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Sin unidad padre</option>
                <option v-for="u in unidadesSinActual" :key="u.id" :value="u.id">{{ u.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">País *</label>
              <select v-model="form.paisId" @change="form.provinciaId = ''" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Seleccionar país...</option>
                <option v-for="p in paises" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Provincia</label>
              <select v-model="form.provinciaId" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Sin provincia</option>
                <option v-for="p in provinciasDelPais" :key="p.id" :value="p.id">
                  <template v-if="p.comunidadAutonoma">{{ p.comunidadAutonoma }} — </template>{{ p.nombre }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input v-model="form.email" type="email" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input v-model="form.telefono" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Web</label>
              <input v-model="form.web" type="url" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea v-model="form.descripcion" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
            </div>
          </div>

          <!-- Datos jurídicos — solo si vínculo FILIAL o FEDERADA -->
          <template v-if="tipoSeleccionado && ['FILIAL','FEDERADA'].includes(tipoSeleccionado.vinculo)">
            <div class="border-t border-gray-100 pt-4">
              <h4 class="text-sm font-semibold text-gray-700 mb-3">Datos jurídicos</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">NIF / CIF</label>
                  <input v-model="form.nif" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha constitución</label>
                  <input v-model="form.fechaConstitucion" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Registro oficial</label>
                  <input v-model="form.registroOficial" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>
            </div>
          </template>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="cerrarFormulario" class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
          <button @click="guardarUnidad" :disabled="!form.nombre || !form.paisId"
            class="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
            {{ editando ? 'Guardar cambios' : 'Crear unidad' }}
          </button>
        </div>
      </div>
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
import { ref, reactive, computed, watch, onMounted, onActivated, provide } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useGraphQL } from '@/composables/useGraphQL'
import { useOrgConfigStore } from '@/stores/orgConfig'
import NodoArbol from './NodoArbol.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'

defineOptions({ name: 'DetalleAgrupacionesTerritoriales' })

const { tipos, unidades, coordinaciones, miembros, loading, error, cargarTipos, cargarArbol, construirArbol, crearUnidad, actualizarUnidad, archivarUnidad } = useUnidadesOrganizativas()
const filtersApplied = ref(false)
const { query: gqlQuery } = useGraphQL()
const orgConfig = useOrgConfigStore()

// ── Estado de filtros ──────────────────────────────────────────────────────────
const busqueda = ref('')
const filtros  = ref({ agrupacionId: '' })

// ── Estado formulario ─────────────────────────────────────────────────────────
const paises            = ref([])
const provincias        = ref([])
const mostrarFormulario = ref(false)
const editando          = ref(null)
const unidadAEliminar   = ref(null)
const errorEliminar     = ref('')
const archivando        = ref(false)

const formVacio = () => ({
  nombre: '', nombreCorto: '', tipoId: '', agrupacionPadreId: '',
  paisId: '', provinciaId: '', email: '', telefono: '', web: '', descripcion: '',
  nif: '', fechaConstitucion: '', registroOficial: '', activo: true,
})
const form = ref(formVacio())

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

const provinciasDelPais = computed(() => {
  if (!form.value.paisId) return []
  return provincias.value
    .filter(p => p.paisId === form.value.paisId && p.activo)
    .sort((a, b) => {
      const ca = (a.comunidadAutonoma ?? '').localeCompare(b.comunidadAutonoma ?? '', 'es')
      return ca !== 0 ? ca : a.nombre.localeCompare(b.nombre, 'es')
    })
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

const tipoSeleccionado = computed(() => tipos.value.find(t => t.id === form.value.tipoId) ?? null)

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

// Tipos disponibles según el contexto: raíz → sólo tipo raíz; hijo → sólo hijos del tipo del padre
const tiposDisponibles = computed(() => {
  const territoriales = tipos.value.filter(t => t.naturaleza === 'TERRITORIAL')
  const padreId = form.value.agrupacionPadreId
  if (!padreId) {
    return territoriales.filter(t => !t.padreTipoId)
  }
  const padre = unidades.value.find(u => u.id === padreId)
  if (!padre?.tipoId) return territoriales
  return territoriales.filter(t => t.padreTipoId === padre.tipoId)
})

// Auto-seleccionar tipo cuando sólo hay una opción disponible
watch(tiposDisponibles, (lista) => {
  if (lista.length === 1) {
    form.value.tipoId = lista[0].id
  } else if (!lista.find(t => t.id === form.value.tipoId)) {
    form.value.tipoId = ''
  }
})

const unidadesSinActual = computed(() =>
  unidades.value.filter(u => u.id !== editando.value)
)

// ── Helpers ───────────────────────────────────────────────────────────────────

const labelNaturaleza = (n) => ({ TERRITORIAL: 'Territorial', FUNCIONAL: 'Funcional', PROGRAMATICA: 'Programática', ADMINISTRATIVA: 'Administrativa' }[n] ?? '')

const limpiarFiltros = () => { busqueda.value = '' }

async function aplicarFiltros() {
  if (!filtersApplied.value) {
    await cargarArbol()
  }
  filtersApplied.value = true
}

// ── Formulario ────────────────────────────────────────────────────────────────

const abrirFormulario = (nodo) => {
  if (nodo) {
    editando.value = nodo.id
    form.value = {
      nombre:            nodo.nombre ?? '',
      nombreCorto:       nodo.nombreCorto ?? '',
      tipoId:            nodo.tipoId ?? '',
      agrupacionPadreId: nodo.agrupacionPadreId ?? '',
      paisId:            nodo.paisId ?? '',
      provinciaId:       nodo.provinciaId ?? '',
      email:             nodo.email ?? '',
      telefono:          nodo.telefono ?? '',
      web:               nodo.web ?? '',
      descripcion:       nodo.descripcion ?? '',
      nif:               nodo.nif ?? '',
      fechaConstitucion: nodo.fechaConstitucion ?? '',
      registroOficial:   nodo.registroOficial ?? '',
      activo:            nodo.activo ?? true,
    }
  } else {
    editando.value = null
    form.value = formVacio()
  }
  mostrarFormulario.value = true
}

const abrirFormularioHijo = (nodo) => {
  editando.value = null
  form.value = { ...formVacio(), agrupacionPadreId: nodo.id }
  mostrarFormulario.value = true
}

const cerrarFormulario = () => {
  mostrarFormulario.value = false
  editando.value = null
}

const guardarUnidad = async () => {
  const payload = { ...form.value }
  if (!payload.agrupacionPadreId)  payload.agrupacionPadreId = null
  if (!payload.tipoId)             payload.tipoId = null
  if (!payload.provinciaId)        payload.provinciaId = null
  if (!payload.fechaConstitucion)  payload.fechaConstitucion = null

  if (editando.value) {
    await actualizarUnidad({ id: editando.value, ...payload })
  } else {
    await crearUnidad(payload)
  }
  cerrarFormulario()
}

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

const cargarGeo = async () => {
  const [dataPaises, dataProvs] = await Promise.all([
    gqlQuery(`query { paises(filter: { activo: { eq: true } }) { id nombre } }`),
    gqlQuery(`query { provincias(filter: { activo: { eq: true } }) { id nombre comunidadAutonoma paisId activo } }`),
  ])
  paises.value     = (dataPaises.paises ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  provincias.value = (dataProvs.provincias ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
}

onMounted(async () => {
  await Promise.all([cargarTipos(), cargarGeo()])
  await cargarArbol()
  filtersApplied.value = true
})

onActivated(async () => {
  await cargarTipos()
})
</script>
