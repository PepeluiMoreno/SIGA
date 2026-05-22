<template>
  <AppLayout title="Evolución presupuestaria"
    subtitle="Previsto frente a ejecutado, ejercicio por ejercicio">

    <div v-if="cargando" class="text-center text-slate-400 text-sm py-10">Cargando…</div>

    <div v-else-if="!filas.length"
      class="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400 text-sm">
      No hay presupuestos registrados todavía.
    </div>

    <template v-else>
      <!-- Tabla comparativa multi-ejercicio -->
      <div class="bg-white rounded-xl border border-slate-200 overflow-hidden mb-6">
        <div class="overflow-x-auto -mx-1"><table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 text-slate-600">
              <th rowspan="2" class="px-4 py-2 text-left align-bottom">Ejercicio</th>
              <th colspan="2" class="px-4 py-2 text-center border-l border-slate-200">Ingresos</th>
              <th colspan="2" class="px-4 py-2 text-center border-l border-slate-200">Gastos</th>
              <th colspan="2" class="px-4 py-2 text-center border-l border-slate-200">Resultado</th>
              <th rowspan="2" class="px-4 py-2 text-center align-bottom border-l border-slate-200">% ejec. gasto</th>
            </tr>
            <tr class="bg-slate-50 text-xs text-slate-500">
              <th class="px-4 py-1.5 text-right border-l border-slate-200">Previsto</th>
              <th class="px-4 py-1.5 text-right">Ejecutado</th>
              <th class="px-4 py-1.5 text-right border-l border-slate-200">Previsto</th>
              <th class="px-4 py-1.5 text-right">Ejecutado</th>
              <th class="px-4 py-1.5 text-right border-l border-slate-200">Previsto</th>
              <th class="px-4 py-1.5 text-right">Ejecutado</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="f in filas" :key="f.ejercicio" class="hover:bg-slate-50">
              <td class="px-4 py-2 font-semibold text-slate-800">{{ f.ejercicio }}</td>
              <td class="px-4 py-2 text-right text-slate-500 border-l border-slate-100">{{ eur(f.ingresosPrevistos) }}</td>
              <td class="px-4 py-2 text-right font-medium text-green-700">{{ eur(f.ingresosEjecutados) }}</td>
              <td class="px-4 py-2 text-right text-slate-500 border-l border-slate-100">{{ eur(f.gastosPrevistos) }}</td>
              <td class="px-4 py-2 text-right font-medium text-red-700">{{ eur(f.gastosEjecutados) }}</td>
              <td class="px-4 py-2 text-right text-slate-500 border-l border-slate-100">{{ eur(f.resultadoPrevisto) }}</td>
              <td class="px-4 py-2 text-right font-medium"
                :class="f.resultadoEjecutado >= 0 ? 'text-blue-700' : 'text-amber-700'">
                {{ eur(f.resultadoEjecutado) }}
              </td>
              <td class="px-4 py-2 text-center border-l border-slate-100">
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="f.gradoEjecucionGastos > 100 ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'">
                  {{ f.gradoEjecucionGastos }}%
                </span>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="filas.length > 1">
            <tr class="bg-slate-50 font-semibold text-slate-700 border-t-2 border-slate-200">
              <td class="px-4 py-2">Acumulado</td>
              <td class="px-4 py-2 text-right border-l border-slate-200">{{ eur(tot.ingP) }}</td>
              <td class="px-4 py-2 text-right text-green-700">{{ eur(tot.ingE) }}</td>
              <td class="px-4 py-2 text-right border-l border-slate-200">{{ eur(tot.gasP) }}</td>
              <td class="px-4 py-2 text-right text-red-700">{{ eur(tot.gasE) }}</td>
              <td class="px-4 py-2 text-right border-l border-slate-200">{{ eur(tot.ingP - tot.gasP) }}</td>
              <td class="px-4 py-2 text-right" :class="(tot.ingE - tot.gasE) >= 0 ? 'text-blue-700' : 'text-amber-700'">
                {{ eur(tot.ingE - tot.gasE) }}
              </td>
              <td class="px-4 py-2"></td>
            </tr>
          </tfoot>
        </table></div>
      </div>

      <!-- Barras comparativas por ejercicio -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h3 class="text-sm font-semibold text-slate-800 mb-4">Ingresos y gastos ejecutados por ejercicio</h3>
        <div class="space-y-4">
          <div v-for="f in filas" :key="f.ejercicio">
            <div class="flex justify-between text-xs text-slate-500 mb-1">
              <span class="font-medium text-slate-700">{{ f.ejercicio }}</span>
              <span>Saldo: {{ eur(f.resultadoEjecutado) }}</span>
            </div>
            <div class="flex gap-1 items-center">
              <div class="h-4 bg-green-500 rounded-l" :style="{ width: barra(f.ingresosEjecutados) }"
                :title="`Ingresos: ${eur(f.ingresosEjecutados)}`"></div>
              <span class="text-xs text-slate-400 w-24">{{ eur(f.ingresosEjecutados) }}</span>
            </div>
            <div class="flex gap-1 items-center mt-0.5">
              <div class="h-4 bg-red-400 rounded-l" :style="{ width: barra(f.gastosEjecutados) }"
                :title="`Gastos: ${eur(f.gastosEjecutados)}`"></div>
              <span class="text-xs text-slate-400 w-24">{{ eur(f.gastosEjecutados) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { GET_LIQUIDACIONES_TODAS } from '@/graphql/queries/presupuestos.js'

const { query } = useGraphQL()

const filas = ref([])
const cargando = ref(true)

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

const tot = computed(() => filas.value.reduce((acc, f) => ({
  ingP: acc.ingP + (f.ingresosPrevistos || 0),
  ingE: acc.ingE + (f.ingresosEjecutados || 0),
  gasP: acc.gasP + (f.gastosPrevistos || 0),
  gasE: acc.gasE + (f.gastosEjecutados || 0),
}), { ingP: 0, ingE: 0, gasP: 0, gasE: 0 }))

const maxImporte = computed(() => {
  const todos = filas.value.flatMap(f => [f.ingresosEjecutados || 0, f.gastosEjecutados || 0])
  return Math.max(1, ...todos)
})
const barra = (importe) => `${Math.max(2, ((importe || 0) / maxImporte.value) * 100)}%`

onMounted(async () => {
  const data = await query(GET_LIQUIDACIONES_TODAS)
  filas.value = data?.liquidacionesPresupuestarias ?? []
  cargando.value = false
})
</script>
