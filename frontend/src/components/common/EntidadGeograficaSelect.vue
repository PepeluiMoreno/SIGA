<template>
  <div class="relative" ref="raiz">
    <label v-if="label" class="label">{{ label }}</label>

    <!-- Lectura / no editable: muestra la selección -->
    <div v-if="!editing" class="text-sm text-slate-800 bg-slate-50 border border-slate-200 rounded-lg px-3 h-10 flex items-center">
      <span v-if="seleccion">{{ seleccion.nombre }}<span class="text-slate-400 text-xs"> · {{ seleccion.ruta }}</span></span>
      <span v-else class="text-slate-400">—</span>
    </div>

    <!-- Edición -->
    <template v-else>
      <!-- Selección fijada -->
      <div v-if="seleccion" class="flex items-center gap-2 border border-slate-300 rounded-lg px-3 h-10 bg-white">
        <span class="flex-1 min-w-0 truncate text-sm text-slate-800">{{ seleccion.nombre }}<span class="text-slate-400 text-xs"> · {{ seleccion.ruta }}</span></span>
        <button type="button" @click="limpiar" class="flex-shrink-0 text-slate-400 hover:text-red-500" title="Quitar">×</button>
      </div>
      <!-- Buscador -->
      <input v-else v-model="termino" type="text" :placeholder="placeholder"
        class="input" @input="onInput" @focus="onInput" />
      <!-- Resultados -->
      <ul v-if="!seleccion && resultados.length"
        class="absolute z-20 mt-1 w-full max-h-64 overflow-auto bg-white border border-slate-200 rounded-lg shadow-lg">
        <li v-for="r in resultados" :key="r.codigo" @click="elegir(r)"
          class="px-3 py-2 text-sm hover:bg-indigo-50 cursor-pointer">
          <span class="text-slate-800">{{ r.nombre }}</span>
          <span class="block text-[11px] text-slate-400">{{ r.ruta }}</span>
        </li>
      </ul>
      <p v-if="!seleccion && termino.length >= 2 && !cargando && !resultados.length"
        class="mt-1 text-xs text-slate-400">Sin resultados.</p>
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
  // Filtra por nivel(es): 0 país, 1 CCAA, 2 provincia, 3 municipio. Vacío = todos.
  niveles: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Buscar municipio o provincia…' },
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
let timer = null

function _filtro(extra) {
  const f = { ...extra }
  if (props.niveles.length) f.nivel = { in: props.niveles }
  return f
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
  const t = termino.value.trim()
  if (t.length < 2) { resultados.value = []; return }
  timer = setTimeout(async () => {
    cargando.value = true
    try {
      const d = await graphqlClient.request(QUERY, { filter: _filtro({ nombre: { ilike: `%${t}%` } }) })
      resultados.value = (d.entidadesGeograficas || []).slice(0, 25)
    } catch { resultados.value = [] }
    finally { cargando.value = false }
  }, 250)
}

function elegir(r) {
  seleccion.value = r
  resultados.value = []
  termino.value = ''
  emit('update:modelValue', r.id)
  emit('seleccion', r)   // entidad completa (id, nombre, ruta, nivel)
}

function limpiar() {
  seleccion.value = null
  emit('update:modelValue', null)
  emit('seleccion', null)
}

function onClickFuera(e) {
  if (raiz.value && !raiz.value.contains(e.target)) resultados.value = []
}

onMounted(() => {
  document.addEventListener('click', onClickFuera)
  if (props.modelValue) cargarSeleccion(props.modelValue)
})
onBeforeUnmount(() => document.removeEventListener('click', onClickFuera))

watch(() => props.modelValue, (nuevo) => {
  if (!nuevo) { seleccion.value = null; return }
  if (!seleccion.value || seleccion.value.id !== nuevo) cargarSeleccion(nuevo)
})
</script>
