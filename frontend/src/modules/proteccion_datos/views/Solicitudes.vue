<template>
  <AppLayout
    title="Solicitudes de derechos (ARSULIPO)"
    subtitle="Acceso, Rectificación, Supresión, Limitación, Portabilidad, Oposición (art. 15-22 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por código, nombre o DNI…"
      create-label="+ Registrar solicitud"
      :fields="camposFiltro"
      @create="abrirAlta()"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando solicitudes…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtradas"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        vacio-texto="No hay solicitudes registradas"
        @row-click="abrirDetalle"
      >
        <template #cell-codigoInterno="{ fila }">
          <span class="font-mono text-xs">{{ fila.codigoInterno }}</span>
        </template>
        <template #cell-tipo="{ fila }">
          <span class="text-[10px] uppercase rounded-full px-2 py-0.5 bg-indigo-100 text-indigo-700">{{ fila.tipo }}</span>
        </template>
        <template #cell-estado="{ fila }">
          <span :class="badgeEstado(fila.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.estado }}
          </span>
        </template>
        <template #cell-plazo="{ fila }">
          <span :class="claseAlerta(fila)" class="text-xs">
            {{ plazoTexto(fila) }}
          </span>
        </template>
        <template #cell-fechaPresentacion="{ fila }">
          <span class="text-xs text-slate-600">{{ fechaFmt(fila.fechaPresentacion) }}</span>
        </template>
      </ResponsiveTable>
    </div>

    <!-- Modal alta nueva solicitud -->
    <BaseModal v-model="modalAlta" title="Registrar solicitud de derecho" size="xl">
      <form @submit.prevent="crear" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="lbl">Tipo de derecho <span class="req">*</span></label>
            <select v-model="alta.tipo" required class="inp">
              <option value="">Selecciona…</option>
              <option v-for="t in TIPOS" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div>
            <label class="lbl">Canal de presentación <span class="req">*</span></label>
            <select v-model="alta.canalPresentacion" required class="inp">
              <option v-for="c in CANALES" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Nombre del solicitante <span class="req">*</span></label>
            <input v-model="alta.nombreSolicitante" type="text" required maxlength="200" class="inp" />
          </div>
          <div>
            <label class="lbl">Documento (DNI/NIE/Pasaporte)</label>
            <input v-model="alta.documentoSolicitante" type="text" maxlength="40" class="inp" />
          </div>
          <div>
            <label class="lbl">Email</label>
            <input v-model="alta.emailSolicitante" type="email" maxlength="200" class="inp" />
          </div>
          <div>
            <label class="lbl">Teléfono</label>
            <input v-model="alta.telefonoSolicitante" type="text" maxlength="50" class="inp" />
          </div>
          <div>
            <label class="lbl">Fecha de presentación <span class="req">*</span></label>
            <input v-model="alta.fechaPresentacion" type="date" required class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Descripción de la solicitud</label>
            <textarea v-model="alta.descripcionSolicitud" rows="3" class="inp"></textarea>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalAlta = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit" :disabled="guardando"
            class="text-sm px-4 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            {{ guardando ? 'Registrando…' : 'Registrar' }}
          </button>
        </div>
      </form>
    </BaseModal>

    <!-- Modal detalle / tramitación -->
    <BaseModal v-model="modalDetalle" :title="seleccionada ? `Solicitud ${seleccionada.codigoInterno}` : ''" size="xl">
      <div v-if="seleccionada" class="space-y-4">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div><span class="text-slate-500">Tipo:</span> <strong>{{ seleccionada.tipo }}</strong></div>
          <div><span class="text-slate-500">Estado:</span>
            <span :class="badgeEstado(seleccionada.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5 ml-1">
              {{ seleccionada.estado }}
            </span>
          </div>
          <div><span class="text-slate-500">Solicitante:</span> {{ seleccionada.nombreSolicitante }}</div>
          <div><span class="text-slate-500">Documento:</span> {{ seleccionada.documentoSolicitante || '—' }}</div>
          <div><span class="text-slate-500">Email:</span> {{ seleccionada.emailSolicitante || '—' }}</div>
          <div><span class="text-slate-500">Teléfono:</span> {{ seleccionada.telefonoSolicitante || '—' }}</div>
          <div><span class="text-slate-500">Presentada:</span> {{ fechaFmt(seleccionada.fechaPresentacion) }} ({{ seleccionada.canalPresentacion }})</div>
          <div>
            <span class="text-slate-500">Plazo límite:</span>
            <span :class="claseAlerta(seleccionada)">{{ fechaFmt(seleccionada.fechaLimiteRespuesta) }}</span>
            <span v-if="seleccionada.prorrogada" class="ml-1 text-[10px] text-amber-700">
              (prórroga: {{ fechaFmt(seleccionada.fechaLimiteProrroga) }})
            </span>
          </div>
        </div>
        <div v-if="seleccionada.descripcionSolicitud" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <div class="text-xs text-slate-500 mb-1">Descripción</div>
          <div class="text-sm whitespace-pre-line">{{ seleccionada.descripcionSolicitud }}</div>
        </div>
        <div v-if="seleccionada.motivoProrroga" class="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <div class="text-xs text-amber-700 mb-1">Motivo de la prórroga</div>
          <div class="text-sm whitespace-pre-line">{{ seleccionada.motivoProrroga }}</div>
        </div>
        <div v-if="seleccionada.resolucion" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <div class="text-xs text-slate-500 mb-1">Resolución ({{ fechaFmt(seleccionada.fechaResolucion) }})</div>
          <div class="text-sm whitespace-pre-line">{{ seleccionada.resolucion }}</div>
          <a v-if="seleccionada.documentoResolucionUrl" :href="seleccionada.documentoResolucionUrl" target="_blank"
            class="text-xs text-indigo-600 hover:underline mt-2 inline-block">📄 Documento adjunto</a>
        </div>

        <!-- Acciones según estado -->
        <div v-if="!enCerrado(seleccionada)" class="flex flex-wrap gap-2 pt-3 border-t border-slate-200">
          <button v-if="seleccionada.estado === 'PRESENTADA'" type="button"
            @click="iniciar(seleccionada)"
            class="text-sm px-3 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
            Iniciar trámite
          </button>
          <button v-if="!seleccionada.prorrogada" type="button"
            @click="abrirProrroga"
            class="text-sm px-3 h-9 rounded-lg border border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100">
            Prorrogar a 3 meses
          </button>
          <span class="flex-1" />
          <button type="button"
            @click="abrirResolver(false)"
            class="text-sm px-3 h-9 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700">
            Resolver favorablemente
          </button>
          <button type="button"
            @click="abrirResolver(true)"
            class="text-sm px-3 h-9 rounded-lg bg-red-600 text-white hover:bg-red-700">
            Denegar
          </button>
        </div>
      </div>
    </BaseModal>

    <!-- Modal prórroga -->
    <BaseModal v-model="modalProrroga" title="Prorrogar plazo a 3 meses" size="md">
      <form @submit.prevent="prorrogar" class="space-y-3">
        <p class="text-sm text-slate-600">
          La prórroga (art. 12.3 RGPD) debe motivarse y notificarse al interesado dentro del primer mes.
        </p>
        <div>
          <label class="lbl">Motivo de la prórroga <span class="req">*</span></label>
          <textarea v-model="motivoProrroga" rows="4" required class="inp"></textarea>
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalProrroga = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit"
            class="text-sm px-4 h-9 rounded-lg bg-amber-600 text-white hover:bg-amber-700">Prorrogar</button>
        </div>
      </form>
    </BaseModal>

    <!-- Modal resolución -->
    <BaseModal v-model="modalResolucion"
      :title="modoDenegar ? 'Denegar solicitud' : 'Resolver solicitud favorablemente'" size="lg">
      <form @submit.prevent="resolver" class="space-y-3">
        <div>
          <label class="lbl">Resolución motivada <span class="req">*</span></label>
          <textarea v-model="textoResolucion" rows="6" required class="inp"
            :placeholder="modoDenegar ? 'Motiva la denegación con base legal…' : 'Describe la acción tomada (entrega de datos, rectificación, supresión…)'"></textarea>
        </div>
        <div>
          <label class="lbl">URL del documento de resolución</label>
          <input v-model="urlResolucion" type="url" class="inp" />
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalResolucion = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit"
            :class="modoDenegar ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700'"
            class="text-sm px-4 h-9 rounded-lg text-white">
            {{ modoDenegar ? 'Denegar' : 'Resolver' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_SOLICITUDES, REGISTRAR_SOLICITUD,
  INICIAR_TRAMITE_SOLICITUD, PRORROGAR_SOLICITUD, RESOLVER_SOLICITUD,
} from '@/modules/proteccion_datos/graphql/queries.js'

const TIPOS = [
  'ACCESO', 'RECTIFICACION', 'SUPRESION', 'LIMITACION',
  'PORTABILIDAD', 'OPOSICION', 'DECISION_AUTOMATIZADA',
]
const CANALES = ['EMAIL', 'WEB', 'PAPEL', 'PRESENCIAL', 'CORREO_POSTAL']

const loading = ref(false)
const solicitudes = ref([])
const busqueda = ref('')
const filtros = ref({ estado: '', tipo: '' })

const camposFiltro = [
  { key: 'estado', label: 'Estado', type: 'select', allLabel: 'Todos',
    options: ['PRESENTADA', 'EN_TRAMITE', 'PRORROGADA', 'RESUELTA', 'DENEGADA']
      .map(e => ({ value: e, label: e })) },
  { key: 'tipo', label: 'Tipo', type: 'select', allLabel: 'Todos',
    options: TIPOS.map(t => ({ value: t, label: t })) },
]

const columnas = [
  { key: 'codigoInterno',     label: 'Código' },
  { key: 'tipo',              label: 'Tipo' },
  { key: 'nombreSolicitante', label: 'Solicitante' },
  { key: 'fechaPresentacion', label: 'Presentada', align: 'center' },
  { key: 'plazo',             label: 'Plazo', align: 'center' },
  { key: 'estado',            label: 'Estado', align: 'center' },
]

const filtradas = computed(() => {
  let rows = solicitudes.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.codigoInterno || '').toLowerCase().includes(q) ||
      (r.nombreSolicitante || '').toLowerCase().includes(q) ||
      (r.documentoSolicitante || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.estado) rows = rows.filter(r => r.estado === filtros.value.estado)
  if (filtros.value.tipo)   rows = rows.filter(r => r.tipo === filtros.value.tipo)
  return rows
})

