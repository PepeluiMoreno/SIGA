<template>
  <AppLayout title="Agrupaciones" subtitle="Estructura territorial de la organización" fluid>

    <!-- Resumen por nivel -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div
        v-for="nivel in nivelesResumen"
        :key="nivel.tipo"
        class="rounded-lg shadow p-4 border cursor-pointer transition-colors"
        :class="[nivel.bg, nivel.border, filters.nivel === nivel.tipo ? 'ring-2 ring-offset-1 ' + nivel.ring : '']"
        @click="filters.nivel = filters.nivel === nivel.tipo ? '' : nivel.tipo"
      >
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg flex items-center justify-center mr-3" :class="nivel.iconBg">
            <component :is="nivel.icon" class="w-5 h-5" :class="nivel.iconText" />
          </div>
          <div>
            <p class="text-xs text-gray-500">{{ nivel.label }}</p>
            <p class="text-xl font-bold" :class="nivel.textColor">{{ nivel.count }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Patrón de lista: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">
      <FilterRail storage-key="agrupaciones">
        <FilterBar
          vertical
          v-model="filters"
          v-model:search="busqueda"
          search-placeholder="Buscar por nombre o código…"
          :fields="filterFields"
          @clear="limpiarFiltros" />
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">
        <div class="flex items-center justify-end text-sm mb-3">
          <span class="text-slate-500">{{ agrupacionesFiltradas.length }} de {{ agrupaciones.length }} agrupaciones</span>
        </div>

        <!-- Loading / Error -->
        <EstadoCarga v-if="loading" mensaje="Cargando agrupaciones..." />

        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          {{ error }}
        </div>

        <!-- Tabla -->
        <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <ResponsiveTable
            :columnas="columnas"
            :filas="agrupacionesFiltradas"
            vacio-texto="No se encontraron agrupaciones con los filtros seleccionados.">

            <template #cell-agrupacion="{ fila: ag }">
              <div class="flex items-center">
                <div
                  class="h-9 w-9 rounded-lg flex items-center justify-center mr-3 flex-shrink-0"
                  :class="tipoConfig(ag.tipoUnidad).iconBg"
                >
                  <component :is="tipoConfig(ag.tipoUnidad).icon" class="w-4 h-4" :class="tipoConfig(ag.tipoUnidad).iconText" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ ag.nombre }}</p>
                  <p v-if="ag.nombreCorto && ag.nombreCorto !== ag.nombre" class="text-xs text-gray-500">{{ ag.nombreCorto }}</p>
                </div>
              </div>
            </template>

            <template #cell-tipo="{ fila: ag }">
              <span
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                :class="tipoConfig(ag.tipoUnidad).badge"
              >
                {{ tipoConfig(ag.tipoUnidad).label }}
              </span>
            </template>

            <template #cell-padre="{ fila: ag }">
              {{ nombrePadre(ag.agrupacionPadreId) || '—' }}
            </template>

            <template #cell-contacto="{ fila: ag }">
              <div class="text-sm text-gray-600 space-y-0.5">
                <div v-if="ag.email" class="flex items-center gap-1">
                  <EnvelopeIcon class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                  <a :href="'mailto:' + ag.email" class="hover:text-purple-600 hover:underline" @click.stop>{{ ag.email }}</a>
                </div>
                <div v-if="ag.telefono" class="flex items-center gap-1">
                  <PhoneIcon class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                  <span>{{ ag.telefono }}</span>
                </div>
                <span v-if="!ag.email && !ag.telefono" class="text-gray-400">—</span>
              </div>
            </template>

            <template #cell-estado="{ fila: ag }">
              <span
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                :class="ag.activo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
              >
                {{ ag.activo ? 'Activa' : 'Inactiva' }}
              </span>
            </template>

            <template #cell-acciones="{ fila: ag }">
              <div class="flex items-center justify-end gap-3">
                <router-link
                  :to="{ path: '/miembros', query: { agrupacion: ag.id } }"
                  class="inline-flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 font-medium"
                  :title="'Ver miembros de ' + ag.nombre"
                  @click.stop
                >
                  <span>{{ conteoMiembros(ag.id) }}</span>
                  <span class="hidden sm:inline">miembros</span>
                  <span>→</span>
                </router-link>
                <router-link
                  :to="`/agrupaciones/${ag.id}/junta`"
                  class="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium border border-indigo-200 rounded px-2 py-0.5 hover:bg-indigo-50 transition"
                  :title="`Gestionar ${orgConfig.organoGobierno}`"
                  @click.stop
                >
                  {{ orgConfig.OrganoGobierno }}
                </router-link>
              </div>
            </template>
          </ResponsiveTable>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onActivated } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import {
  MapPinIcon, WrenchScrewdriverIcon, GlobeAltIcon, BuildingOfficeIcon,
  BuildingOffice2Icon, Squares2X2Icon, EnvelopeIcon, PhoneIcon,
} from '@heroicons/vue/24/outline'
import EstadoCarga from '@/components/common/EstadoCarga.vue'

