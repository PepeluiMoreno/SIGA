<template>
  <div class="relative" ref="raiz">
    <label v-if="label" class="block text-sm font-medium text-slate-700 mb-1.5">{{ label }}</label>

    <!-- Lectura / no editable: muestra la selección con el aspecto de un campo readonly -->
    <div v-if="!editing"
      class="h-10 w-full px-3 flex items-center text-sm text-slate-800 bg-slate-50 border border-slate-200 rounded-lg">
      <span v-if="seleccion" class="truncate">
        {{ seleccion.nombre }}<span class="text-slate-400 text-xs"> · {{ seleccion.ruta }}</span>
      </span>
      <span v-else class="text-slate-400">—</span>
    </div>

    <!-- Edición -->
    <template v-else>
      <!-- Selección fijada: chip con el mismo marco que un input -->
      <div v-if="seleccion"
        class="h-10 w-full px-3 flex items-center gap-2 border border-slate-300 rounded-lg bg-white">
        <span class="flex-1 min-w-0 truncate text-sm text-slate-800">
          {{ seleccion.nombre }}<span class="text-slate-400 text-xs"> · {{ seleccion.ruta }}</span>
        </span>
        <button type="button" @click="limpiar"
          class="flex-shrink-0 text-slate-400 hover:text-red-500 text-lg leading-none" title="Quitar">×</button>
      </div>

      <!-- Buscador: input con el estilo canónico de la app -->
      <div v-else class="relative">
        <input v-model="termino" type="text" :placeholder="placeholder"
          class="h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all
                 bg-white text-slate-800 placeholder:text-slate-400
                 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
          @input="onInput" @focus="onInput" />
        <!-- Spinner de carga -->
        <span v-if="cargando"
          class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin"></span>
      </div>

      <!-- Resultados -->
      <ul v-if="!seleccion && resultados.length"
        class="absolute z-30 mt-1 w-full max-h-64 overflow-auto bg-white border border-slate-200 rounded-lg shadow-lg">
        <li v-for="r in resultados" :key="r.id" @click="elegir(r)"
          class="px-3 py-2 hover:bg-indigo-50 cursor-pointer border-b border-slate-50 last:border-0">
          <span class="text-sm text-slate-800">{{ r.nombre }}</span>
          <span class="block text-[11px] text-slate-400">{{ r.ruta }}</span>
        </li>
      </ul>

      <!-- Estados: error de búsqueda / sin resultados -->
      <p v-if="!seleccion && errorBusqueda"
        class="mt-1 text-xs text-red-600 flex items-center gap-1">
        <span>⚠</span> No se pudo buscar la ubicación. {{ errorBusqueda }}
      </p>
      <p v-else-if="!seleccion && termino.trim().length >= 2 && !cargando && !resultados.length"
        class="mt-1 text-xs text-slate-400">Sin resultados para «{{ termino.trim() }}».</p>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { graphqlClient } from '@/graphql/client.js'

const props = defineProps({
  modelValue: { type: String, default: null },   // entidad_geografica_id
  label: { type: String, default: '' },
  editing: { type: Boolean, default: true },
  // Filtra por nivel(es): 0 país, 1 CCAA, 2 provincia, 3 municipio, 4+ pedanía. Vacío = todos.
  niveles: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Buscar municipio, provincia…' },
  // Ámbito raíz: id de una entidad geográfica. Si se indica, la búsqueda se ACOTA a esa
  // entidad y sus descendientes (por prefijo de `ruta`). Usado para enganchar este buscador
  // al de la agrupación superior: al elegir "Cádiz Laica" (prov. Cádiz), buscar ubicación
  // solo devuelve municipios de Cádiz. Al cambiar la raíz se limpia la selección incoherente.
  raizId: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue', 'seleccion'])

const QUERY = `
  query EntidadesGeograficas($filter: EntidadGeograficaFilter!) {
    entidadesGeograficas(filter: $filter) { id codigo nombre ruta nivel }
  }`

const raiz = ref(null)
const termino = ref('')
const resultados = ref([])
const seleccion = ref(null)
const cargando = ref(false)
const errorBusqueda = ref('')
const raizRuta = ref('')   // ruta de la entidad raíz (para acotar por prefijo)
let timer = null

function _filtro(extra) {
  const f = { ...extra }
  if (props.niveles.length) f.nivel = { in: props.niveles }
  // Acota al ámbito raíz: la ruta de los resultados debe empezar por la de la raíz.
  if (raizRuta.value) f.ruta = { ...(f.ruta || {}), startswith: raizRuta.value }
  return f
}

// Carga la ruta de la entidad raíz para poder acotar por prefijo.
async function cargarRaiz(id) {
  if (!id) { raizRuta.value = ''; return }
  try {
    const d = await graphqlClient.request(QUERY, { filter: { id: { eq: id } } })
    raizRuta.value = (d.entidadesGeograficas || [])[0]?.ruta || ''
  } catch { raizRuta.value = '' }
}

async function cargarSeleccion(id) {
  if (!id) { seleccion.value = null; return }
  try {
    const d = await graphqlClient.request(QUERY, { filter: { id: { eq: id } } })
    seleccion.value = (d.entidadesGeograficas || [])[0] || null
  } catch { seleccion.value = null }
}

function onInput() {
  clearTimeout(timer)
  errorBusqueda.value = ''
  const t = termino.value.trim()
  if (t.length < 2) { resultados.value = []; cargando.value = false; return }
  cargando.value = true
  timer = setTimeout(async () => {
    try {
      const d = await graphqlClient.request(QUERY, { filter: _filtro({ nombre: { ilike: `%${t}%` } }) })
      resultados.value = (d.entidadesGeograficas || []).slice(0, 25)
    } catch (e) {
      // No tragarse el fallo: mostrarlo (el usuario debe saber que el buscador no respondió).
      resultados.value = []
      errorBusqueda.value = e?.response?.errors?.[0]?.message || e?.message || 'Error de conexión.'
    } finally {
      cargando.value = false
    }
  }, 250)
}

function elegir(r) {
  seleccion.value = r
  resultados.value = []
  termino.value = ''
  errorBusqueda.value = ''
  emit('update:modelValue', r.id)
  emit('seleccion', r)   // entidad completa (id, nombre, ruta, nivel)
}

function limpiar() {
  seleccion.value = null
  errorBusqueda.value = ''
  emit('update:modelValue', null)
  emit('seleccion', null)
}

function onClickFuera(e) {
  if (raiz.value && !raiz.value.contains(e.target)) resultados.value = []
}

onMounted(() => {
  document.addEventListener('click', onClickFuera)
  if (props.modelValue) cargarSeleccion(props.modelValue)
  if (props.raizId) cargarRaiz(props.raizId)
})
onBeforeUnmount(() => document.removeEventListener('click', onClickFuera))

watch(() => props.modelValue, (nuevo) => {
  if (!nuevo) { seleccion.value = null; return }
  if (!seleccion.value || seleccion.value.id !== nuevo) cargarSeleccion(nuevo)
})

// Al cambiar el ámbito raíz (p.ej. se elige otra agrupación superior): recargar su ruta.
// Si la selección actual ya no cae dentro del nuevo ámbito, se limpia (es incoherente).
watch(() => props.raizId, async (nuevo) => {
  await cargarRaiz(nuevo)
  termino.value = ''
  resultados.value = []
  if (seleccion.value && raizRuta.value && !(seleccion.value.ruta || '').startsWith(raizRuta.value)) {
    limpiar()
  }
})
</script>
