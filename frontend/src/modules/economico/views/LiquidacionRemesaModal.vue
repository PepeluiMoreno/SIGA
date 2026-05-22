<template>
  <!-- Pantalla 5.1 — Liquidar remesa con respuesta del banco (Flujo 4) -->
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="cerrar">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-slate-200">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold text-slate-800">
              Liquidar remesa <span class="font-mono text-indigo-700">{{ remesa.referencia }}</span>
            </h3>
            <p class="text-sm text-slate-500 mt-1">
              {{ remesa.numOrdenes }} órdenes ·
              Total emitido <strong>{{ fmt(remesa.importeTotal) }}</strong> ·
              Cobro programado {{ fechaFmt(remesa.fechaCobro) }}
            </p>
          </div>
          <button @click="cerrar" class="text-slate-400 hover:text-slate-700 text-2xl leading-none">×</button>
        </div>
      </div>

      <!-- Paso 1: Cargar respuesta del banco -->
      <div v-if="paso === 'cargar'" class="p-6 space-y-4">
        <h4 class="font-medium text-slate-700">1. Carga la respuesta del banco</h4>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          <button
            v-for="t in tiposFichero" :key="t.id"
            @click="tipoFichero = t.id"
            :class="[
              'px-4 py-3 rounded-lg border text-sm text-left transition-colors',
              tipoFichero === t.id
                ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                : 'border-slate-200 hover:bg-slate-50'
            ]"
          >
            <div class="font-medium">{{ t.label }}</div>
            <div class="text-xs text-slate-500 mt-0.5">{{ t.descr }}</div>
          </button>
        </div>

        <div v-if="tipoFichero === 'pain002' || tipoFichero === 'camt054'">
          <label class="label">Fichero XML del banco *</label>
          <input
            type="file" accept=".xml"
            @change="onFichero"
            class="block w-full text-sm border border-slate-200 rounded-lg p-2"
          />
          <p v-if="ficheroNombre" class="text-xs text-slate-500 mt-1">Seleccionado: {{ ficheroNombre }}</p>
        </div>

        <div v-else-if="tipoFichero === 'manual'" class="space-y-3">
          <p class="text-sm text-slate-600">
            Marca las órdenes que el banco ha rechazado con su código SEPA.
            Las que no marques se considerarán cobradas.
          </p>
          <div class="border border-slate-200 rounded-lg max-h-64 overflow-y-auto">
            <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm">
              <thead class="bg-slate-50 sticky top-0">
                <tr>
                  <th class="px-3 py-2 text-left text-xs text-slate-500 w-10">¿Fallida?</th>
                  <th class="px-3 py-2 text-left text-xs text-slate-500">Orden</th>
                  <th class="px-3 py-2 text-left text-xs text-slate-500">Socio</th>
                  <th class="px-3 py-2 text-right text-xs text-slate-500">Importe</th>
                  <th class="px-3 py-2 text-left text-xs text-slate-500">Código SEPA</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="o in remesa.ordenes" :key="o.id">
                  <td class="px-3 py-1.5">
                    <input type="checkbox" :value="o.id" v-model="manualSeleccionFallidos" />
                  </td>
                  <td class="px-3 py-1.5 font-mono text-xs">{{ remesa.referencia }}-{{ String(o.nseq).padStart(3,'0') }}</td>
                  <td class="px-3 py-1.5">{{ socioNombre(o) }}</td>
                  <td class="px-3 py-1.5 text-right font-mono">{{ fmt(o.importe) }}</td>
                  <td class="px-3 py-1.5">
                    <select
                      v-model="manualCodigos[o.id]"
                      :disabled="!manualSeleccionFallidos.includes(o.id)"
                      class="input-sm w-full"
                    >
                      <option value="">—</option>
                      <option v-for="(d, c) in codigosSepa" :key="c" :value="c">{{ c }} – {{ d.motivo }}</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table></div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
          <button @click="cerrar" class="btn-secondary">Cancelar</button>
          <button
            @click="previsualizar"
            :disabled="!puedePrevisualizar || cargando"
            class="btn-primary"
          >
            {{ cargando ? 'Procesando…' : 'Previsualizar resultado' }}
          </button>
        </div>
      </div>

      <!-- Paso 2: Previsualización (cobradas vs fallidas) -->
      <div v-else-if="paso === 'preview' && preview" class="p-6 space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="bg-green-50 border border-green-100 rounded-lg p-3">
            <div class="text-xs text-green-700">Cobradas</div>
            <div class="text-2xl font-bold text-green-700">{{ preview.totales.nCobradas }}</div>
            <div class="text-xs text-green-600 mt-1">{{ fmt(preview.totales.importeCobrado) }}</div>
          </div>
          <div class="bg-red-50 border border-red-100 rounded-lg p-3">
            <div class="text-xs text-red-700">Fallidas</div>
            <div class="text-2xl font-bold text-red-700">{{ preview.totales.nFallidas }}</div>
          </div>
          <div class="bg-amber-50 border border-amber-100 rounded-lg p-3">
            <div class="text-xs text-amber-700">No emparejadas</div>
            <div class="text-2xl font-bold text-amber-700">{{ preview.noEmparejadas.length }}</div>
            <div class="text-xs text-amber-600 mt-1">Revisar antes de confirmar</div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Cobradas -->
          <div>
            <h5 class="font-medium text-green-700 mb-2 text-sm">✓ Cobradas ({{ preview.cobradas.length }})</h5>
            <div class="border border-slate-200 rounded-lg max-h-72 overflow-y-auto">
              <div class="overflow-x-auto -mx-1"><<table class="w-full text-xs">
                <thead class="bg-slate-50 sticky top-0">
                  <tr>
                    <th class="px-2 py-1.5 text-left text-slate-500">Orden</th>
                    <th class="px-2 py-1.5 text-left text-slate-500">Socio</th>
                    <th class="px-2 py-1.5 text-right text-slate-500">Importe</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="c in preview.cobradas" :key="c.ordenId">
                    <td class="px-2 py-1 font-mono">{{ c.endToEndId }}</td>
                    <td class="px-2 py-1">{{ c.miembroNombre }}</td>
                    <td class="px-2 py-1 text-right font-mono">{{ fmt(c.importe) }}</td>
                  </tr>
                </tbody>
              </table></div>
            </div>
          </div>

          <!-- Fallidas -->
          <div>
            <h5 class="font-medium text-red-700 mb-2 text-sm">✗ Fallidas ({{ preview.fallidas.length }})</h5>
            <div class="border border-slate-200 rounded-lg max-h-72 overflow-y-auto">
              <div class="overflow-x-auto -mx-1"><<table class="w-full text-xs">
                <thead class="bg-slate-50 sticky top-0">
                  <tr>
                    <th class="px-2 py-1.5 text-left text-slate-500">Orden</th>
                    <th class="px-2 py-1.5 text-left text-slate-500">Código</th>
                    <th class="px-2 py-1.5 text-left text-slate-500">Motivo</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="f in preview.fallidas" :key="f.ordenId">
                    <td class="px-2 py-1 font-mono">{{ f.endToEndId }}</td>
                    <td class="px-2 py-1">
                      <span class="text-xs font-mono bg-red-100 text-red-700 px-1.5 py-0.5 rounded">{{ f.codigo }}</span>
                    </td>
                    <td class="px-2 py-1">{{ f.motivo }}</td>
                  </tr>
                </tbody>
              </table></div>
            </div>
          </div>
        </div>

        <div v-if="preview.noEmparejadas.length" class="bg-amber-50 border border-amber-100 rounded-lg p-3 text-sm">
          <p class="font-medium text-amber-800 mb-1">No emparejadas:</p>
          <ul class="text-xs text-amber-700 space-y-0.5">
            <li v-for="ne in preview.noEmparejadas" :key="ne.endToEndId">
              <span class="font-mono">{{ ne.endToEndId }}</span> — {{ ne.motivo }}
            </li>
          </ul>
        </div>

        <!-- Datos del cobro real -->
        <div class="border-t border-slate-100 pt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="label">Cuenta bancaria del ingreso *</label>
            <select v-model="cuentaBancariaId" class="input">
              <option value="">— Selecciona —</option>
              <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
                {{ c.nombre }} ({{ ibanFmt(c.iban) }})
              </option>
            </select>
          </div>
          <div>
            <label class="label">Fecha de liquidación *</label>
            <input type="date" v-model="fechaLiquidacion" class="input" />
          </div>
        </div>

        <ErrorAlert v-if="errorConfirmar" :message="errorConfirmar" />

        <div class="flex justify-between gap-2 pt-3 border-t border-slate-100">
          <button @click="paso = 'cargar'" class="btn-secondary">← Volver</button>
          <button
            @click="confirmar"
            :disabled="!puedeConfirmar || cargando"
            class="btn-primary"
          >
            {{ cargando ? 'Aplicando…' : 'Confirmar liquidación' }}
          </button>
        </div>
      </div>

      <!-- Paso 3: Resultado -->
      <div v-else-if="paso === 'resultado' && resultado" class="p-6 space-y-4">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="font-medium text-green-800">✓ Liquidación aplicada</p>
          <ul class="text-sm text-green-700 mt-2 space-y-1">
            <li>Cobradas: <strong>{{ resultado.nCobradas }}</strong></li>
            <li>Fallidas: <strong>{{ resultado.nFallidas }}</strong></li>
            <li>Ingresado en cuenta: <strong>{{ fmt(resultado.importeCobrado) }}</strong></li>
            <li>Asiento contable: <strong>{{ resultado.asientoId ? 'generado ✓' : 'no aplicable' }}</strong></li>
            <li>Estado final de la remesa: <strong>{{ resultado.remesaEstado }}</strong></li>
          </ul>
        </div>
        <div class="flex justify-end">
          <button @click="cerrar" class="btn-primary">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { ref, computed } from 'vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
