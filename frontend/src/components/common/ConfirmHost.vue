<template>
  <ConfirmActionModal
    v-model="_confirmState.value.visible"
    :titulo="_confirmState.value.titulo"
    :mensaje="_confirmState.value.mensaje"
    :variante="_confirmState.value.variante"
    :etiquetaConfirmar="_confirmState.value.etiquetaConfirmar"
    :etiquetaCancelar="_confirmState.value.etiquetaCancelar"
    @confirm="_resolveConfirm(true)"
    @cancel="_resolveConfirm(false)"
  />
</template>

<script setup>
import ConfirmActionModal from './ConfirmActionModal.vue'
import { _confirmState, _resolveConfirm } from '@/composables/useConfirm'
</script>
