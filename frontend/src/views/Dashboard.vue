<template>
  <AppLayout title="Dashboard" subtitle="Resumen general de Europa Laica">
    <!-- Estadísticas rápidas -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Miembros -->
      <div class="bg-purple-50 rounded-lg shadow p-6 border-l-4 border-purple-500 border border-purple-100">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center">
              <span class="text-2xl">👥</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total miembros</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalmiembros }}</p>
            <p class="text-sm text-green-600 mt-1">↑ {{ stats.nuevosmiembrosMes }} este mes</p>
          </div>
        </div>
      </div>

      <!-- Campañas -->
      <div class="bg-green-50 rounded-lg shadow p-6 border-l-4 border-green-500 border border-green-100">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center">
              <span class="text-2xl">🚩</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Campañas Activas</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.campaniasActivas }}</p>
            <p class="text-sm text-purple-600 mt-1">{{ stats.campaniasPlanificadas }} planificadas</p>
          </div>
        </div>
      </div>

      <!-- Grupos -->
      <div class="bg-blue-50 rounded-lg shadow p-6 border-l-4 border-blue-500 border border-blue-100">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <span class="text-2xl">👥</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Grupos de Trabajo</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.gruposActivos }}</p>
            <p class="text-sm text-gray-600 mt-1">{{ stats.gruposPermanentes }} permanentes</p>
          </div>
        </div>
      </div>

      <!-- Recaudación -->
      <div class="bg-yellow-50 rounded-lg shadow p-6 border-l-4 border-yellow-500 border border-yellow-100">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-yellow-100 flex items-center justify-center">
              <span class="text-2xl">💰</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Cuotas del Mes</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(stats.cuotasMes) }}</p>
            <p class="text-sm text-green-600 mt-1">↑ {{ stats.porcentajeCobro }}% cobrado</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Resumen de Presupuesto -->
    <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200 mb-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Ejecución Presupuestaria 2025</h3>
        <router-link to="/financiero" class="text-sm text-purple-600 hover:text-purple-800">
          Ver detalle →
        </router-link>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div class="text-center">
          <p class="text-sm text-gray-500">Presupuestado</p>
          <p class="text-xl font-bold text-gray-900">{{ formatCurrency(presupuesto.total) }}</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-500">Ejecutado</p>
          <p class="text-xl font-bold text-purple-600">{{ formatCurrency(presupuesto.ejecutado) }}</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-500">Disponible</p>
          <p class="text-xl font-bold text-green-600">{{ formatCurrency(presupuesto.total - presupuesto.ejecutado) }}</p>
        </div>
        <div class="text-center">
          <p class="text-sm text-gray-500">% Ejecutado</p>
          <p class="text-xl font-bold" :class="presupuesto.porcentaje > 80 ? 'text-red-600' : presupuesto.porcentaje > 60 ? 'text-yellow-600' : 'text-green-600'">
            {{ presupuesto.porcentaje }}%
          </p>
        </div>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-4">
        <div
          class="h-4 rounded-full transition-all duration-500"
          :class="presupuesto.porcentaje > 80 ? 'bg-red-500' : presupuesto.porcentaje > 60 ? 'bg-yellow-500' : 'bg-green-500'"
          :style="{ width: Math.min(presupuesto.porcentaje, 100) + '%' }"
        ></div>
      </div>
      <p class="text-xs text-gray-500 mt-2 text-center">
        Quedan {{ formatCurrency(presupuesto.total - presupuesto.ejecutado) }} del presupuesto anual
      </p>
    </div>

    <!-- Contenido principal -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- Últimas campañas -->
      <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Campañas de Europa Laica</h3>
          <router-link to="/campanias" class="text-sm text-purple-600 hover:text-purple-800">
            Ver todas →
          </router-link>
        </div>
        <div class="space-y-4">
          <div v-for="campania in ultimasCampanias" :key="campania.id" class="border-l-4 border-purple-500 pl-4 py-2">
            <h4 class="font-medium text-gray-900">{{ campania.nombre }}</h4>
            <p class="text-sm text-gray-600">{{ campania.descripcion }}</p>
            <div class="flex items-center text-sm text-gray-500 mt-1">
              <span class="mr-3">📅 {{ campania.fecha }}</span>
              <span :class="campania.estadoClass">{{ campania.estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actividad reciente -->
      <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Actividad Reciente</h3>
          <button class="text-sm text-purple-600 hover:text-purple-800">
            Ver más →
          </button>
        </div>
        <div class="space-y-3">
          <div v-for="actividad in actividadReciente" :key="actividad.id" class="flex items-start">
            <div class="flex-shrink-0 mr-3 mt-1">
              <div class="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <span class="text-sm text-purple-600">{{ actividad.iniciales }}</span>
              </div>
            </div>
            <div>
              <p class="text-sm text-gray-900">
                <span class="font-medium">{{ actividad.usuario }}</span> {{ actividad.accion }}
              </p>
              <p class="text-xs text-gray-500">{{ actividad.fecha }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Próximas actividades -->
    <div class="bg-gray-50 rounded-lg shadow p-6 border border-gray-200">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Próximas Actividades</h3>
        <button class="text-sm text-purple-600 hover:text-purple-800">
          Ver calendario →
        </button>
      </div>
      <div class="space-y-3">
        <div v-for="actividad in proximasActividades" :key="actividad.id" class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
          <div class="flex-shrink-0 mr-4">
            <div class="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center">
              <span class="text-purple-600">📅</span>
            </div>
          </div>
          <div class="flex-1">
            <h4 class="font-medium text-gray-900">{{ actividad.nombre }}</h4>
            <div class="flex items-center text-sm text-gray-500 mt-1">
              <span>📍 {{ actividad.lugar }}</span>
              <span class="mx-2">•</span>
              <span>🕒 {{ actividad.hora }}</span>
            </div>
            <div class="mt-2">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                {{ actividad.campania }}
              </span>
            </div>
          </div>
          <div>
            <button class="text-purple-600 hover:text-purple-800 text-sm font-medium">
              Ver detalles
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'

// Estadísticas
const stats = ref({
  totalmiembros: 1247,
  nuevosmiembrosMes: 23,
  campaniasActivas: 5,
  campaniasPlanificadas: 3,
  gruposActivos: 18,
  gruposPermanentes: 12,
  cuotasMes: 8450,
  porcentajeCobro: 87
})

// Presupuesto anual
const presupuesto = ref({
  total: 52000,
  ejecutado: 15280,
  porcentaje: 29
})

// Datos de ejemplo - campañas de Europa Laica
const ultimasCampanias = ref([
  {
    id: 1,
    nombre: 'Día Internacional del Laicismo 2025',
    descripcion: 'Celebración del 9 de diciembre con actos en toda España',
    fecha: '9 Dic 2025',
    estado: 'PLANIFICADA',
    estadoClass: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800'
  },
  {
    id: 2,
    nombre: 'Campaña "Religión fuera de la Escuela"',
    descripcion: 'Denuncia de la presencia de religión confesional en centros educativos públicos',
    fecha: 'Ene - Jun 2025',
    estado: 'ACTIVA',
    estadoClass: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  },
  {
    id: 3,
    nombre: 'Jornadas Laicistas 2025',
    descripcion: 'XII Jornadas de debate y reflexión sobre laicismo',
    fecha: '15-16 Mar 2025',
    estado: 'ACTIVA',
    estadoClass: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  }
])

const actividadReciente = ref([
  {
    id: 1,
    usuario: 'María García',
    iniciales: 'MG',
    accion: 'registró 5 nuevos miembros de Madrid',
    fecha: 'Hace 2 horas'
  },
  {
    id: 2,
    usuario: 'Juan Martínez',
    iniciales: 'JM',
    accion: 'creó la campaña "Apostasía Colectiva 2025"',
    fecha: 'Hace 4 horas'
  },
  {
    id: 3,
    usuario: 'Ana López',
    iniciales: 'AL',
    accion: 'generó remesa SEPA de cuotas enero',
    fecha: 'Hace 6 horas'
  },
  {
    id: 4,
    usuario: 'Carlos Ruiz',
    iniciales: 'CR',
    accion: 'publicó nota de prensa sobre laicidad',
    fecha: 'Hace 1 día'
  }
])

const proximasActividades = ref([
  {
    id: 1,
    nombre: 'Reunión Comisión de Educación',
    lugar: 'Sede Central Madrid',
    hora: '18:00 - 20:00',
    campania: 'Religión fuera de la Escuela'
  },
  {
    id: 2,
    nombre: 'Conferencia "Laicismo y Democracia"',
    lugar: 'Ateneo de Madrid',
    hora: '19:00 - 21:00',
    campania: 'Jornadas Laicistas'
  },
  {
    id: 3,
    nombre: 'Asamblea General Ordinaria',
    lugar: 'Online (Zoom)',
    hora: '11:00 - 14:00',
    campania: 'Institucional'
  }
])

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(amount)
}
</script>
