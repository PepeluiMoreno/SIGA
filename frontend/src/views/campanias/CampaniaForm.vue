<template>
  <AppLayout :title="isEdit ? 'Editar Campaña' : 'Nueva Campaña'" :subtitle="isEdit ? `Editando: ${campania.nombre}` : 'Crear nueva campaña'">
    <div class="max-w-4xl mx-auto">
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

      <!-- Formulario -->
      <div class="bg-white rounded-lg shadow border border-gray-200">
        <div class="p-6">
          <div v-if="loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <p class="mt-2 text-gray-600">Cargando...</p>
          </div>

          <form v-else @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Información básica -->
            <div class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">Información básica</h3>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  v-model="campania.nombre"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Nombre de la campaña"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Descripción corta
                </label>
                <input
                  v-model="campania.descripcion_corta"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Breve descripción"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Descripción larga
                </label>
                <textarea
                  v-model="campania.descripcion_larga"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Descripción detallada de la campaña..."
                />
              </div>
            </div>

            <!-- Clasificación -->
            <div class="space-y-4 pt-6 border-t border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Clasificación</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de campaña *
                  </label>
                  <select
                    v-model="campania.tipo_campania_id"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar tipo</option>
                    <option v-for="tipo in tiposCampania" :key="tipo.id" :value="tipo.id">
                      {{ tipo.nombre }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Estado *
                  </label>
                  <select
                    v-model="campania.estado_campania_id"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar estado</option>
                    <option v-for="estado in estadosCampania" :key="estado.id" :value="estado.id">
                      {{ estado.nombre }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Fechas -->
            <div class="space-y-4 pt-6 border-t border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Fechas</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Fecha inicio planificada
                  </label>
                  <input
                    v-model="campania.fecha_inicio_plan"
                    type="date"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Fecha fin planificada
                  </label>
                  <input
                    v-model="campania.fecha_fin_plan"
                    type="date"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <!-- Objetivos -->
            <div class="space-y-4 pt-6 border-t border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Objetivos</h3>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Objetivo principal
                </label>
                <textarea
                  v-model="campania.objetivo_principal"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Objetivo principal de la campaña..."
                />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Meta de recaudación (€)
                  </label>
                  <input
                    v-model="campania.meta_recaudacion"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Meta de participantes
                  </label>
                  <input
                    v-model="campania.meta_participantes"
                    type="number"
                    min="0"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <!-- Responsable -->
            <div class="space-y-4 pt-6 border-t border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Responsable</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Responsable
                  </label>
                  <select
                    v-model="campania.responsable_id"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar responsable</option>
                    <option v-for="miembro in miembros" :key="miembro.id" :value="miembro.id">
                      {{ miembro.nombre }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Agrupación
                  </label>
                  <select
                    v-model="campania.agrupacion_id"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar agrupación</option>
                    <option v-for="agrupacion in agrupaciones" :key="agrupacion.id" :value="agrupacion.id">
                      {{ agrupacion.nombre }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Error -->
            <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {{ error }}
            </div>

            <!-- Botones -->
            <div class="pt-6 border-t border-gray-200 flex justify-end space-x-3">
              <router-link
                to="/campanias"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </router-link>
              <button
                type="submit"
                :disabled="submitting"
                class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span v-if="submitting" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                <span>{{ isEdit ? 'Actualizar' : 'Crear' }} campaña</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'
import {
  GET_CAMPANIA,
  GET_TIPOS_CAMPANIA,
  GET_ESTADOS_CAMPANIA,
  CREAR_CAMPANIA,
  ACTUALIZAR_CAMPANIA,
} from '@/graphql/queries/campanias.js'
import { GET_MIEMBROS, GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.params.id && !route.path.includes('/nueva'))
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)

const campania = ref({
  nombre: '',
  lema: '',
  descripcion_corta: '',
  descripcion_larga: '',
  url_externa: '',
  tipo_campania_id: '',
  estado_campania_id: '',
  fecha_inicio_plan: '',
  fecha_fin_plan: '',
  fecha_inicio_real: '',
  fecha_fin_real: '',
  objetivo_principal: '',
  meta_recaudacion: null,
  meta_participantes: null,
  meta_firmas: null,
  responsable_id: '',
  agrupacion_id: '',
})

const tiposCampania = ref([])
const estadosCampania = ref([])
const miembros = ref([])
const agrupaciones = ref([])

onMounted(async () => {
  await loadData()
  if (isEdit.value) {
    await loadCampania()
  }
})

const loadCampania = async () => {
  loading.value = true
  try {
    const data = await executeQuery(GET_CAMPANIA, { id: route.params.id })
    const c = data.campanias?.[0]
    if (c) {
      campania.value = {
        nombre: c.nombre || '',
        lema: c.lema || '',
        descripcion_corta: c.descripcionCorta || '',
        descripcion_larga: c.descripcionLarga || '',
        url_externa: c.urlExterna || '',
        tipo_campania_id: c.tipoCampania?.id || '',
        estado_campania_id: c.estado?.id || '',
        fecha_inicio_plan: c.fechaInicioPlan || '',
        fecha_fin_plan: c.fechaFinPlan || '',
        fecha_inicio_real: c.fechaInicioReal || '',
        fecha_fin_real: c.fechaFinReal || '',
        objetivo_principal: c.objetivoPrincipal || '',
        meta_recaudacion: c.metaRecaudacion || null,
        meta_participantes: c.metaParticipantes || null,
        meta_firmas: c.metaFirmas || null,
        responsable_id: c.responsable?.id || '',
        agrupacion_id: c.agrupacion?.id || '',
      }
    }
  } catch (err) {
    console.error('Error cargando campaña:', err)
    error.value = 'Error al cargar la campaña'
  } finally {
    loading.value = false
  }
}

const loadData = async () => {
  try {
    const [tiposData, estadosData, miembrosData, agrupacionesData] = await Promise.all([
      executeQuery(GET_TIPOS_CAMPANIA),
      executeQuery(GET_ESTADOS_CAMPANIA),
      executeQuery(GET_MIEMBROS),
      executeQuery(GET_AGRUPACIONES),
    ])
    tiposCampania.value = tiposData.tiposCampania || []
    estadosCampania.value = estadosData.estadosCampania || []
    miembros.value = (miembrosData.miembros || []).map(m => ({
      id: m.id,
      nombre: [m.nombre, m.apellido1, m.apellido2].filter(Boolean).join(' '),
    }))
    agrupaciones.value = agrupacionesData.agrupacionesTerritoriales || []
  } catch (err) {
    console.error('Error cargando catálogos:', err)
  }
}

const handleSubmit = async () => {
  submitting.value = true
  error.value = null
  try {
    const payload = {
      nombre: campania.value.nombre,
      lema: campania.value.lema || null,
      descripcionCorta: campania.value.descripcion_corta || null,
      descripcionLarga: campania.value.descripcion_larga || null,
      urlExterna: campania.value.url_externa || null,
      tipoCampaniaId: campania.value.tipo_campania_id,
      estadoId: campania.value.estado_campania_id,
      fechaInicioPlan: campania.value.fecha_inicio_plan || null,
      fechaFinPlan: campania.value.fecha_fin_plan || null,
      fechaInicioReal: campania.value.fecha_inicio_real || null,
      fechaFinReal: campania.value.fecha_fin_real || null,
      objetivoPrincipal: campania.value.objetivo_principal || null,
      metaRecaudacion: campania.value.meta_recaudacion || null,
      metaParticipantes: campania.value.meta_participantes || null,
      metaFirmas: campania.value.meta_firmas || null,
      responsableId: campania.value.responsable_id || null,
      agrupacionId: campania.value.agrupacion_id || null,
    }

    if (isEdit.value) {
      await executeMutation(ACTUALIZAR_CAMPANIA, { data: { id: route.params.id, ...payload } })
      router.push(`/campanias/${route.params.id}`)
    } else {
      const result = await executeMutation(CREAR_CAMPANIA, { data: payload })
      router.push(`/campanias/${result.crearCampania.id}`)
    }
  } catch (err) {
    console.error('Error guardando campaña:', err)
    error.value = 'Error al guardar la campaña. Por favor, inténtalo de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>