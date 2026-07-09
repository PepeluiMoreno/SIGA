<template>
  <AppLayout title="Traslados" subtitle="Solicitudes de traslado de socios entre agrupaciones">
    <ErrorAlert v-if="error" :message="error" class="mb-3" />

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="!filas.length" class="text-center py-16 text-slate-400 text-sm">
      No hay solicitudes de traslado.
    </div>

    <div v-else class="bg-white border border-slate-200 rounded-xl sm:overflow-hidden p-3 sm:p-0">
      <ResponsiveTable :columnas="columnas" :filas="filas" clave-fila="id">
        <template #cell-socio="{ fila }">
          <div class="font-medium text-slate-800">{{ nombreSocio(fila) }}</div>
          <div class="text-xs text-slate-400">{{ fechaFmt(fila.fechaSolicitud) }}</div>
        </template>

        <template #cell-ruta="{ fila }">
          <span class="text-slate-600">{{ agr(fila.agrupacionOrigenId) }}</span>
          <span class="text-slate-300 mx-1">→</span>
          <span class="text-slate-800 font-medium">{{ agr(fila.agrupacionDestinoId) }}</span>
        </template>

        <template #cell-estado="{ fila }">
          <EstadoBadge :texto="estadoTexto(fila.estado)" :color="estadoColor(fila.estado)" />
          <div class="mt-1 flex gap-1 text-[10px] text-slate-400">
            <span :class="fila.aprobadoOrigen ? 'text-emerald-600' : ''">origen {{ fila.aprobadoOrigen ? '✓' : '·' }}</span>
            <span :class="fila.aprobadoDestino ? 'text-emerald-600' : ''">destino {{ fila.aprobadoDestino ? '✓' : '·' }}</span>
          </div>
        </template>

        <template #cell-acciones="{ fila }">
          <div class="flex items-center justify-end gap-1.5 flex-wrap">
            <template v-if="enCurso(fila.estado)">
              <AppButton v-if="puedeAprobar && !fila.aprobadoOrigen" size="xs" variant="secondary"
                :loading="procesando === fila.id" @click="aprobarOrigen(fila)">Aprobar origen</AppButton>
              <AppButton v-if="puedeAprobar && !fila.aprobadoDestino" size="xs" variant="secondary"
                :loading="procesando === fila.id" @click="aprobarDestino(fila)">Aprobar destino</AppButton>
              <AppButton v-if="puedeAprobar && fila.estado === 'APROBADO'" size="xs" variant="primary"
                :loading="procesando === fila.id" @click="ejecutar(fila)">Ejecutar</AppButton>
              <AppButton v-if="puedeRechazar" size="xs" variant="danger"
                :loading="procesando === fila.id" @click="rechazar(fila)">Rechazar</AppButton>
              <AppButton v-if="puedeSolicitar" size="xs" variant="ghost"
                :loading="procesando === fila.id" @click="cancelar(fila)">Cancelar</AppButton>
            </template>
            <span v-else class="text-xs text-slate-400">—</span>
          </div>
        </template>
      </ResponsiveTable>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import EstadoBadge from '@/components/common/EstadoBadge.vue'
