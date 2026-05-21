<template>
  <component
    :is="tag"
    v-bind="linkProps"
    class="inline-flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-1 disabled:opacity-50 disabled:pointer-events-none"
    :class="[sizeClass, variantClass, { 'w-full': block }]"
    :disabled="disabled || loading"
    @click="!tag || tag === 'button' ? $emit('click', $event) : undefined"
  >
    <!-- Spinner de carga -->
    <span v-if="loading" class="animate-spin rounded-full border-2 border-current border-t-transparent w-4 h-4 shrink-0" />
    <!-- Icono izquierda -->
    <component v-else-if="icon" :is="icon" class="shrink-0" :class="iconSizeClass" />
    <slot />
    <!-- Icono derecha -->
    <component v-if="iconRight && !loading" :is="iconRight" class="shrink-0" :class="iconSizeClass" />
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** 'primary' | 'secondary' | 'danger' | 'ghost' | 'link' */
  variant:   { type: String, default: 'primary' },
  /** 'xs' | 'sm' | 'md' | 'lg' */
  size:      { type: String, default: 'md' },
  icon:      { type: [Object, Function], default: null },
  iconRight: { type: [Object, Function], default: null },
  loading:   { type: Boolean, default: false },
  disabled:  { type: Boolean, default: false },
  block:     { type: Boolean, default: false },
  /** Si se pasa 'to', el botón se convierte en router-link */
  to:        { type: [String, Object], default: null },
  /** Si se pasa 'href', el botón se convierte en <a> */
  href:      { type: String, default: null },
})

defineEmits(['click'])

const tag = computed(() => {
  if (props.to)   return 'router-link'
  if (props.href) return 'a'
  return 'button'
})

const linkProps = computed(() => {
  if (props.to)   return { to: props.to }
  if (props.href) return { href: props.href, target: '_blank', rel: 'noopener' }
  return {}
})

const VARIANTS = {
  primary:   'bg-purple-600 text-white hover:bg-purple-700 rounded-lg shadow-sm',
  secondary: 'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 rounded-lg shadow-sm',
  danger:    'bg-red-600 text-white hover:bg-red-700 rounded-lg shadow-sm',
  ghost:     'text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg',
  link:      'text-purple-600 hover:text-purple-800 underline-offset-2 hover:underline',
}

const SIZES = {
  xs: 'h-7  px-2.5 text-xs',
  sm: 'h-8  px-3   text-sm',
  md: 'h-10 px-4   text-sm',
  lg: 'h-11 px-5   text-base',
}

const ICON_SIZES = {
  xs: 'w-3 h-3',
  sm: 'w-3.5 h-3.5',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
}

const variantClass  = computed(() => VARIANTS[props.variant]  ?? VARIANTS.primary)
const sizeClass     = computed(() => SIZES[props.size]        ?? SIZES.md)
const iconSizeClass = computed(() => ICON_SIZES[props.size]   ?? ICON_SIZES.md)
</script>
