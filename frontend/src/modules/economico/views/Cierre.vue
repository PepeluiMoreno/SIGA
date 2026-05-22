<template>
  <AppLayout title="Cierre de ejercicio" subtitle="Regularización, cierre y apertura conforme a PCESFL 2013">

    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4 flex items-end gap-4">
      <div>
        <label class="label">Ejercicio</label>
        <select v-model.number="ejercicio" @change="recargar" class="input">
          <option v-for="y in anosDisponibles" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="error" class="text-red-700 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mb-4 flex items-start gap-3">
      <span class="font-semibold shrink-0">⚠</span>
      <span class="flex-1">{{ error }}</span>
      <button @click="error = ''" class="text-red-400 hover:text-red-700 leading-none">×</button>
    </div>
    <p v-if="info" class="text-green-700 text-sm bg-green-50 p-3 rounded-lg mb-4">{{ info }}</p>

    <!-- CHECKLIST -->
    <div class="bg-white border border-slate-200 rounded-xl mb-4 overflow-hidden">
      <div class="px-4 py-3 bg-slate-50 border-b border-slate-100">
        <h3 class="font-semibold text-sm text-slate-800">Checklist del cierre — Ejercicio {{ ejercicio }}</h3>
      </div>
      <ul v-if="estado" class="divide-y divide-slate-100 text-sm">
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.todosConfirmados ? 'text-green-600' : 'text-red-500'">{{ estado.todosConfirmados ? '✓' : '✗' }}</span>
          <span class="flex-1">Todos los asientos confirmados</span>
          <span class="text-xs text-slate-500">
            {{ estado.todosConfirmados ? 'OK' : `${estado.numBorradores} en BORRADOR` }}
          </span>
        </li>
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.balanceCuadra ? 'text-green-600' : 'text-red-500'">{{ estado.balanceCuadra ? '✓' : '✗' }}</span>
          <span class="flex-1">Balance cuadra (Σ debe = Σ haber)</span>
          <span class="text-xs text-slate-500 font-mono">{{ fmt(estado.totalDebe) }} / {{ fmt(estado.totalHaber) }}</span>
        </li>
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.conciliacionCompleta ? 'text-green-600' : 'text-red-500'">{{ estado.conciliacionCompleta ? '✓' : '✗' }}</span>
          <span class="flex-1">Conciliación bancaria completa</span>
          <span class="text-xs text-slate-500">
            <template v-if="estado.conciliacionCompleta">OK</template>
            <template v-else>
              {{ estado.numApuntesSinConciliar }} apunte(s) sin conciliar
              ·
              <router-link to="/economico/conciliacion" class="text-indigo-600 hover:underline">
                ir a conciliación
              </router-link>
            </template>
          </span>
        </li>
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.regularizacionHecha ? 'text-green-600' : 'text-slate-400'">{{ estado.regularizacionHecha ? '✓' : '·' }}</span>
          <span class="flex-1">Asiento de regularización generado</span>
          <span class="text-xs text-slate-500">{{ estado.regularizacionHecha ? 'OK' : 'Pendiente' }}</span>
        </li>
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.cierreHecho ? 'text-green-600' : 'text-slate-400'">{{ estado.cierreHecho ? '✓' : '·' }}</span>
          <span class="flex-1">Asiento de cierre generado</span>
          <span class="text-xs text-slate-500">{{ estado.cierreHecho ? 'OK' : 'Pendiente' }}</span>
        </li>
        <li class="px-4 py-2 flex items-center gap-3">
          <span :class="estado.aperturaSiguienteHecha ? 'text-green-600' : 'text-slate-400'">{{ estado.aperturaSiguienteHecha ? '✓' : '·' }}</span>
          <span class="flex-1">Asiento de apertura del ejercicio {{ ejercicio + 1 }} generado</span>
          <span class="text-xs text-slate-500">{{ estado.aperturaSiguienteHecha ? 'OK' : 'Pendiente' }}</span>
        </li>
      </ul>
      <div v-else class="px-4 py-4 text-slate-400 text-sm">Cargando estado…</div>
    </div>

    <!-- ACCIONES -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4">
      <h3 class="font-semibold text-sm text-slate-800 mb-3">Acciones del cierre</h3>
      <div class="flex flex-wrap gap-3">
        <button @click="ejecutarRegularizacion" :disabled="!puedeRegularizar || ocupado" class="btn-primary text-sm">
          1. Generar regularización
        </button>
        <button @click="ejecutarCierre" :disabled="!puedeCerrar || ocupado" class="btn-primary text-sm">
          2. Generar cierre
        </button>
        <button @click="ejecutarApertura" :disabled="!puedeAbrir || ocupado" class="btn-primary text-sm">
          3. Generar apertura del ejercicio {{ ejercicio + 1 }}
        </button>
      </div>
      <p class="text-xs text-slate-500 mt-3">
        Cada acción habilita la siguiente. La regularización exige todos los asientos en CONFIRMADO;
        el cierre exige conciliación bancaria completa.
      </p>
    </div>

    <!-- DOCUMENTOS -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4">
      <h3 class="font-semibold text-sm text-slate-800 mb-3">Documentos del ejercicio</h3>
      <div class="flex flex-wrap gap-3">
        <button @click="descargarLibroDiario" :disabled="ocupado" class="btn-secondary text-sm">
          ↓ Libro Diario (CSV)
        </button>
        <button @click="cargarBalance" :disabled="ocupado" class="btn-secondary text-sm">
          Ver Balance PCESFL
        </button>
        <button @click="cargarResultados" :disabled="ocupado" class="btn-secondary text-sm">
          Ver Cuenta de Resultados
        </button>
        <router-link
          v-if="estado && estado.cierreHecho"
          to="/economico/cuentas-anuales"
          class="px-3 py-1.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700"
        >
          → Preparar Cuentas Anuales
        </router-link>
      </div>
    </div>

    <!-- BALANCE PCESFL -->
    <div v-if="balance" class="bg-white border border-slate-200 rounded-xl p-4 mb-4 text-sm">
      <h3 class="font-semibold text-slate-800 mb-3">Balance PCESFL {{ balance.ejercicio }}</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium text-slate-700 mb-1 text-xs uppercase">Activo</h4>
          <div class="overflow-x-auto -mx-1"><<table class="w-full text-xs">
            <tbody>
              <tr><td class="py-0.5">A) No corriente</td><td class="text-right font-mono">{{ fmt(sumaSecciones(balance.activoNoCorriente)) }}</td></tr>
              <tr><td class="py-0.5">B) Corriente</td><td class="text-right font-mono">{{ fmt(sumaSecciones(balance.activoCorriente)) }}</td></tr>
              <tr class="border-t border-slate-200 font-semibold"><td class="py-1">TOTAL ACTIVO</td><td class="text-right font-mono">{{ fmt(balance.totalActivo) }}</td></tr>
            </tbody>
          </table></div>
        </div>
        <div>
          <h4 class="font-medium text-slate-700 mb-1 text-xs uppercase">Patrimonio neto y pasivo</h4>
          <div class="overflow-x-auto -mx-1"><<table class="w-full text-xs">
            <tbody>
              <tr><td class="py-0.5">A) Patrimonio neto</td><td class="text-right font-mono">{{ fmt(balance.totalPatrimonioNeto) }}</td></tr>
              <tr><td class="py-0.5">B) Pasivo no corriente</td><td class="text-right font-mono">{{ fmt(balance.totalPasivoNoCorriente) }}</td></tr>
              <tr><td class="py-0.5">C) Pasivo corriente</td><td class="text-right font-mono">{{ fmt(balance.totalPasivoCorriente) }}</td></tr>
              <tr class="border-t border-slate-200 font-semibold"><td class="py-1">TOTAL PN + PASIVO</td><td class="text-right font-mono">{{ fmt(balance.totalPasivoYPn) }}</td></tr>
            </tbody>
          </table></div>
        </div>
      </div>
      <p class="mt-3 text-xs" :class="balance.cuadra ? 'text-green-700' : 'text-red-600'">
        {{ balance.cuadra ? '✓ El balance cuadra' : `⚠ Diferencia: ${fmt(balance.diferencia)}` }}
      </p>
    </div>

    <!-- Modal de confirmación reutilizable -->
    <ConfirmActionModal
      v-model="modal.abierto"
      :titulo="modal.titulo"
      :mensaje="modal.mensaje"
      :etiqueta-confirmar="modal.etiquetaConfirmar"
      :variante="modal.variante"
      @confirm="onConfirmModal"
      @cancel="onCancelModal"
    />

    <!-- CUENTA DE RESULTADOS -->
    <div v-if="resultados" class="bg-white border border-slate-200 rounded-xl p-4 mb-4 text-sm">
      <h3 class="font-semibold text-slate-800 mb-3">Cuenta de Resultados (Excedente) {{ resultados.ejercicio }}</h3>
      <div class="overflow-x-auto -mx-1"><<table class="w-full text-xs">
        <tbody>
          <tr><td class="py-0.5">Ingresos actividad propia</td><td class="text-right font-mono text-green-700">{{ fmt(resultados.ingresosActividadPropia) }}</td></tr>
          <tr><td class="py-0.5">Gastos actividad propia</td><td class="text-right font-mono text-red-600">−{{ fmt(resultados.gastosActividadPropia) }}</td></tr>
          <tr class="border-t border-slate-100"><td class="py-0.5 italic">Excedente actividad propia</td><td class="text-right font-mono italic">{{ fmt(resultados.excedenteActividadPropia) }}</td></tr>

          <tr><td class="py-0.5 pt-3">Ingresos mercantiles</td><td class="text-right font-mono text-green-700">{{ fmt(resultados.ingresosMercantil) }}</td></tr>
          <tr><td class="py-0.5">Gastos mercantiles</td><td class="text-right font-mono text-red-600">−{{ fmt(resultados.gastosMercantil) }}</td></tr>
          <tr class="border-t border-slate-100"><td class="py-0.5 italic">Excedente mercantil</td><td class="text-right font-mono italic">{{ fmt(resultados.excedenteMercantil) }}</td></tr>

          <tr><td class="py-0.5 pt-3">Ingresos financieros</td><td class="text-right font-mono text-green-700">{{ fmt(resultados.ingresosFinancieros) }}</td></tr>
          <tr><td class="py-0.5">Gastos financieros</td><td class="text-right font-mono text-red-600">−{{ fmt(resultados.gastosFinancieros) }}</td></tr>
          <tr class="border-t border-slate-100"><td class="py-0.5 italic">Resultado financiero</td><td class="text-right font-mono italic">{{ fmt(resultados.resultadoFinanciero) }}</td></tr>

          <tr class="border-t border-slate-200"><td class="py-1">Excedente antes de impuestos</td><td class="text-right font-mono">{{ fmt(resultados.excedenteAntesImpuestos) }}</td></tr>
          <tr><td class="py-0.5">Impuesto sobre beneficios</td><td class="text-right font-mono text-red-600">−{{ fmt(resultados.impuestoSobreBeneficios) }}</td></tr>
          <tr class="border-t-2 border-slate-300 font-bold"><td class="py-1.5">EXCEDENTE DEL EJERCICIO</td><td class="text-right font-mono">{{ fmt(resultados.excedenteEjercicio) }}</td></tr>
        </tbody>
      </table></div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ConfirmActionModal from '@/components/common/ConfirmActionModal.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_ESTADO_CIERRE,
  GET_BALANCE_PCESFL,
  GET_CUENTA_RESULTADOS,
  GET_LIBRO_DIARIO_CSV,
  GENERAR_ASIENTO_REGULARIZACION,
  GENERAR_ASIENTO_CIERRE,
  GENERAR_ASIENTO_APERTURA,
} from '@/graphql/queries/financiero'

