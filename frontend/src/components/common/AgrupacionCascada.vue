<template>
  <div class="flex items-center gap-1.5 flex-wrap">
    <span class="text-xs font-medium text-slate-500 shrink-0 mr-1">Ámbito:</span>
    <template v-for="(sel, idx) in selecciones" :key="idx">
      <span v-if="idx > 0" class="text-slate-300 text-sm shrink-0">›</span>
      <select
        :value="sel"
        @change="cambiarNivel(idx, $event.target.value)"
        class="h-8 text-sm border border-slate-200 rounded-md px-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent">
        <option value="">{{ placeholderNivel(idx) }}</option>
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

// Selecciones por profundidad: selecciones[0]=raíz, selecciones[1]=hijo, etc.
const selecciones = ref([''])

// Inicializar selecciones cuando cambia modelValue externamente (p.ej. limpiarFiltros)
watch(() => props.modelValue, (val) => {
  if (!val) {
    selecciones.value = ['']
    return
  }
  // Reconstruir cadena de ancestros
  const cadena = construirCadena(val)
  selecciones.value = cadena.length ? [...cadena, ''] : ['']
}, { immediate: true })

// Reconstruye la cadena de IDs desde raíz hasta targetId
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
    return props.agrupaciones
      .filter(a => !a.agrupacionPadreId)
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  }
  const padreId = selecciones.value[idx - 1]
  if (!padreId) return []
  return props.agrupaciones
    .filter(a => a.agrupacionPadreId === padreId)
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
}

function placeholderNivel(idx) {
  if (idx === 0) {
    const roots = props.agrupaciones.filter(a => !a.agrupacionPadreId)
    return roots[0]?.tipoUnidad?.nombre || 'Todas'
  }
  const padreId = selecciones.value[idx - 1]
  if (!padreId) return '—'
  const hijos = props.agrupaciones.filter(a => a.agrupacionPadreId === padreId)
  const tipo = hijos[0]?.tipoUnidad?.nombre
  return tipo ? `Todas (${tipo})` : 'Todos'
}

function cambiarNivel(idx, valor) {
  // Actualizar nivel idx y eliminar todos los más profundos
  const nuevas = selecciones.value.slice(0, idx)
  nuevas.push(valor)

  if (valor) {
    const tieneHijos = props.agrupaciones.some(a => a.agrupacionPadreId === valor)
    if (tieneHijos) nuevas.push('')
  }

  selecciones.value = nuevas

  // Emitir el último valor no vacío
  const ultimo = [...nuevas].reverse().find(s => s !== '') || ''
  emit('update:modelValue', ultimo)
}

function limpiar() {
  selecciones.value = ['']
  emit('update:modelValue', '')
}

const haySeleccion = computed(() => selecciones.value.some(s => s !== ''))
</script>
