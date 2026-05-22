<template>
  <div ref="rootRef" class="flex items-center gap-1 flex-wrap text-sm">
    <span class="text-xs font-medium text-slate-500 shrink-0 mr-0.5">Ámbito:</span>

    <!-- Breadcrumb de niveles -->
    <template v-for="(nivel, idx) in niveles" :key="idx">
      <ChevronRightIcon v-if="idx > 0" class="w-3.5 h-3.5 text-slate-300 shrink-0" />

      <div class="relative shrink-0">
        <button
          type="button"
          @click.stop="toggle(idx)"
          class="inline-flex items-center gap-1 h-8 px-2.5 rounded-lg border text-sm transition-colors"
          :class="nivel.seleccionado
            ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium'
            : 'bg-white border-slate-200 text-slate-500 hover:border-slate-300'"
        >
          <span class="max-w-[140px] truncate">
            {{ nivel.seleccionado ? nivel.seleccionado.nombre : (nivel.tipoLabel || 'Todas') }}
          </span>
          <ChevronDownIcon class="w-3 h-3 opacity-60 transition-transform" :class="abierto === idx ? 'rotate-180' : ''" />
        </button>

        <!-- Popover del nivel -->
        <div
          v-if="abierto === idx"
          class="absolute left-0 top-full mt-1 z-40 w-60 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden"
          @click.stop
        >
          <div v-if="nivel.opciones.length > 8" class="p-2 border-b border-slate-100">
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <input
                v-model="busqueda"
                type="text"
                :placeholder="`Buscar ${(nivel.tipoLabel || 'unidad').toLowerCase()}…`"
                class="w-full h-8 pl-7 pr-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                @click.stop
              />
            </div>
          </div>

          <div class="max-h-60 overflow-y-auto py-1">
            <button
              type="button"
              @click="elegir(idx, '')"
              class="w-full text-left px-3 py-1.5 text-sm transition-colors"
              :class="!nivel.seleccionado ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-600 hover:bg-slate-50'"
            >
              Todas{{ nivel.tipoLabel ? ` las ${nivel.tipoLabel.toLowerCase()}s` : '' }}
            </button>

            <button
              v-for="agr in opcionesFiltradas(nivel)"
              :key="agr.id"
              type="button"
              @click="elegir(idx, agr.id)"
              class="w-full text-left px-3 py-1.5 text-sm transition-colors flex items-center justify-between gap-2"
              :class="nivel.seleccionado?.id === agr.id ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700 hover:bg-slate-50'"
            >
              <span class="truncate">{{ agr.nombre }}</span>
              <ChevronRightIcon v-if="tieneHijos(agr.id)" class="w-3.5 h-3.5 text-slate-300 shrink-0" />
            </button>

            <p v-if="!opcionesFiltradas(nivel).length" class="px-3 py-2 text-xs text-slate-400">Sin resultados</p>
          </div>
        </div>
      </div>
    </template>

    <button
      v-if="haySeleccion"
      @click="limpiar"
      class="inline-flex items-center h-8 px-2 text-xs text-slate-400 hover:text-red-600 transition-colors shrink-0"
      title="Quitar filtro de ámbito"
    >
      <XMarkIcon class="w-3.5 h-3.5" />
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ChevronRightIcon, ChevronDownIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  agrupaciones: { type: Array, default: () => [] },
  modelValue:   { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const rootRef  = ref(null)
const abierto  = ref(null)
const busqueda = ref('')

function construirCadena(targetId) {
  const map = Object.fromEntries(props.agrupaciones.map(a => [a.id, a]))
  const cadena = []
  let curr = map[targetId]
  while (curr) {
    cadena.unshift(curr)
    curr = curr.agrupacionPadreId ? map[curr.agrupacionPadreId] : null
  }
  return cadena
}

function opcionesDeNivel(padreId) {
  return props.agrupaciones
    .filter(a => (padreId ? a.agrupacionPadreId === padreId : !a.agrupacionPadreId))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
}

function tieneHijos(id) {
  return props.agrupaciones.some(a => a.agrupacionPadreId === id)
}

const niveles = computed(() => {
  const cadena = props.modelValue ? construirCadena(props.modelValue) : []
  const resultado = []
  let padreId = null
  for (const agr of cadena) {
    const opciones = opcionesDeNivel(padreId)
    resultado.push({ seleccionado: agr, opciones, tipoLabel: opciones[0]?.tipoUnidad?.nombre ?? '' })
    padreId = agr.id
  }
  const siguiente = opcionesDeNivel(padreId)
  if (siguiente.length) {
    resultado.push({ seleccionado: null, opciones: siguiente, tipoLabel: siguiente[0]?.tipoUnidad?.nombre ?? '' })
  }
  return resultado
})

const haySeleccion = computed(() => !!props.modelValue)

function opcionesFiltradas(nivel) {
  if (!busqueda.value) return nivel.opciones
  const q = busqueda.value.toLowerCase()
  return nivel.opciones.filter(a => a.nombre.toLowerCase().includes(q))
}

function toggle(idx) {
  abierto.value = abierto.value === idx ? null : idx
  busqueda.value = ''
}

function elegir(idx, agrId) {
  abierto.value = null
  busqueda.value = ''
  if (!agrId) {
    const padre = idx > 0 ? niveles.value[idx - 1].seleccionado?.id : ''
    emit('update:modelValue', padre || '')
  } else {
    emit('update:modelValue', agrId)
  }
}

function limpiar() {
  abierto.value = null
  emit('update:modelValue', '')
}

function onClickOutside(e) {
  if (abierto.value !== null && rootRef.value && !rootRef.value.contains(e.target)) abierto.value = null
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))

watch(() => props.modelValue, () => { abierto.value = null })
</script>