const toast = useToast()
  PREVISUALIZAR_LIQUIDACION_REMESA,
  LIQUIDAR_REMESA,
} from '@/graphql/queries/financiero'

const props = defineProps({
  remesa: { type: Object, required: true },              // remesa completa con ordenes y miembros cargados
  cuentasBancarias: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'liquidada'])

const { mutation } = useGraphQL()

const paso = ref('cargar')                        // cargar | preview | resultado
const tipoFichero = ref('pain002')
const ficheroB64 = ref(null)
const ficheroNombre = ref('')
const manualSeleccionFallidos = ref([])            // array de orden ids fallidas
const manualCodigos = ref({})                      // { ordenId: 'AM04' }
const preview = ref(null)
const resultado = ref(null)
const cuentaBancariaId = ref('')
const fechaLiquidacion = ref(new Date().toISOString().slice(0,10))
const cargando = ref(false)
const errorConfirmar = ref('')

const tiposFichero = [
  { id: 'pain002',  label: 'pain.002',  descr: 'Payment Status Report' },
  { id: 'camt054',  label: 'camt.054',  descr: 'Bank to Customer Notification' },
  { id: 'manual',   label: 'Entrada manual', descr: 'Marcar fallidas a mano' },
]

const codigosSepa = {
  AM04: { motivo: 'Fondos insuficientes' },
  AC04: { motivo: 'Cuenta cerrada' },
  AC01: { motivo: 'Formato de cuenta incorrecto' },
  AC06: { motivo: 'Cuenta bloqueada' },
  AC13: { motivo: 'Deudor no autorizado' },
  MD01: { motivo: 'Mandato no válido' },
  MD02: { motivo: 'Información del mandato incorrecta' },
  MD07: { motivo: 'Cliente fallecido' },
  MS02: { motivo: 'Solicitud de devolución por el deudor' },
  MS03: { motivo: 'Motivo no especificado' },
}

