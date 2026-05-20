<template>
  <AppLayout title="Libro de Actas" subtitle="Redacción, aprobación y firma de actas">

    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <select v-model="filtroAnio" @change="cargar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
        <option v-for="a in aniosDisponibles" :key="a" :value="a">{{ a }}</option>
      </select>
      <select v-model="filtroEstado" @change="cargar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
        <option value="">Todos los estados</option>
        <option value="BORRADOR">Borrador</option>
        <option value="APROBADA">Aprobada</option>
        <option value="FIRMADA">Firmada</option>
      </select>
    </div>

    <!-- Alerta: borradores pendientes -->
    <InfoCard v-if="actasPendientes.length > 0"
      :title="`${actasPendientes.length} acta${actasPendientes.length > 1 ? 's' : ''} pendiente${actasPendientes.length > 1 ? 's' : ''} de aprobación`"
      description="Las actas en borrador deben aprobarse en la siguiente reunión del órgano."
      icon="⚠️"
      bg-class="bg-amber-50 border-amber-200"
      class="mb-6"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando actas…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="actas.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <DocumentTextIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay actas en {{ filtroAnio }}</p>
    </div>

    <div v-else class="bg-white rounded-lg border border-gray-200 shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acta</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aprobación</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Firma</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="a in actas" :key="a.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 font-semibold text-gray-900">
              Acta {{ a.numero }}/{{ a.anio }}
            </td>
            <td class="px-4 py-3">
              <span :class="badgeEstadoActa(a.estado)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ a.estado }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatFecha(a.fechaAprobacion) }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatFechaHora(a.fechaFirma) }}</td>
            <td class="px-4 py-3">
              <div class="flex justify-end items-center gap-2">
                <button v-if="a.estado === 'BORRADOR' && tienePermiso('SEC_ACTA_APROBAR')"
                  @click="abrirAprobar(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 font-medium transition-colors">
                  Aprobar
                </button>
                <button v-if="a.estado === 'APROBADA' && tienePermiso('SEC_ACTA_FIRMAR')"
                  @click="abrirFirmar(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 font-medium transition-colors">
                  Firmar
                </button>
                <button v-if="['APROBADA','FIRMADA'].includes(a.estado) && tienePermiso('SEC_CERTIFICADO_EMITIR')"
                  @click="abrirCertificado(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 font-medium transition-colors">
                  Certificar acuerdo
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal: Aprobar acta -->
    <Teleport to="body">
      <div v-if="modalAprobar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalAprobar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Aprobar acta</h2>
              <p class="text-xs text-gray-500 mt-0.5">Acta {{ actaActiva?.numero }}/{{ actaActiva?.anio }}</p>
            </div>
            <button @click="modalAprobar = false" class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Fecha de aprobación <span class="text-red-500">*</span>
              </label>
              <input type="date" v-model="formAprobar.fechaAprobacion"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalAprobar = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button @click="ejecutarAprobar" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Aprobando…' : 'Aprobar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Firmar acta -->
    <Teleport to="body">
      <div v-if="modalFirmar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalFirmar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Firmar acta</h2>
              <p class="text-xs text-gray-500 mt-0.5">Acta {{ actaActiva?.numero }}/{{ actaActiva?.anio }}</p>
            </div>
            <button @click="modalFirmar = false" class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <p class="text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
              Confirma que el acta ha sido revisada y firmada físicamente por el Secretario/a
              con el Visto Bueno del Presidente/a.
            </p>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalFirmar = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button @click="ejecutarFirmar" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Firmando…' : 'Confirmar firma' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Emitir certificado -->
    <Teleport to="body">
      <div v-if="modalCertificado"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalCertificado = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Emitir certificado de acuerdo</h2>
              <p class="text-xs text-gray-500 mt-0.5">Acta {{ actaActiva?.numero }}/{{ actaActiva?.anio }}</p>
            </div>
            <button @click="modalCertificado = false" class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Destinatario</label>
              <input type="text" v-model="formCert.destinatario"
                placeholder="Entidad Bancaria XYZ, Registro de Asociaciones…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Propósito</label>
              <input type="text" v-model="formCert.proposito"
                placeholder="Apertura de cuenta corriente, inscripción registral…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Texto del certificado <span class="text-red-500">*</span>
              </label>
              <textarea v-model="formCert.textoCertificado" rows="5"
                placeholder="D./Dña. [nombre], Secretario/a de [asociación], con el Visto Bueno del/de la Presidente/a, certifica que en la reunión celebrada el [fecha]…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalCertificado = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button @click="ejecutarCertificado" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Emitiendo…' : 'Emitir certificado' }}
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
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import InfoCard from '@/components/common/InfoCard.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_ACTAS, GET_ACTAS_PENDIENTES, APROBAR_ACTA, FIRMAR_ACTA, EMITIR_CERTIFICADO,
} from '@/graphql/queries/secretaria.js'
import { DocumentTextIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const loading  = ref(false)
const error    = ref('')
const guardando  = ref(false)
const errorModal = ref('')
const actas    = ref([])
const actasPendientes = ref([])
const actaActiva = ref(null)

const anioActual = new Date().getFullYear()
const filtroAnio   = ref(anioActual)
const filtroEstado = ref('')
const aniosDisponibles = computed(() => {
  const r = []
  for (let a = anioActual; a >= anioActual - 4; a--) r.push(a)
  return r
})

const modalAprobar    = ref(false)
const modalFirmar     = ref(false)
const modalCertificado = ref(false)
const formAprobar = ref({ fechaAprobacion: '' })
const formCert    = ref({ destinatario: '', proposito: '', textoCertificado: '' })

const formatFecha   = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : '—'

const badgeEstadoActa = (e) => ({
  BORRADOR: 'bg-orange-100 text-orange-700',
  APROBADA: 'bg-indigo-100 text-indigo-700',
  FIRMADA:  'bg-green-100 text-green-700',
}[e] ?? 'bg-gray-100 text-gray-500')

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const [dataActas, dataPend] = await Promise.all([
      executeQuery(GET_ACTAS, { anio: filtroAnio.value, estado: filtroEstado.value || undefined }),
      executeQuery(GET_ACTAS_PENDIENTES),
    ])
    actas.value          = dataActas?.actas ?? []
    actasPendientes.value = dataPend?.actasPendientesAprobacion ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar actas'
  } finally {
    loading.value = false
  }
}

