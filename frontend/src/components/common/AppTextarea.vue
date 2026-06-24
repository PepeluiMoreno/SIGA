<template>
  <textarea
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
    :placeholder="placeholder"
    :disabled="disabled"
    :rows="rows"
    class="control"
  />
</template>

<script setup>
/**
 * AppTextarea — área de texto enmarcada y estandarizada.
 */
defineProps({
  modelValue:  { type: String,  default: '' },
  placeholder: { type: String,  default: '' },
  disabled:    { type: Boolean, default: false },
  rows:        { type: [Number, String], default: 3 },
})

defineEmits(['update:modelValue'])
</script>