import AppButton from '@/components/common/AppButton.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useToast } from '@/composables/useToast'
import { useConfirm, usePrompt } from '@/composables/useConfirm'
import { usePermisos } from '@/composables/usePermisos'
import { GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import {
  GET_SOLICITUDES_TRASLADO, APROBAR_TRASLADO_ORIGEN, APROBAR_TRASLADO_DESTINO,
  RECHAZAR_TRASLADO, CANCELAR_TRASLADO, EJECUTAR_TRASLADO,
} from '@/graphql/queries/socioGestion.js'

const { query, mutation, loading } = useGraphQL()
const toast = useToast()
const confirm = useConfirm()
const prompt = usePrompt()
const { tienePermiso } = usePermisos()

const puedeAprobar = computed(() => tienePermiso('MEMBRESIA_TRASLADO_APROBAR'))
const puedeRechazar = computed(() => tienePermiso('MEMBRESIA_TRASLADO_RECHAZAR'))
const puedeSolicitar = computed(() => tienePermiso('MEMBRESIA_TRASLADO_SOLICITAR'))

const filas = ref([])
const agrupaciones = ref({})
const error = ref('')
const procesando = ref(null)

const columnas = [
  { key: 'socio', label: 'Socio', align: 'left' },
  { key: 'ruta', label: 'Origen → Destino', align: 'left' },
  { key: 'motivo', label: 'Motivo', align: 'left', ocultaEnMovil: true },
  { key: 'estado', label: 'Estado', align: 'left' },
  { key: 'acciones', label: '', align: 'right', esAcciones: true },
]

const _ESTADOS_EN_CURSO = ['PENDIENTE', 'APROBADO_ORIGEN', 'APROBADO_DESTINO', 'APROBADO']
const enCurso = (e) => _ESTADOS_EN_CURSO.includes(e)

const _COLORES = {
  PENDIENTE: '#f59e0b', APROBADO_ORIGEN: '#3b82f6', APROBADO_DESTINO: '#3b82f6',
  APROBADO: '#10b981', EJECUTADO: '#059669', CANCELADO: '#94a3b8',
  RECHAZADO_ORIGEN: '#ef4444', RECHAZADO_DESTINO: '#ef4444',
}
const estadoColor = (e) => _COLORES[e] ?? '#94a3b8'
const estadoTexto = (e) => (e || '').replaceAll('_', ' ').toLowerCase()

const agr = (id) => agrupaciones.value[id] || '—'
const nombreSocio = (f) => [f.miembro?.nombre, f.miembro?.apellido1, f.miembro?.apellido2].filter(Boolean).join(' ') || '—'
const fechaFmt = (d) => d ? new Date(d).toLocaleDateString('es-ES') : ''

async function cargar() {
  error.value = ''
  try {
    const [dataT, dataA] = await Promise.all([
      query(GET_SOLICITUDES_TRASLADO),
      query(GET_AGRUPACIONES),
    ])
    filas.value = dataT.solicitudesTraslado || []
    agrupaciones.value = Object.fromEntries((dataA.unidadesOrganizativas || []).map(a => [a.id, a.nombre]))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar los traslados'
  }
}

async function _ejecutarMutacion(fila, doc, vars, okMsg) {
  procesando.value = fila.id
  try {
    await mutation(doc, vars)
    toast.success(okMsg)
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'La operación no se pudo completar')
  } finally {
    procesando.value = null
  }
}

const aprobarOrigen = (f) => _ejecutarMutacion(f, APROBAR_TRASLADO_ORIGEN, { solicitudId: f.id, observaciones: null }, 'Aprobado por origen.')
const aprobarDestino = (f) => _ejecutarMutacion(f, APROBAR_TRASLADO_DESTINO, { solicitudId: f.id, observaciones: null }, 'Aprobado por destino.')

async function ejecutar(f) {
  const ok = await confirm({
    titulo: 'Ejecutar traslado',
    mensaje: `¿Trasladar a ${nombreSocio(f)} a ${agr(f.agrupacionDestinoId)}? Se moverá su agrupación y se registrará en su historial.`,
    etiquetaConfirmar: 'Ejecutar',
  })
  if (!ok) return
  await _ejecutarMutacion(f, EJECUTAR_TRASLADO, { solicitudId: f.id }, 'Traslado ejecutado.')
}

async function rechazar(f) {
  const motivo = await prompt({
    titulo: 'Rechazar traslado',
    label: `Motivo del rechazo del traslado de ${nombreSocio(f)}`,
    requerido: true,
    variante: 'peligro',
    etiquetaConfirmar: 'Rechazar',
  })
  if (!motivo) return
  const lado = f.aprobadoOrigen ? 'destino' : 'origen'
  await _ejecutarMutacion(f, RECHAZAR_TRASLADO, { solicitudId: f.id, motivo, lado }, 'Traslado rechazado.')
}

async function cancelar(f) {
  const ok = await confirm({
    titulo: 'Cancelar traslado',
    mensaje: `¿Cancelar la solicitud de traslado de ${nombreSocio(f)}?`,
    etiquetaConfirmar: 'Cancelar traslado',
    variante: 'peligro',
  })
  if (!ok) return
  await _ejecutarMutacion(f, CANCELAR_TRASLADO, { solicitudId: f.id }, 'Traslado cancelado.')
}

onMounted(cargar)
</script>
