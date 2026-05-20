<template>
  <DebugPanel />
  <router-view v-slot="{ Component }">
    <keep-alive :include="['DetalleAgrupacionesTerritoriales','ListaMiembros','ListaUsuarios','ListaRoles','ListaEventos','ListaGrupos','ListaCampanias','ListaVoluntarios','ListaTransacciones','Tesoreria','Contabilidad','Remesas','Donaciones']">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>

<script setup>
import DebugPanel from '@/components/common/DebugPanel.vue'
</script>
