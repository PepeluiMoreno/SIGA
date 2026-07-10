<template>
  <DebugPanel />
  <router-view v-slot="{ Component }">
    <!-- Vistas de lista cacheadas: conservan scroll y filtros al volver de un
         detalle. El nombre debe coincidir con el `defineOptions({ name })` de la
         vista, o keep-alive no la reconoce. Toda vista de lista nueva va aquí. -->
    <keep-alive :include="['DetalleAgrupacionesTerritoriales','ListaContactos','ListaMiembros','ListaAgrupaciones','ListaUsuarios','ListaRoles','ListaTransacciones','LogAuditoria','ListaEventos','ListaGrupos','ListaAcciones','ListaCampanias','Tesoreria','Contabilidad','Remesas','Donaciones']">
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
