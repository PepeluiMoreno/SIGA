<template>
  <AppLayout title="Grupos de Trabajo" subtitle="Gestión de grupos y equipos" fluid>

    <!-- Acción principal en el topbar (estándar global) -->
    <template v-if="tienePermiso('GRUPO_CREAR')" #actions>
      <router-link to="/grupos/nuevo"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nuevo Grupo
      </router-link>
    </template>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

      <FilterRail storage-key="grupos">
        <FilterBar
          vertical
          v-model="filters"
          v-model:search="searchQuery"
          search-placeholder="Buscar grupos…"
          :fields="filterFields"
          @clear="limpiarFiltros"
        />
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">

        <!-- Estado carga / error -->
        <EstadoCarga v-if="loading" mensaje="Cargando grupos…" />
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          {{ error }}
          <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
        </div>

        <!-- Tabla -->
        <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <ResponsiveTable
            :columnas="columnas"
            :filas="gruposFiltrados"
            :orden-inicial="{ key: 'nombre', dir: 'asc' }"
            vacio-texto="No hay grupos con los filtros seleccionados">

            <template #cell-nombre="{ fila: g }">
              <div class="text-sm font-medium text-gray-900">{{ g.nombre }}</div>
              <div v-if="g.descripcion" class="text-xs text-gray-400 truncate max-w-xs">{{ g.descripcion }}</div>
            </template>

            <template #cell-tipo="{ fila: g }">
              <span :class="getTipoClass(g.tipo?.nombre)">{{ g.tipo?.nombre ?? '—' }}</span>
            </template>

            <template #cell-coordinador="{ fila: g }">
              <span v-if="g.coordinador" class="text-sm text-gray-700">
                {{ g.coordinador.nombre }} {{ g.coordinador.apellido1 }}
              </span>
              <span v-else class="text-xs text-gray-400 italic">Sin coordinador</span>
            </template>

            <template #cell-miembros="{ fila: g }">
              {{ g.miembros?.length ?? 0 }}
            </template>

            <template #cell-fechaCreacion="{ fila: g }">
              {{ g.fechaCreacion ? formatDate(g.fechaCreacion) : '—' }}
            </template>

            <template #cell-activo="{ fila: g }">
              <span class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                :class="g.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
                {{ g.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </template>

            <template #cell-acciones="{ fila: g }">
              <div class="flex items-center justify-end">
                <RowActions
                  :show-view="true"
                  :show-edit="true"
                  confirm-title="¿Eliminar este grupo?"
                  :confirm-text="`«${g.nombre}» será eliminado permanentemente.`"
                  @view="$router.push(`/grupos/${g.id}`)"
                  @edit="$router.push(`/grupos/${g.id}`)"
                  @delete="eliminarGrupo(g)"
                />
              </div>
            </template>
          </ResponsiveTable>
        </div>

      </div><!-- /columna de resultados -->
    </div><!-- /layout -->

  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, onActivated } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import RowActions from '@/components/common/RowActions.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import { graphqlClient, executeQuery } from '@/graphql/client'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_GRUPOS, GET_TIPOS_GRUPO, ELIMINAR_GRUPO } from '@/graphql/queries/grupos.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'

defineOptions({ name: 'ListaGrupos' })

const toast = useToast()
const { tienePermiso } = usePermisos()

const loading = ref(false)
const error = ref('')
const grupos = ref([])
const tiposGrupo = ref([])
const searchQuery = ref('')
const filters = ref({ tipo: [], activo: [] })

const columnas = [
  { key: 'nombre',       label: 'Nombre',      ordenable: true },
  { key: 'tipo',         label: 'Tipo',        ordenable: true, valorOrden: g => g.tipo?.nombre ?? '' },
  { key: 'coordinador',  label: 'Coordinador', valorOrden: g => g.coordinador?.apellido1 ?? '' },
  { key: 'miembros',     label: 'Miembros',    align: 'center', ordenable: true,
    valorOrden: g => g.miembros?.length ?? 0 },
  { key: 'fechaCreacion', label: 'Desde',      align: 'center', ordenable: true },
  { key: 'activo',       label: 'Estado',      align: 'center', ordenable: true },
  { key: 'acciones',     label: '',            align: 'right', esAcciones: true },
]

const filterFields = computed(() => [
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect', allLabel: 'Todos los tipos',
    options: tiposGrupo.value.map(t => ({ value: t.id, label: t.nombre })),
  },
  {
    key: 'activo', label: 'Estado', type: 'multiselect', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }],
  },
])

const gruposFiltrados = computed(() => {
  let result = grupos.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(g =>
      g.nombre?.toLowerCase().includes(q) ||
      g.descripcion?.toLowerCase().includes(q)
    )
  }
  if (filters.value.tipo?.length) {
    result = result.filter(g => filters.value.tipo.includes(g.tipo?.id))
  }
  if (filters.value.activo?.length) {
    result = result.filter(g => filters.value.activo.includes(String(g.activo)))
  }
  return result
})

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const [dataGrupos, dataTipos] = await Promise.all([
      executeQuery(GET_GRUPOS),
      executeQuery(GET_TIPOS_GRUPO),
    ])
    grupos.value = dataGrupos.gruposTrabajo || []
    tiposGrupo.value = (dataTipos?.tiposGrupo || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando grupos'
  } finally {
    loading.value = false
  }
}

function limpiarFiltros() {
  filters.value = { tipo: [], activo: [] }
  searchQuery.value = ''
}

async function eliminarGrupo(grupo) {
  try {
    await graphqlClient.request(ELIMINAR_GRUPO, { id: grupo.id })
    grupos.value = grupos.value.filter(g => g.id !== grupo.id)
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error eliminando grupo')
  }
}

function getTipoClass(nombre) {
  if (!nombre) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
  const n = nombre.toUpperCase()
  if (n.includes('PERMANENTE')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800'
  if (n.includes('TEMPORAL')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800'
  return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', { month: 'short', year: 'numeric' })
}

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso.
onActivated(cargar)
</script>
