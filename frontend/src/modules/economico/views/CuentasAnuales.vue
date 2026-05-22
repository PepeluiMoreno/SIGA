<template>
  <AppLayout title="Cuentas Anuales" subtitle="Preparación, aprobación y depósito de las cuentas anuales del ejercicio">

    <!-- Generar -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4 flex items-end gap-3">
      <div>
        <label class="label">Ejercicio</label>
        <select v-model.number="ejercicioGen" class="input">
          <option v-for="y in anosDisponibles" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <button @click="generar" :disabled="ocupado" class="btn-primary text-sm">
        + Generar CCAA del ejercicio
      </button>
      <p class="text-xs text-slate-500 ml-auto">
        Requiere que el ejercicio esté cerrado contablemente (flujo 9).
      </p>
    </div>

    <ErrorAlert v-if="error" :message="error" />
    <p v-if="info" class="text-green-700 text-sm bg-green-50 p-3 rounded-lg mb-4">{{ info }}</p>

    <!-- Listado -->
    <div v-if="ccaaList.length" class="bg-white border border-slate-200 rounded-xl overflow-hidden mb-4">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Ejercicio</th>
            <th class="px-3 py-2 text-center">Estado</th>
            <th class="px-3 py-2 text-right">Excedente</th>
            <th class="px-3 py-2 text-center">F. aprobación</th>
            <th class="px-3 py-2 text-center">F. depósito</th>
            <th class="px-3 py-2 text-center w-8"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="c in ccaaList" :key="c.id"
              class="hover:bg-slate-50 cursor-pointer"
              :class="seleccionada?.id === c.id ? 'bg-indigo-50' : ''"
              @click="seleccionar(c)">
            <td class="px-3 py-2 font-medium">{{ c.ejercicio }}</td>
            <td class="px-3 py-2 text-center">
              <span :class="badgeEstado(c.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ c.estado }}
              </span>
            </td>
            <td class="px-3 py-2 text-right font-mono"
                :class="(c.excedente || 0) >= 0 ? 'text-green-700' : 'text-red-600'">
              {{ fmt(c.excedente) }}
            </td>
            <td class="px-3 py-2 text-center text-xs text-slate-500">{{ fechaFmt(c.fechaAprobacion) }}</td>
            <td class="px-3 py-2 text-center text-xs text-slate-500">{{ fechaFmt(c.fechaDeposito) }}</td>
            <td class="px-3 py-2 text-center text-slate-400">›</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="text-center text-slate-400 py-10 text-sm border border-dashed border-slate-200 rounded-xl mb-4">
      No hay Cuentas Anuales registradas. Genera las del ejercicio cerrado más reciente.
    </p>

    <!-- Detalle -->
    <div v-if="seleccionada" class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
        <h3 class="font-semibold text-sm text-slate-800">
          CCAA Ejercicio {{ seleccionada.ejercicio }}
          <span :class="badgeEstado(seleccionada.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5 ml-2">
            {{ seleccionada.estado }}
          </span>
        </h3>
        <button @click="seleccionada = null" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
      </div>

      <!-- Tabs -->
      <div class="border-b border-slate-100 px-4">
        <nav class="-mb-px flex space-x-4">
          <button v-for="t in pestanas" :key="t.id" @click="tabActiva = t.id"
            :class="[tabActiva === t.id ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-700',
                    'py-2 px-1 border-b-2 text-xs font-medium']">
            {{ t.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Resumen -->
      <div v-if="tabActiva === 'resumen'" class="p-4 text-sm">
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          <div><dt class="text-xs text-slate-500">Excedente</dt>
            <dd class="font-mono">{{ fmt(seleccionada.excedente) }}</dd></div>
          <div><dt class="text-xs text-slate-500">F. aprobación</dt>
            <dd>{{ fechaFmt(seleccionada.fechaAprobacion) }}</dd></div>
          <div v-if="seleccionada.actaReferencia"><dt class="text-xs text-slate-500">Acta</dt>
            <dd>{{ seleccionada.actaReferencia }}</dd></div>
          <div><dt class="text-xs text-slate-500">F. depósito</dt>
            <dd>{{ fechaFmt(seleccionada.fechaDeposito) }}</dd></div>
          <div v-if="seleccionada.archivoAcuseRecibo" class="col-span-2">
            <dt class="text-xs text-slate-500">Acuse de recibo</dt>
            <dd><a :href="seleccionada.archivoAcuseRecibo" target="_blank" class="text-indigo-600 hover:underline text-xs">{{ seleccionada.archivoAcuseRecibo }}</a></dd>
          </div>
        </dl>

        <div class="flex flex-wrap gap-2 pt-3 border-t border-slate-100">
          <button v-if="seleccionada.estado === 'BORRADOR'" @click="abrirAprobar" class="btn-primary text-xs">
            Aprobar (junta)
          </button>
          <button v-if="seleccionada.estado === 'APROBADAS'" @click="abrirDepositar" class="btn-primary text-xs">
            Marcar depositadas
          </button>
          <button v-if="seleccionada.estado !== 'BORRADOR'" @click="reabrir" :disabled="ocupado" class="btn-secondary text-xs">
            Reabrir
          </button>
          <button @click="exportarPdf" :disabled="ocupado" class="btn-secondary text-xs ml-auto">↓ PDF</button>
        </div>
      </div>

      <!-- Tab Balance -->
      <div v-if="tabActiva === 'balance'" class="p-4 text-sm overflow-x-auto">
        <pre class="text-xs bg-slate-50 p-3 rounded">{{ JSON.stringify(seleccionada.balancePcesfl, null, 2) }}</pre>
      </div>

      <!-- Tab Cuenta de Resultados -->
      <div v-if="tabActiva === 'resultados'" class="p-4 text-sm overflow-x-auto">
        <pre class="text-xs bg-slate-50 p-3 rounded">{{ JSON.stringify(seleccionada.cuentaResultados, null, 2) }}</pre>
      </div>

      <!-- Tab Memoria -->
      <div v-if="tabActiva === 'memoria'" class="p-4 text-sm space-y-3">
        <details v-for="(apartado, i) in apartadosMemoria" :key="apartado.clave"
                 :open="i === 0" class="border border-slate-200 rounded-lg">
          <summary class="px-3 py-2 cursor-pointer text-sm font-medium text-slate-800 hover:bg-slate-50">
            {{ i + 1 }}. {{ apartado.label }}
          </summary>
          <div class="p-3 border-t border-slate-100">
            <textarea
              v-model="memoriaLocal[apartado.clave]"
              :disabled="seleccionada.estado !== 'BORRADOR'"
              class="input h-32 text-xs font-mono"
              :placeholder="apartado.guia"
            />
            <div v-if="seleccionada.estado === 'BORRADOR'" class="mt-2 flex justify-end">
              <button @click="guardarApartado(apartado.clave)" :disabled="ocupado" class="btn-secondary text-xs">
                Guardar apartado
              </button>
            </div>
          </div>
        </details>
      </div>
    </div>

    <!-- Modal Aprobar -->
    <div v-if="modalAprobar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalAprobar = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Aprobar Cuentas Anuales</h3>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm">
          <div>
            <label class="label">Aprobado por (presidente/vicepresidente) *</label>
            <select v-model="formApr.aprobadoPorId" class="input">
              <option :value="null">— Selecciona miembro —</option>
              <option v-for="m in miembros" :key="m.id" :value="m.id">{{ miembroNombre(m) }}</option>
            </select>
          </div>
          <div>
            <label class="label">Referencia del acta *</label>
            <input v-model="formApr.actaReferencia" class="input"
                   placeholder="Acta de junta directiva 2026/03 de 28/06/2026" />
          </div>
          <div>
            <label class="label">Fecha de aprobación</label>
            <input type="date" v-model="formApr.fechaAprobacion" class="input" />
          </div>
          <ErrorAlert v-if="formApr.error" :message="formApr.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalAprobar = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="confirmarAprobar" :disabled="ocupado" class="btn-primary text-sm">Aprobar</button>
        </div>
      </div>
    </div>

    <!-- Modal Depositar -->
    <div v-if="modalDepositar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalDepositar = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Marcar como depositadas</h3>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm">
          <div>
            <label class="label">Fecha de depósito *</label>
            <input type="date" v-model="formDep.fechaDeposito" class="input" />
          </div>
          <div>
            <label class="label">URL / referencia del acuse de recibo</label>
            <input v-model="formDep.archivoAcuseRecibo" class="input"
                   placeholder="URL del PDF firmado por el registro (opcional)" />
          </div>
          <ErrorAlert v-if="formDep.error" :message="formDep.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalDepositar = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="confirmarDepositar" :disabled="ocupado" class="btn-primary text-sm">Confirmar</button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_CUENTAS_ANUALES,
  GENERAR_CCAA,
  ACTUALIZAR_MEMORIA_CCAA,
  APROBAR_CCAA,
  MARCAR_CCAA_DEPOSITADAS,
  REABRIR_CCAA,
  EXPORTAR_CCAA_PDF,
  GET_MIEMBROS_PARA_GASTO,
} from '@/graphql/queries/economico'

const toast = useToast()

const { query, mutation } = useGraphQL()

const ccaaList = ref([])
const miembros = ref([])
const seleccionada = ref(null)
const tabActiva = ref('resumen')
const memoriaLocal = ref({})
const ejercicioGen = ref(new Date().getFullYear() - 1)
const error = ref('')
const info = ref('')
const ocupado = ref(false)

const modalAprobar = ref(false)
const modalDepositar = ref(false)
const formApr = ref({ aprobadoPorId: null, actaReferencia: '', fechaAprobacion: '', error: '' })
const formDep = ref({ fechaDeposito: '', archivoAcuseRecibo: '', error: '' })

const anosDisponibles = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y - 2, y - 3, y - 4, y - 5]
})

