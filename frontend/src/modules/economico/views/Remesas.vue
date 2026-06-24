<template>
  <AppLayout title="Remesas SEPA" subtitle="Generación y cobro domiciliado de cuotas">

    <FilterBar
      v-model="filtros"
      :fields="camposFiltro"
      create-label="+ Nueva remesa"
      :description="descripcionFiltros"
      @create="abrirAsistente()"
    />

    <div class="text-xs text-slate-500 mt-2 mb-3 px-1">
      {{ remesasFiltradas.length }} de {{ remesas.length }} remesas
    </div>

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="remesasFiltradas.length" class="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
      <div
        v-for="r in remesasFiltradas"
        :key="r.id"
        class="px-4 py-3 hover:bg-slate-50 cursor-pointer transition-colors"
        :class="seleccionada?.id === r.id ? 'bg-indigo-50/50' : ''"
        @click="seleccionada = seleccionada?.id === r.id ? null : r"
      >
        <div class="grid grid-cols-[minmax(0,1.4fr)_auto_minmax(0,2fr)_8rem_6rem] items-center gap-3">
          <span
            class="font-mono text-sm font-medium text-slate-800 truncate"
            :title="r.referencia"
          >{{ formatRef(r.referencia) }}</span>
          <span class="text-[10px] uppercase tracking-wide rounded px-1.5 py-0.5 justify-self-start" :class="badgeTipo(r.tipoRemesa)">
            {{ tipoLabel(r.tipoRemesa) }}
          </span>
          <span class="text-xs text-slate-500 truncate">
            Cobro {{ fechaFmt(r.fechaCobro) }} · {{ r.numOrdenes }} órdenes
            <span v-if="r.agrupacion" class="ml-1 text-indigo-600">· {{ r.agrupacion.nombre }}</span>
          </span>
          <span class="font-mono text-sm font-bold text-slate-900 text-right">{{ fmt(r.importeTotal) }}</span>
          <span :class="badgeEstado(r.estado?.nombre)" class="text-xs px-2 py-0.5 rounded-full font-medium justify-self-end whitespace-nowrap">
            {{ r.estado?.nombre || '—' }}
          </span>
        </div>

        <!-- Acciones por estado -->
        <div v-if="seleccionada?.id === r.id" class="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
          <button
            v-if="['Borrador','Generada','Enviada','Procesada','Parcial'].includes(r.estado?.nombre)"
            @click.stop="descargarXml(r)"
            class="btn-secondary text-xs"
            :disabled="ocupado"
          >↓ XML SEPA</button>

          <button
            v-if="r.estado?.nombre === 'Borrador' || r.estado?.nombre === 'Generada'"
            @click.stop="marcarEnviada(r.id)"
            class="btn-secondary text-xs"
            :disabled="ocupado"
          >Marcar enviada</button>

          <button
            v-if="r.estado?.nombre === 'Enviada'"
            @click.stop="abrirModalLiquidar(r)"
            class="btn-primary text-xs"
          >Liquidar cobro</button>

          <button
            v-if="['Procesada','Parcial'].includes(r.estado?.nombre)"
            @click.stop="abrirReenvio(r)"
            class="btn-secondary text-xs"
            :disabled="ocupado"
          >+ Remesa de reenvío</button>

          <button
            v-if="['Borrador','Generada','Enviada'].includes(r.estado?.nombre)"
            @click.stop="anularRemesa(r)"
            class="btn-danger text-xs ml-auto"
            :disabled="ocupado"
          >Anular</button>

          <span v-if="r.estado?.nombre === 'Procesada'" class="text-xs text-green-600 self-center">
            ✓ Cobro registrado
          </span>
          <p v-if="r.observaciones" class="w-full text-xs text-slate-500 mt-1 italic">{{ r.observaciones }}</p>
        </div>
      </div>
    </div>

    <p v-else class="text-center text-slate-400 py-12 text-sm border border-dashed border-slate-200 rounded-xl">
      No hay remesas con los filtros aplicados.
    </p>

    <ErrorAlert v-if="error" :message="error" />

    <!-- Asistente de nueva remesa (3 pasos) -->
    <div v-if="asistente.abierto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="cerrarAsistente()">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-slate-800">Nueva remesa SEPA</h3>
            <p class="text-xs text-slate-500 mt-0.5">Paso {{ asistente.paso }} de 3 · {{ pasoTitulo }}</p>
          </div>
          <button @click="cerrarAsistente()" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>

        <div class="px-6 py-5 overflow-y-auto flex-1">
          <!-- PASO 1: Tipo de remesa -->
          <div v-if="asistente.paso === 1" class="space-y-3">
            <label
              class="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50"
              :class="asistente.tipo === 'ORDINARIA' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200'"
            >
              <input type="radio" v-model="asistente.tipo" value="ORDINARIA" class="mt-1" />
              <div>
                <p class="text-sm font-medium text-slate-800">Ordinaria</p>
                <p class="text-xs text-slate-500">Cobro de cuotas pendientes del ejercicio. Una sola al año.</p>
              </div>
            </label>
            <label
              class="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50"
              :class="asistente.tipo === 'EXTRAORDINARIA' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200'"
            >
              <input type="radio" v-model="asistente.tipo" value="EXTRAORDINARIA" class="mt-1" />
              <div>
                <p class="text-sm font-medium text-slate-800">Extraordinaria</p>
                <p class="text-xs text-slate-500">Cargo único con concepto e importe libres (derrama, congresal…). SeqTp=OOFF.</p>
              </div>
            </label>
            <label
              class="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50"
              :class="asistente.tipo === 'REENVIO' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200'"
            >
              <input type="radio" v-model="asistente.tipo" value="REENVIO" class="mt-1" />
              <div>
                <p class="text-sm font-medium text-slate-800">Reenvío de fallidos</p>
                <p class="text-xs text-slate-500">Re-presenta órdenes fallidas de una remesa anterior. SeqTp=FRST.</p>
              </div>
            </label>
          </div>

          <!-- PASO 2: Parámetros (varía según tipo) -->
          <div v-else-if="asistente.paso === 2" class="space-y-4">
            <!-- ORDINARIA -->
            <template v-if="asistente.tipo === 'ORDINARIA'">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="label">Ejercicio *</label>
                  <input type="number" v-model.number="asistente.ejercicio" class="input" :min="2000" :max="2099" />
                </div>
                <div>
                  <label class="label">Fecha de cobro *</label>
                  <input type="date" v-model="asistente.fechaCobro" :min="fechaMinimaRcur" class="input" />
                  <p class="text-[11px] text-slate-500 mt-0.5">Mínimo 2 días después de hoy (RCUR).</p>
                </div>
              </div>
              <div>
                <label class="label">Agrupación territorial</label>
                <select v-model="asistente.agrupacionId" class="input">
                  <option :value="null">— Toda la organización —</option>
                  <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="label">Concepto</label>
                <input v-model="asistente.concepto" class="input" :placeholder="`Cuota ordinaria ejercicio ${asistente.ejercicio}`" />
              </div>
              <div>
                <label class="label">SeqTp SEPA</label>
                <select v-model="asistente.seqTipo" class="input">
                  <option value="RCUR">RCUR — Recurrente (cobros sucesivos)</option>
                  <option value="FRST">FRST — Primera presentación (mínimo 14 días)</option>
                </select>
              </div>

              <div class="pt-2">
                <button @click="cargarPreview()" class="btn-secondary text-sm" :disabled="cargandoPreview">
                  {{ cargandoPreview ? 'Calculando…' : 'Previsualizar' }}
                </button>
              </div>

              <div v-if="preview" class="space-y-3 pt-2">
                <div v-if="preview.ordinariaExistente" class="bg-red-50 border border-red-200 text-red-800 text-sm p-3 rounded-lg">
                  Ya existe una remesa ORDINARIA activa para este ejercicio
                  (<span class="font-mono">{{ preview.ordinariaExistente.referencia }}</span>).
                  Anúlala antes de crear otra (D3.2).
                </div>
                <div v-else class="bg-indigo-50 border border-indigo-100 rounded-lg p-3 text-sm">
                  <p class="text-indigo-800">
                    <b>{{ preview.nIncluidas }}</b> cuotas se incluirán ·
                    Importe total: <b class="text-green-700">{{ fmt(preview.importeTotal) }}</b>
                  </p>
                  <p v-if="preview.nExcluidas > 0" class="text-amber-700 text-xs mt-1">
                    ⚠ {{ preview.nExcluidas }} cuotas excluidas (sin IBAN o ya en otra remesa) — ver detalle abajo.
                  </p>
                </div>

                <div v-if="preview.excluidas.length" class="border border-slate-200 rounded-lg overflow-hidden">
                  <details>
                    <summary class="px-3 py-2 bg-slate-50 cursor-pointer text-xs font-medium text-slate-700 hover:bg-slate-100">
                      Ver cuotas excluidas ({{ preview.excluidas.length }})
                    </summary>
                    <div class="overflow-x-auto -mx-1"><table class="w-full text-xs">
                      <thead class="bg-slate-50 border-t border-slate-100">
                        <tr>
                          <th class="px-3 py-1.5 text-left text-slate-500">Miembro</th>
                          <th class="px-3 py-1.5 text-right text-slate-500">Importe</th>
                          <th class="px-3 py-1.5 text-left text-slate-500">Motivo</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-100">
                        <tr v-for="e in preview.excluidas" :key="e.cuotaId">
                          <td class="px-3 py-1 truncate">{{ e.miembroNombre }}</td>
                          <td class="px-3 py-1 text-right font-mono">{{ fmt(e.importePendiente) }}</td>
                          <td class="px-3 py-1 text-amber-700">{{ e.motivoExclusion }}</td>
                        </tr>
                      </tbody>
                    </table></div>
                  </details>
                </div>
              </div>
            </template>

            <!-- EXTRAORDINARIA -->
            <template v-else-if="asistente.tipo === 'EXTRAORDINARIA'">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="label">Ejercicio *</label>
                  <input type="number" v-model.number="asistente.ejercicio" class="input" :min="2000" :max="2099" />
                </div>
                <div>
                  <label class="label">Fecha de cobro *</label>
                  <input type="date" v-model="asistente.fechaCobro" :min="fechaMinimaOoff" class="input" />
                  <p class="text-[11px] text-slate-500 mt-0.5">Mínimo 14 días después de hoy (OOFF).</p>
                </div>
              </div>
              <div>
                <label class="label">Concepto *</label>
                <input v-model="asistente.concepto" class="input" placeholder="Ej: Derrama techo solar 2026" />
              </div>
              <div>
                <label class="label">Importe por miembro (€) *</label>
                <input type="number" v-model.number="asistente.importePorMiembro" class="input" step="0.01" min="0.01" />
              </div>
              <div>
                <label class="label">Miembros destinatarios *</label>
                <p class="text-xs text-slate-500 mb-1">
                  Pega o introduce los UUIDs de los miembros (uno por línea). Selector multi-pendiente.
                </p>
                <textarea v-model="asistente.miembroIdsRaw" class="input h-24 font-mono text-xs" />
              </div>
              <div>
                <label class="label">Agrupación territorial</label>
                <select v-model="asistente.agrupacionId" class="input">
                  <option :value="null">— Toda la organización —</option>
                  <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre }}</option>
                </select>
              </div>
            </template>

            <!-- REENVIO -->
            <template v-else-if="asistente.tipo === 'REENVIO'">
              <div>
                <label class="label">Remesa origen (con fallidos) *</label>
                <select v-model="asistente.remesaOrigenId" class="input">
                  <option :value="null">— Selecciona una remesa procesada con fallidos —</option>
                  <option v-for="r in remesasReenviables" :key="r.id" :value="r.id">
                    {{ r.referencia }} — {{ fechaFmt(r.fechaCobro) }} ({{ r.numOrdenes }} órdenes)
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Fecha de cobro *</label>
                <input type="date" v-model="asistente.fechaCobro" :min="fechaMinimaFrst" class="input" />
                <p class="text-[11px] text-slate-500 mt-0.5">Mínimo 14 días después de hoy (FRST).</p>
              </div>
              <div>
                <label class="label">Observaciones</label>
                <textarea v-model="asistente.observaciones" class="input h-16" placeholder="Opcional…" />
              </div>
            </template>

            <ErrorAlert v-if="asistente.error" :message="asistente.error" />
          </div>

          <!-- PASO 3: Confirmar -->
          <div v-else-if="asistente.paso === 3" class="space-y-3 text-sm">
            <p class="text-slate-700">Vas a crear la siguiente remesa:</p>
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-1">
              <p><b>Tipo:</b> {{ tipoLabel(asistente.tipo) }}</p>
              <p v-if="asistente.tipo !== 'REENVIO'"><b>Ejercicio:</b> {{ asistente.ejercicio }}</p>
              <p><b>Fecha de cobro:</b> {{ fechaFmt(asistente.fechaCobro) }}</p>
              <p v-if="asistente.tipo === 'ORDINARIA'"><b>SeqTp:</b> {{ asistente.seqTipo }}</p>
              <p v-if="asistente.tipo === 'EXTRAORDINARIA'">
                <b>Concepto:</b> {{ asistente.concepto }}<br>
                <b>Importe por miembro:</b> {{ fmt(asistente.importePorMiembro) }}<br>
                <b>Destinatarios:</b> {{ miembrosParseados.length }}
              </p>
              <p v-if="asistente.tipo === 'REENVIO'">
                <b>Remesa origen:</b> {{ remesas.find(r => r.id === asistente.remesaOrigenId)?.referencia || '—' }}
              </p>
              <p v-if="preview && asistente.tipo === 'ORDINARIA'">
                <b>Cuotas a incluir:</b> {{ preview.nIncluidas }} · <b>Importe total:</b> {{ fmt(preview.importeTotal) }}
              </p>
            </div>
            <p class="text-xs text-slate-500">
              La remesa se creará en estado <b>Borrador</b>. Después podrás generar el XML SEPA, marcarla como enviada
              y, al recibir respuesta del banco, liquidarla.
            </p>
            <ErrorAlert v-if="asistente.error" :message="asistente.error" />
          </div>
        </div>

        <div class="px-6 py-4 border-t border-slate-200 flex justify-between">
          <button @click="pasoAnterior()" class="btn-secondary text-sm" :disabled="asistente.paso === 1">← Anterior</button>
          <div class="flex gap-2">
            <button @click="cerrarAsistente()" class="btn-secondary text-sm">Cancelar</button>
            <button v-if="asistente.paso < 3" @click="pasoSiguiente()" class="btn-primary text-sm" :disabled="!puedeAvanzar">
              Siguiente →
            </button>
            <button v-else @click="confirmarCreacion()" class="btn-primary text-sm" :disabled="ocupado">
              {{ ocupado ? 'Creando…' : 'Crear remesa' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pantalla 5.1 — Liquidación de remesa (Flujo 4) -->
    <LiquidacionRemesaModal
      v-if="remesaParaLiquidar"
      :remesa="remesaParaLiquidar"
      :cuentas-bancarias="cuentasBancarias"
      @close="remesaParaLiquidar = null"
      @liquidada="onLiquidada"
    />

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useConfirm } from '@/composables/useConfirm'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import LiquidacionRemesaModal from './LiquidacionRemesaModal.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { executeQuery } from '@/graphql/client'
import { GET_REMESA_DETALLE } from '@/graphql/queries/economico'
const confirmDialog = useConfirm()

const { query: gqlQuery, mutation: gqlMutation, loading } = useGraphQL()
const { unidades } = useUnidadesOrganizativas()

// ── Estado principal ──────────────────────────────────────────────────────────
const remesas = ref([])
const seleccionada = ref(null)
const cuentasBancarias = ref([])
const error = ref('')
const ocupado = ref(false)
const remesaParaLiquidar = ref(null)

// ── FilterBar ─────────────────────────────────────────────────────────────────
const filtros = ref({ ejercicio: null, tipo: [], estado: [], agrupacionId: null })

const camposFiltro = computed(() => [
  {
    key: 'ejercicio', label: 'Ejercicio', type: 'select',
    options: anosDisponibles.value.map(y => ({ value: y, label: String(y) })),
    allLabel: 'Todos los ejercicios',
  },
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect',
    options: [
      { value: 'ORDINARIA',     label: 'Ordinaria' },
      { value: 'EXTRAORDINARIA',label: 'Extraordinaria' },
      { value: 'REENVIO',       label: 'Reenvío' },
    ],
    allLabel: 'Todos los tipos',
  },
  {
    key: 'estado', label: 'Estado', type: 'multiselect',
    options: [
      { value: 'Borrador',  label: 'Borrador' },
      { value: 'Generada',  label: 'Generada' },
      { value: 'Enviada',   label: 'Enviada' },
      { value: 'Procesada', label: 'Procesada' },
      { value: 'Parcial',   label: 'Parcial' },
      { value: 'Rechazada', label: 'Rechazada' },
      { value: 'Anulada',   label: 'Anulada' },
    ],
    allLabel: 'Todos los estados',
  },
  {
    key: 'agrupacionId', label: 'Agrupación', type: 'select',
    options: (unidades.value || []).map(u => ({ value: u.id, label: u.nombre })),
    allLabel: 'Todas',
  },
])

