<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/40 backdrop-blur-sm"
        @click="$emit('update:modelValue', false)"
      />

      <!-- Modal -->
      <div class="relative bg-white rounded-xl shadow-xl max-w-sm w-full p-6">
        <!-- Icono -->
        <div
          class="flex items-center justify-center w-12 h-12 rounded-full mx-auto mb-4 transition-colors"
          :class="hardDelete ? 'bg-red-100' : 'bg-amber-100'"
        >
          <component
            :is="hardDelete ? ExclamationTriangleIcon : ArchiveBoxArrowDownIcon"
            class="w-6 h-6 transition-colors"
            :class="hardDelete ? 'text-red-600' : 'text-amber-600'"
          />
        </div>

        <!-- Título -->
        <h3 class="text-base font-semibold text-slate-900 text-center mb-1">
          {{ hardDelete ? title : titleSoft }}
        </h3>

        <!-- Mensaje -->
        <p class="text-sm text-center mb-4 transition-colors" :class="hardDelete ? 'text-slate-500' : 'text-slate-500'">
          <template v-if="hardDelete">
            {{ message || 'Esta operación no se puede deshacer.' }}
          </template>
          <template v-else>
            Se enviará a la <strong>papelera</strong> y podrá recuperarse más adelante.
          </template>
        </p>

        <!-- Toggle hard delete -->
        <label class="flex items-center gap-2.5 p-3 rounded-lg border cursor-pointer mb-5 transition-colors select-none"
          :class="hardDelete ? 'border-red-200 bg-red-50' : 'border-slate-200 bg-slate-50 hover:bg-slate-100'"
        >
          <input
            type="checkbox"
            v-model="hardDelete"
            class="w-4 h-4 accent-red-600 cursor-pointer"
          />
          <span class="text-xs font-medium" :class="hardDelete ? 'text-red-700' : 'text-slate-600'">
            Eliminar permanentemente (sin posibilidad de recuperación)
          </span>
        </label>

        <!-- Botones -->
        <div class="flex gap-3">
          <button
            type="button"
            class="flex-1 h-10 px-4 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="flex-1 h-10 px-4 text-sm font-medium text-white rounded-lg transition-colors"
            :class="hardDelete ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-500 hover:bg-amber-600'"
            @click="confirmar"
          >
            {{ hardDelete ? confirmLabel : 'Mover a papelera' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ExclamationTriangleIcon, ArchiveBoxArrowDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '¿Eliminar permanentemente?' },
  titleSoft: { type: String, default: '¿Mover a la papelera?' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Eliminar' },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const hardDelete = ref(false)

// Resetear a soft-delete cada vez que se abre el modal
watch(() => props.modelValue, (val) => {
  if (val) hardDelete.value = false
})

function confirmar() {
  emit('confirm', { hardDelete: hardDelete.value })
  emit('update:modelValue', false)
}
</script>
