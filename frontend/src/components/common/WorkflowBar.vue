<template>
  <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
    <!-- Estado actual + acciones de transición -->
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-xs text-slate-500 mr-1">Estado actual:</span>
      <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
        :class="estadoBadgeClass">
        {{ estadoNombre }}
      </span>

      <div class="flex-1"/>

      <template v-if="transicionesDisponibles.length">
        <button v-for="t in transicionesDisponibles" :key="t.label"
          @click="$emit('transicion', t)"
          :disabled="cargando"
          class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium rounded-lg transition-colors disabled:opacity-50"
          :class="t.estilo || 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100'">
          <svg v-if="t.icono === 'send'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          <svg v-else-if="t.icono === 'check'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else-if="t.icono === 'reject'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else-if="t.icono === 'play'" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else-if="t.icono === 'close'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          {{ t.label }}
        </button>
      </template>

      <span v-else-if="esFinal" class="text-xs text-slate-400 italic">Estado final</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  estadoNombre: { type: String, default: '' },
  transicionesDisponibles: { type: Array, default: () => [] },
  cargando: { type: Boolean, default: false },
  esFinal: { type: Boolean, default: false },
})

defineEmits(['transicion'])

const estadoBadgeClass = computed(() => {
  const n = (props.estadoNombre || '').toLowerCase()
  if (n.includes('finaliz') || n.includes('cerrad')) return 'bg-emerald-100 text-emerald-700'
  if (n.includes('cancelad') || n.includes('rechazad')) return 'bg-red-100 text-red-700'
  if (n.includes('aprobad')) return 'bg-green-100 text-green-700'
  if (n.includes('pendiente') || n.includes('revisión')) return 'bg-amber-100 text-amber-700'
  if (n.includes('curso')) return 'bg-blue-100 text-blue-700'
  if (n.includes('preparac')) return 'bg-sky-100 text-sky-700'
  return 'bg-slate-100 text-slate-600'
})
</script>
