<template>
  <div class="flex flex-col items-center justify-center py-12 gap-3 text-slate-500">
    <div class="w-8 h-8 rounded-full border-4 border-purple-600 border-t-transparent animate-spin" />
    <p v-if="mensaje || message" class="text-sm">{{ mensaje || message }}</p>
  </div>
</template>

<script setup>
defineProps({
  mensaje: { type: String, default: '' },
  message: { type: String, default: '' }, // alias en inglés por compatibilidad
})
</script>
