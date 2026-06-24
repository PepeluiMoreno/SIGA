<template>
  <input
    :type="type"
    :value="modelValue"
    @input="$emit('update:modelValue', coerce($event.target.value))"
    :placeholder="placeholder"
    :disabled="disabled"
    :readonly="readonly"
    class="control"
    :class="widthClass"
  />
</template>

<script setup>
/**
 * AppInput — input de texto enmarcado y estandarizado.
 * La anchura se declara por contenido esperado, no por defecto a todo el ancho:
 *   width="xs"  → CP, año, nº          width="md"  → nombre, email corto
 *   width="sm"  → fecha, DNI, teléfono width="lg"  → email largo, asunto
 *   width="full"→ ocupa la celda completa (por defecto)
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue:  { type: [String, Number], default: '' },
  type:        { type: String,  default: 'text' },
  placeholder: { type: String,  default: '' },
  disabled:    { type: Boolean, default: false },
  readonly:    { type: Boolean, default: false },
  /** 'xs' | 'sm' | 'md' | 'lg' | 'full' */
  width:       { type: String,  default: 'full' },
})

defineEmits(['update:modelValue'])

const WIDTHS = {
  xs: 'w-field-xs', sm: 'w-field-sm', md: 'w-field-md', lg: 'w-field-lg', full: 'w-full',
}
const widthClass = computed(() => WIDTHS[props.width] ?? 'w-full')

function coerce(v) {
  return props.type === 'number' && v !== '' ? Number(v) : v
}
</script>
