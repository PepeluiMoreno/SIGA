<template>
  <!-- ══════════ Modo VERTICAL (para FilterRail lateral) ══════════ -->
  <div v-if="vertical" class="space-y-4">

    <!-- Búsqueda (ancho completo) -->
    <div v-if="search !== undefined" class="relative">
      <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
      <input
        :value="search"
        @input="$emit('update:search', $event.target.value)"
        type="text"
        :placeholder="searchPlaceholder"
        class="w-full h-9 pl-8 pr-7 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      />
      <button v-if="search" @click="$emit('update:search', '')" tabindex="-1"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
        <XMarkIcon class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Slot para filtros especiales (p.ej. ámbito territorial) -->
    <slot name="filters-prefix" />

    <!-- Campos apilados -->
    <div v-for="field in visibleFields" :key="field.key">
      <!-- Toggle -->
      <label v-if="field.type === 'toggle'" class="flex items-center gap-2 text-sm cursor-pointer select-none">
        <input type="checkbox" :checked="modelValue[field.key]"
          @change="update(field.key, $event.target.checked)"
          class="w-4 h-4 text-indigo-600 border-slate-300 rounded" />
        <span class="text-slate-700">{{ field.label }}</span>
      </label>

      <!-- Resto: etiqueta + control en línea (sin popover) -->
      <div v-else class="space-y-1.5">
        <span class="block text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ field.label }}</span>

        <!-- Slot personalizado (override) -->
        <slot v-if="$slots['dropdown-' + field.key]"
          :name="'dropdown-' + field.key"
          :filters="modelValue"
          :setFilters="setFilters"
          :close="() => {}" />

        <!-- Auto: single select -->
        <div v-else-if="field.type === 'select'" class="space-y-0.5">
          <button type="button" @click="update(field.key, '')"
            :class="['w-full text-left px-2 py-1.5 text-sm rounded transition-colors',
              !modelValue[field.key] ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-600 hover:bg-slate-50']">
            {{ field.allLabel || 'Todas' }}
          </button>
          <button type="button" v-for="opt in field.options" :key="opt.value"
            @click="update(field.key, opt.value)"
            :class="['w-full text-left px-2 py-1.5 text-sm rounded transition-colors',
              modelValue[field.key] === opt.value ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700 hover:bg-slate-50']">
            {{ opt.label }}
          </button>
        </div>

        <!-- Auto: multiselect ('Todos' = sin selección concreta) -->
        <div v-else-if="field.type === 'multiselect'" class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-slate-50">
            <input type="checkbox" :checked="!(modelValue[field.key] || []).length"
              @change="update(field.key, [])"
              class="w-4 h-4 text-indigo-600 border-slate-300 rounded" />
            <span class="text-sm font-medium text-slate-900">{{ field.allLabel || 'Todos' }}</span>
          </label>
          <label v-for="opt in field.options" :key="opt.value"
            class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-slate-50">
            <input type="checkbox" :checked="(modelValue[field.key] || []).includes(opt.value)"
              @change="toggleOption(field, opt.value, $event.target.checked)"
              class="w-4 h-4 text-indigo-600 border-slate-300 rounded" />
            <span class="text-sm text-slate-700">{{ opt.label }}</span>
          </label>
        </div>

        <p v-if="field.hint" class="text-xs text-slate-400">{{ field.hint }}</p>
      </div>
    </div>

    <!-- Limpiar -->
    <button v-if="hasActive || (search !== undefined && search)" @click="doClear"
      class="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-500 hover:text-red-600 hover:border-red-300 transition-colors">
      <XMarkIcon class="w-3.5 h-3.5" />
      Limpiar filtros
    </button>

    <p v-if="description" class="text-xs text-indigo-700 italic">{{ description }}</p>
  </div>

  <!-- ══════════ Modo HORIZONTAL (por defecto) ══════════ -->
  <div v-else class="bg-white border border-gray-200 rounded-lg p-3" @click.self="open = null">

    <!-- ── Fila 1: Nuevo + Búsqueda + botones de acción (nunca se rompe) ── -->
    <div class="flex items-center gap-2">

      <!-- Nuevo button -->
      <RouterLink v-if="createLabel && createRoute" :to="createRoute"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 shrink-0 transition-colors">
        <PlusIcon class="w-4 h-4" />
        {{ createLabel }}
      </RouterLink>
      <button v-else-if="createLabel" @click="$emit('create')"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 shrink-0 transition-colors">
        <PlusIcon class="w-4 h-4" />
        {{ createLabel }}
      </button>

      <!-- Búsqueda libre (siempre instantánea) -->
      <div v-if="search !== undefined" class="relative shrink-0">
        <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        <input
          :value="search"
          @input="$emit('update:search', $event.target.value)"
          type="text"
          :placeholder="searchPlaceholder"
          class="h-9 pl-8 pr-7 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 w-52 sm:w-72"
        />
        <button v-if="search"
          @click="$emit('update:search', '')"
          tabindex="-1"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
          <XMarkIcon class="w-3.5 h-3.5" />
        </button>
      </div>

      <span class="flex-1" />

      <!-- Indicador de carga sutil (modo lazy con debounce) + contador -->
      <span v-if="lazy && loading" class="flex items-center gap-1.5 text-xs text-gray-400 shrink-0">
        <span class="w-3 h-3 border-2 border-gray-300 border-t-purple-500 rounded-full animate-spin" />
        Buscando…
      </span>
      <span v-else-if="countText" class="text-xs text-gray-400 shrink-0">{{ countText }}</span>

    </div>

    <!-- ── Fila 2: Filtros en píldoras (hacen wrap libremente) ─────────── -->
    <div v-if="visibleFields.length || $slots['filters-prefix']" class="flex flex-wrap items-center gap-2 mt-2">

      <!-- Slot para filtros especiales (p.ej. AgrupacionCascada) — antes de las píldoras estándar -->
      <slot name="filters-prefix" />

      <!-- Separador visual si hay contenido en el slot y también hay píldoras -->
      <span v-if="$slots['filters-prefix'] && visibleFields.length"
        class="h-5 w-px bg-gray-200 shrink-0 self-center" />

      <template v-for="field in visibleFields" :key="field.key">

        <!-- Toggle: inline checkbox pill -->
        <label v-if="field.type === 'toggle'"
          :class="[
            'flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm cursor-pointer transition-colors select-none',
            modelValue[field.key]
              ? 'bg-purple-100 border-purple-300 text-purple-800'
              : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
          ]">
          <input type="checkbox"
            :checked="modelValue[field.key]"
            @change="update(field.key, $event.target.checked)"
            class="w-3.5 h-3.5 text-purple-600 border-gray-300 rounded" />
          <span>{{ field.label }}</span>
        </label>

        <!-- Dropdown pill (select / multiselect / custom) -->
        <div v-else class="relative"
          @mouseenter="cancelClose(field.key)"
          @mouseleave="scheduleClose(field.key)">

          <button type="button"
            @click.stop="open = open === field.key ? null : field.key"
            :class="[
              'flex items-center gap-1 px-3 py-1.5 rounded-full border text-sm transition-colors select-none',
              isActive(field)
                ? 'bg-purple-100 border-purple-300 text-purple-800'
                : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
            ]">
            <span>{{ computedPillLabel(field) }}</span>
            <ChevronDownIcon
              class="w-3 h-3 opacity-60 transition-transform"
              :class="open === field.key ? 'rotate-180' : ''" />
          </button>

          <!-- pt-1 creates a transparent bridge over the 4px gap so mouseleave doesn't fire -->
          <div v-if="open === field.key"
            class="absolute left-0 top-full z-30 pt-1"
            @click.stop>
            <div class="bg-white border border-gray-200 rounded-lg shadow-lg p-3"
              :class="field.width || 'w-64'">

              <!-- Named slot overrides auto-render -->
              <slot v-if="$slots['dropdown-' + field.key]"
                :name="'dropdown-' + field.key"
                :filters="modelValue"
                :setFilters="setFilters"
                :close="() => (open = null)" />

              <!-- Auto: single select -->
              <div v-else-if="field.type === 'select'" class="space-y-0.5">
                <button type="button"
                  @click="update(field.key, ''); open = null"
                  :class="[
                    'w-full text-left px-2 py-1.5 text-sm rounded transition-colors',
                    !modelValue[field.key]
                      ? 'bg-purple-50 text-purple-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-50'
                  ]">
                  {{ field.allLabel || 'Todas' }}
                </button>
                <button type="button"
                  v-for="opt in field.options" :key="opt.value"
                  @click="update(field.key, opt.value); open = null"
                  :class="[
                    'w-full text-left px-2 py-1.5 text-sm rounded transition-colors',
                    modelValue[field.key] === opt.value
                      ? 'bg-purple-50 text-purple-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  ]">
                  {{ opt.label }}
                </button>
              </div>

              <!-- Auto: multiselect checkboxes -->
              <div v-else-if="field.type === 'multiselect'" class="space-y-1">
                <label class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
                  <input type="checkbox"
                    :checked="!(modelValue[field.key] || []).length"
                    @change="update(field.key, [])"
                    class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
                  <span class="text-sm font-medium text-gray-900">{{ field.allLabel || 'Todos' }}</span>
                </label>
                <label v-for="opt in field.options" :key="opt.value"
                  class="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-50">
                  <input type="checkbox"
                    :checked="(modelValue[field.key] || []).includes(opt.value)"
                    @change="toggleOption(field, opt.value, $event.target.checked)"
                    class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
                  <span class="text-sm text-gray-700">{{ opt.label }}</span>
                </label>
              </div>

              <p v-if="field.hint" class="text-xs text-gray-400 mt-2">{{ field.hint }}</p>
            </div>
          </div>

        </div>
      </template>

      <!-- Limpiar: × al final de las píldoras, solo si hay filtros activos (lazy o live) -->
      <button v-if="hasActive" @click="doClear"
        class="flex items-center gap-1 px-3 py-1.5 rounded-full border border-gray-200 text-sm text-gray-500 hover:text-red-600 hover:border-red-300 transition-colors">
        <XMarkIcon class="w-3.5 h-3.5" />
        Limpiar
      </button>

    </div>

    <!-- Descripción (literal, computado en el padre) -->
    <p v-if="description" class="mt-2 text-xs text-purple-700 italic px-1">{{ description }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ChevronDownIcon, XMarkIcon, MagnifyingGlassIcon, PlusIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue:        { type: Object,  required: true },
  fields:            { type: Array,   default: () => [] },
  description:       { type: String,  default: '' },
  lazy:              { type: Boolean, default: false },
  loading:           { type: Boolean, default: false },
  countText:         { type: String,  default: '' },
  // Búsqueda integrada (undefined = no mostrar el input)
  search:            { type: String },
  searchPlaceholder: { type: String,  default: 'Buscar…' },
  // Botón de creación
  createLabel:       { type: String,  default: '' },
  createRoute:       { type: String,  default: '' },
  // Retardo del auto-apply en modo lazy (ms)
  debounce:          { type: Number,  default: 400 },
  // Disposición vertical (para alojarlo en el FilterRail lateral)
  vertical:          { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'update:search', 'apply', 'clear', 'create'])

