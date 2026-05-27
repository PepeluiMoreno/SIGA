<template>
  <AppLayout
    title="Consentimientos"
    subtitle="Consentimientos otorgados y retirados (art. 7 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por email, nombre o cláusula…"
      :fields="camposFiltro"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando consentimientos…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtrados"
        clave-fila="id"
        vacio-texto="No hay consentimientos registrados"
      >
        <template #cell-interesado="{ fila }">
          <div class="text-sm text-slate-800">{{ fila.nombreExterno || fila.emailExterno || (fila.miembroId ? 'Miembro' : 'Usuario') }}</div>
          <div v-if="fila.emailExterno" class="text-[10px] text-slate-500">{{ fila.emailExterno }}</div>
        </template>
        <template #cell-clausula="{ fila }">
          <span class="font-mono text-xs">{{ fila.clausula?.codigo || '—' }}</span>
          <span v-if="fila.clausula" class="text-[10px] text-slate-500 ml-1">v{{ fila.clausula.version }}</span>
        </template>
        <template #cell-estado="{ fila }">
          <span :class="badgeEstado(fila.estado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.estado }}
          </span>
        </template>
        <template #cell-fechaOtorgamiento="{ fila }">
          <span class="text-xs text-slate-600">{{ fechaFmt(fila.fechaOtorgamiento) }}</span>
        </template>
        <template #cell-acciones="{ fila }">
          <button v-if="fila.estado === 'OTORGADO'"
            @click="retirar(fila)"
            class="text-xs text-amber-700 hover:text-amber-800">Retirar</button>
        </template>
      </ResponsiveTable>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_CONSENTIMIENTOS, RETIRAR_CONSENTIMIENTO } from '@/modules/proteccion_datos/graphql/queries.js'

const loading = ref(false)
const consentimientos = ref([])
const busqueda = ref('')
const filtros = ref({ estado: '' })

const camposFiltro = [
  { key: 'estado', label: 'Estado', type: 'select', allLabel: 'Todos',
    options: [{ value: 'OTORGADO', label: 'Otorgados' }, { value: 'RETIRADO', label: 'Retirados' }] },
]

const columnas = [
  { key: 'interesado',         label: 'Interesado' },
  { key: 'clausula',           label: 'Cláusula' },
  { key: 'canal',              label: 'Canal', align: 'center' },
  { key: 'fechaOtorgamiento',  label: 'Otorgado', align: 'center' },
  { key: 'estado',             label: 'Estado', align: 'center' },
  { key: 'acciones',           label: '', align: 'right', esAcciones: true },
]

const filtrados = computed(() => {
  let rows = consentimientos.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.nombreExterno || '').toLowerCase().includes(q) ||
      (r.emailExterno || '').toLowerCase().includes(q) ||
      (r.clausula?.codigo || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.estado) rows = rows.filter(r => r.estado === filtros.value.estado)
  return rows
})

function badgeEstado(estado) {
  return estado === 'OTORGADO'
    ? 'bg-emerald-100 text-emerald-700'
    : 'bg-slate-100 text-slate-600'
}

function fechaFmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_CONSENTIMIENTOS)
    consentimientos.value = [...(data.rgpdConsentimientos || [])].sort((a, b) =>
      new Date(b.fechaOtorgamiento) - new Date(a.fechaOtorgamiento))
  } finally {
    loading.value = false
  }
}

async function retirar(fila) {
  if (!confirm(`¿Confirmas la retirada del consentimiento de "${fila.nombreExterno || fila.emailExterno || 'este interesado'}"?\n\nLa retirada queda registrada con fecha y hora (art. 7.3 RGPD).`)) return
  try {
    await executeMutation(RETIRAR_CONSENTIMIENTO, { consentimientoId: fila.id })
    await cargar()
  } catch (e) {
    alert('Error al retirar: ' + (e.message || e))
  }
}

onMounted(cargar)
</script>
