<template>
  <AppLayout :title="isEdit ? 'Editar Campaña' : 'Nueva Campaña'" :subtitle="isEdit ? `Editando: ${campania.nombre}` : 'Crear nueva campaña'">
    <div class="max-w-7xl mx-auto">
      <!-- Breadcrumb -->
      <nav class="flex mb-6" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li class="inline-flex items-center">
            <router-link to="/campanias" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-purple-600">
              <span>🚩</span>
              <span class="ml-2">Campañas</span>
            </router-link>
          </li>
          <li>
            <div class="flex items-center">
              <span class="text-gray-400 mx-2">›</span>
              <span class="text-sm font-medium text-gray-500">
                {{ isEdit ? 'Editar' : 'Nueva' }}
              </span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Form Container -->
      <div class="bg-white rounded-lg shadow border border-gray-200">
        <!-- TABS HEADER -->
        <div class="border-b border-gray-200">
          <nav class="flex space-x-8 px-6" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center'
              ]"
            >
              <span class="mr-2">{{ tab.icon }}</span>
              {{ tab.name }}
              <span v-if="tab.count" class="ml-2 bg-gray-100 text-gray-900 text-xs font-medium px-2 py-0.5 rounded-full">
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Form Content -->
        <form @submit.prevent="handleSubmit">
          <div class="p-6">
            <!-- Loading -->
            <div v-if="loading" class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <p class="mt-2 text-gray-600">Cargando...</p>
            </div>

            <!-- CONTENIDO DE LAS PESTAÑAS -->
            <div v-else>
              <!-- Información Básica -->
              <BasicInfoTab 
                v-if="activeTab === 'basic'"
                v-model:campania="campania"
                :tiposCampania="tiposCampania"
              />

              <!-- Objetivos -->
              <ObjectivesTab 
                v-else-if="activeTab === 'objectives'"
                v-model:objetivos="objetivos"
                v-model:campania="campania"
                @open-objective-modal="openObjectiveModal"
              />

              <!-- Actividades -->
              <ActivitiesTab 
                v-else-if="activeTab === 'activities'"
                v-model:actividades="actividades"
                v-model:campania="campania"
                @open-activity-modal="openActivityModal"
              />

              <!-- Recursos -->
              <ResourcesTab 
                v-else-if="activeTab === 'resources'"
                v-model:recursosHumanos="recursosHumanos"
                v-model:recursosMateriales="recursosMateriales"
                v-model:campania="campania"
                @open-resource-modal="openResourceModal"
              />

              <!-- Resultados -->
              <ResultsTab 
                v-else-if="activeTab === 'results'"
                v-model:campania="campania"
              />
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="px-6 py-4 border-t border-gray-200 flex justify-between">
            <button
              v-if="activeTab !== 'basic'"
              type="button"
              @click="goToPreviousTab"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <span class="mr-2">←</span>
              Anterior
            </button>
            <div v-else></div>

            <div class="flex space-x-3">
              <button
                v-if="activeTab !== 'results'"
                type="button"
                @click="goToNextTab"
                class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 flex items-center"
              >
                Siguiente
                <span class="ml-2">→</span>
              </button>
              
              <button
                v-if="activeTab === 'results'"
                type="submit"
                :disabled="submitting"
                class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span v-if="submitting" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                <span>{{ isEdit ? 'Actualizar' : 'Crear' }} campaña</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Modales -->
    <ObjectiveModal 
      v-if="showObjectiveModal"
      :objective="editingObjective"
      :editingIndex="editingObjectiveIndex"
      @save="saveObjective"
      @close="closeObjectiveModal"
    />

    <ActivityModal 
      v-if="showActivityModal"
      :activity="editingActivity"
      :editingIndex="editingActivityIndex"
      @save="saveActivity"
      @close="closeActivityModal"
    />

    <ResourceModal 
      v-if="showResourceModal"
      :type="resourceModalType"
      :resource="editingResource"
      :editingIndex="editingResourceIndex"
      @save="saveResource"
      @close="closeResourceModal"
    />
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../../layouts/AppLayout.vue'

// ¡IMPORTAR LOS COMPONENTES HIJOS!
// Ajusta estas rutas según donde tengas tus componentes
import BasicInfoTab from './form/BasicInfoTab.vue'
import ObjectivesTab from './form/ObjectivesTab.vue'
import ActivitiesTab from './form/ActivitiesTab.vue'
import ResourcesTab from './form/ResourcesTab.vue'
import ResultsTab from './form/ResultsTab.vue'
import ObjectiveModal from './form/modals/ObjectiveModal.vue'
import ActivityModal from './form/modals/ActivityModal.vue'
import ResourceModal from './form/modals/ResourceModal.vue'
const toast = useToast()

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.params.id && !route.path.includes('/nueva'))
const loading = ref(false)
const submitting = ref(false)
const activeTab = ref('basic')

