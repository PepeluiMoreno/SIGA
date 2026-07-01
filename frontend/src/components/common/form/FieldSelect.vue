<template>
  <div :class="widthClass">
    <label v-if="label" class="block text-xs font-medium text-slate-600 mb-1">{{ label }}</label>
    <select v-if="editando" :value="modelValue ?? ''"
      class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 bg-white focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
      @change="$emit('update:modelValue', $event.target.value || null)">
      <option value="">{{ emptyLabel }}</option>
      <option v-for="opt in options" :key="opt[optionValue]" :value="opt[optionValue]">
        {{ opt[optionLabel] }}
      </option>
    </select>
    <div v-else class="py-1.5 text-sm text-slate-900 min-h-[34px]">{{ display }}</div>
  </div>
</template>

<script setup>
/** FieldSelect — select estándar (ver/editar). Ver feedback_campos_dimensionados. */
import { computed } from 'vue'

const props = defineProps({
  modelValue:  { default: null },
  label:       { type: String, default: '' },
  options:     { type: Array, default: () => [] },
  optionLabel: { type: String, default: 'label' },
  optionValue: { type: String, default: 'value' },
  emptyLabel:  { type: String, default: 'Sin especificar' },
  editMode:    { type: Boolean, default: false },
  editing:     { type: Boolean, default: false },  // alias de editMode
  width:       { type: String, default: 'full' },
})
defineEmits(['update:modelValue'])

const editando = computed(() => props.editMode || props.editing)

const WIDTHS = { xs: 'w-24', sm: 'w-40', md: 'w-64', lg: 'w-96', full: 'w-full' }
const widthClass = computed(() => WIDTHS[props.width] ?? 'w-full')
const display = computed(() => {
  const cur = props.options.find((o) => o?.[props.optionValue] === props.modelValue)
  return cur?.[props.optionLabel] || props.emptyLabel
})
</script>