const descripcionFiltros = computed(() => {
  const parts = []
  if (filtros.value.ejercicio) parts.push(`ejercicio ${filtros.value.ejercicio}`)
  if (filtros.value.tipo?.length) parts.push(`${filtros.value.tipo.length} tipo(s)`)
  if (filtros.value.estado?.length) parts.push(`${filtros.value.estado.length} estado(s)`)
  if (filtros.value.agrupacionId) parts.push('agrupación filtrada')
  return parts.join(' · ')
})

// ── Computed ──────────────────────────────────────────────────────────────────
const anosDisponibles = computed(() => {
  const years = [...new Set(remesas.value.map(r => r.fechaCobro?.slice(0, 4)).filter(Boolean))]
  return years.sort().reverse()
})

const remesasFiltradas = computed(() => {
  return remesas.value.filter(r => {
    if (filtros.value.ejercicio && !(r.fechaCobro || '').startsWith(String(filtros.value.ejercicio))) return false
    if (filtros.value.tipo?.length && !filtros.value.tipo.includes(r.tipoRemesa)) return false
    if (filtros.value.estado?.length && !filtros.value.estado.includes(r.estado?.nombre)) return false
    if (filtros.value.agrupacionId && r.agrupacion?.id !== filtros.value.agrupacionId) return false
    return true
  })
})

