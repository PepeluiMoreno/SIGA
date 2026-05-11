<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
    :style="estilobadge"
  >
    {{ texto }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { badgeStyle } from '@/utils/badge'

const props = defineProps({
  // Objeto del catálogo con { id, nombre, color } — uso preferente
  estadoObj: {
    type: Object,
    default: null,
  },
  // Texto a mostrar (si no se pasa estadoObj)
  texto: {
    type: String,
    default: '',
  },
  // Color hex directo (si no se pasa estadoObj)
  color: {
    type: String,
    default: null,
  },
})

const texto  = computed(() => props.estadoObj?.nombre ?? props.texto)
const estilobadge = computed(() => badgeStyle(props.estadoObj?.color ?? props.color))
</script>