// ── Modo lazy: auto-aplicar con debounce (sin botón "Buscar") ──────────────────
let debounceTimer = null
function scheduleApply() {
  if (!props.lazy) return
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => emit('apply'), props.debounce)
}
watch(
  () => [props.modelValue, props.search],
  () => scheduleApply(),
  { deep: true }
)

const open   = ref(null)
const timers = {}

function scheduleClose(key) {
  timers[key] = setTimeout(() => { if (open.value === key) open.value = null }, 120)
}
function cancelClose(key) { clearTimeout(timers[key]) }

function onKeydown(e) { if (e.key === 'Escape') open.value = null }
onMounted(()   => document.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  clearTimeout(debounceTimer)
})

const visibleFields = computed(() => props.fields.filter(f => !f.hidden))

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
function setFilters(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}
function toggleOption(field, value, checked) {
  const current = [...(props.modelValue[field.key] || [])]
  if (checked) current.push(value)
  else current.splice(current.indexOf(value), 1)
  update(field.key, current)
}
function toggleAll(field, checked) {
  update(field.key, checked ? (field.options || []).map(o => o.value) : [])
}
function isAllSelected(field) {
  const sel = props.modelValue[field.key] || []
  return sel.length > 0 && sel.length === (field.options || []).length
}
function isSomeSelected(field) {
  return (props.modelValue[field.key] || []).length > 0
}
function isActive(field) {
  if (field.isActive) return field.isActive(props.modelValue[field.key], props.modelValue)
  if (field.type === 'select') return !!props.modelValue[field.key]
  if (field.type === 'multiselect') {
    const sel = props.modelValue[field.key] || []
    return sel.length > 0 && sel.length < (field.options || []).length
  }
  return false
}
function computedPillLabel(field) {
  if (field.pillLabel) return field.pillLabel(props.modelValue[field.key], props.modelValue)
  if (field.type === 'select') {
    const val = props.modelValue[field.key]
    if (!val) return field.label
    return (field.options || []).find(o => o.value === val)?.label || field.label
  }
  if (field.type === 'multiselect') {
    const sel = props.modelValue[field.key] || []
    const total = (field.options || []).length
    if (!sel.length || sel.length === total) return field.label
    return `${field.label} · ${sel.length}`
  }
  return field.label ?? ''
}

const hasActive = computed(() => props.fields.some(f => !f.hidden && isActive(f)))

function doClear() {
  const empty = {}
  props.fields.forEach(f => {
    if (f.defaultValue !== undefined) {
      empty[f.key] = Array.isArray(f.defaultValue) ? [...f.defaultValue] : f.defaultValue
    } else if (f.type === 'multiselect') {
      empty[f.key] = []
    } else if (f.type === 'toggle') {
      empty[f.key] = false
    } else {
      empty[f.key] = ''
    }
  })
  if (props.search !== undefined) emit('update:search', '')
  emit('update:modelValue', empty)
  emit('clear')
}
</script>
