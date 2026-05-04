<template>
  <AppLayout :title="agrupacion ? `Junta: ${agrupacion.nombre}` : 'Junta Directiva'" subtitle="Gestión de la junta directiva y cargos">

    <!-- Loading agrupación -->
    <div v-if="loadingAgrupacion" class="text-center py-16">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>

    <template v-else>
      <!-- Header: info agrupación + constitución -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 class="text-xl font-bold text-gray-900">{{ agrupacion?.nombre }}</h2>
          <p class="text-sm text-gray-500 mt-0.5">{{ agrupacion?.tipo }} · {{ agrupacion?.provincia?.nombre }}</p>
        </div>
        <button
          @click="abrirModalJunta"
          class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Constituir nueva junta
        </button>
      </div>

      <!-- Sin junta -->
      <div v-if="!junta && !loadingJunta" class="text-center py-16 bg-white rounded-xl border border-dashed border-gray-300">
        <svg class="mx-auto w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <p class="text-gray-500 font-medium">Esta agrupación no tiene junta directiva activa</p>
        <p class="text-sm text-gray-400 mt-1">Usa el botón superior para constituirla</p>
      </div>

      <!-- Junta activa -->
      <template v-else-if="junta">
        <!-- Tabs -->
        <div class="border-b border-gray-200 mb-6">
          <nav class="-mb-px flex gap-6">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="pb-3 text-sm font-medium border-b-2 transition-colors"
              :class="activeTab === tab.id
                ? 'border-purple-600 text-purple-700'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            >
              {{ tab.label }}
              <span v-if="tab.count !== undefined"
                class="ml-2 px-2 py-0.5 rounded-full text-xs"
                :class="activeTab === tab.id ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'"
              >{{ tab.count }}</span>
            </button>
          </nav>
        </div>

        <!-- Tab: Composición actual -->
        <div v-show="activeTab === 'composicion'">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900">{{ junta.nombre }}</h3>
              <p class="text-sm text-gray-500">
                Constituida el {{ formatDate(junta.fechaConstitucion) }} ·
                <span class="text-green-600 font-medium">Activa</span>
              </p>
            </div>
            <button
              @click="abrirModalCargo"
              class="inline-flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 text-sm font-medium rounded-lg hover:bg-gray-50 transition shadow-sm"
            >
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Asignar cargo
            </button>
          </div>

          <div v-if="cargosActivos.length === 0" class="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <p class="text-gray-500 text-sm">No hay cargos asignados en esta junta</p>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="cargo in cargosOrdenados"
              :key="cargo.id"
              class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col gap-3 hover:shadow-md transition-shadow"
            >
              <!-- Cargo header -->
              <div class="flex items-start justify-between">
                <div>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {{ cargo.tipoCargo.nombre }}
                    <span v-if="cargo.tipoCargo.permiteMultiples" class="ml-1 text-purple-500">#{{ cargo.posicion }}</span>
                  </span>
                </div>
                <button
                  @click="confirmarRevocacion(cargo)"
                  class="text-gray-300 hover:text-red-500 transition-colors"
                  title="Revocar cargo"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <!-- Miembro -->
              <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <span class="text-white text-sm font-semibold">{{ iniciales(cargo.miembro) }}</span>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-900 truncate">{{ nombreCompleto(cargo.miembro) }}</p>
                  <p class="text-xs text-gray-500 truncate">{{ cargo.miembro.email || '—' }}</p>
                </div>
              </div>

              <!-- Fecha -->
              <div class="text-xs text-gray-400">
                Desde {{ formatDate(cargo.fechaInicio) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Tab: Historial -->
        <div v-show="activeTab === 'historial'">
          <div v-if="loadingHistorial" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
          </div>
          <div v-else-if="historial.length === 0" class="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <p class="text-gray-500 text-sm">No hay registros históricos</p>
          </div>
          <div v-else class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <table class="min-w-full divide-y divide-gray-100">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cargo</th>
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Miembro</th>
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Inicio</th>
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Fin</th>
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Motivo</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="h in historialOrdenado" :key="h.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-5 py-3 text-sm">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {{ h.tipoCargo.nombre }}
                    </span>
                  </td>
                  <td class="px-5 py-3 text-sm text-gray-900 font-medium">{{ nombreCompleto(h.miembro) }}</td>
                  <td class="px-5 py-3 text-sm text-gray-600">{{ formatDate(h.fechaInicio) }}</td>
                  <td class="px-5 py-3 text-sm text-gray-600">
                    <span v-if="h.fechaFin" class="text-red-500">{{ formatDate(h.fechaFin) }}</span>
                    <span v-else class="text-green-600 font-medium">Activo</span>
                  </td>
                  <td class="px-5 py-3 text-sm text-gray-500 max-w-xs truncate">{{ h.motivoCambio || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </template>

    <!-- ===== MODAL: Constituir junta ===== -->
    <Teleport to="body">
      <div v-if="modalJunta" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="modalJunta = false"/>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Constituir nueva junta</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de la junta <span class="text-red-500">*</span></label>
                <input v-model="formJunta.nombre" type="text" placeholder="Ej: Junta Directiva 2025-2027"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de constitución <span class="text-red-500">*</span></label>
                <input v-model="formJunta.fechaConstitucion" type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
                <textarea v-model="formJunta.observaciones" rows="3" placeholder="Notas opcionales..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"/>
              </div>
              <div v-if="junta" class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-xs text-yellow-800">
                La junta actual <strong>{{ junta.nombre }}</strong> quedará desactivada.
              </div>
              <div v-if="modalError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{{ modalError }}</div>
            </div>
            <div class="flex gap-3 mt-6">
              <button @click="modalJunta = false" class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
              <button @click="constituirJunta" :disabled="modalLoading"
                class="flex-1 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-60 flex items-center justify-center gap-2">
                <svg v-if="modalLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Constituir
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== MODAL: Asignar cargo ===== -->
      <div v-if="modalCargo" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="modalCargo = false"/>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Asignar cargo</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de cargo <span class="text-red-500">*</span></label>
                <select v-model="formCargo.tipoCargaId"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
                  <option value="">Seleccionar...</option>
                  <option v-for="tc in tiposCargo" :key="tc.id" :value="tc.id">
                    {{ tc.nombre }}{{ tc.permiteMultiples ? ' (múltiple)' : '' }}
                  </option>
                </select>
              </div>
              <div v-if="tipoCargaSeleccionado?.permiteMultiples">
                <label class="block text-sm font-medium text-gray-700 mb-1">Posición (vocalía)</label>
                <input v-model.number="formCargo.posicion" type="number" min="1"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  :placeholder="`Siguiente disponible: ${siguientePosicion}`"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Miembro <span class="text-red-500">*</span></label>
                <input v-model="busquedaMiembro" type="text" placeholder="Buscar por nombre..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"/>
                <div v-if="miembrosFiltrados.length > 0 && busquedaMiembro.length > 1"
                  class="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-40 overflow-y-auto">
                  <button v-for="m in miembrosFiltrados" :key="m.id"
                    @click="seleccionarMiembro(m)"
                    class="w-full text-left px-4 py-2 text-sm hover:bg-purple-50 transition-colors">
                    {{ nombreCompleto(m) }}
                    <span class="text-xs text-gray-400 ml-2">{{ m.email }}</span>
                  </button>
                </div>
                <p v-if="formCargo.miembroId" class="mt-1 text-sm text-purple-700 font-medium">
                  Seleccionado: {{ miembroSeleccionadoNombre }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de inicio <span class="text-red-500">*</span></label>
                <input v-model="formCargo.fechaInicio" type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"/>
              </div>
              <div v-if="modalError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{{ modalError }}</div>
            </div>
            <div class="flex gap-3 mt-6">
              <button @click="modalCargo = false" class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
              <button @click="asignarCargo" :disabled="modalLoading"
                class="flex-1 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-60 flex items-center justify-center gap-2">
                <svg v-if="modalLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Asignar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== MODAL: Confirmar revocación ===== -->
      <div v-if="modalRevocar" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="modalRevocar = false"/>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-2">Revocar cargo</h3>
            <p class="text-sm text-gray-600 mb-4">
              ¿Revocar el cargo de <strong>{{ cargoRevocar?.tipoCargo.nombre }}</strong>
              a <strong>{{ nombreCompleto(cargoRevocar?.miembro) }}</strong>?
            </p>
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de fin <span class="text-red-500">*</span></label>
                <input v-model="formRevocar.fechaFin" type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-400"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
                <input v-model="formRevocar.motivo" type="text" placeholder="Opcional..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-400"/>
              </div>
              <div v-if="modalError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{{ modalError }}</div>
            </div>
            <div class="flex gap-3 mt-5">
              <button @click="modalRevocar = false" class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
              <button @click="revocarCargo" :disabled="modalLoading"
                class="flex-1 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-60 flex items-center justify-center gap-2">
                <svg v-if="modalLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Revocar
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import {
  GET_JUNTA_ACTIVA,
  GET_HISTORIAL_JUNTA,
  GET_TIPOS_CARGO,
  CONSTITUIR_JUNTA,
  ASIGNAR_CARGO,
  REVOCAR_CARGO,
} from '@/graphql/queries/administracion.js'

const route = useRoute()
const agrupacionId = route.params.id

// ─── Estado ───────────────────────────────────────────────────────────────────
const agrupacion = ref(null)
const junta = ref(null)
const historial = ref([])
const tiposCargo = ref([])
const miembros = ref([])

const loadingAgrupacion = ref(true)
const loadingJunta = ref(false)
const loadingHistorial = ref(false)

const activeTab = ref('composicion')

// Modales
const modalJunta = ref(false)
const modalCargo = ref(false)
const modalRevocar = ref(false)
const modalLoading = ref(false)
const modalError = ref('')

const formJunta = ref({ nombre: '', fechaConstitucion: new Date().toISOString().slice(0, 10), observaciones: '' })
const formCargo = ref({ tipoCargaId: '', miembroId: '', fechaInicio: new Date().toISOString().slice(0, 10), posicion: 1 })
const formRevocar = ref({ fechaFin: new Date().toISOString().slice(0, 10), motivo: '' })
const cargoRevocar = ref(null)
const busquedaMiembro = ref('')
const miembroSeleccionadoNombre = ref('')

// ─── Computed ─────────────────────────────────────────────────────────────────
const tabs = computed(() => [
  { id: 'composicion', label: 'Composición actual', count: cargosActivos.value.length },
  { id: 'historial', label: 'Historial' },
])

const cargosActivos = computed(() => (junta.value?.cargos || []).filter(c => c.activo))

const cargosOrdenados = computed(() =>
  [...cargosActivos.value].sort((a, b) =>
    (a.tipoCargo.orden - b.tipoCargo.orden) || (a.posicion - b.posicion)
  )
)

const historialOrdenado = computed(() =>
  [...historial.value].sort((a, b) => new Date(b.fechaInicio) - new Date(a.fechaInicio))
)

const tipoCargaSeleccionado = computed(() =>
  tiposCargo.value.find(t => t.id === formCargo.value.tipoCargaId) || null
)

const siguientePosicion = computed(() => {
  if (!tipoCargaSeleccionado.value?.permiteMultiples || !junta.value) return 1
  const posiciones = cargosActivos.value
    .filter(c => c.tipoCargo.id === formCargo.value.tipoCargaId)
    .map(c => c.posicion)
  return posiciones.length ? Math.max(...posiciones) + 1 : 1
})

const miembrosFiltrados = computed(() => {
  if (busquedaMiembro.value.length < 2) return []
  const q = busquedaMiembro.value.toLowerCase()
  return miembros.value
    .filter(m => `${m.nombre} ${m.apellido1} ${m.apellido2 || ''}`.toLowerCase().includes(q))
    .slice(0, 8)
})

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

function nombreCompleto(m) {
  if (!m) return '—'
  return [m.nombre, m.apellido1, m.apellido2].filter(Boolean).join(' ')
}

function iniciales(m) {
  if (!m) return '?'
  return ((m.nombre?.[0] || '') + (m.apellido1?.[0] || '')).toUpperCase()
}

// ─── Data loading ─────────────────────────────────────────────────────────────
async function cargarDatos() {
  loadingAgrupacion.value = true
  try {
    const [juntas, tiposRes, miembrosRes] = await Promise.all([
      graphqlClient.request(GET_JUNTA_ACTIVA, { agrupacionId }),
      graphqlClient.request(GET_TIPOS_CARGO),
      graphqlClient.request(`query { miembros { id nombre apellido1 apellido2 email } }`),
    ])
    junta.value = juntas.juntasDirectivas?.[0] || null
    tiposCargo.value = (tiposRes.tiposCargo || []).sort((a, b) => a.orden - b.orden)
    miembros.value = miembrosRes.miembros || []

    // Inferir agrupacion desde la junta (solo nombre)
    agrupacion.value = { nombre: `Agrupación ${agrupacionId.slice(0, 8)}…`, tipo: '', provincia: null }

    if (junta.value) await cargarHistorial()
  } catch (e) {
    console.error('Error cargando datos de junta:', e)
  } finally {
    loadingAgrupacion.value = false
  }
}

async function cargarHistorial() {
  if (!junta.value) return
  loadingHistorial.value = true
  try {
    const res = await graphqlClient.request(GET_HISTORIAL_JUNTA, { juntaId: junta.value.id })
    historial.value = res.historialCargosJunta || []
  } catch (e) {
    console.error('Error cargando historial:', e)
  } finally {
    loadingHistorial.value = false
  }
}

// ─── Acciones ─────────────────────────────────────────────────────────────────
function abrirModalJunta() {
  formJunta.value = { nombre: '', fechaConstitucion: new Date().toISOString().slice(0, 10), observaciones: '' }
  modalError.value = ''
  modalJunta.value = true
}

function abrirModalCargo() {
  formCargo.value = { tipoCargaId: '', miembroId: '', fechaInicio: new Date().toISOString().slice(0, 10), posicion: 1 }
  busquedaMiembro.value = ''
  miembroSeleccionadoNombre.value = ''
  modalError.value = ''
  modalCargo.value = true
}

function confirmarRevocacion(cargo) {
  cargoRevocar.value = cargo
  formRevocar.value = { fechaFin: new Date().toISOString().slice(0, 10), motivo: '' }
  modalError.value = ''
  modalRevocar.value = true
}

function seleccionarMiembro(m) {
  formCargo.value.miembroId = m.id
  miembroSeleccionadoNombre.value = nombreCompleto(m)
  busquedaMiembro.value = ''
}

async function constituirJunta() {
  if (!formJunta.value.nombre || !formJunta.value.fechaConstitucion) {
    modalError.value = 'Completa los campos obligatorios'
    return
  }
  modalLoading.value = true
  modalError.value = ''
  try {
    await graphqlClient.request(CONSTITUIR_JUNTA, {
      agrupacionId,
      nombre: formJunta.value.nombre,
      fechaConstitucion: formJunta.value.fechaConstitucion,
      observaciones: formJunta.value.observaciones || null,
    })
    modalJunta.value = false
    await cargarDatos()
  } catch (e) {
    modalError.value = e?.response?.errors?.[0]?.message || 'Error al constituir la junta'
  } finally {
    modalLoading.value = false
  }
}

async function asignarCargo() {
  if (!formCargo.value.tipoCargaId || !formCargo.value.miembroId || !formCargo.value.fechaInicio) {
    modalError.value = 'Completa los campos obligatorios'
    return
  }
  const posicion = tipoCargaSeleccionado.value?.permiteMultiples
    ? (formCargo.value.posicion || siguientePosicion.value)
    : 0

  modalLoading.value = true
  modalError.value = ''
  try {
    await graphqlClient.request(ASIGNAR_CARGO, {
      juntaId: junta.value.id,
      miembroId: formCargo.value.miembroId,
      tipoCargaId: formCargo.value.tipoCargaId,
      fechaInicio: formCargo.value.fechaInicio,
      posicion,
    })
    modalCargo.value = false
    await cargarDatos()
  } catch (e) {
    modalError.value = e?.response?.errors?.[0]?.message || 'Error al asignar el cargo'
  } finally {
    modalLoading.value = false
  }
}

async function revocarCargo() {
  if (!formRevocar.value.fechaFin) {
    modalError.value = 'Indica la fecha de fin'
    return
  }
  modalLoading.value = true
  modalError.value = ''
  try {
    await graphqlClient.request(REVOCAR_CARGO, {
      cargoJuntaId: cargoRevocar.value.id,
      fechaFin: formRevocar.value.fechaFin,
      motivo: formRevocar.value.motivo || null,
    })
    modalRevocar.value = false
    await cargarDatos()
  } catch (e) {
    modalError.value = e?.response?.errors?.[0]?.message || 'Error al revocar el cargo'
  } finally {
    modalLoading.value = false
  }
}

watch(activeTab, async (tab) => {
  if (tab === 'historial' && historial.value.length === 0) await cargarHistorial()
})

onMounted(cargarDatos)
</script>
