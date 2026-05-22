<template>
  <div :class="['flex flex-col gap-1', spanClass]">
    <!-- Label -->
    <label v-if="label" :for="fieldId" class="text-sm font-medium text-slate-700 leading-tight">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-0.5">*</span>
      <span v-if="optional" class="text-slate-400 font-normal text-xs ml-1">(opcional)</span>
    </label>

    <!-- Slot del input/select/textarea -->
    <slot :id="fieldId" :aria-describedby="helpId || errorId" :aria-invalid="!!error" />

    <!-- Texto de ayuda -->
    <p v-if="help && !error" :id="helpId" class="text-xs text-slate-500 leading-snug">
      {{ help }}
    </p>

    <!-- Error -->
    <p v-if="error" :id="errorId" class="text-xs text-red-600 leading-snug flex items-center gap-1">
      <ExclamationCircleIcon class="w-3.5 h-3.5 shrink-0" />
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ExclamationCircleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  label:    { type: String,  default: '' },
  help:     { type: String,  default: '' },
  error:    { type: String,  default: '' },
  required: { type: Boolean, default: false },
  optional: { type: Boolean, default: false },
  /** Cuántas columnas ocupa en el AppFormGrid (col-span-N) */
  span:     { type: [Number, String], default: 1 },
})

const uid = Math.random().toString(36).slice(2, 7)
const fieldId = `field-${uid}`
const helpId  = `help-${uid}`
const errorId = `error-${uid}`

const SPANS = { 1: '', 2: 'sm:col-span-2', 3: 'sm:col-span-3', full: 'col-span-full' }
const spanClass = computed(() => SPANS[props.span] ?? '')
</script>
