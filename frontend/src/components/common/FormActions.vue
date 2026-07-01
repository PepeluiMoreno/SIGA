<template>
  <div class="flex items-center gap-3">
    <!-- Mensaje de estado (error / guardado), a la izquierda de los botones -->
    <span v-if="error" class="flex items-center gap-1.5 text-xs text-red-600">
      <ExclamationTriangleIcon class="w-4 h-4 shrink-0" /> {{ error }}
    </span>
    <span v-else-if="ok" class="flex items-center gap-1.5 text-xs text-emerald-600">
      <CheckIcon class="w-4 h-4 shrink-0" /> {{ okText }}
    </span>

    <slot name="extra" />

    <!-- Secundaria (Cancelar / Volver) -->
    <button v-if="showCancel" type="button" @click="$emit('cancel')"
      class="h-8 px-3 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
      {{ cancelText }}
    </button>

    <!-- Primaria (Crear / Guardar) -->
    <button v-if="showSubmit" type="button" @click="$emit('submit')"
      :disabled="loading || disabled"
      class="inline-flex items-center gap-2 h-8 px-4 text-sm font-semibold text-white rounded-lg transition-colors disabled:opacity-50 shadow-sm"
      :class="submitClass">
      <span v-if="loading" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
      {{ loading ? loadingText : submitText }}
    </button>

    <slot />
  </div>
</template>

<script setup>
/**
 * FormActions — barra estándar de acciones de una vista, pensada para el slot
 * #actions de AppLayout (header, arriba a la derecha). Unifica Cancelar + acción
 * primaria + estado (error/guardado) con tamaños y colores consistentes.
 *
 * Ver feedback_acciones_arriba_derecha y feedback_profesionalidad_extrema.
 *
 * Uso:
 *   <template #actions>
 *     <FormActions :loading="guardando" :error="error"
 *       :submit-text="isCreate ? 'Crear socio' : 'Guardar cambios'"
 *       @cancel="cancelar" @submit="guardar" />
 *   </template>
 *
 * Slots: #extra (antes de los botones), default (después de la primaria).
 */
import { computed } from 'vue'
import { CheckIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  submitText:  { type: String, default: 'Guardar' },
  cancelText:  { type: String, default: 'Cancelar' },
  loadingText: { type: String, default: 'Guardando…' },
  loading:     { type: Boolean, default: false },
  disabled:    { type: Boolean, default: false },
  showSubmit:  { type: Boolean, default: true },
  showCancel:  { type: Boolean, default: true },
  error:       { type: String, default: '' },
  ok:          { type: Boolean, default: false },
  okText:      { type: String, default: 'Guardado' },
  // Color de la acción primaria: 'indigo' (por defecto) o 'green' para "crear".
  variant:     { type: String, default: 'indigo' },
})
defineEmits(['submit', 'cancel'])

const submitClass = computed(() =>
  props.variant === 'green'
    ? 'bg-green-600 hover:bg-green-700'
    : 'bg-indigo-600 hover:bg-indigo-700'
)
</script>
