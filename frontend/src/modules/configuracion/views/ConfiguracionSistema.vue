<template>
  <AppLayout title="Configuración del Sistema" subtitle="Parámetros globales de la aplicación">
    <div class="space-y-6">
      <!-- Identidad de la organización -->
      <div class="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <BuildingOffice2Icon class="w-5 h-5 text-purple-600" />
          Organización
        </h3>
        <div class="bg-gray-50 rounded p-4 text-sm text-gray-500 text-center">
          Módulo en desarrollo — nombre, tipo de organización, logotipo y datos de contacto.
        </div>
      </div>

      <!-- Modo de funcionamiento -->
      <div class="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <CogIcon class="w-5 h-5 text-purple-600" />
          Modo de funcionamiento
        </h3>
        <div class="bg-gray-50 rounded p-4 text-sm text-gray-500 text-center">
          Módulo en desarrollo — modo multiterritorial, feature flags (SIMPLE / COMPLETA), etc.
        </div>
      </div>

      <!-- Acceso rápido a catálogos -->
      <div class="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <ListBulletIcon class="w-5 h-5 text-purple-600" />
          Catálogos del sistema
        </h3>
        <router-link to="/parametrizacion/catalogos"
          class="text-sm text-purple-600 hover:underline">
          Gestionar catálogos (tipos, estados, motivos…) →
        </router-link>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import { BuildingOffice2Icon, CogIcon, ListBulletIcon } from '@heroicons/vue/24/outline'
</script>
