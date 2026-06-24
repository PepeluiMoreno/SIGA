<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-end sm:items-stretch"
        role="dialog"
        :aria-labelledby="titleId"
        aria-modal="true"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/30 backdrop-blur-sm"
          @click="closeOnBackdrop && cerrar()"
        />

        <!-- Panel — bottom sheet en móvil, drawer lateral en sm+ -->
        <div
          ref="panel"
          tabindex="-1"
          class="relative flex flex-col bg-white shadow-2xl overflow-hidden focus:outline-none
                 w-full max-h-[90vh] rounded-t-2xl
                 sm:ml-auto sm:h-full sm:max-h-none sm:rounded-none sm:rounded-l-2xl"
          :class="widthClass"
        >
          <!-- Cabecera -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 shrink-0">
            <div>
              <h2 :id="titleId" class="text-base font-semibold text-slate-900">{{ title }}</h2>
              <p v-if="subtitle" class="text-xs text-slate-500 mt-0.5">{{ subtitle }}</p>
            </div>
            <button
              @click="cerrar"
              class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              aria-label="Cerrar"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Cuerpo — scrolleable -->
          <div class="flex-1 overflow-y-auto px-6 py-5 min-h-0">
            <slot />
          </div>

          <!-- Pie con acciones -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3 shrink-0 bg-slate-50">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useFocusTrap } from '@/composables/useFocusTrap'

const props = defineProps({
  modelValue:      { type: Boolean, default: false },
  title:           { type: String,  default: '' },
  subtitle:        { type: String,  default: '' },
  /** 'sm' (384px) | 'md' (512px) | 'lg' (640px) | 'xl' (768px) */
  size:            { type: String,  default: 'md' },
  closeOnBackdrop: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue', 'close'])

const titleId = `drawer-title-${Math.random().toString(36).slice(2)}`

const panel = ref(null)
useFocusTrap(panel, () => props.modelValue)

const WIDTH = {
  sm: 'sm:max-w-sm',
  md: 'sm:max-w-lg',
  lg: 'sm:max-w-2xl',
  xl: 'sm:max-w-3xl',
}
const widthClass = computed(() => WIDTH[props.size] ?? WIDTH.md)

function cerrar() {
  emit('update:modelValue', false)
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape' && props.modelValue) cerrar()
}
onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-active .relative,
.drawer-leave-active .relative {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-enter-from { opacity: 0; }
.drawer-leave-to  { opacity: 0; }
@media (max-width: 639px) {
  .drawer-enter-from .relative { transform: translateY(100%); }
  .drawer-leave-to  .relative  { transform: translateY(100%); }
}
@media (min-width: 640px) {
  .drawer-enter-from .relative { transform: translateX(100%); }
  .drawer-leave-to  .relative  { transform: translateX(100%); }
}
</style>
