<template>
  <AppLayout :title="agrupacion ? `${orgConfig.OrganoGobierno}: ${agrupacion.nombre}` : orgConfig.OrganoGobierno" :subtitle="`Gestión del ${orgConfig.organoGobierno} y cargos`">

    <DetailHeader fallback="/agrupaciones" />

    <div v-if="loadingAgrupacion" class="text-center py-16">
      <EstadoCarga />
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 class="text-xl font-bold text-gray-900">{{ agrupacion?.nombre }}</h2>
          <p class="text-sm text-gray-500 mt-0.5">{{ agrupacion?.tipo }} · {{ agrupacion?.provincia?.nombre }}</p>
        </div>
        <button @click="abrirDrawerJunta"
          class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition shadow-sm">
          <PlusIcon class="w-4 h-4" />
          Constituir {{ orgConfig.organoGobierno }}
        </button>
      </div>

      <!-- Sin junta -->
      <div v-if="!junta && !loadingJunta" class="text-center py-16 bg-white rounded-xl border border-dashed border-gray-300">
        <UsersIcon class="w-12 h-12 mx-auto text-gray-300 mb-3" />
        <p class="text-gray-500 font-medium">Esta agrupación no tiene {{ orgConfig.organoGobierno }} activo</p>
        <p class="text-sm text-gray-400 mt-1">Usa el botón superior para constituirla</p>
      </div>

      <!-- Junta activa -->
      <template v-else-if="junta">
        <!-- Tabs -->
        <div class="border-b border-gray-200 mb-6">
          <nav class="-mb-px flex gap-6">
            <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
              class="pb-3 text-sm font-medium border-b-2 transition-colors"
              :class="activeTab === tab.id ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'">
              {{ tab.label }}
              <span v-if="tab.count !== undefined" class="ml-2 px-2 py-0.5 rounded-full text-xs"
                :class="activeTab === tab.id ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'">
                {{ tab.count }}
              </span>
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
            <button @click="abrirDrawerCargo"
              class="inline-flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 text-sm font-medium rounded-lg hover:bg-gray-50 transition shadow-sm">
              <PlusIcon class="w-4 h-4 text-gray-500" />
              Asignar cargo
            </button>
          </div>

          <div v-if="cargosActivos.length === 0" class="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <p class="text-gray-500 text-sm">No hay cargos asignados</p>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="cargo in cargosOrdenados" :key="cargo.id"
              class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col gap-3 hover:shadow-md transition-shadow">

              <div class="flex items-start justify-between">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {{ cargo.tipoCargo.nombre }}
                  <span v-if="cargo.tipoCargo.permiteMultiples" class="ml-1 text-purple-500">#{{ cargo.posicion }}</span>
                </span>

                <!-- ConfirmPopover para revocar — sin modal -->
                <ConfirmPopover
                  titulo="Revocar cargo"
                  :mensaje="`¿Revocar ${cargo.tipoCargo.nombre} a ${nombreCompleto(cargo.miembro)}?`"
                  variante="peligro"
                  etiqueta-confirmar="Revocar"
                  posicion="top"
                  :cargando="revocandoId === cargo.id"
                  @confirm="revocarCargo(cargo)"
                >
                  <template #default="{ open }">
                    <button @click="open" class="text-gray-300 hover:text-red-500 transition-colors" title="Revocar cargo">
                      <XMarkIcon class="w-4 h-4" />
                    </button>
                  </template>
                </ConfirmPopover>
              </div>

              <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center shrink-0">
                  <span class="text-white text-sm font-semibold">{{ iniciales(cargo.miembro) }}</span>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-900 truncate">{{ nombreCompleto(cargo.miembro) }}</p>
                  <p class="text-xs text-gray-500 truncate">{{ cargo.miembro.email || '—' }}</p>
                </div>
              </div>

              <div class="text-xs text-gray-400">Desde {{ formatDate(cargo.fechaInicio) }}</div>
            </div>
          </div>
        </div>

        <!-- Tab: Historial -->
        <div v-show="activeTab === 'historial'">
          <EstadoCarga v-if="loadingHistorial" />
          <div v-else-if="historial.length === 0" class="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <p class="text-gray-500 text-sm">No hay registros históricos</p>
          </div>
          <div v-else class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-100">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cargo</th>
                  <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{{ orgConfig.Miembro }}</th>
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
            </table></div>
          </div>
        </div>
      </template>
    </template>

    <!-- ── DRAWER: Constituir junta ──────────────────────────────────────── -->
    <AppDrawer
      v-model="drawerJunta"
      :title="`Constituir ${orgConfig.organoGobierno}`"
      subtitle="Los datos del órgano actual quedarán como histórico"
      size="sm"
      @close="drawerJunta = false"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre <span class="text-red-500">*</span></label>
          <input v-model="formJunta.nombre" type="text" :placeholder="`Ej: ${orgConfig.OrganoGobierno} 2025-2027`"
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
          {{ orgConfig.OrganoGobierno }} actual <strong>{{ junta.nombre }}</strong> quedará desactivado.
        </div>
        <ErrorAlert v-if="errorJunta" :message="errorJunta" />
      </div>

      <template #footer>
        <button @click="drawerJunta = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="constituirJunta" :disabled="guardandoJunta"
          class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-60 flex items-center gap-2">
          <span v-if="guardandoJunta" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"/>
          Constituir
        </button>
      </template>
    </AppDrawer>

    <!-- ── DRAWER: Asignar cargo ─────────────────────────────────────────── -->
    <AppDrawer
      v-model="drawerCargo"
      title="Asignar cargo"
      size="sm"
      @close="drawerCargo = false"
    >
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
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ orgConfig.Miembro }} <span class="text-red-500">*</span></label>
          <select v-model="formCargo.miembroId"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
            <option value="">Seleccionar {{ orgConfig.miembro }} activo…</option>
            <option v-for="m in miembros" :key="m.id" :value="m.id">
              {{ nombreCompleto(m) }}{{ m.email ? ` · ${m.email}` : '' }}
            </option>
          </select>
          <p v-if="!miembros.length" class="mt-1 text-xs text-gray-400">
            No hay {{ orgConfig.miembros }} activos en esta agrupación.
          </p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de inicio <span class="text-red-500">*</span></label>
          <input v-model="formCargo.fechaInicio" type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"/>
        </div>
        <ErrorAlert v-if="errorCargo" :message="errorCargo" />
      </div>

      <template #footer>
        <button @click="drawerCargo = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="asignarCargo" :disabled="guardandoCargo"
          class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-60 flex items-center gap-2">
          <span v-if="guardandoCargo" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"/>
          Asignar
        </button>
      </template>
    </AppDrawer>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { XMarkIcon, PlusIcon, UsersIcon } from '@heroicons/vue/24/outline'
