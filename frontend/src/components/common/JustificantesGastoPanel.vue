<template>
  <div>
    <!-- Barra superior -->
    <div class="flex items-center justify-between gap-3 mb-3 flex-wrap">
      <div class="text-xs text-slate-500 flex items-center gap-3 flex-wrap">
        <span>{{ justificantesFiltrados.length }} de {{ justificantes.length }} justificantes</span>
        <span class="text-slate-300">·</span>
        <span class="text-amber-700"><strong>{{ contar('PRESENTADO') }}</strong> presentados</span>
        <span class="text-blue-700"><strong>{{ contar('ACEPTADO') }}</strong> aceptados</span>
        <span class="text-purple-700"><strong>{{ contar('APROBADO') }}</strong> aprobados</span>
        <span class="text-green-700"><strong>{{ contar('PAGADO') }}</strong> pagados</span>
        <span class="text-red-700"><strong>{{ contar('RECHAZADO') }}</strong> rechazados</span>
        <span class="text-slate-500"><strong>{{ contar('ANULADO') }}</strong> anulados</span>
      </div>
      <div class="flex gap-2">
        <button v-if="modo === 'PROPIO' && puedePresentar" @click="abrirModalPresentar('PROPIO')"
                class="btn-primary text-sm">+ Presentar gasto</button>
        <button v-if="modo === 'GESTION' && esTesorero" @click="abrirModalPresentar('OTRO')"
                class="btn-primary text-sm">+ Registrar gasto de socio</button>
      </div>
    </div>

    <!-- Filtros (solo en modo gestión) -->
    <FilterBar
      v-if="modo === 'GESTION'"
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por número, concepto o miembro…"
      :fields="camposFiltro"
      :description="descripcionFiltros"
      class="mb-3"
    />

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="justificantesFiltrados.length" class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div class="overflow-x-auto -mx-1"><table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Nº</th>
            <th v-if="modo === 'GESTION'" class="px-3 py-2 text-left">Presentado por</th>
            <th class="px-3 py-2 text-left">Actividad</th>
            <th class="px-3 py-2 text-left">Concepto</th>
            <th class="px-3 py-2 text-right">Importe</th>
            <th class="px-3 py-2 text-center">F. gasto</th>
            <th class="px-3 py-2 text-center">Estado</th>
            <th class="px-3 py-2 text-center w-24">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="j in justificantesFiltrados" :key="j.id"
              class="hover:bg-slate-50 cursor-pointer"
              @click="abrirDetalle(j)">
            <td class="px-3 py-1.5 font-mono text-xs text-slate-700">{{ j.numeroJustificante }}</td>
            <td v-if="modo === 'GESTION'" class="px-3 py-1.5 truncate max-w-[12rem]">{{ miembroNombre(j.miembro) }}</td>
            <td class="px-3 py-1.5 truncate max-w-[14rem] text-slate-600">{{ j.actividad?.nombre || '—' }}</td>
            <td class="px-3 py-1.5 truncate max-w-[14rem] text-slate-600">{{ j.concepto }}</td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(j.importe) }}</td>
            <td class="px-3 py-1.5 text-center text-xs text-slate-500">{{ fechaFmt(j.fechaGasto) }}</td>
            <td class="px-3 py-1.5 text-center">
              <span :class="badgeEstado(j.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ j.estado }}
              </span>
            </td>
            <td class="px-3 py-1.5">
              <RowActions
                :show-view="true"
                :show-edit="false"
                :show-delete="puedeAnular(j)"
                confirm-title="¿Anular este justificante?"
                :confirm-text="`Se cancelará el justificante ${j.numeroJustificante}. Esta operación no se puede deshacer salvo reabrir el flujo desde cero.`"
                @view.stop="abrirDetalle(j)"
                @delete="anular(j)"
              />
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <p v-else class="text-center text-slate-400 py-10 text-sm border border-dashed border-slate-200 rounded-xl">
      {{ modo === 'PROPIO' ? 'Todavía no has presentado ningún gasto.' : 'No hay justificantes con los filtros aplicados.' }}
    </p>

    <ErrorAlert v-if="error" :message="error" />

    <!-- Modal: presentar justificante -->
    <div v-if="modalPresentar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalPresentar = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">
            {{ formPres.modo === 'OTRO' ? 'Registro de justificantes de gastos' : 'Presentar justificante de gasto' }}
          </h3>
          <p class="text-xs text-slate-500 mt-0.5">
            <template v-if="formPres.modo === 'OTRO'">
              Selecciona la actividad y el socio que incurrió en el gasto. Al guardar, el
              justificante quedará automáticamente <em>ACEPTADO</em> y tu nombre figura como aceptador.
            </template>
            <template v-else>
              Selecciona la actividad y añade los gastos en los que incurriste participando en ella.
            </template>
          </p>
        </div>
        <div class="px-6 py-5 space-y-4 overflow-y-auto">

          <!-- Imputación a actividad (componente común reutilizable) -->
          <ImputacionActividadPicker
            v-model="imputacionPres"
            :campanias="campanias"
            :actividades="actividades"
          />

          <!-- Solo modo OTRO: selector del socio que incurrió en el gasto -->
          <div v-if="formPres.modo === 'OTRO'" class="border border-indigo-200 bg-indigo-50/50 rounded-lg p-3">
            <label class="label">Socio que incurrió en el gasto *</label>
            <select v-model="formPres.miembroPagadorId" :disabled="!formPres.actividadId"
                    class="input disabled:bg-slate-100 disabled:text-slate-400">
              <option :value="null">
                {{ formPres.actividadId ? '— Selecciona socio —' : '— Selecciona primero una actividad —' }}
              </option>
              <option v-for="m in miembrosElegibles" :key="m.id" :value="m.id">
                {{ miembroNombre(m) }}
              </option>
            </select>
            <p v-if="formPres.actividadId && cargandoElegibles" class="text-xs text-slate-500 mt-1">
              Cargando candidatos…
            </p>
            <p v-else-if="formPres.actividadId && !miembrosElegibles.length"
               class="text-xs text-amber-700 mt-1">
              Ningún socio está vinculado al grupo de trabajo de esta actividad.
            </p>
            <p v-else-if="formPres.modoImputacion === 'CAMPANIA' && formPres.actividadId"
               class="text-xs text-slate-500 mt-1">
              Solo se muestran socios del equipo asignado a la actividad.
            </p>
          </div>

          <!-- Gastos del justificante -->
          <div class="border border-slate-200 rounded-lg p-3 bg-slate-50">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-700 uppercase">Gastos</span>
              <span class="text-xs text-slate-500">
                Total: <span class="font-mono">{{ fmt(totalLineas) }}</span>
              </span>
            </div>
            <div v-for="(l, i) in formPres.lineas" :key="i"
                 class="bg-white border border-slate-200 rounded p-2 mb-2 grid grid-cols-12 gap-2 items-end">
              <div class="col-span-6">
                <label class="label">Concepto *</label>
                <input v-model="l.concepto" class="input" placeholder="Ej: Alquiler proyector" />
              </div>
              <div class="col-span-3">
                <label class="label">Importe (€) *</label>
                <input type="number" v-model.number="l.importe" step="0.01" min="0.01" class="input" />
              </div>
              <div class="col-span-2">
                <label class="label">Fecha *</label>
                <input type="date" v-model="l.fechaGasto" class="input" />
              </div>
              <div class="col-span-1 flex justify-end">
                <button v-if="formPres.lineas.length > 1" @click="quitarLinea(i)" title="Quitar gasto"
                        class="h-10 px-2 text-red-500 hover:text-red-700">×</button>
              </div>
            </div>
            <button type="button" @click="anadirLinea"
                    class="text-xs text-indigo-600 hover:text-indigo-800 hover:underline">
              + Añadir otro gasto
            </button>
          </div>

          <!-- Documentos probatorios -->
          <div class="border border-slate-200 rounded-lg p-3 bg-slate-50">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-700 uppercase">Documentos probatorios</span>
              <label class="text-xs text-indigo-600 hover:text-indigo-800 cursor-pointer">
                + Añadir archivo
                <input type="file" class="hidden" multiple accept=".pdf,.jpg,.jpeg,.png,.heic"
                       @change="onSeleccionArchivos" />
              </label>
            </div>
            <p v-if="!formPres.archivos.length" class="text-xs text-slate-500">
              Adjunta facturas, tickets o fotos. PDF / JPG / PNG (máx. 30 MB cada uno).
            </p>
            <ul v-else class="space-y-1 text-xs">
              <li v-for="(f, i) in formPres.archivos" :key="i"
                  class="flex items-center justify-between bg-white border border-slate-200 rounded px-2 py-1">
                <span class="truncate">📎 {{ f.name }}</span>
                <button @click="formPres.archivos.splice(i, 1)" class="text-red-500 hover:text-red-700">×</button>
              </li>
            </ul>
          </div>

          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formPres.observaciones" class="input h-16" />
          </div>
          <ErrorAlert v-if="formPres.error" :message="formPres.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalPresentar = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="presentar()" :disabled="ocupado" class="btn-primary text-sm">
            {{ ocupado ? 'Enviando…' : 'Presentar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: detalle del justificante -->
    <div v-if="justDetalle" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="justDetalle = null">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-slate-800 font-mono">{{ justDetalle.numeroJustificante }}</h3>
            <span :class="badgeEstado(justDetalle.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5 mt-1 inline-block">
              {{ justDetalle.estado }}
            </span>
          </div>
          <button @click="justDetalle = null" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm overflow-y-auto">
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <dt class="text-xs text-slate-500">Presentado por</dt>
              <dd class="font-medium text-slate-800">{{ miembroNombre(justDetalle.miembro) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Ejercicio</dt>
              <dd class="text-slate-800">{{ justDetalle.ejercicio }}</dd>
            </div>
            <div class="col-span-2">
              <dt class="text-xs text-slate-500">Actividad</dt>
              <dd class="text-slate-800">{{ justDetalle.actividad?.nombre || '—' }}</dd>
            </div>
            <div class="col-span-2">
              <dt class="text-xs text-slate-500">Concepto</dt>
              <dd class="text-slate-800">{{ justDetalle.concepto }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Importe</dt>
              <dd class="font-mono text-slate-800">{{ fmt(justDetalle.importe) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Fecha gasto</dt>
              <dd class="text-slate-800">{{ fechaFmt(justDetalle.fechaGasto) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Presentado</dt>
              <dd class="text-slate-800">{{ fechaFmt(justDetalle.fechaPresentacion) }}</dd>
            </div>
            <div v-if="justDetalle.aceptador">
              <dt class="text-xs text-slate-500">Aceptado</dt>
              <dd class="text-slate-800">
                {{ fechaFmt(justDetalle.fechaAceptacion) }} · {{ miembroNombre(justDetalle.aceptador) }}
              </dd>
            </div>
            <div v-if="justDetalle.aprobador">
              <dt class="text-xs text-slate-500">Aprobado / Rechazado</dt>
              <dd class="text-slate-800">
                {{ fechaFmt(justDetalle.fechaAprobacion) }} · {{ miembroNombre(justDetalle.aprobador) }}
              </dd>
            </div>
            <div v-if="justDetalle.fechaPago">
              <dt class="text-xs text-slate-500">Pagado</dt>
              <dd class="text-slate-800">
                {{ fechaFmt(justDetalle.fechaPago) }} · {{ justDetalle.modoPago }}
              </dd>
            </div>
            <div v-if="justDetalle.cuentaBancaria">
              <dt class="text-xs text-slate-500">Cuenta destino</dt>
              <dd class="text-slate-800">{{ justDetalle.cuentaBancaria.nombre }}</dd>
            </div>
            <div v-if="justDetalle.motivoRechazo" class="col-span-2">
              <dt class="text-xs text-red-600">Motivo del rechazo</dt>
              <dd class="text-red-700 bg-red-50 p-2 rounded text-xs">{{ justDetalle.motivoRechazo }}</dd>
            </div>
            <div v-if="justDetalle.observaciones" class="col-span-2">
              <dt class="text-xs text-slate-500">Observaciones</dt>
              <dd class="text-xs text-slate-600 whitespace-pre-wrap">{{ justDetalle.observaciones }}</dd>
            </div>
          </dl>

          <!-- Detalle de gastos (líneas) -->
          <div v-if="justDetalle.lineas?.length" class="border-t border-slate-200 pt-3">
            <h4 class="text-xs font-semibold text-slate-700 uppercase mb-2">
              Gastos ({{ justDetalle.lineas.length }})
            </h4>
            <div class="overflow-x-auto -mx-1"><table class="w-full text-xs">
              <thead class="text-slate-500">
                <tr>
                  <th class="text-left font-medium py-1">Concepto</th>
                  <th class="text-center font-medium py-1 w-24">Fecha</th>
                  <th class="text-right font-medium py-1 w-24">Importe</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="l in justDetalle.lineas" :key="l.id">
                  <td class="py-1 text-slate-700">
                    {{ l.concepto }}
                    <span v-if="l.observaciones" class="block text-slate-400">{{ l.observaciones }}</span>
                  </td>
                  <td class="py-1 text-center text-slate-500">{{ fechaFmt(l.fechaGasto) }}</td>
                  <td class="py-1 text-right font-mono text-slate-700">{{ fmt(l.importe) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="border-t border-slate-200 font-medium">
                  <td colspan="2" class="py-1 text-right text-slate-500">Total</td>
                  <td class="py-1 text-right font-mono text-slate-800">{{ fmt(justDetalle.importe) }}</td>
                </tr>
              </tfoot>
            </table></div>
          </div>

          <!-- Documentos probatorios -->
          <div class="border-t border-slate-200 pt-3">
            <h4 class="text-xs font-semibold text-slate-700 uppercase mb-2">
              Documentos probatorios
            </h4>
            <ul v-if="justDetalle.documentos?.length" class="space-y-1 text-xs">
              <li v-for="d in justDetalle.documentos" :key="d.id"
                  class="flex items-center justify-between bg-slate-50 border border-slate-200 rounded px-2 py-1">
                <a :href="d.url" target="_blank"
                   class="text-indigo-600 hover:underline truncate">📎 {{ d.nombreArchivo }}</a>
                <span class="text-slate-400 shrink-0 ml-2">{{ tamanoFmt(d.tamanoBytes) }}</span>
              </li>
            </ul>
            <p v-else class="text-xs text-slate-400">Sin documentos adjuntos.</p>
          </div>

          <!-- Formulario pagar -->
          <div v-if="modalPagar" class="border-t border-slate-200 pt-3 space-y-2">
            <h4 class="font-medium text-sm text-slate-700">Registrar pago</h4>
            <div>
              <label class="label">Cuenta bancaria de origen *</label>
              <select v-model="formPagar.cuentaBancariaId" class="input">
                <option :value="null">— Selecciona cuenta —</option>
                <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
                  {{ c.nombre }}{{ c.iban ? ` — ${c.iban}` : '' }}
                </option>
              </select>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="label">Modo pago *</label>
                <select v-model="formPagar.modoPago" class="input">
                  <option value="TRANSFERENCIA">Transferencia</option>
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="TARJETA">Tarjeta</option>
                  <option value="MANUAL">Manual / otro</option>
                </select>
              </div>
              <div>
                <label class="label">Fecha pago *</label>
                <input type="date" v-model="formPagar.fechaPago" class="input" />
              </div>
            </div>
            <div>
              <label class="label">Referencia</label>
              <input v-model="formPagar.referencia" class="input"
                     placeholder="Núm. transferencia, ticket, etc. (opcional)" />
            </div>
            <ErrorAlert v-if="formPagar.error" :message="formPagar.error" />
          </div>
        </div>

        <div class="px-6 py-4 border-t border-slate-200 flex flex-wrap justify-end gap-2">
          <template v-if="!modalPagar">
            <button v-if="puedeAceptar(justDetalle)" @click="aceptar(justDetalle)" :disabled="ocupado"
                    class="btn-primary text-xs">Aceptar (como responsable)</button>
            <button v-if="puedeAprobar(justDetalle)" @click="aprobar(justDetalle)" :disabled="ocupado"
                    class="btn-primary text-xs">Aprobar (como tesorero)</button>
            <button v-if="puedePagar(justDetalle)" @click="abrirPagar()" class="btn-primary text-xs">
              Registrar pago
            </button>
            <button v-if="puedeRechazar(justDetalle)" @click="rechazar(justDetalle)" :disabled="ocupado"
                    class="btn-danger text-xs">Rechazar</button>
            <button v-if="puedeAnular(justDetalle)" @click="anular(justDetalle)" :disabled="ocupado"
                    class="btn-secondary text-xs">Anular</button>
          </template>
          <template v-else>
            <button @click="modalPagar = false" class="btn-secondary text-xs">Cancelar</button>
            <button @click="confirmarPago()" :disabled="ocupado" class="btn-primary text-xs">
              {{ ocupado ? 'Registrando…' : 'Confirmar pago' }}
            </button>
          </template>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useConfirm } from '@/composables/useConfirm'
import { ref, computed, onMounted, watch } from 'vue'
import FilterBar from '@/components/common/FilterBar.vue'
import RowActions from '@/components/common/RowActions.vue'
import ImputacionActividadPicker from '@/components/common/ImputacionActividadPicker.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useAuthStore } from '@/stores/auth'
import {
  GET_JUSTIFICANTES,
  GET_JUSTIFICANTES_DE_MIEMBRO,
  GET_ACTIVIDADES_PARA_GASTO,
  PRESENTAR_JUSTIFICANTE,
  ACEPTAR_JUSTIFICANTE,
  APROBAR_JUSTIFICANTE,
  RECHAZAR_JUSTIFICANTE,
  PAGAR_JUSTIFICANTE,
  ANULAR_JUSTIFICANTE,
  GET_CUENTAS_BANCARIAS_ACTIVAS,
  GET_MIEMBROS_ELEGIBLES_JUSTIFICANTE,
} from '@/graphql/queries/economico'
import { GET_CAMPANIAS } from '@/graphql/queries/campanias'
const confirmDialog = useConfirm()

const props = defineProps({
  // PROPIO: justificantes de un socio (autoservicio en Mis Datos).
  // GESTION: todos los justificantes (tesorería: aceptar/aprobar/pagar).
  modo:      { type: String, default: 'GESTION', validator: (v) => ['PROPIO', 'GESTION'].includes(v) },
  // Socio al que pertenece el panel en modo PROPIO.
  miembroId: { type: String, default: null },
})

const { query, mutation, loading } = useGraphQL()
const authStore = useAuthStore()

const justificantes = ref([])
const actividades = ref([])
const campanias = ref([])
const cuentasBancarias = ref([])
const error = ref('')
const ocupado = ref(false)

const justDetalle = ref(null)
const modalPresentar = ref(false)
const modalPagar = ref(false)

const _hoyISO = () => new Date().toISOString().split('T')[0]
const _nuevaLinea = () => ({ concepto: '', importe: 0, fechaGasto: _hoyISO() })

const formPres = ref({
  modo: 'PROPIO',              // PROPIO | OTRO
  modoImputacion: 'CAMPANIA',  // CAMPANIA | FUERA
  tipoFuera: 'PERMANENTE',     // PERMANENTE | PUNTUAL | RECURRENTE
  campaniaId: null,
  actividadId: null,
  lineas: [_nuevaLinea()],
  archivos: [],
  observaciones: '',
  miembroPagadorId: null,
  error: '',
})

const miembrosElegibles = ref([])
const cargandoElegibles = ref(false)

const totalLineas = computed(() =>
  formPres.value.lineas.reduce((s, l) => s + (Number(l.importe) || 0), 0)
)

const anadirLinea = () => formPres.value.lineas.push(_nuevaLinea())
const quitarLinea = (i) => {
  if (formPres.value.lineas.length > 1) formPres.value.lineas.splice(i, 1)
}
const onSeleccionArchivos = (ev) => {
  const files = Array.from(ev.target.files || [])
  formPres.value.archivos.push(...files)
  ev.target.value = ''
}

const esTesorero = computed(() => tienePermiso('JUST_APROBAR'))
const puedePresentar = computed(() => tienePermiso('JUST_PRESENTAR'))

const formPagar = ref({
  cuentaBancariaId: null,
  modoPago: 'TRANSFERENCIA',
  fechaPago: '',
  referencia: '',
  error: '',
})

// ── Filtros (solo modo GESTION) ─────────────────────────────────────────────
const busqueda = ref('')
const filtros = ref({ ejercicio: null, estado: [], soloPendientesMios: false })

const camposFiltro = computed(() => [
  {
    key: 'ejercicio', label: 'Ejercicio', type: 'select',
    options: anosDisponibles.value.map(y => ({ value: y, label: String(y) })),
    allLabel: 'Todos los ejercicios',
  },
  {
    key: 'estado', label: 'Estado', type: 'multiselect',
    options: [
      { value: 'PRESENTADO', label: 'Presentado' },
      { value: 'ACEPTADO',   label: 'Aceptado' },
      { value: 'APROBADO',   label: 'Aprobado' },
      { value: 'PAGADO',     label: 'Pagado' },
      { value: 'RECHAZADO',  label: 'Rechazado' },
      { value: 'ANULADO',    label: 'Anulado' },
    ],
    allLabel: 'Todos los estados',
  },
  ...(tienePermiso('JUST_ACEPTAR') || tienePermiso('JUST_APROBAR') || tienePermiso('JUST_PAGAR')
    ? [{ key: 'soloPendientesMios', label: 'Pendientes de mi visto bueno', type: 'toggle' }]
    : []),
])

const descripcionFiltros = computed(() => {
  const parts = []
  if (filtros.value.ejercicio) parts.push(`ejercicio ${filtros.value.ejercicio}`)
  if (filtros.value.estado?.length) parts.push(`${filtros.value.estado.length} estado(s)`)
  if (filtros.value.soloPendientesMios) parts.push('pendientes de mi visto bueno')
  return parts.join(' · ')
})

const anosDisponibles = computed(() =>
  [...new Set(justificantes.value.map(j => j.ejercicio).filter(Boolean))].sort((a, b) => b - a)
)

const miembroIdLogueado = computed(() => authStore.user?.miembroId || authStore.miembroId || null)

const justificantesFiltrados = computed(() => {
  if (props.modo === 'PROPIO') return justificantes.value
  const q = (busqueda.value || '').toLowerCase().trim()
  const miId = miembroIdLogueado.value
  return justificantes.value.filter(j => {
    if (filtros.value.ejercicio && j.ejercicio !== filtros.value.ejercicio) return false
    if (filtros.value.estado?.length && !filtros.value.estado.includes(j.estado)) return false
    if (filtros.value.soloPendientesMios) {
      const esResp = j.estado === 'PRESENTADO' && j.actividad?.responsableId === miId
      const esTes = j.estado === 'ACEPTADO' && tienePermiso('JUST_APROBAR')
      if (!esResp && !esTes) return false
    }
    if (q) {
      const num = (j.numeroJustificante || '').toLowerCase()
      const con = (j.concepto || '').toLowerCase()
      const nom = miembroNombre(j.miembro).toLowerCase()
      if (!num.includes(q) && !con.includes(q) && !nom.includes(q)) return false
    }
    return true
  })
})

const contar = (e) => justificantes.value.filter(j => j.estado === e).length

// ── Permisos / posibles acciones ───────────────────────────────────────────
const tienePermiso = (codigo) => {
  const perms = authStore.user?.permisos || authStore.permisos || []
  return Array.isArray(perms) ? perms.includes(codigo) : false
}

const puedeAceptar = (j) =>
  j.estado === 'PRESENTADO'
  && j.actividad?.responsableId === miembroIdLogueado.value
  && tienePermiso('JUST_ACEPTAR')

const puedeAprobar = (j) =>
  j.estado === 'ACEPTADO' && tienePermiso('JUST_APROBAR')

const puedePagar = (j) =>
  j.estado === 'APROBADO' && tienePermiso('JUST_PAGAR')

const puedeRechazar = (j) => {
  if (j.estado === 'PRESENTADO' && j.actividad?.responsableId === miembroIdLogueado.value && tienePermiso('JUST_ACEPTAR')) return true
  if (j.estado === 'ACEPTADO' && tienePermiso('JUST_APROBAR')) return true
  return false
}

const puedeAnular = (j) =>
  j.estado === 'PRESENTADO' && j.miembro?.id === miembroIdLogueado.value && tienePermiso('JUST_PRESENTAR')

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  error.value = ''
  try {
    let data
    if (props.modo === 'PROPIO') {
      if (!props.miembroId) { justificantes.value = []; return }
      data = await query(GET_JUSTIFICANTES_DE_MIEMBRO, { miembroId: props.miembroId })
    } else {
      data = await query(GET_JUSTIFICANTES)
    }
    justificantes.value = (data.justificantesGasto || []).slice().sort((a, b) =>
      (b.numeroJustificante || '').localeCompare(a.numeroJustificante || '')
    )
  } catch (e) {
    error.value = 'Error al cargar los justificantes'
    console.error(e)
  }
}

const cargarActividades = async () => {
  try {
    const data = await query(GET_ACTIVIDADES_PARA_GASTO)
    actividades.value = data.actividades || []
  } catch (e) { console.error('Error cargando actividades:', e) }
}

const cargarCampanias = async () => {
  try {
    const data = await query(GET_CAMPANIAS)
    campanias.value = data.campanias || []
  } catch (e) { console.error('Error cargando campañas:', e) }
}

// Puente bidireccional con ImputacionActividadPicker
const imputacionPres = computed({
  get: () => ({
    modo:        formPres.value.modoImputacion,
    campaniaId:  formPres.value.campaniaId,
    actividadId: formPres.value.actividadId,
    tipoFuera:   formPres.value.tipoFuera,
  }),
  set: (v) => {
    formPres.value.modoImputacion = v.modo
    formPres.value.campaniaId     = v.campaniaId
    formPres.value.actividadId    = v.actividadId
    formPres.value.tipoFuera      = v.tipoFuera
  },
})

const cargarMiembrosElegibles = async (actividadId) => {
  if (!actividadId) { miembrosElegibles.value = []; return }
  cargandoElegibles.value = true
  try {
    const data = await query(GET_MIEMBROS_ELEGIBLES_JUSTIFICANTE, { actividadId })
    miembrosElegibles.value = (data.miembrosElegiblesParaJustificante || [])
      .slice().sort((a, b) => miembroNombre(a).localeCompare(miembroNombre(b)))
  } catch (e) {
    console.error('Error cargando socios elegibles:', e)
    miembrosElegibles.value = []
  } finally {
    cargandoElegibles.value = false
  }
}

watch(
  () => [formPres.value.modo, formPres.value.actividadId],
  ([modo, actividadId]) => {
    formPres.value.miembroPagadorId = null
    if (modo === 'OTRO') cargarMiembrosElegibles(actividadId)
    else miembrosElegibles.value = []
  },
)

const cargarCuentas = async () => {
  try {
    const data = await query(GET_CUENTAS_BANCARIAS_ACTIVAS)
    cuentasBancarias.value = (data.cuentasBancarias || []).filter(c => c.activa)
  } catch (e) { console.error('Error cargando cuentas:', e) }
}

// ── Presentar ──────────────────────────────────────────────────────────────
const abrirModalPresentar = (modo = 'PROPIO') => {
  formPres.value = {
    modo,
    modoImputacion: 'CAMPANIA',
    tipoFuera: 'PERMANENTE',
    campaniaId: null,
    actividadId: null,
    lineas: [_nuevaLinea()],
    archivos: [],
    observaciones: '',
    miembroPagadorId: null,
    error: '',
  }
  miembrosElegibles.value = []
  if (!campanias.value.length) cargarCampanias()
  modalPresentar.value = true
}

const presentar = async () => {
  formPres.value.error = ''
  if (!formPres.value.actividadId) { formPres.value.error = 'Selecciona una actividad'; return }
  if (!formPres.value.lineas.length) { formPres.value.error = 'Añade al menos un gasto'; return }
  for (let i = 0; i < formPres.value.lineas.length; i++) {
    const l = formPres.value.lineas[i]
    if (!l.concepto?.trim()) { formPres.value.error = `Gasto ${i + 1}: indica el concepto`; return }
    if (!(Number(l.importe) > 0)) { formPres.value.error = `Gasto ${i + 1}: el importe debe ser positivo`; return }
    if (!l.fechaGasto) { formPres.value.error = `Gasto ${i + 1}: indica la fecha`; return }
  }

  // En modo PROPIO el gastador es el socio del panel; en OTRO, el seleccionado.
  let miembroIdReal = props.modo === 'PROPIO'
    ? (props.miembroId || miembroIdLogueado.value)
    : miembroIdLogueado.value
  let presentadoPorTesoreroId = null
  if (formPres.value.modo === 'OTRO') {
    if (!formPres.value.miembroPagadorId) {
      formPres.value.error = 'Selecciona el socio que incurrió en el gasto'; return
    }
    miembroIdReal = formPres.value.miembroPagadorId
    presentadoPorTesoreroId = miembroIdLogueado.value
  }
  if (!miembroIdReal) {
    formPres.value.error = 'No se ha podido determinar el miembro. Contacta con administración.'; return
  }

  ocupado.value = true
  try {
    const data = await mutation(PRESENTAR_JUSTIFICANTE, {
      miembroId: miembroIdReal,
      actividadId: formPres.value.actividadId,
      lineas: formPres.value.lineas.map(l => ({
        concepto: l.concepto.trim(),
        importe: Number(l.importe),
        fechaGasto: l.fechaGasto,
      })),
      observaciones: formPres.value.observaciones || null,
      presentadoPorTesoreroId,
    })
    const justificanteId = data.presentarJustificanteGasto
    // Subir documentos uno a uno (si hay)
    if (justificanteId && formPres.value.archivos.length) {
      const token = localStorage.getItem('siga_token') || sessionStorage.getItem('siga_token')
      for (const f of formPres.value.archivos) {
        const fd = new FormData()
        fd.append('file', f)
        try {
          await fetch(`/upload/justificantes/${justificanteId}/documentos`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: fd,
          })
        } catch (e) {
          console.warn('Error subiendo documento', f.name, e)
        }
      }
    }
    modalPresentar.value = false
    await cargar()
  } catch (e) {
    formPres.value.error = errMsg(e, 'Error al presentar el justificante')
  } finally { ocupado.value = false }
}

const errMsg = (e, fallback = 'Error') => {
  if (e?.response?.errors?.[0]?.message) return e.response.errors[0].message
  if (typeof e?.message === 'string') {
    const i = e.message.indexOf(': {')
    return i > 0 ? e.message.slice(0, i) : e.message
  }
  return fallback
}

// ── Acciones por estado ─────────────────────────────────────────────────────
const abrirDetalle = (j) => { justDetalle.value = j; modalPagar.value = false }

const aceptar = async (j) => {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: `¿Aceptar el justificante ${j.numeroJustificante}?`, variante: 'aviso' }))) return
  ocupado.value = true
  try {
    await mutation(ACEPTAR_JUSTIFICANTE, { justificanteId: j.id, aceptadorId: miembroIdLogueado.value })
    justDetalle.value = null
    await cargar()
  } catch (e) { error.value = e.message || 'Error al aceptar' } finally { ocupado.value = false }
}

const aprobar = async (j) => {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: `¿Aprobar el justificante ${j.numeroJustificante}?`, variante: 'aviso' }))) return
  ocupado.value = true
  try {
    await mutation(APROBAR_JUSTIFICANTE, { justificanteId: j.id, aprobadorId: miembroIdLogueado.value })
    justDetalle.value = null
    await cargar()
  } catch (e) { error.value = e.message || 'Error al aprobar' } finally { ocupado.value = false }
}

