<template>
  <div class="space-y-6">
    <!-- Indicadores de éxito -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Indicadores de Éxito</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Participantes -->
        <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Participantes Reales</span>
            <span class="text-2xl font-bold text-blue-700">{{ campania.participantes_reales || 0 }}</span>
          </div>
          <div v-if="campania.meta_participantes" class="mt-2">
            <div class="flex justify-between text-xs text-gray-600">
              <span>Meta: {{ campania.meta_participantes }}</span>
              <span>{{ calcularPorcentajeParticipantes() }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div
                class="bg-blue-600 h-2 rounded-full"
                :style="{ width: calcularPorcentajeParticipantes() + '%' }"
              ></div>
            </div>
          </div>
          <p v-else class="text-xs text-gray-500 mt-2">Sin meta definida</p>
        </div>
        
        <!-- Recaudación -->
        <div class="bg-green-50 p-4 rounded-lg border border-green-200">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Recaudación Real</span>
            <span class="text-2xl font-bold text-green-700">{{ formatearMoneda(campania.recaudacion_real || 0) }}</span>
          </div>
          <div v-if="campania.meta_recaudacion" class="mt-2">
            <div class="flex justify-between text-xs text-gray-600">
              <span>Meta: {{ formatearMoneda(campania.meta_recaudacion) }}</span>
              <span>{{ calcularPorcentajeRecaudacion() }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div
                class="bg-green-600 h-2 rounded-full"
                :style="{ width: calcularPorcentajeRecaudacion() + '%' }"
              ></div>
            </div>
          </div>
          <p v-else class="text-xs text-gray-500 mt-2">Sin meta definida</p>
        </div>
        
        <!-- Alcance -->
        <div class="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Alcance</span>
            <span class="text-2xl font-bold text-purple-700">{{ campania.alcance || 0 }}</span>
          </div>
          <p class="text-xs text-gray-500 mt-2">Personas impactadas</p>
        </div>
      </div>
    </div>

    <!-- Resultados cualitativos -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-3">Resultados Cualitativos</h4>
      <div class="bg-gray-50 p-4 rounded-lg">
        <p v-if="campania.resultados_cualitativos" class="text-gray-700 whitespace-pre-line">
          {{ campania.resultados_cualitativos }}
        </p>
        <p v-else class="text-gray-500 italic">No se han registrado resultados cualitativos.</p>
      </div>
    </div>

    <!-- Lecciones aprendidas -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-3">Lecciones Aprendidas</h4>
      <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <p v-if="campania.lecciones_aprendidas" class="text-gray-700 whitespace-pre-line">
          {{ campania.lecciones_aprendidas }}
        </p>
        <p v-else class="text-gray-500 italic">No se han registrado lecciones aprendidas.</p>
      </div>
    </div>

    <!-- Evaluación final -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-4">Evaluación Final</h4>
      
      <!-- Nivel de éxito -->
      <div v-if="campania.nivel_exito" class="space-y-3">
        <div>
          <span class="text-sm text-gray-600">Nivel de éxito (1-10)</span>
          <div class="flex items-center space-x-3 mt-2">
            <div class="flex-1">
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-purple-600 h-3 rounded-full"
                  :style="{ width: (campania.nivel_exito / 10) * 100 + '%' }"
                ></div>
              </div>
            </div>
            <span class="text-xl font-bold text-purple-600 min-w-[3rem] text-center">
              {{ campania.nivel_exito }}/10
            </span>
          </div>
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>Bajo</span>
            <span>Alto</span>
          </div>
        </div>
        
        <!-- Calificación -->
        <div class="flex items-center space-x-2 mt-4">
          <span class="text-sm text-gray-600">Calificación:</span>
          <div class="flex">
            <span
              v-for="n in 5"
              :key="n"
              class="text-2xl"
              :class="n <= Math.ceil(campania.nivel_exito / 2) ? 'text-yellow-500' : 'text-gray-300'"
            >
              ★
            </span>
          </div>
          <span class="text-sm text-gray-700 ml-2">
            {{ obtenerCalificacionTexto(campania.nivel_exito) }}
          </span>
        </div>
      </div>
      <p v-else class="text-gray-500 italic">No se ha evaluado el nivel de éxito.</p>

      <!-- Recomendaciones -->
      <div v-if="campania.recomendaciones" class="mt-6">
        <span class="text-sm text-gray-600">Recomendaciones para futuras campañas</span>
        <div class="bg-blue-50 p-4 rounded-lg border border-blue-200 mt-2">
          <p class="text-gray-700 whitespace-pre-line">{{ campania.recomendaciones }}</p>
        </div>
      </div>
    </div>

    <!-- Resumen ejecutivo -->
    <div class="pt-6 border-t border-gray-200">
      <h4 class="text-md font-medium text-gray-900 mb-3">Resumen Ejecutivo</h4>
      <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-gray-50 p-4 rounded-lg">
          <h5 class="font-medium text-gray-900 mb-2">Fortalezas</h5>
          <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
            <li>Alta participación de voluntarios</li>
            <li>Buena cobertura en medios</li>
            <li>Cumplimiento de cronograma</li>
          </ul>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-lg">
          <h5 class="font-medium text-gray-900 mb-2">Áreas de mejora</h5>
          <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
            <li>Mayor planificación de recursos</li>
            <li>Mejor seguimiento de objetivos</li>
            <li>Comunicación más frecuente</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  campania: {
    type: Object,
    required: true
  }
})

const formatearMoneda = (cantidad) => {
  if (!cantidad) return '€0.00'
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR'
  }).format(cantidad)
}

const calcularPorcentajeParticipantes = () => {
  if (!props.campania.meta_participantes) return 0
  const participantes = props.campania.participantes_reales || 0
  return Math.round((participantes / props.campania.meta_participantes) * 100)
}

const calcularPorcentajeRecaudacion = () => {
  if (!props.campania.meta_recaudacion) return 0
  const recaudado = props.campania.recaudacion_real || 0
  return Math.round((recaudado / props.campania.meta_recaudacion) * 100)
}

const obtenerCalificacionTexto = (nivel) => {
  if (nivel >= 9) return 'Excelente'
  if (nivel >= 7) return 'Muy bueno'
  if (nivel >= 5) return 'Aceptable'
  if (nivel >= 3) return 'Necesita mejorar'
  return 'Insuficiente'
}
</script>