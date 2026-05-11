<template>
  <div class="flex items-center justify-between mb-5">
    <button @click="goBack"
      class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
      </svg>
      Volver
    </button>
    <slot />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  fallback: { type: String, default: '/' },
})

const router = useRouter()

function goBack() {
  if (window.history.state?.back) router.back()
  else router.push(props.fallback)
}
</script>
