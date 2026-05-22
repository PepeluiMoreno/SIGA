<template>
  <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-xs text-slate-500 mr-1">Estado actual:</span>
      <EstadoBadge :texto="estadoNombre" :color="estadoColor" />

      <div class="flex-1" />

      <template v-if="transicionesDisponibles.length">
        <button
          v-for="t in transicionesDisponibles"
          :key="t.label"
          @click="$emit('transicion', t)"
          :disabled="cargando"
          class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium rounded-lg transition-colors disabled:opacity-50"
          :class="t.estilo || 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100'"
        >
          <component :is="ICONOS[t.icono]" v-if="t.icono && ICONOS[t.icono]" class="w-3.5 h-3.5" />
          {{ t.label }}
        </button>
      </template>

      <span v-else-if="esFinal" class="text-xs text-slate-400 italic">Estado final</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  PaperAirplaneIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/vue/24/outline'
import EstadoBadge from './EstadoBadge.vue'

const ICONOS = {
  send:   PaperAirplaneIcon,
  check:  CheckCircleIcon,
  reject: XCircleIcon,
  play:   PlayIcon,
  close:  ClipboardDocumentCheckIcon,
}

const props = defineProps({
  estadoNombre: { type: String, default: '' },
  estadoColor:  { type: String, default: null },
  transicionesDisponibles: { type: Array, default: () => [] },
  cargando:  { type: Boolean, default: false },
  esFinal:   { type: Boolean, default: false },
})

defineEmits(['transicion'])
</script>
