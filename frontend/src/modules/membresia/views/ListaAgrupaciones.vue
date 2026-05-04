<template>
  <AppLayout title="Agrupaciones" subtitle="Estructura territorial de la organización">

    <!-- Resumen por nivel -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div
        v-for="nivel in nivelesResumen"
        :key="nivel.tipo"
        class="rounded-lg shadow p-4 border cursor-pointer transition-colors"
        :class="[nivel.bg, nivel.border, filtroTipo === nivel.tipo ? 'ring-2 ring-offset-1 ' + nivel.ring : '']"
        @click="toggleFiltroTipo(nivel.tipo)"
      >
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg flex items-center justify-center mr-3" :class="nivel.iconBg">
            <span class="text-lg">{{ nivel.icon }}</span>
          </div>
          <div>
            <p class="text-xs text-gray-500">{{ nivel.label }}</p>
            <p class="text-xl font-bold" :class="nivel.textColor">{{ nivel.count }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="mb-4 bg-white rounded-lg shadow p-4 border border-gray-100">
      <div class="flex flex-col md:flex-row md:items-center gap-3">
        <div class="flex-1">
          <input
            v-model="busqueda"
            type="text"
            placeholder="Buscar por nombre..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
          />
        </div>
        <select v-model="filtroActivo" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">Todas (activas e inactivas)</option>
          <option value="true">Solo activas</option>
          <option value="false">Solo inactivas</option>
        </select>
        <button
          v-if="filtroTipo || busqueda || filtroActivo"
          @click="limpiarFiltros"
          class="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Limpiar filtros
        </button>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600 text-sm">Cargando agrupaciones...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <!-- Tabla -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden border border-gray-100">
      <div v-if="agrupacionesFiltradas.length === 0" class="text-center py-12">
        <span class="text-4xl">🗺️</span>
        <h3 class="text-sm font-medium text-gray-900 mt-2">No hay agrupaciones</h3>
        <p class="text-sm text-gray-500 mt-1">No se encontraron agrupaciones con los filtros seleccionados.</p>
      </div>

      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agrupación</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Depende de</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Contacto</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Miembros</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="ag in agrupacionesFiltradas"
            :key="ag.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-6 py-4">
              <div class="flex items-center">
                <div
                  class="h-9 w-9 rounded-lg flex items-center justify-center mr-3 flex-shrink-0 text-base"
                  :class="tipoConfig(ag.tipo).iconBg"
                >
                  {{ tipoConfig(ag.tipo).icon }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ ag.nombre }}</p>
                  <p v-if="ag.nombreCorto && ag.nombreCorto !== ag.nombre" class="text-xs text-gray-500">{{ ag.nombreCorto }}</p>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                :class="tipoConfig(ag.tipo).badge"
              >
                {{ tipoConfig(ag.tipo).label }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 hidden md:table-cell">
              {{ nombrePadre(ag.agrupacionPadreId) || '—' }}
            </td>
            <td class="px-6 py-4 hidden lg:table-cell">
              <div class="text-sm text-gray-600 space-y-0.5">
                <div v-if="ag.email" class="flex items-center gap-1">
                  <span class="text-xs">✉️</span>
                  <a :href="'mailto:' + ag.email" class="hover:text-purple-600 hover:underline">{{ ag.email }}</a>
                </div>
                <div v-if="ag.telefono" class="flex items-center gap-1">
                  <span class="text-xs">📞</span>
                  <span>{{ ag.telefono }}</span>
                </div>
                <span v-if="!ag.email && !ag.telefono" class="text-gray-400">—</span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                :class="ag.activo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
              >
                {{ ag.activo ? 'Activa' : 'Inactiva' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
              <div class="flex items-center justify-end gap-3">
                <router-link
                  :to="{ path: '/miembros', query: { agrupacion: ag.id } }"
                  class="inline-flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 font-medium"
                  :title="'Ver miembros de ' + ag.nombre"
                >
                  <span>{{ conteoMiembros(ag.id) }}</span>
                  <span class="hidden sm:inline">miembros</span>
                  <span>→</span>
                </router-link>
                <router-link
                  :to="`/agrupaciones/${ag.id}/junta`"
                  class="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium border border-indigo-200 rounded px-2 py-0.5 hover:bg-indigo-50 transition"
                  title="Gestionar junta directiva"
                >
                  Junta
                </router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="agrupacionesFiltradas.length > 0" class="px-6 py-3 border-t border-gray-100 bg-gray-50 text-xs text-gray-500">
        Mostrando {{ agrupacionesFiltradas.length }} de {{ agrupaciones.length }} agrupaciones
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'

const QUERY = gql`
  query Agrupaciones {
    agrupacionesTerritoriales {
      id
      nombre
      nombreCorto
      tipo
      nivel
      agrupacionPadreId
      email
      telefono
      web
      activo
    }
    miembros {
      id
      agrupacionId
    }
  }
`

const TIPO_CONFIG = {
  NACIONAL:   { label: 'Nacional',    icon: '🏛️', iconBg: 'bg-purple-100', badge: 'bg-purple-100 text-purple-800', bg: 'bg-purple-50', border: 'border-purple-100', textColor: 'text-purple-600', ring: 'ring-purple-400' },
  AUTONOMICO: { label: 'Autonómica',  icon: '🌍', iconBg: 'bg-blue-100',   badge: 'bg-blue-100 text-blue-800',   bg: 'bg-blue-50',   border: 'border-blue-100',   textColor: 'text-blue-600',   ring: 'ring-blue-400' },
  PROVINCIAL: { label: 'Provincial',  icon: '📍', iconBg: 'bg-green-100',  badge: 'bg-green-100 text-green-800', bg: 'bg-green-50',  border: 'border-green-100',  textColor: 'text-green-600',  ring: 'ring-green-400' },
  LOCAL:      { label: 'Local',       icon: '📌', iconBg: 'bg-yellow-100', badge: 'bg-yellow-100 text-yellow-800', bg: 'bg-yellow-50', border: 'border-yellow-100', textColor: 'text-yellow-600', ring: 'ring-yellow-400' },
}

const TIPOS_ORDEN = ['NACIONAL', 'AUTONOMICO', 'PROVINCIAL', 'LOCAL']

const loading = ref(false)
const error = ref('')
const agrupaciones = ref([])
const miembros = ref([])

const busqueda = ref('')
const filtroTipo = ref('')
const filtroActivo = ref('true')

const tipoConfig = (tipo) => TIPO_CONFIG[tipo] || { label: tipo, icon: '🗂️', iconBg: 'bg-gray-100', badge: 'bg-gray-100 text-gray-700', bg: 'bg-gray-50', border: 'border-gray-100', textColor: 'text-gray-600', ring: 'ring-gray-400' }

const nivelesResumen = computed(() =>
  TIPOS_ORDEN.map((tipo) => ({
    tipo,
    count: agrupaciones.value.filter((a) => a.tipo === tipo && a.activo).length,
    ...tipoConfig(tipo),
  }))
)

const agrupacionesFiltradas = computed(() => {
  let lista = [...agrupaciones.value]
  if (filtroActivo.value === 'true') lista = lista.filter((a) => a.activo)
  if (filtroActivo.value === 'false') lista = lista.filter((a) => !a.activo)
  if (filtroTipo.value) lista = lista.filter((a) => a.tipo === filtroTipo.value)
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    lista = lista.filter((a) => a.nombre.toLowerCase().includes(q) || (a.nombreCorto || '').toLowerCase().includes(q))
  }
  // Ordenar: nivel descendente (Nacional primero), luego nombre
  lista.sort((a, b) => {
    const nivelDiff = (b.nivel || 0) - (a.nivel || 0)
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

function toggleFiltroTipo(tipo) {
  filtroTipo.value = filtroTipo.value === tipo ? '' : tipo
}

function limpiarFiltros() {
  busqueda.value = ''
  filtroTipo.value = ''
  filtroActivo.value = 'true'
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(QUERY)
    agrupaciones.value = data.agrupacionesTerritoriales || []
    miembros.value = data.miembros || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando agrupaciones'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
