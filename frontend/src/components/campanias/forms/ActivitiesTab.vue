<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium text-gray-900">Programación de Actividades</h3>
      <button
        type="button"
        @click="$emit('open-activity-modal')"
        class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 flex items-center"
      >
        <span class="mr-2">+</span>
        Nueva Actividad
      </button>
    </div>

    <!-- Vista de lista -->
    <div v-if="actividades.length === 0" class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <span class="text-2xl">📅</span>
      </div>
      <h3 class="text-sm font-medium text-gray-900">No hay actividades programadas</h3>
      <p class="text-sm text-gray-500 mt-1">Comienza planificando las actividades de esta campaña.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="(actividad, index) in actividades"
        :key="actividad.id"
        class="p-3 border border-gray-200 rounded-lg bg-white hover:bg-gray-50"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h5 class="font-medium text-gray-900">{{ actividad.nombre }}</h5>
            <div class="flex items-center space-x-4 mt-1 text-sm text-gray-600">
              <span>📅 {{ formatDate(actividad.fecha) }}</span>
              <span v-if="actividad.hora_inicio">
                🕒 {{ actividad.hora_inicio }}{{ actividad.hora_fin ? ` - ${actividad.hora_fin}` : '' }}
              </span>
              <span v-if="actividad.lugar">📍 {{ actividad.lugar }}</span>
            </div>
            <p class="text-sm text-gray-700 mt-2">{{ actividad.descripcion }}</p>
            
            <div class="flex items-center space-x-4 mt-3">
              <span class="text-xs text-gray-500">
                👥 {{ actividad.voluntarios_confirmados || 0 }}/{{ actividad.voluntarios_necesarios || 0 }} voluntarios
              </span>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="actividad.completada ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                {{ actividad.completada ? 'Completada' : 'Pendiente' }}
              </span>
            </div>
          </div>
          
          <div class="flex space-x-2 ml-4">
            <button
              type="button"
              @click="$emit('open-activity-modal', index)"
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

    <!-- Logística general -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-3">Logística General</h4>
      <textarea
        v-model="campania.logistica"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        placeholder="Notas generales sobre logística, materiales, etc..."
      />
    </div>
  </div>
  <ConfirmModal
    v-model="showConfirmDelete"
    title-soft="¿Eliminar esta actividad?"
    title="¿Eliminar esta actividad?"
    message="Esta operación no se puede deshacer."
    @confirm="confirmarDelete"
  />
</template>

<script setup>
import { ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
const props = defineProps({
  actividades: {
    type: Array,
    required: true
  },
  campania: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'update:actividades',
  'update:campania',
  'open-activity-modal'
])

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
    emit('update:actividades', props.actividades.filter((_, i) => i !== pendingDeleteIndex.value))
    pendingDeleteIndex.value = null
  }
}
</script>