import AppLayout      from '@/components/common/AppLayout.vue'
import DetailHeader   from '@/components/common/DetailHeader.vue'
import EstadoCarga    from '@/components/common/EstadoCarga.vue'
import ErrorAlert     from '@/components/common/ErrorAlert.vue'
import AppDrawer      from '@/components/common/AppDrawer.vue'
import ConfirmPopover from '@/components/common/ConfirmPopover.vue'
import { useToast }   from '@/composables/useToast'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import {
  GET_JUNTA_ACTIVA, GET_HISTORIAL_JUNTA, GET_TIPOS_CARGO,
  CONSTITUIR_JUNTA, ASIGNAR_CARGO, REVOCAR_CARGO,
} from '@/graphql/queries/administracion.js'

const route = useRoute()
const agrupacionId = route.params.id
const orgConfig = useOrgConfigStore()
const toast = useToast()

// ─── Estado ───────────────────────────────────────────────────────────────────
const agrupacion      = ref(null)
const junta           = ref(null)
const historial       = ref([])
const tiposCargo      = ref([])
const miembros        = ref([])
const activeTab       = ref('composicion')

const loadingAgrupacion = ref(true)
const loadingJunta      = ref(false)
const loadingHistorial  = ref(false)

// Drawers (reemplazan los modales inline)
const drawerJunta    = ref(false)
const drawerCargo    = ref(false)
const guardandoJunta = ref(false)
const guardandoCargo = ref(false)
const errorJunta     = ref('')
const errorCargo     = ref('')
const revocandoId    = ref(null)

const formJunta   = ref({ nombre: '', fechaConstitucion: new Date().toISOString().slice(0, 10), observaciones: '' })
const formCargo   = ref({ tipoCargaId: '', miembroId: '', fechaInicio: new Date().toISOString().slice(0, 10), posicion: 1 })
const busquedaMiembro           = ref('')
const miembroSeleccionadoNombre = ref('')

