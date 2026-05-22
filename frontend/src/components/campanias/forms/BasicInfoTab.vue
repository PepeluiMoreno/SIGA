<template>
  <div class="space-y-6">
    <!-- Información básica -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Información básica</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Código *
          </label>
          <input
            v-model="campania.codigo"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Ej: CAMP-2025-001"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nombre *
          </label>
          <input
            v-model="campania.nombre"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Nombre de la campaña"
          />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descripción corta
        </label>
        <input
          v-model="campania.descripcion_corta"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="Breve descripción"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descripción completa
        </label>
        <textarea
          v-model="campania.descripcion_larga"
          rows="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="Descripción detallada de la campaña..."
        />
      </div>
    </div>

    <!-- Clasificación -->
    <div class="space-y-4 pt-6 border-t border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">Clasificación</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tipo de campaña *
          </label>
          <select
            v-model="campania.tipo_campania_id"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Seleccionar tipo</option>
            <option v-for="tipo in tiposCampania" :key="tipo.id" :value="tipo.id">
              {{ tipo.nombre }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Estado *
          </label>
          <select
            v-model="campania.estado_campania_id"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Seleccionar estado</option>
            <option value="1">Planificada</option>
            <option value="2">Activa</option>
            <option value="3">Finalizada</option>
            <option value="4">Cancelada</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Fechas -->
    <div class="space-y-4 pt-6 border-t border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">Fechas</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Fecha inicio planificada
          </label>
          <input
            v-model="campania.fecha_inicio_plan"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Fecha fin planificada
          </label>
          <input
            v-model="campania.fecha_fin_plan"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  campania: {
    type: Object,
    required: true
  },
  tiposCampania: {
    type: Array,
    default: () => []
  }
})

defineEmits(['update:campania'])
</script>