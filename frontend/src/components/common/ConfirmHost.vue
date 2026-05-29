<template>
  <ConfirmActionModal
    v-model="_confirmState.visible"
    :titulo="_confirmState.titulo"
    :mensaje="_confirmState.mensaje"
    :variante="_confirmState.variante"
    :etiquetaConfirmar="_confirmState.etiquetaConfirmar"
    :etiquetaCancelar="_confirmState.etiquetaCancelar"
    :input="_confirmState.input"
    :input-value="_confirmState.inputValue"
    @update:input-value="v => _confirmState.inputValue = v"
    @confirm="_resolveConfirm(true)"
    @cancel="_resolveConfirm(false)"
  />
</template>

<script setup>
import ConfirmActionModal from './ConfirmActionModal.vue'
import { _confirmState, _resolveConfirm } from '@/composables/useConfirm'
</script>
