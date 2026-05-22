<template>
  <AppLayout title="Conciliación bancaria" subtitle="Emparejar apuntes del sistema con líneas del extracto del banco">

    <!-- Selector de cuenta + acciones -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4 flex flex-wrap items-end gap-3">
      <div class="flex-1 min-w-[200px]">
        <label class="label">Cuenta bancaria</label>
        <select v-model="cuentaSeleccionadaId" @change="cargarPendientes" class="input">
          <option :value="null">— Selecciona cuenta —</option>
          <option v-for="c in cuentas" :key="c.id" :value="c.id">
            {{ c.nombre }}{{ c.iban ? ` — ${c.iban}` : '' }}
          </option>
        </select>
      </div>

      <div class="flex gap-2">
        <label class="btn-secondary text-sm cursor-pointer">
          ↑ Importar CSV
          <input type="file" accept=".csv" class="hidden" @change="importarCsv" />
        </label>
        <label class="btn-secondary text-sm cursor-pointer">
          ↑ Importar Norma 43
          <input type="file" accept=".q43,.aeb43,.txt" class="hidden" @change="importarN43" />
        </label>
      </div>
    </div>

    <!-- Aviso Open Banking activo -->
    <div v-if="openbankingActivo" class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 text-sm text-blue-800">
      <strong>Open Banking activo:</strong> los movimientos del banco se sincronizan automáticamente vía PSD2.
      Si no ves líneas recientes, puede que falte renovar la autorización OAuth (caduca cada 90 días).
      <em class="block mt-1 text-xs">Integración en desarrollo: por ahora sigue activa la importación manual como respaldo.</em>
    </div>

    <ErrorAlert v-if="error" :message="error" />
    <p v-if="info" class="text-green-700 text-sm bg-green-50 p-3 rounded-lg mb-4">{{ info }}</p>

    <!-- Tarjeta de info de la cuenta seleccionada -->
    <div v-if="cuentaActual"
      class="bg-white border border-slate-200 rounded-xl p-4 mb-4 grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-x-4 gap-y-3 text-sm">
      <div>
        <p class="text-xs text-slate-500 mb-0.5">Cuenta</p>
        <p class="font-medium text-slate-800">{{ cuentaActual.nombre }}</p>
        <p v-if="cuentaActual.bancoNombre" class="text-xs text-slate-400">{{ cuentaActual.bancoNombre }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-500 mb-0.5">Titular</p>
        <p class="font-medium text-slate-800">{{ cuentaActual.titular || '—' }}</p>
      </div>
      <div class="col-span-2">
        <p class="text-xs text-slate-500 mb-0.5">IBAN</p>
        <p class="font-mono text-slate-800">{{ cuentaActual.iban || '—' }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-500 mb-0.5">Saldo actual</p>
        <p class="font-semibold text-slate-900">{{ fmt(cuentaActual.saldoActual) }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-500 mb-0.5">Saldo conciliado</p>
        <p class="font-semibold text-slate-900">{{ fmt(cuentaActual.saldoConciliado) }}</p>
      </div>
      <div class="col-span-2">
        <p class="text-xs text-slate-500 mb-0.5">Pendiente de conciliar</p>
        <p class="font-semibold" :class="diferenciaSaldo === 0 ? 'text-green-600' : 'text-amber-600'">
          {{ fmt(diferenciaSaldo) }}
        </p>
      </div>
    </div>

    <div v-if="!cuentaSeleccionadaId" class="text-center text-slate-400 py-12 text-sm border border-dashed border-slate-200 rounded-xl">
      Selecciona una cuenta bancaria para empezar.
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Columna izquierda: apuntes del sistema -->
      <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-semibold text-sm text-slate-800">Apuntes del sistema pendientes</h3>
          <span class="text-xs text-slate-500">{{ apuntesPendientes.length }} líneas</span>
        </div>
        <div v-if="!apuntesPendientes.length" class="text-center text-slate-400 py-8 text-xs">
          Sin apuntes pendientes de conciliar.
        </div>
        <div v-else class="overflow-x-auto -mx-1"><table class="w-full text-xs">
          <thead class="bg-slate-50 text-slate-500 text-[10px] uppercase">
            <tr>
              <th class="px-3 py-1.5 text-center w-8"></th>
              <th class="px-3 py-1.5 text-left">Fecha</th>
              <th class="px-3 py-1.5 text-right">Importe</th>
              <th class="px-3 py-1.5 text-left">Concepto</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="a in apuntesPendientes" :key="a.id"
                class="hover:bg-indigo-50 cursor-pointer"
                :class="apunteSel?.id === a.id ? 'bg-indigo-100' : ''"
                @click="apunteSel = apunteSel?.id === a.id ? null : a">
              <td class="px-3 py-1 text-center">
                <input type="radio" :checked="apunteSel?.id === a.id" class="pointer-events-none" />
              </td>
              <td class="px-3 py-1 whitespace-nowrap">{{ fechaFmt(a.fecha) }}</td>
              <td class="px-3 py-1 text-right font-mono" :class="a.tipo === 'GASTO' ? 'text-red-600' : 'text-green-700'">
                {{ a.tipo === 'GASTO' ? '-' : '+' }}{{ fmt(a.importe) }}
              </td>
              <td class="px-3 py-1 truncate max-w-[16rem]">{{ a.concepto }}</td>
            </tr>
          </tbody>
        </table></div>
      </div>

      <!-- Columna derecha: extracto bancario -->
      <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-semibold text-sm text-slate-800">Líneas de extracto pendientes</h3>
          <span class="text-xs text-slate-500">{{ extractosPendientes.length }} líneas</span>
        </div>
        <div v-if="!extractosPendientes.length" class="text-center text-slate-400 py-8 text-xs">
          Sin líneas de extracto pendientes. Importa un extracto bancario para empezar.
        </div>
        <div v-else class="overflow-x-auto -mx-1"><table class="w-full text-xs">
          <thead class="bg-slate-50 text-slate-500 text-[10px] uppercase">
            <tr>
              <th class="px-3 py-1.5 text-center w-8"></th>
              <th class="px-3 py-1.5 text-left">Fecha</th>
              <th class="px-3 py-1.5 text-right">Importe</th>
              <th class="px-3 py-1.5 text-left">Concepto / Ref.</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="e in extractosPendientes" :key="e.id"
                class="hover:bg-indigo-50 cursor-pointer"
                :class="extractoSel?.id === e.id ? 'bg-indigo-100' : ''"
                @click="extractoSel = extractoSel?.id === e.id ? null : e">
              <td class="px-3 py-1 text-center">
                <input type="radio" :checked="extractoSel?.id === e.id" class="pointer-events-none" />
              </td>
              <td class="px-3 py-1 whitespace-nowrap">{{ fechaFmt(e.fecha) }}</td>
              <td class="px-3 py-1 text-right font-mono" :class="(e.importe || 0) < 0 ? 'text-red-600' : 'text-green-700'">
                {{ (e.importe || 0) >= 0 ? '+' : '' }}{{ fmt(e.importe) }}
              </td>
              <td class="px-3 py-1 truncate max-w-[16rem]">
                {{ e.concepto || '—' }}
                <span v-if="e.referencia" class="text-slate-400 ml-1">[{{ e.referencia }}]</span>
              </td>
            </tr>
          </tbody>
        </table></div>
      </div>
    </div>

    <!-- Barra inferior de acción -->
    <div v-if="cuentaSeleccionadaId" class="bg-white border border-slate-200 rounded-xl p-4 mt-4 flex flex-wrap items-center gap-3">
      <div class="text-xs text-slate-600">
        <div v-if="apunteSel && extractoSel">
          Pareja seleccionada:
          <span class="font-mono ml-1">{{ fmt(apunteSel.importe) }}</span>
          (apunte) ↔
          <span class="font-mono">{{ fmt(extractoSel.importe) }}</span>
          (extracto)
          <span v-if="importesCuadran" class="text-green-700 ml-2">✓ importes cuadran</span>
          <span v-else class="text-red-700 ml-2">⚠ importes no coinciden</span>
        </div>
        <div v-else class="text-slate-400">
          Selecciona un apunte y una línea de extracto para emparejar.
        </div>
      </div>
      <div class="ml-auto">
        <button @click="conciliar" :disabled="!apunteSel || !extractoSel || ocupado"
                class="btn-primary text-sm">
          {{ ocupado ? 'Emparejando…' : 'Emparejar →' }}
        </button>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useConfirm } from '@/composables/useConfirm'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_CUENTAS_BANCARIAS_ACTIVAS,
  GET_APUNTES_PARA_CONCILIAR,
  GET_EXTRACTOS_PARA_CONCILIAR,
  CONCILIAR_APUNTE_CON_EXTRACTO,
  IMPORTAR_EXTRACTO_NORMA43,
  IMPORTAR_EXTRACTO_CSV,
  GET_OPENBANKING_ACTIVO,
} from '@/graphql/queries/economico'

const confirmDialog = useConfirm()

const { query, mutation } = useGraphQL()

const cuentas = ref([])
const cuentaSeleccionadaId = ref(null)
const apuntesPendientes = ref([])
const extractosPendientes = ref([])
const apunteSel = ref(null)
const extractoSel = ref(null)
const ocupado = ref(false)
const error = ref('')
const info = ref('')
const openbankingActivo = ref(false)

const cuentaActual = computed(() =>
  cuentas.value.find(c => c.id === cuentaSeleccionadaId.value) || null
)
const diferenciaSaldo = computed(() => {
  const c = cuentaActual.value
  if (!c) return 0
  return Number(c.saldoActual || 0) - Number(c.saldoConciliado || 0)
})

const importesCuadran = computed(() => {
  if (!apunteSel.value || !extractoSel.value) return false
  const a = parseFloat(apunteSel.value.importe || 0)
  const e = parseFloat(extractoSel.value.importe || 0)
  // Apunte INGRESO debería emparejarse con extracto positivo;
  // apunte GASTO con extracto negativo. Importes en valor absoluto deben coincidir.
  return Math.abs(Math.abs(a) - Math.abs(e)) < 0.005
})

const cargarCuentas = async () => {
  try {
    const data = await query(GET_CUENTAS_BANCARIAS_ACTIVAS)
    // El filtro `activa` no existe en el CuentaBancariaFilter de strawchemy (vacío por defecto).
    // Filtramos en cliente.
    cuentas.value = (data.cuentasBancarias || []).filter(c => c.activa)
    if (cuentas.value.length === 1) {
      cuentaSeleccionadaId.value = cuentas.value[0].id
      await cargarPendientes()
    }
  } catch (e) { console.error(e) }
}

const cargarFlagOpenBanking = async () => {
  try {
    const data = await query(GET_OPENBANKING_ACTIVO)
    openbankingActivo.value = !!data.parametrosOrganizacion?.openbankingActivo
  } catch (e) { /* ignorable */ }
}

const cargarPendientes = async () => {
  if (!cuentaSeleccionadaId.value) return
  error.value = ''
  apunteSel.value = null
  extractoSel.value = null
  try {
    const [a, e] = await Promise.all([
      query(GET_APUNTES_PARA_CONCILIAR, { cuentaId: cuentaSeleccionadaId.value }),
      query(GET_EXTRACTOS_PARA_CONCILIAR, { cuentaId: cuentaSeleccionadaId.value }),
    ])
    apuntesPendientes.value = (a.apuntesCaja || []).slice().sort((x, y) => (x.fecha || '').localeCompare(y.fecha || ''))
    extractosPendientes.value = (e.extractosBancarios || []).slice().sort((x, y) => (x.fecha || '').localeCompare(y.fecha || ''))
  } catch (e) {
    error.value = e.message || 'Error al cargar los pendientes'
  }
}

const conciliar = async () => {
  if (!apunteSel.value || !extractoSel.value) return
  if (!importesCuadran.value) {
    if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: 'Los importes no cuadran exactamente. ¿Conciliar de todos modos?', variante: 'aviso' }))) return
  }
  ocupado.value = true
  error.value = ''
  info.value = ''
  try {
    await mutation(CONCILIAR_APUNTE_CON_EXTRACTO, {
      apunteId: apunteSel.value.id,
      extractoId: extractoSel.value.id,
    })
    info.value = 'Emparejamiento registrado correctamente.'
    await cargarPendientes()
  } catch (e) {
    error.value = e.message || 'Error al emparejar'
  } finally { ocupado.value = false }
}

