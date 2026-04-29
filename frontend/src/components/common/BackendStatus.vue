<template>
  <div class="px-4 py-2 border-t border-purple-800">
    <div class="flex items-center justify-between text-xs">
      <span class="text-purple-300">Backend</span>
      <span class="flex items-center gap-1.5">
        <span
          class="inline-flex h-2 w-2 rounded-full"
          :class="{
            'bg-green-400': status === 'online',
            'bg-red-500 animate-pulse': status === 'offline',
            'bg-yellow-400 animate-pulse': status === 'checking',
          }"
        />
        <span
          :class="{
            'text-green-300': status === 'online',
            'text-red-300': status === 'offline',
            'text-yellow-300': status === 'checking',
          }"
        >
          {{ status }}
        </span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const status = ref('checking')
let timer = null
let consecutiveFailures = 0

async function checkHealth() {
  try {
    const r = await fetch('/api/health', { signal: AbortSignal.timeout(8000) })
    if (r.ok) {
      consecutiveFailures = 0
      status.value = 'online'
    } else if (++consecutiveFailures >= 2) {
      status.value = 'offline'
    }
  } catch {
    if (++consecutiveFailures >= 2) status.value = 'offline'
  }
}

onMounted(() => {
  checkHealth()
  timer = setInterval(checkHealth, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
