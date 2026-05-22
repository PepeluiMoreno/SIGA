<template>
  <Teleport to="body">
    <div
      class="fixed bottom-4 right-4 left-4 sm:left-auto z-[100] flex flex-col gap-2 pointer-events-none items-end"
      aria-live="polite"
      aria-atomic="false"
    >
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg border w-full sm:max-w-sm text-sm font-medium"
          :class="STYLES[t.type]?.container"
        >
          <component
            :is="STYLES[t.type]?.icon"
            class="w-5 h-5 shrink-0 mt-0.5"
            :class="STYLES[t.type]?.iconColor"
          />

          <div class="flex-1 min-w-0">
            <p class="leading-snug">{{ t.message }}</p>
            <!-- Botón de acción (Deshacer u otra) -->
            <button
              v-if="t.accion"
              @click="t.accion.callback()"
              class="mt-1.5 text-xs font-semibold underline underline-offset-2 hover:no-underline opacity-80 hover:opacity-100 transition-opacity"
              :class="STYLES[t.type]?.iconColor"
            >
              {{ t.accion.label }}
            </button>
          </div>

          <button
            @click="remove(t.id)"
            class="shrink-0 opacity-50 hover:opacity-100 transition-opacity"
            :class="STYLES[t.type]?.iconColor"
            aria-label="Cerrar"
          >
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

const STYLES = {
  success: {
    container: 'bg-green-50 border-green-200 text-green-900',
    icon: CheckCircleIcon,
    iconColor: 'text-green-600',
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-900',
    icon: ExclamationCircleIcon,
    iconColor: 'text-red-600',
  },
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-900',
    icon: InformationCircleIcon,
    iconColor: 'text-blue-600',
  },
  warning: {
    container: 'bg-amber-50 border-amber-200 text-amber-900',
    icon: ExclamationTriangleIcon,
    iconColor: 'text-amber-600',
  },
}
</script>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from { opacity: 0; transform: translateX(100%) scale(0.95); }
.toast-leave-to   { opacity: 0; transform: translateX(100%) scale(0.95); }
.toast-move       { transition: transform 0.25s ease; }
</style>
