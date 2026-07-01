<template>
  <div class="relative py-2 select-none">
    <!-- Línea base que conecta los nodos -->
    <div class="absolute top-7 left-8 right-8 h-px bg-slate-200 z-0" />

    <div class="relative z-10 flex items-start justify-between">
      <button
        v-for="ej in ejercicios"
        :key="ej.anio"
        @click="$emit('select', ej.anio)"
        class="flex flex-col items-center gap-1.5 flex-1 group focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 rounded"
      >
        <!-- Nodo circular -->
        <div
          class="w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-200 shadow-sm"
          :class="[nodeClass(ej), ej.anio === seleccionado && 'scale-110 ring-2 ring-indigo-500 ring-offset-2']"
        >
          <component :is="cfg(ej).icon" class="w-4 h-4" v-if="ej.anio !== seleccionado" />
          <span v-else class="text-xs font-bold leading-none">{{ String(ej.anio).slice(2) }}</span>
        </div>

        <!-- Año -->
        <span
          class="text-xs font-semibold transition-colors leading-tight"
          :class="ej.anio === seleccionado ? 'text-indigo-700' : 'text-slate-500 group-hover:text-slate-800'"
        >{{ ej.anio }}</span>

        <!-- Badge de estado -->
        <span
          v-if="ej.estado"
          class="text-[10px] px-1.5 py-0.5 rounded-full font-medium whitespace-nowrap leading-tight"
          :class="cfg(ej).badge"
        >{{ cfg(ej).label }}</span>
        <span v-else class="text-[10px] text-slate-400 italic leading-tight">Sin datos</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import {
  CheckCircleIcon, ClockIcon, PencilSquareIcon,
  LockClosedIcon, PlusCircleIcon, PlayIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  /** Array de { anio: number, estado: string|null } — ordenado cronológicamente */
  ejercicios:   { type: Array,  default: () => [] },
  /** Año actualmente seleccionado */
  seleccionado: { type: Number, default: null },
})
defineEmits(['select'])

const ESTADOS = {
  BORRADOR:     { label: 'Borrador', badge: 'bg-slate-100 text-slate-600',   icon: PencilSquareIcon, node: 'bg-white border-slate-300 text-slate-500 group-hover:border-indigo-400 group-hover:text-indigo-500' },
  PROPUESTO:    { label: 'Propuesto', badge: 'bg-blue-100 text-blue-700',    icon: ClockIcon,        node: 'bg-blue-50 border-blue-400 text-blue-600' },
  APROBADO:     { label: 'Aprobado', badge: 'bg-green-100 text-green-700',   icon: CheckCircleIcon,  node: 'bg-green-50 border-green-500 text-green-600' },
  EN_EJECUCION: { label: 'En curso', badge: 'bg-purple-100 text-purple-700', icon: PlayIcon,         node: 'bg-purple-50 border-purple-500 text-purple-700 ring-2 ring-purple-200 ring-offset-1' },
  CERRADO:      { label: 'Cerrado',  badge: 'bg-gray-100 text-gray-500',     icon: LockClosedIcon,   node: 'bg-gray-100 border-gray-400 text-gray-500' },
}
const VACIO = {
  label: null, badge: '', icon: PlusCircleIcon,
  node: 'bg-white border-dashed border-slate-300 text-slate-400 group-hover:border-indigo-400 group-hover:text-indigo-500',
}

function cfg(ej) { return ESTADOS[ej.estado] ?? VACIO }
function nodeClass(ej) { return cfg(ej).node }
</script>
