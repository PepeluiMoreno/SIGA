<template>
  <AppLayout title="Modelo 182" subtitle="Declaración fiscal anual de donaciones (AEAT)">

    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4 flex flex-wrap items-end gap-3">
      <div>
        <label class="label">Ejercicio</label>
        <select v-model.number="ejercicio" @change="cargarAgregado" class="input">
          <option v-for="y in anosDisponibles" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <button @click="cargarAgregado" :disabled="ocupado" class="btn-secondary text-sm">
        Recalcular
      </button>
      <p class="text-xs text-slate-500 ml-auto">
        Plazo de presentación: enero del año siguiente al ejercicio.
      </p>
    </div>

    <ErrorAlert v-if="error" :message="error" />
    <p v-if="info" class="text-green-700 text-sm bg-green-50 p-3 rounded-lg mb-4">{{ info }}</p>

    <!-- Resumen -->
    <div v-if="agregado" class="bg-white border border-slate-200 rounded-xl p-4 mb-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
        <div>
          <p class="text-xs text-slate-500">Donantes incluibles</p>
          <p class="text-2xl font-bold text-green-700">{{ agregado.nIncluidos }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-500">Donaciones excluidas</p>
          <p class="text-2xl font-bold text-amber-700">{{ agregado.nExcluidos }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-500">Importe total declarable</p>
          <p class="text-2xl font-bold text-slate-800 font-mono">{{ fmt(agregado.importeTotal) }}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-2 mt-4 pt-3 border-t border-slate-100">
        <button @click="descargarTxt" :disabled="ocupado || !agregado.nIncluidos" class="btn-primary text-sm">
          ↓ Fichero AEAT (TXT)
        </button>
        <button @click="descargarPdf" :disabled="ocupado" class="btn-secondary text-sm">
          ↓ PDF resumen
        </button>
        <button @click="abrirRegistrar" :disabled="!agregado.nIncluidos || presentacionExistente" class="btn-primary text-sm ml-auto">
          {{ presentacionExistente ? 'Ya presentado' : 'Registrar presentación' }}
        </button>
      </div>
    </div>

    <!-- Donantes incluidos -->
    <div v-if="agregado && agregado.incluidos.length" class="bg-white border border-slate-200 rounded-xl overflow-hidden mb-4">
      <div class="px-4 py-3 bg-slate-50 border-b border-slate-100">
        <h3 class="font-semibold text-sm text-slate-800">Donantes incluidos en el Modelo 182</h3>
      </div>
      <div class="overflow-x-auto -mx-1"><table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">NIF</th>
            <th class="px-3 py-2 text-left">Nombre</th>
            <th class="px-3 py-2 text-center">Tipo</th>
            <th class="px-3 py-2 text-center">Clave</th>
            <th class="px-3 py-2 text-right">Donaciones</th>
            <th class="px-3 py-2 text-right">Importe</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="d in agregado.incluidos" :key="d.nif + ':' + (d.clave || 'A')" class="hover:bg-slate-50">
            <td class="px-3 py-1.5 font-mono text-xs">{{ d.nif }}</td>
            <td class="px-3 py-1.5 truncate max-w-xs">{{ d.nombre }}</td>
            <td class="px-3 py-1.5 text-center">
              <span class="text-[10px] uppercase rounded px-1.5 py-0.5"
                    :class="d.tipo === 1 ? 'bg-blue-100 text-blue-700' : 'bg-indigo-100 text-indigo-700'">
                {{ d.tipo === 1 ? 'PF' : 'PJ' }}
              </span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span class="text-[10px] uppercase rounded px-1.5 py-0.5"
                    :class="d.clave === 'B' ? 'bg-sky-100 text-sky-700' : 'bg-emerald-100 text-emerald-700'"
                    :title="d.clave === 'B' ? 'B · En especie' : 'A · Dineraria'">
                {{ d.clave || 'A' }}
              </span>
            </td>
            <td class="px-3 py-1.5 text-right">{{ d.nDonaciones }}</td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(d.importe) }}</td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- Excluidos -->
    <div v-if="agregado && agregado.excluidos.length" class="bg-white border border-amber-200 rounded-xl overflow-hidden mb-4">
      <div class="px-4 py-3 bg-amber-50 border-b border-amber-100">
        <h3 class="font-semibold text-sm text-amber-800">
          {{ agregado.excluidos.length }} donaciones excluidas
        </h3>
        <p class="text-xs text-amber-700 mt-0.5">
          Revisa si puedes completar el NIF del donante para incluirlas.
        </p>
      </div>
      <div class="overflow-x-auto -mx-1"><table class="w-full text-xs">
        <thead class="bg-amber-50 text-amber-700 text-[10px] uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Fecha</th>
            <th class="px-3 py-2 text-right">Importe</th>
            <th class="px-3 py-2 text-left">Motivo</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-amber-100">
          <tr v-for="(x, i) in agregado.excluidos" :key="i">
            <td class="px-3 py-1.5">{{ fechaFmt(x.fecha) }}</td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(x.importe) }}</td>
            <td class="px-3 py-1.5 text-slate-600">{{ x.motivo }}</td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- Histórico de presentaciones -->
    <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div class="px-4 py-3 bg-slate-50 border-b border-slate-100">
        <h3 class="font-semibold text-sm text-slate-800">Histórico de presentaciones a la AEAT</h3>
      </div>
      <div class="overflow-x-auto -mx-1"><table v-if="presentaciones.length" class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Ejercicio</th>
            <th class="px-3 py-2 text-left">F. envío</th>
            <th class="px-3 py-2 text-left">Código AEAT</th>
            <th class="px-3 py-2 text-right">Donantes</th>
            <th class="px-3 py-2 text-right">Total</th>
            <th class="px-3 py-2 text-left">Acuse</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="p in presentaciones" :key="p.id" class="hover:bg-slate-50">
            <td class="px-3 py-1.5 font-medium">{{ p.ejercicio }}</td>
            <td class="px-3 py-1.5">{{ fechaFmt(p.fechaEnvio) }}</td>
            <td class="px-3 py-1.5 font-mono text-xs">{{ p.codigoAeat || '—' }}</td>
            <td class="px-3 py-1.5 text-right">{{ p.nDonantes }}</td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(p.importeTotal) }}</td>
            <td class="px-3 py-1.5 text-xs">
              <a v-if="p.archivoAcuse" :href="p.archivoAcuse" target="_blank" class="text-indigo-600 hover:underline">ver PDF</a>
              <span v-else class="text-slate-400">—</span>
            </td>
          </tr>
        </tbody>
      </table></div>
      <p v-else class="text-center text-slate-400 py-8 text-sm">No hay presentaciones registradas todavía.</p>
    </div>

    <!-- Modal registrar presentación -->
    <div v-if="modalRegistrar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalRegistrar = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Registrar presentación AEAT — Ejercicio {{ ejercicio }}</h3>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm">
          <div>
            <label class="label">Fecha de envío *</label>
            <input type="date" v-model="formReg.fechaEnvio" class="input" />
          </div>
          <div>
            <label class="label">Código AEAT (acuse)</label>
            <input v-model="formReg.codigoAeat" class="input" placeholder="AEAT-XXXXXXX..." />
          </div>
          <div>
            <label class="label">URL del acuse de recibo (PDF)</label>
            <input v-model="formReg.archivoAcuse" class="input" placeholder="Opcional: URL al PDF del justificante" />
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formReg.observaciones" class="input h-16" />
          </div>
          <ErrorAlert v-if="formReg.error" :message="formReg.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalRegistrar = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="confirmarRegistrar" :disabled="ocupado" class="btn-primary text-sm">Registrar</button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_AGREGADO_182,
  GET_PRESENTACIONES_182,
  DESCARGAR_FICHERO_AEAT_182,
  DESCARGAR_PDF_RESUMEN_182,
  REGISTRAR_PRESENTACION_182,
} from '@/graphql/queries/economico'

