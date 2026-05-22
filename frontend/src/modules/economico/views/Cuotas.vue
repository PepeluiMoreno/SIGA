<template>
  <AppLayout title="Cuotas" subtitle="Historial de cuotas base por ejercicio">

    <div class="space-y-4">

      <!-- Cabecera con botón ir a configurar -->
      <div class="flex justify-end">
        <router-link to="/economico/cuotas-ejercicio" class="btn-primary text-sm">
          + Configurar ejercicio
        </router-link>
      </div>

      <!-- Tabla de historial -->
      <div class="bg-white rounded-xl border border-slate-200 sm:overflow-hidden p-3 sm:p-0">
        <div v-if="cargando" class="p-8 text-center text-slate-400 text-sm">Cargando…</div>
        <div v-else-if="!cuotas.length" class="p-8 text-center text-slate-400 text-sm">
          No hay cuotas configuradas. Usa "Configurar ejercicio" para establecer la primera.
        </div>
        <ResponsiveTable
          v-else
          :columnas="columnasCuotas"
          :filas="cuotasConVariacion"
          clave-fila="id"
        >
          <template #cell-ejercicio="{ fila }">
            <span class="font-semibold text-slate-800">{{ fila.ejercicio }}</span>
          </template>
          <template #cell-denominacion="{ fila }">
            <span class="text-slate-600">{{ fila.nombreCuota || `Cuota base ${fila.ejercicio}` }}</span>
          </template>
          <template #cell-importe="{ fila }">
            <span class="font-mono font-medium text-slate-800">{{ fmt(fila.importe) }}</span>
          </template>
          <template #cell-variacion="{ fila }">
            <span v-if="fila._variacion !== null"
              :class="fila._variacion > 0 ? 'text-green-700 bg-green-50' : fila._variacion < 0 ? 'text-red-700 bg-red-50' : 'text-slate-500 bg-slate-100'"
              class="text-xs font-medium px-2 py-0.5 rounded-full">
              {{ fila._variacion > 0 ? '+' : '' }}{{ fila._variacion.toFixed(1) }}%
            </span>
            <span v-else class="text-xs text-slate-400">—</span>
          </template>
          <template #cell-observaciones="{ fila }">
            <span class="text-slate-500">{{ fila.observaciones || '—' }}</span>
          </template>
          <template #cell-acciones="{ fila }">
            <router-link
              :to="{ path: '/economico/cuotas-ejercicio', query: { ejercicio: fila.ejercicio } }"
              class="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
            >Editar</router-link>
          </template>
        </ResponsiveTable>
      </div>

      <!-- Resumen de cobertura de ejercicios activos -->
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800" v-if="sinCuota.length">
        <p class="font-medium mb-1">Ejercicios sin cuota configurada:</p>
        <div class="flex flex-wrap gap-2 mt-1">
          <span v-for="y in sinCuota" :key="y"
            class="bg-white border border-amber-300 rounded-full px-3 py-0.5 text-xs font-medium">
            {{ y }}
          </span>
        </div>
        <p class="text-xs mt-2 text-amber-700">
          Sin cuota establecida no se puede iniciar la elaboración del presupuesto de ingresos para ese ejercicio.
        </p>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { GET_HISTORIAL_CUOTAS } from '@/graphql/queries/economico'

const { query } = useGraphQL()

const cuotas = ref([])
const cargando = ref(true)

const anoActual = new Date().getFullYear()

const cuotasOrdenadas = computed(() =>
  [...cuotas.value].sort((a, b) => b.ejercicio - a.ejercicio)
)

const sinCuota = computed(() => {
  const ejerciciosConCuota = new Set(cuotas.value.map(c => c.ejercicio))
  const mes = new Date().getMonth() + 1
  const relevantes = mes >= 10 ? [anoActual - 1, anoActual, anoActual + 1] : [anoActual - 1, anoActual]
  return relevantes.filter(y => !ejerciciosConCuota.has(y))
})

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)

const variacion = (cuota, idx) => {
  const siguiente = cuotasOrdenadas.value[idx + 1]
  if (!siguiente || !siguiente.importe) return null
  return ((parseFloat(cuota.importe) - parseFloat(siguiente.importe)) / parseFloat(siguiente.importe)) * 100
}

// Cuotas con la variación precalculada (ResponsiveTable no expone el índice en el slot)
const cuotasConVariacion = computed(() =>
  cuotasOrdenadas.value.map((c, i) => ({ ...c, _variacion: variacion(c, i) }))
)

// Columnas de la tabla responsive (Ejercicio = cabecera de tarjeta en móvil)
const columnasCuotas = [
  { key: 'ejercicio',     label: 'Ejercicio' },
  { key: 'denominacion',  label: 'Denominación' },
  { key: 'importe',       label: 'Importe base', align: 'right' },
  { key: 'variacion',     label: 'Variación' },
  { key: 'observaciones', label: 'Observaciones', ocultaEnMovil: true },
  { key: 'acciones',      label: 'Acciones', align: 'right', esAcciones: true },
]

onMounted(async () => {
  const data = await query(GET_HISTORIAL_CUOTAS)
  cuotas.value = data.importesCuotaAnio || []
  cargando.value = false
})
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium; }
</style>