const puedePrevisualizar = computed(() => {
  if (tipoFichero.value === 'manual') return true
  return !!ficheroB64.value
})

const puedeConfirmar = computed(() => {
  return cuentaBancariaId.value && fechaLiquidacion.value && preview.value
})

const socioNombre = (o) => {
  const m = o.cuota?.miembro
  return m ? `${m.nombre || ''} ${m.apellido1 || ''}`.trim() : '—'
}

const fmt = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d)) : ''
const ibanFmt = (iban) => iban ? iban.replace(/(.{4})/g, '$1 ').trim() : ''

const onFichero = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  ficheroNombre.value = file.name
  const buf = await file.arrayBuffer()
  // base64 sin librerías
  const bytes = new Uint8Array(buf)
  let bin = ''
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i])
  ficheroB64.value = btoa(bin)
}

const previsualizar = async () => {
  cargando.value = true
  try {
    const variables = { remesaId: props.remesa.id, tipoFichero: tipoFichero.value }
    if (tipoFichero.value === 'manual') {
      variables.fallidosManual = manualSeleccionFallidos.value.map(id => ({
        ordenId: id,
        codigo: manualCodigos.value[id] || 'MS03',
        motivo: codigosSepa[manualCodigos.value[id] || 'MS03']?.motivo,
        fecha: fechaLiquidacion.value,
      }))
    } else {
      variables.ficheroB64 = ficheroB64.value
    }
    const data = await mutation(PREVISUALIZAR_LIQUIDACION_REMESA, variables)
    preview.value = data.previsualizarLiquidacionRemesa
    paso.value = 'preview'
  } catch (e) {
    toast.error(e.message || 'Error al previsualizar')
  } finally {
    cargando.value = false
  }
}

const confirmar = async () => {
  errorConfirmar.value = ''
  cargando.value = true
  try {
    const data = await mutation(LIQUIDAR_REMESA, {
      remesaId: props.remesa.id,
      cuentaBancariaId: cuentaBancariaId.value,
      fechaLiquidacion: fechaLiquidacion.value,
      cobradas: preview.value.cobradas.map(c => c.ordenId),
      fallidas: preview.value.fallidas.map(f => ({
        ordenId: f.ordenId,
        codigo: f.codigo,
        motivo: f.motivo,
        fecha: f.fecha || fechaLiquidacion.value,
      })),
    })
    resultado.value = data.liquidarRemesa
    paso.value = 'resultado'
    emit('liquidada', resultado.value)
  } catch (e) {
    errorConfirmar.value = e.message || 'Error al liquidar'
  } finally {
    cargando.value = false
  }
}

const cerrar = () => emit('close')
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-slate-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
.input-sm { @apply px-2 py-1 border border-slate-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400; }
</style>