const pestanas = [
  { id: 'resumen',    label: 'Resumen' },
  { id: 'balance',    label: 'Balance PCESFL' },
  { id: 'resultados', label: 'Cuenta de Resultados' },
  { id: 'memoria',    label: 'Memoria (12 apartados)' },
]

const apartadosMemoria = [
  { clave: 'apartado_1',  label: 'Actividad de la entidad',
    guia: 'Resumen de la actividad propia, fines fundacionales, ámbito territorial, beneficiarios.' },
  { clave: 'apartado_2',  label: 'Bases de presentación de las cuentas anuales',
    guia: 'Imagen fiel, principios contables, comparabilidad, agrupación de partidas.' },
  { clave: 'apartado_3',  label: 'Excedente del ejercicio',
    guia: 'Análisis del excedente, propuesta de aplicación, comparativa con el ejercicio anterior.' },
  { clave: 'apartado_4',  label: 'Normas de registro y valoración',
    guia: 'Criterios contables aplicados (inmovilizado, existencias, ingresos, gastos, subvenciones…).' },
  { clave: 'apartado_5',  label: 'Inmovilizado material, intangible e inversiones inmobiliarias',
    guia: 'Movimientos del ejercicio: altas, bajas, amortizaciones, deterioro.' },
  { clave: 'apartado_6',  label: 'Usuarios y otros deudores de la actividad propia',
    guia: 'Cuentas 430-439: saldos, vencimientos, dotaciones por deterioro.' },
  { clave: 'apartado_7',  label: 'Beneficiarios-acreedores',
    guia: 'Cuentas 412 y 419: deudas con beneficiarios, vencimientos.' },
  { clave: 'apartado_8',  label: 'Activos y pasivos financieros',
    guia: 'Categorías, vencimientos, riesgos (crédito, liquidez, tipo de cambio).' },
  { clave: 'apartado_9',  label: 'Fondos propios',
    guia: 'Dotación fundacional, reservas, excedentes acumulados. Variaciones del ejercicio.' },
  { clave: 'apartado_10', label: 'Situación fiscal',
    guia: 'Régimen fiscal aplicable (Ley 49/2002 o no), conciliación, impuestos pendientes.' },
  { clave: 'apartado_11', label: 'Subvenciones, donaciones y legados',
    guia: 'Detalle por aportante, finalidad, importes recibidos y aplicados, saldos en patrimonio neto.' },
  { clave: 'apartado_12', label: 'Aplicación de elementos patrimoniales a fines propios',
    guia: 'Cumplimiento del 70% de los ingresos a fines fundacionales (Ley 50/2002 art. 27).' },
]

