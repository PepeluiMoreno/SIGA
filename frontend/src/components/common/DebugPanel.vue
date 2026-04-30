<template>
  <div
    v-if="debug.enabled"
    class="fixed inset-x-0 top-0 z-[1000] border-b border-amber-300 bg-amber-100/95 text-amber-950 shadow-lg backdrop-blur"
  >
    <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p class="text-sm font-semibold uppercase tracking-wide">Debug Mode</p>
          <p class="text-xs">
            Ruta: <span class="font-mono">{{ debug.sessionSnapshot.route }}</span>
          </p>
          <p class="text-xs">
            GraphQL: <span class="font-mono break-all">{{ debug.sessionSnapshot.graphqlEndpoint }}</span>
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <span class="rounded-full bg-amber-200 px-2 py-1 text-xs font-medium">
            Token: {{ debug.sessionSnapshot.hasToken ? 'yes' : 'no' }}
          </span>
          <button
            class="rounded border border-amber-400 px-3 py-1 text-xs font-medium hover:bg-amber-200"
            @click="copySummary"
          >
            Copiar diagnóstico
          </button>
          <button
            class="rounded border border-amber-400 px-3 py-1 text-xs font-medium hover:bg-amber-200"
            @click="debug.clearEvents"
          >
            Limpiar
          </button>
          <button
            class="rounded border border-amber-400 px-3 py-1 text-xs font-medium hover:bg-amber-200"
            @click="debug.toggleExpanded"
          >
            {{ debug.expanded ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>

      <div v-if="debug.expanded" class="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <section class="rounded border border-amber-300 bg-amber-50 p-3">
          <h2 class="text-xs font-semibold uppercase tracking-wide">Estado</h2>
          <pre class="mt-2 overflow-auto text-xs">{{ prettyState }}</pre>
        </section>

        <section class="rounded border border-amber-300 bg-amber-50 p-3">
          <h2 class="text-xs font-semibold uppercase tracking-wide">Eventos recientes</h2>
          <div v-if="debug.events.length" class="mt-2 max-h-72 space-y-2 overflow-auto">
            <article
              v-for="event in debug.events"
              :key="event.id"
              class="rounded border border-amber-200 bg-white p-2 text-xs"
            >
              <p class="font-semibold">{{ event.type }} · {{ event.timestamp }}</p>
              <p class="mt-1 break-words">{{ event.message }}</p>
              <pre v-if="event.meta" class="mt-2 overflow-auto">{{ formatJson(event.meta) }}</pre>
              <pre v-if="event.error" class="mt-2 overflow-auto">{{ formatJson(event.error) }}</pre>
            </article>
          </div>
          <p v-else class="mt-2 text-xs text-amber-800">Sin eventos capturados todavía.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDebugStore } from '@/stores/debug.js'

const debug = useDebugStore()

const prettyState = computed(() => formatJson(debug.sessionSnapshot))

function formatJson(value) {
  return JSON.stringify(value, null, 2)
}

async function copySummary() {
  try {
    await debug.copySummary()
    debug.addEvent('debug', 'Diagnóstico copiado al portapapeles')
  } catch (error) {
    debug.captureError('debug', error, { action: 'copySummary' })
  }
}
</script>
