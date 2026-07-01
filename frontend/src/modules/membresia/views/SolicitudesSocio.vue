<template>
  <AppLayout title="Solicitudes de admisión" subtitle="Solicitudes de socio pendientes de aprobación o rechazo">
    <div class="w-3/4 mx-auto">
      <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando solicitudes…</div>
      <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>
      <div v-else-if="!solicitudes.length" class="text-center py-16 text-slate-400 text-sm">
        No hay solicitudes de socio pendientes.
      </div>

      <div v-else class="overflow-x-auto border border-slate-200 rounded-lg">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50">
            <tr class="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
              <th class="px-4 py-3">Nombre</th>
              <th class="px-4 py-3">Documento</th>
              <th class="px-4 py-3">Contacto</th>
              <th class="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="s in solicitudes" :key="s.id" class="hover:bg-slate-50">
              <td class="px-4 py-3 font-medium text-slate-800">
                {{ [s.nombre, s.apellido1, s.apellido2].filter(Boolean).join(' ') || '—' }}
              </td>
              <td class="px-4 py-3 text-slate-600">{{ s.numeroDocumento || '—' }}</td>
              <td class="px-4 py-3 text-slate-600">
                <div>{{ s.email || '—' }}</div>
                <div class="text-xs text-slate-400">{{ s.telefono || '' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-2">
                  <button @click="aprobar(s)" :disabled="procesando === s.id"
                    class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 disabled:opacity-50">
                    Aprobar
                  </button>
                  <button @click="rechazar(s)" :disabled="procesando === s.id"
                    class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50">
                    Rechazar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import {
  GET_SOLICITUDES_SOCIO, APROBAR_SOLICITUD_SOCIO, RECHAZAR_SOLICITUD_SOCIO,
} from '@/graphql/queries/miembros.js'

const toast = useToast()
const confirm = useConfirm()

const solicitudes = ref([])
const cargando = ref(true)
const error = ref('')
const procesando = ref(null)

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(GET_SOLICITUDES_SOCIO)
    solicitudes.value = data.solicitudesSocioPendientes || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar las solicitudes'
  } finally {
    cargando.value = false
  }
}

function nombreDe(s) {
  return [s.nombre, s.apellido1].filter(Boolean).join(' ') || 'este contacto'
}

async function aprobar(s) {
  const ok = await confirm({
    title: 'Aprobar socio',
    message: `¿Aprobar a ${nombreDe(s)} como socio de pleno derecho?`,
    confirmText: 'Aprobar',
  })
  if (!ok) return
  procesando.value = s.id
  try {
    await graphqlClient.request(APROBAR_SOLICITUD_SOCIO, { contactoId: s.id, numeroSocio: null })
    toast.success('Solicitud aprobada. El aspirante es ahora socio.')
    solicitudes.value = solicitudes.value.filter(x => x.id !== s.id)
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error al aprobar la solicitud')
  } finally {
    procesando.value = null
  }
}

async function rechazar(s) {
  const ok = await confirm({
    title: 'Rechazar solicitud',
    message: `¿Rechazar la solicitud de socio de ${nombreDe(s)}?`,
    confirmText: 'Rechazar',
    danger: true,
  })
  if (!ok) return
  procesando.value = s.id
  try {
    await graphqlClient.request(RECHAZAR_SOLICITUD_SOCIO, { contactoId: s.id, motivo: null })
    toast.success('Solicitud rechazada.')
    solicitudes.value = solicitudes.value.filter(x => x.id !== s.id)
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error al rechazar la solicitud')
  } finally {
    procesando.value = null
  }
}

onMounted(cargar)
</script>
