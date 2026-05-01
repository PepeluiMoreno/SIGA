<template>
  <AppLayout title="Eventos" subtitle="Actos, jornadas y asambleas de Europa Laica">
    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <p class="text-sm text-gray-500">Total eventos</p>
        <p class="text-xl font-bold text-purple-600">{{ eventos.length }}</p>
      </div>
      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <p class="text-sm text-gray-500">Confirmados</p>
        <p class="text-xl font-bold text-green-600">{{ eventosConfirmados }}</p>
      </div>
      <div class="bg-blue-50 rounded-lg shadow p-4 border border-blue-100">
        <p class="text-sm text-gray-500">En preparación</p>
        <p class="text-xl font-bold text-blue-600">{{ eventosEnPreparacion }}</p>
      </div>
      <div class="bg-yellow-50 rounded-lg shadow p-4 border border-yellow-100">
        <p class="text-sm text-gray-500">Próximos (30 días)</p>
        <p class="text-xl font-bold text-yellow-600">{{ eventosProximos }}</p>
      </div>
    </div>

    <!-- Barra de filtros + toggle de vista -->
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar eventos..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <div class="absolute left-3 top-2.5 text-gray-400">🔍</div>
          </div>
        </div>
        <div class="flex gap-2 items-center">
          <!-- Toggle lista / calendario -->
          <div class="flex rounded-lg overflow-hidden border border-gray-300 text-sm">
            <button
              @click="vista = 'lista'"
              :class="['px-4 py-2 flex items-center gap-1.5 font-medium transition-colors',
                vista === 'lista' ? 'bg-purple-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
              </svg>
              Lista
            </button>
            <button
              @click="vista = 'calendario'"
              :class="['px-4 py-2 flex items-center gap-1.5 font-medium border-l border-gray-300 transition-colors',
                vista === 'calendario' ? 'bg-purple-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              Calendario
            </button>
          </div>
          <button
            @click="showFilters = !showFilters"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
          >
            Filtros
          </button>
          <router-link
            to="/eventos/nuevo"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
          >
            + Nuevo Evento
          </router-link>
        </div>
      </div>

      <div v-if="showFilters" class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div>
          <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Tipo</label>
          <select v-model="filtroTipo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Todos</option>
            <option v-for="t in tiposEvento" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Estado</label>
          <select v-model="filtroEstado" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Todos</option>
            <option v-for="e in estadosEvento" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Periodo</label>
          <select v-model="filtroPeriodo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Todos</option>
            <option value="proximos">Próximos</option>
            <option value="pasados">Pasados</option>
            <option value="mes">Este mes</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <!-- Vista Lista -->
    <div v-else-if="vista === 'lista'" class="space-y-3">
      <div v-if="eventosFiltrados.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-4xl mb-4">📅</p>
        <p class="text-sm text-gray-500">No hay eventos con los filtros seleccionados.</p>
      </div>

      <div
        v-for="e in eventosFiltrados"
        :key="e.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-100"
      >
        <div class="p-5 flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <!-- Fecha -->
          <div class="flex-shrink-0 w-16 text-center hidden md:block">
            <div class="bg-purple-100 rounded-lg p-2">
              <p class="text-xs text-purple-600 font-medium uppercase">{{ mesCorto(e.fechaInicio) }}</p>
              <p class="text-2xl font-bold text-purple-800">{{ dia(e.fechaInicio) }}</p>
            </div>
          </div>

          <!-- Contenido -->
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <h3 class="text-base font-semibold text-gray-900">{{ e.nombre }}</h3>
              <span
                v-if="e.tipoEvento"
                class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800"
              >{{ e.tipoEvento.nombre }}</span>
              <span
                v-if="e.estado"
                class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                :style="e.estado.color
                  ? `background:${e.estado.color}22;color:${e.estado.color}`
                  : 'background:#f3f4f6;color:#374151'"
              >{{ e.estado.nombre }}</span>
            </div>

            <p v-if="e.descripcionCorta" class="text-sm text-gray-600 mb-2 truncate">{{ e.descripcionCorta }}</p>

            <div class="flex flex-wrap gap-4 text-xs text-gray-500">
              <span v-if="e.lugar || e.ciudad">
                📍 {{ [e.lugar, e.ciudad].filter(Boolean).join(', ') }}
                <span v-if="e.esOnline" class="ml-1 text-blue-600">(también online)</span>
              </span>
              <span v-else-if="e.esOnline">🌐 Online</span>
              <span>
                🕐 {{ formatFecha(e.fechaInicio) }}
                <template v-if="e.fechaFin && e.fechaFin !== e.fechaInicio"> → {{ formatFecha(e.fechaFin) }}</template>
                <template v-if="!e.esTodoDia && e.horaInicio"> · {{ e.horaInicio }}</template>
              </span>
              <span v-if="e.requiereInscripcion">
                🎟 {{ e.participantes?.length ?? 0 }} inscritos
                <template v-if="e.aforoMaximo"> / {{ e.aforoMaximo }}</template>
              </span>
              <span v-if="e.campania">🚩 {{ e.campania.nombre }}</span>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex gap-2 flex-shrink-0">
            <router-link
              :to="`/eventos/${e.id}`"
              class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
            >
              Ver detalle
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Vista Calendario -->
    <div v-else-if="vista === 'calendario'" class="bg-white rounded-lg shadow overflow-hidden">
      <!-- Navegación de mes -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <button
          @click="mesAnterior"
          class="p-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-colors"
          title="Mes anterior"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <div class="text-center">
          <h2 class="text-lg font-semibold text-gray-800 capitalize">{{ nombreMes }} {{ calendarioAnio }}</h2>
          <p class="text-xs text-gray-400">{{ eventosFiltrados.length }} evento(s) total</p>
        </div>
        <button
          @click="mesSiguiente"
          class="p-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-colors"
          title="Mes siguiente"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

      <!-- Cabecera días de semana -->
      <div class="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
        <div
          v-for="d in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']"
          :key="d"
          class="py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider"
        >{{ d }}</div>
      </div>

      <!-- Cuadrícula del mes -->
      <div class="grid grid-cols-7 border-l border-t border-gray-100">
        <div
          v-for="(celda, idx) in diasCalendario"
          :key="idx"
          @click="() => celda.fecha && celda.eventos.length > 0 && abrirDia(celda)"
          :class="[
            'min-h-[110px] border-b border-r border-gray-100 p-2 flex flex-col',
            celda.fecha && celda.eventos.length > 0
              ? 'cursor-pointer hover:bg-purple-50/60 transition-colors'
              : '',
            esDiaHoy(celda) ? 'bg-amber-50/40' : (!celda.dia ? 'bg-gray-50/50' : ''),
          ]"
        >
          <!-- Número del día -->
          <div class="flex-shrink-0 mb-1">
            <span
              v-if="celda.dia"
              :class="[
                'inline-flex items-center justify-center w-7 h-7 text-sm font-medium rounded-full',
                esDiaHoy(celda)
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >{{ celda.dia }}</span>
          </div>

          <!-- Chips de eventos del día -->
          <div class="flex-1 space-y-0.5 overflow-hidden">
            <div
              v-for="e in celda.eventos.slice(0, 3)"
              :key="e.id"
              :style="`border-left: 3px solid ${e.estado?.color || '#8B5CF6'}; background: ${e.estado?.color || '#8B5CF6'}18`"
              class="text-xs px-1.5 py-0.5 rounded-r text-gray-800 leading-tight truncate"
              :title="e.nombre"
            >{{ e.nombre }}</div>
            <div
              v-if="celda.eventos.length > 3"
              class="text-xs text-gray-400 pl-1"
            >+{{ celda.eventos.length - 3 }} más</div>
          </div>
        </div>
      </div>

      <!-- Leyenda de colores -->
      <div v-if="estadosEvento.length" class="flex flex-wrap gap-4 px-6 py-3 border-t border-gray-100 bg-gray-50">
        <div
          v-for="est in estadosEvento.filter(e => e.activo)"
          :key="est.id"
          class="flex items-center gap-1.5 text-xs text-gray-600"
        >
          <span
            :style="`background: ${est.color || '#8B5CF6'}`"
            class="inline-block w-2.5 h-2.5 rounded-sm"
          ></span>
          {{ est.nombre }}
        </div>
      </div>
    </div>

    <!-- Modal: detalle del día -->
    <Teleport to="body">
      <div
        v-if="showModal && diaSeleccionado"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 max-h-[80vh] flex flex-col overflow-hidden">
          <!-- Cabecera modal -->
          <div class="flex items-start justify-between p-5 border-b border-gray-200 bg-purple-50">
            <div>
              <h3 class="text-base font-semibold text-gray-900 capitalize">
                {{ formatFechaLarga(diaSeleccionado.fecha) }}
              </h3>
              <p class="text-sm text-purple-600 mt-0.5">
                {{ diaSeleccionado.eventos.length }} evento{{ diaSeleccionado.eventos.length > 1 ? 's' : '' }}
              </p>
            </div>
            <button
              @click="showModal = false"
              class="text-gray-400 hover:text-gray-600 transition-colors p-1 -mt-1 -mr-1"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Lista de eventos del día -->
          <div class="overflow-y-auto flex-1 p-4 space-y-3">
            <div
              v-for="e in diaSeleccionado.eventos"
              :key="e.id"
              class="border border-gray-200 rounded-xl p-4 hover:border-purple-300 transition-colors"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                  <!-- Nombre + badges -->
                  <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
                    <h4 class="font-semibold text-gray-900 text-sm">{{ e.nombre }}</h4>
                    <span
                      v-if="e.tipoEvento"
                      class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700"
                    >{{ e.tipoEvento.nombre }}</span>
                  </div>

                  <!-- Estado con color -->
                  <div v-if="e.estado" class="mb-2">
                    <span
                      class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full"
                      :style="e.estado.color
                        ? `background:${e.estado.color}22;color:${e.estado.color}`
                        : 'background:#f3f4f6;color:#374151'"
                    >
                      <span :style="`background:${e.estado.color || '#8B5CF6'}`" class="w-1.5 h-1.5 rounded-full inline-block"></span>
                      {{ e.estado.nombre }}
                    </span>
                  </div>

                  <!-- Detalles -->
                  <div class="text-xs text-gray-500 space-y-1">
                    <p v-if="!e.esTodoDia && e.horaInicio">
                      🕐 {{ e.horaInicio }}<template v-if="e.horaFin"> – {{ e.horaFin }}</template>
                    </p>
                    <p v-else class="text-xs text-gray-400">Todo el día</p>
                    <p v-if="e.lugar || e.ciudad">📍 {{ [e.lugar, e.ciudad].filter(Boolean).join(', ') }}</p>
                    <p v-if="e.esOnline">🌐 Online</p>
                    <p v-if="e.requiereInscripcion && e.aforoMaximo">
                      🎟 {{ e.participantes?.length ?? 0 }} / {{ e.aforoMaximo }} plazas
                    </p>
                  </div>
                </div>

                <!-- Link al detalle -->
                <router-link
                  :to="`/eventos/${e.id}`"
                  @click="showModal = false"
                  class="flex-shrink-0 text-xs font-medium text-purple-600 hover:text-purple-800 hover:underline whitespace-nowrap"
                >
                  Ver →
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_EVENTOS, GET_TIPOS_EVENTO, GET_ESTADOS_EVENTO } from '@/graphql/queries/eventos.js'

