<template>
  <section class="bg-white border border-slate-200 rounded-xl px-5 py-3 grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-2 text-sm">
    <!-- Tipo y ámbito -->
    <div class="flex flex-col gap-0.5">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Tipo</span>
      <span class="font-semibold text-slate-700">{{ campania.tipoCampania?.nombre ?? '—' }}</span>
    </div>

    <div class="flex flex-col gap-0.5">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Ámbito</span>
      <span class="font-semibold text-slate-700">{{ campania.agrupacion?.nombre ?? '—' }}</span>
    </div>

    <!-- Fechas -->
    <div class="flex flex-col gap-0.5">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Fechas</span>
      <span class="font-semibold text-slate-700">{{ rangoFechas }}</span>
    </div>

    <!-- Actividades -->
    <div class="flex flex-col gap-0.5">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Actividades</span>
      <span class="font-semibold text-slate-700">{{ numActividades }}</span>
    </div>

    <!-- Presupuesto con barra de progreso -->
    <div class="flex flex-col gap-1 sm:col-span-2 lg:col-span-1">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Presupuesto</span>
      <div class="flex items-center gap-2">
        <span class="font-semibold text-slate-700">{{ formatEuros(totalPresupuesto) }}</span>
        <span v-if="pctEjecutado !== null" class="text-xs text-slate-400">
          {{ pctEjecutado }}% ej.
        </span>
      </div>
      <div v-if="pctEjecutado !== null" class="w-full bg-slate-100 rounded-full h-1.5">
        <div
          class="h-1.5 rounded-full transition-all"
          :class="pctEjecutado >= 100 ? 'bg-red-400' : pctEjecutado >= 75 ? 'bg-amber-400' : 'bg-indigo-400'"
          :style="{ width: Math.min(pctEjecutado, 100) + '%' }"
        />
      </div>
    </div>

    <!-- Metas (si las hay) -->
    <div v-if="campania.metas?.length" class="flex flex-col gap-0.5">
      <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Metas</span>
      <span class="font-semibold text-slate-700">
        {{ metasConValor }}/{{ campania.metas.length }}
        <span class="text-slate-400 font-normal">con dato real</span>
      </span>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  campania: { type: Object, required: true },
})

const numActividades = computed(() => props.campania.actividades?.length ?? 0)

const rangoFechas = computed(() => {
  const ini = props.campania.fechaInicioPlan
  const fin = props.campania.fechaFinPlan
  if (!ini && !fin) return '—'
  const fmt = (d) => new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  if (!fin) return fmt(ini)
  return `${fmt(ini)} – ${fmt(fin)}`
})

const totalPresupuesto = computed(() => {
  const partidas = props.campania.partidasPresupuesto ?? []
  const gastos = partidas
    .filter(p => p.tipoPartida === 'gasto')
    .reduce((s, p) => s + (parseFloat(p.importeEstimado) || 0), 0)
  const actsGastos = (props.campania.actividades ?? [])
    .reduce((s, a) => s + (parseFloat(a.presupuestoEstimado) || 0), 0)
  return gastos + actsGastos
})

const pctEjecutado = computed(() => {
  const ej = parseFloat(props.campania.presupuestoEjecutado)
  if (!ej || totalPresupuesto.value === 0) return null
  return Math.round((ej / totalPresupuesto.value) * 100)
})

const metasConValor = computed(() =>
  (props.campania.metas ?? []).filter(m => m.valorReal != null).length
)

function formatEuros(n) {
  if (!n) return '0 €'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n)
}
</script>
