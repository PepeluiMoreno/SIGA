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
      <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-200 text-sm">
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
            <td class="px-4 py-3 font-semibold text-gray-900">Acta {{ a.numero }}/{{ a.anio }}</td>
            <td class="px-4 py-3">
              <span :class="badgeEstadoActa(a.estadoCodigo)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ etiquetaActa(a.estadoCodigo) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatFecha(a.fechaAprobacion) }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatFechaHora(a.fechaFirma) }}</td>
            <td class="px-4 py-3">
              <div class="flex justify-end items-center gap-2">
                <button v-if="a.estadoCodigo === 'BORRADOR' && tienePermiso('SEC_ACTA_APROBAR')"
                  @click="abrirAprobar(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 font-medium transition-colors">
                  Aprobar
                </button>
                <button v-if="a.estadoCodigo === 'APROBADA' && tienePermiso('SEC_ACTA_FIRMAR')"
                  @click="abrirFirmar(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 font-medium transition-colors">
                  Firmar
                </button>
                <button v-if="['APROBADA','FIRMADA'].includes(a.estadoCodigo) && tienePermiso('SEC_CERTIFICADO_EMITIR')"
                  @click="abrirCertificado(a)"
                  class="text-xs px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 font-medium transition-colors">
                  Certificar acuerdo
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- ── Modal: Aprobar acta ── -->
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
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
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

    <!-- ── Modal: Firmar acta ── -->
    <Teleport to="body">
      <div v-if="modalFirmar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalFirmar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md">
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
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Secretario/a firmante <span class="text-red-500">*</span>
              </label>
              <SelectorMiembro
                v-model="formFirmar.secretarioId"
                :miembros="miembros"
                placeholder="Buscar secretario/a…"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Presidente/a (Visto Bueno) <span class="text-red-500">*</span>
              </label>
              <SelectorMiembro
                v-model="formFirmar.presidenteId"
                :miembros="miembros"
                placeholder="Buscar presidente/a…"
              />
            </div>
            <p class="text-xs text-gray-500 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
              Confirma que el acta ha sido revisada y firmada físicamente por ambos cargos.
            </p>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalFirmar = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
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

    <!-- ── Modal: Emitir certificado ── -->
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
            <!-- Selector de acuerdo -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Acuerdo a certificar <span class="text-red-500">*</span>
              </label>
              <select v-model="formCert.acuerdoId"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">Selecciona un acuerdo…</option>
                <option v-for="ac in acuerdosActa" :key="ac.id" :value="ac.id">
                  Nº {{ ac.numero }} — {{ ac.descripcion.slice(0, 60) }}{{ ac.descripcion.length > 60 ? '…' : '' }}
                </option>
              </select>
            </div>
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
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Secretario/a firmante</label>
              <SelectorMiembro
                v-model="formCert.secretarioId"
                :miembros="miembros"
                placeholder="Buscar secretario/a…"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Presidente/a (Visto Bueno)</label>
              <SelectorMiembro
                v-model="formCert.presidenteId"
                :miembros="miembros"
                placeholder="Buscar presidente/a…"
              />
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {{ errorModal }}
            </p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalCertificado = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
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
import SelectorMiembro from '@/components/common/SelectorMiembro.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_ACTAS, GET_ACTAS_PENDIENTES, APROBAR_ACTA, FIRMAR_ACTA, EMITIR_CERTIFICADO,
  GET_MIEMBROS_LIGERO,
} from '@/graphql/queries/secretaria.js'
import { DocumentTextIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const loading   = ref(false)
const error     = ref('')
const guardando = ref(false)
const errorModal = ref('')
const actas     = ref([])
const actasPendientes = ref([])
const miembros  = ref([])
const actaActiva = ref(null)
const acuerdosActa = ref([]) // acuerdos del acta seleccionada para el certificado

const anioActual = new Date().getFullYear()
const filtroAnio   = ref(anioActual)
const filtroEstado = ref('')
const aniosDisponibles = computed(() => {
  const r = []
  for (let a = anioActual; a >= anioActual - 4; a--) r.push(a)
  return r
})

const modalAprobar     = ref(false)
const modalFirmar      = ref(false)
const modalCertificado = ref(false)

const formAprobar = ref({ fechaAprobacion: '' })
const formFirmar  = ref({ secretarioId: null, presidenteId: null })
const formCert    = ref({
  acuerdoId: '', destinatario: '', proposito: '',
  textoCertificado: '', secretarioId: null, presidenteId: null,
})

const ESTADOS_ACTA = [
  { codigo: 'BORRADOR', etiqueta: 'Borrador', clase: 'bg-orange-100 text-orange-700' },
  { codigo: 'APROBADA', etiqueta: 'Aprobada', clase: 'bg-indigo-100 text-indigo-700' },
  { codigo: 'FIRMADA',  etiqueta: 'Firmada',  clase: 'bg-green-100 text-green-700' },
]

const formatFecha     = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : '—'
const badgeEstadoActa = (c) => ESTADOS_ACTA.find(e => e.codigo === c)?.clase ?? 'bg-gray-100 text-gray-500'
const etiquetaActa    = (c) => ESTADOS_ACTA.find(e => e.codigo === c)?.etiqueta ?? c

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const [dataActas, dataPend] = await Promise.all([
      executeQuery(GET_ACTAS, { anio: filtroAnio.value, estado: filtroEstado.value || undefined }),
      executeQuery(GET_ACTAS_PENDIENTES),
    ])
    actas.value           = dataActas?.actas ?? []
    actasPendientes.value = dataPend?.actasPendientesAprobacion ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar actas'
  } finally {
    loading.value = false
  }
}