const { query, mutation } = useGraphQL()

const ejercicio = ref(new Date().getFullYear() - 1)  // por defecto el anterior, que es el que se cierra
const estado = ref(null)
const balance = ref(null)
const resultados = ref(null)
const ocupado = ref(false)
const error = ref('')
const info = ref('')

const anosDisponibles = computed(() => {
  const y = new Date().getFullYear()
  return [y, y - 1, y - 2, y - 3, y - 4]
})

const puedeRegularizar = computed(() =>
  estado.value && estado.value.todosConfirmados && estado.value.balanceCuadra && !estado.value.regularizacionHecha
)
const puedeCerrar = computed(() =>
  estado.value && estado.value.regularizacionHecha
    && estado.value.conciliacionCompleta && !estado.value.cierreHecho
)
const puedeAbrir = computed(() =>
  estado.value && estado.value.cierreHecho && !estado.value.aperturaSiguienteHecha
)

// Extrae solo el `message` del primer error GraphQL (sin el dump del response).
const errMsg = (e, fallback = 'Error') => {
  if (e?.response?.errors?.[0]?.message) return e.response.errors[0].message
  if (typeof e?.message === 'string') {
    // graphql-request añade el response JSON al final del message: cortar al `: {`.
    const i = e.message.indexOf(': {')
    return i > 0 ? e.message.slice(0, i) : e.message
  }
  return fallback
}

