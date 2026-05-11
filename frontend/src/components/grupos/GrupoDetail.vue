<template>
  <div class="bg-white rounded-lg shadow">
    <!-- Header con tabs -->
    <div class="border-b border-gray-200">
      <div class="px-6 pt-4">
        <DetailHeader fallback="/grupos" />
      </div>

      <!-- Tabs -->
      <div class="px-6">
        <nav class="flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab.name }}
            <span v-if="tab.count" class="ml-2 bg-gray-100 text-gray-900 text-xs font-medium px-2 py-0.5 rounded-full">
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Content based on active tab -->
    <div class="p-6">
      <!-- Información General -->
      <div v-if="activeTab === 'info'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Información básica -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-gray-900">Información del Grupo</h3>
            <div>
              <span class="text-sm text-gray-600">Tipo de Grupo</span>
              <div class="mt-1 font-medium">{{ grupo.tipo_nombre }}</div>
            </div>
            <div>
              <span class="text-sm text-gray-600">Fecha inicio</span>
              <div class="mt-1 font-medium">{{ grupo.fecha_inicio }}</div>
            </div>
            <div>
              <span class="text-sm text-gray-600">Fecha fin</span>
              <div class="mt-1 font-medium">{{ grupo.fecha_fin || 'Permanente' }}</div>
            </div>
          </div>

          <!-- Presupuesto -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-gray-900">Presupuesto</h3>
            <div>
              <span class="text-sm text-gray-600">Asignado</span>
              <div class="mt-1 font-medium text-green-600">{{ formatCurrency(grupo.presupuesto_asignado) }}</div>
            </div>
            <div>
              <span class="text-sm text-gray-600">Ejecutado</span>
              <div class="mt-1 font-medium text-blue-600">{{ formatCurrency(grupo.presupuesto_ejecutado) }}</div>
            </div>
            <div class="pt-2">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-green-600 h-2 rounded-full"
                  :style="{ width: presupuestoPorcentaje + '%' }"
                ></div>
              </div>
              <div class="text-xs text-gray-600 mt-1">
                {{ presupuestoPorcentaje }}% del presupuesto ejecutado
              </div>
            </div>
          </div>
        </div>

        <!-- Objetivo -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-3">Objetivo</h3>
          <p class="text-gray-700 bg-gray-50 p-4 rounded-lg">{{ grupo.objetivo }}</p>
        </div>
      </div>

      <!-- Miembros -->
      <div v-else-if="activeTab === 'members'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Miembros del Grupo</h3>
          <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
            + Añadir Miembro
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="miembro in miembros"
            :key="miembro.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div class="flex items-start space-x-3">
              <div class="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                {{ getInitials(miembro.nombre) }}
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-gray-900">{{ miembro.nombre }}</h4>
                <p class="text-sm text-gray-600">{{ miembro.rol }}</p>
                <p class="text-xs text-gray-500 mt-1">Desde {{ miembro.fecha_incorporacion }}</p>
              </div>
              <div class="relative">
                <button class="p-1 text-gray-400 hover:text-gray-600">
                  •••
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tareas -->
      <div v-else-if="activeTab === 'tasks'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Tareas</h3>
          <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
            + Nueva Tarea
          </button>
        </div>

        <div class="space-y-3">
          <div
            v-for="tarea in tareas"
            :key="tarea.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-medium text-gray-900">{{ tarea.titulo }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ tarea.descripcion }}</p>
                <div class="flex items-center space-x-4 mt-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="tarea.prioridadClass">
                    {{ tarea.prioridadText }}
                  </span>
                  <span class="text-sm text-gray-600">{{ tarea.fecha_limite }}</span>
                  <span class="text-sm text-gray-600">{{ tarea.asignado_a }}</span>
                </div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="tarea.estadoClass">
                {{ tarea.estado }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Reuniones -->
      <div v-else-if="activeTab === 'meetings'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Reuniones</h3>
          <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
            + Nueva Reunión
          </button>
        </div>

        <div class="space-y-4">
          <div
            v-for="reunion in reuniones"
            :key="reunion.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-medium text-gray-900">{{ reunion.titulo }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ reunion.fecha }} · {{ reunion.hora_inicio }} - {{ reunion.hora_fin }}</p>
                <p class="text-sm text-gray-700 mt-2">{{ reunion.descripcion }}</p>
                <div class="mt-3 flex items-center space-x-2">
                  <span class="text-sm text-gray-600">{{ reunion.asistentes }} asistentes</span>
                  <span v-if="reunion.url_online" class="text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                    🔗 Enlace
                  </span>
                </div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="reunion.realizada ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                {{ reunion.realizada ? 'Realizada' : 'Planificada' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailHeader from '@/components/common/DetailHeader.vue'