// ---------- datos ----------
const loading = ref(false)
const error = ref('')
const eventos = ref([])
const tiposEvento = ref([])
const estadosEvento = ref([])

// ---------- filtros ----------
const searchQuery = ref('')
const showFilters = ref(false)
const filtroTipo = ref('')
const filtroEstado = ref('')
const filtroPeriodo = ref('')

// ---------- vista ----------
const vista = ref('lista') // 'lista' | 'calendario'

// ---------- calendario ----------
const hoy = new Date()
const hoyStr = hoy.toISOString().split('T')[0]
const calendarioMes = ref(hoy.getMonth())
const calendarioAnio = ref(hoy.getFullYear())

// ---------- modal ----------
const showModal = ref(false)
const diaSeleccionado = ref(null)

// ---------- computed de resumen ----------
const eventosConfirmados = computed(() =>
  eventos.value.filter(e => e.estado?.nombre?.toLowerCase().includes('confirmad')).length
)
const eventosEnPreparacion = computed(() =>
  eventos.value.filter(e => e.estado?.nombre?.toLowerCase().includes('preparaci')).length
)
const eventosProximos = computed(() => {
  const limite = new Date(hoy)
  limite.setDate(limite.getDate() + 30)
  return eventos.value.filter(e => {
    const f = new Date(e.fechaInicio + 'T00:00:00')
    return f >= hoy && f <= limite
  }).length
})

