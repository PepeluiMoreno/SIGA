<template>
  <div
    v-if="visible"
    class="flex items-start gap-3 rounded-lg border px-4 py-3 text-sm"
    :class="VARIANTS[variant].container"
    role="alert"
  >
    <component :is="VARIANTS[variant].icon" class="w-5 h-5 shrink-0 mt-0.5" :class="VARIANTS[variant].iconColor" />
    <div class="flex-1 min-w-0">
      <p v-if="title" class="font-medium" :class="VARIANTS[variant].title">{{ title }}</p>
      <p :class="VARIANTS[variant].text">
        <slot>{{ message }}</slot>
      </p>
      <button
        v-if="retryAction"
        @click="$emit('retry')"
        class="mt-1.5 text-xs font-medium underline underline-offset-2 hover:no-underline"
        :class="VARIANTS[variant].title"
      >
        Reintentar
      </button>
    </div>
    <button
      v-if="dismissible"
      @click="visible = false"
      class="shrink-0 opacity-60 hover:opacity-100 transition-opacity"
      :class="VARIANTS[variant].iconColor"
      aria-label="Cerrar"
    >
      <XMarkIcon class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  /** 'error' | 'warning' | 'info' */
  variant:     { type: String,  default: 'error' },
  title:       { type: String,  default: '' },
  message:     { type: String,  default: '' },
  retryAction: { type: Boolean, default: false },
  dismissible: { type: Boolean, default: false },
})

defineEmits(['retry'])

const visible = ref(true)
watch(() => props.message, () => { visible.value = true })

const VARIANTS = {
  error: {
    container: 'bg-red-50 border-red-200',
    icon:      ExclamationCircleIcon,
    iconColor: 'text-red-400',
    title:     'text-red-800',
    text:      'text-red-700',
  },
  warning: {
    container: 'bg-amber-50 border-amber-200',
    icon:      ExclamationTriangleIcon,
    iconColor: 'text-amber-400',
    title:     'text-amber-800',
    text:      'text-amber-700',
  },
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon:      InformationCircleIcon,
    iconColor: 'text-blue-400',
    title:     'text-blue-800',
    text:      'text-blue-700',
  },
}
</script>