const cargarMiembros = async () => {
  try {
    const data = await executeQuery(GET_MIEMBROS_LIGERO)
    miembros.value = data?.miembros ?? []
  } catch (e) { console.error('Error cargando miembros', e) }
}

// Carga los acuerdos del acta para el selector del certificado
const cargarAcuerdosActa = async (actaId) => {
  // Por ahora los acuerdos se obtienen a través de la reunión asociada
  // Cuando exista query directa de acuerdos por acta, reemplazar aquí
  acuerdosActa.value = []
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
  formFirmar.value = {
    secretarioId: a.secretarioId ?? null,
    presidenteId: a.presidenteId ?? null,
  }
  errorModal.value = ''
  modalFirmar.value = true
}

const ejecutarFirmar = async () => {
  if (!formFirmar.value.secretarioId) { errorModal.value = 'Selecciona el secretario/a firmante'; return }
  if (!formFirmar.value.presidenteId) { errorModal.value = 'Selecciona el presidente/a'; return }
  guardando.value = true
  try {
    await executeMutation(FIRMAR_ACTA, {
      actaId: actaActiva.value.id,
      secretarioId: formFirmar.value.secretarioId,
      presidenteId: formFirmar.value.presidenteId,
    })
    modalFirmar.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al firmar el acta'
  } finally {
    guardando.value = false
  }
}

const abrirCertificado = async (a) => {
  actaActiva.value = a
  formCert.value = {
    acuerdoId: '', destinatario: '', proposito: '',
    textoCertificado: '', secretarioId: null, presidenteId: null,
  }
  errorModal.value = ''
  await cargarAcuerdosActa(a.id)
  modalCertificado.value = true
}

const ejecutarCertificado = async () => {
  if (!formCert.value.acuerdoId)        { errorModal.value = 'Selecciona el acuerdo a certificar'; return }
  if (!formCert.value.textoCertificado) { errorModal.value = 'El texto del certificado es obligatorio'; return }
  guardando.value = true
  try {
    await executeMutation(EMITIR_CERTIFICADO, {
      data: {
        actaId:           actaActiva.value.id,
        acuerdoId:        formCert.value.acuerdoId,
        textoCertificado: formCert.value.textoCertificado,
        destinatario:     formCert.value.destinatario || null,
        proposito:        formCert.value.proposito || null,
        secretarioId:     formCert.value.secretarioId || null,
        presidenteId:     formCert.value.presidenteId || null,
      },
    })
    modalCertificado.value = false
  } catch (e) {
    errorModal.value = e.message ?? 'Error al emitir el certificado'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await Promise.all([cargar(), cargarMiembros()])
})
</script>