defineOptions({ name: 'ListaAgrupaciones' })

const orgConfig = useOrgConfigStore()

const QUERY = gql`
  query Agrupaciones {
    unidadesOrganizativas {
      id
      nombre
      nombreCorto
      tipoId
      tipoUnidad { id nombre naturaleza vinculo nivel }
      agrupacionPadreId
      email
      telefono
      web
      activo
    }
    miembros: socios {
      id
      agrupacionId
    }
  }
`

const TIPO_CONFIG = {
  TERRITORIAL:    { icon: MapPinIcon,            label: 'Territorial',    iconBg: 'bg-blue-100',   iconText: 'text-blue-600',   badge: 'bg-blue-100 text-blue-800',     bg: 'bg-blue-50',   border: 'border-blue-100',   textColor: 'text-blue-600',   ring: 'ring-blue-400'   },
  FUNCIONAL:      { icon: WrenchScrewdriverIcon, label: 'Funcional',      iconBg: 'bg-green-100',  iconText: 'text-green-600',  badge: 'bg-green-100 text-green-800',   bg: 'bg-green-50',  border: 'border-green-100',  textColor: 'text-green-600',  ring: 'ring-green-400'  },
  PROGRAMATICA:   { icon: GlobeAltIcon,          label: 'Programática',   iconBg: 'bg-purple-100', iconText: 'text-purple-600', badge: 'bg-purple-100 text-purple-800', bg: 'bg-purple-50', border: 'border-purple-100', textColor: 'text-purple-600', ring: 'ring-purple-400' },
  ADMINISTRATIVA: { icon: BuildingOfficeIcon,    label: 'Administrativa', iconBg: 'bg-gray-100',   iconText: 'text-gray-600',   badge: 'bg-gray-100 text-gray-800',     bg: 'bg-gray-50',   border: 'border-gray-100',   textColor: 'text-gray-600',   ring: 'ring-gray-400'   },
}
const DEFAULT_TIPO = { icon: Squares2X2Icon, label: 'Sin tipo', iconBg: 'bg-slate-100', iconText: 'text-slate-500', badge: 'bg-slate-100 text-slate-700', bg: 'bg-slate-50', border: 'border-slate-100', textColor: 'text-slate-600', ring: 'ring-slate-400' }

const NIVEL_LABELS = { 1: 'Nivel 1 - Nacional', 2: 'Nivel 2 - Regional', 3: 'Nivel 3 - Local' }

const loading = ref(false)
const error = ref('')
const agrupaciones = ref([])
const miembros = ref([])

const busqueda = ref('')
const filters = ref({ naturaleza: [], nivel: '', activo: ['true'] })

const columnas = [
  { key: 'agrupacion', label: 'Agrupación', anchoMax: 'none' },
  { key: 'tipo',       label: 'Tipo' },
  { key: 'padre',      label: 'Depende de', ocultaEnMovil: true },
  { key: 'contacto',   label: 'Contacto', ocultaEnMovil: true },
  { key: 'estado',     label: 'Estado' },
  { key: 'acciones',   label: 'Acciones', align: 'right', esAcciones: true },
]