const remesasReenviables = computed(() =>
  remesas.value.filter(r => ['Procesada','Parcial'].includes(r.estado?.nombre))
)

// ── Asistente ─────────────────────────────────────────────────────────────────
const _hoy = new Date()
const _addDays = (n) => {
  const d = new Date(_hoy); d.setDate(d.getDate() + n)
  return d.toISOString().split('T')[0]
}
const fechaMinimaRcur = _addDays(2)
const fechaMinimaFrst = _addDays(14)
const fechaMinimaOoff = _addDays(14)

const asistente = ref({
  abierto: false,
  paso: 1,
  tipo: 'ORDINARIA',
  ejercicio: new Date().getFullYear(),
  fechaCobro: '',
  agrupacionId: null,
  concepto: '',
  seqTipo: 'RCUR',
  importePorMiembro: 0,
  miembroIdsRaw: '',
  remesaOrigenId: null,
  observaciones: '',
  error: '',
})

const preview = ref(null)
const cargandoPreview = ref(false)

const pasoTitulo = computed(() => ({
  1: 'Tipo de remesa',
  2: 'Parámetros',
  3: 'Confirmar',
}[asistente.value.paso]))

const miembrosParseados = computed(() =>
  (asistente.value.miembroIdsRaw || '')
    .split(/\s+/)
    .map(s => s.trim())
    .filter(s => s.length >= 32)
)

