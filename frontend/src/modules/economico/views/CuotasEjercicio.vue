<template>
  <!-- Pantalla 5.1 + 5.4 — Configuración y generación de cuotas del ejercicio -->
  <AppLayout title="Cuotas del ejercicio" subtitle="Configurar importes y generar las cuotas anuales de los socios">

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">

      <!-- Panel izquierdo: configurar -->
      <div class="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 self-start">
        <h3 class="font-semibold text-slate-800 mb-3">Configuración del ejercicio</h3>

        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Ejercicio *</label>
              <select v-model.number="ejercicio" class="input" @change="cargarConfig">
                <option v-for="y in ejercicios" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div>
              <label class="label">Estado</label>
              <div class="input bg-slate-50 flex items-center text-sm text-slate-600">
                {{ config ? 'Configurado' : 'Sin configurar' }}
              </div>
            </div>
          </div>

          <div>
            <label class="label">Importe base *</label>
            <div class="relative">
              <input v-model.number="importeBase" type="number" min="0" step="0.01" class="input pr-8" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">€</span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">Cuota anual del socio que no tiene reducciones.</p>
          </div>

          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="observaciones" class="input h-16" placeholder="Opcional…" />
          </div>

          <div v-if="ejercicios.length > 1 && !config" class="bg-indigo-50 border border-indigo-100 rounded p-2 text-xs text-indigo-700">
            Tip: pulsa "Clonar del anterior" para tomar el importe de {{ ejercicio - 1 }}.
          </div>

          <p v-if="errorConfig" class="text-red-600 text-sm">{{ errorConfig }}</p>

          <div class="flex gap-2 pt-1">
            <button @click="clonarAnterior" class="btn-secondary text-sm flex-1" :disabled="guardando">
              Clonar del anterior
            </button>
            <button @click="guardarConfig" class="btn-primary text-sm flex-1" :disabled="guardando || !importeBase">
              {{ guardando ? 'Guardando…' : 'Guardar configuración' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Panel derecho: previsualizar + generar -->
      <div class="lg:col-span-3 bg-white border border-slate-200 rounded-xl p-5 self-start">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-slate-800">Generación de cuotas individuales</h3>
          <button @click="previsualizar" class="btn-secondary text-sm" :disabled="!config || calculando">
            {{ calculando ? 'Calculando…' : '↻ Previsualizar' }}
          </button>
        </div>

        <p v-if="!config" class="text-sm text-slate-400 py-6 text-center">
          Configura primero el importe base del ejercicio.
        </p>

        <template v-else-if="preview">
          <div class="grid grid-cols-4 gap-2 mb-3">
            <div class="bg-slate-50 rounded p-2 text-center">
              <div class="text-xs text-slate-500">Generables</div>
              <div class="text-lg font-bold text-indigo-600">{{ preview.nGenerables }}</div>
            </div>
            <div class="bg-slate-50 rounded p-2 text-center">
              <div class="text-xs text-slate-500">Excluidos</div>
              <div class="text-lg font-bold text-amber-600">{{ preview.nExcluidos }}</div>
            </div>
            <div class="bg-slate-50 rounded p-2 text-center">
              <div class="text-xs text-slate-500">Ya existen</div>
              <div class="text-lg font-bold text-green-600">{{ preview.nExistentes }}</div>
            </div>
            <div class="bg-slate-50 rounded p-2 text-center">
              <div class="text-xs text-slate-500">Total esperado</div>
              <div class="text-lg font-bold text-slate-800">{{ fmt(preview.totalEsperado) }}</div>
            </div>
          </div>

          <div class="border border-slate-200 rounded-lg overflow-hidden">
            <table class="w-full text-sm">
              <thead class="bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-3 py-2 text-left">Tipo de miembro</th>
                  <th class="px-3 py-2 text-left">Motivo reducción</th>
                  <th class="px-3 py-2 text-right">Miembros</th>
                  <th class="px-3 py-2 text-right">Unitario</th>
                  <th class="px-3 py-2 text-right">Total</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="d in preview.desglose" :key="d.tipoMiembroId" :class="d.excluido ? 'bg-amber-50' : ''">
                  <td class="px-3 py-1.5">{{ d.tipoMiembroNombre }}</td>
                  <td class="px-3 py-1.5">
                    <span v-if="d.motivoCodigo" class="text-xs font-mono">
                      {{ d.motivoCodigo }} (-{{ d.motivoPorcentaje }}%)
                    </span>
                    <span v-else class="text-xs text-slate-400">—</span>
                  </td>
                  <td class="px-3 py-1.5 text-right">{{ d.nMiembros }}</td>
                  <td class="px-3 py-1.5 text-right font-mono">
                    <span v-if="d.excluido" class="text-amber-700">excluido</span>
                    <span v-else>{{ fmt(d.importeUnitario) }}</span>
                  </td>
                  <td class="px-3 py-1.5 text-right font-mono">{{ fmt(d.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-3 flex items-end gap-3">
            <div class="flex-1">
              <label class="label">Fecha de vencimiento sugerida</label>
              <input v-model="fechaVencimiento" type="date" class="input" />
            </div>
            <button
              @click="generar"
              :disabled="generando || preview.nGenerables === 0"
              class="btn-primary"
            >
              {{ generando ? 'Generando…' : `Generar ${preview.nGenerables} cuotas` }}
            </button>
          </div>

          <div v-if="preview.nExistentes > 0" class="text-xs text-slate-500 mt-2">
            ⓘ {{ preview.nExistentes }} cuotas ya existen para este ejercicio — se omitirán (idempotente).
          </div>
        </template>

        <p v-else class="text-sm text-slate-400 py-6 text-center">
          Pulsa "Previsualizar" para ver el desglose por tipo de miembro.
        </p>

        <div v-if="resultadoGeneracion" class="mt-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <p class="font-medium text-green-800 text-sm">✓ Generación completada</p>
          <ul class="text-xs text-green-700 mt-1 space-y-0.5">
            <li>Creadas: <strong>{{ resultadoGeneracion.nCreadas }}</strong></li>
            <li>Omitidas (ya existían): <strong>{{ resultadoGeneracion.nOmitidasExistentes }}</strong></li>
            <li>Omitidas (tipos excluidos): <strong>{{ resultadoGeneracion.nOmitidasExcluidas }}</strong></li>
            <li>Importe total: <strong>{{ fmt(resultadoGeneracion.totalImporte) }}</strong></li>
          </ul>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_CONFIG_CUOTA_EJERCICIO,
  CONFIGURAR_CUOTA_EJERCICIO,
  PREVISUALIZAR_GENERACION_CUOTAS,
  GENERAR_CUOTAS_INDIVIDUALES,
} from '@/graphql/queries/financiero'

const { query, mutation } = useGraphQL()

const anoActual = new Date().getFullYear()
const ejercicios = [anoActual - 1, anoActual, anoActual + 1]
const ejercicio = ref(anoActual)
const importeBase = ref(0)
const observaciones = ref('')
const config = ref(null)
const preview = ref(null)
const resultadoGeneracion = ref(null)
const fechaVencimiento = ref('')

const guardando = ref(false)
const calculando = ref(false)
const generando = ref(false)
const errorConfig = ref('')

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)

const cargarConfig = async () => {
  errorConfig.value = ''
  preview.value = null
  resultadoGeneracion.value = null
  const data = await query(GET_CONFIG_CUOTA_EJERCICIO, { ejercicio: ejercicio.value })
  const cfg = (data.importesCuotaAnio || [])[0]
  if (cfg) {
    config.value = cfg
    importeBase.value = parseFloat(cfg.importe)
    observaciones.value = cfg.observaciones || ''
  } else {
    config.value = null
    importeBase.value = 0
    observaciones.value = ''
  }
}

const clonarAnterior = async () => {
  const previo = ejercicio.value - 1
  const data = await query(GET_CONFIG_CUOTA_EJERCICIO, { ejercicio: previo })
  const cfg = (data.importesCuotaAnio || [])[0]
  if (cfg) {
    importeBase.value = parseFloat(cfg.importe)
  } else {
    errorConfig.value = `No hay configuración del ejercicio ${previo} para clonar`
  }
}

const guardarConfig = async () => {
  errorConfig.value = ''
  guardando.value = true
  try {
    await mutation(CONFIGURAR_CUOTA_EJERCICIO, {
      ejercicio: ejercicio.value,
      importeBase: parseFloat(importeBase.value),
      observaciones: observaciones.value || null,
    })
    await cargarConfig()
  } catch (e) {
    errorConfig.value = e.message || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

const previsualizar = async () => {
  calculando.value = true
  resultadoGeneracion.value = null
  try {
    const data = await mutation(PREVISUALIZAR_GENERACION_CUOTAS, { ejercicio: ejercicio.value })
    preview.value = data.previsualizarGeneracionCuotas
  } catch (e) {
    alert(e.message || 'Error al previsualizar')
  } finally {
    calculando.value = false
  }
}

const generar = async () => {
  if (!confirm(`¿Generar ${preview.value.nGenerables} cuotas individuales para el ejercicio ${ejercicio.value}?`)) return
  generando.value = true
  try {
    const data = await mutation(GENERAR_CUOTAS_INDIVIDUALES, {
      ejercicio: ejercicio.value,
      fechaVencimiento: fechaVencimiento.value || null,
    })
    resultadoGeneracion.value = data.generarCuotasIndividuales
    await previsualizar()
  } catch (e) {
    alert(e.message || 'Error al generar')
  } finally {
    generando.value = false
  }
}

onMounted(cargarConfig)
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.label { @apply block text-sm font-medium text-slate-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
</style>
