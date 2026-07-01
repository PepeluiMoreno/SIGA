<template>
  <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
    <!-- Cabecera -->
    <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold text-slate-800">Nuevo presupuesto {{ ejercicio }}</h3>
        <p class="text-xs text-slate-500 mt-0.5">Elige cómo quieres crearlo</p>
      </div>
      <button @click="$emit('cancel')" class="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">
        <XMarkIcon class="w-4 h-4" />
      </button>
    </div>

    <div class="p-6">
      <!-- Selector de modo: 3 tarjetas -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
        <button
          @click="modo = 'nuevo'"
          class="relative flex flex-col items-start gap-2 p-4 rounded-xl border-2 text-left transition-all"
          :class="modo === 'nuevo' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="modo === 'nuevo' ? 'bg-indigo-100' : 'bg-slate-100'">
            <DocumentPlusIcon class="w-4 h-4" :class="modo === 'nuevo' ? 'text-indigo-600' : 'text-slate-500'" />
          </div>
          <div>
            <p class="text-sm font-semibold" :class="modo === 'nuevo' ? 'text-indigo-800' : 'text-slate-700'">Desde cero</p>
            <p class="text-xs mt-0.5" :class="modo === 'nuevo' ? 'text-indigo-600' : 'text-slate-500'">Partidas vacías</p>
          </div>
          <CheckBadge v-if="modo === 'nuevo'" />
        </button>

        <button
          @click="puedeClonarse && (modo = 'clonar')"
          :disabled="!puedeClonarse"
          class="relative flex flex-col items-start gap-2 p-4 rounded-xl border-2 text-left transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          :class="modo === 'clonar' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="modo === 'clonar' ? 'bg-indigo-100' : 'bg-slate-100'">
            <DocumentDuplicateIcon class="w-4 h-4" :class="modo === 'clonar' ? 'text-indigo-600' : 'text-slate-500'" />
          </div>
          <div>
            <p class="text-sm font-semibold" :class="modo === 'clonar' ? 'text-indigo-800' : 'text-slate-700'">Clonar {{ ejercicio - 1 }}</p>
            <p class="text-xs mt-0.5" :class="modo === 'clonar' ? 'text-indigo-600' : 'text-slate-500'">Copia con ajuste de cuota</p>
          </div>
          <CheckBadge v-if="modo === 'clonar'" />
        </button>

        <button
          @click="puedeProrrogarse && (modo = 'prorrogar')"
          :disabled="!puedeProrrogarse"
          class="relative flex flex-col items-start gap-2 p-4 rounded-xl border-2 text-left transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          :class="modo === 'prorrogar' ? 'border-amber-500 bg-amber-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="modo === 'prorrogar' ? 'bg-amber-100' : 'bg-slate-100'">
            <ArrowPathIcon class="w-4 h-4" :class="modo === 'prorrogar' ? 'text-amber-600' : 'text-slate-500'" />
          </div>
          <div>
            <p class="text-sm font-semibold" :class="modo === 'prorrogar' ? 'text-amber-800' : 'text-slate-700'">Prorrogar {{ ejercicio - 1 }}</p>
            <p class="text-xs mt-0.5" :class="modo === 'prorrogar' ? 'text-amber-700' : 'text-slate-500'">Extiende el aprobado</p>
          </div>
          <CheckBadge v-if="modo === 'prorrogar'" variante="amber" />
        </button>
      </div>

      <!-- Panel contextual: clonar muestra el factor de variación de cuota -->
      <Transition name="fade">
        <div v-if="modo === 'clonar'" class="mb-5 rounded-xl bg-slate-50 border border-slate-200 p-4">
          <div v-if="ratioCuota === null" class="flex items-center gap-2 text-sm text-slate-500">
            <span class="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin shrink-0" />
            Calculando variación prevista de ingresos…
          </div>

          <template v-else-if="ratioCuota.disponible">
            <div class="flex items-center justify-between mb-3">
              <div>
                <p class="text-sm font-medium text-slate-700">Variación de ingresos por cuotas</p>
                <p class="text-xs text-slate-500 mt-0.5">
                  {{ eur(ratioCuota.totalOrigen) }} ({{ ejercicio - 1 }}) → {{ eur(ratioCuota.totalNuevo) }} ({{ ejercicio }})
                </p>
              </div>
              <span class="text-sm font-bold px-3 py-1 rounded-full"
                :class="ratioCuota.variacionPorcentaje >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
                {{ ratioCuota.variacionPorcentaje >= 0 ? '+' : '' }}{{ ratioCuota.variacionPorcentaje.toFixed(1) }}%
              </span>
            </div>
            <label class="flex items-center gap-3 cursor-pointer group">
              <span
                @click="aplicarFactor = !aplicarFactor"
                class="relative w-9 h-5 rounded-full transition-colors shrink-0"
                :class="aplicarFactor ? 'bg-indigo-500' : 'bg-slate-300'"
              >
                <span class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
                  :class="aplicarFactor ? 'translate-x-4' : 'translate-x-0'" />
              </span>
              <span class="text-sm text-slate-700 group-hover:text-slate-900">
                Ajustar todas las partidas con este factor (×{{ ratioCuota.ratio.toFixed(4) }})
              </span>
            </label>
          </template>

          <div v-else class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            No hay datos suficientes para calcular el factor. Los importes se copiarán tal cual.
          </div>
        </div>
      </Transition>

      <!-- Panel contextual: prorrogar -->
      <Transition name="fade">
        <div v-if="modo === 'prorrogar'" class="mb-5 rounded-xl bg-amber-50 border border-amber-200 p-4 text-sm text-amber-800">
          La prórroga reutiliza el presupuesto aprobado de {{ ejercicio - 1 }} hasta que se apruebe
          uno nuevo para {{ ejercicio }}. Quedará marcado como prórroga.
        </div>
      </Transition>

      <!-- Acciones -->
      <div class="flex justify-end gap-2">
        <button @click="$emit('cancel')" class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors">
          Cancelar
        </button>
        <button
          @click="confirmar"
          :disabled="ocupado"
          class="px-4 py-2 text-white text-sm font-medium rounded-lg disabled:opacity-50 flex items-center gap-2 transition-colors"
          :class="modo === 'prorrogar' ? 'bg-amber-600 hover:bg-amber-700' : 'bg-indigo-600 hover:bg-indigo-700'"
        >
          <span v-if="ocupado" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          {{ textoBoton }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import {
  XMarkIcon, DocumentPlusIcon, DocumentDuplicateIcon, ArrowPathIcon, CheckIcon,
} from '@heroicons/vue/24/outline'

// Pequeño badge de selección reutilizable (check en círculo, esquina superior derecha)
const CheckBadge = (props) => h('div', {
  class: `absolute top-2 right-2 w-4 h-4 rounded-full flex items-center justify-center ${props.variante === 'amber' ? 'bg-amber-500' : 'bg-indigo-500'}`,
}, h(CheckIcon, { class: 'w-2.5 h-2.5 text-white' }))

const props = defineProps({
  ejercicio:        { type: Number, required: true },
  /** Resultado de GET_RATIO_VARIACION_CUOTA; null mientras carga */
  ratioCuota:       { type: Object, default: null },
  puedeClonarse:    { type: Boolean, default: true },
  puedeProrrogarse: { type: Boolean, default: false },
  ocupado:          { type: Boolean, default: false },
})

const emit = defineEmits(['cancel', 'crear', 'modo-cambiado'])

const modo = ref('nuevo')
const aplicarFactor = ref(false)

// Avisar al padre cuando cambia a 'clonar' para que cargue el ratio
watch(modo, (m) => emit('modo-cambiado', m))

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

const textoBoton = computed(() => ({
  nuevo:     'Crear presupuesto',
  clonar:    'Clonar y crear',
  prorrogar: 'Prorrogar',
}[modo.value]))

function confirmar() {
  const factor = (modo.value === 'clonar' && aplicarFactor.value && props.ratioCuota?.disponible)
    ? props.ratioCuota.ratio
    : null
  emit('crear', { modo: modo.value, factor })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
