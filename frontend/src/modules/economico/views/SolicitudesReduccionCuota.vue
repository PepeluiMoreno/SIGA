<template>
  <div class="p-5">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por socio…"
      :fields="camposFiltro"
      :count-text="`${solicitudesFiltradas.length} de ${solicitudes.length}`"
    />

    <div v-if="loading" class="py-12 text-center text-sm text-slate-400">Cargando…</div>

    <div v-else-if="!solicitudesFiltradas.length" class="py-12 text-center text-sm text-slate-400">
      No hay solicitudes que mostrar.
    </div>

    <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden mt-3">
      <div class="overflow-x-auto -mx-1"><table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Socio</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Tipo de reducción</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Ejercicio</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Presentada</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Estado</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="s in solicitudesFiltradas" :key="s.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3 font-medium text-slate-900">{{ nombreSocio(s.miembro) }}</td>
            <td class="px-4 py-3 text-slate-600">
              {{ s.motivoReduccion?.nombre || '—' }}
              <span v-if="s.motivoReduccion" class="text-slate-400">
                ({{ Number(s.motivoReduccion.porcentajeReduccion) }}%)
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ s.ejercicio }}</td>
            <td class="px-4 py-3 text-slate-500">{{ fechaFmt(s.fechaPresentacion) }}</td>
            <td class="px-4 py-3">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" :class="claseEstado(s.estado)">
                {{ etiquetaEstado(s.estado) }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button @click="abrirDetalle(s)"
                class="h-8 px-3 text-xs font-medium text-indigo-600 border border-slate-300 rounded-lg hover:bg-slate-50">
                Ver
              </button>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- Modal de detalle / resolución -->
    <div v-if="detalle" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 class="text-base font-semibold text-slate-900">Solicitud de reducción de cuota</h3>
          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" :class="claseEstado(detalle.estado)">
            {{ etiquetaEstado(detalle.estado) }}
          </span>
        </div>
        <div class="px-6 py-5 space-y-4 text-sm">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-slate-500">Socio</p>
              <p class="font-medium text-slate-800">{{ nombreSocio(detalle.miembro) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500">Ejercicio</p>
              <p class="font-medium text-slate-800">{{ detalle.ejercicio }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500">Tipo de reducción</p>
              <p class="font-medium text-slate-800">
                {{ detalle.motivoReduccion?.nombre || '—' }}
                <span v-if="detalle.motivoReduccion" class="text-slate-400">
                  ({{ Number(detalle.motivoReduccion.porcentajeReduccion) }}%)
                </span>
              </p>
            </div>
            <div>
              <p class="text-xs text-slate-500">Presentada</p>
              <p class="font-medium text-slate-800">{{ fechaFmt(detalle.fechaPresentacion) }}</p>
            </div>
          </div>

          <div v-if="detalle.textoSolicitud">
            <p class="text-xs text-slate-500 mb-0.5">Explicación del socio</p>
            <p class="text-slate-700 bg-slate-50 rounded-lg px-3 py-2">{{ detalle.textoSolicitud }}</p>
          </div>

          <div>
            <p class="text-xs text-slate-500 mb-1">Documentos acreditativos</p>
            <ul v-if="detalle.documentos?.length" class="space-y-1">
              <li v-for="d in detalle.documentos" :key="d.id">
                <a :href="docUrl(d.url)" target="_blank"
                  class="text-indigo-600 hover:underline text-sm inline-flex items-center gap-1">
                  📎 {{ d.nombreArchivo }}
                </a>
              </li>
            </ul>
            <p v-else class="text-slate-400 italic">Sin documentos adjuntos.</p>
          </div>

          <div v-if="detalle.estado === 'RECHAZADA' && detalle.motivoRechazo"
            class="bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            <p class="text-xs text-red-600 mb-0.5">Motivo del rechazo</p>
            <p class="text-red-800">{{ detalle.motivoRechazo }}</p>
          </div>

          <!-- Campo de rechazo -->
          <div v-if="modoRechazo">
            <label class="block text-xs font-medium text-slate-700 mb-1">Motivo del rechazo *</label>
            <textarea v-model="motivoRechazo" rows="3"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
              placeholder="Indica por qué se rechaza la solicitud…"></textarea>
          </div>

          <ErrorAlert v-if="error" :message="error" />
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="cerrarDetalle"
            class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            Cerrar
          </button>
          <template v-if="detalle.estado === 'PRESENTADA'">
            <template v-if="modoRechazo">
              <button @click="modoRechazo = false"
                class="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
              <button @click="rechazar" :disabled="ocupado"
                class="px-5 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
                Confirmar rechazo
              </button>
            </template>
            <template v-else>
              <button @click="modoRechazo = true"
                class="px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50">
                Rechazar
              </button>
              <button @click="aprobar" :disabled="ocupado"
                class="px-5 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">
                {{ ocupado ? '…' : 'Aprobar' }}
              </button>
            </template>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useAuthStore } from '@/stores/auth'

const { query, mutation } = useGraphQL()
const authStore = useAuthStore()

const loading = ref(true)
const solicitudes = ref([])
const ambito = ref({ veTodas: true, agrupacionIds: [] })
const busqueda = ref('')
const filtros = ref({ estado: 'PRESENTADA' })
const detalle = ref(null)
const modoRechazo = ref(false)
const motivoRechazo = ref('')
const ocupado = ref(false)
const error = ref('')

const camposFiltro = [
  {
    key: 'estado',
    label: 'Estado',
    type: 'select',
    allLabel: 'Todos los estados',
    options: [
      { value: 'PRESENTADA', label: 'Pendientes' },
      { value: 'APROBADA', label: 'Aprobadas' },
      { value: 'RECHAZADA', label: 'Rechazadas' },
      { value: 'ANULADA', label: 'Anuladas' },
    ],
  },
]

const GET_SOLICITUDES = `
  query SolicitudesReduccionCuota {
    solicitudesReduccionCuota(filter: { eliminado: { eq: false } }) {
      id estado ejercicio fechaPresentacion fechaResolucion textoSolicitud motivoRechazo
      miembro { id nombre apellido1 apellido2 agrupacionId }
      motivoReduccion { id nombre porcentajeReduccion }
      resolutor { id nombre apellido1 }
      documentos { id nombreArchivo url mimeType }
    }
  }
`
const APROBAR = `
  mutation Aprobar($id: UUID!, $resueltoPorId: UUID!) {
    aprobarSolicitudReduccionCuota(solicitudId: $id, resueltoPorId: $resueltoPorId)
  }
`
const RECHAZAR = `
  mutation Rechazar($id: UUID!, $resueltoPorId: UUID!, $motivo: String!) {
    rechazarSolicitudReduccionCuota(solicitudId: $id, resueltoPorId: $resueltoPorId, motivo: $motivo)
  }
`
// Ámbito de tesorería: qué agrupaciones puede ver el tesorero que consulta.
const GET_AMBITO = `
  query AmbitoTesoreria {
    ambitoTesoreria { veTodas agrupacionIds }
  }
`

const nombreSocio = (m) =>
  m ? `${m.nombre || ''} ${m.apellido1 || ''} ${m.apellido2 || ''}`.trim() || '—' : '—'

const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

const docUrl = (url) => url?.startsWith('http') ? url : `${window.location.origin}${url}`

const ETIQUETAS = {
  PRESENTADA: 'Pendiente', APROBADA: 'Aprobada', RECHAZADA: 'Rechazada', ANULADA: 'Anulada',
}
const etiquetaEstado = (e) => ETIQUETAS[e] || e

const claseEstado = (e) => ({
  PRESENTADA: 'bg-amber-100 text-amber-700',
  APROBADA: 'bg-green-100 text-green-700',
  RECHAZADA: 'bg-red-100 text-red-700',
  ANULADA: 'bg-slate-100 text-slate-500',
}[e] || 'bg-slate-100 text-slate-600')

const solicitudesFiltradas = computed(() => {
  let list = solicitudes.value
  // Tesorería distribuida: el tesorero regional solo ve su ámbito de agrupaciones.
  if (!ambito.value.veTodas) {
    const ids = new Set(ambito.value.agrupacionIds || [])
    list = list.filter(s => ids.has(s.miembro?.agrupacionId))
  }
  if (filtros.value.estado) {
    list = list.filter(s => s.estado === filtros.value.estado)
  }
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    list = list.filter(s => nombreSocio(s.miembro).toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => (b.fechaPresentacion || '').localeCompare(a.fechaPresentacion || ''))
})

async function cargar() {
  loading.value = true
  try {
    const [datSol, datAmb] = await Promise.all([
      query(GET_SOLICITUDES),
      query(GET_AMBITO),
    ])
    solicitudes.value = datSol.solicitudesReduccionCuota || []
    ambito.value = datAmb.ambitoTesoreria || { veTodas: true, agrupacionIds: [] }
  } catch (e) {
    console.error('Error cargando solicitudes:', e)
  } finally {
    loading.value = false
  }
}

function abrirDetalle(s) {
  detalle.value = s
  modoRechazo.value = false
  motivoRechazo.value = ''
  error.value = ''
}
function cerrarDetalle() {
  detalle.value = null
}

const errMsg = (e, fallback) =>
  e?.response?.errors?.[0]?.message || (e?.message || '').split(': {')[0] || fallback

async function aprobar() {
  error.value = ''
  const resueltoPorId = authStore.user?.miembroId
  if (!resueltoPorId) { error.value = 'No se ha podido determinar tu ficha de socio.'; return }
  ocupado.value = true
  try {
    await mutation(APROBAR, { id: detalle.value.id, resueltoPorId })
    cerrarDetalle()
    await cargar()
  } catch (e) {
    error.value = errMsg(e, 'No se pudo aprobar la solicitud.')
  } finally {
    ocupado.value = false
  }
}

async function rechazar() {
  error.value = ''
  if (!motivoRechazo.value.trim()) { error.value = 'Indica el motivo del rechazo.'; return }
  const resueltoPorId = authStore.user?.miembroId
  if (!resueltoPorId) { error.value = 'No se ha podido determinar tu ficha de socio.'; return }
  ocupado.value = true
  try {
    await mutation(RECHAZAR, { id: detalle.value.id, resueltoPorId, motivo: motivoRechazo.value.trim() })
    cerrarDetalle()
    await cargar()
  } catch (e) {
    error.value = errMsg(e, 'No se pudo rechazar la solicitud.')
  } finally {
    ocupado.value = false
  }
}

onMounted(cargar)
</script>