// ---------- computed de filtrado ----------
const eventosFiltrados = computed(() => {
  let result = [...eventos.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(e =>
      e.nombre?.toLowerCase().includes(q) ||
      e.descripcionCorta?.toLowerCase().includes(q) ||
      e.lugar?.toLowerCase().includes(q) ||
      e.ciudad?.toLowerCase().includes(q)
    )
  }
  if (filtroTipo.value) {
    result = result.filter(e => e.tipoEvento?.id === filtroTipo.value)
  }
  if (filtroEstado.value) {
    result = result.filter(e => e.estado?.id === filtroEstado.value)
  }
  if (filtroPeriodo.value === 'proximos') {
    result = result.filter(e => new Date(e.fechaInicio + 'T00:00:00') >= hoy)
  } else if (filtroPeriodo.value === 'pasados') {
    result = result.filter(e => new Date(e.fechaInicio + 'T00:00:00') < hoy)
  } else if (filtroPeriodo.value === 'mes') {
    const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
    const finMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)
    result = result.filter(e => {
      const f = new Date(e.fechaInicio + 'T00:00:00')
      return f >= inicioMes && f <= finMes
    })
  }

  return result.sort((a, b) => a.fechaInicio.localeCompare(b.fechaInicio))
})

// ---------- computed de calendario ----------
const nombreMes = computed(() =>
  new Date(calendarioAnio.value, calendarioMes.value, 1)
    .toLocaleDateString('es-ES', { month: 'long' })
)

