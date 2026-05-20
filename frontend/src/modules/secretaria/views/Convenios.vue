<template>
  <AppLayout title="Convenios y Delegaciones" subtitle="Acuerdos institucionales y poderes de representación">

    <TabsNavigation
      :tabs="TABS"
      :active-tab="tabActiva"
      class="mb-6"
      @tab-change="tabActiva = $event"
    />

    <!-- ── Tab: Convenios ── -->
    <template v-if="tabActiva === 'convenios'">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
        <select v-model="filtroEstadoConvenio" @change="cargarConvenios"
          class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
          <option value="">Todos los estados</option>
          <option value="VIGENTE">Vigente</option>
          <option value="VENCIDO">Vencido</option>
          <option value="RESCINDIDO">Rescindido</option>
          <option value="SUSPENDIDO">Suspendido</option>
        </select>
        <button v-if="tienePermiso('SEC_CONVENIO_CREAR')" @click="abrirModalConvenio"
          class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
          <PlusIcon class="w-4 h-4" /> Registrar convenio
        </button>
      </div>

      <EstadoCarga v-if="loadingConvenios" mensaje="Cargando convenios…" />

      <div v-else-if="convenios.length === 0"
        class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
        <DocumentCheckIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p class="font-medium text-gray-700">No hay convenios registrados</p>
        <p class="text-sm mt-1">Registra el primer convenio con el botón de arriba.</p>
      </div>

      <div v-else class="space-y-3">
        <div v-for="c in convenios" :key="c.id"
          class="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <span class="font-semibold text-gray-900">{{ c.titulo }}</span>
                <span :class="badgeConvenio(c.estado)"
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ c.estado }}
                </span>
              </div>
              <p class="text-sm text-gray-600">
                {{ c.entidadContraparte }}
                <span v-if="c.cifContraparte" class="text-gray-400"> · {{ c.cifContraparte }}</span>
              </p>
              <div class="flex flex-wrap gap-4 text-xs text-gray-400 mt-2">
                <span>Ref: {{ c.referencia }}</span>
                <span>Firma: {{ formatFecha(c.fechaFirma) }}</span>
                <span>Inicio: {{ formatFecha(c.fechaInicio) }}</span>
                <span v-if="c.fechaFin">Fin: {{ formatFecha(c.fechaFin) }}</span>
                <span v-if="c.renovacionAutomatica" class="text-blue-500">↻ Renovación automática</span>
              </div>
            </div>
            <div v-if="tienePermiso('SEC_CONVENIO_EDITAR') && c.estado === 'VIGENTE'"
              class="flex-shrink-0">
              <select @change="cambiarEstado(c, $event.target.value)"
                class="text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white">
                <option value="">Cambiar estado…</option>
                <option value="VENCIDO">Marcar vencido</option>
                <option value="RESCINDIDO">Rescindir</option>
                <option value="SUSPENDIDO">Suspender</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Tab: Delegaciones ── -->
    <template v-if="tabActiva === 'delegaciones'">
      <div class="flex justify-end mb-4">
        <button v-if="tienePermiso('SEC_DELEGACION_GESTIONAR')" @click="modalDelegacion = true"
          class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
          <PlusIcon class="w-4 h-4" /> Nueva delegación
        </button>
      </div>

      <EstadoCarga v-if="loadingDelegaciones" mensaje="Cargando delegaciones…" />

      <div v-else-if="delegaciones.length === 0"
        class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
        <UserGroupIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p class="font-medium text-gray-700">No hay delegaciones registradas</p>
      </div>

      <div v-else class="space-y-3">
        <div v-for="d in delegaciones" :key="d.id"
          class="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div class="p-5 flex flex-col sm:flex-row sm:items-start gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-2">
                <span :class="d.activa ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ d.activa ? 'Activa' : 'Revocada' }}
                </span>
              </div>
              <p class="text-sm text-gray-800 leading-relaxed">{{ d.descripcionActos }}</p>
              <div class="flex flex-wrap gap-4 text-xs text-gray-400 mt-2">
                <span>Desde: {{ formatFecha(d.fechaInicio) }}</span>
                <span v-if="d.fechaFin">Hasta: {{ formatFecha(d.fechaFin) }}</span>
                <span v-if="d.limiteImporte">Límite: {{ formatImporte(d.limiteImporte) }} €</span>
              </div>
            </div>
            <RowActions
              v-if="d.activa && tienePermiso('SEC_DELEGACION_GESTIONAR')"
              :show-view="false" :show-edit="false" :show-delete="true"
              confirm-title="¿Revocar esta delegación?"
              confirm-title-soft="¿Revocar esta delegación?"
              confirm-text="La delegación quedará inactiva y no podrá utilizarse."
              @delete="revocarDelegacion(d)"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- ── Modal: Registrar convenio ── -->
    <Teleport to="body">
      <div v-if="modalConvenio"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalConvenio = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Registrar convenio</h2>
            <button @click="modalConvenio = false" class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo <span class="text-red-500">*</span></label>
              <select v-model="formConvenio.tipoConvenioId"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">Selecciona…</option>
                <option v-for="t in tiposConvenio" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Título <span class="text-red-500">*</span></label>
              <input type="text" v-model="formConvenio.titulo"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Entidad contraparte <span class="text-red-500">*</span></label>
              <input type="text" v-model="formConvenio.entidadContraparte"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">CIF contraparte</label>
                <input type="text" v-model="formConvenio.cifContraparte"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha firma <span class="text-red-500">*</span></label>
                <input type="date" v-model="formConvenio.fechaFirma"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha inicio <span class="text-red-500">*</span></label>
                <input type="date" v-model="formConvenio.fechaInicio"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha fin</label>
                <input type="date" v-model="formConvenio.fechaFin"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>
            <label class="flex items-center gap-3 cursor-pointer select-none">
              <input type="checkbox" v-model="formConvenio.renovacionAutomatica"
                class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              <span class="text-sm text-gray-700">Renovación automática</span>
            </label>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Objeto del convenio</label>
              <textarea v-model="formConvenio.objeto" rows="3"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalConvenio = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button @click="guardarConvenio" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Guardando…' : 'Registrar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import TabsNavigation from '@/components/common/TabsNavigation.vue'
