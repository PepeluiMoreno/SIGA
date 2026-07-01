<template>
  <div :class="widthClass">
    <label v-if="label" class="block text-xs font-medium text-slate-600 mb-1">{{ label }}</label>
    <input v-if="editando" :type="type" :value="modelValue ?? ''" :placeholder="placeholder"
      class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
      @input="$emit('update:modelValue', $event.target.value)" />
    <div v-else class="py-1.5 text-sm text-slate-900 min-h-[34px]">{{ display }}</div>
  </div>
</template>

<script setup>
/**
 * FieldText — campo de texto estándar (ver/editar) con ancho dimensionable.
 *
 * `width` dimensiona el campo según su contenido (no todo a w-full): un CP o un
 * año no ocupan lo mismo que una dirección. Ver feedback_campos_dimensionados.
 *   xs  ~ 6rem  (código, %, orden)
 *   sm  ~ 10rem (CP, fecha corta, teléfono)
 *   md  ~ 16rem (nombre, email)
 *   lg  ~ 24rem
 *   full = 100% (dirección, descripciones)
 * En un AppFormGrid, usar `width="full"` y dejar que el grid reparta, o un ancho
 * fijo para acotar campos pequeños dentro de una fila flexible.
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label:      { type: String, default: '' },
  type:       { type: String, default: 'text' },
  placeholder:{ type: String, default: '' },
  editMode:   { type: Boolean, default: false },
  editing:    { type: Boolean, default: false },  // alias de editMode
  width:      { type: String, default: 'full' },
})
defineEmits(['update:modelValue'])

const editando = computed(() => props.editMode || props.editing)
const WIDTHS = {
  xs: 'w-24', sm: 'w-40', md: 'w-64', lg: 'w-96', full: 'w-full',
}
const widthClass = computed(() => WIDTHS[props.width] ?? 'w-full')
const display = computed(() => {
  const v = props.modelValue
  return v === null || v === undefined || v === '' ? '—' : String(v)
})
</script>
