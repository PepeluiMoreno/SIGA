<template>
  <AppLayout title="Estadísticas de socios" subtitle="Altas y bajas por año y agrupación">
    <!-- Filtros: rango de años + agrupación. Reutiliza los controles de formulario comunes. -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <label class="text-xs text-slate-500">
        Desde (año)
        <input v-model.number="anioDesde" type="number" class="mt-1 block w-28 rounded-lg border-slate-300 text-sm" />
      </label>
      <label class="text-xs text-slate-500">
        Hasta (año)
        <input v-model.number="anioHasta" type="number" class="mt-1 block w-28 rounded-lg border-slate-300 text-sm" />
      </label>
      <label class="text-xs text-slate-500">
        Agrupación
        <select v-model="agrupacionId" class="mt-1 block w-64 rounded-lg border-slate-300 text-sm">
          <option :value="null">Todas</option>
          <option v-for="a in agrupaciones" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </select>
      </label>
      <AppButton size="sm" @click="cargar">Actualizar</AppButton>
    </div>

    <ErrorAlert v-if="error" :message="error" class="mb-3" />

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <template v-else>
      <!-- Totales del rango. -->
      <div class="text-xs text-slate-500 mb-3 px-1 flex items-center gap-3 flex-wrap">
        <span>{{ filas.length }} filas</span>
        <span class="text-slate-300">·</span>
        <span class="text-emerald-700"><strong>{{ totalAltas }}</strong> altas</span>
        <span class="text-red-700"><strong>{{ totalBajas }}</strong> bajas</span>
        <span class="text-slate-300">·</span>
        <span :class="totalNeto >= 0 ? 'text-emerald-700' : 'text-red-700'">
          Neto <strong>{{ totalNeto >= 0 ? '+' : '' }}{{ totalNeto }}</strong>
        </span>
      </div>

      <div v-if="filas.length" class="bg-white border border-slate-200 rounded-xl sm:overflow-hidden p-3 sm:p-0">
        <ResponsiveTable :columnas="columnas" :filas="filas" clave-fila="_key">
          <template #cell-neto="{ fila }">
            <span :class="fila.neto >= 0 ? 'text-emerald-700' : 'text-red-700'" class="font-mono">
              {{ fila.neto >= 0 ? '+' : '' }}{{ fila.neto }}
            </span>
          </template>
        </ResponsiveTable>
      </div>
      <div v-else class="text-center py-16 text-slate-400 text-sm">
        No hay altas ni bajas en el rango seleccionado.
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import AppButton from '@/components/common/AppButton.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import { GET_ESTADISTICAS_ALTAS_BAJAS } from '@/graphql/queries/socioGestion.js'

const { query, loading, error: gqlError } = useGraphQL()

const anioActual = new Date().getFullYear()
const anioDesde = ref(anioActual - 4)
const anioHasta = ref(anioActual)
const agrupacionId = ref(null)
const agrupaciones = ref([])
const filas = ref([])
const error = ref('')

const columnas = [
  { key: 'anio', label: 'Año', align: 'left' },
  { key: 'agrupacionNombre', label: 'Agrupación', align: 'left', formato: v => v || 'Sin agrupación' },
  { key: 'altas', label: 'Altas', align: 'right' },
  { key: 'bajas', label: 'Bajas', align: 'right' },
  { key: 'neto', label: 'Neto', align: 'right' },
]

const totalAltas = computed(() => filas.value.reduce((s, f) => s + f.altas, 0))
const totalBajas = computed(() => filas.value.reduce((s, f) => s + f.bajas, 0))
const totalNeto = computed(() => totalAltas.value - totalBajas.value)

async function cargarAgrupaciones() {
  try {
    const data = await query(GET_AGRUPACIONES)
    agrupaciones.value = (data.unidadesOrganizativas || []).filter(a => a.activo)
  } catch { /* el error de estadísticas es el relevante */ }
}

async function cargar() {
  error.value = ''
  try {
    const data = await query(GET_ESTADISTICAS_ALTAS_BAJAS, {
      anioDesde: anioDesde.value,
      anioHasta: anioHasta.value,
      agrupacionId: agrupacionId.value,
    })
    filas.value = (data.estadisticasAltasBajas || []).map(f => ({
      ...f,
      _key: `${f.anio}-${f.agrupacionId ?? 'null'}`,
    }))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar las estadísticas'
  }
}

onMounted(async () => {
  await cargarAgrupaciones()
  await cargar()
})
</script>