import RowActions from '@/components/common/RowActions.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_TIPOS_CONVENIO, GET_CONVENIOS, REGISTRAR_CONVENIO, CAMBIAR_ESTADO_CONVENIO,
  GET_DELEGACIONES, REVOCAR_DELEGACION,
} from '@/graphql/queries/secretaria.js'
import { PlusIcon, XMarkIcon, DocumentCheckIcon, UserGroupIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()

const TABS = [
  { id: 'convenios',    name: 'Convenios',           icon: '📄' },
  { id: 'delegaciones', name: 'Delegaciones de firma', icon: '🤝' },
]
const tabActiva = ref('convenios')

const loadingConvenios    = ref(false)
const loadingDelegaciones = ref(false)
const guardando  = ref(false)
const errorModal = ref('')

const convenios     = ref([])
const tiposConvenio = ref([])
const delegaciones  = ref([])

const filtroEstadoConvenio = ref('VIGENTE')
const modalConvenio  = ref(false)
const modalDelegacion = ref(false)

const formConvenio = ref({
  tipoConvenioId: '', titulo: '', entidadContraparte: '', cifContraparte: '',
  fechaFirma: '', fechaInicio: '', fechaFin: '', renovacionAutomatica: false, objeto: '',
})

const formatFecha   = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatImporte = (n) => Number(n).toLocaleString('es-ES', { minimumFractionDigits: 2 })

const badgeConvenio = (e) => ({
  VIGENTE:    'bg-green-100 text-green-700',
  VENCIDO:    'bg-gray-100 text-gray-500',
  RESCINDIDO: 'bg-red-100 text-red-700',
  SUSPENDIDO: 'bg-yellow-100 text-yellow-700',
}[e] ?? 'bg-gray-100 text-gray-500')

const cargarConvenios = async () => {
  loadingConvenios.value = true
  try {
    const [dataConv, dataTipos] = await Promise.all([
      executeQuery(GET_CONVENIOS, { estado: filtroEstadoConvenio.value || undefined }),
      tiposConvenio.value.length ? null : executeQuery(GET_TIPOS_CONVENIO),
    ])
    convenios.value     = dataConv?.convenios ?? []
    if (dataTipos) tiposConvenio.value = dataTipos?.tiposConvenio ?? []
  } catch (e) { console.error(e) }
  finally { loadingConvenios.value = false }
}

const cargarDelegaciones = async () => {
  loadingDelegaciones.value = true
  try {
    const data = await executeQuery(GET_DELEGACIONES, { activasSolo: false })
    delegaciones.value = data?.delegacionesFirma ?? []
  } catch (e) { console.error(e) }
  finally { loadingDelegaciones.value = false }
}

watch(tabActiva, (tab) => {
  if (tab === 'delegaciones' && !delegaciones.value.length) cargarDelegaciones()
})

const abrirModalConvenio = () => {
  formConvenio.value = {
    tipoConvenioId: '', titulo: '', entidadContraparte: '', cifContraparte: '',
    fechaFirma: '', fechaInicio: '', fechaFin: '', renovacionAutomatica: false, objeto: '',
  }
  errorModal.value = ''
  modalConvenio.value = true
}

const guardarConvenio = async () => {
  errorModal.value = ''
  const f = formConvenio.value
  if (!f.tipoConvenioId || !f.titulo || !f.entidadContraparte || !f.fechaFirma || !f.fechaInicio) {
    errorModal.value = 'Completa los campos obligatorios'
    return
  }
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_CONVENIO, {
      data: {
        tipoConvenioId: f.tipoConvenioId,
        titulo: f.titulo,
        entidadContraparte: f.entidadContraparte,
        cifContraparte: f.cifContraparte || null,
        fechaFirma: f.fechaFirma,
        fechaInicio: f.fechaInicio,
        fechaFin: f.fechaFin || null,
        renovacionAutomatica: f.renovacionAutomatica,
        objeto: f.objeto || null,
      },
    })
    modalConvenio.value = false
    await cargarConvenios()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al registrar el convenio'
  } finally {
    guardando.value = false
  }
}

const cambiarEstado = async (convenio, nuevoEstado) => {
  if (!nuevoEstado) return
  try {
    await executeMutation(CAMBIAR_ESTADO_CONVENIO, { convenioId: convenio.id, nuevoEstado })
    await cargarConvenios()
  } catch (e) { alert(e.message ?? 'Error al cambiar el estado') }
}

const revocarDelegacion = async (d) => {
  try {
    await executeMutation(REVOCAR_DELEGACION, { delegacionId: d.id })
    await cargarDelegaciones()
  } catch (e) { alert(e.message ?? 'Error al revocar la delegación') }
}

onMounted(cargarConvenios)
</script>
