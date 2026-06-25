<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-end sm:items-stretch"
        :class="{ 'select-none cursor-col-resize': dragging }"
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
          :style="panelStyle"
        >
          <!-- Tirador de redimensión (solo escritorio) — arrastra para ensanchar -->
          <div
            v-if="resizable"
            class="hidden sm:block absolute inset-y-0 left-0 w-2 z-10 cursor-col-resize group touch-none"
            role="separator"
            aria-orientation="vertical"
            aria-label="Ensanchar panel"
            @pointerdown="startResize"
            @pointermove="onResize"
            @pointerup="endResize"
            @pointercancel="endResize"
            @dblclick="resetWidth"
          >
            <div
              class="absolute inset-y-0 left-0 w-px bg-slate-200 transition-colors group-hover:bg-indigo-400"
              :class="{ '!bg-indigo-500 w-0.5': dragging }"
            />
          </div>

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
  /** 'sm' (384px) | 'md' (512px) | 'lg' (672px) | 'xl' (768px) */
  size:            { type: String,  default: 'md' },
  closeOnBackdrop: { type: Boolean, default: true },
  /** Permite ensanchar el panel arrastrando su borde izquierdo (solo escritorio). */
  resizable:       { type: Boolean, default: true },
  /**
   * Identificador para recordar el ancho entre sesiones. Cada drawer con una
   * clave distinta recuerda su ancho de forma independiente; si se omite, se
   * agrupan por `size`.
   */
  storageKey:      { type: String,  default: '' },
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

// ── Redimensión + memoria de ancho ─────────────────────────────────────────
const DEFAULT_PX = { sm: 384, md: 512, lg: 672, xl: 768 }
const MIN_WIDTH = 320

const width = ref(DEFAULT_PX[props.size] ?? DEFAULT_PX.md)
const dragging = ref(false)
const isDesktop = ref(true)
let startX = 0
let startWidth = 0
let mediaQuery = null

const persistKey = computed(() => `siga.drawer.width.${props.storageKey || props.size}`)

// Inline solo en escritorio: gana al `sm:max-w-*` y deja intacto el bottom-sheet móvil.
const panelStyle = computed(() =>
  props.resizable && isDesktop.value
    ? { width: `${width.value}px`, maxWidth: '95vw' }
    : {}
)

function clampWidth(px) {
  const max = Math.floor(window.innerWidth * 0.95)
  return Math.min(Math.max(Math.round(px), MIN_WIDTH), max)
}

function loadWidth() {
  let initial = DEFAULT_PX[props.size] ?? DEFAULT_PX.md
  try {
    const saved = localStorage.getItem(persistKey.value)
    const n = saved == null ? NaN : parseInt(saved, 10)
    if (Number.isFinite(n)) initial = n
  } catch { /* localStorage no disponible */ }
  width.value = clampWidth(initial)
}

function saveWidth() {
  try { localStorage.setItem(persistKey.value, String(width.value)) } catch { /* ignore */ }
}

function startResize(e) {
  if (!props.resizable) return
  dragging.value = true
  startX = e.clientX
  startWidth = width.value
  e.currentTarget.setPointerCapture?.(e.pointerId)
  e.preventDefault()
}

function onResize(e) {
  if (!dragging.value) return
  // El panel se ancla a la derecha: arrastrar hacia la izquierda lo ensancha.
  width.value = clampWidth(startWidth + (startX - e.clientX))
}

function endResize(e) {
  if (!dragging.value) return
  dragging.value = false
  try { e.currentTarget.releasePointerCapture?.(e.pointerId) } catch { /* ignore */ }
  saveWidth()
}

function resetWidth() {
  width.value = clampWidth(DEFAULT_PX[props.size] ?? DEFAULT_PX.md)
  saveWidth()
}

function onWindowResize() {
  width.value = clampWidth(width.value)
}

function cerrar() {
  emit('update:modelValue', false)
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape' && props.modelValue) cerrar()
}

function updateMedia() { isDesktop.value = mediaQuery ? mediaQuery.matches : true }

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', onWindowResize)
  mediaQuery = window.matchMedia('(min-width: 640px)')
  mediaQuery.addEventListener('change', updateMedia)
  updateMedia()
  loadWidth()
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onWindowResize)
  mediaQuery?.removeEventListener('change', updateMedia)
})
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
