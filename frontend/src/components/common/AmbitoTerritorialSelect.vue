<template>
  <!-- Sin jerarquía territorial (org sin despliegue) no se muestra nada -->
  <div v-if="niveles.length" class="space-y-2">
    <span class="block text-xs font-semibold text-slate-500 uppercase tracking-wide">Ámbito territorial</span>

    <!-- Un desplegable por nivel de la jerarquía: solo se muestran los niveles que existen -->
    <select
      v-for="(nivel, idx) in niveles"
      :key="idx"
      :value="nivel.seleccionadoId"
      @change="elegir(idx, $event.target.value)"
      class="w-full h-9 px-2.5 text-sm border border-slate-300 rounded-lg bg-white text-slate-700
             focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
    >
      <option value="">{{ nivel.tipoLabel ? `Todas · ${nivel.tipoLabel}` : 'Todas' }}</option>
      <option v-for="op in nivel.opciones" :key="op.id" :value="op.id">{{ op.nombre }}</option>
    </select>

    <button v-if="modelValue" type="button" @click="limpiar"
      class="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-red-600 transition-colors">
      <XMarkIcon class="w-3.5 h-3.5" />
      Quitar ámbito
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  agrupaciones: { type: Array,  default: () => [] },
  modelValue:   { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

function porId() {
  return Object.fromEntries(props.agrupaciones.map(a => [a.id, a]))
}

// Cadena raíz → nodo seleccionado, para reconstruir los niveles ya elegidos.
function construirCadena(targetId) {
  const map = porId()
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

// Lista de niveles a mostrar: los ya seleccionados + el siguiente (si existe).
// Cada nivel sin opciones desaparece, así que con jerarquía de profundidad 1
// solo se ve un desplegable.
const niveles = computed(() => {
  const cadena = props.modelValue ? construirCadena(props.modelValue) : []
  const res = []
  let padreId = null
  for (const agr of cadena) {
    const opciones = opcionesDeNivel(padreId)
    res.push({ seleccionadoId: agr.id, opciones, tipoLabel: opciones[0]?.tipoUnidad?.nombre ?? '' })
    padreId = agr.id
  }
  const siguiente = opcionesDeNivel(padreId)
  if (siguiente.length) {
    res.push({ seleccionadoId: '', opciones: siguiente, tipoLabel: siguiente[0]?.tipoUnidad?.nombre ?? '' })
  }
  return res
})

function elegir(idx, val) {
  if (!val) {
    // "Todas" en este nivel → sube al padre (o limpia si es el nivel raíz)
    const padre = idx > 0 ? niveles.value[idx - 1].seleccionadoId : ''
    emit('update:modelValue', padre || '')
  } else {
    emit('update:modelValue', val)
  }
}

function limpiar() {
  emit('update:modelValue', '')
}
</script>
