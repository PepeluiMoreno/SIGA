<template>
  <div class="space-y-6">

    <!-- Resumen de horas -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-slate-50 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ totalHorasEstimadas }}</div>
        <div class="text-xs text-slate-500 mt-1">Horas estimadas</div>
      </div>
      <div class="bg-indigo-50 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-indigo-700">{{ totalHorasReales }}</div>
        <div class="text-xs text-slate-500 mt-1">Horas reales</div>
      </div>
      <div class="bg-green-50 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-green-700">{{ totalVoluntarios }}</div>
        <div class="text-xs text-slate-500 mt-1">Voluntarios activos</div>
      </div>
      <div class="bg-amber-50 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-amber-700">{{ totalTareas }}</div>
        <div class="text-xs text-slate-500 mt-1">Tareas en total</div>
      </div>
    </div>

    <!-- Desglose por equipo -->
    <div v-if="grupos.length > 0">
      <h3 class="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wide">Desglose por equipo</h3>
      <div class="rounded-lg border border-slate-200 overflow-hidden">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Equipo</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">Voluntarios</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">Tareas</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">H. Estimadas</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">H. Reales</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">Desviación</th>
              <th class="px-4 py-3 text-right font-medium text-slate-600">Presupuesto</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-slate-100">
            <tr v-for="g in resumenGrupos" :key="g.id" class="hover:bg-slate-50">
              <td class="px-4 py-3">
                <div class="font-medium text-slate-800">{{ g.nombre }}</div>
                <div v-if="g.tipoGrupo" class="text-xs text-slate-400">{{ g.tipoGrupo.nombre }}</div>
              </td>
              <td class="px-4 py-3 text-right text-slate-600">{{ g.voluntarios }}</td>
              <td class="px-4 py-3 text-right text-slate-600">{{ g.tareas }}</td>
              <td class="px-4 py-3 text-right text-slate-600">{{ g.horasEstimadas ?? '—' }}</td>
              <td class="px-4 py-3 text-right text-slate-600">{{ g.horasReales ?? '—' }}</td>
              <td class="px-4 py-3 text-right">
                <span
                  v-if="g.horasEstimadas != null && g.horasReales != null"
                  :class="g.horasReales > g.horasEstimadas ? 'text-red-600' : 'text-green-600'"
                  class="font-medium"
                >
                  {{ g.horasReales > g.horasEstimadas ? '+' : '' }}{{ (g.horasReales - g.horasEstimadas).toFixed(1) }}h
                </span>
                <span v-else class="text-slate-300">—</span>
              </td>
              <td class="px-4 py-3 text-right">
                <div v-if="g.presupuestoAsignado != null" class="text-slate-800">
                  {{ fmt(g.presupuestoEjecutado) }} / {{ fmt(g.presupuestoAsignado) }}
                </div>
                <span v-else class="text-slate-300">—</span>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="grupos.length > 1" class="bg-slate-50 border-t-2 border-slate-300">
            <tr class="font-semibold text-slate-700">
              <td class="px-4 py-3">Total</td>
              <td class="px-4 py-3 text-right">{{ totalVoluntarios }}</td>
              <td class="px-4 py-3 text-right">{{ totalTareas }}</td>
              <td class="px-4 py-3 text-right">{{ totalHorasEstimadas || '—' }}</td>
              <td class="px-4 py-3 text-right">{{ totalHorasReales || '—' }}</td>
              <td class="px-4 py-3 text-right">
                <span
                  v-if="totalHorasEstimadas && totalHorasReales"
                  :class="totalHorasReales > totalHorasEstimadas ? 'text-red-600' : 'text-green-600'"
                >
                  {{ totalHorasReales > totalHorasEstimadas ? '+' : '' }}{{ (totalHorasReales - totalHorasEstimadas).toFixed(1) }}h
                </span>
              </td>
              <td class="px-4 py-3 text-right">{{ fmt(totalPresupuestoEjecutado) }} / {{ fmt(totalPresupuestoAsignado) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Tareas por estado -->
    <div v-if="totalTareas > 0">
      <h3 class="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wide">Tareas por estado</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div
          v-for="(count, estado) in tareasPorEstado"
          :key="estado"
          class="bg-white border border-slate-200 rounded-lg p-3 text-center"
        >
          <div class="text-xl font-bold text-slate-800">{{ count }}</div>
          <div class="text-xs text-slate-500 mt-0.5">{{ estado }}</div>
        </div>
      </div>
    </div>

    <!-- Presupuesto de la campaña -->
    <div v-if="campania.metaRecaudacion || totalPresupuestoAsignado > 0" class="pt-4 border-t border-slate-200">
      <h3 class="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wide">Presupuesto global</h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="bg-slate-50 rounded-lg p-4">
          <div class="text-xs text-slate-500">Presupuesto equipos</div>
          <div class="mt-1 text-lg font-semibold text-slate-800">{{ fmt(totalPresupuestoAsignado) }}</div>
          <div class="text-xs text-slate-400 mt-0.5">Ejecutado: {{ fmt(totalPresupuestoEjecutado) }}</div>
        </div>
        <div v-if="campania.metaRecaudacion" class="bg-green-50 rounded-lg p-4 border border-green-200">
          <div class="text-xs text-slate-500">Meta recaudación</div>
          <div class="mt-1 text-lg font-semibold text-green-700">{{ fmt(campania.metaRecaudacion) }}</div>
        </div>
        <div v-if="totalPresupuestoAsignado > 0" class="bg-white border border-slate-200 rounded-lg p-4">
          <div class="text-xs text-slate-500">Ejecución presupuesto</div>
          <div class="mt-2">
            <div class="flex justify-between text-xs text-slate-600 mb-1">
              <span>{{ fmt(totalPresupuestoEjecutado) }}</span>
              <span>{{ pctPresupuesto }}%</span>
            </div>
            <div class="w-full bg-slate-200 rounded-full h-2">
              <div
                :class="pctPresupuesto >= 90 ? 'bg-red-500' : pctPresupuesto >= 70 ? 'bg-amber-500' : 'bg-indigo-500'"
                class="h-2 rounded-full transition-all"
                :style="{ width: Math.min(pctPresupuesto, 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sin datos -->
    <div v-if="grupos.length === 0" class="text-center py-12 border-2 border-dashed border-slate-200 rounded-lg">
      <p class="text-slate-500 text-sm">Asigna equipos a esta campaña para ver la estimación de recursos</p>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  campania: { type: Object, required: true },
  grupos: { type: Array, default: () => [] },
})

