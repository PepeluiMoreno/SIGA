<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        :aria-labelledby="titleId"
        aria-modal="true"
        @keydown.esc="cerrar"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/40 backdrop-blur-sm"
          @click="closeOnBackdrop && cerrar()"
        />

        <!-- Panel -->
        <div
          ref="panel"
          tabindex="-1"
          class="relative bg-white rounded-xl shadow-xl w-full flex flex-col max-h-[90vh] focus:outline-none"
          :class="widthClass"
        >
          <!-- Cabecera -->
          <div v-if="title || $slots.header" class="flex items-center justify-between px-6 py-4 border-b border-slate-100 shrink-0">
            <slot name="header">
              <h2 :id="titleId" class="text-base font-semibold text-slate-900">{{ title }}</h2>
            </slot>
            <button
              v-if="showClose"
              @click="cerrar"
              class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              aria-label="Cerrar"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Cuerpo -->
          <div class="px-6 py-5 overflow-y-auto flex-1 min-h-0">
            <slot />
          </div>

          <!-- Pie (acciones) -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3 shrink-0">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useFocusTrap } from '@/composables/useFocusTrap'

const props = defineProps({
  modelValue:      { type: Boolean, default: false },
  title:           { type: String,  default: '' },
  /** 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' */
  size:            { type: String,  default: 'md' },
  showClose:       { type: Boolean, default: true },
  closeOnBackdrop: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue', 'close'])

const titleId = `modal-title-${Math.random().toString(36).slice(2)}`

const panel = ref(null)
useFocusTrap(panel, () => props.modelValue)

const WIDTH = {
  sm:   'max-w-sm',
  md:   'max-w-md',
  lg:   'max-w-lg',
  xl:   'max-w-xl',
  '2xl':'max-w-2xl',
  full: 'max-w-full mx-4',
}

const widthClass = computed(() => WIDTH[props.size] ?? WIDTH.md)

function cerrar() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.15s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.97) translateY(4px);
  opacity: 0;
}
</style>