const rechazar = async (j) => {
  const motivo = prompt(`¿Rechazar el justificante ${j.numeroJustificante}? Indica el motivo:`)
  if (!motivo) return
  ocupado.value = true
  try {
    await mutation(RECHAZAR_JUSTIFICANTE, { justificanteId: j.id, aprobadorId: miembroIdLogueado.value, motivo })
    justDetalle.value = null
    await cargar()
  } catch (e) { error.value = e.message || 'Error al rechazar' } finally { ocupado.value = false }
}

const anular = async (j) => {
  const motivo = prompt(`¿Anular el justificante ${j.numeroJustificante}? Motivo (opcional):`)
  if (motivo === null) return
  ocupado.value = true
  try {
    await mutation(ANULAR_JUSTIFICANTE, { justificanteId: j.id, motivo: motivo || null })
    justDetalle.value = null
    await cargar()
  } catch (e) { error.value = e.message || 'Error al anular' } finally { ocupado.value = false }
}

const abrirPagar = () => {
  formPagar.value = {
    cuentaBancariaId: cuentasBancarias.value.length === 1 ? cuentasBancarias.value[0].id : null,
    modoPago: 'TRANSFERENCIA',
    fechaPago: new Date().toISOString().split('T')[0],
    referencia: '',
    error: '',
  }
  modalPagar.value = true
}

