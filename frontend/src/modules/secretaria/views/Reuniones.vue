<template>
  <AppLayout title="Reuniones" subtitle="Convocatoria y gestión de órganos de gobierno">

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
      <div class="flex gap-2 flex-wrap">
        <select v-model="filtroAnio" @change="cargar"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option v-for="a in aniosDisponibles" :key="a" :value="a">{{ a }}</option>
        </select>
        <select v-model="filtroTipo" @change="cargar"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option value="">Todos los tipos</option>
          <option v-for="t in tiposReunion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
        </select>
        <select v-model="filtroEstado" @change="cargar"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option value="">Todos los estados</option>
          <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.etiqueta }}</option>
        </select>
      </div>
      <button v-if="tienePermiso('SEC_REUNION_CREAR')" @click="abrirConvocar"
        class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
        <PlusIcon class="w-4 h-4" /> Convocar reunión
      </button>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando reuniones…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="reuniones.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <CalendarDaysIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay reuniones en {{ filtroAnio }}</p>
      <p class="text-sm mt-1">Cambia los filtros o convoca una nueva reunión.</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="r in reuniones" :key="r.id"
        class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow transition-shadow">
        <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">

          <div :class="estadoColor(r.estadoCodigo)"
            class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center">
            <component :is="estadoIcono(r.estadoCodigo)" class="w-5 h-5" />
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <span class="font-semibold text-gray-900">{{ nombreTipo(r.tipoReunionId) }}</span>
              <span class="text-sm text-gray-400">nº {{ r.numeroConvocatoria }}/{{ r.anio }}</span>
              <span :class="badgeEstado(r.estadoCodigo)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ etiquetaEstado(r.estadoCodigo) }}
              </span>
              <span v-if="r.esTelematica"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                Telemática
              </span>
            </div>
            <div class="flex flex-wrap gap-4 text-sm text-gray-500 mt-1">
              <span class="flex items-center gap-1">
                <CalendarIcon class="w-4 h-4" /> {{ formatFecha(r.fechaConvocatoria) }}
              </span>
              <span v-if="r.fechaCelebracion" class="flex items-center gap-1">
                <ClockIcon class="w-4 h-4" /> {{ formatFechaHora(r.fechaCelebracion) }}
              </span>
              <span v-if="r.lugar" class="flex items-center gap-1">
                <MapPinIcon class="w-4 h-4" /> {{ r.lugar }}
              </span>
            </div>
            <div v-if="r.sociosTotales" class="mt-2 flex flex-wrap gap-4 text-xs">
              <span class="text-gray-500">Total: {{ r.sociosTotales }}</span>
              <span class="text-gray-500">Presentes: {{ r.sociosPresentes }}</span>
              <span v-if="r.sociosRepresentados" class="text-gray-500">Representados: {{ r.sociosRepresentados }}</span>
              <span :class="r.hayQuorum ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'">
                {{ r.hayQuorum ? '✓ Quórum' : '✗ Sin quórum' }}
              </span>
            </div>
          </div>

          <div class="flex-shrink-0 flex items-center gap-2">
            <button v-if="r.estadoCodigo === 'CONVOCADA' && tienePermiso('SEC_REUNION_REGISTRAR_ASIST')"
              @click="abrirCelebracion(r)"
              class="text-xs px-3 py-1.5 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 font-medium transition-colors">
              Celebración
            </button>
            <button v-if="r.estadoCodigo === 'CELEBRADA' && tienePermiso('SEC_ACTA_CREAR')"
              @click="crearActa(r)"
              class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 font-medium transition-colors">
              Redactar acta
            </button>
            <RowActions
              v-if="r.estadoCodigo === 'CONVOCADA' && tienePermiso('SEC_REUNION_CANCELAR')"
              :show-view="false" :show-edit="false" :show-delete="true"
              confirm-title="¿Cancelar esta reunión?"
              confirm-title-soft="¿Cancelar esta reunión?"
              :confirm-text="`${nombreTipo(r.tipoReunionId)} nº ${r.numeroConvocatoria}/${r.anio} quedará cancelada.`"
              @delete="ejecutarCancelar(r)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: Convocar ── -->
    <Teleport to="body">
      <div v-if="modalConvocar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalConvocar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Convocar reunión</h2>
            <button @click="modalConvocar = false"
              class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Tipo de reunión <span class="text-red-500">*</span>
              </label>
              <select v-model="form.tipoReunionId"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">Selecciona un tipo…</option>
                <option v-for="t in tiposReunion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Fecha convocatoria <span class="text-red-500">*</span>
                </label>
                <input type="date" v-model="form.fechaConvocatoria"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha celebración</label>
                <input type="datetime-local" v-model="form.fechaCelebracion"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Lugar</label>
              <input type="text" v-model="form.lugar" placeholder="Sede social, sala de reuniones…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <label class="flex items-center gap-3 cursor-pointer select-none">
              <input type="checkbox" v-model="form.esTelematica"
                class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              <span class="text-sm text-gray-700">Reunión telemática</span>
            </label>
            <div v-if="form.esTelematica">
              <label class="block text-sm font-medium text-gray-700 mb-1">Plataforma</label>
              <input type="text" v-model="form.plataformaTelematica" placeholder="Zoom, Teams, Meet…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <label class="flex items-center gap-3 cursor-pointer select-none">
              <input type="checkbox" v-model="form.tieneSegundaConvocatoria"
                class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              <span class="text-sm text-gray-700">Incluir segunda convocatoria</span>
            </label>
            <div v-if="form.tieneSegundaConvocatoria">
              <label class="block text-sm font-medium text-gray-700 mb-1">Fecha segunda convocatoria</label>
              <input type="datetime-local" v-model="form.fechaSegundaConvocatoria"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
              <textarea v-model="form.observaciones" rows="2"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalConvocar = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
            <button @click="guardarConvocatoria" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Guardando…' : 'Convocar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Modal: Celebración ── -->
    <Teleport to="body">
      <div v-if="modalCelebracion"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalCelebracion = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Registrar celebración</h2>
              <p class="text-xs text-gray-500 mt-0.5">
                {{ nombreTipo(reunionActiva?.tipoReunionId) }} · nº {{ reunionActiva?.numeroConvocatoria }}/{{ reunionActiva?.anio }}
              </p>
            </div>
            <button @click="modalCelebracion = false"
              class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Convocatoria utilizada</label>
              <select v-model="formCeleb.convocatoriaUtilizada"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option :value="1">Primera convocatoria</option>
                <option :value="2">Segunda convocatoria</option>
              </select>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Total socios <span class="text-red-500">*</span></label>
                <input type="number" min="0" v-model.number="formCeleb.sociosTotales"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Presentes</label>
                <input type="number" min="0" v-model.number="formCeleb.sociosPresentes"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Representados</label>
                <input type="number" min="0" v-model.number="formCeleb.sociosRepresentados"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>
            <div v-if="formCeleb.sociosTotales > 0"
              class="rounded-lg p-3 text-sm font-medium text-center border"
              :class="quorumPreview.ok
                ? 'bg-green-50 text-green-700 border-green-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'">
              {{ quorumPreview.porcentaje }}% de asistencia ·
              {{ quorumPreview.ok ? '✓ Quórum suficiente' : '✗ Sin quórum' }}
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalCelebracion = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
            <button @click="guardarCelebracion" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Guardando…' : 'Registrar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast de error para acciones rápidas -->
    <Teleport to="body">
      <div v-if="errorInline"
        class="fixed bottom-4 right-4 z-50 bg-red-600 text-white text-sm px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 max-w-sm">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0" />
        <span>{{ errorInline }}</span>
        <button @click="errorInline = ''" class="ml-auto text-white/80 hover:text-white">
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
import RowActions from '@/components/common/RowActions.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_TIPOS_REUNION, GET_REUNIONES,
  CONVOCAR_REUNION, REGISTRAR_CELEBRACION, CANCELAR_REUNION, CREAR_ACTA_BORRADOR,
} from '@/graphql/queries/secretaria.js'
import {
  CalendarDaysIcon, CalendarIcon, ClockIcon, MapPinIcon, PlusIcon, XMarkIcon,
  CheckCircleIcon, XCircleIcon,
} from '@heroicons/vue/24/outline'
import { ClockIcon as ClockOutlineIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()

const loading   = ref(false)
const error     = ref('')
const guardando = ref(false)
const errorModal = ref('')
const errorInline = ref('')
const reuniones   = ref([])
const tiposReunion = ref([])
const reunionActiva = ref(null)

const anioActual = new Date().getFullYear()
const filtroAnio   = ref(anioActual)
const filtroTipo   = ref('')
const filtroEstado = ref('')
const aniosDisponibles = computed(() => {
  const r = []
  for (let a = anioActual + 1; a >= anioActual - 3; a--) r.push(a)
  return r
})

const modalConvocar    = ref(false)
const modalCelebracion = ref(false)

const form = ref({
  tipoReunionId: '', fechaConvocatoria: '', fechaCelebracion: '',
  lugar: '', esTelematica: false, plataformaTelematica: '',
  tieneSegundaConvocatoria: true, fechaSegundaConvocatoria: '',
  observaciones: '',
})
const formCeleb = ref({ convocatoriaUtilizada: 1, sociosTotales: 0, sociosPresentes: 0, sociosRepresentados: 0 })

const ESTADOS = [
  { valor: 'CONVOCADA',      etiqueta: 'Convocada' },
  { valor: 'CELEBRADA',      etiqueta: 'Celebrada' },
  { valor: 'ACTA_BORRADOR',  etiqueta: 'Acta en borrador' },
  { valor: 'ACTA_APROBADA',  etiqueta: 'Acta aprobada' },
  { valor: 'CANCELADA',      etiqueta: 'Cancelada' },
]

const quorumPreview = computed(() => {
  const total     = formCeleb.value.sociosTotales || 0
  const presentes = (formCeleb.value.sociosPresentes || 0) + (formCeleb.value.sociosRepresentados || 0)
  if (!total) return { porcentaje: 0, ok: false }
  const pct = Math.round(presentes / total * 100)
  const ok  = formCeleb.value.convocatoriaUtilizada === 2 || pct >= 50
  return { porcentaje: pct, ok }
})

const nombreTipo    = (id) => tiposReunion.value.find(t => t.id === id)?.nombre ?? '—'
const formatFecha   = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : '—'
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

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const [dataTipos, dataReuniones] = await Promise.all([
      tiposReunion.value.length ? null : executeQuery(GET_TIPOS_REUNION),
      executeQuery(GET_REUNIONES, {
        anio: filtroAnio.value,
        tipoReunionId: filtroTipo.value || undefined,
        estado: filtroEstado.value || undefined,
      }),
    ])
    if (dataTipos) tiposReunion.value = dataTipos.tiposReunion ?? []
    reuniones.value = dataReuniones.reuniones ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar reuniones'
  } finally {
    loading.value = false
  }
}

