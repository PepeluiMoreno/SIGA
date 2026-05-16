<template>
  <AppLayout title="Memoria Anual" subtitle="Resumen de campañas y actividades del ejercicio">

    <!-- Cabecera: selector de año + exportar -->
    <div class="flex items-center justify-between mb-6 print:hidden">
      <div class="flex items-center gap-2">
        <button @click="anio--" class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600">
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
        <span class="text-2xl font-bold text-slate-800 w-20 text-center">{{ anio }}</span>
        <button @click="anio++" :disabled="anio >= anioActual" class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 disabled:opacity-40">
          <ChevronRightIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="flex items-center gap-3">
        <button @click="recargar" class="h-9 px-4 text-sm font-medium border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50">
          Actualizar
        </button>
        <button @click="imprimir" class="h-9 px-4 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          Exportar / Imprimir
        </button>
      </div>
    </div>

    <!-- Cabecera visible solo en impresión -->
    <div class="hidden print:block mb-6">
      <h1 class="text-2xl font-bold">Memoria Anual de Actividades {{ anio }}</h1>
      <p class="text-sm text-slate-500">{{ orgNombre }}</p>
    </div>

    <EstadoCarga v-if="cargando" mensaje="Cargando datos del ejercicio..." />
    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="recargar" />

    <template v-else>

      <!-- Resumen estadístico -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        <div v-for="stat in estadisticas" :key="stat.label" class="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div class="text-2xl font-bold" :class="stat.color">{{ stat.valor }}</div>
          <div class="text-xs text-slate-500 mt-1">{{ stat.label }}</div>
        </div>
      </div>

      <!-- Campañas del ejercicio -->
      <AccordionPanel
        title="Campañas"
        :count="campaniasFiltradas.length"
        :default-open="true"
        class="mb-3"
      >
        <div v-if="!campaniasFiltradas.length" class="px-5 py-8 text-center text-slate-400 text-sm">
          Sin campañas en {{ anio }}
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="camp in campaniasFiltradas" :key="camp.id" class="px-5 py-4">
            <!-- Cabecera campaña -->
            <div class="flex items-start justify-between gap-4 mb-2">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <router-link :to="`/campanias/${camp.id}`" class="font-semibold text-slate-800 hover:text-indigo-600 truncate">
                    {{ camp.nombre }}
                  </router-link>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                    {{ camp.tipoCampania?.nombre }}
                  </span>
                  <span class="text-xs px-2 py-0.5 rounded-full" :class="colorEstado(camp.estado?.nombre)">
                    {{ camp.estado?.nombre }}
                  </span>
                  <span v-if="camp.objetivosCumplidos !== null" class="text-xs px-2 py-0.5 rounded-full"
                    :class="camp.objetivosCumplidos ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'">
                    {{ camp.objetivosCumplidos ? 'Objetivos cumplidos' : 'Objetivos no cumplidos' }}
                  </span>
                </div>
                <div v-if="camp.lema" class="text-sm text-slate-500 italic mt-0.5">{{ camp.lema }}</div>
              </div>
              <div class="text-xs text-slate-400 whitespace-nowrap">
                {{ formatFechaRango(camp.fechaInicioPlan || camp.fechaInicioReal, camp.fechaFinPlan || camp.fechaFinReal) }}
              </div>
            </div>

            <!-- Métricas campaña -->
            <div class="flex flex-wrap gap-4 text-xs text-slate-600 mb-2">
              <span v-if="camp.actividades?.length">
                <strong>{{ camp.actividades.length }}</strong> actividades
              </span>
              <span v-if="camp.participantes?.length">
                <strong>{{ camp.participantes.length }}</strong> participantes
              </span>
              <span v-if="camp.presupuestoEstimado">
                Presupuesto: <strong>{{ formatImporte(camp.presupuestoEstimado) }}</strong>
                <template v-if="camp.presupuestoEjecutado"> / ejecutado: <strong>{{ formatImporte(camp.presupuestoEjecutado) }}</strong></template>
              </span>
            </div>

            <!-- Valoración -->
            <div v-if="camp.valoracion" class="text-sm text-slate-600 bg-slate-50 rounded-lg px-3 py-2 mb-2">
              <span class="font-medium text-slate-700">Valoración: </span>{{ camp.valoracion }}
            </div>

            <!-- Actividades de la campaña (colapsadas por defecto) -->
            <details v-if="camp.actividades?.length" class="mt-2">
              <summary class="text-xs text-indigo-600 hover:text-indigo-800 cursor-pointer select-none">
                Ver {{ camp.actividades.length }} actividades de esta campaña
              </summary>
              <div class="mt-2 ml-4 space-y-1">
                <div v-for="act in camp.actividades" :key="act.id"
                  class="flex items-center gap-3 py-1 text-xs text-slate-700 border-l-2 border-slate-200 pl-3">
                  <span class="font-medium">{{ act.nombre }}</span>
                  <span class="text-slate-400">{{ act.tipoActividad?.nombre }}</span>
                  <span class="px-1.5 py-0.5 rounded" :class="colorEstado(act.estado?.nombre)">{{ act.estado?.nombre }}</span>
                  <span v-if="act.fechaInicio" class="text-slate-400">{{ formatFecha(act.fechaInicio) }}</span>
                  <span v-if="act.asistenciaReal" class="text-emerald-600">{{ act.asistenciaReal }} asistentes</span>
                </div>
              </div>
            </details>
          </div>
        </div>
      </AccordionPanel>

      <!-- Actividades independientes -->
      <AccordionPanel
        title="Actividades internas"
        :count="actividadesIndependientes.length"
        :default-open="true"
        class="mb-3"
      >
        <div v-if="!actividadesIndependientes.length" class="px-5 py-8 text-center text-slate-400 text-sm">
          Sin actividades independientes en {{ anio }}
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="act in actividadesIndependientes" :key="act.id" class="px-5 py-3 flex items-center gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <router-link :to="`/actividades/${act.id}`" class="font-medium text-slate-800 hover:text-indigo-600 truncate">
                  {{ act.nombre }}
                </router-link>
                <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">{{ act.tipoActividad?.nombre }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="colorEstado(act.estado?.nombre)">{{ act.estado?.nombre }}</span>
                <span v-if="act.objetivosCumplidos !== null" class="text-xs px-2 py-0.5 rounded-full"
                  :class="act.objetivosCumplidos ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'">
                  {{ act.objetivosCumplidos ? 'Obj. cumplidos' : 'Obj. no cumplidos' }}
                </span>
              </div>
              <div v-if="act.valoracion" class="text-xs text-slate-500 mt-0.5 truncate">{{ act.valoracion }}</div>
            </div>
            <div class="text-xs text-slate-400 whitespace-nowrap shrink-0">
              {{ formatFecha(act.fechaInicio) }}
            </div>
            <div v-if="act.asistenciaReal" class="text-xs text-emerald-600 whitespace-nowrap shrink-0">
              {{ act.asistenciaReal }} asistentes
            </div>
          </div>
        </div>
      </AccordionPanel>

    </template>
  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { graphqlClient } from '@/graphql/client'
