<template>
  <div :class="widthClass">
    <label v-if="label" class="block text-xs font-medium text-slate-600 mb-1">{{ label }}</label>
    <textarea v-if="editMode" :rows="rows" :value="modelValue ?? ''" :placeholder="placeholder"
      class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 resize-none focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
      @input="$emit('update:modelValue', $event.target.value)"></textarea>
    <div v-else class="py-1.5 text-sm text-slate-900 min-h-[60px] whitespace-pre-wrap">{{ display }}</div>
  </div>
</template>

<script setup>
/** FieldTextarea — textarea estándar (ver/editar). Ver feedback_campos_dimensionados. */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label:      { type: String, default: '' },
  rows:       { type: [Number, String], default: 3 },
  placeholder:{ type: String, default: '' },
  editMode:   { type: Boolean, default: false },
  width:      { type: String, default: 'full' },
})
defineEmits(['update:modelValue'])

const WIDTHS = { xs: 'w-24', sm: 'w-40', md: 'w-64', lg: 'w-96', full: 'w-full' }
const widthClass = computed(() => WIDTHS[props.width] ?? 'w-full')
const display = computed(() => {
  const v = props.modelValue
  return v === null || v === undefined || v === '' ? '—' : String(v)
})
</script>