// ── Modal de confirmación genérico ──────────────────────────────────────────
const modal = ref({
  abierto: false,
  titulo: '',
  mensaje: '',
  etiquetaConfirmar: 'Confirmar',
  variante: 'aviso',  // 'primaria' | 'aviso' | 'critica' | 'exito'
  _resolver: null,
})
const confirmarAccion = (opts) => new Promise((resolve) => {
  modal.value = {
    abierto: true,
    titulo: opts.titulo,
    mensaje: opts.mensaje,
    etiquetaConfirmar: opts.etiquetaConfirmar || 'Confirmar',
    variante: opts.variante || 'aviso',
    _resolver: resolve,
  }
})
const onConfirmModal = () => { const r = modal.value._resolver; modal.value.abierto = false; r?.(true) }
const onCancelModal  = () => { const r = modal.value._resolver; modal.value.abierto = false; r?.(false) }

const cargarEstado = async () => {
  try {
    const data = await query(GET_ESTADO_CIERRE, { ejercicio: ejercicio.value })
    estado.value = data.estadoCierre
  } catch (e) {
    error.value = errMsg(e, 'Error al cargar el estado del cierre')
  }
}

const recargar = async () => {
  balance.value = null
  resultados.value = null
  error.value = ''
  info.value = ''
  await cargarEstado()
}

