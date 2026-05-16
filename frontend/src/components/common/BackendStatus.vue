<template>
  <div class="px-4 py-2 border-t border-purple-800 space-y-1.5">
    <div v-for="svc in services" :key="svc.key" class="flex items-center justify-between text-xs">
      <span class="text-purple-300">{{ svc.label }}</span>
      <span class="flex items-center gap-1.5">
        <span class="inline-flex h-2 w-2 rounded-full flex-shrink-0"
          :class="{
            'bg-green-400':               svc.estado === 'ok',
            'bg-red-500 animate-pulse':   svc.estado === 'error',
            'bg-yellow-400':              svc.estado === 'warn',
            'bg-slate-500 animate-pulse': svc.estado === 'checking',
          }"
        />
        <span :class="{
            'text-green-300':  svc.estado === 'ok',
            'text-red-300':    svc.estado === 'error',
            'text-yellow-300': svc.estado === 'warn',
            'text-slate-400':  svc.estado === 'checking',
          }">
          {{ svc.texto }}
        </span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const CHECKING = { estado: 'checking', texto: '…' }

const api  = ref({ ...CHECKING })
const db   = ref({ ...CHECKING })
const smtp = ref({ ...CHECKING })

const services = [
  { key: 'api',  label: 'Backend',     get estado() { return api.value.estado  }, get texto() { return api.value.texto  } },
  { key: 'bd',   label: 'Servidor BD', get estado() { return db.value.estado   }, get texto() { return db.value.texto   } },
  { key: 'smtp', label: 'SMTP', get estado() { return smtp.value.estado }, get texto() { return smtp.value.texto } },
]

let timer = null
let consecutiveFailures = 0

async function checkHealth() {
  try {
    const r = await fetch('/api/health', { signal: AbortSignal.timeout(8000) })
    if (r.ok) {
      consecutiveFailures = 0
      const data = await r.json()
      api.value  = { estado: 'ok',  texto: 'online' }
      db.value   = data.database === 'ok'
        ? { estado: 'ok',    texto: 'ok' }
        : { estado: 'error', texto: 'error' }
      smtp.value = data.smtp === 'ok'             ? { estado: 'ok',    texto: 'ok' }
               : data.smtp === 'not_configured'  ? { estado: 'warn',  texto: 'sin config' }
               : data.smtp === 'timeout'         ? { estado: 'error', texto: 'timeout' }
               :                                   { estado: 'error', texto: 'error' }
    } else if (++consecutiveFailures >= 2) {
      api.value  = { estado: 'error', texto: 'offline' }
      db.value   = { estado: 'error', texto: '?' }
      smtp.value = { estado: 'error', texto: '?' }
    }
  } catch {
    if (++consecutiveFailures >= 2) {
      api.value  = { estado: 'error', texto: 'offline' }
      db.value   = { estado: 'error', texto: '?' }
      smtp.value = { estado: 'error', texto: '?' }
    }
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