const abrirConvocar = () => {
  form.value = {
    tipoReunionId: '', fechaConvocatoria: '', fechaCelebracion: '',
    lugar: '', esTelematica: false, plataformaTelematica: '',
    tieneSegundaConvocatoria: true, fechaSegundaConvocatoria: '', observaciones: '',
  }
  errorModal.value = ''
  modalConvocar.value = true
}

const guardarConvocatoria = async () => {
  errorModal.value = ''
  if (!form.value.tipoReunionId)       { errorModal.value = 'Selecciona el tipo de reunión'; return }
  if (!form.value.fechaConvocatoria)   { errorModal.value = 'Indica la fecha de convocatoria'; return }
  guardando.value = true
  try {
    await executeMutation(CONVOCAR_REUNION, {
      data: {
        tipoReunionId: form.value.tipoReunionId,
        fechaConvocatoria: form.value.fechaConvocatoria,
        fechaCelebracion: form.value.fechaCelebracion || null,
        lugar: form.value.lugar || null,
        esTelematica: form.value.esTelematica,
        plataformaTelematica: form.value.plataformaTelematica || null,
        tieneSegundaConvocatoria: form.value.tieneSegundaConvocatoria,
        fechaSegundaConvocatoria: form.value.fechaSegundaConvocatoria || null,
        observaciones: form.value.observaciones || null,
      },
    })
    modalConvocar.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al convocar la reunión'
  } finally {
    guardando.value = false
  }
}

