<template>
  <label class="flex items-center gap-2 rounded-lg px-3 py-2.5 min-h-[42px] text-sm cursor-pointer select-none"
    :class="modelValue ? 'bg-indigo-50 border border-indigo-200 text-indigo-800' : 'bg-slate-50 border border-slate-200 text-slate-700'">
    <input type="checkbox" :checked="modelValue" :disabled="!editando"
      class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
      @change="$emit('update:modelValue', $event.target.checked)" />
    <span>{{ label }}</span>
  </label>
</template>

<script setup>
/** FieldCheckbox — casilla estándar en caja (ver/editar). Ver feedback_campos_dimensionados. */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  label:      { type: String, required: true },
  editMode:   { type: Boolean, default: false },
  editing:    { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const editando = computed(() => props.editMode || props.editing)
</script>