const { query, mutation } = useGraphQL()

const ejercicio = ref(new Date().getFullYear() - 1)
const agregado = ref(null)
const presentaciones = ref([])
const error = ref('')
const info = ref('')
const ocupado = ref(false)

const modalRegistrar = ref(false)
const formReg = ref({ fechaEnvio: '', codigoAeat: '', archivoAcuse: '', observaciones: '', error: '' })

// Datos del declarante (entidad) — provisionalmente fijos; idealmente leerlos de Parámetros Generales
const declaranteNif = 'G12345678'
const declaranteNombre = 'Asociación SIGA'

const anosDisponibles = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y - 2, y - 3, y - 4]
})

const presentacionExistente = computed(() =>
  presentaciones.value.some(p => p.ejercicio === ejercicio.value)
)

const cargarAgregado = async () => {
  error.value = ''; info.value = ''
  ocupado.value = true
  try {
    const data = await query(GET_AGREGADO_182, { ejercicio: ejercicio.value })
    agregado.value = data.agregadoModelo182
  } catch (e) { error.value = e.message || 'Error al calcular el agregado' } finally { ocupado.value = false }
}

const cargarPresentaciones = async () => {
  try {
    const data = await query(GET_PRESENTACIONES_182)
    presentaciones.value = data.presentacionesModelo182 || []
  } catch (e) { console.error(e) }
}

const descargarTxt = async () => {
  ocupado.value = true; error.value = ''
  try {
    const data = await mutation(DESCARGAR_FICHERO_AEAT_182, {
      ejercicio: ejercicio.value,
      declaranteNif,
      declaranteNombre,
    })
    const b64 = data.descargarFicheroAeat182
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'text/plain;charset=iso-8859-1' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `modelo-182-${ejercicio.value}.txt`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) { error.value = e.message || 'Error al generar el TXT' } finally { ocupado.value = false }
}

const descargarPdf = async () => {
  ocupado.value = true; error.value = ''
  try {
    const data = await mutation(DESCARGAR_PDF_RESUMEN_182, {
      ejercicio: ejercicio.value,
      organizacionNombre: declaranteNombre,
    })
    const b64 = data.descargarPdfResumen182
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `modelo-182-${ejercicio.value}-resumen.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) { error.value = e.message || 'Error al generar el PDF' } finally { ocupado.value = false }
}

const abrirRegistrar = () => {
  formReg.value = {
    fechaEnvio: new Date().toISOString().split('T')[0],
    codigoAeat: '',
    archivoAcuse: '',
    observaciones: '',
    error: '',
  }
  modalRegistrar.value = true
}

const confirmarRegistrar = async () => {
  formReg.value.error = ''
  if (!formReg.value.fechaEnvio) { formReg.value.error = 'Indica la fecha de envío'; return }
  ocupado.value = true
  try {
    await mutation(REGISTRAR_PRESENTACION_182, {
      ejercicio: ejercicio.value,
      fechaEnvio: formReg.value.fechaEnvio,
      codigoAeat: formReg.value.codigoAeat || null,
      archivoAcuse: formReg.value.archivoAcuse || null,
      observaciones: formReg.value.observaciones || null,
    })
    modalRegistrar.value = false
    info.value = `Presentación del ejercicio ${ejercicio.value} registrada.`
    await cargarPresentaciones()
  } catch (e) { formReg.value.error = e.message || 'Error al registrar' } finally { ocupado.value = false }
}

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

onMounted(async () => {
  await Promise.all([cargarAgregado(), cargarPresentaciones()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-sm font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
</style>
