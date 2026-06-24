<template>
  <AppLayout
    title="Brechas de seguridad"
    subtitle="Incidencias y asistente de notificación a la AEPD en 72 h (art. 33/34 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por código o descripción…"
      create-label="+ Registrar brecha"
      :fields="camposFiltro"
      @create="abrirAlta()"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando brechas…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtradas"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        vacio-texto="No hay brechas registradas"
        @row-click="abrirDetalle"
      >
        <template #cell-codigoInterno="{ fila }">
          <span class="font-mono text-xs">{{ fila.codigoInterno }}</span>
        </template>
        <template #cell-severidad="{ fila }">
          <span :class="badgeSeveridad(fila.severidad)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.severidad }}
          </span>
        </template>
        <template #cell-origen="{ fila }">
          <span class="text-xs text-slate-600">{{ fila.origen }}</span>
        </template>
        <template #cell-plazo="{ fila }">
          <span :class="claseAlerta72(fila)" class="text-xs">{{ texto72h(fila) }}</span>
        </template>
        <template #cell-cerrada="{ fila }">
          <span :class="fila.cerrada ? 'text-slate-500' : 'text-amber-700'" class="text-xs">
            {{ fila.cerrada ? 'Cerrada' : 'Abierta' }}
          </span>
        </template>
      </ResponsiveTable>
    </div>

    <!-- Modal alta -->
    <AppDrawer v-model="modalAlta" title="Registrar brecha de seguridad" size="xl">
      <form @submit.prevent="crear" class="space-y-4">
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
          ⏰ El plazo de notificación a la AEPD (art. 33 RGPD) es de <strong>72 horas</strong> desde
          que se tiene conocimiento de la brecha.
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="md:col-span-2">
            <label class="lbl">Descripción <span class="req">*</span></label>
            <textarea v-model="alta.descripcion" rows="3" required class="inp"
              placeholder="Qué ocurrió, cómo, alcance…"></textarea>
          </div>
          <div>
            <label class="lbl">Origen <span class="req">*</span></label>
            <select v-model="alta.origen" required class="inp">
              <option value="">Selecciona…</option>
              <option v-for="o in ORIGENES" :key="o" :value="o">{{ o }}</option>
            </select>
          </div>
          <div>
            <label class="lbl">Severidad <span class="req">*</span></label>
            <select v-model="alta.severidad" required class="inp">
              <option v-for="s in SEVERIDADES" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div>
            <label class="lbl">Fecha/hora detección <span class="req">*</span></label>
            <input v-model="alta.fechaDeteccion" type="datetime-local" required class="inp" />
          </div>
          <div>
            <label class="lbl">Fecha estimada de ocurrencia</label>
            <input v-model="alta.fechaOcurrencia" type="date" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Datos afectados</label>
            <input v-model="alta.datosAfectados" type="text" class="inp"
              placeholder="Identificativos, contacto, salud, económicos…" />
          </div>
          <div>
            <label class="lbl">Nº de personas afectadas</label>
            <input v-model.number="alta.personasAfectadasNum" type="number" min="0" class="inp" />
          </div>
          <div class="flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="alta.datosSensiblesAfectados" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Afecta a categorías especiales (art. 9)</span>
            </label>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Medidas inmediatas adoptadas</label>
            <textarea v-model="alta.medidasInmediatas" rows="3" class="inp"
              placeholder="Aislamiento, bloqueo de cuentas, copias de seguridad…"></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalAlta = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit" :disabled="guardando"
            class="text-sm px-4 h-9 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">
            {{ guardando ? 'Registrando…' : 'Registrar brecha' }}
          </button>
        </div>
      </form>
    </AppDrawer>

    <!-- Modal detalle / asistente -->
    <AppDrawer v-model="modalDetalle"
      :title="seleccionada ? `Brecha ${seleccionada.codigoInterno}` : ''" size="xl">
      <div v-if="seleccionada" class="space-y-4">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div><span class="text-slate-500">Severidad:</span>
            <span :class="badgeSeveridad(seleccionada.severidad)" class="text-[10px] uppercase rounded-full px-2 py-0.5 ml-1">
              {{ seleccionada.severidad }}
            </span>
          </div>
          <div><span class="text-slate-500">Origen:</span> {{ seleccionada.origen }}</div>
          <div><span class="text-slate-500">Detectada:</span> {{ fechaHoraFmt(seleccionada.fechaDeteccion) }}</div>
          <div><span class="text-slate-500">Ocurrencia:</span> {{ fechaFmt(seleccionada.fechaOcurrencia) }}</div>
          <div><span class="text-slate-500">Personas afectadas:</span> {{ seleccionada.personasAfectadasNum ?? '—' }}</div>
          <div><span class="text-slate-500">Datos sensibles:</span>
            <span v-if="seleccionada.datosSensiblesAfectados" class="text-rose-700">⚠️ Sí</span>
            <span v-else class="text-slate-500">No</span>
          </div>
        </div>

        <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <div class="text-xs text-slate-500 mb-1">Descripción</div>
          <div class="text-sm whitespace-pre-line">{{ seleccionada.descripcion }}</div>
        </div>

        <div v-if="seleccionada.datosAfectados" class="text-sm">
          <span class="text-slate-500">Datos afectados:</span> {{ seleccionada.datosAfectados }}
        </div>

        <div v-if="seleccionada.medidasInmediatas" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <div class="text-xs text-slate-500 mb-1">Medidas inmediatas</div>
          <div class="text-sm whitespace-pre-line">{{ seleccionada.medidasInmediatas }}</div>
        </div>

        <!-- Plazo 72h -->
        <div :class="claseBox72(seleccionada)" class="border rounded-lg p-3 text-sm">
          <div class="font-medium mb-1">⏰ Plazo notificación AEPD (art. 33)</div>
          <div>{{ texto72hLargo(seleccionada) }}</div>
        </div>

        <!-- Notificación AEPD -->
        <div v-if="seleccionada.notificadaAepd" class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-sm">
          <div class="font-medium text-emerald-800 mb-1">✅ Notificada a la AEPD</div>
          <div class="text-emerald-700">Fecha: {{ fechaHoraFmt(seleccionada.fechaNotificacionAepd) }}</div>
          <div v-if="seleccionada.referenciaAepd" class="text-emerald-700">Referencia: {{ seleccionada.referenciaAepd }}</div>
          <a v-if="seleccionada.notificacionAepdDocumentoUrl" :href="seleccionada.notificacionAepdDocumentoUrl" target="_blank"
            class="text-emerald-700 hover:underline text-xs mt-1 inline-block">📄 Documento</a>
        </div>

        <!-- Resolución -->
        <div v-if="seleccionada.cerrada" class="bg-slate-100 border border-slate-200 rounded-lg p-3 text-sm">
          <div class="font-medium text-slate-700 mb-1">Brecha cerrada</div>
          <div class="text-slate-600 text-xs">{{ fechaHoraFmt(seleccionada.fechaCierre) }}</div>
          <div v-if="seleccionada.medidasCorrectivas" class="text-slate-600 mt-2 whitespace-pre-line">{{ seleccionada.medidasCorrectivas }}</div>
        </div>

        <!-- Acciones -->
        <div v-if="!seleccionada.cerrada" class="flex flex-wrap gap-2 pt-3 border-t border-slate-200">
          <button v-if="!seleccionada.notificadaAepd" type="button"
            @click="abrirNotificar"
            class="text-sm px-3 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
            Notificar a la AEPD
          </button>
          <button type="button"
            @click="abrirCerrar"
            class="text-sm px-3 h-9 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 ml-auto">
            Cerrar brecha
          </button>
        </div>
      </div>
    </AppDrawer>

    <!-- Modal notificar AEPD -->
    <AppDrawer v-model="modalNotificar" title="Notificar brecha a la AEPD" size="lg">
      <form @submit.prevent="notificar" class="space-y-3">
        <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-xs text-indigo-800">
          📋 Sede electrónica AEPD: <a href="https://sedeagpd.gob.es" target="_blank" class="underline">sedeagpd.gob.es</a>
          — formulario de notificación de brechas. Una vez presentada, registra aquí la fecha y la referencia.
        </div>
        <div>
          <label class="lbl">Fecha/hora de notificación <span class="req">*</span></label>
          <input v-model="notif.fecha" type="datetime-local" required class="inp" />
        </div>
        <div>
          <label class="lbl">Referencia AEPD</label>
          <input v-model="notif.referencia" type="text" class="inp" placeholder="Nº de expediente de la AEPD" />
        </div>
        <div>
          <label class="lbl">URL del acuse / documento</label>
          <input v-model="notif.url" type="url" class="inp" />
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalNotificar = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit"
            class="text-sm px-4 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">Registrar notificación</button>
        </div>
      </form>
    </AppDrawer>

    <!-- Modal cerrar -->
    <AppDrawer v-model="modalCerrar" title="Cerrar brecha" size="lg">
      <form @submit.prevent="cerrar" class="space-y-3">
        <div>
          <label class="lbl">Medidas correctivas adoptadas <span class="req">*</span></label>
          <textarea v-model="medidasCierre" rows="6" required class="inp"
            placeholder="Acciones para evitar la repetición: parches, formación, revisión de procesos…"></textarea>
        </div>
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalCerrar = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit"
            class="text-sm px-4 h-9 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700">Cerrar brecha</button>
        </div>
      </form>
    </AppDrawer>
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_BRECHAS, REGISTRAR_BRECHA, NOTIFICAR_BRECHA_AEPD, CERRAR_BRECHA,
} from '@/modules/proteccion_datos/graphql/queries.js'