const abrirCelebracion = (r) => {
  reunionActiva.value = r
  formCeleb.value = { convocatoriaUtilizada: 1, sociosTotales: 0, sociosPresentes: 0, sociosRepresentados: 0 }
  errorModal.value = ''
  modalCelebracion.value = true
}

const guardarCelebracion = async () => {
  errorModal.value = ''
  if (!formCeleb.value.sociosTotales) { errorModal.value = 'Indica el total de socios'; return }
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_CELEBRACION, {
      data: { reunionId: reunionActiva.value.id, ...formCeleb.value },
    })
    modalCelebracion.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al registrar la celebración'
  } finally {
    guardando.value = false
  }
}

const crearActa = async (r) => {
  try {
    await executeMutation(CREAR_ACTA_BORRADOR, { data: { reunionId: r.id } })
    await cargar()
  } catch (e) {
    errorInline.value = e.message ?? 'Error al crear el acta'
    setTimeout(() => errorInline.value = '', 5000)
  }
}

const ejecutarCancelar = async (r) => {
  try {
    await executeMutation(CANCELAR_REUNION, { reunionId: r.id })
    await cargar()
  } catch (e) {
    errorInline.value = e.message ?? 'Error al cancelar la reunión'
    setTimeout(() => errorInline.value = '', 5000)
  }
}

onMounted(cargar)
</script>
