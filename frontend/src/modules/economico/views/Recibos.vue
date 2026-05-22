<template>
  <AppLayout title="Recibos" subtitle="Emisión y gestión de recibos numerados de cuotas">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por número, nombre o email…"
      create-label="+ Emitir lote"
      :fields="camposFiltro"
      :description="descripcionFiltros"
      @create="abrirModalLote()"
    />

    <div class="text-xs text-slate-500 mt-2 mb-3 px-1 flex items-center gap-3">
      <span>{{ recibosFiltrados.length }} de {{ recibos.length }} recibos</span>
      <span class="text-slate-300">·</span>
      <span class="text-green-700"><strong>{{ contarEstado('COBRADO') }}</strong> cobrados</span>
      <span class="text-amber-700"><strong>{{ contarEstado('EMITIDO') }}</strong> emitidos</span>
      <span class="text-red-700"><strong>{{ contarEstado('FALLIDO') }}</strong> fallidos</span>
      <span class="text-slate-500"><strong>{{ contarEstado('ANULADO') }}</strong> anulados</span>
    </div>

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="recibosFiltrados.length" class="bg-white border border-slate-200 rounded-xl sm:overflow-hidden p-3 sm:p-0">
      <ResponsiveTable
        :columnas="columnasRecibos"
        :filas="recibosFiltrados"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        @row-click="abrirDetalle"
      >
        <template #cell-numeroRecibo="{ fila }">
          <span class="font-mono text-xs text-slate-700">{{ fila.numeroRecibo }}</span>
        </template>
        <template #cell-socio="{ fila }">{{ socioNombre(fila) }}</template>
        <template #cell-concepto="{ fila }">
          <span class="text-slate-600 text-xs">{{ fila.concepto }}</span>
        </template>
        <template #cell-importe="{ fila }">
          <span class="font-mono">{{ fmt(fila.importe) }}</span>
        </template>
        <template #cell-modo="{ fila }">
          <span class="text-[10px] uppercase">{{ fila.modoCobro || '—' }}</span>
        </template>
        <template #cell-estado="{ fila }">
          <span :class="badgeEstado(fila.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.estado }}
          </span>
        </template>
        <template #cell-fechaEmision="{ fila }">
          <span class="text-xs text-slate-500">{{ fechaFmt(fila.fechaEmision) }}</span>
        </template>
        <template #cell-fechaCobro="{ fila }">
          <span class="text-xs text-slate-500">{{ fechaFmt(fila.fechaCobro) }}</span>
        </template>
      </ResponsiveTable>
    </div>

    <p v-else class="text-center text-slate-400 py-12 text-sm border border-dashed border-slate-200 rounded-xl">
      No hay recibos con los filtros aplicados.
    </p>

    <ErrorAlert v-if="error" :message="error" />

    <!-- Modal: emitir lote -->
    <div v-if="modalLote" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalLote = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Emitir lote de recibos</h3>
          <p class="text-xs text-slate-500 mt-0.5">Genera recibos para todas las cuotas Pendientes sin recibo emitido.</p>
        </div>
        <div class="px-6 py-5 space-y-3">
          <div>
            <label class="label">Ejercicio *</label>
            <input type="number" v-model.number="formLote.ejercicio" class="input" :min="2000" :max="2099" />
          </div>
          <div>
            <label class="label">Tipo</label>
            <select v-model="formLote.tipo" class="input">
              <option value="CUOTA_ORDINARIA">Cuota ordinaria</option>
              <option value="EXTRAORDINARIA">Extraordinaria</option>
            </select>
          </div>
          <div>
            <label class="label">Concepto</label>
            <input v-model="formLote.concepto" class="input"
                   :placeholder="`Cuota ordinaria ejercicio ${formLote.ejercicio}`" />
          </div>
          <div>
            <label class="label">Fecha vencimiento</label>
            <input type="date" v-model="formLote.fechaVencimiento" class="input" />
          </div>
          <ErrorAlert v-if="formLote.error" :message="formLote.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalLote = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="emitirLote()" :disabled="ocupado" class="btn-primary text-sm">
            {{ ocupado ? 'Emitiendo…' : 'Emitir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: detalle de recibo -->
    <div v-if="reciboDetalle" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="reciboDetalle = null">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-slate-800 font-mono">{{ reciboDetalle.numeroRecibo }}</h3>
            <p class="text-xs text-slate-500 mt-0.5">
              <span :class="badgeEstado(reciboDetalle.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ reciboDetalle.estado }}
              </span>
            </p>
          </div>
          <button @click="reciboDetalle = null" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm">
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <dt class="text-xs text-slate-500">Socio</dt>
              <dd class="font-medium text-slate-800">{{ socioNombre(reciboDetalle) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Ejercicio</dt>
              <dd class="text-slate-800">{{ reciboDetalle.ejercicio }}</dd>
            </div>
            <div class="col-span-2">
              <dt class="text-xs text-slate-500">Concepto</dt>
              <dd class="text-slate-800">{{ reciboDetalle.concepto }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Importe</dt>
              <dd class="font-mono text-slate-800">{{ fmt(reciboDetalle.importe) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Pagado</dt>
              <dd class="font-mono text-slate-800">{{ fmt(reciboDetalle.importePagado) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Modo cobro</dt>
              <dd class="text-slate-800">{{ reciboDetalle.modoCobro || '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Tipo</dt>
              <dd class="text-slate-800">{{ reciboDetalle.tipo }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">F. emisión</dt>
              <dd class="text-slate-800">{{ fechaFmt(reciboDetalle.fechaEmision) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">F. cobro</dt>
              <dd class="text-slate-800">{{ fechaFmt(reciboDetalle.fechaCobro) }}</dd>
            </div>
            <div v-if="reciboDetalle.observaciones" class="col-span-2">
              <dt class="text-xs text-slate-500">Observaciones</dt>
              <dd class="text-xs text-slate-600 whitespace-pre-wrap">{{ reciboDetalle.observaciones }}</dd>
            </div>
          </dl>

          <!-- Formulario marcar cobrado (D5.1) -->
          <div v-if="modalCobrar" class="border-t border-slate-200 pt-3 space-y-2">
            <h4 class="font-medium text-sm text-slate-700">Marcar como cobrado</h4>
            <div>
              <label class="label">Cuenta bancaria de destino *</label>
              <select v-model="formCobrar.cuentaBancariaId" class="input">
                <option :value="null">— Selecciona cuenta —</option>
                <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
                  {{ c.nombre }}{{ c.iban ? ` — ${c.iban}` : '' }}
                </option>
              </select>
              <p v-if="!cuentasBancarias.length" class="text-xs text-amber-700 mt-1">
                No hay cuentas bancarias activas configuradas.
              </p>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="label">Modo cobro *</label>
                <select v-model="formCobrar.modoCobro" class="input">
                  <option value="TRANSFERENCIA">Transferencia</option>
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="TARJETA">Tarjeta</option>
                  <option value="MANUAL">Manual / otro</option>
                </select>
              </div>
              <div>
                <label class="label">Fecha cobro *</label>
                <input type="date" v-model="formCobrar.fechaCobro" class="input" />
              </div>
            </div>
            <div>
              <label class="label">Referencia</label>
              <input v-model="formCobrar.referencia" class="input"
                     placeholder="Núm. transferencia, ticket, etc. (opcional)" />
            </div>
            <ErrorAlert v-if="formCobrar.error" :message="formCobrar.error" />
            <p class="text-xs text-slate-500">
              Al confirmar se registra el cobro en el recibo y en la cuota, y se genera el apunte
              de caja con su asiento contable.
            </p>
          </div>

          <!-- Formulario enviar email -->
          <div v-if="modalEmail" class="border-t border-slate-200 pt-3 space-y-2">
            <h4 class="font-medium text-sm text-slate-700">Enviar PDF al socio</h4>
            <div>
              <label class="label">Plantilla de email</label>
              <select v-model="formEmail.plantillaId" class="input">
                <option :value="null">— Selecciona plantilla —</option>
                <option v-for="p in plantillas" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
              <p v-if="!plantillas.length" class="text-xs text-amber-700 mt-1">
                No hay plantillas configuradas para el módulo Económico. Crea una en Comunicación Interna.
              </p>
            </div>
            <ErrorAlert v-if="formEmail.error" :message="formEmail.error" />
          </div>
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex flex-wrap justify-end gap-2">
          <button v-if="!modalCobrar && !modalEmail" @click="descargarPdf(reciboDetalle)"
                  :disabled="ocupado" class="btn-secondary text-xs">↓ PDF</button>
          <button v-if="!modalCobrar && !modalEmail && reciboDetalle.estado !== 'COBRADO' && reciboDetalle.estado !== 'ANULADO'"
                  @click="abrirCobrar()" class="btn-secondary text-xs">Marcar cobrado</button>
          <button v-if="!modalCobrar && !modalEmail" @click="abrirEmail()"
                  class="btn-secondary text-xs">Enviar al socio</button>
          <button v-if="!modalCobrar && !modalEmail && reciboDetalle.estado !== 'COBRADO' && reciboDetalle.estado !== 'ANULADO'"
                  @click="anular(reciboDetalle)" :disabled="ocupado" class="btn-danger text-xs">Anular</button>

          <!-- Acciones de los sub-formularios -->
          <template v-if="modalCobrar">
            <button @click="modalCobrar = false" class="btn-secondary text-xs">Cancelar</button>
            <button @click="confirmarCobrado()" :disabled="ocupado" class="btn-primary text-xs">
              {{ ocupado ? 'Registrando…' : 'Confirmar cobro' }}
            </button>
          </template>
          <template v-if="modalEmail">
            <button @click="modalEmail = false" class="btn-secondary text-xs">Cancelar</button>
            <button @click="confirmarEmail()" :disabled="ocupado || !formEmail.plantillaId" class="btn-primary text-xs">
              {{ ocupado ? 'Enviando…' : 'Enviar' }}
            </button>
          </template>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_RECIBOS,
  EMITIR_RECIBOS_LOTE,
  MARCAR_RECIBO_COBRADO,
  ANULAR_RECIBO,
  DESCARGAR_RECIBO_PDF,
  ENVIAR_RECIBO_EMAIL,
  GET_PLANTILLAS_EMAIL_ECONOMICO,
  GET_CUENTAS_BANCARIAS_ACTIVAS,
} from '@/graphql/queries/economico'

const toast = useToast()

const { query, mutation, loading } = useGraphQL()

const recibos = ref([])

// Columnas de la tabla responsive (Socio = cabecera de tarjeta en móvil)
const columnasRecibos = [
  { key: 'socio',         label: 'Socio' },
  { key: 'numeroRecibo',  label: 'Nº Recibo' },
  { key: 'concepto',      label: 'Concepto', ocultaEnMovil: true },
  { key: 'importe',       label: 'Importe', align: 'right' },
  { key: 'modo',          label: 'Modo', align: 'center' },
  { key: 'estado',        label: 'Estado', align: 'center' },
  { key: 'fechaEmision',  label: 'F. emisión', align: 'center' },
  { key: 'fechaCobro',    label: 'F. cobro', align: 'center' },
]
const plantillas = ref([])
const cuentasBancarias = ref([])
const error = ref('')
const ocupado = ref(false)

// Detalle
const reciboDetalle = ref(null)
const modalCobrar = ref(false)
const modalEmail = ref(false)
const formCobrar = ref({
  cuentaBancariaId: null,
  modoCobro: 'TRANSFERENCIA',
  fechaCobro: '',
  referencia: '',
  error: '',
})
const formEmail = ref({ plantillaId: null, error: '' })

// Lote
const modalLote = ref(false)
const formLote = ref({
  ejercicio: new Date().getFullYear(),
  tipo: 'CUOTA_ORDINARIA',
  concepto: '',
  fechaVencimiento: '',
  error: '',
})

// Filtros
const busqueda = ref('')
const filtros = ref({ ejercicio: null, tipo: [], estado: [] })

const camposFiltro = computed(() => [
  {
    key: 'ejercicio', label: 'Ejercicio', type: 'select',
    options: anosDisponibles.value.map(y => ({ value: y, label: String(y) })),
    allLabel: 'Todos los ejercicios',
  },
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect',
    options: [
      { value: 'CUOTA_ORDINARIA',  label: 'Cuota ordinaria' },
      { value: 'EXTRAORDINARIA',   label: 'Extraordinaria' },
      { value: 'REENVIO',          label: 'Reenvío' },
    ],
    allLabel: 'Todos los tipos',
  },
  {
    key: 'estado', label: 'Estado', type: 'multiselect',
    options: [
      { value: 'EMITIDO',  label: 'Emitido' },
      { value: 'COBRADO',  label: 'Cobrado' },
      { value: 'FALLIDO',  label: 'Fallido' },
      { value: 'ANULADO',  label: 'Anulado' },
    ],
    allLabel: 'Todos los estados',
  },
])

const descripcionFiltros = computed(() => {
  const parts = []
  if (filtros.value.ejercicio) parts.push(`ejercicio ${filtros.value.ejercicio}`)
  if (filtros.value.tipo?.length) parts.push(`${filtros.value.tipo.length} tipo(s)`)
  if (filtros.value.estado?.length) parts.push(`${filtros.value.estado.length} estado(s)`)
  return parts.join(' · ')
})

const anosDisponibles = computed(() =>
  [...new Set(recibos.value.map(r => r.ejercicio).filter(Boolean))].sort((a, b) => b - a)
)

const recibosFiltrados = computed(() => {
  const q = (busqueda.value || '').toLowerCase().trim()
  return recibos.value.filter(r => {
    if (filtros.value.ejercicio && r.ejercicio !== filtros.value.ejercicio) return false
    if (filtros.value.tipo?.length && !filtros.value.tipo.includes(r.tipo)) return false
    if (filtros.value.estado?.length && !filtros.value.estado.includes(r.estado)) return false
    if (q) {
      const nombre = socioNombre(r).toLowerCase()
      const email = (r.miembro?.email || '').toLowerCase()
      const num = (r.numeroRecibo || '').toLowerCase()
      if (!nombre.includes(q) && !email.includes(q) && !num.includes(q)) return false
    }
    return true
  })
})

const contarEstado = (e) => recibos.value.filter(r => r.estado === e).length

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  error.value = ''
  try {
    const data = await query(GET_RECIBOS)
    recibos.value = (data.recibos || []).slice().sort((a, b) =>
      (b.numeroRecibo || '').localeCompare(a.numeroRecibo || '')
    )
  } catch (e) {
    error.value = 'Error al cargar los recibos'
    console.error(e)
  }
}

const cargarPlantillas = async () => {
  try {
    const data = await query(GET_PLANTILLAS_EMAIL_ECONOMICO)
    plantillas.value = data.plantillasEmail || []
  } catch (e) { console.error('Error cargando plantillas:', e) }
}

const cargarCuentasBancarias = async () => {
  try {
    const data = await query(GET_CUENTAS_BANCARIAS_ACTIVAS)
    cuentasBancarias.value = (data.cuentasBancarias || []).filter(c => c.activa)
  } catch (e) { console.error('Error cargando cuentas:', e) }
}

// ── Acciones lote ──────────────────────────────────────────────────────────
const abrirModalLote = () => {
  formLote.value = {
    ejercicio: new Date().getFullYear(),
    tipo: 'CUOTA_ORDINARIA',
    concepto: '',
    fechaVencimiento: '',
    error: '',
  }
  modalLote.value = true
}

const emitirLote = async () => {
  formLote.value.error = ''
  ocupado.value = true
  try {
    await mutation(EMITIR_RECIBOS_LOTE, {
      ejercicio: formLote.value.ejercicio,
      tipo: formLote.value.tipo,
      concepto: formLote.value.concepto || null,
      fechaVencimiento: formLote.value.fechaVencimiento || null,
    })
    modalLote.value = false
    await cargar()
  } catch (e) {
    formLote.value.error = e.message || 'Error al emitir el lote'
  } finally {
    ocupado.value = false
  }
}

// ── Detalle ────────────────────────────────────────────────────────────────
const abrirDetalle = (r) => {
  reciboDetalle.value = r
  modalCobrar.value = false
  modalEmail.value = false
}

const abrirCobrar = async () => {
  formCobrar.value = {
    cuentaBancariaId: cuentasBancarias.value.length === 1 ? cuentasBancarias.value[0].id : null,
    modoCobro: 'TRANSFERENCIA',
    fechaCobro: new Date().toISOString().split('T')[0],
    referencia: '',
    error: '',
  }
  if (!cuentasBancarias.value.length) await cargarCuentasBancarias()
  modalCobrar.value = true
}

const confirmarCobrado = async () => {
  formCobrar.value.error = ''
  if (!formCobrar.value.cuentaBancariaId) {
    formCobrar.value.error = 'Selecciona la cuenta bancaria de destino'; return
  }
  if (!formCobrar.value.fechaCobro) { formCobrar.value.error = 'Indica la fecha de cobro'; return }
  ocupado.value = true
  try {
    await mutation(MARCAR_RECIBO_COBRADO, {
      reciboId: reciboDetalle.value.id,
      cuentaBancariaId: formCobrar.value.cuentaBancariaId,
      modoCobro: formCobrar.value.modoCobro,
      fechaCobro: formCobrar.value.fechaCobro,
      referencia: formCobrar.value.referencia || null,
    })
    modalCobrar.value = false
    reciboDetalle.value = null
    await cargar()
  } catch (e) {
    formCobrar.value.error = e.message || 'Error al registrar el cobro'
  } finally { ocupado.value = false }
}

const anular = async (r) => {
  const motivo = prompt(`¿Anular el recibo ${r.numeroRecibo}? Indica el motivo (opcional):`)
  if (motivo === null) return
  ocupado.value = true
  try {
    await mutation(ANULAR_RECIBO, { reciboId: r.id, motivo: motivo || null })
    reciboDetalle.value = null
    await cargar()
  } catch (e) {
    error.value = e.message || 'Error al anular'
  } finally { ocupado.value = false }
}

const descargarPdf = async (r) => {
  ocupado.value = true
  try {
    const data = await mutation(DESCARGAR_RECIBO_PDF, { reciboId: r.id })
    const b64 = data.descargarReciboPdf
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${r.numeroRecibo}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message || 'Error al descargar el PDF'
  } finally { ocupado.value = false }
}

const abrirEmail = async () => {
  formEmail.value = { plantillaId: null, error: '' }
  if (!plantillas.value.length) await cargarPlantillas()
  modalEmail.value = true
}

const confirmarEmail = async () => {
  formEmail.value.error = ''
  if (!formEmail.value.plantillaId) { formEmail.value.error = 'Selecciona una plantilla'; return }
  ocupado.value = true
  try {
    await mutation(ENVIAR_RECIBO_EMAIL, {
      reciboId: reciboDetalle.value.id,
      plantillaEmailId: formEmail.value.plantillaId,
    })
    modalEmail.value = false
    reciboDetalle.value = null
    toast.error('Solicitud de envío registrada. El envío real se procesará por el módulo de Comunicación Interna.')
  } catch (e) {
    formEmail.value.error = e.message || 'Error al enviar'
  } finally { ocupado.value = false }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const socioNombre = (r) => {
  const m = r.miembro
  if (!m) return '—'
  return `${m.nombre || ''} ${m.apellido1 || ''} ${m.apellido2 || ''}`.trim() || '—'
}
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

const badgeEstado = (e) => ({
  EMITIDO: 'bg-amber-100 text-amber-700',
  COBRADO: 'bg-green-100 text-green-700',
  FALLIDO: 'bg-red-100 text-red-700',
  ANULADO: 'bg-slate-100 text-slate-500',
}[e] || 'bg-slate-100 text-slate-500')

onMounted(async () => {
  await Promise.all([cargar(), cargarPlantillas(), cargarCuentasBancarias()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.btn-danger    { @apply px-3 py-1.5 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
</style>
