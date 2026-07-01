<template>
  <div class="rounded-lg border border-slate-300 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 overflow-hidden">
    <!-- Barra de formato -->
    <div class="flex flex-wrap items-center gap-0.5 px-2 py-1.5 border-b border-slate-200 bg-slate-50">
      <button v-for="b in botones" :key="b.cmd" type="button" :title="b.title"
        @mousedown.prevent="ejecutar(b.cmd, b.valor)"
        class="w-8 h-8 flex items-center justify-center rounded text-slate-600 hover:bg-slate-200 transition-colors text-sm">
        <component :is="b.icon" v-if="b.icon" class="w-4 h-4" />
        <span v-else :class="b.clase">{{ b.txt }}</span>
      </button>
      <span class="w-px h-5 bg-slate-300 mx-1"></span>
      <button type="button" title="Insertar enlace" @mousedown.prevent="insertarEnlace"
        class="w-8 h-8 flex items-center justify-center rounded text-slate-600 hover:bg-slate-200 transition-colors">
        <LinkIcon class="w-4 h-4" />
      </button>
    </div>

    <!-- Área editable (WYSIWYG) -->
    <div ref="editor" contenteditable="true"
      class="min-h-[12rem] max-h-[24rem] overflow-y-auto px-3 py-2.5 text-sm text-slate-800 focus:outline-none prose-sm"
      :data-placeholder="placeholder"
      @input="onInput"
      @blur="onInput"></div>
  </div>
</template>

<script setup>
/**
 * EditorTextoRico — editor WYSIWYG ligero (contenteditable + execCommand), sin
 * dependencias. Barra con negrita/cursiva/subrayado, listas y enlaces. v-model =
 * HTML del contenido. Para redactar cuerpos de email tipo cliente de correo.
 */
import { ref, onMounted, watch } from 'vue'
import { ListBulletIcon, NumberedListIcon, LinkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Escribe el mensaje…' },
})
const emit = defineEmits(['update:modelValue'])

const editor = ref(null)

const botones = [
  { cmd: 'bold',          title: 'Negrita',    txt: 'B', clase: 'font-bold' },
  { cmd: 'italic',        title: 'Cursiva',    txt: 'I', clase: 'italic' },
  { cmd: 'underline',     title: 'Subrayado',  txt: 'U', clase: 'underline' },
  { cmd: 'insertUnorderedList', title: 'Lista', icon: ListBulletIcon },
  { cmd: 'insertOrderedList',   title: 'Lista numerada', icon: NumberedListIcon },
]

function ejecutar(cmd, valor = null) {
  document.execCommand(cmd, false, valor)
  onInput()
}
function insertarEnlace() {
  const url = window.prompt('URL del enlace:')
  if (url) ejecutar('createLink', url)
}
function onInput() {
  emit('update:modelValue', editor.value?.innerHTML || '')
}

onMounted(() => {
  if (editor.value && props.modelValue) editor.value.innerHTML = props.modelValue
})
// Sincroniza si el modelo cambia desde fuera (p.ej. al aplicar una plantilla),
// evitando pisar lo que el usuario está escribiendo.
watch(() => props.modelValue, (val) => {
  if (editor.value && val !== editor.value.innerHTML) editor.value.innerHTML = val || ''
})
</script>

<style scoped>
[contenteditable][data-placeholder]:empty::before {
  content: attr(data-placeholder);
  color: #94a3b8;
  pointer-events: none;
}
</style>