function badgeEstado(estado) {
  const map = {
    PRESENTADA: 'bg-blue-100 text-blue-700',
    EN_TRAMITE: 'bg-indigo-100 text-indigo-700',
    PRORROGADA: 'bg-amber-100 text-amber-700',
    RESUELTA:   'bg-emerald-100 text-emerald-700',
    DENEGADA:   'bg-rose-100 text-rose-700',
  }
  return map[estado] || 'bg-slate-100 text-slate-600'
}

function fechaFmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function enCerrado(s) {
  return s.estado === 'RESUELTA' || s.estado === 'DENEGADA'
}

function plazoTexto(s) {
  const limite = s.prorrogada && s.fechaLimiteProrroga ? s.fechaLimiteProrroga : s.fechaLimiteRespuesta
  if (!limite) return '—'
  if (enCerrado(s)) return 'Cerrada'
  const diff = Math.ceil((new Date(limite) - new Date()) / 86400000)
  if (diff < 0) return `Vencido (${Math.abs(diff)} días)`
  if (diff === 0) return 'Hoy'
  return `${diff} días`
}

function claseAlerta(s) {
  if (enCerrado(s)) return 'text-slate-500'
  const limite = s.prorrogada && s.fechaLimiteProrroga ? s.fechaLimiteProrroga : s.fechaLimiteRespuesta
  if (!limite) return ''
  const diff = Math.ceil((new Date(limite) - new Date()) / 86400000)
  if (diff < 0) return 'text-red-600 font-semibold'
  if (diff <= 7) return 'text-amber-700 font-semibold'
  return 'text-slate-600'
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_SOLICITUDES)
    solicitudes.value = [...(data.rgpdSolicitudesDerechos || [])].sort((a, b) =>
      new Date(b.fechaPresentacion) - new Date(a.fechaPresentacion))
  } finally {
    loading.value = false
  }
}

