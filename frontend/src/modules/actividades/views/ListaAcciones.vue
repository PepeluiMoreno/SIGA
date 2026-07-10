<template>
  <AppLayout title="Actividades" subtitle="Reuniones, asambleas, talleres y demás actividades de la organización" fluid>

    <!-- Acción principal en el topbar (estándar global) -->
    <template v-if="tienePermiso('ACTIVIDAD_CREAR')" #actions>
      <router-link to="/actividades/nueva"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nueva actividad
      </router-link>
    </template>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

      <FilterRail storage-key="acciones">
        <FilterBar
          vertical
          v-model="filtros"
          v-model:search="filtroNombre"
          search-placeholder="Buscar por nombre…"
          :fields="camposFiltro"
          @clear="limpiarFiltros"
        />
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">

        <div v-if="loading" class="py-12 text-center text-sm text-slate-400">Cargando…</div>

        <div v-else-if="!actividadesFiltradas.length" class="py-12 text-center text-sm text-slate-400">
          No hay actividades que mostrar.
        </div>

        <div v-else class="space-y-3">

          <!-- ── Acordeón 1: Actividades fuera de campaña (lista plana) ── -->
          <AccordionPanel title="Fuera de campaña" :count="actividadesSinCampania.length" :default-open="true">
            <div v-if="!actividadesSinCampania.length" class="px-5 py-8 text-center text-sm text-slate-400">
              Ninguna actividad fuera de campaña con estos filtros.
            </div>
            <ResponsiveTable
              v-else
              :columnas="columnas"
              :filas="actividadesSinCampania"
              :por-pagina="0"
              vacio-texto="Ninguna actividad fuera de campaña con estos filtros">
              <template #cell-nombre="{ fila: a }"><CeldaNombre :actividad="a" /></template>
              <template #cell-tipo="{ fila: a }">{{ a.tipoActividad?.nombre || '—' }}</template>
              <template #cell-caracter="{ fila: a }">{{ caracterLabel(a) }}</template>
              <template #cell-estado="{ fila: a }"><CeldaEstado :actividad="a" /></template>
              <template #cell-fecha="{ fila: a }">{{ a.fechaInicio || '—' }}</template>
              <template #cell-acciones="{ fila: a }">
                <RowActions
                  :show-view="true"
                  :show-edit="true"
                  confirm-title="¿Eliminar esta actividad?"
                  :confirm-text="`«${a.nombre}» será eliminada permanentemente.`"
                  @view="abrir(a)"
                  @edit="abrir(a)"
                  @delete="(opts) => eliminarActividad(a, opts)"
                />
              </template>
            </ResponsiveTable>
          </AccordionPanel>

          <!-- ── Acordeón 2: Actividades de campaña (árbol campaña → actividad) ── -->
          <AccordionPanel title="De campaña" :count="gruposCampania.length" :default-open="true">
            <div v-if="!gruposCampania.length" class="px-5 py-8 text-center text-sm text-slate-400">
              Ninguna actividad de campaña con estos filtros.
            </div>
            <div v-else class="divide-y divide-slate-100">
              <div v-for="grupo in gruposCampania" :key="grupo.campania.id">
                <!-- Cabecera de campaña (nivel 1 del árbol) — plegable -->
                <div class="bg-indigo-50/60 border-y border-indigo-100 cursor-pointer hover:bg-indigo-100/60 px-4 py-2"
                  @click="toggleCampania(grupo.campania.id)">
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
                </div>
                <!-- Actividades de la campaña (nivel 2 del árbol) -->
                <ResponsiveTable
                  v-show="!estaColapsada(grupo.campania.id)"
                  :columnas="columnas"
                  :filas="grupo.actividades"
                  :por-pagina="0"
                  vacio-texto="Sin actividades">
                  <template #cell-nombre="{ fila: a }"><CeldaNombre :actividad="a" indent /></template>
                  <template #cell-tipo="{ fila: a }">{{ a.tipoActividad?.nombre || '—' }}</template>
                  <template #cell-caracter="{ fila: a }">{{ caracterLabel(a) }}</template>
                  <template #cell-estado="{ fila: a }"><CeldaEstado :actividad="a" /></template>
                  <template #cell-fecha="{ fila: a }">{{ a.fechaInicio || '—' }}</template>
                  <template #cell-acciones="{ fila: a }">
                    <RowActions
                      :show-view="true"
                      :show-edit="true"
                      confirm-title="¿Eliminar esta actividad?"
                      :confirm-text="`«${a.nombre}» será eliminada permanentemente.`"
                      @view="abrir(a)"
                      @edit="abrir(a)"
                      @delete="(opts) => eliminarActividad(a, opts)"
                    />
                  </template>
                </ResponsiveTable>
              </div>
            </div>
          </AccordionPanel>

        </div>
      </div><!-- /columna de resultados -->
    </div><!-- /layout -->
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, h, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import RowActions from '@/components/common/RowActions.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import { FolderIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import { graphqlClient } from '@/graphql/client'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_ACCIONES, GET_TIPOS_ACCION, GET_ESTADOS_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION } from '../graphql/queries.js'