// Datos principales
const campania = ref({
  id: null,
  codigo: '',
  nombre: '',
  descripcion_corta: '',
  descripcion_larga: '',
  tipo_campania_id: '',
  estado_campania_id: '',
  fecha_inicio_plan: '',
  fecha_fin_plan: '',
  objetivo_principal: '',
  meta_recaudacion: null,
  meta_participantes: null,
  responsable_id: null,
  agrupacion_id: null,
  presupuesto_total: null,
  presupuesto_ejecutado: null,
  participantes_reales: null,
  recaudacion_real: null,
  alcance: null,
  resultados_cualitativos: '',
  lecciones_aprendidas: '',
  nivel_exito: 5,
  recomendaciones: '',
  logistica: ''
})

// Arrays para CRUDs
const objetivos = ref([])
const actividades = ref([])
const recursosHumanos = ref([])
const recursosMateriales = ref([])

// Estado de modales
const showObjectiveModal = ref(false)
const editingObjectiveIndex = ref(null)
const editingObjective = ref(null)

const showActivityModal = ref(false)
const editingActivityIndex = ref(null)
const editingActivity = ref(null)

const showResourceModal = ref(false)
const resourceModalType = ref('human')
const editingResourceIndex = ref(null)
const editingResource = ref(null)

// Configuración de tabs (con computed para contar)
const tabs = computed(() => [
  { id: 'basic', name: 'Información Básica', icon: '📋' },
  { 
    id: 'objectives', 
    name: 'Objetivos', 
    icon: '🎯', 
    count: objetivos.value.length 
  },
  { 
    id: 'activities', 
    name: 'Actividades', 
    icon: '📅', 
    count: actividades.value.length 
  },
  { id: 'resources', name: 'Recursos', icon: '💰' },
  { id: 'results', name: 'Resultados', icon: '📊' }
])

// Datos para selects
const tiposCampania = ref([])

onMounted(() => {
  if (isEdit.value) {
    loadCampania()
  } else {
    // Inicializar nueva campaña
    campania.value.estado_campania_id = '1'
    campania.value.fecha_inicio_plan = new Date().toISOString().split('T')[0]
    campania.value.nivel_exito = 5
  }
  loadData()
})

const loadCampania = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    if (route.params.id === '1') {
      campania.value = {
        id: 1,
        codigo: 'CAMP-2025-001',
        nombre: 'Campaña Día del Laicismo 2025',
        descripcion_corta: 'Actividades para celebrar el Día Internacional del Laicismo',
        descripcion_larga: 'Esta es una campaña completa para celebrar el Día Internacional del Laicismo...',
        tipo_campania_id: '1',
        estado_campania_id: '2',
        fecha_inicio_plan: '2025-01-15',
        fecha_fin_plan: '2025-02-15',
        objetivo_principal: 'Promover valores laicos en la sociedad',
        meta_recaudacion: 5000,
        meta_participantes: 50
      }
      
      objetivos.value = [
        {
          id: 1,
          titulo: 'Recaudar 5000€',
          descripcion: 'Alcanzar la meta de recaudación para financiar las actividades',
          tipo: 'cuantitativo',
          prioridad: 'alta',
          meta: '5000€',
          progreso: 47,
          fecha_limite: '2025-02-15'
        }
      ]
      
      actividades.value = [
        {
          id: 1,
          nombre: 'Recogida de firmas en Plaza Mayor',
          fecha: '2025-01-20',
          hora_inicio: '10:00',
          hora_fin: '14:00',
          lugar: 'Plaza Mayor',
          descripcion: 'Recogida de firmas para la iniciativa de laicismo',
          voluntarios_necesarios: 5,
          voluntarios_confirmados: 3,
          completada: true
        }
      ]
    }
  } catch (error) {
    console.error('Error cargando campaña:', error)
  } finally {
    loading.value = false
  }
}

const loadData = () => {
  tiposCampania.value = [
    { id: '1', nombre: 'Eventos' },
    { id: '2', nombre: 'Formación' },
    { id: '3', nombre: 'Denuncia' },
    { id: '4', nombre: 'Recaudación' }
  ]
}

// Navegación entre tabs
const goToPreviousTab = () => {
  const currentIndex = tabs.value.findIndex(tab => tab.id === activeTab.value)
  if (currentIndex > 0) {
    activeTab.value = tabs.value[currentIndex - 1].id
  }
}

