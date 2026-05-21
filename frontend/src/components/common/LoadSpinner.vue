<!-- Alias de EstadoCarga — usar EstadoCarga directamente -->
<template>
  <EstadoCarga :mensaje="message" />
</template>

<script setup>
import EstadoCarga from './EstadoCarga.vue'
defineProps({ message: { type: String, default: 'Cargando...' } })
</script>
