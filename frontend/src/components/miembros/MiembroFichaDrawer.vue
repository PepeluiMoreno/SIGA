<template>
  <AppDrawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="titulo || 'Ficha de socio'"
    :subtitle="subtitulo"
    size="xl"
  >
    <!-- Se remonta en cada apertura (v-if) y al cambiar de socio (:key) para que
         la ficha cargue los datos del id actual. -->
    <MiembroDetail
      v-if="modelValue && miembroId"
      :key="miembroId"
      :miembro-id-prop="miembroId"
      embebido
      :editar-inicial="editarInicial"
    />
  </AppDrawer>
</template>

<script setup>
import AppDrawer from '@/components/common/AppDrawer.vue'
import MiembroDetail from '@/components/miembros/MiembroDetail.vue'

defineProps({
  modelValue: { type: Boolean, default: false },
  miembroId: { type: String, default: null },
  editarInicial: { type: Boolean, default: false },
  titulo: { type: String, default: '' },
  subtitulo: { type: String, default: '' },
})
defineEmits(['update:modelValue'])
</script>
