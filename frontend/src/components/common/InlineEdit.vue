<template>
  <div class="group relative inline-flex items-center gap-1" :class="{ 'w-full': block }">
    <!-- Modo lectura -->
    <template v-if="!editando">
      <span
        class="text-inherit leading-tight"
        :class="[displayClass, { 'text-slate-400 italic': !modelValue }]"
      >
        {{ modelValue || placeholder }}
      </span>
      <button
        @click="iniciarEdicion"
        class="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 shrink-0"
        :title="`Editar ${label}`"
        aria-label="Editar"
      >
        <PencilIcon class="w-3.5 h-3.5" />
      </button>
    </template>

    <!-- Modo edición -->
    <template v-else>
      <component
        :is="tipo === 'textarea' ? 'textarea' : 'input'"
        ref="inputRef"
        v-model="valorLocal"
        :type="tipo === 'textarea' ? undefined : tipo"
        :rows="tipo === 'textarea' ? 3 : undefined"
        :placeholder="placeholder"
        :disabled="guardando"
        class="flex-1 px-2 py-1 text-sm border border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white disabled:opacity-60"
        :class="{ 'w-full resize-none': tipo === 'textarea' }"
        @keydown.enter.exact="tipo !== 'textarea' && guardar()"
        @keydown.escape="cancelar"
      />

      <div class="flex items-center gap-1 shrink-0">
        <!-- Confirmar -->
        <button
          @click="guardar"
          :disabled="guardando"
          class="p-1 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
          title="Confirmar (Enter)"
        >
          <span v-if="guardando" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin block" />
          <CheckIcon v-else class="w-3.5 h-3.5" />
        </button>
        <!-- Cancelar -->
        <button
          @click="cancelar"
          :disabled="guardando"
          class="p-1 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-50 transition-colors"
          title="Cancelar (Esc)"
        >
          <XMarkIcon class="w-3.5 h-3.5" />
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label:      { type: String, default: 'campo' },
  placeholder:{ type: String, default: '—' },
  /** 'text' | 'number' | 'email' | 'date' | 'textarea' */
  tipo:       { type: String, default: 'text' },
  block:      { type: Boolean, default: false },
  displayClass: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'save'])

const editando   = ref(false)
const guardando  = ref(false)
const valorLocal = ref('')
const inputRef   = ref(null)

async function iniciarEdicion() {
  valorLocal.value = props.modelValue ?? ''
  editando.value = true
  await nextTick()
  inputRef.value?.focus()
  inputRef.value?.select?.()
}

async function guardar() {
  if (valorLocal.value === props.modelValue) { cancelar(); return }
  guardando.value = true
  try {
    await new Promise((resolve, reject) => emit('save', { value: valorLocal.value, resolve, reject }))
    emit('update:modelValue', valorLocal.value)
    editando.value = false
  } catch {
    // El padre manejó el error — mantener en modo edición
  } finally {
    guardando.value = false
  }
}

function cancelar() {
  editando.value = false
  valorLocal.value = ''
}
</script>