const fmt = (v) => {
  if (v == null || v === 0) return '€0'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v)
}

const sumH = (tareas, campo) => {
  const s = (tareas ?? []).reduce((acc, t) => acc + (parseFloat(t[campo]) || 0), 0)
  return s > 0 ? parseFloat(s.toFixed(1)) : null
}

const resumenGrupos = computed(() =>
  props.grupos.map(g => ({
    id: g.id,
    nombre: g.nombre,
    tipoGrupo: g.tipoGrupo,
    voluntarios: (g.miembros ?? []).filter(m => m.activo).length,
    tareas: (g.tareas ?? []).length,
    horasEstimadas: sumH(g.tareas, 'horasEstimadas'),
    horasReales: sumH(g.tareas, 'horasReales'),
    presupuestoAsignado: g.presupuestoAsignado ? parseFloat(g.presupuestoAsignado) : null,
    presupuestoEjecutado: parseFloat(g.presupuestoEjecutado) || 0,
  }))
)

const totalVoluntarios = computed(() => {
  const ids = new Set()
  for (const g of props.grupos) {
    for (const m of g.miembros ?? []) {
      if (m.activo) ids.add(m.id)
    }
  }
  return ids.size
})

const totalTareas = computed(() => props.grupos.reduce((acc, g) => acc + (g.tareas?.length ?? 0), 0))

const totalHorasEstimadas = computed(() => {
  const s = resumenGrupos.value.reduce((acc, g) => acc + (g.horasEstimadas ?? 0), 0)
  return s > 0 ? parseFloat(s.toFixed(1)) : null
})

const totalHorasReales = computed(() => {
  const s = resumenGrupos.value.reduce((acc, g) => acc + (g.horasReales ?? 0), 0)
  return s > 0 ? parseFloat(s.toFixed(1)) : null
})

const totalPresupuestoAsignado = computed(() =>
  resumenGrupos.value.reduce((acc, g) => acc + (g.presupuestoAsignado ?? 0), 0)
)

const totalPresupuestoEjecutado = computed(() =>
  resumenGrupos.value.reduce((acc, g) => acc + g.presupuestoEjecutado, 0)
)

const pctPresupuesto = computed(() => {
  if (!totalPresupuestoAsignado.value) return 0
  return Math.round((totalPresupuestoEjecutado.value / totalPresupuestoAsignado.value) * 100)
})

const tareasPorEstado = computed(() => {
  const counts = {}
  for (const g of props.grupos) {
    for (const t of g.tareas ?? []) {
      const estado = t.estado?.nombre ?? 'Sin estado'
      counts[estado] = (counts[estado] ?? 0) + 1
    }
  }
  return counts
})
</script>
