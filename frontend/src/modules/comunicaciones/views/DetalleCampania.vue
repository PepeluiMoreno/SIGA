<template>
  <AppLayout :title="titulo" :subtitle="subtitulo">
    <!-- Estados de carga/error -->
    <div v-if="cargando">
      <div class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p class="mt-2 text-gray-600">Cargando detalles de la campaña...</p>
      </div>
    </div>

    <div v-else-if="error">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <span class="text-red-400">⚠️</span>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error al cargar la campaña</h3>
            <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
            <button @click="cargarCampania" class="mt-2 text-sm text-red-600 hover:text-red-500">
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div v-else-if="campania" class="bg-white rounded-lg shadow">
      <!-- Encabezado -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center space-x-3">
              <h2 class="text-2xl font-bold text-gray-900">{{ campania.nombre }}</h2>
              <span :class="claseEstado" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                {{ campania.estado?.nombre || 'Sin estado' }}
              </span>
            </div>
            <div class="mt-2 flex items-center space-x-4 text-sm text-gray-600">
              <span v-if="campania.lema" class="text-gray-700">Lema: "{{ campania.lema }}"</span>
              <span v-if="campania.tipoCampania" class="text-purple-600 bg-purple-100 px-2 py-0.5 rounded">
                {{ campania.tipoCampania.nombre }}
              </span>
              <span v-if="campania.fechaInicioPlan || campania.fechaFinPlan">
                📅 {{ formatearFecha(campania.fechaInicioPlan) }} - {{ formatearFecha(campania.fechaFinPlan) }}
              </span>
            </div>
            <p v-if="campania.descripcionCorta" class="mt-2 text-gray-700">
              {{ campania.descripcionCorta }}
            </p>
            <a
              v-if="campania.urlExterna"
              :href="campania.urlExterna"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-2 inline-flex items-center text-sm text-purple-600 hover:text-purple-800"
            >
              🔗 Ver en laicismo.org
            </a>
          </div>

          <div class="flex space-x-3">
            <router-link
              to="/campanias"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Volver
            </router-link>
          </div>
        </div>
      </div>

      <!-- Pestañas -->
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6" aria-label="Tabs">
          <button
            v-for="pestania in pestañas"
            :key="pestania.id"
            @click="pestañaActiva = pestania.id"
            :class="[
              pestañaActiva === pestania.id
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center'
            ]"
          >
            <span class="mr-2">{{ pestania.icono }}</span>
            {{ pestania.nombre }}
            <span v-if="pestania.contador" class="ml-2 bg-gray-100 text-gray-900 text-xs font-medium px-2 py-0.5 rounded-full">
              {{ pestania.contador }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Contenido de pestañas -->
      <div class="p-6">
        <InformacionGeneralTab 
          v-if="pestañaActiva === 'informacion'" 
          :campania="campania" 
        />
        
        <ObjetivosTab 
          v-else-if="pestañaActiva === 'objetivos'" 
          :objetivos="objetivos" 
        />
        
        <ActividadesTab 
          v-else-if="pestañaActiva === 'actividades'" 
          :actividades="actividades" 
        />
        
        <RecursosTab 
          v-else-if="pestañaActiva === 'recursos'" 
          :campania="campania"
          :recursos-humanos="recursosHumanos"
          :recursos-materiales="recursosMateriales"
        />
        
        <ResultadosTab 
          v-else-if="pestañaActiva === 'resultados'" 
          :campania="campania" 
        />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_CAMPANIA } from '@/graphql/queries/campanias'

// Importar componentes de pestañas
import InformacionGeneralTab from '@/components/campanias/tabs/InformacionGeneralTab.vue'
import ObjetivosTab from '@/components/campanias/tabs/ObjetivosTab.vue'
import ActividadesTab from '@/components/campanias/tabs/ActividadesTab.vue'
import RecursosTab from '@/components/campanias/tabs/RecursosTab.vue'
import ResultadosTab from '@/components/campanias/tabs/ResultadosTab.vue'

const route = useRoute()
const cargando = ref(true)
const error = ref(null)
const campania = ref(null)
const pestañaActiva = ref('informacion')

// Datos relacionados
const objetivos = ref([])
const actividades = ref([])
const recursosHumanos = ref([])
const recursosMateriales = ref([])

const titulo = computed(() => '')
const subtitulo = computed(() => '')

const pestañas = computed(() => [
  { 
    id: 'informacion', 
    nombre: 'Información', 
    icono: '📋' 
  },
  { 
    id: 'objetivos', 
    nombre: 'Objetivos', 
    icono: '🎯', 
    contador: objetivos.value.length 
  },
  { 
    id: 'actividades', 
    nombre: 'Actividades', 
    icono: '📅', 
    contador: actividades.value.length 
  },
  { 
    id: 'recursos', 
    nombre: 'Recursos', 
    icono: '💰' 
  },
  { 
    id: 'resultados', 
    nombre: 'Resultados', 
    icono: '📊' 
  }
])

onMounted(() => {
  cargarCampania()
})

const cargarCampania = async () => {
  cargando.value = true
  error.value = null

  try {
    const campaniaId = route.params.id
    const data = await executeQuery(GET_CAMPANIA, { id: campaniaId })

    if (data.campanias && data.campanias.length > 0) {
      campania.value = data.campanias[0]
      actividades.value = campania.value.actividades || []
    } else {
      throw new Error('Campaña no encontrada')
    }
  } catch (err) {
    error.value = err
    console.error('Error cargando campaña:', err)
  } finally {
    cargando.value = false
  }
}

const claseEstado = computed(() => {
  const codigo = campania.value?.estado?.codigo
  if (codigo === 'ACTIVA') return 'bg-green-100 text-green-800'
  if (codigo === 'PLANIFICADA') return 'bg-blue-100 text-blue-800'
  if (codigo === 'FINALIZADA') return 'bg-gray-100 text-gray-800'
  if (codigo === 'CANCELADA') return 'bg-red-100 text-red-800'
  if (codigo === 'SUSPENDIDA') return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-800'
})

const formatearFecha = (fecha) => {
  if (!fecha) return 'No especificada'
  try {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  } catch {
    return fecha
  }
}
</script>