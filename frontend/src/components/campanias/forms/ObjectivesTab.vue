<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium text-gray-900">Objetivos de la Campaña</h3>
      <button
        type="button"
        @click="$emit('open-objective-modal')"
        class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 flex items-center"
      >
        <span class="mr-2">+</span>
        Añadir Objetivo
      </button>
    </div>

    <!-- Lista de objetivos -->
    <div v-if="objetivos.length === 0" class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <span class="text-2xl">🎯</span>
      </div>
      <h3 class="text-sm font-medium text-gray-900">No hay objetivos definidos</h3>
      <p class="text-sm text-gray-500 mt-1">Comienza definiendo los objetivos de esta campaña.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(objetivo, index) in objetivos"
        :key="objetivo.id"
        class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center mb-2">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2" 
                    :class="getObjetivoTypeClass(objetivo.tipo)">
                {{ getObjetivoTypeName(objetivo.tipo) }}
              </span>
              <span class="text-sm text-gray-500">Prioridad: {{ objetivo.prioridad }}</span>
            </div>
            <h4 class="font-medium text-gray-900">{{ objetivo.titulo }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ objetivo.descripcion }}</p>
            
            <div v-if="objetivo.meta" class="mt-3">
              <div class="flex justify-between text-xs text-gray-500 mb-1">
                <span>Progreso</span>
                <span>{{ objetivo.progreso || 0 }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-green-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: (objetivo.progreso || 0) + '%' }"
                ></div>
              </div>
            </div>

            <div v-if="objetivo.fecha_limite" class="mt-2 text-xs text-gray-500">
              <span>📅 Límite: {{ formatDate(objetivo.fecha_limite) }}</span>
            </div>
          </div>
          
          <div class="flex space-x-2 ml-4">
            <button
              type="button"
              @click="$emit('open-objective-modal', index)"
              class="p-1 text-gray-400 hover:text-blue-600"
              title="Editar"
            >
              ✏️
            </button>
            <button
              type="button"
              @click="pendingDeleteIndex = index; showConfirmDelete = true"
              class="p-1 text-gray-400 hover:text-red-600"
              title="Eliminar"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Objetivo principal -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-3">Objetivo Principal</h4>
      <textarea
        v-model="campania.objetivo_principal"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        placeholder="Describe el objetivo principal de esta campaña..."
      />
    </div>
  </div>
  <ConfirmModal
    v-model="showConfirmDelete"
    title-soft="¿Eliminar este objetivo?"
    title="¿Eliminar este objetivo?"
    message="Esta operación no se puede deshacer."
    @confirm="confirmarDelete"
  />
</template>

<script setup>
import { ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const props = defineProps({
  objetivos: {
    type: Array,
    required: true
  },
  campania: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'update:objetivos',
  'update:campania',
  'open-objective-modal'
])

const getObjetivoTypeClass = (tipo) => {
  const classes = {
    'cuantitativo': 'bg-blue-100 text-blue-800',
    'cualitativo': 'bg-purple-100 text-purple-800',
    'estrategico': 'bg-green-100 text-green-800',
    'operativo': 'bg-yellow-100 text-yellow-800'
  }
  return classes[tipo] || 'bg-gray-100 text-gray-800'
}

const getObjetivoTypeName = (tipo) => {
  const names = {
    'cuantitativo': 'Cuantitativo',
    'cualitativo': 'Cualitativo',
    'estrategico': 'Estratégico',
    'operativo': 'Operativo'
  }
  return names[tipo] || tipo
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const showConfirmDelete = ref(false)
const pendingDeleteIndex = ref(null)

function confirmarDelete() {
  if (pendingDeleteIndex.value !== null) {
    emit('update:objetivos', props.objetivos.filter((_, i) => i !== pendingDeleteIndex.value))
    pendingDeleteIndex.value = null
  }
}
</script>