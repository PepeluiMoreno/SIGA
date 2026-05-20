<template>
  <div class="relative" ref="wrapperRef">
    <!-- Input de búsqueda -->
    <div class="relative">
      <input
        type="text"
        v-model="busqueda"
        :placeholder="placeholder"
        :disabled="disabled"
        @focus="abierto = true"
        @input="abierto = true"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 pr-8 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400"
      />
      <!-- Icono: X si hay selección, lupa si no -->
      <button v-if="modelValue" type="button" @click="limpiar"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
        <XMarkIcon class="w-4 h-4" />
      </button>
      <MagnifyingGlassIcon v-else class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300 pointer-events-none" />
    </div>

    <!-- Dropdown de resultados -->
    <div v-if="abierto && resultados.length > 0"
      class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-52 overflow-y-auto">
      <button
        v-for="m in resultados" :key="m.id"
        type="button"
        @click="seleccionar(m)"
        class="w-full text-left px-3 py-2 text-sm hover:bg-purple-50 flex items-center gap-3 transition-colors">
        <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-100 flex items-center justify-center text-xs font-medium text-purple-700">
          {{ iniciales(m) }}
        </div>
        <div class="min-w-0">
          <p class="font-medium text-gray-900 truncate">{{ m.nombre }} {{ m.apellido1 }} {{ m.apellido2 ?? '' }}</p>
          <p v-if="m.email" class="text-xs text-gray-400 truncate">{{ m.email }}</p>
        </div>
      </button>
    </div>

    <!-- Sin resultados -->
    <div v-if="abierto && busqueda.length >= 2 && resultados.length === 0"
      class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm text-gray-500">
      Sin resultados para «{{ busqueda }}»
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { XMarkIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: String, default: null },       // UUID del miembro seleccionado
  miembros:   { type: Array,  default: () => [] },   // Lista completa de miembros
  placeholder:{ type: String, default: 'Buscar miembro…' },
  disabled:   { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'select'])

const busqueda  = ref('')
const abierto   = ref(false)
const wrapperRef = ref(null)

// Cuando se recibe un valor externo, mostrar el nombre del miembro
watch(() => props.modelValue, (id) => {
  if (!id) { busqueda.value = ''; return }
  const m = props.miembros.find(x => x.id === id)
  if (m) busqueda.value = `${m.nombre} ${m.apellido1}`
}, { immediate: true })

const resultados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (q.length < 1) return props.miembros.slice(0, 8)
  return props.miembros
    .filter(m => `${m.nombre} ${m.apellido1} ${m.apellido2 ?? ''} ${m.email ?? ''}`.toLowerCase().includes(q))
    .slice(0, 8)
})

const iniciales = (m) => `${m.nombre[0] ?? ''}${m.apellido1[0] ?? ''}`.toUpperCase()

const seleccionar = (m) => {
  busqueda.value = `${m.nombre} ${m.apellido1}`
  abierto.value = false
  emit('update:modelValue', m.id)
  emit('select', m)
}

const limpiar = () => {
  busqueda.value = ''
  abierto.value = false
  emit('update:modelValue', null)
  emit('select', null)
}

// Cerrar al hacer clic fuera
const cerrarFuera = (e) => {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    abierto.value = false
    // Si hay un modelValue pero el texto no coincide, restaurar el nombre
    if (props.modelValue) {
      const m = props.miembros.find(x => x.id === props.modelValue)
      if (m) busqueda.value = `${m.nombre} ${m.apellido1}`
    }
  }
}

onMounted(() => document.addEventListener('mousedown', cerrarFuera))
onBeforeUnmount(() => document.removeEventListener('mousedown', cerrarFuera))
</script>
