<template>
  <!-- Contenedor: columna lateral en lg+, bloque apilado en móvil -->
  <div class="shrink-0 lg:sticky lg:top-0" :style="isDesktop && !collapsed ? { width: width + 'px' } : null">

    <!-- ── Raíl colapsado (solo escritorio): se "escamotea" a la izquierda ── -->
    <div v-if="isDesktop && collapsed"
      class="w-11 bg-white border border-slate-200 rounded-xl flex flex-col items-center py-3 gap-3">
      <button type="button" @click="toggle"
        class="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-50 transition-colors"
        title="Mostrar filtros">
        <ChevronRightIcon class="w-4 h-4" />
      </button>
      <span class="[writing-mode:vertical-rl] rotate-180 flex items-center gap-2 text-xs font-medium text-slate-500 tracking-wide select-none">
        <FunnelIcon class="w-4 h-4" />
        {{ title }}
      </span>
      <span v-if="activeCount"
        class="w-5 h-5 flex items-center justify-center text-[10px] font-semibold rounded-full bg-indigo-100 text-indigo-700">
        {{ activeCount }}
      </span>
    </div>

    <!-- ── Panel desplegado (y vista móvil) ── -->
    <div v-show="!(isDesktop && collapsed)"
      class="relative bg-white border border-slate-200 rounded-xl flex flex-col"
      :style="isDesktop ? { width: width + 'px' } : null">

      <div class="flex items-center justify-between px-3 py-2.5 border-b border-slate-100 shrink-0">
        <span class="flex items-center gap-1.5 text-sm font-semibold text-slate-700">
          <FunnelIcon class="w-4 h-4 text-slate-400" />
          {{ title }}
        </span>
        <button type="button" @click="toggle"
          class="hidden lg:inline-flex p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          title="Ocultar filtros">
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
      </div>

      <div class="p-3">
        <slot />
      </div>

      <!-- Tirador de redimensión (borde derecho, solo escritorio) -->
      <div v-if="isDesktop"
        class="absolute inset-y-0 -right-1 w-2 cursor-col-resize group touch-none"
        @pointerdown="startResize" @pointermove="onResize"
        @pointerup="endResize" @pointercancel="endResize" @dblclick="resetWidth">
        <div class="absolute inset-y-0 right-1 w-px bg-transparent group-hover:bg-indigo-300 transition-colors"
          :class="{ '!bg-indigo-500': dragging }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon, FunnelIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title:        { type: String, default: 'Filtros' },
  /** Clave para recordar estado (colapsado) y ancho de forma independiente por vista. */
  storageKey:   { type: String, default: 'default' },
  /** Nº de filtros activos: se muestra como badge cuando el raíl está colapsado. */
  activeCount:  { type: Number, default: 0 },
  defaultWidth: { type: Number, default: 280 },
})

const MIN_WIDTH = 220
const MAX_WIDTH = 460

const collapsed = ref(false)
const width = ref(props.defaultWidth)
const dragging = ref(false)
const isDesktop = ref(true)
let startX = 0
let startWidth = 0
let mediaQuery = null

const keyCollapsed = `siga.filterrail.${props.storageKey}.collapsed`
const keyWidth = `siga.filterrail.${props.storageKey}.width`

function clampWidth(px) {
  return Math.min(Math.max(Math.round(px), MIN_WIDTH), MAX_WIDTH)
}

function toggle() {
  collapsed.value = !collapsed.value
  try { localStorage.setItem(keyCollapsed, collapsed.value ? '1' : '0') } catch { /* ignore */ }
}

function startResize(e) {
  dragging.value = true
  startX = e.clientX
  startWidth = width.value
  e.currentTarget.setPointerCapture?.(e.pointerId)
  e.preventDefault()
}
function onResize(e) {
  if (!dragging.value) return
  // Panel anclado a la izquierda: arrastrar a la derecha lo ensancha.
  width.value = clampWidth(startWidth + (e.clientX - startX))
}
function endResize(e) {
  if (!dragging.value) return
  dragging.value = false
  try { e.currentTarget.releasePointerCapture?.(e.pointerId) } catch { /* ignore */ }
  try { localStorage.setItem(keyWidth, String(width.value)) } catch { /* ignore */ }
}
function resetWidth() {
  width.value = props.defaultWidth
  try { localStorage.setItem(keyWidth, String(width.value)) } catch { /* ignore */ }
}

function updateMedia() { isDesktop.value = mediaQuery ? mediaQuery.matches : true }

onMounted(() => {
  mediaQuery = window.matchMedia('(min-width: 1024px)')
  mediaQuery.addEventListener('change', updateMedia)
  updateMedia()
  try {
    collapsed.value = localStorage.getItem(keyCollapsed) === '1'
    const w = parseInt(localStorage.getItem(keyWidth), 10)
    if (Number.isFinite(w)) width.value = clampWidth(w)
  } catch { /* localStorage no disponible */ }
})
onUnmounted(() => mediaQuery?.removeEventListener('change', updateMedia))
</script>
