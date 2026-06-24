<template>
  <select
    :value="modelValue"
    @change="$emit('update:modelValue', $event.target.value)"
    :disabled="disabled"
    class="control"
    :class="widthClass"
  >
    <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
    <option
      v-for="opt in normalizadas"
      :key="opt.value"
      :value="opt.value"
    >{{ opt.label }}</option>
    <slot />
  </select>
</template>

<script setup>
/**
 * AppSelect — desplegable enmarcado y estandarizado.
 * Acepta opciones por prop (array de {value,label} o strings) o vía <slot>.
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue:  { type: [String, Number, null], default: '' },
  options:     { type: Array,   default: () => [] },
  placeholder: { type: String,  default: '' },
  disabled:    { type: Boolean, default: false },
  /** 'xs' | 'sm' | 'md' | 'lg' | 'full' */
  width:       { type: String,  default: 'full' },
})

defineEmits(['update:modelValue'])

const WIDTHS = {
  xs: 'w-field-xs', sm: 'w-field-sm', md: 'w-field-md', lg: 'w-field-lg', full: 'w-full',
}
const widthClass = computed(() => WIDTHS[props.width] ?? 'w-full')

const normalizadas = computed(() =>
  props.options.map((o) =>
    typeof o === 'object' ? { value: o.value ?? o.id, label: o.label ?? o.nombre } : { value: o, label: o },
  ),
)
</script>