const route = useRoute()
const activeTab = ref('info')

const grupo = ref({
  id: route.params.id,
  nombre: 'Grupo de Comunicación',
  descripcion: 'Grupo encargado de la comunicación interna y externa',
  tipo_nombre: 'Permanente',
  fecha_inicio: '2024-01-15',
  fecha_fin: null,
  presupuesto_asignado: 5000,
  presupuesto_ejecutado: 3250,
  objetivo: 'Mejorar la comunicación interna y gestionar las redes sociales de la organización.'
})

const miembros = ref([
  { id: 1, nombre: 'Ana García', rol: 'Coordinadora', fecha_incorporacion: '2024-01-15' },
  { id: 2, nombre: 'Carlos Ruiz', rol: 'Redactor', fecha_incorporacion: '2024-02-01' },
  { id: 3, nombre: 'María López', rol: 'Community Manager', fecha_incorporacion: '2024-01-20' }
])

const tareas = ref([
  { id: 1, titulo: 'Redactar boletín mensual', descripcion: 'Preparar contenido para el boletín de marzo', fecha_limite: '2024-03-15', asignado_a: 'Carlos Ruiz', prioridad: 1, estado: 'En progreso' },
  { id: 2, titulo: 'Actualizar redes sociales', descripcion: 'Programar publicaciones para la próxima semana', fecha_limite: '2024-03-10', asignado_a: 'María López', prioridad: 2, estado: 'Pendiente' }
])

const reuniones = ref([
  { id: 1, titulo: 'Reunión semanal', descripcion: 'Revisión de tareas y planificación', fecha: '2024-03-08', hora_inicio: '10:00', hora_fin: '11:30', asistentes: 3, realizada: true, url_online: 'https://meet.google.com/xxx' },
  { id: 2, titulo: 'Planificación mensual', descripcion: 'Planificación del contenido de abril', fecha: '2024-03-15', hora_inicio: '16:00', hora_fin: '17:30', asistentes: 3, realizada: false, url_online: null }
])

const tabs = computed(() => [
  { id: 'info', name: 'Información', count: null },
  { id: 'members', name: 'Miembros', count: miembros.value.length },
  { id: 'tasks', name: 'Tareas', count: tareas.value.length },
  { id: 'meetings', name: 'Reuniones', count: reuniones.value.length }
])

const presupuestoPorcentaje = computed(() => {
  if (!grupo.value.presupuesto_asignado) return 0
  return Math.round((grupo.value.presupuesto_ejecutado / grupo.value.presupuesto_asignado) * 100)
})

const formatCurrency = (value) => {
  if (!value) return '€0.00'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

const getInitials = (name) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}

onMounted(() => {
  // Aquí cargarías los datos del grupo
  console.log('Cargando grupo:', route.params.id)
})

// Computed para clases de prioridad y estado
tareas.value.forEach(tarea => {
  tarea.prioridadClass = tarea.prioridad === 1 ? 'bg-red-100 text-red-800' : 
                         tarea.prioridad === 2 ? 'bg-yellow-100 text-yellow-800' : 
                         'bg-green-100 text-green-800'
  tarea.prioridadText = tarea.prioridad === 1 ? 'Alta' : 
                        tarea.prioridad === 2 ? 'Media' : 'Baja'
  tarea.estadoClass = tarea.estado === 'Completada' ? 'bg-green-100 text-green-800' :
                      tarea.estado === 'En progreso' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
})
</script>