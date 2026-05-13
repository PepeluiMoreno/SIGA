<template>
  <div class="flex items-center gap-1 shrink-0">
    <button
      v-if="showView"
      type="button"
      @click.stop="$emit('view')"
      class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
      title="Ver detalle"
    >
      <EyeIcon class="w-4 h-4" />
    </button>
    <button
      v-if="showEdit"
      type="button"
      @click.stop="$emit('edit')"
      class="p-1.5 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-md transition-colors"
      title="Editar"
    >
      <PencilSquareIcon class="w-4 h-4" />
    </button>
    <button
      v-if="showDelete"
      type="button"
      @click.stop="showConfirm = true"
      class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
      title="Eliminar"
    >
      <TrashIcon class="w-4 h-4" />
    </button>
  </div>

  <ConfirmModal
    v-model="showConfirm"
    :title="confirmTitle"
    :title-soft="confirmTitleSoft"
    :message="confirmText"
    @confirm="(opts) => { $emit('delete', opts); showConfirm = false }"
  />
</template>

<script setup>
import { ref } from 'vue'
import { EyeIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline'
import ConfirmModal from './ConfirmModal.vue'

const props = defineProps({
  showView: { type: Boolean, default: false },
  showEdit: { type: Boolean, default: true },
  showDelete: { type: Boolean, default: true },
  confirmTitle: { type: String, default: '¿Eliminar permanentemente?' },
  confirmTitleSoft: { type: String, default: '¿Mover a la papelera?' },
  confirmText: { type: String, default: '' },
})

const emit = defineEmits(['view', 'edit', 'delete'])

const showConfirm = ref(false)
</script>
