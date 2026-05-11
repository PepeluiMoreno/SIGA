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
      <div class="px-6 pt-4">
        <DetailHeader fallback="/campanias" />
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

        <ActividadesTab
          v-else-if="pestañaActiva === 'actividades'"
          :actividades="actividades"
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
import DetailHeader from '@/components/common/DetailHeader.vue'
import { executeQuery } from '@/graphql/client'
import { GET_CAMPANIA } from '@/graphql/queries/campanias'
import { badgeStyle } from '@/utils/badge'

// Importar componentes de pestañas
import InformacionGeneralTab from '@/components/campanias/tabs/InformacionGeneralTab.vue'
import ActividadesTab from '@/components/campanias/tabs/ActividadesTab.vue'
import ResultadosTab from '@/components/campanias/tabs/ResultadosTab.vue'

const route = useRoute()
const cargando = ref(true)
const error = ref(null)
const campania = ref(null)
const pestañaActiva = ref('informacion')

// Datos relacionados
const actividades = ref([])

const titulo = computed(() => '')
const subtitulo = computed(() => '')

const ESTADOS_CIERRE = ['Finalizada', 'Cancelada']

const esCierre = computed(() =>
  campania.value ? ESTADOS_CIERRE.includes(campania.value.estado?.nombre) : false
)

const pestañas = computed(() => {
  const tabs = [
    { id: 'informacion', nombre: 'Información', icono: '📋' },
    { id: 'actividades', nombre: 'Tareas', icono: '📅', contador: actividades.value.length },
  ]
  if (esCierre.value) {
    tabs.push({ id: 'resultados', nombre: 'Resultados', icono: '📊' })
  }
  return tabs
})

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