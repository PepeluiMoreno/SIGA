<template>
  <AppLayout title="Estructura y órganos"
             subtitle="Niveles territoriales y el modelo de órganos de cada uno"
             fluid>
    <!-- El editor lo es todo: el árbol de niveles y, en cada tarjeta, sus datos y
         su modelo organizativo. La denominación de cada órgano vive en su tipo
         (catálogo de tipos de órgano), no en un parámetro suelto. -->
    <EstructuraOrganizativaEditor :mostrar-radiogroup="true" />
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import EstructuraOrganizativaEditor from '@/components/configuracion/EstructuraOrganizativaEditor.vue'

defineOptions({ name: 'EstructuraOrganizativa' })
</script>
