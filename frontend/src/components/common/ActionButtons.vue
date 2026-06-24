<template>
  <div class="flex items-center gap-2">
    <AppButton v-if="showBack" :to="backRoute" variant="secondary" :icon="ArrowLeftIcon">
      {{ backText }}
    </AppButton>

    <AppButton v-if="editRoute" :to="editRoute" variant="primary" :icon="PencilSquareIcon">
      {{ editText }}
    </AppButton>

    <AppButton v-if="showDelete" variant="danger" :icon="TrashIcon" @click="showConfirm = true">
      {{ deleteText }}
    </AppButton>

    <slot />
  </div>

  <ConfirmModal
    v-model="showConfirm"
    :title="confirmTitle"
    @confirm="(opts) => $emit('delete', opts)"
  />
</template>

<script setup>
import { ref } from 'vue'
import { ArrowLeftIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline'
import AppButton from './AppButton.vue'
import ConfirmModal from './ConfirmModal.vue'

defineProps({
  showBack:     { type: Boolean, default: true },
  backRoute:    { type: [String, Object], default: '/campanias' },
  backText:     { type: String, default: 'Volver' },
  editRoute:    { type: [String, Object], default: '' },
  editText:     { type: String, default: 'Editar' },
  showDelete:   { type: Boolean, default: false },
  deleteText:   { type: String, default: 'Eliminar' },
  confirmTitle: { type: String, default: '¿Eliminar este elemento?' },
})

defineEmits(['delete'])

const showConfirm = ref(false)
</script>
