<template>
  <div class="flex items-center justify-between mb-5">
    <button
      @click="goBack"
      class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
    >
      <ArrowLeftIcon class="w-4 h-4" />
      {{ backText }}
    </button>
    <slot />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  fallback: { type: String, default: '/' },
  backText: { type: String, default: 'Volver' },
})

const router = useRouter()

function goBack() {
  if (window.history.state?.back) router.back()
  else router.push(props.fallback)
}
</script>
