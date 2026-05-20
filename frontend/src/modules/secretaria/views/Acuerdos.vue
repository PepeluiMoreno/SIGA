<template>
  <AppLayout title="Seguimiento de Acuerdos" subtitle="Control de ejecución de acuerdos adoptados">

    <div class="flex gap-2 mb-6">
      <select v-model="filtroEstado" @change="filtrar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
        <option value="">Todos los estados</option>
        <option value="PENDIENTE">Pendiente</option>
        <option value="EN_CURSO">En curso</option>
        <option value="COMPLETADO">Completado</option>
        <option value="ARCHIVADO">Archivado</option>
      </select>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando acuerdos…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="acuerdosFiltrados.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <ClipboardDocumentCheckIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay acuerdos pendientes</p>
      <p class="text-sm mt-1">Los acuerdos aparecen aquí cuando se adoptan en reuniones.</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="a in acuerdosFiltrados" :key="a.id"
        class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">

          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span :class="badgeEjecucion(a.estadoEjecucionCodigo)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ etiquetaEjecucion(a.estadoEjecucionCodigo) }}
              </span>
              <span class="text-xs text-gray-400">Acuerdo nº {{ a.numero }}</span>
              <span v-if="vencido(a.fechaLimiteEjecucion)"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                <ExclamationCircleIcon class="w-3 h-3" /> Plazo vencido
              </span>
            </div>

            <p class="text-sm text-gray-800 leading-relaxed">{{ a.descripcion }}</p>

            <div v-if="a.fechaLimiteEjecucion" class="mt-2 flex items-center gap-1 text-xs text-gray-500">
              <CalendarIcon class="w-3.5 h-3.5" />
              Fecha límite: <span :class="vencido(a.fechaLimiteEjecucion) ? 'text-red-600 font-medium' : ''">
                {{ formatFecha(a.fechaLimiteEjecucion) }}
              </span>
            </div>

            <p v-if="a.observacionesEjecucion" class="mt-2 text-xs text-gray-400 italic">
              {{ a.observacionesEjecucion }}
            </p>
          </div>

          <div v-if="tienePermiso('SEC_ACUERDO_SEGUIMIENTO')" class="flex-shrink-0">
            <select :value="a.estadoEjecucionCodigo" @change="actualizarEstado(a, $event.target.value)"
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

    <Teleport to="body">
      <div v-if="errorAccion"
        class="fixed bottom-4 right-4 z-50 bg-red-600 text-white text-sm px-4 py-3 rounded-lg shadow-lg max-w-sm">
        {{ errorAccion }}
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_ACUERDOS_PENDIENTES, ACTUALIZAR_SEGUIMIENTO, GET_MIEMBROS_LIGERO } from '@/graphql/queries/secretaria.js'
import { ClipboardDocumentCheckIcon, CalendarIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import SelectorMiembro from '@/components/common/SelectorMiembro.vue'

const { tienePermiso } = usePermisos()
const loading  = ref(false)
const error    = ref('')
const acuerdos = ref([])
const filtroEstado = ref('')
const miembros = ref([])
const errorAccion = ref('')

const ESTADOS_EJECUCION = [
  { valor: 'PENDIENTE',  etiqueta: 'Pendiente',  clase: 'bg-yellow-100 text-yellow-700' },
  { valor: 'EN_CURSO',   etiqueta: 'En curso',   clase: 'bg-blue-100 text-blue-700' },
  { valor: 'COMPLETADO', etiqueta: 'Completado', clase: 'bg-green-100 text-green-700' },
  { valor: 'ARCHIVADO',  etiqueta: 'Archivado',  clase: 'bg-gray-100 text-gray-500' },
]

const acuerdosFiltrados = computed(() =>
  filtroEstado.value
    ? acuerdos.value.filter(a => a.estadoEjecucionCodigo === filtroEstado.value)
    : acuerdos.value
)

const formatFecha     = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const vencido         = (s) => s && new Date(s) < new Date() 
const badgeEjecucion  = (e) => ESTADOS_EJECUCION.find(x => x.valor === e)?.clase ?? 'bg-gray-100 text-gray-500'
const etiquetaEjecucion = (e) => ESTADOS_EJECUCION.find(x => x.valor === e)?.etiqueta ?? e

const filtrar = () => {} // el computed ya filtra reactivamente

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const data = await executeQuery(GET_ACUERDOS_PENDIENTES)
    acuerdos.value = data?.acuerdosPendientes ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar acuerdos'
  } finally {
    loading.value = false
  }
}

const actualizarEstado = async (acuerdo, nuevoEstado) => {
  const estadoAnterior = acuerdo.estadoEjecucion
  acuerdo.estadoEjecucionCodigo = nuevoEstado // optimistic update
  try {
    await executeMutation(ACTUALIZAR_SEGUIMIENTO, {
      data: { acuerdoId: acuerdo.id, estadoEjecucion: nuevoEstado },
    })
  } catch (e) {
    acuerdo.estadoEjecucionCodigo = estadoAnterior // revertir
    errorAccion.value = e.message ?? 'Error al actualizar el acuerdo'
    setTimeout(() => errorAccion.value = '', 4000)
  }
}

const cargarMiembros = async () => {
  try {
    const data = await executeQuery(GET_MIEMBROS_LIGERO)
    miembros.value = data?.miembros ?? []
  } catch (e) { console.error(e) }
}

onMounted(() => Promise.all([cargar(), cargarMiembros()]))
</script>