const confirmarPago = async () => {
  formPagar.value.error = ''
  if (!formPagar.value.cuentaBancariaId) { formPagar.value.error = 'Selecciona la cuenta'; return }
  if (!formPagar.value.fechaPago) { formPagar.value.error = 'Indica la fecha de pago'; return }
  ocupado.value = true
  try {
    await mutation(PAGAR_JUSTIFICANTE, {
      justificanteId: justDetalle.value.id,
      cuentaBancariaId: formPagar.value.cuentaBancariaId,
      modoPago: formPagar.value.modoPago,
      fechaPago: formPagar.value.fechaPago,
      referencia: formPagar.value.referencia || null,
    })
    modalPagar.value = false
    justDetalle.value = null
    await cargar()
  } catch (e) { formPagar.value.error = e.message || 'Error al registrar el pago' } finally { ocupado.value = false }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const miembroNombre = (m) => {
  if (!m) return '—'
  return `${m.nombre || ''} ${m.apellido1 || ''} ${m.apellido2 || ''}`.trim() || '—'
}
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'
const tamanoFmt = (b) => {
  if (!b) return ''
  if (b < 1024) return `${b} B`
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(0)} KB`
  return `${(b / 1024 / 1024).toFixed(1)} MB`
}

const badgeEstado = (e) => ({
  PRESENTADO: 'bg-amber-100 text-amber-700',
  ACEPTADO:   'bg-blue-100 text-blue-700',
  APROBADO:   'bg-purple-100 text-purple-700',
  PAGADO:     'bg-green-100 text-green-700',
  RECHAZADO:  'bg-red-100 text-red-700',
  ANULADO:    'bg-slate-100 text-slate-500',
}[e] || 'bg-slate-100 text-slate-500')

// Recargar si cambia el socio del panel (modo PROPIO).
watch(() => props.miembroId, () => { if (props.modo === 'PROPIO') cargar() })

onMounted(async () => {
  await Promise.all([
    cargar(),
    cargarActividades(),
    cargarCuentas(),
  ])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.btn-danger    { @apply px-3 py-1.5 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
</style>
