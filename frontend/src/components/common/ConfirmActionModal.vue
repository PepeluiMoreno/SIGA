<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/40 backdrop-blur-sm"
        @click="cancelar"
      />

      <!-- Modal -->
      <div class="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
        <!-- Icono -->
        <div
          class="flex items-center justify-center w-12 h-12 rounded-full mx-auto mb-4"
          :class="iconoFondo"
        >
          <component :is="iconoComp" class="w-6 h-6" :class="iconoColor" />
        </div>

        <!-- Título -->
        <h3 class="text-base font-semibold text-slate-900 text-center mb-2">
          {{ titulo }}
        </h3>

        <!-- Mensaje -->
        <p class="text-sm text-slate-600 text-center mb-5 leading-relaxed whitespace-pre-line">
          {{ mensaje }}
        </p>

        <!-- Botones -->
        <div class="flex gap-3">
          <button
            type="button"
            class="flex-1 h-10 px-4 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
            @click="cancelar"
          >
            {{ etiquetaCancelar }}
          </button>
          <button
            type="button"
            class="flex-1 h-10 px-4 text-sm font-medium text-white rounded-lg"
            :class="botonConfirmar"
            @click="confirmar"
          >
            {{ etiquetaConfirmar }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  LockClosedIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue:        { type: Boolean, default: false },
  titulo:            { type: String,  default: '¿Confirmar acción?' },
  mensaje:           { type: String,  default: '' },
  etiquetaConfirmar: { type: String,  default: 'Confirmar' },
  etiquetaCancelar:  { type: String,  default: 'Cancelar' },
  // 'primaria' (indigo, default) | 'aviso' (amber) | 'critica' (red) | 'exito' (green)
  variante:          { type: String,  default: 'primaria' },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const VARIANTES = {
  primaria: { fondo: 'bg-indigo-100', color: 'text-indigo-600', boton: 'bg-indigo-600 hover:bg-indigo-700', icon: InformationCircleIcon },
  aviso:    { fondo: 'bg-amber-100',  color: 'text-amber-600',  boton: 'bg-amber-500 hover:bg-amber-600',  icon: ExclamationTriangleIcon },
  critica:  { fondo: 'bg-red-100',    color: 'text-red-600',    boton: 'bg-red-600 hover:bg-red-700',      icon: LockClosedIcon },
  exito:    { fondo: 'bg-green-100',  color: 'text-green-600',  boton: 'bg-green-600 hover:bg-green-700',  icon: CheckCircleIcon },
}

const v = computed(() => VARIANTES[props.variante] || VARIANTES.primaria)
const iconoFondo     = computed(() => v.value.fondo)
const iconoColor     = computed(() => v.value.color)
const iconoComp      = computed(() => v.value.icon)
const botonConfirmar = computed(() => v.value.boton)

function confirmar() {
  emit('confirm')
  emit('update:modelValue', false)
}
function cancelar() {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>