// ─── Computed ─────────────────────────────────────────────────────────────────
const tabs = computed(() => [
  { id: 'composicion', label: 'Composición actual', count: cargosActivos.value.length },
  { id: 'historial',   label: 'Historial' },
])
const cargosActivos  = computed(() => (junta.value?.cargos || []).filter(c => c.activo))
const cargosOrdenados = computed(() =>
  [...cargosActivos.value].sort((a, b) => (a.tipoCargo.orden - b.tipoCargo.orden) || (a.posicion - b.posicion))
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
      graphqlClient.request(
        `query($agrupacionId: UUID!) { miembros: socios(agrupacionId: $agrupacionId, activo: true) { id nombre apellido1 apellido2 email } }`,
        { agrupacionId },
      ),
    ])
    junta.value      = juntas.juntasDirectivas?.[0] || null
    tiposCargo.value = (tiposRes.tiposCargo || []).sort((a, b) => a.orden - b.orden)
    miembros.value   = miembrosRes.miembros || []
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
function abrirDrawerJunta() {
  formJunta.value = { nombre: '', fechaConstitucion: new Date().toISOString().slice(0, 10), observaciones: '' }
  errorJunta.value = ''
  drawerJunta.value = true
}

function abrirDrawerCargo() {
  formCargo.value = { tipoCargaId: '', miembroId: '', fechaInicio: new Date().toISOString().slice(0, 10), posicion: 1 }
  busquedaMiembro.value = ''
  miembroSeleccionadoNombre.value = ''
  errorCargo.value = ''
  drawerCargo.value = true
}

function seleccionarMiembro(m) {
  formCargo.value.miembroId = m.id
  miembroSeleccionadoNombre.value = nombreCompleto(m)
  busquedaMiembro.value = ''
}

async function constituirJunta() {
  if (!formJunta.value.nombre || !formJunta.value.fechaConstitucion) {
    errorJunta.value = 'Completa los campos obligatorios'
    return
  }
  guardandoJunta.value = true
  errorJunta.value = ''
  try {
    await graphqlClient.request(CONSTITUIR_JUNTA, {
      agrupacionId,
      nombre: formJunta.value.nombre,
      fechaConstitucion: formJunta.value.fechaConstitucion,
      observaciones: formJunta.value.observaciones || null,
    })
    drawerJunta.value = false
    toast.success(`${orgConfig.OrganoGobierno} constituido correctamente`)
    await cargarDatos()
  } catch (e) {
    errorJunta.value = e?.response?.errors?.[0]?.message || 'Error al constituir la junta'
  } finally {
    guardandoJunta.value = false
  }
}

async function asignarCargo() {
  if (!formCargo.value.tipoCargaId || !formCargo.value.miembroId || !formCargo.value.fechaInicio) {
    errorCargo.value = 'Completa los campos obligatorios'
    return
  }
  const posicion = tipoCargaSeleccionado.value?.permiteMultiples
    ? (formCargo.value.posicion || siguientePosicion.value) : 0
  guardandoCargo.value = true
  errorCargo.value = ''
  try {
    await graphqlClient.request(ASIGNAR_CARGO, {
      juntaId: junta.value.id,
      miembroId: formCargo.value.miembroId,
      tipoCargaId: formCargo.value.tipoCargaId,
      fechaInicio: formCargo.value.fechaInicio,
      posicion,
    })
    drawerCargo.value = false
    toast.success('Cargo asignado correctamente')
    await cargarDatos()
  } catch (e) {
    errorCargo.value = e?.response?.errors?.[0]?.message || 'Error al asignar el cargo'
  } finally {
    guardandoCargo.value = false
  }
}

async function revocarCargo(cargo) {
  revocandoId.value = cargo.id
  try {
    await graphqlClient.request(REVOCAR_CARGO, {
      cargoJuntaId: cargo.id,
      fechaFin: new Date().toISOString().slice(0, 10),
      motivo: null,
    })
    toast.success(`Cargo de ${cargo.tipoCargo.nombre} revocado`)
    await cargarDatos()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error al revocar el cargo')
  } finally {
    revocandoId.value = null
  }
}

watch(activeTab, async (tab) => {
  if (tab === 'historial' && historial.value.length === 0) await cargarHistorial()
})

onMounted(cargarDatos)
</script>