const eventosPorDia = computed(() => {
  const map = {}
  for (const e of eventosFiltrados.value) {
    if (!e.fechaInicio) continue
    if (!map[e.fechaInicio]) map[e.fechaInicio] = []
    map[e.fechaInicio].push(e)
  }
  return map
})

const diasCalendario = computed(() => {
  const primerDia = new Date(calendarioAnio.value, calendarioMes.value, 1)
  const ultimoDia = new Date(calendarioAnio.value, calendarioMes.value + 1, 0)

  // Semana empieza en lunes: domingo (0) → 7
  let offsetInicio = primerDia.getDay()
  if (offsetInicio === 0) offsetInicio = 7

  const celdas = []

  // Celdas vacías antes del día 1
  for (let i = 1; i < offsetInicio; i++) {
    celdas.push({ dia: null, fecha: null, eventos: [] })
  }

  // Días del mes
  for (let d = 1; d <= ultimoDia.getDate(); d++) {
    const mes = String(calendarioMes.value + 1).padStart(2, '0')
    const diaStr = String(d).padStart(2, '0')
    const fecha = `${calendarioAnio.value}-${mes}-${diaStr}`
    celdas.push({ dia: d, fecha, eventos: eventosPorDia.value[fecha] || [] })
  }

  // Rellenar hasta múltiplo de 7
  while (celdas.length % 7 !== 0) {
    celdas.push({ dia: null, fecha: null, eventos: [] })
  }

  return celdas
})

// ---------- funciones de calendario ----------
function esDiaHoy(celda) {
  return celda.fecha === hoyStr
}

function mesAnterior() {
  if (calendarioMes.value === 0) {
    calendarioMes.value = 11
    calendarioAnio.value--
  } else {
    calendarioMes.value--
  }
}

function mesSiguiente() {
  if (calendarioMes.value === 11) {
    calendarioMes.value = 0
    calendarioAnio.value++
  } else {
    calendarioMes.value++
  }
}

function abrirDia(celda) {
  diaSeleccionado.value = celda
  showModal.value = true
}

// ---------- helpers de formato ----------
function mesCorto(fecha) {
  return new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES', { month: 'short' }).toUpperCase()
}

function dia(fecha) {
  return new Date(fecha + 'T00:00:00').getDate()
}

function formatFecha(fecha) {
  return new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

function formatFechaLarga(fecha) {
  if (!fecha) return ''
  return new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  })
}

// ---------- carga ----------
async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const [dataEventos, dataTipos, dataEstados] = await Promise.all([
      executeQuery(GET_EVENTOS),
      executeQuery(GET_TIPOS_EVENTO),
      executeQuery(GET_ESTADOS_EVENTO),
    ])
    eventos.value = dataEventos.eventos || []
    tiposEvento.value = dataTipos.tiposEvento || []
    estadosEvento.value = dataEstados.estadosEvento || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando eventos'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