const puedeAvanzar = computed(() => {
  const a = asistente.value
  if (a.paso === 1) return !!a.tipo
  if (a.paso === 2) {
    if (!a.fechaCobro) return false
    if (a.tipo === 'ORDINARIA') {
      return !!preview.value && !preview.value.ordinariaExistente && preview.value.nIncluidas > 0
    }
    if (a.tipo === 'EXTRAORDINARIA') {
      return !!a.concepto && a.importePorMiembro > 0 && miembrosParseados.value.length > 0
    }
    if (a.tipo === 'REENVIO') return !!a.remesaOrigenId
  }
  return true
})

const abrirAsistente = () => {
  Object.assign(asistente.value, {
    abierto: true,
    paso: 1,
    tipo: 'ORDINARIA',
    ejercicio: new Date().getFullYear(),
    fechaCobro: '',
    agrupacionId: null,
    concepto: '',
    seqTipo: 'RCUR',
    importePorMiembro: 0,
    miembroIdsRaw: '',
    remesaOrigenId: null,
    observaciones: '',
    error: '',
  })
  preview.value = null
}

const cerrarAsistente = () => { asistente.value.abierto = false; preview.value = null }
const pasoSiguiente = () => { if (puedeAvanzar.value && asistente.value.paso < 3) asistente.value.paso++ }
const pasoAnterior  = () => { if (asistente.value.paso > 1) asistente.value.paso-- }

