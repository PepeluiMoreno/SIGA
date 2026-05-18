<template>
  <div class="flex items-center gap-1.5 flex-wrap">
    <span class="text-xs font-medium text-slate-500 shrink-0 mr-1">Ámbito:</span>
    <template v-for="(sel, idx) in selecciones" :key="idx">
      <span v-if="idx > 0" class="text-slate-300 text-sm shrink-0">›</span>
      <!-- Etiqueta del nivel (nombre del tipo) -->
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
const selecciones = ref([''])

watch(() => props.modelValue, (val) => {
  if (!val) { resetToRoot(); return }
  const cadena = construirCadena(val)
  selecciones.value = cadena.length ? [...cadena, ''] : ['']
}, { immediate: true })

watch(() => props.agrupaciones, () => {
  if (!props.modelValue) resetToRoot()
}, { immediate: true })

function resetToRoot() {
  const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
  if (roots.length === 1) {
    selecciones.value = [roots[0].id, '']
  } else {
    selecciones.value = ['']
  }
}

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
    return props.agrupaciones.filter(a => !a.agrupacionPadreId)
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  }
  const padreId = selecciones.value[idx - 1]
  if (!padreId) return []
  return props.agrupaciones.filter(a => a.agrupacionPadreId === padreId)
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
}

function labelNivel(idx) {
  if (idx === 0) {
    const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
    return roots[0]?.tipoUnidad?.nombre ?? ''
  }
  const padreId = selecciones.value[idx - 1]
  if (!padreId) return ''
  const hijos = props.agrupaciones.filter(a => a.agrupacionPadreId === padreId)
  return hijos[0]?.tipoUnidad?.nombre ?? ''
}

function cambiarNivel(idx, valor) {
  const nuevas = selecciones.value.slice(0, idx)
  nuevas.push(valor)
  if (valor) {
    const tieneHijos = props.agrupaciones.some(a => a.agrupacionPadreId === valor)
    if (tieneHijos) nuevas.push('')
  } else if (idx === 0) {
    const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
    if (roots.length === 1) nuevas[0] = roots[0].id
  }
  selecciones.value = nuevas
  // Emitir el último valor no vacío, excluyendo la raíz auto-seleccionada si es única
  const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
  const selSignificativas = roots.length === 1 ? nuevas.slice(1) : nuevas
  const ultimo = [...selSignificativas].reverse().find(s => s !== '') || ''
  emit('update:modelValue', ultimo)
}

function limpiar() {
  resetToRoot()
  emit('update:modelValue', '')
}

const haySeleccion = computed(() => {
  const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
  const base = roots.length === 1 ? selecciones.value.slice(1) : selecciones.value
  return base.some(s => s !== '')
})
</script>