const filterFields = computed(() => [
  {
    key: 'naturaleza',
    label: 'Naturaleza',
    type: 'multiselect',
    allLabel: 'Todas las naturalezas',
    options: [
      { value: 'TERRITORIAL',    label: 'Territorial' },
      { value: 'FUNCIONAL',      label: 'Funcional' },
      { value: 'PROGRAMATICA',   label: 'Programática' },
      { value: 'ADMINISTRATIVA', label: 'Administrativa' },
    ],
  },
  {
    key: 'nivel',
    label: 'Nivel',
    type: 'select',
    allLabel: 'Todos los niveles',
    options: [
      { value: '1', label: 'Nivel 1 - Nacional' },
      { value: '2', label: 'Nivel 2 - Regional' },
      { value: '3', label: 'Nivel 3 - Local' },
    ],
  },
  {
    key: 'activo',
    label: 'Estado',
    type: 'multiselect',
    allLabel: 'Todos',
    options: [
      { value: 'true',  label: 'Activas' },
      { value: 'false', label: 'Inactivas' },
    ],
    isActive: (val) => val?.length > 0 && val.length < 2,
  },
])

function tipoConfig(tipoUnidad) {
  if (!tipoUnidad) return DEFAULT_TIPO
  const cfg = TIPO_CONFIG[tipoUnidad.naturaleza] ?? DEFAULT_TIPO
  return { ...cfg, label: tipoUnidad.nombre }
}

const nivelesResumen = computed(() => {
  const conteo = { 1: 0, 2: 0, 3: 0, transversal: 0 }
  agrupaciones.value.forEach((a) => {
    if (!a.activo) return
    if (a.tipoUnidad?.nivel) conteo[a.tipoUnidad.nivel] = (conteo[a.tipoUnidad.nivel] || 0) + 1
    else if (a.tipoUnidad) conteo.transversal = (conteo.transversal || 0) + 1
  })
  return [
    { tipo: '1',           count: conteo[1],           label: 'Nivel 1',       icon: BuildingOffice2Icon,    iconBg: 'bg-purple-100', iconText: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-100', textColor: 'text-purple-600', ring: 'ring-purple-400' },
    { tipo: '2',           count: conteo[2],           label: 'Nivel 2',       icon: GlobeAltIcon,           iconBg: 'bg-blue-100',   iconText: 'text-blue-600',   bg: 'bg-blue-50',   border: 'border-blue-100',   textColor: 'text-blue-600',   ring: 'ring-blue-400'   },
    { tipo: '3',           count: conteo[3],           label: 'Nivel 3',       icon: MapPinIcon,             iconBg: 'bg-green-100',  iconText: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-100',  textColor: 'text-green-600',  ring: 'ring-green-400'  },
    { tipo: 'transversal', count: conteo.transversal,  label: 'Transversales', icon: WrenchScrewdriverIcon,  iconBg: 'bg-yellow-100', iconText: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-100', textColor: 'text-yellow-600', ring: 'ring-yellow-400' },
  ]
})

const agrupacionesFiltradas = computed(() => {
  let lista = [...agrupaciones.value]
  // 'activo' es multiselect: ['true','false'] (o vacío) muestra ambas; un solo
  // valor filtra activas o inactivas.
  const act = filters.value.activo
  if (act.length === 1) lista = lista.filter((a) => act.includes('true') ? a.activo : !a.activo)
  if (filters.value.naturaleza.length) lista = lista.filter((a) => filters.value.naturaleza.includes(a.tipoUnidad?.naturaleza))
  if (filters.value.nivel) lista = lista.filter((a) => String(a.tipoUnidad?.nivel) === filters.value.nivel)
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    lista = lista.filter((a) => a.nombre.toLowerCase().includes(q) || (a.nombreCorto || '').toLowerCase().includes(q))
  }
  lista.sort((a, b) => {
    const nA = a.tipoUnidad?.nivel || 0
    const nB = b.tipoUnidad?.nivel || 0
    const nivelDiff = nB - nA
    return nivelDiff !== 0 ? nivelDiff : a.nombre.localeCompare(b.nombre, 'es')
  })
  return lista
})

const agrupacionMap = computed(() => Object.fromEntries(agrupaciones.value.map((a) => [a.id, a])))

function nombrePadre(padreId) {
  if (!padreId) return null
  return agrupacionMap.value[padreId]?.nombre || null
}

function conteoMiembros(agrupacionId) {
  return miembros.value.filter((m) => m.agrupacionId === agrupacionId).length
}


function limpiarFiltros() {
  busqueda.value = ''
  filters.value = { naturaleza: [], nivel: '', activo: ['true'] }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(QUERY)
    agrupaciones.value = data.unidadesOrganizativas || []
    miembros.value = data.miembros || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando agrupaciones'
  } finally {
    loading.value = false
  }
}

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso,
// evitando mostrar datos obsoletos.
onActivated(cargar)
</script>
