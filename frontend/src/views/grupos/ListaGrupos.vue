<template>
  <AppLayout title="Grupos de Trabajo" subtitle="Gestión de grupos y equipos">
    <!-- Filtros y búsqueda -->
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar grupos..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              @input="onSearch"
            />
            <div class="absolute left-3 top-2.5">
              <span>🔍</span>
            </div>
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="showFilters = !showFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Filtros
          </button>
          <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            + Nuevo Grupo
          </button>
        </div>
      </div>

      <!-- Filtros avanzados -->
      <div v-if="showFilters" class="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="filters.tipo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todos</option>
              <option value="PERMANENTE">Permanente</option>
              <option value="TEMPORAL">Temporal</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select v-model="filters.activo" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todos</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ámbito</label>
            <select v-model="filters.ambito" class="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="">Todos</option>
              <option value="ESTATAL">Estatal</option>
              <option value="AUTONOMICO">Autonómico</option>
              <option value="LOCAL">Local</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600">Cargando grupos...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <span class="text-red-400">⚠️</span>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error al cargar grupos</h3>
          <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
        </div>
      </div>
    </div>

    <!-- Lista de grupos -->
    <div v-else class="space-y-4">
      <div v-if="grupos.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
          <span class="text-4xl">👥</span>
        </div>
        <h3 class="text-sm font-medium text-gray-900">No hay grupos</h3>
        <p class="text-sm text-gray-500 mt-1">Aún no hay grupos de trabajo registrados.</p>
      </div>

      <div
        v-for="grupo in grupos"
        :key="grupo.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">{{ grupo.nombre }}</h3>
                <span :class="getTipoClass(grupo.tipo)">{{ grupo.tipo }}</span>
                <span v-if="!grupo.activo" class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                  Inactivo
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-3">{{ grupo.descripcion }}</p>

              <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                <div class="flex items-center">
                  <span class="mr-1">👤</span>
                  <span>Coordinador: {{ grupo.coordinador }}</span>
                </div>
                <div class="flex items-center">
                  <span class="mr-1">👥</span>
                  <span>{{ grupo.numMiembros }} miembros</span>
                </div>
                <div class="flex items-center">
                  <span class="mr-1">📍</span>
                  <span>{{ grupo.ambito }}</span>
                </div>
                <div v-if="grupo.fechaCreacion" class="flex items-center">
                  <span class="mr-1">📅</span>
                  <span>Desde {{ formatDate(grupo.fechaCreacion) }}</span>
                </div>
              </div>
            </div>

            <div class="mt-4 md:mt-0 md:ml-6 flex space-x-2">
              <button @click="verMiembros(grupo)" class="px-3 py-2 text-sm text-purple-600 hover:text-purple-800 font-medium">
                Ver miembros
              </button>
              <button @click="editarGrupo(grupo)" class="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 font-medium">
                Editar
              </button>
            </div>
          </div>

          <!-- Miembros del grupo (preview) -->
          <div v-if="grupo.miembrosPreview && grupo.miembrosPreview.length > 0" class="mt-4 pt-4 border-t border-gray-100">
            <div class="flex items-center">
              <div class="flex -space-x-2">
                <div
                  v-for="(miembro, index) in grupo.miembrosPreview.slice(0, 5)"
                  :key="miembro.id"
                  class="h-8 w-8 rounded-full bg-purple-100 border-2 border-white flex items-center justify-center"
                  :title="miembro.nombre"
                >
                  <span class="text-xs font-medium text-purple-700">{{ miembro.iniciales }}</span>
                </div>
                <div
                  v-if="grupo.numMiembros > 5"
                  class="h-8 w-8 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center"
                >
                  <span class="text-xs font-medium text-gray-600">+{{ grupo.numMiembros - 5 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL.js'

const { loading, error, query } = useGraphQL()

const grupos = ref([])
const searchQuery = ref('')
const showFilters = ref(false)

const filters = ref({
  tipo: '',
  activo: '',
  ambito: ''
})

onMounted(() => {
  loadGrupos()
})

const loadGrupos = async () => {
  // Datos de ejemplo - reemplazar con datos reales de GraphQL
  grupos.value = [
    {
      id: 1,
      nombre: 'Comisión de Educación',
      descripcion: 'Grupo de trabajo dedicado al seguimiento de temas educativos y defensa de la escuela laica.',
      tipo: 'PERMANENTE',
      activo: true,
      coordinador: 'María García',
      numMiembros: 12,
      ambito: 'ESTATAL',
      fechaCreacion: '2020-03-15',
      miembrosPreview: [
        { id: 1, nombre: 'María García', iniciales: 'MG' },
        { id: 2, nombre: 'Juan Pérez', iniciales: 'JP' },
        { id: 3, nombre: 'Ana López', iniciales: 'AL' },
        { id: 4, nombre: 'Carlos Ruiz', iniciales: 'CR' },
        { id: 5, nombre: 'Laura Martín', iniciales: 'LM' }
      ]
    },
    {
      id: 2,
      nombre: 'Grupo de Comunicación',
      descripcion: 'Responsables de la comunicación externa, redes sociales y relaciones con medios.',
      tipo: 'PERMANENTE',
      activo: true,
      coordinador: 'Pedro Sánchez',
      numMiembros: 8,
      ambito: 'ESTATAL',
      fechaCreacion: '2019-06-01',
      miembrosPreview: [
        { id: 6, nombre: 'Pedro Sánchez', iniciales: 'PS' },
        { id: 7, nombre: 'Elena Torres', iniciales: 'ET' },
        { id: 8, nombre: 'David García', iniciales: 'DG' }
      ]
    },
    {
      id: 3,
      nombre: 'Comité Organizador Jornadas 2025',
      descripcion: 'Grupo temporal para la organización de las Jornadas Laicistas 2025.',
      tipo: 'TEMPORAL',
      activo: true,
      coordinador: 'Ana López',
      numMiembros: 6,
      ambito: 'ESTATAL',
      fechaCreacion: '2024-11-01',
      miembrosPreview: [
        { id: 3, nombre: 'Ana López', iniciales: 'AL' },
        { id: 9, nombre: 'Roberto Díaz', iniciales: 'RD' }
      ]
    },
    {
      id: 4,
      nombre: 'Grupo de Trabajo Madrid',
      descripcion: 'Coordinación de actividades y miembros en la Comunidad de Madrid.',
      tipo: 'PERMANENTE',
      activo: true,
      coordinador: 'Carmen Vega',
      numMiembros: 25,
      ambito: 'AUTONOMICO',
      fechaCreacion: '2018-01-15',
      miembrosPreview: [
        { id: 10, nombre: 'Carmen Vega', iniciales: 'CV' },
        { id: 11, nombre: 'Miguel Ángel', iniciales: 'MA' },
        { id: 12, nombre: 'Rosa Jiménez', iniciales: 'RJ' },
        { id: 13, nombre: 'Pablo Hernández', iniciales: 'PH' },
        { id: 14, nombre: 'Lucía Fernández', iniciales: 'LF' }
      ]
    }
  ]
}

const onSearch = () => {
  console.log('Buscando:', searchQuery.value)
}

const getTipoClass = (tipo) => {
  const classes = {
    'PERMANENTE': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    'TEMPORAL': 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800'
  }
  return classes[tipo] || 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', { month: 'short', year: 'numeric' })
}

const verMiembros = (grupo) => {
  console.log('Ver miembros:', grupo)
}

const editarGrupo = (grupo) => {
  console.log('Editar grupo:', grupo)
}

watch(filters, () => {
  loadGrupos()
}, { deep: true })
</script>
