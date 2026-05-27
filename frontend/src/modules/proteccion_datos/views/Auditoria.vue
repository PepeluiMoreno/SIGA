<template>
  <AppLayout
    title="Auditoría de accesos a datos personales"
    subtitle="Registro append-only para responsabilidad proactiva (art. 5.2 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por entidad, usuario o motivo…"
      :fields="camposFiltro"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando log…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtrados"
        clave-fila="id"
        vacio-texto="No hay registros de acceso"
      >
        <template #cell-fechaAcceso="{ fila }">
          <span class="text-xs text-slate-600">{{ fechaHoraFmt(fila.fechaAcceso) }}</span>
        </template>
        <template #cell-tipoAcceso="{ fila }">
          <span :class="badgeTipo(fila.tipoAcceso)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.tipoAcceso }}
          </span>
        </template>
        <template #cell-usuario="{ fila }">
          <div class="text-xs text-slate-700">{{ fila.usuarioEmailSnapshot || '—' }}</div>
          <div v-if="fila.ip" class="text-[10px] text-slate-400 font-mono">{{ fila.ip }}</div>
        </template>
        <template #cell-entidad="{ fila }">
          <div class="text-xs font-medium">{{ fila.entidad }}</div>
          <div v-if="fila.entidadId" class="text-[10px] text-slate-400 font-mono">{{ fila.entidadId.slice(0, 8) }}…</div>
        </template>
      </ResponsiveTable>
    </div>

    <p class="text-[11px] text-slate-400 mt-3">
      ⓘ Este log es append-only: las entradas no se editan ni se borran (responsabilidad proactiva).
    </p>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { executeQuery } from '@/graphql/client'
import { GET_AUDITORIA_ACCESOS } from '@/modules/proteccion_datos/graphql/queries.js'

const loading = ref(false)
const log = ref([])
const busqueda = ref('')
const filtros = ref({ tipoAcceso: '', entidad: '' })

const camposFiltro = [
  { key: 'tipoAcceso', label: 'Tipo', type: 'select', allLabel: 'Todos',
    options: ['LECTURA', 'ESCRITURA', 'EXPORT', 'ANONIMIZACION', 'BORRADO']
      .map(t => ({ value: t, label: t })) },
]

const columnas = [
  { key: 'fechaAcceso', label: 'Fecha' },
  { key: 'usuario',     label: 'Usuario' },
  { key: 'entidad',     label: 'Entidad' },
  { key: 'tipoAcceso',  label: 'Acción', align: 'center' },
  { key: 'motivo',      label: 'Motivo' },
]

const filtrados = computed(() => {
  let rows = log.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.entidad || '').toLowerCase().includes(q) ||
      (r.usuarioEmailSnapshot || '').toLowerCase().includes(q) ||
      (r.motivo || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.tipoAcceso) rows = rows.filter(r => r.tipoAcceso === filtros.value.tipoAcceso)
  return rows
})

function badgeTipo(t) {
  const map = {
    LECTURA:        'bg-slate-100 text-slate-600',
    ESCRITURA:      'bg-amber-100 text-amber-700',
    EXPORT:         'bg-indigo-100 text-indigo-700',
    ANONIMIZACION:  'bg-orange-100 text-orange-700',
    BORRADO:        'bg-rose-100 text-rose-700',
  }
  return map[t] || 'bg-slate-100 text-slate-500'
}

function fechaHoraFmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_AUDITORIA_ACCESOS)
    log.value = [...(data.rgpdAuditoriaAccesos || [])].sort((a, b) =>
      new Date(b.fechaAcceso) - new Date(a.fechaAcceso))
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
