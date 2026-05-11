<template>
  <div class="text-center py-12">
    <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent"></div>
    <p v-if="mensaje" class="mt-2 text-sm text-gray-600">{{ mensaje }}</p>
  </div>
</template>

<script setup>
defineProps({ mensaje: { type: String, default: '' } })
</script>