const goToNextTab = () => {
  const currentIndex = tabs.value.findIndex(tab => tab.id === activeTab.value)
  if (currentIndex < tabs.value.length - 1) {
    activeTab.value = tabs.value[currentIndex + 1].id
  }
}

// Handlers de modales
const openObjectiveModal = (index = null) => {
  if (index !== null) {
    editingObjectiveIndex.value = index
    editingObjective.value = { ...objetivos.value[index] }
  } else {
    editingObjectiveIndex.value = null
    editingObjective.value = {
      titulo: '',
      descripcion: '',
      tipo: 'cuantitativo',
      prioridad: 'media',
      meta: '',
      progreso: 0,
      fecha_limite: ''
    }
  }
  showObjectiveModal.value = true
}

const saveObjective = (objective) => {
  if (editingObjectiveIndex.value !== null) {
    objetivos.value[editingObjectiveIndex.value] = objective
  } else {
    objetivos.value.push({
      id: objetivos.value.length + 1,
      ...objective
    })
  }
  closeObjectiveModal()
}

const closeObjectiveModal = () => {
  showObjectiveModal.value = false
  editingObjectiveIndex.value = null
  editingObjective.value = null
}

const openActivityModal = (index = null) => {
  if (index !== null) {
    editingActivityIndex.value = index
    editingActivity.value = { ...actividades.value[index] }
  } else {
    editingActivityIndex.value = null
    editingActivity.value = {
      nombre: '',
      fecha: '',
      hora_inicio: '',
      hora_fin: '',
      lugar: '',
      descripcion: '',
      voluntarios_necesarios: 0,
      voluntarios_confirmados: 0,
      completada: false
    }
  }
  showActivityModal.value = true
}

const saveActivity = (activity) => {
  if (editingActivityIndex.value !== null) {
    actividades.value[editingActivityIndex.value] = activity
  } else {
    actividades.value.push({
      id: actividades.value.length + 1,
      ...activity
    })
  }
  closeActivityModal()
}

const closeActivityModal = () => {
  showActivityModal.value = false
  editingActivityIndex.value = null
  editingActivity.value = null
}

const openResourceModal = (type, index = null) => {
  resourceModalType.value = type
  
  if (index !== null) {
    editingResourceIndex.value = index
    if (type === 'human') {
      editingResource.value = { ...recursosHumanos.value[index] }
    } else {
      editingResource.value = { ...recursosMateriales.value[index] }
    }
  } else {
    editingResourceIndex.value = null
    editingResource.value = type === 'human' 
      ? { rol: '', personas: 1, descripcion: '' }
      : { nombre: '', cantidad: 1, unidad: 'unidad', costo: null, descripcion: '' }
  }
  showResourceModal.value = true
}

const saveResource = (resource) => {
  if (editingResourceIndex.value !== null) {
    if (resourceModalType.value === 'human') {
      recursosHumanos.value[editingResourceIndex.value] = resource
    } else {
      recursosMateriales.value[editingResourceIndex.value] = resource
    }
  } else {
    if (resourceModalType.value === 'human') {
      recursosHumanos.value.push({
        id: recursosHumanos.value.length + 1,
        ...resource
      })
    } else {
      recursosMateriales.value.push({
        id: recursosMateriales.value.length + 1,
        ...resource
      })
    }
  }
  closeResourceModal()
}

const closeResourceModal = () => {
  showResourceModal.value = false
  editingResourceIndex.value = null
  editingResource.value = null
}

// Envío del formulario
const handleSubmit = async () => {
  submitting.value = true
  try {
    // Validación básica
    if (!campania.value.codigo || !campania.value.nombre || !campania.value.tipo_campania_id || !campania.value.estado_campania_id) {
      toast.error('Por favor, completa los campos obligatorios en la pestaña de Información Básica')
      activeTab.value = 'basic'
      return
    }
    
    console.log('Enviando datos:', {
      campania: campania.value,
      objetivos: objetivos.value,
      actividades: actividades.value,
      recursosHumanos: recursosHumanos.value,
      recursosMateriales: recursosMateriales.value
    })
    
    // Simular envío a API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Redirigir
    if (isEdit.value) {
      router.push(`/campanias/${campania.value.id}`)
    } else {
      router.push('/campanias')
    }
    
  } catch (error) {
    console.error('Error guardando campaña:', error)
    toast.error('Error al guardar la campaña. Por favor, inténtalo de nuevo.')
  } finally {
    submitting.value = false
  }
}
</script>