const fileToB64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => {
    const dataUrl = reader.result
    const b64 = dataUrl.split(',')[1]
    resolve(b64)
  }
  reader.onerror = reject
  reader.readAsDataURL(file)
})

const importarN43 = async (ev) => {
  const file = ev.target.files?.[0]; if (!file) return
  if (!cuentaSeleccionadaId.value) { error.value = 'Selecciona una cuenta antes'; return }
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    const b64 = await fileToB64(file)
    const data = await mutation(IMPORTAR_EXTRACTO_NORMA43, { cuentaId: cuentaSeleccionadaId.value, archivoB64: b64 })
    info.value = `${data.importarExtractoNorma43} líneas importadas desde Norma 43.`
    await cargarPendientes()
  } catch (e) {
    error.value = e.message || 'Error al importar Norma 43'
  } finally { ocupado.value = false; ev.target.value = '' }
}

const parseCsv = (texto) => {
  // CSV simple: separador ';' o ',' detectado. Cabecera obligatoria con
  // columnas (en cualquier orden): fecha, importe, concepto, referencia.
  const sep = texto.includes(';') ? ';' : ','
  const lineas = texto.split(/\r?\n/).filter(l => l.trim())
  if (!lineas.length) return []
  const cabeceras = lineas[0].split(sep).map(s => s.trim().toLowerCase())
  const idx = {
    fecha: cabeceras.indexOf('fecha'),
    importe: cabeceras.indexOf('importe'),
    concepto: cabeceras.indexOf('concepto'),
    referencia: cabeceras.indexOf('referencia'),
  }
  if (idx.fecha < 0 || idx.importe < 0) {
    throw new Error('El CSV debe tener cabecera con columnas fecha e importe (al menos).')
  }
  const out = []
  for (let i = 1; i < lineas.length; i++) {
    const cols = lineas[i].split(sep)
    let fecha = cols[idx.fecha]?.trim()
    // Aceptar dd/mm/yyyy → yyyy-mm-dd
    const m = fecha?.match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
    if (m) fecha = `${m[3]}-${m[2]}-${m[1]}`
    const importeStr = (cols[idx.importe] || '').trim().replace(/\./g, '').replace(',', '.')
    const importe = parseFloat(importeStr)
    if (!fecha || isNaN(importe)) continue
    out.push({
      fecha,
      importe,
      concepto: idx.concepto >= 0 ? (cols[idx.concepto] || '').trim() : '',
      referencia: idx.referencia >= 0 ? (cols[idx.referencia] || '').trim() : '',
    })
  }
  return out
}

const importarCsv = async (ev) => {
  const file = ev.target.files?.[0]; if (!file) return
  if (!cuentaSeleccionadaId.value) { error.value = 'Selecciona una cuenta antes'; return }
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    const texto = await file.text()
    const lineas = parseCsv(texto)
    if (!lineas.length) { error.value = 'No se han encontrado líneas válidas en el CSV.'; return }
    const data = await mutation(IMPORTAR_EXTRACTO_CSV, {
      cuentaId: cuentaSeleccionadaId.value,
      lineasJson: JSON.stringify(lineas),
    })
    info.value = `${data.importarExtractoCsv} líneas importadas desde CSV.`
    await cargarPendientes()
  } catch (e) {
    error.value = e.message || 'Error al importar CSV'
  } finally { ocupado.value = false; ev.target.value = '' }
}

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

onMounted(async () => {
  await Promise.all([cargarCuentas(), cargarFlagOpenBanking()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
</style>
