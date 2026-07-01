<template>
  <div ref="rootRef" class="relative">
    <!-- Disparador -->
    <button
      type="button"
      :disabled="disabled"
      @click.stop="toggle"
      class="w-full h-10 px-3 flex items-center gap-2 text-sm text-left border rounded-lg bg-white transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      :class="abierto ? 'border-indigo-400 ring-2 ring-indigo-500' : 'border-slate-300 hover:border-slate-400'"
    >
      <MapPinIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
      <span v-if="seleccionada" class="flex items-center gap-1.5 min-w-0 flex-1">
        <span class="truncate font-medium text-slate-800">{{ seleccionada.nombre }}</span>
        <span v-if="nivelNombre(seleccionada)" class="flex-shrink-0 px-1.5 py-0.5 text-[10px] rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200 leading-none">
          {{ nivelNombre(seleccionada) }}
        </span>
      </span>
      <span v-else class="flex-1 text-slate-400 truncate">{{ placeholder }}</span>
      <XMarkIcon v-if="seleccionada && !disabled" @click.stop="elegir(null)"
        class="w-4 h-4 text-slate-300 hover:text-red-500 flex-shrink-0 transition-colors" />
      <ChevronDownIcon class="w-4 h-4 text-slate-400 flex-shrink-0 transition-transform" :class="abierto ? 'rotate-180' : ''" />
    </button>

    <!-- Panel desplegable: buscador + árbol -->
    <div v-if="abierto"
      class="absolute z-50 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden">
      <div class="p-2 border-b border-slate-100">
        <div class="relative">
          <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            ref="inputRef"
            v-model="busqueda"
            type="text"
            placeholder="Buscar agrupación…"
            class="w-full h-9 pl-8 pr-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            @click.stop
          />
        </div>
      </div>

      <div class="max-h-72 overflow-y-auto py-1">
        <!-- Modo árbol (sin búsqueda): jerárquico, raíz primero -->
        <template v-if="!busqueda">
          <button
            v-for="node in arbolPlano"
            :key="node.id"
            type="button"
            @click="elegir(node)"
            class="w-full flex items-center gap-1.5 pr-3 py-1.5 text-sm transition-colors text-left"
            :style="{ paddingLeft: `${0.75 + node.depth * 1.15}rem` }"
            :class="node.id === modelValue ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="font-mono text-slate-300 select-none flex-shrink-0">{{ node.depth === 0 ? '●' : '└' }}</span>
            <span class="truncate">{{ node.nombre }}</span>
            <span v-if="nivelNombre(node)" class="flex-shrink-0 px-1.5 py-0.5 text-[10px] rounded-full bg-slate-100 text-slate-500 leading-none">
              {{ nivelNombre(node) }}
            </span>
          </button>
        </template>

        <!-- Modo búsqueda: lista aplanada con ruta (raíz primero, luego alfabético) -->
        <template v-else>
          <button
            v-for="node in resultadosBusqueda"
            :key="node.id"
            type="button"
            @click="elegir(node)"
            class="w-full flex flex-col items-start px-3 py-1.5 text-sm transition-colors text-left"
            :class="node.id === modelValue ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-1.5 min-w-0 w-full">
              <span class="truncate">{{ node.nombre }}</span>
              <span v-if="nivelNombre(node)" class="flex-shrink-0 px-1.5 py-0.5 text-[10px] rounded-full bg-slate-100 text-slate-500 leading-none">
                {{ nivelNombre(node) }}
              </span>
            </span>
            <span v-if="node.ruta" class="text-[11px] text-slate-400 truncate w-full">{{ node.ruta }}</span>
          </button>
        </template>

        <p v-if="(busqueda ? resultadosBusqueda.length : arbolPlano.length) === 0"
          class="px-3 py-3 text-xs text-slate-400 text-center">
          {{ agrupaciones.length ? 'Sin resultados' : 'No hay agrupaciones' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronDownIcon, MagnifyingGlassIcon, XMarkIcon, MapPinIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  // Lista de agrupaciones con { id, nombre, agrupacionPadreId, tipoUnidad? }
  agrupaciones: { type: Array, default: () => [] },
  modelValue:   { type: String, default: null },
  placeholder:  { type: String, default: 'Seleccionar agrupación…' },
  disabled:     { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const rootRef  = ref(null)
const inputRef = ref(null)
const abierto  = ref(false)
const busqueda = ref('')

const porId = computed(() => Object.fromEntries(props.agrupaciones.map(a => [a.id, a])))
const seleccionada = computed(() => (props.modelValue ? porId.value[props.modelValue] : null) || null)

const nivelNombre = (a) => a?.tipoUnidad?.nombre || null

// Árbol aplanado en orden DFS: raíces primero, hijos indentados; hermanos por
// orden alfabético. Cada nodo lleva su profundidad para la indentación.
const arbolPlano = computed(() => {
  const hijosDe = (padreId) => props.agrupaciones
    .filter(a => (padreId ? a.agrupacionPadreId === padreId : !a.agrupacionPadreId))
    .sort((x, y) => x.nombre.localeCompare(y.nombre, 'es'))
  const out = []
  const dfs = (nodo, depth) => {
    out.push({ ...nodo, depth })
    hijosDe(nodo.id).forEach(h => dfs(h, depth + 1))
  }
  hijosDe(null).forEach(r => dfs(r, 0))
  return out
})

// Ruta de ancestros ("Raíz › Padre") para dar contexto en la búsqueda.
const rutaDe = (id) => {
  const cadena = []
  let curr = porId.value[id]
  curr = curr?.agrupacionPadreId ? porId.value[curr.agrupacionPadreId] : null
  while (curr) {
    cadena.unshift(curr.nombre)
    curr = curr.agrupacionPadreId ? porId.value[curr.agrupacionPadreId] : null
  }
  return cadena.join(' › ')
}

// Búsqueda: aplana, conserva el orden del árbol (raíz primero), filtra por nombre.
const resultadosBusqueda = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return []
  return arbolPlano.value
    .filter(n => n.nombre.toLowerCase().includes(q))
    .map(n => ({ ...n, ruta: rutaDe(n.id) }))
})

function toggle() {
  if (props.disabled) return
  abierto.value = !abierto.value
  if (abierto.value) {
    busqueda.value = ''
    nextTick(() => inputRef.value?.focus())
  }
}

function elegir(node) {
  emit('update:modelValue', node ? node.id : null)
  abierto.value = false
  busqueda.value = ''
}

function onClickOutside(e) {
  if (abierto.value && rootRef.value && !rootRef.value.contains(e.target)) abierto.value = false
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))
watch(() => props.modelValue, () => { abierto.value = false })
</script>
