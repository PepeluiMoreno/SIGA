<template>
  <div class="flex items-center gap-1.5 flex-wrap">
    <span class="text-xs font-medium text-slate-500 shrink-0 mr-1">Ámbito:</span>
    <template v-for="(sel, idx) in selecciones" :key="idx">
      <span v-if="idx > 0" class="text-slate-300 text-sm shrink-0">›</span>
      <!-- Etiqueta del nivel (nombre del tipo de unidad) -->
      <span v-if="labelNivel(idx)" class="text-xs text-slate-400 shrink-0">{{ labelNivel(idx) }}</span>
      <select :value="sel" @change="cambiarNivel(idx, $event.target.value)"
        class="h-8 text-sm border border-slate-200 rounded-md px-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent">
        <option value="">{{ opcionesParaNivel(idx).length ? 'Todas' : '—' }}</option>
        <option v-for="agr in opcionesParaNivel(idx)" :key="agr.id" :value="agr.id">
          {{ agr.nombre }}
        </option>
      </select>
    </template>
    <button v-if="haySeleccion" @click="limpiar"
      class="text-xs text-slate-400 hover:text-slate-600 ml-1 underline-offset-2 hover:underline">
      Limpiar
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  agrupaciones: { type: Array, default: () => [] },
  modelValue:   { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

// La cascada arranca en el nivel superior de la jerarquía territorial (los
// órganos sin padre — la asociación que instala la aplicación) y desciende por
// el árbol real de unidades según `agrupacionPadreId`, adaptándose a la
// profundidad existente (Nacional → CCAA → Provincia → Local…).
const selecciones = ref([''])

watch(() => props.modelValue, (val) => {
  if (!val) { selecciones.value = ['']; return }
  const cadena = construirCadena(val)
  if (!cadena.length) { selecciones.value = ['']; return }
  // Solo se añade un desplegable más si la unidad seleccionada tiene hijos.
  const ultimoTieneHijos = props.agrupaciones.some(
    a => a.agrupacionPadreId === cadena[cadena.length - 1]
  )
  selecciones.value = ultimoTieneHijos ? [...cadena, ''] : [...cadena]
}, { immediate: true })

watch(() => props.agrupaciones, () => {
  if (!props.modelValue) selecciones.value = ['']
}, { immediate: true })

// Cadena de ids desde la raíz hasta `targetId`.
function construirCadena(targetId) {
  const map = Object.fromEntries(props.agrupaciones.map(a => [a.id, a]))
  const cadena = []
  let curr = map[targetId]
  while (curr) {
    cadena.unshift(curr.id)
    curr = curr.agrupacionPadreId ? map[curr.agrupacionPadreId] : null
  }
  return cadena
}

function opcionesParaNivel(idx) {
  if (idx === 0) {
    // Nivel superior: unidades raíz (sin padre).
    return props.agrupaciones.filter(a => !a.agrupacionPadreId)
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  }
  const padreId = selecciones.value[idx - 1]
  if (!padreId) return []
  return props.agrupaciones.filter(a => a.agrupacionPadreId === padreId)
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
}

function labelNivel(idx) {
  // Nombre del tipo de unidad de las opciones de ese nivel.
  return opcionesParaNivel(idx)[0]?.tipoUnidad?.nombre ?? ''
}

function cambiarNivel(idx, valor) {
  const nuevas = selecciones.value.slice(0, idx)
  nuevas.push(valor)
  if (valor) {
    const tieneHijos = props.agrupaciones.some(a => a.agrupacionPadreId === valor)
    if (tieneHijos) nuevas.push('')
  }
  selecciones.value = nuevas
  // Emitir la última selección no vacía (la más específica).
  const ultimo = [...nuevas].reverse().find(s => s !== '') || ''
  emit('update:modelValue', ultimo)
}

function limpiar() {
  selecciones.value = ['']
  emit('update:modelValue', '')
}

const haySeleccion = computed(() => selecciones.value.some(s => s !== ''))
</script>
