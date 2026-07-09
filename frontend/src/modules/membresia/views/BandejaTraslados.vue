<template>
  <AppLayout title="Traslados" subtitle="Solicitudes de traslado de socios entre agrupaciones">
    <template #actions>
      <AppButton v-if="puedeSolicitar" size="sm" @click="abrirModal">+ Nueva solicitud</AppButton>
    </template>

    <ErrorAlert v-if="error" :message="error" class="mb-3" />

    <!-- Resumen por estado -->
    <div v-if="!loading && filas.length" class="flex flex-wrap items-center gap-2 mb-4 text-xs">
      <span class="text-slate-500">{{ filas.length }} solicitudes ·</span>
      <button v-for="c in resumenEstados" :key="c.codigo"
        @click="filtroEstado = filtroEstado === c.codigo ? null : c.codigo"
        class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border transition"
        :class="filtroEstado === c.codigo ? 'border-slate-400 bg-slate-100' : 'border-slate-200 hover:bg-slate-50'">
        <span class="w-2 h-2 rounded-full" :style="{ background: estadoInfo(c.codigo).color }"></span>
        {{ estadoInfo(c.codigo).nombre }} <strong>{{ c.n }}</strong>
      </button>
      <button v-if="filtroEstado" @click="filtroEstado = null" class="text-slate-400 hover:text-slate-600 underline">
        limpiar
      </button>
    </div>

    <div v-if="loading" class="py-16 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="!filasFiltradas.length" class="text-center py-16 text-slate-400 text-sm border border-dashed border-slate-200 rounded-xl">
      {{ filas.length ? 'No hay solicitudes con ese estado.' : 'No hay solicitudes de traslado.' }}
    </div>

    <!-- Tarjetas -->
    <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-3">
      <div v-for="f in filasFiltradas" :key="f.id"
        class="bg-white border border-slate-200 rounded-xl p-4 flex flex-col gap-3">

        <!-- Cabecera: socio + estado -->
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="font-semibold text-slate-800">{{ nombreSocio(f) }}</div>
            <div class="text-xs text-slate-400">Solicitado el {{ fechaFmt(f.fechaSolicitud) }}</div>
          </div>
          <span class="text-[11px] font-medium px-2 py-1 rounded-full whitespace-nowrap"
            :style="badgeStyle(f.estado)">{{ estadoInfo(f.estado).nombre }}</span>
        </div>

        <!-- Ruta origen → destino -->
        <div class="flex items-center gap-2 text-sm flex-wrap">
          <span class="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">{{ agr(f.agrupacionOrigenId) }}</span>
          <span class="text-slate-400">→</span>
          <span class="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-medium">{{ agr(f.agrupacionDestinoId) }}</span>
        </div>

        <!-- Motivo -->
        <div class="text-sm">
          <span class="text-slate-500">Motivo:</span>
          <span class="text-slate-800">{{ f.motivoTraslado?.nombre || '—' }}</span>
          <span v-if="f.motivo" class="text-slate-500 italic"> · {{ f.motivo }}</span>
        </div>

        <!-- Stepper de doble aprobación -->
        <div class="flex items-center gap-1 text-[11px]">
          <span class="paso" :class="pasoClase(f, 'solicitada')">Solicitada</span>
          <span class="flecha">→</span>
          <span class="paso" :class="pasoClase(f, 'origen')">
            Origen {{ f.aprobadoOrigen ? '✓' : (esRechazoOrigen(f) ? '✕' : '·') }}
          </span>
          <span class="flecha">→</span>
          <span class="paso" :class="pasoClase(f, 'destino')">
            Destino {{ f.aprobadoDestino ? '✓' : (esRechazoDestino(f) ? '✕' : '·') }}
          </span>
          <span class="flecha">→</span>
          <span class="paso" :class="pasoClase(f, 'ejecutado')">Ejecutado</span>
        </div>

        <div v-if="f.motivoRechazo" class="text-xs text-red-600 bg-red-50 rounded-md px-2 py-1">
          Rechazo: {{ f.motivoRechazo }}
        </div>

        <!-- Acciones -->
        <div v-if="enCurso(f.estado)" class="flex items-center gap-1.5 flex-wrap pt-1 border-t border-slate-100">
          <AppButton v-if="puedeAprobar && !f.aprobadoOrigen" size="xs" variant="secondary"
            :loading="procesando === f.id" @click="aprobarOrigen(f)">Aprobar origen</AppButton>
          <AppButton v-if="puedeAprobar && !f.aprobadoDestino" size="xs" variant="secondary"
            :loading="procesando === f.id" @click="aprobarDestino(f)">Aprobar destino</AppButton>
          <AppButton v-if="puedeAprobar && f.estado === 'APROBADO'" size="xs" variant="primary"
            :loading="procesando === f.id" @click="ejecutar(f)">Ejecutar traslado</AppButton>
          <AppButton v-if="puedeRechazar" size="xs" variant="danger"
            :loading="procesando === f.id" @click="rechazar(f)">Rechazar</AppButton>
          <AppButton v-if="puedeSolicitar" size="xs" variant="ghost"
            :loading="procesando === f.id" @click="cancelar(f)">Cancelar</AppButton>
        </div>
      </div>
    </div>

    <!-- Modal: nueva solicitud -->
    <div v-if="modal.abierto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="cerrarModal">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div class="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">Nueva solicitud de traslado</h3>
          <button @click="cerrarModal" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div class="px-5 py-4 space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Socio a trasladar</label>
            <SelectorMiembro v-model="modal.miembroId" placeholder="Buscar socio…" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Agrupación de destino</label>
            <SelectorAgrupacion v-model="modal.agrupacionDestinoId" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Motivo</label>
            <select v-model="modal.motivoTrasladoId" class="block w-full rounded-lg border-slate-300 text-sm">
              <option :value="null" disabled>Selecciona un motivo…</option>
              <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Detalle (opcional)</label>
            <textarea v-model="modal.detalle" rows="2" class="block w-full rounded-lg border-slate-300 text-sm"
              placeholder="Aclaraciones sobre el traslado…"></textarea>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Fecha deseada (opcional)</label>
            <input v-model="modal.fechaEfectivaDeseada" type="date" class="block w-48 rounded-lg border-slate-300 text-sm" />
          </div>
        </div>
        <div class="px-5 py-4 border-t border-slate-200 flex justify-end gap-2">
          <AppButton variant="ghost" size="sm" @click="cerrarModal">Cancelar</AppButton>
          <AppButton size="sm" :loading="modal.enviando" :disabled="!modalValido" @click="crearSolicitud">
            Crear solicitud
          </AppButton>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import AppButton from '@/components/common/AppButton.vue'
