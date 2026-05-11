<template>
  <AppLayout :title="isCreate ? 'Nuevo miembro' : 'Membresía'" :subtitle="isCreate ? 'Registrar un nuevo miembro en la organización' : 'Ficha detallada de miembro'">
    <MiembroDetail />
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import MiembroDetail from '@/components/miembros/MiembroDetail.vue'

const route = useRoute()
const isCreate = computed(() => route.name === 'NuevoMiembro')
</script>
