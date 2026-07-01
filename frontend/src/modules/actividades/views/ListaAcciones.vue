<template>
  <AppLayout title="Actividades" subtitle="Reuniones, asambleas, talleres y demás actividades de la organización">

    <FilterBar
      v-model="filtros"
      v-model:search="filtroNombre"
      search-placeholder="Buscar por nombre…"
      :create-label="tienePermiso('ACTIVIDAD_CREAR') ? 'Nueva actividad' : ''"
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
        <div v-else class="overflow-x-auto -mx-1"><table class="w-full text-sm">
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
            <FilaActividad
              v-for="a in actividadesSinCampania"
              :key="a.id"
              :actividad="a"
              @delete="(opts) => eliminarActividad(a, opts)"
            />
          </tbody>
        </table></div>
      </AccordionPanel>

      <!-- ── Acordeón 2: Actividades de campaña (árbol campaña → actividad) ── -->
      <AccordionPanel title="De campaña" :count="gruposCampania.length" :default-open="true">
        <div v-if="!gruposCampania.length" class="px-5 py-8 text-center text-sm text-slate-400">
          Ninguna actividad de campaña con estos filtros.
        </div>
        <div v-else class="overflow-x-auto -mx-1"><table class="w-full text-sm">
          <tbody v-for="grupo in gruposCampania" :key="grupo.campania.id" class="divide-y divide-slate-100">
            <!-- Cabecera de campaña (nivel 1 del árbol) — plegable -->
            <tr class="bg-indigo-50/60 border-y border-indigo-100 cursor-pointer hover:bg-indigo-100/60"
              @click="toggleCampania(grupo.campania.id)">
              <td colspan="6" class="px-4 py-2">
                <div class="flex items-center gap-2">
                  <ChevronDownIcon class="w-4 h-4 text-indigo-400 shrink-0 transition-transform"
                    :class="{ '-rotate-90': estaColapsada(grupo.campania.id) }" />
                  <FolderIcon class="w-4 h-4 text-indigo-500 shrink-0" />
                  <span class="font-semibold text-indigo-800">{{ grupo.campania.nombre }}</span>
                  <span v-if="grupo.campania.estado"
                    class="text-xs px-2 py-0.5 rounded-full bg-white border border-indigo-200 text-indigo-600">
                    {{ grupo.campania.estado.nombre }}
                  </span>
                  <span class="text-xs text-slate-400">· {{ grupo.actividades.length }} actividad(es)</span>
                </div>
              </td>
            </tr>
            <!-- Cabecera de columnas: DEBAJO del nombre de campaña, solo si está desplegada -->
            <tr v-show="!estaColapsada(grupo.campania.id)" class="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wide">
              <th class="pl-10 pr-4 py-2 text-left font-medium text-slate-500">Nombre</th>
              <th class="px-4 py-2 text-left font-medium text-slate-500">Tipo</th>
              <th class="px-4 py-2 text-left font-medium text-slate-500">Carácter</th>
              <th class="px-4 py-2 text-left font-medium text-slate-500">Estado</th>
              <th class="px-4 py-2 text-left font-medium text-slate-500">Fecha</th>
              <th class="px-4 py-2"></th>
            </tr>
            <!-- Actividades de la campaña (nivel 2 del árbol) -->
            <FilaActividad
              v-for="a in grupo.actividades"
              v-show="!estaColapsada(grupo.campania.id)"
              :key="a.id"
              :actividad="a"
              :indent="true"
              @delete="(opts) => eliminarActividad(a, opts)"
            />
          </tbody>
        </table></div>
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
import FilaActividad from './FilaActividad.vue'
import { FolderIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
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
const filtros = ref({ ejercicio: '', caracter: '', estado: '', tipo: '' })

// Ejercicios (años) disponibles según la fecha de inicio de las actividades
const ejerciciosDisponibles = computed(() => {
  const set = new Set()
  for (const a of actividades.value) {
    if (a.fechaInicio) set.add(String(a.fechaInicio).slice(0, 4))
  }
  return Array.from(set).sort((x, y) => y.localeCompare(x))
})

// Plegado de campañas en el árbol (nivel 1). Por defecto, todas plegadas;
// se expanden al hacer clic en la cabecera de campaña.
const expandidas = ref(new Set())
const estaColapsada = (id) => !expandidas.value.has(id)
function toggleCampania(id) {
  const s = new Set(expandidas.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expandidas.value = s
}

const camposFiltro = computed(() => [
  {
    key: 'ejercicio',
    label: 'Ejercicio',
    type: 'select',
    allLabel: 'Todos los años',
    options: ejerciciosDisponibles.value.map(y => ({ value: y, label: y })),
  },
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
  if (filtros.value.ejercicio) {
    list = list.filter(a => String(a.fechaInicio || '').slice(0, 4) === filtros.value.ejercicio)
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

// Orden: de más reciente a más antigua (por fecha de inicio); sin fecha al final,
// desempatando por nombre.
const ordenarRecientes = (arr) =>
  arr.slice().sort((a, b) => {
    const fa = String(a.fechaInicio || ''), fb = String(b.fechaInicio || '')
    if (fa !== fb) return fb.localeCompare(fa)
    return (a.nombre || '').localeCompare(b.nombre || '', 'es')
  })

// Acordeón 1: sin campaña, lista plana (reciente → antigua)
const actividadesSinCampania = computed(() =>
  ordenarRecientes(actividadesFiltradas.value.filter(a => !a.campaniaId))
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
    .map(g => ({ campania: g.campania, actividades: ordenarRecientes(g.actividades) }))
    // Grupos ordenados por la actividad más reciente de cada campaña (reciente → antigua)
    .sort((x, y) => String(y.actividades[0]?.fechaInicio || '').localeCompare(String(x.actividades[0]?.fechaInicio || '')))
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
