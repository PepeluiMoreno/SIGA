<template>
  <AppLayout title="Parametrización" subtitle="Configuración de catálogos del sistema">
    <!-- Navegación por categorías -->
    <div class="mb-6">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="categoria in categorias"
          :key="categoria.id"
          @click="categoriaActiva = categoria.id"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            categoriaActiva === categoria.id
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ categoria.nombre }}
        </button>
      </div>
    </div>

    <!-- Grid de catálogos -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <router-link
        v-for="catalogo in catalogosFiltrados"
        :key="catalogo.ruta"
        :to="catalogo.ruta"
        class="block bg-white rounded-lg shadow border border-gray-200 p-5 hover:shadow-md hover:border-purple-300 transition-all"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ catalogo.nombre }}</h3>
            <p class="text-sm text-gray-500 mt-1">{{ catalogo.descripcion }}</p>
          </div>
          <span class="text-2xl">{{ catalogo.icono }}</span>
        </div>
        <div class="mt-4 flex items-center text-sm text-purple-600">
          <span>Gestionar</span>
          <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </div>
      </router-link>
    </div>

    <!-- Información adicional -->
    <div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-blue-800">Información</h3>
          <p class="text-sm text-blue-700 mt-1">
            Los catálogos definen los valores predeterminados del sistema.
            Modificar estos valores puede afectar el funcionamiento de otras partes de la aplicación.
          </p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'

const categoriaActiva = ref('Miembros')

const categorias = [
  { id: 'Miembros', nombre: 'Miembros' },
  { id: 'financiero', nombre: 'Financiero' },
  { id: 'campanias', nombre: 'Campañas' },
  { id: 'actividades', nombre: 'Actividades' },
  { id: 'grupos', nombre: 'Grupos' },
  { id: 'geografico', nombre: 'Geográfico' },
]

const catalogos = [
  // Miembros
  {
    categoria: 'Miembros',
    nombre: 'Tipos de miembro',
    descripcion: 'miembro, Simpatizante, Voluntario, etc.',
    icono: '👤',
    ruta: '/parametrizacion/tipos-miembro'
  },
  {
    categoria: 'Miembros',
    nombre: 'Situaciones',
    descripcion: 'Situaciones por las que pasa un miembro',
    icono: '📊',
    ruta: '/parametrizacion/estados-miembro'
  },
  {
    categoria: 'Miembros',
    nombre: 'Motivos de Baja',
    descripcion: 'Razones para dar de baja a un miembro',
    icono: '📝',
    ruta: '/parametrizacion/motivos-baja'
  },

  // Financiero
  {
    categoria: 'financiero',
    nombre: 'Estados de Cuota',
    descripcion: 'Pendiente, Pagada, Vencida, etc.',
    icono: '💰',
    ruta: '/parametrizacion/estados-cuota'
  },
  {
    categoria: 'financiero',
    nombre: 'Estados de Donación',
    descripcion: 'Pendiente, Recibida, Certificada, etc.',
    icono: '🎁',
    ruta: '/parametrizacion/estados-donacion'
  },
  {
    categoria: 'financiero',
    nombre: 'Estados de Remesa',
    descripcion: 'Borrador, Enviada, Procesada, etc.',
    icono: '🏦',
    ruta: '/parametrizacion/estados-remesa'
  },
  {
    categoria: 'financiero',
    nombre: 'Conceptos de Donación',
    descripcion: 'Tipos de conceptos para donaciones',
    icono: '📋',
    ruta: '/parametrizacion/conceptos-donacion'
  },

  // Campañas
  {
    categoria: 'campanias',
    nombre: 'Tipos de Campaña',
    descripcion: 'Recaudación, Sensibilización, etc.',
    icono: '📢',
    ruta: '/parametrizacion/tipos-campania'
  },
  {
    categoria: 'campanias',
    nombre: 'Estados de Campaña',
    descripcion: 'Borrador, Activa, Finalizada, etc.',
    icono: '🚦',
    ruta: '/parametrizacion/estados-campania'
  },
  {
    categoria: 'campanias',
    nombre: 'Roles de Participante',
    descripcion: 'Coordinador, Voluntario, Donante, etc.',
    icono: '🎭',
    ruta: '/parametrizacion/roles-participante'
  },

  // Actividades
  {
    categoria: 'actividades',
    nombre: 'Tipos de Actividad',
    descripcion: 'Formación, Evento, Reunión, etc.',
    icono: '📅',
    ruta: '/parametrizacion/tipos-actividad'
  },
  {
    categoria: 'actividades',
    nombre: 'Estados de Actividad',
    descripcion: 'Propuesta, Aprobada, Completada, etc.',
    icono: '✅',
    ruta: '/parametrizacion/estados-actividad'
  },
  {
    categoria: 'actividades',
    nombre: 'Tipos de Recurso',
    descripcion: 'Material, Humano, Económico, etc.',
    icono: '📦',
    ruta: '/parametrizacion/tipos-recurso'
  },
  {
    categoria: 'actividades',
    nombre: 'Tipos de KPI',
    descripcion: 'Indicadores de rendimiento',
    icono: '📈',
    ruta: '/parametrizacion/tipos-kpi'
  },

  // Grupos
  {
    categoria: 'grupos',
    nombre: 'Tipos de Grupo',
    descripcion: 'Comisión, Equipo, Territorial, etc.',
    icono: '👥',
    ruta: '/parametrizacion/tipos-grupo'
  },
  {
    categoria: 'grupos',
    nombre: 'Roles de Grupo',
    descripcion: 'Coordinador, miembro, Invitado, etc.',
    icono: '🎖️',
    ruta: '/parametrizacion/roles-grupo'
  },

  // Geográfico
  {
    categoria: 'geografico',
    nombre: 'Países',
    descripcion: 'Catálogo de países',
    icono: '🌍',
    ruta: '/parametrizacion/paises'
  },
  {
    categoria: 'geografico',
    nombre: 'Provincias',
    descripcion: 'Provincias por país',
    icono: '🗺️',
    ruta: '/parametrizacion/provincias'
  },
  {
    categoria: 'geografico',
    nombre: 'Agrupaciones Territoriales',
    descripcion: 'Delegaciones y sedes',
    icono: '🏢',
    ruta: '/parametrizacion/agrupaciones'
  },
]

const catalogosFiltrados = computed(() => {
  return catalogos.filter(c => c.categoria === categoriaActiva.value)
})
</script>