const ORIGENES = [
  'CIBERATAQUE', 'PERDIDA_DISPOSITIVO', 'ROBO_DISPOSITIVO', 'ENVIO_ERRONEO',
  'ERROR_HUMANO', 'ACCESO_NO_AUTORIZADO', 'FALLO_TECNICO', 'OTROS',
]
const SEVERIDADES = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA']

const loading = ref(false)
const brechas = ref([])
const busqueda = ref('')
const filtros = ref({ severidad: '', cerrada: '' })

const camposFiltro = [
  { key: 'severidad', label: 'Severidad', type: 'select', allLabel: 'Todas',
    options: SEVERIDADES.map(s => ({ value: s, label: s })) },
  { key: 'cerrada', label: 'Estado', type: 'select', allLabel: 'Todas',
    options: [{ value: 'false', label: 'Abiertas' }, { value: 'true', label: 'Cerradas' }] },
]

const columnas = [
  { key: 'codigoInterno',   label: 'Código' },
  { key: 'severidad',       label: 'Severidad', align: 'center' },
  { key: 'origen',          label: 'Origen' },
  { key: 'descripcion',     label: 'Descripción' },
  { key: 'plazo',           label: 'Plazo AEPD', align: 'center' },
  { key: 'cerrada',         label: 'Estado', align: 'center' },
]