defineOptions({ name: 'ListaAcciones' })

const toast = useToast()
const router = useRouter()

const { tienePermiso } = usePermisos()
const loading = ref(true)
const actividades = ref([])
const tiposActividad = ref([])
const estadosAccion = ref([])

const filtroNombre = ref('')
const filtros = ref({ ejercicio: [], caracter: [], estado: [], tipo: [] })

const columnas = [
  { key: 'nombre',   label: 'Nombre',   ordenable: true, valorOrden: a => a.nombre },
  { key: 'tipo',     label: 'Tipo',     ordenable: true, valorOrden: a => a.tipoActividad?.nombre },
  { key: 'caracter', label: 'Carácter', ordenable: true, valorOrden: a => a.caracter },
  { key: 'estado',   label: 'Estado',   ordenable: true, valorOrden: a => a.estado?.nombre },
  { key: 'fecha',    label: 'Fecha',    ordenable: true, valorOrden: a => a.fechaInicio },
  { key: 'acciones', label: '',         align: 'right',  esAcciones: true },
]

const abrir = (a) => router.push(`/actividades/${a.id}`)

// Plantilla recurrente: caracter RECURRENTE sin padre. No es imputable y se marca.
const esPlantilla = (a) => a.caracter === 'RECURRENTE' && !a.padreId

function caracterLabel(a) {
  const c = a.caracter
  if (c === 'PERMANENTE') return 'Permanente'
  if (c === 'PUNTUAL') return 'Puntual'
  if (c === 'RECURRENTE') return esPlantilla(a) ? 'Recurrente (plantilla)' : 'Recurrente (instancia)'
  return '—'
}

// Celdas de render enriquecido (badge de plantilla / estado con color), en línea
// para poder pintarlas dentro de los slots de ResponsiveTable.
const CeldaNombre = (props) => h('div', { class: props.indent ? 'pl-6 font-medium text-slate-900' : 'font-medium text-slate-900' }, [
  props.actividad.nombre,
  esPlantilla(props.actividad)
    ? h('span', { class: 'ml-2 text-xs px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 align-middle' }, 'Plantilla')
    : null,
])
CeldaNombre.props = ['actividad', 'indent']

const CeldaEstado = (props) => {
  const e = props.actividad.estado
  if (!e) return h('span', { class: 'text-slate-400' }, '—')
  return h('span', {
    class: ['inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', !e.color ? 'bg-slate-100 text-slate-600' : ''],
    style: e.color ? `background-color: ${e.color}22; color: ${e.color}` : '',
  }, e.nombre)
}
CeldaEstado.props = ['actividad']

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

// Filtros con pocas opciones = multiselect (OR): p. ej. varios estados a la vez.
const camposFiltro = computed(() => [
  {
    key: 'ejercicio',
    label: 'Ejercicio',
    type: 'multiselect',
    allLabel: 'Todos los años',
    options: ejerciciosDisponibles.value.map(y => ({ value: y, label: y })),
  },
  {
    key: 'caracter',
    label: 'Carácter',
    type: 'multiselect',
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
    type: 'multiselect',
    allLabel: 'Todos los estados',
    options: estadosAccion.value.map(e => ({ value: e.id, label: e.nombre })),
  },
  {
    key: 'tipo',
    label: 'Tipo',
    type: 'multiselect',
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
  if (filtros.value.ejercicio.length) {
    list = list.filter(a => filtros.value.ejercicio.includes(String(a.fechaInicio || '').slice(0, 4)))
  }
  if (filtros.value.caracter.length) {
    list = list.filter(a => filtros.value.caracter.includes(a.caracter))
  }
  if (filtros.value.estado.length) {
    list = list.filter(a => filtros.value.estado.includes(a.estado?.id))
  }
  if (filtros.value.tipo.length) {
    list = list.filter(a => filtros.value.tipo.includes(a.tipoActividad?.id))
  }
  return list
})

function limpiarFiltros() {
  filtroNombre.value = ''
  filtros.value = { ejercicio: [], caracter: [], estado: [], tipo: [] }
}

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

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso,
// evitando mostrar datos obsoletos.
onActivated(cargar)
</script>
