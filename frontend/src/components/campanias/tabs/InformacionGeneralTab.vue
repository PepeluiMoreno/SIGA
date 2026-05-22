<template>
  <div class="space-y-8">
    <!-- Descripción -->
    <div>
      <h3 class="text-lg font-medium text-gray-900 mb-4">Descripción</h3>
      <div class="prose max-w-none">
        <p class="text-gray-700 whitespace-pre-line">{{ campania.descripcionLarga || 'No hay descripción disponible.' }}</p>
      </div>
    </div>

    <!-- Información clave -->
    <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Tipo y Responsable -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h4 class="font-medium text-gray-900 mb-3">Información General</h4>
        <div class="space-y-3">
          <div>
            <span class="text-sm text-gray-600">Tipo de campaña</span>
            <div class="mt-1 font-medium">{{ campania.tipoCampania?.nombre || 'No especificado' }}</div>
          </div>
          <div>
            <span class="text-sm text-gray-600">Estado</span>
            <div class="mt-1">
              <span :class="obtenerClaseEstado(campania.estado?.codigo)"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ campania.estado?.nombre || 'Sin estado' }}
              </span>
            </div>
          </div>
          <div>
            <span class="text-sm text-gray-600">Fecha inicio</span>
            <div class="mt-1 font-medium">{{ formatearFecha(campania.fechaInicioPlan) }}</div>
          </div>
          <div>
            <span class="text-sm text-gray-600">Fecha fin</span>
            <div class="mt-1 font-medium">{{ formatearFecha(campania.fechaFinPlan) }}</div>
          </div>
        </div>
      </div>

      <!-- Objetivos -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h4 class="font-medium text-gray-900 mb-3">Objetivos</h4>
        <div class="space-y-3">
          <div v-if="campania.metaRecaudacion">
            <span class="text-sm text-gray-600">Meta recaudación</span>
            <div class="mt-1 font-medium text-green-600">{{ formatearMoneda(campania.metaRecaudacion) }}</div>
          </div>
          <div v-if="campania.metaParticipantes">
            <span class="text-sm text-gray-600">Participantes objetivo</span>
            <div class="mt-1 font-medium">{{ campania.metaParticipantes }}</div>
          </div>
          <div v-if="campania.objetivoPrincipal">
            <span class="text-sm text-gray-600">Objetivo principal</span>
            <p class="mt-1 text-sm text-gray-700">{{ campania.objetivoPrincipal }}</p>
          </div>
        </div>
      </div>

      <!-- Coordinador/a -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h4 class="font-medium text-gray-900 mb-3">Coordinador/a</h4>
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
            {{ obtenerIniciales(nombreCompletoResponsable) }}
          </div>
          <div class="ml-3 flex-1">
            <p class="font-medium text-gray-900">{{ nombreCompletoResponsable }}</p>
            <p v-if="campania.responsable?.agrupacion?.nombre" class="text-sm text-gray-600">
              {{ campania.responsable.agrupacion.nombre }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Progreso de recaudación -->
    <div v-if="campania.metaRecaudacion" class="bg-green-50 p-4 rounded-lg border border-green-200">
      <h4 class="font-medium text-gray-900 mb-3">Progreso de Recaudación</h4>

      <!-- Total recaudado destacado -->
      <div class="text-center mb-4">
        <span class="text-3xl font-bold text-green-700">{{ formatearMoneda(campania.recaudacionActual || 0) }}</span>
        <span class="text-gray-600 ml-2">recaudados</span>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between text-sm text-gray-700">
          <span>Progreso</span>
          <span>Meta: {{ formatearMoneda(campania.metaRecaudacion) }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div
            class="bg-green-600 h-3 rounded-full transition-all duration-300"
            :style="{ width: Math.min(((campania.recaudacionActual || 0) / campania.metaRecaudacion) * 100, 100) + '%' }"
          ></div>
        </div>
        <div class="text-center text-sm font-medium text-green-700">
          {{ Math.round(((campania.recaudacionActual || 0) / campania.metaRecaudacion) * 100) }}% completado
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  campania: {
    type: Object,
    required: true
  }
})

// Computed para nombre completo del responsable
const nombreCompletoResponsable = computed(() => {
  if (!props.campania.responsable) return ''
  const { nombre, apellido1, apellido2 } = props.campania.responsable
  const apellidos = [apellido1, apellido2].filter(Boolean).join(' ')
  return apellidos ? `${nombre} ${apellidos}` : nombre
})

const obtenerClaseEstado = (codigo) => {
  if (codigo === 'ACTIVA') return 'bg-green-100 text-green-800'
  if (codigo === 'PLANIFICADA') return 'bg-blue-100 text-blue-800'
  if (codigo === 'FINALIZADA') return 'bg-gray-100 text-gray-800'
  if (codigo === 'CANCELADA') return 'bg-red-100 text-red-800'
  if (codigo === 'SUSPENDIDA') return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-800'
}

const formatearFecha = (fecha) => {
  if (!fecha) return ''
  return new Date(fecha).toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatearMoneda = (cantidad) => {
  if (!cantidad) return '0,00 €'
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR'
  }).format(cantidad)
}

const obtenerIniciales = (nombre) => {
  if (!nombre) return '??'
  return nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}
</script>
