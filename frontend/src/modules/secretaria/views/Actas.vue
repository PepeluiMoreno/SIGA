<template>
  <AppLayout title="Libro de Actas" subtitle="Redacción, aprobación y firma de actas">

    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <select v-model="filtroAnio" @change="cargar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
        <option v-for="a in aniosDisponibles" :key="a" :value="a">{{ a }}</option>
      </select>
      <select v-model="filtroEstado" @change="cargar"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
        <option value="">Todos los estados</option>
        <option value="BORRADOR">Borrador</option>
        <option value="APROBADA">Aprobada</option>
        <option value="FIRMADA">Firmada</option>
      </select>
    </div>

    <!-- Alertas: actas pendientes de aprobar -->
    <div v-if="actasPendientes.length > 0"
      class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4 flex items-start gap-3">
      <ExclamationCircleIcon class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
      <div>
        <p class="text-sm font-medium text-amber-800">
          {{ actasPendientes.length }} acta{{ actasPendientes.length > 1 ? 's' : '' }} pendiente{{ actasPendientes.length > 1 ? 's' : '' }} de aprobación
        </p>
        <p class="text-xs text-amber-600 mt-0.5">Las actas en borrador deben aprobarse en la siguiente reunión.</p>
      </div>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando actas…" />

    <div v-else-if="actas.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <DocumentTextIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay actas en {{ filtroAnio }}</p>
    </div>

    <div v-else class="bg-white rounded-lg border border-gray-200 shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nº Acta</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reunión</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aprobación</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Firma</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="a in actas" :key="a.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">
              Acta {{ a.numero }}/{{ a.anio }}
            </td>
            <td class="px-4 py-3 text-gray-600 text-xs">{{ a.reunionId.slice(0, 8) }}…</td>
            <td class="px-4 py-3">
              <span :class="badgeEstado(a.estado)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ a.estado }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ formatFecha(a.fechaAprobacion) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatFecha(a.fechaFirma) }}</td>
            <td class="px-4 py-3 text-right">
              <div class="flex justify-end gap-2">
                <button v-if="a.estado === 'BORRADOR' && tienePermiso('SEC_ACTA_APROBAR')"
                  @click="abrirAprobar(a)"
                  class="text-xs px-3 py-1 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100">
                  Aprobar
                </button>
                <button v-if="a.estado === 'APROBADA' && tienePermiso('SEC_ACTA_FIRMAR')"
                  @click="abrirFirmar(a)"
                  class="text-xs px-3 py-1 rounded-lg bg-green-50 text-green-700 border border-green-200 hover:bg-green-100">
                  Firmar
                </button>
                <button v-if="a.estado === 'APROBADA' && tienePermiso('SEC_CERTIFICADO_EMITIR')"
                  @click="abrirCertificado(a)"
                  class="text-xs px-3 py-1 rounded-lg bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100">
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
      <div v-if="modalAprobar" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">Aprobar acta {{ actaActiva?.numero }}/{{ actaActiva?.anio }}</h2>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de aprobación *</label>
            <input type="date" v-model="formAprobar.fechaAprobacion"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <p v-if="errorModal" class="text-sm text-red-600">{{ errorModal }}</p>
          <div class="flex justify-end gap-3">
            <button @click="modalAprobar = false" class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="ejecutarAprobar" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
              {{ guardando ? 'Aprobando…' : 'Aprobar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Emitir certificado (simplificado) -->
    <Teleport to="body">
      <div v-if="modalCertificado" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">Emitir certificado de acuerdo</h2>
          <p class="text-xs text-gray-500">Acta {{ actaActiva?.numero }}/{{ actaActiva?.anio }}</p>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Destinatario</label>
            <input type="text" v-model="formCertificado.destinatario" placeholder="Entidad Bancaria XYZ…"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Propósito</label>
            <input type="text" v-model="formCertificado.proposito" placeholder="Apertura de cuenta, inscripción registral…"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Texto del certificado *</label>
            <textarea v-model="formCertificado.textoCertificado" rows="4" placeholder="D./Dña. [Secretario/a], con el Visto Bueno del/de la Presidente/a, certifica que…"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
          </div>
          <p v-if="errorModal" class="text-sm text-red-600">{{ errorModal }}</p>
          <div class="flex justify-end gap-3">
            <button @click="modalCertificado = false" class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="ejecutarCertificado" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
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
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_ACTAS, GET_ACTAS_PENDIENTES, APROBAR_ACTA, EMITIR_CERTIFICADO } from '@/graphql/queries/secretaria.js'
import { DocumentTextIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const loading  = ref(false)
const guardando = ref(false)
const errorModal = ref('')
const actas    = ref([])
const actasPendientes = ref([])

const anioActual = new Date().getFullYear()
const filtroAnio   = ref(anioActual)
const filtroEstado = ref('')
const aniosDisponibles = computed(() => {
  const arr = []
  for (let a = anioActual; a >= anioActual - 4; a--) arr.push(a)
  return arr
})

const actaActiva = ref(null)
const modalAprobar     = ref(false)
const modalCertificado = ref(false)
const formAprobar = ref({ fechaAprobacion: '' })
const formCertificado = ref({ destinatario: '', proposito: '', textoCertificado: '' })

const formatFecha = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'

const badgeEstado = (e) => ({
  BORRADOR:  'bg-orange-100 text-orange-700',
  APROBADA:  'bg-indigo-100 text-indigo-700',
  FIRMADA:   'bg-green-100 text-green-700',
}[e] ?? 'bg-gray-100 text-gray-500')

const cargar = async () => {
  loading.value = true
  try {
    const [dataActas, dataPendientes] = await Promise.all([
      executeQuery(GET_ACTAS, { anio: filtroAnio.value, estado: filtroEstado.value || undefined }),
      executeQuery(GET_ACTAS_PENDIENTES),
    ])
    actas.value = dataActas?.actas ?? []
    actasPendientes.value = dataPendientes?.actasPendientesAprobacion ?? []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const abrirAprobar = (acta) => {
  actaActiva.value = acta
  formAprobar.value = { fechaAprobacion: new Date().toISOString().split('T')[0] }
  errorModal.value = ''
  modalAprobar.value = true
}

const ejecutarAprobar = async () => {
  if (!formAprobar.value.fechaAprobacion) { errorModal.value = 'Indica la fecha'; return }
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

const abrirCertificado = (acta) => {
  actaActiva.value = acta
  formCertificado.value = { destinatario: '', proposito: '', textoCertificado: '' }
  errorModal.value = ''
  modalCertificado.value = true
}

const ejecutarCertificado = async () => {
  if (!formCertificado.value.textoCertificado) { errorModal.value = 'El texto es obligatorio'; return }
  guardando.value = true
  try {
    await executeMutation(EMITIR_CERTIFICADO, {
      data: {
        actaId: actaActiva.value.id,
        acuerdoId: actaActiva.value.id, // placeholder: en producción se selecciona el acuerdo
        ...formCertificado.value,
      },
    })
    modalCertificado.value = false
  } catch (e) {
    errorModal.value = e.message ?? 'Error al emitir certificado'
  } finally {
    guardando.value = false
  }
}

const abrirFirmar = (acta) => {
  // Simplificado: en producción abre modal con selección de secretario y presidente
  alert(`Funcionalidad de firma del acta ${acta.numero}/${acta.anio} — pendiente de selector de firmantes`)
}

onMounted(cargar)
</script>
