<template>
  <AppLayout title="Juntas Directivas" subtitle="Gestión de juntas directivas y cargos por agrupación">
    <div class="bg-white rounded-lg shadow border border-gray-200 p-8 text-center text-gray-500">
      <BuildingOffice2Icon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700 mb-1">Módulo en desarrollo</p>
      <p class="text-sm">Accede a la junta directiva de cada agrupación desde la vista de Agrupaciones.</p>
      <router-link to="/agrupaciones" class="mt-4 inline-block text-sm text-purple-600 hover:underline">
        Ir a Agrupaciones →
      </router-link>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import { BuildingOffice2Icon } from '@heroicons/vue/24/outline'
</script>