const cargarPreview = async () => {
  asistente.value.error = ''
  cargandoPreview.value = true
  try {
    const data = await gqlMutation(`
      mutation Preview($ejercicio: Int!, $agrupacionId: UUID) {
        previsualizarRemesa(ejercicio: $ejercicio, agrupacionId: $agrupacionId) {
          ejercicio nIncluidas nExcluidas importeTotal
          ordinariaExistente { id referencia }
          excluidas { cuotaId miembroId miembroNombre importePendiente motivoExclusion }
        }
      }
    `, { ejercicio: asistente.value.ejercicio, agrupacionId: asistente.value.agrupacionId })
    preview.value = data.previsualizarRemesa
  } catch (e) {
    asistente.value.error = e.message || 'Error al previsualizar'
  } finally {
    cargandoPreview.value = false
  }
}

const confirmarCreacion = async () => {
  asistente.value.error = ''
  ocupado.value = true
  try {
    const a = asistente.value
    if (a.tipo === 'ORDINARIA') {
      await gqlMutation(`
        mutation($ejercicio: Int!, $fechaCobro: Date!, $agrupacionId: UUID, $obs: String) {
          generarRemesaSepa(ejercicio: $ejercicio, fechaCobro: $fechaCobro, agrupacionId: $agrupacionId, observaciones: $obs)
        }
      `, { ejercicio: a.ejercicio, fechaCobro: a.fechaCobro, agrupacionId: a.agrupacionId || null, obs: a.observaciones || null })
    } else if (a.tipo === 'EXTRAORDINARIA') {
      await gqlMutation(`
        mutation($ejercicio: Int!, $fechaCobro: Date!, $concepto: String!, $vinculacionSocioIds: [UUID!]!, $importe: Float!, $agrupacionId: UUID, $obs: String) {
          generarRemesaExtraordinaria(ejercicio: $ejercicio, fechaCobro: $fechaCobro, concepto: $concepto, vinculacionSocioIds: $vinculacionSocioIds, importePorMiembro: $importe, agrupacionId: $agrupacionId, observaciones: $obs)
        }
      `, {
        ejercicio: a.ejercicio, fechaCobro: a.fechaCobro, concepto: a.concepto,
        vinculacionSocioIds: miembrosParseados.value, importe: a.importePorMiembro,
        agrupacionId: a.agrupacionId || null, obs: a.observaciones || null,
      })
    } else if (a.tipo === 'REENVIO') {
      await gqlMutation(`
        mutation($origen: UUID!, $fechaCobro: Date!, $obs: String) {
          generarRemesaFallidos(remesaOrigenId: $origen, fechaCobro: $fechaCobro, observaciones: $obs)
        }
      `, { origen: a.remesaOrigenId, fechaCobro: a.fechaCobro, obs: a.observaciones || null })
    }
    cerrarAsistente()
    await cargarRemesas()
  } catch (e) {
    asistente.value.error = e.message || 'Error al crear la remesa'
  } finally {
    ocupado.value = false
  }
}