const cargarBalance = async () => {
  error.value = ''
  ocupado.value = true
  try {
    const data = await query(GET_BALANCE_PCESFL, { ejercicio: ejercicio.value, fechaFin: null })
    balance.value = data.balancePcesfl
  } catch (e) { error.value = errMsg(e, 'Error al cargar el balance') } finally { ocupado.value = false }
}

const cargarResultados = async () => {
  error.value = ''
  ocupado.value = true
  try {
    const data = await query(GET_CUENTA_RESULTADOS, { ejercicio: ejercicio.value, fechaFin: null })
    resultados.value = data.cuentaResultados
  } catch (e) { error.value = errMsg(e, 'Error al cargar la cuenta de resultados') } finally { ocupado.value = false }
}

const descargarLibroDiario = async () => {
  error.value = ''
  ocupado.value = true
  try {
    const data = await query(GET_LIBRO_DIARIO_CSV, {
      ejercicio: ejercicio.value,
      organizacionNombre: 'Asociación SIGA',
    })
    const b64 = data.libroDiarioCsv
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `libro-diario-${ejercicio.value}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = errMsg(e, 'Error al descargar el Libro Diario')
  } finally { ocupado.value = false }
}

const ejecutarRegularizacion = async () => {
  const ok = await confirmarAccion({
    titulo: `Generar regularización del ejercicio ${ejercicio.value}`,
    mensaje: 'Se saldarán las cuentas de gastos e ingresos contra la 129 «Excedente del ejercicio». '
           + 'La operación puede deshacerse anulando el asiento mientras no se haya generado el cierre.',
    etiquetaConfirmar: 'Generar regularización',
    variante: 'primaria',
  })
  if (!ok) return
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    await mutation(GENERAR_ASIENTO_REGULARIZACION, { ejercicio: ejercicio.value })
    info.value = 'Regularización generada correctamente.'
    await cargarEstado()
  } catch (e) { error.value = errMsg(e, 'Error al regularizar') } finally { ocupado.value = false }
}

const ejecutarCierre = async () => {
  const ok = await confirmarAccion({
    titulo: `Cerrar el ejercicio ${ejercicio.value}`,
    mensaje: 'Se generará el asiento de CIERRE: las cuentas de balance se saldarán y el ejercicio quedará '
           + 'inmutable. Esta acción solo procede tras la regularización y la conciliación bancaria completa.',
    etiquetaConfirmar: 'Generar cierre',
    variante: 'aviso',
  })
  if (!ok) return
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    await mutation(GENERAR_ASIENTO_CIERRE, { ejercicio: ejercicio.value })
    info.value = 'Cierre del ejercicio generado correctamente.'
    await cargarEstado()
  } catch (e) { error.value = errMsg(e, 'Error al cerrar el ejercicio') } finally { ocupado.value = false }
}

const ejecutarApertura = async () => {
  const proximo = ejercicio.value + 1
  const ok = await confirmarAccion({
    titulo: `Abrir el ejercicio ${proximo}`,
    mensaje: `Se generará el asiento de APERTURA del ejercicio ${proximo} arrastrando los saldos `
           + `del cierre del ${ejercicio.value}. A partir de ese momento podrás registrar movimientos del nuevo ejercicio.`,
    etiquetaConfirmar: 'Generar apertura',
    variante: 'primaria',
  })
  if (!ok) return
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    await mutation(GENERAR_ASIENTO_APERTURA, { ejercicioNuevo: proximo })
    info.value = `Apertura del ejercicio ${proximo} generada correctamente.`
    await cargarEstado()
  } catch (e) { error.value = errMsg(e, 'Error al abrir el ejercicio siguiente') } finally { ocupado.value = false }
}

const sumaSecciones = (obj) => {
  if (!obj || typeof obj !== 'object') return 0
  return Object.values(obj).reduce((s, v) => s + (parseFloat(v) || 0), 0)
}

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)

onMounted(cargarEstado)
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
</style>
