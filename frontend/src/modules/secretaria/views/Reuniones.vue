<template>
  <AppLayout title="Reuniones" subtitle="Convocatoria y gestión de órganos de gobierno">

    <!-- Barra de herramientas -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
      <div class="flex gap-2 flex-wrap">
        <!-- Filtro año -->
        <select v-model="filtroAnio" @change="cargarReuniones"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option v-for="a in aniosDisponibles" :key="a" :value="a">{{ a }}</option>
        </select>
        <!-- Filtro tipo -->
        <select v-model="filtroTipo" @change="cargarReuniones"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option value="">Todos los tipos</option>
          <option v-for="t in tiposReunion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
        </select>
        <!-- Filtro estado -->
        <select v-model="filtroEstado" @change="cargarReuniones"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option value="">Todos los estados</option>
          <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.etiqueta }}</option>
        </select>
      </div>
      <button v-if="tienePermiso('SEC_REUNION_CREAR')"
        @click="abrirModalConvocar"
        class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
        <PlusIcon class="w-4 h-4" />
        Convocar reunión
      </button>
    </div>

    <!-- Carga -->
    <EstadoCarga v-if="loading" mensaje="Cargando reuniones…" />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <p class="text-red-700 text-sm font-medium">{{ error }}</p>
      <button @click="cargarReuniones" class="text-red-600 text-sm mt-1 hover:underline">Reintentar</button>
    </div>

    <!-- Sin datos -->
    <div v-else-if="reuniones.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <CalendarDaysIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay reuniones en {{ filtroAnio }}</p>
      <p class="text-sm mt-1">Cambia los filtros o convoca una nueva reunión.</p>
    </div>

    <!-- Lista -->
    <div v-else class="space-y-3">
      <div v-for="r in reuniones" :key="r.id"
        class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow transition-shadow">
        <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">

          <!-- Icono de estado -->
          <div :class="estadoColor(r.estado)"
            class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center">
            <component :is="estadoIcono(r.estado)" class="w-5 h-5" />
          </div>

          <!-- Info principal -->
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <span class="font-semibold text-gray-900">{{ nombreTipo(r.tipoReunionId) }}</span>
              <span class="text-sm text-gray-500">nº {{ r.numeroConvocatoria }}/{{ r.anio }}</span>
              <span :class="badgeEstado(r.estado)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ etiquetaEstado(r.estado) }}
              </span>
              <span v-if="r.esTelematica"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                Telemática
              </span>
            </div>

            <div class="flex flex-wrap gap-4 text-sm text-gray-600 mt-1">
              <span class="flex items-center gap-1">
                <CalendarIcon class="w-4 h-4 text-gray-400" />
                Convocatoria: {{ formatFecha(r.fechaConvocatoria) }}
              </span>
              <span v-if="r.fechaCelebracion" class="flex items-center gap-1">
                <ClockIcon class="w-4 h-4 text-gray-400" />
                Celebración: {{ formatFechaHora(r.fechaCelebracion) }}
              </span>
              <span v-if="r.lugar" class="flex items-center gap-1">
                <MapPinIcon class="w-4 h-4 text-gray-400" />
                {{ r.lugar }}
              </span>
            </div>

            <!-- Datos de quórum (si ya se celebró) -->
            <div v-if="r.sociosTotales" class="mt-2 flex gap-4 text-xs text-gray-500">
              <span>Socios: {{ r.sociosTotales }}</span>
              <span>Presentes: {{ r.sociosPresentes }}</span>
              <span v-if="r.sociosRepresentados">Representados: {{ r.sociosRepresentados }}</span>
              <span :class="r.hayQuorum ? 'text-green-600 font-medium' : 'text-red-600 font-medium'">
                {{ r.hayQuorum ? '✓ Quórum' : '✗ Sin quórum' }}
              </span>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex-shrink-0 flex gap-2">
            <!-- Registrar celebración -->
            <button v-if="r.estado === 'CONVOCADA' && tienePermiso('SEC_REUNION_REGISTRAR_ASIST')"
              @click="abrirCelebracion(r)"
              class="text-xs px-3 py-1.5 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 font-medium">
              Registrar celebración
            </button>
            <!-- Crear acta -->
            <button v-if="r.estado === 'CELEBRADA' && tienePermiso('SEC_ACTA_CREAR')"
              @click="crearActa(r)"
              class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 font-medium">
              Redactar acta
            </button>
            <!-- Cancelar -->
            <button v-if="['CONVOCADA'].includes(r.estado) && tienePermiso('SEC_REUNION_CANCELAR')"
              @click="confirmarCancelar(r)"
              class="text-xs px-3 py-1.5 rounded-lg bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 font-medium">
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: Convocar reunión ── -->
    <Teleport to="body">
      <div v-if="modalConvocar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Convocar reunión</h2>
            <button @click="modalConvocar = false" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de reunión *</label>
              <select v-model="formConvocar.tipoReunionId"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option value="">Selecciona un tipo…</option>
                <option v-for="t in tiposReunion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha convocatoria *</label>
                <input type="date" v-model="formConvocar.fechaConvocatoria"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha celebración</label>
                <input type="datetime-local" v-model="formConvocar.fechaCelebracion"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Lugar</label>
              <input type="text" v-model="formConvocar.lugar" placeholder="Sede social, sala de reuniones…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>

            <div class="flex items-center gap-3">
              <input type="checkbox" id="esTelematica" v-model="formConvocar.esTelematica"
                class="w-4 h-4 text-purple-600 rounded" />
              <label for="esTelematica" class="text-sm text-gray-700">Reunión telemática</label>
            </div>

            <div v-if="formConvocar.esTelematica">
              <label class="block text-sm font-medium text-gray-700 mb-1">Plataforma</label>
              <input type="text" v-model="formConvocar.plataformaTelematica" placeholder="Zoom, Teams, Meet…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>

            <div class="flex items-center gap-3">
              <input type="checkbox" id="segundaConv" v-model="formConvocar.tieneSegundaConvocatoria"
                class="w-4 h-4 text-purple-600 rounded" />
              <label for="segundaConv" class="text-sm text-gray-700">Incluir segunda convocatoria</label>
            </div>

            <div v-if="formConvocar.tieneSegundaConvocatoria">
              <label class="block text-sm font-medium text-gray-700 mb-1">Fecha segunda convocatoria</label>
              <input type="datetime-local" v-model="formConvocar.fechaSegundaConvocatoria"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
              <textarea v-model="formConvocar.observaciones" rows="2"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
            </div>

            <p v-if="errorModal" class="text-sm text-red-600">{{ errorModal }}</p>
          </div>

          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalConvocar = false"
              class="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
            <button @click="guardarConvocatoria" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
              {{ guardando ? 'Guardando…' : 'Convocar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Modal: Registrar celebración ── -->
    <Teleport to="body">
      <div v-if="modalCelebracion"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Registrar celebración</h2>
            <button @click="modalCelebracion = false" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <p class="text-sm text-gray-600">
              {{ nombreTipo(reunionActiva?.tipoReunionId) }} nº {{ reunionActiva?.numeroConvocatoria }}/{{ reunionActiva?.anio }}
            </p>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Convocatoria utilizada</label>
              <select v-model="formCelebracion.convocatoriaUtilizada"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option :value="1">Primera convocatoria</option>
                <option :value="2">Segunda convocatoria</option>
              </select>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Total socios</label>
                <input type="number" min="0" v-model.number="formCelebracion.sociosTotales"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Presentes</label>
                <input type="number" min="0" v-model.number="formCelebracion.sociosPresentes"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Representados</label>
                <input type="number" min="0" v-model.number="formCelebracion.sociosRepresentados"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>

            <!-- Preview de quórum -->
            <div v-if="formCelebracion.sociosTotales > 0"
              class="rounded-lg p-3 text-sm"
              :class="quorumPreview.ok ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'">
              Asistencia: {{ quorumPreview.porcentaje }}% ({{ quorumPreview.presentes }} de {{ formCelebracion.sociosTotales }})
              — {{ quorumPreview.ok ? 'Quórum suficiente' : 'Sin quórum' }}
            </div>

            <p v-if="errorModal" class="text-sm text-red-600">{{ errorModal }}</p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalCelebracion = false"
              class="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
            <button @click="guardarCelebracion" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">
              {{ guardando ? 'Guardando…' : 'Registrar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Modal: Confirmar cancelar ── -->
    <Teleport to="body">
      <div v-if="modalCancelar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">¿Cancelar esta reunión?</h2>
          <p class="text-sm text-gray-600">
            {{ nombreTipo(reunionActiva?.tipoReunionId) }} nº {{ reunionActiva?.numeroConvocatoria }}/{{ reunionActiva?.anio }}
          </p>
          <textarea v-model="motivoCancelacion" placeholder="Motivo (opcional)" rows="2"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
          <div class="flex justify-end gap-3">
            <button @click="modalCancelar = false"
              class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
              Volver
            </button>
            <button @click="ejecutarCancelar" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
              {{ guardando ? 'Cancelando…' : 'Sí, cancelar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_TIPOS_REUNION, GET_REUNIONES,
  CONVOCAR_REUNION, REGISTRAR_CELEBRACION, CANCELAR_REUNION,
  CREAR_ACTA_BORRADOR,
} from '@/graphql/queries/secretaria.js'
import {
  CalendarDaysIcon, CalendarIcon, ClockIcon, MapPinIcon,
  PlusIcon, XMarkIcon,
  CheckCircleIcon, ClockIcon as ClockOutlineIcon,
  ExclamationCircleIcon, XCircleIcon,
} from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()

// ── Estado ────────────────────────────────────────────────────────────────────
const loading    = ref(false)
const error      = ref('')
const guardando  = ref(false)
const errorModal = ref('')

const reuniones   = ref([])
const tiposReunion = ref([])

const anioActual = new Date().getFullYear()
const filtroAnio  = ref(anioActual)
const filtroTipo  = ref('')
const filtroEstado = ref('')

const aniosDisponibles = computed(() => {
  const arr = []
  for (let a = anioActual + 1; a >= anioActual - 3; a--) arr.push(a)
  return arr
})

// Modales
const modalConvocar    = ref(false)
const modalCelebracion = ref(false)
const modalCancelar    = ref(false)
const reunionActiva    = ref(null)
const motivoCancelacion = ref('')

const formConvocar = ref({
  tipoReunionId: '', fechaConvocatoria: '', fechaCelebracion: '',
  lugar: '', esTelematica: false, plataformaTelematica: '',
  tieneSegundaConvocatoria: true, fechaSegundaConvocatoria: '',
  observaciones: '',
})

const formCelebracion = ref({
  convocatoriaUtilizada: 1,
  sociosTotales: 0, sociosPresentes: 0, sociosRepresentados: 0,
})

// ── Constantes ────────────────────────────────────────────────────────────────
const ESTADOS = [
  { valor: 'CONVOCADA',      etiqueta: 'Convocada' },
  { valor: 'CELEBRADA',      etiqueta: 'Celebrada' },
  { valor: 'ACTA_BORRADOR',  etiqueta: 'Acta en borrador' },
  { valor: 'ACTA_APROBADA',  etiqueta: 'Acta aprobada' },
  { valor: 'CANCELADA',      etiqueta: 'Cancelada' },
]

// ── Computed ──────────────────────────────────────────────────────────────────
const quorumPreview = computed(() => {
  const total     = formCelebracion.value.sociosTotales || 0
  const presentes = (formCelebracion.value.sociosPresentes || 0) +
                    (formCelebracion.value.sociosRepresentados || 0)
  if (!total) return { porcentaje: 0, presentes: 0, ok: false }
  const pct = Math.round(presentes / total * 100)
  // Umbral aproximado: convocatoria 1 → 50%, convocatoria 2 → cualquiera
  const ok = formCelebracion.value.convocatoriaUtilizada === 2 || pct >= 50
  return { porcentaje: pct, presentes, ok }
})

// ── Helpers ───────────────────────────────────────────────────────────────────
const nombreTipo = (id) =>
  tiposReunion.value.find(t => t.id === id)?.nombre ?? '—'

const formatFecha = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s
  ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
  : '—'

const etiquetaEstado = (e) => ESTADOS.find(s => s.valor === e)?.etiqueta ?? e

const badgeEstado = (e) => ({
  CONVOCADA:     'bg-blue-100 text-blue-700',
  CELEBRADA:     'bg-yellow-100 text-yellow-700',
  ACTA_BORRADOR: 'bg-orange-100 text-orange-700',
  ACTA_APROBADA: 'bg-green-100 text-green-700',
  CANCELADA:     'bg-gray-100 text-gray-500',
}[e] ?? 'bg-gray-100 text-gray-500')

const estadoColor = (e) => ({
  CONVOCADA:     'bg-blue-100 text-blue-600',
  CELEBRADA:     'bg-yellow-100 text-yellow-600',
  ACTA_BORRADOR: 'bg-orange-100 text-orange-600',
  ACTA_APROBADA: 'bg-green-100 text-green-600',
  CANCELADA:     'bg-gray-100 text-gray-400',
}[e] ?? 'bg-gray-100 text-gray-400')

const estadoIcono = (e) => ({
  CONVOCADA:     CalendarIcon,
  CELEBRADA:     CheckCircleIcon,
  ACTA_BORRADOR: ClockOutlineIcon,
  ACTA_APROBADA: CheckCircleIcon,
  CANCELADA:     XCircleIcon,
}[e] ?? CalendarIcon)

// ── Carga de datos ────────────────────────────────────────────────────────────
const cargarTipos = async () => {
  try {
    const data = await executeQuery(GET_TIPOS_REUNION)
    tiposReunion.value = data?.tiposReunion ?? []
  } catch (e) {
    console.error('Error cargando tipos de reunión', e)
  }
}

const cargarReuniones = async () => {
  loading.value = true
  error.value = ''
  try {
    const vars = {
      anio: filtroAnio.value,
      tipoReunionId: filtroTipo.value || undefined,
      estado: filtroEstado.value || undefined,
    }
    const data = await executeQuery(GET_REUNIONES, vars)
    reuniones.value = data?.reuniones ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar reuniones'
  } finally {
    loading.value = false
  }
}

// ── Modal convocar ────────────────────────────────────────────────────────────
const abrirModalConvocar = () => {
  formConvocar.value = {
    tipoReunionId: '', fechaConvocatoria: '', fechaCelebracion: '',
    lugar: '', esTelematica: false, plataformaTelematica: '',
    tieneSegundaConvocatoria: true, fechaSegundaConvocatoria: '',
    observaciones: '',
  }
  errorModal.value = ''
  modalConvocar.value = true
}

const guardarConvocatoria = async () => {
  errorModal.value = ''
  if (!formConvocar.value.tipoReunionId) {
    errorModal.value = 'Selecciona el tipo de reunión'
    return
  }
  if (!formConvocar.value.fechaConvocatoria) {
    errorModal.value = 'Indica la fecha de convocatoria'
    return
  }
  guardando.value = true
  try {
    const input = {
      tipoReunionId: formConvocar.value.tipoReunionId,
      fechaConvocatoria: formConvocar.value.fechaConvocatoria,
      fechaCelebracion: formConvocar.value.fechaCelebracion || null,
      lugar: formConvocar.value.lugar || null,
      esTelematica: formConvocar.value.esTelematica,
      plataformaTelematica: formConvocar.value.plataformaTelematica || null,
      tieneSegundaConvocatoria: formConvocar.value.tieneSegundaConvocatoria,
      fechaSegundaConvocatoria: formConvocar.value.fechaSegundaConvocatoria || null,
      observaciones: formConvocar.value.observaciones || null,
    }
    await executeMutation(CONVOCAR_REUNION, { data: input })
    modalConvocar.value = false
    await cargarReuniones()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al convocar reunión'
  } finally {
    guardando.value = false
  }
}

// ── Modal celebración ─────────────────────────────────────────────────────────
const abrirCelebracion = (reunion) => {
  reunionActiva.value = reunion
  formCelebracion.value = {
    convocatoriaUtilizada: 1,
    sociosTotales: 0, sociosPresentes: 0, sociosRepresentados: 0,
  }
  errorModal.value = ''
  modalCelebracion.value = true
}

const guardarCelebracion = async () => {
  errorModal.value = ''
  if (!formCelebracion.value.sociosTotales) {
    errorModal.value = 'Indica el número total de socios'
    return
  }
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_CELEBRACION, {
      data: {
        reunionId: reunionActiva.value.id,
        ...formCelebracion.value,
      },
    })
    modalCelebracion.value = false
    await cargarReuniones()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al registrar celebración'
  } finally {
    guardando.value = false
  }
}

// ── Crear acta ────────────────────────────────────────────────────────────────
const crearActa = async (reunion) => {
  try {
    await executeMutation(CREAR_ACTA_BORRADOR, {
      data: { reunionId: reunion.id },
    })
    await cargarReuniones()
  } catch (e) {
    alert(e.message ?? 'Error al crear el acta')
  }
}

// ── Cancelar reunión ──────────────────────────────────────────────────────────
const confirmarCancelar = (reunion) => {
  reunionActiva.value = reunion
  motivoCancelacion.value = ''
  modalCancelar.value = true
}

const ejecutarCancelar = async () => {
  guardando.value = true
  try {
    await executeMutation(CANCELAR_REUNION, {
      reunionId: reunionActiva.value.id,
      motivo: motivoCancelacion.value || null,
    })
    modalCancelar.value = false
    await cargarReuniones()
  } catch (e) {
    alert(e.message ?? 'Error al cancelar reunión')
  } finally {
    guardando.value = false
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await cargarTipos()
  await cargarReuniones()
})
</script>
