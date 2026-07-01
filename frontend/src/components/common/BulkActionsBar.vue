<template>
  <!-- Barra de acciones masivas: aparece al haber selección (estilo WordPress) -->
  <Transition name="bulk">
    <!-- Barra de acciones en lote, estética sobria estilo WordPress. -->
    <div v-if="count > 0"
      class="flex flex-wrap items-center gap-2 px-3 py-2 mb-3 bg-slate-50 border border-slate-200 rounded text-sm text-slate-600">
      <!-- Desplegable de acción conjunta + Aplicar, junto a la cuenta.
           La selección se quita con el toggle del checkbox general de la tabla. -->
      <select v-model="accionSel"
        class="h-8 px-2.5 text-sm border border-slate-300 rounded bg-white text-slate-700">
        <option value="">Acciones en lote…</option>
        <option v-for="a in accionesVisibles" :key="a.key" :value="a.key">{{ a.label }}</option>
      </select>
      <button type="button" :disabled="!accionSel" @click="aplicar"
        class="h-8 px-3 text-sm text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-100 disabled:opacity-50">
        Aplicar
      </button>

      <span class="text-slate-500">{{ count }} seleccionado{{ count === 1 ? '' : 's' }}</span>

      <!-- Seleccionar todo el resultado del filtro, no solo lo visible -->
      <button v-if="!todoSeleccionado && total > count" type="button"
        @click="$emit('seleccionar-todos')"
        class="text-slate-500 hover:text-slate-700 hover:underline text-xs">
        Seleccionar los {{ total }} del filtro
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePermisos } from '@/composables/usePermisos.js'

const props = defineProps({
  count: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  todoSeleccionado: { type: Boolean, default: false },
  /** [{ key, label, permiso? }] — permiso opcional gatea la acción por RBAC. */
  acciones: { type: Array, default: () => [] },
})
const emit = defineEmits(['seleccionar-todos', 'ejecutar'])

const { tienePermiso } = usePermisos()
const accionSel = ref('')

const accionesVisibles = computed(() =>
  props.acciones.filter((a) => !a.permiso || tienePermiso(a.permiso))
)

function aplicar() {
  if (!accionSel.value) return
  emit('ejecutar', accionSel.value)
  accionSel.value = ''
}
</script>

<style scoped>
.bulk-enter-active, .bulk-leave-active { transition: opacity .15s ease, transform .15s ease; }
.bulk-enter-from, .bulk-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