// ── Alta ───────────────────────────────────────────────────────────────────
const modalAlta = ref(false)
const guardando = ref(false)
const alta = ref(estadoAlta())

function estadoAlta() {
  return {
    tipo: '', canalPresentacion: 'EMAIL',
    nombreSolicitante: '', documentoSolicitante: '',
    emailSolicitante: '', telefonoSolicitante: '',
    fechaPresentacion: new Date().toISOString().slice(0, 10),
    descripcionSolicitud: '',
  }
}

function abrirAlta() {
  alta.value = estadoAlta()
  modalAlta.value = true
}

async function crear() {
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_SOLICITUD, alta.value)
    modalAlta.value = false
    await cargar()
  } catch (e) {
    alert('Error al registrar: ' + (e.message || e))
  } finally {
    guardando.value = false
  }
}

// ── Detalle y tramitación ──────────────────────────────────────────────────
const modalDetalle = ref(false)
const seleccionada = ref(null)

function abrirDetalle(fila) {
  seleccionada.value = fila
  modalDetalle.value = true
}

async function iniciar(s) {
  try {
    await executeMutation(INICIAR_TRAMITE_SOLICITUD, { solicitudId: s.id })
    await cargar()
    seleccionada.value = solicitudes.value.find(x => x.id === s.id) || s
  } catch (e) {
    alert('Error: ' + (e.message || e))
  }
}

