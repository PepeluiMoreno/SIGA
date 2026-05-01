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
          <div v-if="ultimasCampanias.length === 0" class="text-sm text-gray-500 py-4 text-center">Sin campañas registradas</div>
          <div v-for="campania in ultimasCampanias" :key="campania.id" class="border-l-4 border-purple-500 pl-4 py-2">
            <h4 class="font-medium text-gray-900">{{ campania.nombre }}</h4>
            <p class="text-sm text-gray-600">{{ campania.descripcion }}</p>
            <div class="flex items-center text-sm text-gray-500 mt-1">
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
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_CAMPANIAS } from '@/graphql/queries/campanias.js'
import { GET_GRUPOS } from '@/graphql/queries/grupos.js'
import { GET_MIEMBROS } from '@/graphql/queries/miembros.js'

const campanias = ref([])
const miembros = ref([])
const grupos = ref([])

const ultimasCampanias = computed(() => campanias.value.slice(0, 3).map(c => ({
  id: c.id,
  nombre: c.nombre,
  descripcion: c.descripcionCorta || c.lema || '',
  estado: c.estado?.nombre || '—',
  estadoClass: estadoClass(c.estado?.nombre),
})))

const stats = computed(() => ({
  totalmiembros: miembros.value.length,
  nuevosmiembrosMes: 0,
  campaniasActivas: campanias.value.filter(c => c.estado?.nombre?.toLowerCase().includes('activ')).length,
  campaniasPlanificadas: campanias.value.filter(c => c.estado?.nombre?.toLowerCase().includes('planif')).length,
  gruposActivos: grupos.value.filter(g => g.activo).length,
  gruposPermanentes: grupos.value.filter(g => g.activo).length,
  cuotasMes: 0,
  porcentajeCobro: 0,
}))

const presupuesto = ref({ total: 0, ejecutado: 0, porcentaje: 0 })
const actividadReciente = ref([])
const proximasActividades = ref([])

function estadoClass(nombre) {
  if (!nombre) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
  const n = nombre.toLowerCase()
  if (n.includes('activ')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  if (n.includes('planif')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800'
  if (n.includes('finaliz') || n.includes('cerrad')) return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'
  return 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800'
}

async function cargar() {
  const [dataCampanias, dataMiembros, dataGrupos] = await Promise.all([
    executeQuery(GET_CAMPANIAS).catch(() => ({ campanias: [] })),
    executeQuery(GET_MIEMBROS).catch(() => ({ miembros: [] })),
    executeQuery(GET_GRUPOS).catch(() => ({ gruposTrabajo: [] })),
  ])
  campanias.value = dataCampanias.campanias || []
  miembros.value = dataMiembros.miembros || []
  grupos.value = dataGrupos.gruposTrabajo || []
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(amount)
}

onMounted(cargar)
</script>
