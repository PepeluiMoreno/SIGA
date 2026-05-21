<template>
  <DebugPanel />
  <router-view v-slot="{ Component }">
    <keep-alive :include="['DetalleAgrupacionesTerritoriales','ListaMiembros','ListaUsuarios','ListaRoles','ListaEventos','ListaGrupos','ListaCampanias','ListaVoluntarios','ListaTransacciones','Tesoreria','Contabilidad','Remesas','Donaciones']">
      <component :is="Component" />
    </keep-alive>
  </router-view>

  <!-- Infraestructura global de UI — solo se monta una vez -->
  <ToastContainer />
  <ConfirmHost />
</template>

<script setup>
import DebugPanel      from '@/components/common/DebugPanel.vue'
import ToastContainer  from '@/components/common/ToastContainer.vue'
import ConfirmHost     from '@/components/common/ConfirmHost.vue'
</script>
