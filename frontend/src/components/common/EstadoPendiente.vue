<template>
  <div class="p-12 text-center text-gray-500" role="status">
    <slot name="icono">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor"
        viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
    </slot>
    <p class="text-lg">{{ mensaje }}</p>
    <p v-if="detalle" class="text-sm text-gray-400 mt-1">{{ detalle }}</p>
  </div>
</template>

<script setup>
defineProps({
  // Mensaje principal; por defecto, la guía de filtros original.
  mensaje: { type: String, default: 'Configura los filtros y pulsa "Buscar"' },
  // Línea secundaria opcional.
  detalle: { type: String, default: '' },
})
</script>
