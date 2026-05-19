<template>
  <AppLayout title="Convenios y Delegaciones" subtitle="Acuerdos institucionales y poderes de representación">
    <div class="bg-white rounded-lg shadow border border-gray-200 p-8 text-center text-gray-500">
      <HandshakeIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700 mb-1">Módulo en desarrollo</p>
      <p class="text-sm">Gestión de Convenio y DelegacionFirma</p>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
// HandshakeIcon no existe en heroicons; usamos DocumentCheckIcon como sustituto
import { DocumentCheckIcon as HandshakeIcon } from '@heroicons/vue/24/outline'
</script>