import SelectorMiembro from '@/components/common/SelectorMiembro.vue'
import SelectorAgrupacion from '@/components/common/SelectorAgrupacion.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useToast } from '@/composables/useToast'
import { useConfirm, usePrompt } from '@/composables/useConfirm'
import { usePermisos } from '@/composables/usePermisos'
import { GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import {
  GET_SOLICITUDES_TRASLADO, GET_MOTIVOS_TRASLADO, GET_ESTADOS_TRASLADO,
  SOLICITAR_TRASLADO, APROBAR_TRASLADO_ORIGEN, APROBAR_TRASLADO_DESTINO,
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
const motivos = ref([])
const estadosCat = ref({})   // codigo → { nombre, color }
const error = ref('')
const procesando = ref(null)
const filtroEstado = ref(null)

const _ESTADOS_EN_CURSO = ['PENDIENTE', 'APROBADO_ORIGEN', 'APROBADO_DESTINO', 'APROBADO']
const enCurso = (e) => _ESTADOS_EN_CURSO.includes(e)

const estadoInfo = (codigo) => estadosCat.value[codigo] || { nombre: (codigo || '').replaceAll('_', ' ').toLowerCase(), color: '#94a3b8' }
const badgeStyle = (codigo) => {
  const c = estadoInfo(codigo).color
  return { color: c, background: c + '1a', border: `1px solid ${c}55` }
}
const agr = (id) => agrupaciones.value[id] || '—'
const nombreSocio = (f) => [f.miembro?.nombre, f.miembro?.apellido1, f.miembro?.apellido2].filter(Boolean).join(' ') || '—'
const fechaFmt = (d) => d ? new Date(d).toLocaleDateString('es-ES') : ''

const esRechazoOrigen = (f) => f.estado === 'RECHAZADO_ORIGEN'
const esRechazoDestino = (f) => f.estado === 'RECHAZADO_DESTINO'

function pasoClase(f, paso) {
  if (paso === 'solicitada') return 'paso-ok'
  if (paso === 'origen') return f.aprobadoOrigen ? 'paso-ok' : (esRechazoOrigen(f) ? 'paso-ko' : 'paso-pend')
  if (paso === 'destino') return f.aprobadoDestino ? 'paso-ok' : (esRechazoDestino(f) ? 'paso-ko' : 'paso-pend')
  if (paso === 'ejecutado') return f.estado === 'EJECUTADO' ? 'paso-ok' : 'paso-pend'
  return 'paso-pend'
}

const filasFiltradas = computed(() =>
  filtroEstado.value ? filas.value.filter(f => f.estado === filtroEstado.value) : filas.value)

const resumenEstados = computed(() => {
  const m = {}
  for (const f of filas.value) m[f.estado] = (m[f.estado] || 0) + 1
  return Object.entries(m).map(([codigo, n]) => ({ codigo, n }))
})

async function cargar() {
  error.value = ''
  try {
    const [dataT, dataA, dataM, dataE] = await Promise.all([
      query(GET_SOLICITUDES_TRASLADO),
      query(GET_AGRUPACIONES),
      query(GET_MOTIVOS_TRASLADO),
      query(GET_ESTADOS_TRASLADO),
    ])
    filas.value = dataT.solicitudesTraslado || []
    agrupaciones.value = Object.fromEntries((dataA.unidadesOrganizativas || []).map(a => [a.id, a.nombre]))
    motivos.value = (dataM.motivosTraslado || []).filter(m => m.activo).sort((a, b) => a.orden - b.orden)
    estadosCat.value = Object.fromEntries(
      (dataE.estadosTraslado || []).map(e => [e.codigo, { nombre: e.nombre, color: e.color || '#94a3b8' }]))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar los traslados'
  }
}

// ── Nueva solicitud ──────────────────────────────────────────────────────────
const modal = reactive({
  abierto: false, miembroId: null, agrupacionDestinoId: null,
  motivoTrasladoId: null, detalle: '', fechaEfectivaDeseada: '', enviando: false,
})
const modalValido = computed(() => modal.miembroId && modal.agrupacionDestinoId && modal.motivoTrasladoId)

function abrirModal() {
  Object.assign(modal, { abierto: true, miembroId: null, agrupacionDestinoId: null,
    motivoTrasladoId: null, detalle: '', fechaEfectivaDeseada: '', enviando: false })
}
function cerrarModal() { modal.abierto = false }

async function crearSolicitud() {
  if (!modalValido.value) return
  modal.enviando = true
  try {
    await mutation(SOLICITAR_TRASLADO, {
      miembroId: modal.miembroId,
      agrupacionDestinoId: modal.agrupacionDestinoId,
      motivoTrasladoId: modal.motivoTrasladoId,
      detalle: modal.detalle?.trim() || null,
      fechaEfectivaDeseada: modal.fechaEfectivaDeseada || null,
    })
    toast.success('Solicitud de traslado creada.')
    cerrarModal()
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo crear la solicitud')
  } finally {
    modal.enviando = false
  }
}

// ── Transiciones ─────────────────────────────────────────────────────────────
async function _run(f, doc, vars, okMsg) {
  procesando.value = f.id
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

const aprobarOrigen = (f) => _run(f, APROBAR_TRASLADO_ORIGEN, { solicitudId: f.id, observaciones: null }, 'Aprobado por origen.')
const aprobarDestino = (f) => _run(f, APROBAR_TRASLADO_DESTINO, { solicitudId: f.id, observaciones: null }, 'Aprobado por destino.')

async function ejecutar(f) {
  const ok = await confirm({
    titulo: 'Ejecutar traslado',
    mensaje: `¿Trasladar a ${nombreSocio(f)} a ${agr(f.agrupacionDestinoId)}? Se moverá su agrupación y se registrará en su historial.`,
    etiquetaConfirmar: 'Ejecutar',
  })
  if (!ok) return
  await _run(f, EJECUTAR_TRASLADO, { solicitudId: f.id }, 'Traslado ejecutado.')
}

async function rechazar(f) {
  const motivo = await prompt({
    titulo: 'Rechazar traslado',
    label: `Motivo del rechazo del traslado de ${nombreSocio(f)}`,
    requerido: true, variante: 'peligro', etiquetaConfirmar: 'Rechazar',
  })
  if (!motivo) return
  const lado = f.aprobadoOrigen ? 'destino' : 'origen'
  await _run(f, RECHAZAR_TRASLADO, { solicitudId: f.id, motivo, lado }, 'Traslado rechazado.')
}

async function cancelar(f) {
  const ok = await confirm({
    titulo: 'Cancelar traslado',
    mensaje: `¿Cancelar la solicitud de traslado de ${nombreSocio(f)}?`,
    etiquetaConfirmar: 'Cancelar traslado', variante: 'peligro',
  })
  if (!ok) return
  await _run(f, CANCELAR_TRASLADO, { solicitudId: f.id }, 'Traslado cancelado.')
}

onMounted(cargar)
</script>

<style scoped>
.paso { padding: 0.125rem 0.5rem; border-radius: 9999px; white-space: nowrap; }
.paso-ok   { background: #dcfce7; color: #15803d; }
.paso-ko   { background: #fee2e2; color: #b91c1c; }
.paso-pend { background: #f1f5f9; color: #94a3b8; }
.flecha    { color: #cbd5e1; }
</style>
