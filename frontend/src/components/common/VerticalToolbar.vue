<template>
  <div class="space-y-1.5">
    <p v-if="title" class="text-[11px] font-semibold uppercase tracking-wide text-slate-400">{{ title }}</p>
    <button
      v-for="a in visibleActions"
      :key="a.key"
      type="button"
      :disabled="a.disabled || disabled"
      :title="a.title || ''"
      @click="$emit('select', a.key)"
      :class="['w-full text-center text-sm leading-tight px-2 py-2 rounded-md font-medium border transition-colors disabled:opacity-40 disabled:cursor-not-allowed', variantClass(a.variant)]"
    >{{ a.label }}</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Lista vertical de botones de acción reutilizable. Cada acción:
//   { key, label, variant?: 'default'|'primary'|'danger', disabled?, hidden?, title? }
// Emite 'select' con la key de la acción pulsada.
const props = defineProps({
  title:    { type: String,  default: '' },
  actions:  { type: Array,   default: () => [] },
  disabled: { type: Boolean, default: false },
})
defineEmits(['select'])

const visibleActions = computed(() => props.actions.filter(a => !a.hidden))

const variantClass = (v) => {
  if (v === 'primary') return 'border-purple-600 bg-purple-600 text-white hover:bg-purple-700'
  if (v === 'danger')  return 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100'
  return 'border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200'
}
</script>
