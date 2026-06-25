<template>
  <!-- Barra de acciones masivas: aparece al haber selección (estilo WordPress) -->
  <Transition name="bulk">
    <div v-if="count > 0"
      class="flex flex-wrap items-center gap-3 px-4 py-2.5 mb-3 bg-indigo-50 border border-indigo-200 rounded-lg text-sm">
      <span class="font-semibold text-indigo-800">
        {{ count }} seleccionado{{ count === 1 ? '' : 's' }}
      </span>

      <!-- Seleccionar todo el resultado del filtro, no solo lo visible -->
      <button v-if="!todoSeleccionado && total > count" type="button"
        @click="$emit('seleccionar-todos')"
        class="text-indigo-600 hover:underline text-xs">
        Seleccionar los {{ total }} del filtro
      </button>
      <button type="button" @click="$emit('limpiar')"
        class="text-slate-500 hover:text-slate-700 text-xs">
        Quitar selección
      </button>

      <span class="flex-1" />

      <select v-model="accionSel"
        class="h-8 px-2.5 text-sm border border-slate-300 rounded-lg bg-white">
        <option value="">Acciones…</option>
        <option v-for="a in accionesVisibles" :key="a.key" :value="a.key">{{ a.label }}</option>
      </select>
      <button type="button" :disabled="!accionSel" @click="aplicar"
        class="h-8 px-3 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        Aplicar
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
const emit = defineEmits(['seleccionar-todos', 'limpiar', 'ejecutar'])

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