// ── Prórroga ───────────────────────────────────────────────────────────────
const modalProrroga = ref(false)
const motivoProrroga = ref('')

function abrirProrroga() {
  motivoProrroga.value = ''
  modalProrroga.value = true
}

async function prorrogar() {
  try {
    await executeMutation(PRORROGAR_SOLICITUD, {
      solicitudId: seleccionada.value.id,
      motivoProrroga: motivoProrroga.value,
    })
    modalProrroga.value = false
    await cargar()
    seleccionada.value = solicitudes.value.find(x => x.id === seleccionada.value.id) || seleccionada.value
  } catch (e) {
    alert('Error: ' + (e.message || e))
  }
}

// ── Resolución / denegación ────────────────────────────────────────────────
const modalResolucion = ref(false)
const modoDenegar = ref(false)
const textoResolucion = ref('')
const urlResolucion = ref('')

function abrirResolver(denegar) {
  modoDenegar.value = denegar
  textoResolucion.value = ''
  urlResolucion.value = ''
  modalResolucion.value = true
}

async function resolver() {
  try {
    await executeMutation(RESOLVER_SOLICITUD, {
      solicitudId: seleccionada.value.id,
      resolucion: textoResolucion.value,
      denegada: modoDenegar.value,
      documentoResolucionUrl: urlResolucion.value || null,
    })
    modalResolucion.value = false
    modalDetalle.value = false
    await cargar()
  } catch (e) {
    alert('Error: ' + (e.message || e))
  }
}

onMounted(cargar)
</script>

<style scoped>
.lbl { @apply block text-xs font-medium text-slate-700 mb-1; }
.req { @apply text-red-500; }
.inp {
  @apply h-10 w-full px-3 text-sm border border-slate-300 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
textarea.inp { @apply h-auto py-2; }
select.inp { @apply pr-8; }
</style>