const abrirReenvio = (r) => {
  abrirAsistente()
  asistente.value.tipo = 'REENVIO'
  asistente.value.remesaOrigenId = r.id
  asistente.value.paso = 2
}

// ── Carga de datos ────────────────────────────────────────────────────────────
const cargarRemesas = async () => {
  error.value = ''
  try {
    const data = await gqlQuery(`
      query {
        remesas {
          id referencia tipoRemesa importeTotal numOrdenes
          fechaCreacion fechaCobro fechaEnvio observaciones
          estado { id nombre }
          agrupacion { id nombre }
        }
      }
    `)
    remesas.value = (data.remesas || []).sort((a, b) =>
      (b.fechaCobro || '').localeCompare(a.fechaCobro || '')
    )
  } catch (e) {
    error.value = 'Error al cargar las remesas'
    console.error(e)
  }
}

const cargarCuentas = async () => {
  try {
    const data = await executeQuery(`query { cuentasBancarias { id nombre iban activa } }`)
    cuentasBancarias.value = (data.cuentasBancarias || []).filter(c => c.activa)
  } catch (e) { console.error('Error cargando cuentas:', e) }
}

// ── Acciones sobre una remesa ────────────────────────────────────────────────
const descargarXml = async (r) => {
  ocupado.value = true
  error.value = ''
  try {
    const data = await gqlMutation(`mutation($id: UUID!) { generarXmlSepa(remesaId: $id) }`, { id: r.id })
    const b64 = data.generarXmlSepa
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${r.referencia}.xml`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message || 'Error generando XML SEPA. Verifica los datos del acreedor en Parámetros Generales.'
  } finally {
    ocupado.value = false
  }
}

const marcarEnviada = async (remesaId) => {
  ocupado.value = true
  try {
    await gqlMutation(`mutation($id: UUID!) { marcarRemesaEnviada(remesaId: $id) }`, { id: remesaId })
    await cargarRemesas()
    seleccionada.value = remesas.value.find(r => r.id === remesaId) || null
  } catch (e) {
    error.value = e.message || 'Error al marcar como enviada'
  } finally { ocupado.value = false }
}

const anularRemesa = async (r) => {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: `¿Anular la remesa ${r.referencia}? Se liberarán sus cuotas y se anularán los recibos asociados.`, variante: 'critica' }))) return
  ocupado.value = true
  try {
    await gqlMutation(`mutation($id: UUID!) { anularRemesa(remesaId: $id) }`, { id: r.id })
    await cargarRemesas()
    seleccionada.value = null
  } catch (e) {
    error.value = e.message || 'Error al anular la remesa'
  } finally { ocupado.value = false }
}

const abrirModalLiquidar = async (r) => {
  try {
    const data = await gqlQuery(GET_REMESA_DETALLE, { id: r.id })
    const detalle = (data.remesas || [])[0]
    if (!detalle) { error.value = 'No se pudo cargar el detalle de la remesa'; return }
    remesaParaLiquidar.value = detalle
  } catch (e) {
    error.value = e.message || 'Error cargando el detalle'
  }
}

const onLiquidada = async () => {
  remesaParaLiquidar.value = null
  await cargarRemesas()
  if (seleccionada.value) {
    seleccionada.value = remesas.value.find(r => r.id === seleccionada.value.id) || null
  }
}

// ── Helpers de formato ────────────────────────────────────────────────────────
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

// Acorta referencias legacy "SEPA_ISO20022CORE_YYYY-MM-DDTHH-MM-SS.xml" → "2025-10-03 18:30"
// Las nuevas REM-{YYYY}-{NNN} se devuelven tal cual.
const formatRef = (ref) => {
  if (!ref) return '—'
  const m = ref.match(/SEPA_ISO20022CORE_(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})/)
  if (m) return `${m[1]} ${m[2]}:${m[3]}`
  return ref.replace(/\.xml$/, '')
}

const tipoLabel = (t) => ({
  ORDINARIA: 'Ordinaria',
  EXTRAORDINARIA: 'Extraordinaria',
  REENVIO: 'Reenvío',
}[t] || t || '—')

const badgeTipo = (t) => ({
  ORDINARIA:      'bg-indigo-50 text-indigo-700 border border-indigo-100',
  EXTRAORDINARIA: 'bg-amber-50 text-amber-700 border border-amber-100',
  REENVIO:        'bg-purple-50 text-purple-700 border border-purple-100',
}[t] || 'bg-slate-50 text-slate-600 border border-slate-100')

const badgeEstado = (nombre) => ({
  'Borrador':  'bg-slate-100 text-slate-600',
  'Generada':  'bg-blue-100 text-blue-700',
  'Enviada':   'bg-amber-100 text-amber-700',
  'Procesada': 'bg-green-100 text-green-700',
  'Parcial':   'bg-orange-100 text-orange-700',
  'Rechazada': 'bg-red-100 text-red-700',
  'Anulada':   'bg-slate-100 text-slate-400',
}[nombre] || 'bg-slate-100 text-slate-500')

onMounted(async () => {
  await Promise.all([cargarRemesas(), cargarCuentas()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.btn-danger    { @apply px-3 py-1.5 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
.input-sm      { @apply px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
</style>