const abrirAprobar = (a) => {
  actaActiva.value = a
  formAprobar.value = { fechaAprobacion: new Date().toISOString().split('T')[0] }
  errorModal.value = ''
  modalAprobar.value = true
}

const ejecutarAprobar = async () => {
  if (!formAprobar.value.fechaAprobacion) { errorModal.value = 'Indica la fecha de aprobación'; return }
  guardando.value = true
  try {
    await executeMutation(APROBAR_ACTA, {
      actaId: actaActiva.value.id,
      fechaAprobacion: formAprobar.value.fechaAprobacion,
    })
    modalAprobar.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al aprobar el acta'
  } finally {
    guardando.value = false
  }
}

const abrirFirmar = (a) => {
  actaActiva.value = a
  errorModal.value = ''
  modalFirmar.value = true
}

const ejecutarFirmar = async () => {
  guardando.value = true
  try {
    // En producción se seleccionarían los firmantes; aquí se usa el usuario en sesión
    await executeMutation(FIRMAR_ACTA, {
      actaId: actaActiva.value.id,
      secretarioId: actaActiva.value.secretarioId,
      presidenteId: actaActiva.value.presidenteId,
    })
    modalFirmar.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al firmar el acta'
  } finally {
    guardando.value = false
  }
}

const abrirCertificado = (a) => {
  actaActiva.value = a
  formCert.value = { destinatario: '', proposito: '', textoCertificado: '' }
  errorModal.value = ''
  modalCertificado.value = true
}

const ejecutarCertificado = async () => {
  if (!formCert.value.textoCertificado) { errorModal.value = 'El texto del certificado es obligatorio'; return }
  guardando.value = true
  try {
    await executeMutation(EMITIR_CERTIFICADO, {
      data: {
        actaId: actaActiva.value.id,
        acuerdoId: actaActiva.value.id, // placeholder — en futuro se selecciona el acuerdo concreto
        ...formCert.value,
      },
    })
    modalCertificado.value = false
  } catch (e) {
    errorModal.value = e.message ?? 'Error al emitir el certificado'
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>