const cargar = async () => {
  error.value = ''
  try {
    const data = await query(GET_CUENTAS_ANUALES)
    ccaaList.value = (data.cuentasAnuales || []).slice().sort((a, b) => b.ejercicio - a.ejercicio)
  } catch (e) {
    error.value = e.message || 'Error al cargar las CCAA'
  }
}

const cargarMiembros = async () => {
  try {
    const data = await query(GET_MIEMBROS_PARA_GASTO)
    miembros.value = data.miembros || []
  } catch (e) { console.error(e) }
}

const seleccionar = (c) => {
  seleccionada.value = seleccionada.value?.id === c.id ? null : c
  memoriaLocal.value = { ...(c?.memoria || {}) }
  tabActiva.value = 'resumen'
}

const generar = async () => {
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    await mutation(GENERAR_CCAA, { ejercicio: ejercicioGen.value })
    info.value = `Cuentas Anuales del ejercicio ${ejercicioGen.value} generadas en BORRADOR.`
    await cargar()
  } catch (e) { error.value = e.message || 'Error al generar' } finally { ocupado.value = false }
}

const guardarApartado = async (apartado) => {
  ocupado.value = true; error.value = ''; info.value = ''
  try {
    await mutation(ACTUALIZAR_MEMORIA_CCAA, {
      ccaaId: seleccionada.value.id,
      apartado,
      texto: memoriaLocal.value[apartado] || '',
    })
    toast.success('Apartado guardado')
    await cargar()
    const actualizada = ccaaList.value.find(c => c.id === seleccionada.value.id)
    if (actualizada) { seleccionada.value = actualizada }
  } catch (e) { error.value = e.message || 'Error al guardar' } finally { ocupado.value = false }
}

