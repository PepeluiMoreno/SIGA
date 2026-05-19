<template>
  <AppLayout title="Seguimiento de Acuerdos" subtitle="Control de ejecución de acuerdos adoptados">

    <!-- Filtros -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <select v-model="filtroEstado" @change="cargar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
        <option value="">Todos los estados</option>
        <option value="PENDIENTE">Pendiente</option>
        <option value="EN_CURSO">En curso</option>
        <option value="COMPLETADO">Completado</option>
        <option value="ARCHIVADO">Archivado</option>
      </select>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando acuerdos…" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700 text-sm">{{ error }}</p>
    </div>

    <div v-else-if="acuerdos.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <ClipboardDocumentCheckIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay acuerdos pendientes</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="a in acuerdos" :key="a.id"
        class="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
        <div class="flex flex-col sm:flex-row sm:items-start gap-4">

          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <span :class="badgeEjecucion(a.estadoEjecucion)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ a.estadoEjecucion.replace('_', ' ') }}
              </span>
              <span class="text-xs text-gray-500">Acuerdo nº {{ a.numero }}</span>
            </div>

            <p class="text-sm text-gray-800 mt-1">{{ a.descripcion }}</p>

            <div v-if="a.fechaLimiteEjecucion" class="mt-2 text-xs flex items-center gap-1"
              :class="vencido(a.fechaLimiteEjecucion) ? 'text-red-600' : 'text-gray-500'">
              <CalendarIcon class="w-3.5 h-3.5" />
              Fecha límite: {{ formatFecha(a.fechaLimiteEjecucion) }}
              <span v-if="vencido(a.fechaLimiteEjecucion)" class="font-medium">(vencido)</span>
            </div>

            <p v-if="a.observacionesEjecucion" class="mt-2 text-xs text-gray-500 italic">
              {{ a.observacionesEjecucion }}
            </p>
          </div>

          <!-- Cambiar estado de ejecución -->
          <div v-if="tienePermiso('SEC_ACUERDO_SEGUIMIENTO')" class="flex-shrink-0">
            <select :value="a.estadoEjecucion"
              @change="actualizarEstado(a, $event.target.value)"
              class="text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-purple-500">
              <option value="PENDIENTE">Pendiente</option>
              <option value="EN_CURSO">En curso</option>
              <option value="COMPLETADO">Completado</option>
              <option value="ARCHIVADO">Archivado</option>
            </select>
          </div>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_ACUERDOS_PENDIENTES, ACTUALIZAR_SEGUIMIENTO } from '@/graphql/queries/secretaria.js'
import { ClipboardDocumentCheckIcon, CalendarIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const loading = ref(false)
const error   = ref('')
const acuerdos = ref([])
const filtroEstado = ref('')

const formatFecha = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const vencido = (s) => s && new Date(s) < new Date()

const badgeEjecucion = (e) => ({
  PENDIENTE:  'bg-yellow-100 text-yellow-700',
  EN_CURSO:   'bg-blue-100 text-blue-700',
  COMPLETADO: 'bg-green-100 text-green-700',
  ARCHIVADO:  'bg-gray-100 text-gray-500',
}[e] ?? 'bg-gray-100 text-gray-500')

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await executeQuery(GET_ACUERDOS_PENDIENTES)
    let items = data?.acuerdosPendientes ?? []
    if (filtroEstado.value) {
      items = items.filter(a => a.estadoEjecucion === filtroEstado.value)
    }
    acuerdos.value = items
  } catch (e) {
    error.value = e.message ?? 'Error al cargar acuerdos'
  } finally {
    loading.value = false
  }
}

const actualizarEstado = async (acuerdo, nuevoEstado) => {
  try {
    await executeMutation(ACTUALIZAR_SEGUIMIENTO, {
      data: { acuerdoId: acuerdo.id, estadoEjecucion: nuevoEstado },
    })
    acuerdo.estadoEjecucion = nuevoEstado
  } catch (e) {
    alert(e.message ?? 'Error al actualizar el acuerdo')
  }
}

onMounted(cargar)
</script>
