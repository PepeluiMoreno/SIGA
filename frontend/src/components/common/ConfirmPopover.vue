<template>
  <div class="relative inline-block" ref="wrapperRef">
    <!-- Trigger — el botón original que dispara la acción -->
    <slot :open="abrir" />

    <!-- Popover de confirmación -->
    <Transition name="popover">
      <div
        v-if="visible"
        ref="popoverRef"
        class="absolute z-50 w-64 bg-white rounded-xl shadow-xl border border-slate-200 p-4"
        :class="positionClass"
        role="alertdialog"
        :aria-labelledby="popoverId"
      >
        <!-- Flecha decorativa -->
        <div class="absolute w-2.5 h-2.5 bg-white border-slate-200 rotate-45"
             :class="arrowClass" />

        <div class="relative">
          <!-- Icono + título -->
          <div class="flex items-start gap-2.5 mb-3">
            <div class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center"
                 :class="iconBg">
              <component :is="icono" class="w-4 h-4" :class="iconColor" />
            </div>
            <div>
              <p :id="popoverId" class="text-sm font-semibold text-slate-800 leading-tight">
                {{ titulo }}
              </p>
              <p v-if="mensaje" class="text-xs text-slate-500 mt-0.5 leading-snug">
                {{ mensaje }}
              </p>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex gap-2 justify-end">
            <button
              @click="cancelar"
              class="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            >
              {{ etiquetaCancelar }}
            </button>
            <button
              @click="confirmar"
              :disabled="cargando"
              class="px-3 py-1.5 text-xs font-medium text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5"
              :class="confirmClass"
            >
              <span v-if="cargando" class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {{ etiquetaConfirmar }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ExclamationTriangleIcon, TrashIcon, XCircleIcon, QuestionMarkCircleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  titulo:            { type: String,  default: '¿Confirmar acción?' },
  mensaje:           { type: String,  default: '' },
  /** 'peligro' | 'aviso' | 'neutro' */
  variante:          { type: String,  default: 'peligro' },
  etiquetaConfirmar: { type: String,  default: 'Confirmar' },
  etiquetaCancelar:  { type: String,  default: 'Cancelar' },
  /** 'top' | 'bottom' | 'left' | 'right' */
  posicion:          { type: String,  default: 'top' },
  cargando:          { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])

const visible = ref(false)
const wrapperRef = ref(null)
const popoverRef = ref(null)
const popoverId = `popover-${Math.random().toString(36).slice(2)}`

function abrir() { visible.value = true }
function cancelar() { visible.value = false; emit('cancel') }
function confirmar() { emit('confirm'); visible.value = false }

// Cerrar al hacer click fuera
function onClickOutside(e) {
  if (visible.value && wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    cancelar()
  }
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))

const VARIANTES = {
  peligro: {
    icon: TrashIcon,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    confirmClass: 'bg-red-600 hover:bg-red-700',
  },
  aviso: {
    icon: ExclamationTriangleIcon,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    confirmClass: 'bg-amber-600 hover:bg-amber-700',
  },
  neutro: {
    icon: QuestionMarkCircleIcon,
    iconBg: 'bg-slate-100',
    iconColor: 'text-slate-600',
    confirmClass: 'bg-slate-700 hover:bg-slate-800',
  },
}

const icono       = computed(() => VARIANTES[props.variante]?.icon        ?? VARIANTES.neutro.icon)
const iconBg      = computed(() => VARIANTES[props.variante]?.iconBg      ?? VARIANTES.neutro.iconBg)
const iconColor   = computed(() => VARIANTES[props.variante]?.iconColor   ?? VARIANTES.neutro.iconColor)
const confirmClass= computed(() => VARIANTES[props.variante]?.confirmClass?? VARIANTES.neutro.confirmClass)

const POSITIONS = {
  top:    'bottom-full mb-2 left-1/2 -translate-x-1/2',
  bottom: 'top-full mt-2 left-1/2 -translate-x-1/2',
  left:   'right-full mr-2 top-1/2 -translate-y-1/2',
  right:  'left-full ml-2 top-1/2 -translate-y-1/2',
}
const ARROWS = {
  top:    'bottom-[-5px] left-1/2 -translate-x-1/2 border-b border-r',
  bottom: 'top-[-5px] left-1/2 -translate-x-1/2 border-t border-l',
  left:   'right-[-5px] top-1/2 -translate-y-1/2 border-t border-r',
  right:  'left-[-5px] top-1/2 -translate-y-1/2 border-b border-l',
}

const positionClass = computed(() => POSITIONS[props.posicion] ?? POSITIONS.top)
const arrowClass    = computed(() => ARROWS[props.posicion]    ?? ARROWS.top)
</script>

<style scoped>
.popover-enter-active, .popover-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.popover-enter-from, .popover-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
