<template>
  <AppLayout title="Actividades" subtitle="Reuniones, asambleas, talleres y demás actividades de la organización">

    <FilterBar
      v-model="filtros"
      v-model:search="filtroNombre"
      search-placeholder="Buscar por nombre…"
      :create-label="tienePermiso('ACT_CREATE') ? 'Nueva actividad' : ''"
      create-route="/actividades/nueva"
      :fields="camposFiltro"
      :count-text="`${actividadesFiltradas.length} de ${actividades.length}`"
    />

    <div v-if="loading" class="py-12 text-center text-sm text-slate-400">Cargando…</div>

    <div v-else-if="!actividadesFiltradas.length" class="py-12 text-center text-sm text-slate-400">
      No hay actividades que mostrar.
    </div>

    <div v-else class="space-y-3 mt-3">

      <!-- ── Acordeón 1: Actividades fuera de campaña (lista plana) ── -->
      <AccordionPanel title="Fuera de campaña" :count="actividadesSinCampania.length" :default-open="true">
        <div v-if="!actividadesSinCampania.length" class="px-5 py-8 text-center text-sm text-slate-400">
          Ninguna actividad fuera de campaña con estos filtros.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Nombre</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Tipo</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Carácter</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Estado</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Fecha</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <ActividadRow
              v-for="a in actividadesSinCampania"
              :key="a.id"
              :actividad="a"
              @delete="(opts) => eliminarActividad(a, opts)"
            />
          </tbody>
        </table>
      </AccordionPanel>

      <!-- ── Acordeón 2: Actividades de campaña (árbol campaña → actividad) ── -->
      <AccordionPanel title="De campaña" :count="gruposCampania.length" :default-open="true">
        <div v-if="!gruposCampania.length" class="px-5 py-8 text-center text-sm text-slate-400">
          Ninguna actividad de campaña con estos filtros.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Nombre</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Tipo</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Carácter</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Estado</th>
              <th class="px-4 py-3 text-left font-medium text-slate-600">Fecha</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody v-for="grupo in gruposCampania" :key="grupo.campania.id" class="divide-y divide-slate-100">
            <!-- Cabecera de campaña (nivel 1 del árbol) -->
            <tr class="bg-indigo-50/60 border-y border-indigo-100">
              <td colspan="6" class="px-4 py-2">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-indigo-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                  </svg>
                  <span class="font-semibold text-indigo-800">{{ grupo.campania.nombre }}</span>
                  <span v-if="grupo.campania.estado"
                    class="text-xs px-2 py-0.5 rounded-full bg-white border border-indigo-200 text-indigo-600">
                    {{ grupo.campania.estado.nombre }}
                  </span>
                  <span class="text-xs text-slate-400">· {{ grupo.actividades.length }} actividad(es)</span>
                </div>
              </td>
            </tr>
            <!-- Actividades de la campaña (nivel 2 del árbol) -->
            <ActividadRow
              v-for="a in grupo.actividades"
              :key="a.id"
              :actividad="a"
              :indent="true"
              @delete="(opts) => eliminarActividad(a, opts)"
            />
          </tbody>
        </table>
      </AccordionPanel>

    </div>
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import ActividadRow from './ActividadRow.vue'
import { graphqlClient } from '@/graphql/client'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_ACCIONES, GET_TIPOS_ACCION, GET_ESTADOS_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION } from '../graphql/queries.js'
const toast = useToast()

const { tienePermiso } = usePermisos()
const loading = ref(true)
const actividades = ref([])
const tiposActividad = ref([])
const estadosAccion = ref([])

const filtroNombre = ref('')
const filtros = ref({ caracter: '', estado: '', tipo: '' })

const camposFiltro = computed(() => [
  {
    key: 'caracter',
    label: 'Carácter',
    type: 'select',
    allLabel: 'Todos los caracteres',
    options: [
      { value: 'PERMANENTE', label: 'Permanente' },
      { value: 'PUNTUAL',    label: 'Puntual' },
      { value: 'RECURRENTE', label: 'Recurrente' },
    ],
  },
  {
    key: 'estado',
    label: 'Estado',
    type: 'select',
    allLabel: 'Todos los estados',
    options: estadosAccion.value.map(e => ({ value: e.id, label: e.nombre })),
  },
  {
    key: 'tipo',
    label: 'Tipo',
    type: 'select',
    allLabel: 'Todos los tipos',
    options: tiposActividad.value.map(t => ({ value: t.id, label: t.nombre })),
  },
])

const actividadesFiltradas = computed(() => {
  let list = actividades.value
  if (filtroNombre.value) {
    const q = filtroNombre.value.toLowerCase()
    list = list.filter(a => (a.nombre || '').toLowerCase().includes(q))
  }
  if (filtros.value.caracter) {
    list = list.filter(a => a.caracter === filtros.value.caracter)
  }
  if (filtros.value.estado) {
    list = list.filter(a => a.estado?.id === filtros.value.estado)
  }
  if (filtros.value.tipo) {
    list = list.filter(a => a.tipoActividad?.id === filtros.value.tipo)
  }
  return list
})

const ordenarPorNombre = (arr) =>
  arr.slice().sort((a, b) => (a.nombre || '').localeCompare(b.nombre || '', 'es'))

// Acordeón 1: sin campaña, lista plana alfabética
const actividadesSinCampania = computed(() =>
  ordenarPorNombre(actividadesFiltradas.value.filter(a => !a.campaniaId))
)

// Acordeón 2: agrupadas por campaña (árbol de dos niveles)
const gruposCampania = computed(() => {
  const mapa = new Map()
  for (const a of actividadesFiltradas.value) {
    if (!a.campaniaId) continue
    const camp = a.campania || { id: a.campaniaId, nombre: 'Campaña sin nombre' }
    if (!mapa.has(camp.id)) mapa.set(camp.id, { campania: camp, actividades: [] })
    mapa.get(camp.id).actividades.push(a)
  }
  return Array.from(mapa.values())
    .map(g => ({ campania: g.campania, actividades: ordenarPorNombre(g.actividades) }))
    .sort((x, y) => (x.campania.nombre || '').localeCompare(y.campania.nombre || '', 'es'))
})

async function cargar() {
  loading.value = true
  try {
    const [rActividades, rTipos, rEstados] = await Promise.all([
      graphqlClient.request(GET_ACCIONES),
      graphqlClient.request(GET_TIPOS_ACCION),
      graphqlClient.request(GET_ESTADOS_ACCION),
    ])
    actividades.value = rActividades.actividades || []
    tiposActividad.value = rTipos.tiposActividad || []
    estadosAccion.value = rEstados.estadosAccion || []
  } finally {
    loading.value = false
  }
}

async function eliminarActividad(actividad, { hardDelete } = {}) {
  try {
    if (hardDelete) {
      await graphqlClient.request(ELIMINAR_ACCION, { id: actividad.id })
    } else {
      await graphqlClient.request(SOFT_DELETE_ACCION, { id: actividad.id })
    }
    actividades.value = actividades.value.filter(a => a.id !== actividad.id)
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error eliminando actividad')
  }
}

onMounted(cargar)
</script>
