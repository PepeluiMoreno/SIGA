<template>
  <AppLayout :title="campania?.nombre || 'Campaña'" :subtitle="campania ? `${campania.tipoCampania?.nombre || ''} · ${campania.estado?.nombre || ''}` : ''">
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
              <span class="text-sm font-medium text-gray-500">{{ campania?.nombre || '…' }}</span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Carga / error -->
      <div v-if="cargando" class="bg-white rounded-lg shadow border border-gray-200 p-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p class="mt-2 text-gray-600">Cargando campaña...</p>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 class="text-sm font-medium text-red-800">Error al cargar la campaña</h3>
        <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
        <button @click="cargarCampania" class="mt-2 text-sm text-red-600 hover:text-red-500">Intentar de nuevo</button>
      </div>

      <!-- Ficha -->
      <div v-else-if="campania" class="bg-white rounded-lg shadow border border-gray-200">
        <div class="p-6">

          <!-- Información básica -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-gray-900">Información básica</h3>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                {{ campania.nombre || '—' }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Lema</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                {{ campania.lema || '—' }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción corta</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                {{ campania.descripcionCorta || '—' }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción larga</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900 min-h-[96px] whitespace-pre-line">
                {{ campania.descripcionLarga || '—' }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">URL externa</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm">
                <a
                  v-if="campania.urlExterna"
                  :href="campania.urlExterna"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-purple-600 hover:text-purple-800"
                >{{ campania.urlExterna }}</a>
                <span v-else class="text-gray-900">—</span>
              </div>
            </div>
          </div>

          <!-- Clasificación -->
          <div class="space-y-4 pt-6 border-t border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Clasificación</h3>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de campaña</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                {{ campania.tipoCampania?.nombre || '—' }}
              </div>
            </div>
          </div>

          <!-- Fechas + Estado -->
          <div class="pt-6 border-t border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

              <!-- Panel planificación temporal -->
              <div class="space-y-4">
                <h3 class="text-lg font-medium text-gray-900">Fechas</h3>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha inicio planificada</label>
                  <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                    {{ formatearFecha(campania.fechaInicioPlan) || '—' }}
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha fin planificada</label>
                  <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                    {{ formatearFecha(campania.fechaFinPlan) || '—' }}
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha inicio real</label>
                  <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                    {{ formatearFecha(campania.fechaInicioReal) || '—' }}
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha fin real</label>
                  <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                    {{ formatearFecha(campania.fechaFinReal) || '—' }}
                  </div>
                </div>
              </div>

              <!-- Panel estado -->
              <div class="space-y-4">
                <h3 class="text-lg font-medium text-gray-900">Estado</h3>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Estado actual</label>
                  <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm">
                    <span
                      v-if="campania.estado"
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                      :style="badgeStyle(campania.estado.color)"
                    >{{ campania.estado.nombre }}</span>
                    <span v-else class="text-gray-900">—</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- Objetivos -->
          <div class="space-y-4 pt-6 border-t border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Objetivos</h3>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Objetivo principal</label>
              <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900 min-h-[72px] whitespace-pre-line">
                {{ campania.objetivoPrincipal || '—' }}
              </div>
            </div>

          </div>

          <!-- Responsable -->
          <div class="space-y-4 pt-6 border-t border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Responsable</h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Responsable</label>
                <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                  {{ nombreCompletoResponsable || '—' }}
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Agrupación</label>
                <div class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-900">
                  {{ campania.agrupacion?.nombre || '—' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="pt-6 border-t border-gray-200 flex justify-end space-x-3">
            <router-link
              to="/campanias"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Volver
            </router-link>
            <router-link
              :to="`/campanias/${campania.id}/editar`"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700"
            >
              Editar campaña
            </router-link>
          </div>

        </div>
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
import { badgeStyle } from '@/utils/badge'

const route = useRoute()
const cargando = ref(true)
const error = ref(null)
const campania = ref(null)

const nombreCompletoResponsable = computed(() => {
  if (!campania.value?.responsable) return ''
  const { nombre, apellido1, apellido2 } = campania.value.responsable
  return [nombre, apellido1, apellido2].filter(Boolean).join(' ')
})

onMounted(() => cargarCampania())

const cargarCampania = async () => {
  cargando.value = true
  error.value = null
  try {
    const data = await executeQuery(GET_CAMPANIA, { id: route.params.id })
    if (data.campanias?.length > 0) {
      campania.value = data.campanias[0]
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
  if (!fecha) return ''
  return new Date(fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

const formatearMoneda = (cantidad) => {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(cantidad)
}
</script>
