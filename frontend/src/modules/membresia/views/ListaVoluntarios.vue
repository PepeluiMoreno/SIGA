<template>
  <AppLayout title="Voluntarios" subtitle="Gestión del voluntariado de Europa Laica">
    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">❤️</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total voluntarios</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">✅</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Disponibles</p>
            <p class="text-xl font-bold text-green-600">{{ resumen.disponibles }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">🚩</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">En campaña activa</p>
            <p class="text-xl font-bold text-blue-600">{{ resumen.enCampania }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar voluntarios…"
      :fields="filterFields"
      :lazy="true"
      :loading="loading"
      class="mb-6"
      @apply="aplicarFiltros"
    />

    <!-- Loading -->
    <EstadoCarga v-if="loading" mensaje="Cargando voluntarios..." />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <span class="text-red-400 mr-3">⚠️</span>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al cargar voluntarios</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Lista de voluntarios -->
    <div v-else class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-if="!filtersApplied" class="col-span-full bg-white rounded-lg shadow">
        <EstadoPendiente />
      </div>
      <div v-else-if="voluntariosFiltrados.length === 0" class="col-span-full text-center py-12 bg-white rounded-lg shadow">
        <span class="text-4xl">❤️</span>
        <h3 class="text-sm font-medium text-gray-900 mt-4">No hay voluntarios</h3>
        <p class="text-sm text-gray-500 mt-1">Prueba con otros filtros.</p>
      </div>

      <div
        v-for="v in voluntariosFiltrados"
        :key="v.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center">
              <div class="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                <span class="text-lg font-medium text-purple-700">{{ iniciales(v) }}</span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ nombreCompleto(v) }}</h3>
                <p v-if="v.profesion" class="text-sm text-gray-500">{{ v.profesion }}</p>
              </div>
            </div>
            <span v-if="v.disponibilidad" :class="getDisponibilidadClass(v.disponibilidad)">
              {{ v.disponibilidad }}
            </span>
          </div>

          <div class="space-y-2 text-sm text-gray-600 mb-4">
            <div v-if="v.email" class="flex items-center">
              <span class="mr-2">📧</span>
              <span>{{ v.email }}</span>
            </div>
            <div v-if="v.telefono" class="flex items-center">
              <span class="mr-2">📱</span>
              <span>{{ v.telefono }}</span>
            </div>
            <div v-if="v.horasDisponiblesSemana" class="flex items-center">
              <span class="mr-2">⏰</span>
              <span>{{ v.horasDisponiblesSemana }} h/semana disponibles</span>
            </div>
          </div>

          <div v-if="v.intereses" class="mb-4">
            <p class="text-xs text-gray-500 mb-1">Intereses:</p>
            <p class="text-sm text-gray-700">{{ v.intereses }}</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { executeQuery } from '@/graphql/client'
import { GET_VOLUNTARIOS } from '@/graphql/queries/voluntariado.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'

const loading = ref(false)
const error = ref('')
const voluntarios = ref([])
const searchQuery = ref('')
const filtersApplied = ref(false)
const filters = ref({ disponibilidad: '', activo: '' })

const filterFields = [
  {
    key: 'disponibilidad', label: 'Disponibilidad', type: 'select', allLabel: 'Cualquier disponibilidad',
    options: [
      { value: 'DISPONIBLE', label: 'Disponible' },
      { value: 'OCUPADO',    label: 'En campaña' },
      { value: 'INACTIVO',   label: 'Inactivo' },
    ],
  },
  {
    key: 'activo', label: 'Estado', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }],
    isActive: (v) => v !== '',
  },
]

const resumen = computed(() => ({
  total: voluntarios.value.length,
  disponibles: voluntarios.value.filter(v => v.disponibilidad === 'DISPONIBLE').length,
  enCampania: voluntarios.value.filter(v => v.disponibilidad === 'OCUPADO').length,
}))

const voluntariosFiltrados = computed(() => {
  let result = voluntarios.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(v =>
      v.nombre?.toLowerCase().includes(q) ||
      v.apellido1?.toLowerCase().includes(q) ||
      v.email?.toLowerCase().includes(q)
    )
  }
  if (filters.value.disponibilidad) {
    result = result.filter(v => v.disponibilidad === filters.value.disponibilidad)
  }
  if (filters.value.activo !== '') {
    result = result.filter(v => String(v.activo) === filters.value.activo)
  }
  return result
})

function iniciales(v) {
  return `${v.nombre?.[0] ?? ''}${v.apellido1?.[0] ?? ''}`.toUpperCase()
}

function nombreCompleto(v) {
  return [v.nombre, v.apellido1, v.apellido2].filter(Boolean).join(' ')
}

function getDisponibilidadClass(d) {
  const classes = {
    DISPONIBLE: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    OCUPADO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    INACTIVO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return classes[d] || classes.INACTIVO
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await executeQuery(GET_VOLUNTARIOS)
    voluntarios.value = data.voluntariosEnAmbito || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando voluntarios'
  } finally {
    loading.value = false
  }
}

async function aplicarFiltros() {
  await cargar()
  filtersApplied.value = true
}

onMounted(() => {})
</script>
