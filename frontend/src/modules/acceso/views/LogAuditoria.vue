<template>
  <AppLayout title="Auditoría" subtitle="Registro de acciones del sistema" fluid>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

      <FilterRail storage-key="auditoria">
        <FilterBar
          vertical
          v-model="filters"
          v-model:search="searchQuery"
          search-placeholder="Buscar por usuario, transacción o entidad…"
          :fields="filterFields"
          @clear="limpiarFiltros"
        />
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">

        <EstadoCarga v-if="loading" />
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          {{ error }}
          <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
        </div>

        <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <ResponsiveTable
            :columnas="columnas"
            :filas="logsFiltrados"
            vacio-texto="No hay registros de auditoría">

            <template #cell-fechaHora="{ fila: l }">
              <span class="text-xs text-gray-700 whitespace-nowrap">{{ formatFecha(l.fechaHora) }}</span>
            </template>

            <template #cell-usernameSnapshot="{ fila: l }">
              <span class="text-sm text-gray-900">{{ l.usernameSnapshot || '—' }}</span>
            </template>

            <template #cell-accion="{ fila: l }">
              <span :class="accionClass(l.accion)">{{ l.accion }}</span>
            </template>

            <template #cell-transaccionCodigo="{ fila: l }">
              <span class="text-xs font-mono text-gray-700">{{ l.transaccionCodigo || '—' }}</span>
            </template>

            <template #cell-exitoso="{ fila: l }">
              <span :class="l.exitoso
                ? 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
                : 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800'">
                {{ l.exitoso ? 'OK' : 'Error' }}
              </span>
            </template>

          </ResponsiveTable>
        </div>

      </div><!-- /columna de resultados -->
    </div><!-- /layout -->

  </AppLayout>
</template>

<script setup>
import { ref, computed, onActivated } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import { graphqlClient } from '@/graphql/client.js'

defineOptions({ name: 'LogAuditoria' })

const LOGS_QUERY = gql`
  query LogsAuditoria {
    logsAuditoria {
      id
      fechaHora
      usuarioId
      usernameSnapshot
      accion
      transaccionCodigo
      entidad
      entidadId
      exitoso
      mensajeError
      descripcion
      ipAddress
    }
  }
`

const loading = ref(false)
const error = ref('')
const logs = ref([])
const searchQuery = ref('')
const filters = ref({ accion: [], exitoso: [] })

const acciones = ['CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'APROBAR', 'RECHAZAR', 'EXPORTAR', 'LOGIN', 'LOGOUT', 'OTRO']

const columnas = [
  { key: 'fechaHora',         label: 'Fecha',       ordenable: true },
  { key: 'usernameSnapshot',  label: 'Usuario',     ordenable: true },
  { key: 'accion',            label: 'Acción',      ordenable: true },
  { key: 'transaccionCodigo', label: 'Transacción', ordenable: true },
  { key: 'entidad',           label: 'Entidad',     ordenable: true },
  { key: 'exitoso',           label: 'Resultado',   align: 'center', ordenable: true },
  { key: 'descripcion',       label: 'Descripción', ordenable: true },
]

// Filtros con pocas opciones = multiselect (OR): ver «activos o suspendidos».
const filterFields = [
  {
    key: 'accion', label: 'Acción', type: 'multiselect', allLabel: 'Todas',
    options: acciones.map(a => ({ value: a, label: a })),
  },
  {
    key: 'exitoso', label: 'Resultado', type: 'multiselect', allLabel: 'Todos',
    options: [
      { value: 'true',  label: 'Exitosas' },
      { value: 'false', label: 'Fallidas' },
    ],
  },
]

const logsFiltrados = computed(() => {
  let r = logs.value
  if (filters.value.accion.length) {
    r = r.filter((l) => filters.value.accion.includes(l.accion))
  }
  if (filters.value.exitoso.length) {
    r = r.filter((l) => filters.value.exitoso.includes(String(l.exitoso)))
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter((l) =>
      (l.usernameSnapshot || '').toLowerCase().includes(q) ||
      (l.transaccionCodigo || '').toLowerCase().includes(q) ||
      (l.entidad || '').toLowerCase().includes(q) ||
      (l.descripcion || '').toLowerCase().includes(q),
    )
  }
  // Por defecto, de más reciente a más antigua; las columnas ordenables mandan.
  return r.slice().sort((a, b) => (b.fechaHora || '').localeCompare(a.fechaHora || ''))
})

function limpiarFiltros() {
  searchQuery.value = ''
  filters.value = { accion: [], exitoso: [] }
}

function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'medium' })
}

function accionClass(accion) {
  const map = {
    LOGIN: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    LOGOUT: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    CREAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    EDITAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    ELIMINAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    APROBAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    RECHAZAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    EXPORTAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    VER: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    OTRO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return map[accion] || map.OTRO
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(LOGS_QUERY)
    logs.value = data.logsAuditoria || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando auditoría'
  } finally {
    loading.value = false
  }
}

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso,
// evitando mostrar datos obsoletos.
onActivated(cargar)
</script>