const filtradas = computed(() => {
  let rows = brechas.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.codigoInterno || '').toLowerCase().includes(q) ||
      (r.descripcion || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.severidad) rows = rows.filter(r => r.severidad === filtros.value.severidad)
  if (filtros.value.cerrada === 'true')  rows = rows.filter(r => r.cerrada)
  if (filtros.value.cerrada === 'false') rows = rows.filter(r => !r.cerrada)
  return rows
})

function badgeSeveridad(s) {
  const map = {
    BAJA:     'bg-slate-100 text-slate-600',
    MEDIA:    'bg-amber-100 text-amber-700',
    ALTA:     'bg-orange-100 text-orange-700',
    CRITICA:  'bg-rose-100 text-rose-700',
  }
  return map[s] || 'bg-slate-100 text-slate-500'
}

function fechaFmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function fechaHoraFmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function horasRestantes72(b) {
  if (!b.fechaDeteccion) return null
  const ahora = new Date()
  const limite = new Date(new Date(b.fechaDeteccion).getTime() + 72 * 3600 * 1000)
  return Math.floor((limite - ahora) / 3600000)
}

function texto72h(b) {
  if (b.notificadaAepd) return '✓ Notificada'
  const h = horasRestantes72(b)
  if (h === null) return '—'
  if (h < 0) return `Vencido (${Math.abs(h)} h)`
  return `${h} h restantes`
}
function texto72hLargo(b) {
  if (b.notificadaAepd) return 'Brecha ya notificada a la AEPD.'
  const h = horasRestantes72(b)
  if (h === null) return 'Fecha de detección desconocida.'
  if (h < 0) return `El plazo de 72 horas ha vencido hace ${Math.abs(h)} h. Notifica con justificación del retraso.`
  return `Quedan ${h} h para notificar a la AEPD.`
}
function claseAlerta72(b) {
  if (b.notificadaAepd) return 'text-emerald-700'
  const h = horasRestantes72(b)
  if (h === null) return ''
  if (h < 0) return 'text-red-600 font-semibold'
  if (h < 12) return 'text-amber-700 font-semibold'
  return 'text-slate-600'
}
function claseBox72(b) {
  if (b.notificadaAepd) return 'bg-emerald-50 border-emerald-200 text-emerald-800'
  const h = horasRestantes72(b)
  if (h !== null && h < 0) return 'bg-red-50 border-red-200 text-red-800'
  if (h !== null && h < 12) return 'bg-amber-50 border-amber-200 text-amber-800'
  return 'bg-indigo-50 border-indigo-200 text-indigo-800'
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_BRECHAS)
    brechas.value = [...(data.rgpdBrechasSeguridad || [])].sort((a, b) =>
      new Date(b.fechaDeteccion) - new Date(a.fechaDeteccion))
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
    descripcion: '', origen: '', severidad: 'MEDIA',
    fechaDeteccion: new Date().toISOString().slice(0, 16),
    fechaOcurrencia: null,
    datosAfectados: '', personasAfectadasNum: null, datosSensiblesAfectados: false,
    medidasInmediatas: '',
  }
}