import { GET_MEMORIA_ANUAL } from '../graphql/queries.js'

const orgConfigStore = useOrgConfigStore()
const orgNombre = computed(() => orgConfigStore.nombre || '')

const anioActual = new Date().getFullYear()
const anio = ref(anioActual)

const cargando = ref(false)
const error = ref(null)
const todasCampanias = ref([])
const todasActividades = ref([])

async function recargar() {
  cargando.value = true
  error.value = null
  try {
    const data = await graphqlClient.request(GET_MEMORIA_ANUAL)
    todasCampanias.value = data.campanias || []
    todasActividades.value = data.actividades || []
  } catch (e) {
    error.value = e.message || 'Error al cargar datos'
  } finally {
    cargando.value = false
  }
}

// Determina si una campaña/actividad pertenece al ejercicio seleccionado
function perteneceAlAnio(inicio, fin) {
  if (!inicio && !fin) return false
  const y1 = inicio ? new Date(inicio).getFullYear() : null
  const y2 = fin ? new Date(fin).getFullYear() : null
  return y1 === anio.value || y2 === anio.value || (y1 < anio.value && y2 > anio.value)
}

const campaniasFiltradas = computed(() =>
  todasCampanias.value.filter(c =>
    perteneceAlAnio(c.fechaInicioPlan || c.fechaInicioReal, c.fechaFinPlan || c.fechaFinReal)
  )
)

