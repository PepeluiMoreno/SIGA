<template>
  <div class="grid gap-4" :class="gridClass">
    <slot />
  </div>
</template>

<script setup>
/**
 * AppFormGrid — grid de formulario con columnas proporcionales.
 *
 * Uso:
 *   <AppFormGrid cols="2">          → 1 col móvil, 2 col sm+
 *   <AppFormGrid cols="3">          → 1 col móvil, 2 col sm, 3 col lg+
 *   <AppFormGrid cols="1-2">        → campo estrecho + campo ancho (golden ratio)
 *   <AppFormGrid cols="narrow">     → max-w-sm centrado — para formularios cortos
 *   <AppFormGrid cols="compact">    → max-w-md — para formularios medianos
 */
import { computed } from 'vue'

const props = defineProps({
  /**
   * '1' | '2' | '3' | '4' | '1-2' | '2-1' | 'narrow' | 'compact' | 'full'
   */
  cols: { type: String, default: '2' },
  gap:  { type: String, default: '4' },
})

const GRIDS = {
  '1':       'grid-cols-1',
  '2':       'grid-cols-1 sm:grid-cols-2',
  '3':       'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  '4':       'grid-cols-2 lg:grid-cols-4',
  '1-2':     'grid-cols-1 sm:grid-cols-[1fr_2fr]',
  '2-1':     'grid-cols-1 sm:grid-cols-[2fr_1fr]',
  'narrow':  'grid-cols-1 max-w-sm',
  'compact': 'grid-cols-1 max-w-md',
  'full':    'grid-cols-1',
}

const gridClass = computed(() => GRIDS[props.cols] ?? GRIDS['2'])
</script>