function abrirAlta() {
  alta.value = estadoAlta()
  modalAlta.value = true
}

async function crear() {
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_BRECHA, {
      ...alta.value,
      fechaDeteccion: new Date(alta.value.fechaDeteccion).toISOString(),
    })
    modalAlta.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error: ' + (e.message || e))
  } finally {
    guardando.value = false
  }
}

// ── Detalle / acciones ────────────────────────────────────────────────────
const modalDetalle = ref(false)
const seleccionada = ref(null)

function abrirDetalle(fila) {
  seleccionada.value = fila
  modalDetalle.value = true
}

const modalNotificar = ref(false)
const notif = ref({ fecha: '', referencia: '', url: '' })

function abrirNotificar() {
  notif.value = {
    fecha: new Date().toISOString().slice(0, 16),
    referencia: '', url: '',
  }
  modalNotificar.value = true
}

async function notificar() {
  try {
    await executeMutation(NOTIFICAR_BRECHA_AEPD, {
      brechaId: seleccionada.value.id,
      fechaNotificacion: new Date(notif.value.fecha).toISOString(),
      referenciaAepd: notif.value.referencia || null,
      documentoUrl: notif.value.url || null,
    })
    modalNotificar.value = false
    await cargar()
    seleccionada.value = brechas.value.find(x => x.id === seleccionada.value.id) || seleccionada.value
  } catch (e) {
    useToast().error('Error: ' + (e.message || e))
  }
}

const modalCerrar = ref(false)
const medidasCierre = ref('')

function abrirCerrar() {
  medidasCierre.value = ''
  modalCerrar.value = true
}

async function cerrar() {
  try {
    await executeMutation(CERRAR_BRECHA, {
      brechaId: seleccionada.value.id,
      medidasCorrectivas: medidasCierre.value,
    })
    modalCerrar.value = false
    modalDetalle.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error: ' + (e.message || e))
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