const abrirAprobar = () => {
  formApr.value = {
    aprobadoPorId: null,
    actaReferencia: '',
    fechaAprobacion: new Date().toISOString().split('T')[0],
    error: '',
  }
  modalAprobar.value = true
}

const confirmarAprobar = async () => {
  formApr.value.error = ''
  if (!formApr.value.aprobadoPorId) { formApr.value.error = 'Selecciona quién aprueba'; return }
  if (!formApr.value.actaReferencia) { formApr.value.error = 'Indica la referencia del acta'; return }
  ocupado.value = true
  try {
    await mutation(APROBAR_CCAA, {
      ccaaId: seleccionada.value.id,
      aprobadoPorId: formApr.value.aprobadoPorId,
      actaReferencia: formApr.value.actaReferencia,
      fechaAprobacion: formApr.value.fechaAprobacion || null,
    })
    modalAprobar.value = false
    info.value = 'CCAA aprobadas.'
    await cargar()
    seleccionada.value = ccaaList.value.find(c => c.id === seleccionada.value.id) || null
  } catch (e) { formApr.value.error = e.message || 'Error al aprobar' } finally { ocupado.value = false }
}

const abrirDepositar = () => {
  formDep.value = {
    fechaDeposito: new Date().toISOString().split('T')[0],
    archivoAcuseRecibo: '',
    error: '',
  }
  modalDepositar.value = true
}

const confirmarDepositar = async () => {
  formDep.value.error = ''
  if (!formDep.value.fechaDeposito) { formDep.value.error = 'Indica la fecha de depósito'; return }
  ocupado.value = true
  try {
    await mutation(MARCAR_CCAA_DEPOSITADAS, {
      ccaaId: seleccionada.value.id,
      fechaDeposito: formDep.value.fechaDeposito,
      archivoAcuseRecibo: formDep.value.archivoAcuseRecibo || null,
    })
    modalDepositar.value = false
    info.value = 'CCAA marcadas como depositadas.'
    await cargar()
    seleccionada.value = ccaaList.value.find(c => c.id === seleccionada.value.id) || null
  } catch (e) { formDep.value.error = e.message || 'Error al depositar' } finally { ocupado.value = false }
}

const reabrir = async () => {
  const motivo = prompt(`Reabrir CCAA ${seleccionada.value.ejercicio}? Indica el motivo:`)
  if (!motivo) return
  ocupado.value = true
  try {
    await mutation(REABRIR_CCAA, { ccaaId: seleccionada.value.id, motivo })
    info.value = 'CCAA reabiertas en estado BORRADOR.'
    await cargar()
    seleccionada.value = ccaaList.value.find(c => c.id === seleccionada.value.id) || null
  } catch (e) { error.value = e.message || 'Error al reabrir' } finally { ocupado.value = false }
}

const exportarPdf = async () => {
  if (!seleccionada.value) return
  ocupado.value = true; error.value = ''
  try {
    const data = await mutation(EXPORTAR_CCAA_PDF, {
      ccaaId: seleccionada.value.id,
      organizacionNombre: 'Asociación SIGA',
    })
    const b64 = data.exportarCcaaPdf
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ccaa-${seleccionada.value.ejercicio}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message || 'Error al generar el PDF'
  } finally { ocupado.value = false }
}

const miembroNombre = (m) => `${m?.nombre || ''} ${m?.apellido1 || ''} ${m?.apellido2 || ''}`.trim() || '—'
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

const badgeEstado = (e) => ({
  BORRADOR:    'bg-amber-100 text-amber-700',
  APROBADAS:   'bg-blue-100 text-blue-700',
  DEPOSITADAS: 'bg-green-100 text-green-700',
}[e] || 'bg-slate-100 text-slate-500')

onMounted(async () => {
  await Promise.all([cargar(), cargarMiembros()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500; }
</style>
