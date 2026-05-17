<template>
  <div v-if="actividadesPositionadas.length" class="select-none">
    <!-- Cabecera de meses -->
    <div class="relative h-5 mb-1">
      <div
        v-for="mes in meses"
        :key="mes.label + mes.left"
        class="absolute text-xs text-slate-400 font-medium"
        :style="{ left: mes.left + '%' }"
      >
        {{ mes.label }}
      </div>
    </div>

    <!-- Fondo de cuadrícula -->
    <div class="relative bg-slate-50 border border-slate-200 rounded-lg h-8 overflow-hidden">
      <div
        v-for="mes in meses"
        :key="'grid-' + mes.left"
        class="absolute top-0 bottom-0 border-l border-slate-200"
        :style="{ left: mes.left + '%' }"
      />

      <!-- Chips de actividad -->
      <div
        v-for="act in actividadesPositionadas"
        :key="act.id"
        class="absolute top-1 bottom-1 rounded-md cursor-pointer opacity-80 hover:opacity-100 transition-opacity flex items-center px-1.5 overflow-hidden"
        :class="colorClase(act)"
        :style="{ left: act._left + '%', width: Math.max(act._width, 3) + '%' }"
        :title="`${act.nombre} (${fmtDate(act.fechaInicio)} – ${fmtDate(act.fechaFin)})`"
        @click="$emit('select', act.id)"
      >
        <span class="text-xs font-medium text-white truncate leading-none">{{ act.nombre }}</span>
      </div>
    </div>

    <p class="mt-1 text-xs text-slate-400">
      {{ actividadesPositionadas.length }} actividad{{ actividadesPositionadas.length !== 1 ? 'es' : '' }} con fecha
      <span v-if="sinFecha > 0"> · {{ sinFecha }} sin fecha</span>
    </p>
  </div>
  <p v-else class="text-sm text-slate-400 italic py-2">
    Ninguna actividad tiene fechas asignadas aún.
  </p>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  actividades: { type: Array, default: () => [] },
  fechaInicio: { type: String, default: null },
  fechaFin: { type: String, default: null },
})

defineEmits(['select'])

const sinFecha = computed(() =>
  props.actividades.filter(a => !a.fechaInicio).length
)

const rango = computed(() => {
  const conFecha = props.actividades.filter(a => a.fechaInicio)
  if (!conFecha.length && !props.fechaInicio) return null

  const inis = conFecha.map(a => new Date(a.fechaInicio))
  if (props.fechaInicio) inis.push(new Date(props.fechaInicio))

  const fins = conFecha.filter(a => a.fechaFin).map(a => new Date(a.fechaFin))
  if (props.fechaFin) fins.push(new Date(props.fechaFin))

  const min = new Date(Math.min(...inis))
  const maxFin = fins.length ? new Date(Math.max(...fins)) : null
  const maxIni = new Date(Math.max(...inis))
  const max = maxFin && maxFin > maxIni ? maxFin : new Date(maxIni.getTime() + 7 * 86400000)

  const total = Math.max((max - min) / 86400000, 1)
  return { min, max, total }
})

const actividadesPositionadas = computed(() => {
  if (!rango.value) return []
  return props.actividades
    .filter(a => a.fechaInicio)
    .map(a => {
      const ini = new Date(a.fechaInicio)
      const fin = a.fechaFin ? new Date(a.fechaFin) : new Date(ini.getTime() + 86400000)
      const left = ((ini - rango.value.min) / 86400000 / rango.value.total) * 100
      const width = ((fin - ini) / 86400000 / rango.value.total) * 100
      return { ...a, _left: Math.max(0, left), _width: Math.max(0.5, width) }
    })
})

const meses = computed(() => {
  if (!rango.value) return []
  const result = []
  const cur = new Date(rango.value.min)
  cur.setDate(1)
  while (cur <= rango.value.max) {
    const left = ((cur - rango.value.min) / 86400000 / rango.value.total) * 100
    if (left >= 0 && left <= 98) {
      result.push({
        label: cur.toLocaleDateString('es-ES', { month: 'short', year: '2-digit' }),
        left,
      })
    }
    cur.setMonth(cur.getMonth() + 1)
  }
  return result
})

const COLORES = [
  'bg-indigo-500', 'bg-violet-500', 'bg-sky-500', 'bg-emerald-500',
  'bg-amber-500', 'bg-rose-500', 'bg-teal-500', 'bg-fuchsia-500',
]

const tipoIds = computed(() => [
  ...new Set(props.actividades.map(a => a.tipoActividad?.id ?? a.tipoActividad?.nombre ?? 'x'))
])

function colorClase(act) {
  const key = act.tipoActividad?.id ?? act.tipoActividad?.nombre ?? 'x'
  return COLORES[tipoIds.value.indexOf(key) % COLORES.length]
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}
</script>