const actividadesIndependientes = computed(() =>
  todasActividades.value.filter(a =>
    !a.campania?.id && perteneceAlAnio(a.fechaInicio, a.fechaFin)
  )
)

const estadisticas = computed(() => {
  const camps = campaniasFiltradas.value
  const acts = actividadesIndependientes.value
  const todasActs = camps.flatMap(c => c.actividades || []).concat(acts)

  const totalParticipantes = camps.reduce((s, c) => s + (c.participantes?.length || 0), 0)
    + todasActs.reduce((s, a) => s + (a.participaciones?.length || 0), 0)

  const presupEstimado = [...camps, ...todasActs].reduce((s, x) => s + parseFloat(x.presupuestoEstimado || 0), 0)
  const presupEjecutado = [...camps, ...todasActs].reduce((s, x) => s + parseFloat(x.presupuestoEjecutado || 0), 0)
  const actsCumplidas = todasActs.filter(a => a.objetivosCumplidos === true).length

  return [
    { label: 'Campañas', valor: camps.length, color: 'text-indigo-600' },
    { label: 'Actividades', valor: todasActs.length, color: 'text-blue-600' },
    { label: 'Participaciones', valor: totalParticipantes, color: 'text-violet-600' },
    { label: 'Obj. cumplidos', valor: actsCumplidas, color: 'text-emerald-600' },
    { label: 'Presup. estimado', valor: formatImporte(presupEstimado), color: 'text-amber-600' },
    { label: 'Presup. ejecutado', valor: formatImporte(presupEjecutado), color: 'text-orange-600' },
  ]
})

function colorEstado(nombre) {
  if (!nombre) return 'bg-slate-100 text-slate-600'
  const n = nombre.toLowerCase()
  if (n.includes('finaliz') || n.includes('cerrad')) return 'bg-emerald-100 text-emerald-700'
  if (n.includes('aprobad')) return 'bg-green-100 text-green-700'
  if (n.includes('pendiente')) return 'bg-amber-100 text-amber-700'
  if (n.includes('curso') || n.includes('activ') || n.includes('seguim')) return 'bg-blue-100 text-blue-700'
  if (n.includes('cancel') || n.includes('rechaz')) return 'bg-red-100 text-red-700'
  if (n.includes('preparac') || n.includes('programad')) return 'bg-sky-100 text-sky-700'
  return 'bg-slate-100 text-slate-600'
}

function formatFecha(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatFechaRango(inicio, fin) {
  if (!inicio && !fin) return ''
  if (inicio && fin) return `${formatFecha(inicio)} – ${formatFecha(fin)}`
  return formatFecha(inicio || fin)
}

function formatImporte(v) {
  const n = parseFloat(v) || 0
  if (n === 0) return '—'
  return n.toLocaleString('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
}

function imprimir() {
  window.print()
}

onMounted(recargar)
</script>

<style>
@media print {
  .print\:hidden { display: none !important; }
  .print\:block { display: block !important; }

  details[open] summary { display: none; }
  details { display: block; }
  details > *:not(summary) { display: block; }
}
</style>
