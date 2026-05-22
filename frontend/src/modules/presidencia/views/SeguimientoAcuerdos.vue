<template>
  <AppLayout title="Seguimiento de Acuerdos" subtitle="Control ejecutivo de acuerdos adoptados en órganos de gobierno">

    <!-- Resumen por estado -->
    <div class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <button
        v-for="e in ESTADOS_EJEC" :key="e.codigo"
        @click="filtroEstado = filtroEstado === e.codigo ? '' : e.codigo"
        :class="[
          'rounded-xl border p-4 text-left transition-all',
          filtroEstado === e.codigo
            ? 'border-purple-400 ring-2 ring-purple-200 shadow-sm'
            : 'border-gray-200 bg-white hover:border-gray-300',
        ]">
        <p class="text-2xl font-bold text-gray-900">{{ contarEstado(e.codigo) }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ e.etiqueta }}</p>
        <div class="mt-2 h-1.5 rounded-full w-full" :class="e.barra"></div>
      </button>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando acuerdos…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="acuerdosFiltrados.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <ClipboardDocumentCheckIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay acuerdos con los filtros seleccionados</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="a in acuerdosFiltrados" :key="a.id"
        class="bg-white rounded-xl border shadow-sm transition-shadow hover:shadow"
        :class="vencido(a.fechaLimiteEjecucion) && a.estadoEjecucionCodigo !== 'COMPLETADO' ? 'border-red-200' : 'border-gray-200'">
        <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">

          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span :class="badgeEjecucion(a.estadoEjecucionCodigo)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ etiquetaEjecucion(a.estadoEjecucionCodigo) }}
              </span>
              <span class="text-xs text-gray-400">Acuerdo nº {{ a.numero }}</span>
              <span v-if="vencido(a.fechaLimiteEjecucion) && !['COMPLETADO','ARCHIVADO'].includes(a.estadoEjecucionCodigo)"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                ⚠ Plazo vencido
              </span>
            </div>

            <p class="text-sm text-gray-800 leading-relaxed">{{ a.descripcion }}</p>

            <div class="flex flex-wrap gap-4 mt-2 text-xs text-gray-500">
              <span v-if="a.fechaLimiteEjecucion" class="flex items-center gap-1">
                <CalendarIcon class="w-3.5 h-3.5" />
                <span :class="vencido(a.fechaLimiteEjecucion) ? 'text-red-600 font-semibold' : ''">
                  {{ formatFecha(a.fechaLimiteEjecucion) }}
                </span>
              </span>
            </div>

            <p v-if="a.observacionesEjecucion" class="mt-2 text-xs text-gray-400 italic border-l-2 border-gray-200 pl-2">
              {{ a.observacionesEjecucion }}
            </p>
          </div>

          <!-- Cambio de estado directo -->
          <div class="flex-shrink-0">
            <select :value="a.estadoEjecucionCodigo"
              @change="actualizarEstado(a, $event.target.value)"
              class="text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white">
              <option value="PENDIENTE">Pendiente</option>
              <option value="EN_CURSO">En curso</option>
              <option value="COMPLETADO">Completado</option>
              <option value="ARCHIVADO">Archivado</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast de error -->
    <Teleport to="body">
      <div v-if="errorAccion"
        class="fixed bottom-4 right-4 z-50 bg-red-600 text-white text-sm px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 max-w-sm">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0" />
        <span>{{ errorAccion }}</span>
        <button @click="errorAccion = ''" class="ml-auto text-white/80 hover:text-white">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_ACUERDOS_PENDIENTES_PRES } from '@/graphql/queries/presidencia.js'
import { ACTUALIZAR_SEGUIMIENTO } from '@/graphql/queries/secretaria.js'
import { ClipboardDocumentCheckIcon, CalendarIcon, ExclamationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const loading     = ref(false)
const error       = ref('')
const errorAccion = ref('')
const acuerdos    = ref([])
const filtroEstado = ref('')

const ESTADOS_EJEC = [
  { codigo: 'PENDIENTE',  etiqueta: 'Pendiente',  clase: 'bg-yellow-100 text-yellow-700', barra: 'bg-yellow-300' },
  { codigo: 'EN_CURSO',   etiqueta: 'En curso',   clase: 'bg-blue-100 text-blue-700',    barra: 'bg-blue-300' },
  { codigo: 'COMPLETADO', etiqueta: 'Completado', clase: 'bg-green-100 text-green-700',  barra: 'bg-green-400' },
  { codigo: 'ARCHIVADO',  etiqueta: 'Archivado',  clase: 'bg-gray-100 text-gray-500',    barra: 'bg-gray-300' },
]

const formatFecha    = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const vencido        = (s) => s && new Date(s) < new Date()
const badgeEjecucion  = (c) => ESTADOS_EJEC.find(e => e.codigo === c)?.clase ?? 'bg-gray-100 text-gray-500'
const etiquetaEjecucion = (c) => ESTADOS_EJEC.find(e => e.codigo === c)?.etiqueta ?? c
const contarEstado   = (c) => acuerdos.value.filter(a => a.estadoEjecucionCodigo === c).length

const acuerdosFiltrados = computed(() =>
  filtroEstado.value
    ? acuerdos.value.filter(a => a.estadoEjecucionCodigo === filtroEstado.value)
    : acuerdos.value
)

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const data = await executeQuery(GET_ACUERDOS_PENDIENTES_PRES)
    acuerdos.value = data?.acuerdosPendientes ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar acuerdos'
  } finally {
    loading.value = false
  }
}

const actualizarEstado = async (acuerdo, nuevoEstado) => {
  const anterior = acuerdo.estadoEjecucionCodigo
  acuerdo.estadoEjecucionCodigo = nuevoEstado
  try {
    await executeMutation(ACTUALIZAR_SEGUIMIENTO, {
      data: { acuerdoId: acuerdo.id, estadoEjecucion: nuevoEstado },
    })
  } catch (e) {
    acuerdo.estadoEjecucionCodigo = anterior
    errorAccion.value = e.message ?? 'Error al actualizar el acuerdo'
    setTimeout(() => errorAccion.value = '', 4000)
  }
}

onMounted(cargar)
</script>
