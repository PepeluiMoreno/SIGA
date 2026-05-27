<template>
  <div>
    <!-- Zona de drop / click -->
    <label
      :class="[
        'block border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors',
        dragOver
          ? 'border-indigo-500 bg-indigo-50'
          : disabled
            ? 'border-slate-200 bg-slate-50 cursor-not-allowed opacity-60'
            : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-indigo-50/40',
      ]"
      @dragenter.prevent="dragOver = true"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <input ref="inputRef"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        @change="onChange"
        class="sr-only" />

      <div v-if="subiendo" class="space-y-2">
        <div class="text-sm text-slate-600">Subiendo… {{ progreso }}%</div>
        <div class="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
          <div class="h-full bg-indigo-500 transition-all" :style="{ width: progreso + '%' }" />
        </div>
      </div>

      <div v-else-if="!archivoSeleccionado" class="space-y-1">
        <div class="flex items-center justify-center text-slate-400">
          <ArrowUpTrayIcon class="w-6 h-6" />
        </div>
        <p class="text-sm text-slate-700">
          <span class="font-medium text-indigo-600">{{ label }}</span>
          <span class="text-slate-500"> o arrastra aquí</span>
        </p>
        <p v-if="hintText" class="text-xs text-slate-400">{{ hintText }}</p>
      </div>

      <div v-else class="text-left">
        <div class="flex items-center gap-2">
          <DocumentIcon class="w-5 h-5 text-slate-400 shrink-0" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-slate-800 truncate">{{ archivoSeleccionado.name }}</p>
            <p class="text-xs text-slate-500">{{ fmtTamano(archivoSeleccionado.size) }}</p>
          </div>
          <button type="button" @click.stop.prevent="quitar"
            class="text-slate-400 hover:text-red-600 text-xs">
            Quitar
          </button>
        </div>
      </div>
    </label>

    <p v-if="error" class="mt-2 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowUpTrayIcon, DocumentIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  /** Si se proporciona, el archivo se sube automáticamente al seleccionarlo. */
  endpoint:       { type: String,  default: '' },
  /** Query params extra al endpoint (objeto). */
  extraParams:    { type: Object,  default: () => ({}) },
  /** Lista de MIME types o extensiones aceptados, p.ej. 'application/pdf,image/*' o '.pdf,.png'. */
  accept:         { type: String,  default: '' },
  /** Tamaño máximo permitido en MB. 0 = sin límite. */
  maxSizeMB:      { type: Number,  default: 10 },
  /** Permite seleccionar varios archivos. Si true, emit('upload') por cada uno. */
  multiple:       { type: Boolean, default: false },
  /** Etiqueta del botón principal. */
  label:          { type: String,  default: 'Selecciona un archivo' },
  /** Pista bajo el botón (formato y tamaño). Si vacío se construye desde accept/maxSizeMB. */
  hint:           { type: String,  default: '' },
  /** Deshabilita la subida. */
  disabled:       { type: Boolean, default: false },
  /** Nombre del campo en FormData. Por defecto 'file'. */
  fieldName:      { type: String,  default: 'file' },
})

const emit = defineEmits([
  /** Se emite con el File seleccionado antes de subir (útil si no hay endpoint). */
  'select',
  /** Se emite con la respuesta JSON del backend tras subida correcta. */
  'upload',
  /** Se emite con el mensaje de error. */
  'error',
])

const inputRef = ref(null)
const dragOver = ref(false)
const subiendo = ref(false)
const progreso = ref(0)
const archivoSeleccionado = ref(null)
const error = ref('')

const hintText = computed(() => {
  if (props.hint) return props.hint
  const partes = []
  if (props.accept) partes.push(`Formatos: ${props.accept}`)
  if (props.maxSizeMB > 0) partes.push(`máx. ${props.maxSizeMB} MB`)
  return partes.join(' · ')
})

function fmtTamano(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function validar(file) {
  if (props.maxSizeMB > 0 && file.size > props.maxSizeMB * 1024 * 1024) {
    return `El archivo supera el tamaño máximo de ${props.maxSizeMB} MB.`
  }
  if (props.accept) {
    const reglas = props.accept.split(',').map(s => s.trim().toLowerCase())
    const name = file.name.toLowerCase()
    const mime = (file.type || '').toLowerCase()
    const ok = reglas.some(regla => {
      if (regla.startsWith('.')) return name.endsWith(regla)
      if (regla.endsWith('/*'))  return mime.startsWith(regla.slice(0, -1))
      return mime === regla
    })
    if (!ok) return `Formato no aceptado (${file.type || 'desconocido'}).`
  }
  return ''
}

function quitar() {
  archivoSeleccionado.value = null
  error.value = ''
  if (inputRef.value) inputRef.value.value = ''
}

function onChange(e) {
  const files = Array.from(e.target.files || [])
  procesar(files)
}

function onDrop(e) {
  dragOver.value = false
  if (props.disabled) return
  const files = Array.from(e.dataTransfer?.files || [])
  procesar(files)
}

async function procesar(files) {
  error.value = ''
  if (!files.length) return
  if (!props.multiple && files.length > 1) files = [files[0]]

  for (const file of files) {
    const err = validar(file)
    if (err) {
      error.value = err
      emit('error', err)
      return
    }
  }

  if (props.endpoint) {
    for (const file of files) {
      await subir(file)
    }
  } else {
    archivoSeleccionado.value = files[0]
    files.forEach(f => emit('select', f))
  }
}

async function subir(file) {
  subiendo.value = true
  progreso.value = 0
  archivoSeleccionado.value = file
  try {
    const token = localStorage.getItem('siga_token') || sessionStorage.getItem('siga_token')
    const params = new URLSearchParams()
    for (const [k, v] of Object.entries(props.extraParams || {})) {
      if (v !== null && v !== undefined && v !== '') params.set(k, String(v))
    }
    const sep = props.endpoint.includes('?') ? '&' : '?'
    const url = params.toString() ? `${props.endpoint}${sep}${params}` : props.endpoint

    const fd = new FormData()
    fd.append(props.fieldName, file)

    // Usamos XHR para tener barra de progreso (fetch no la expone).
    const respuesta = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', url)
      if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.upload.onprogress = (evt) => {
        if (evt.lengthComputable) progreso.value = Math.round((evt.loaded / evt.total) * 100)
      }
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try { resolve(JSON.parse(xhr.responseText)) }
          catch { resolve({ raw: xhr.responseText }) }
        } else {
          reject(new Error(xhr.responseText || `Error ${xhr.status}`))
        }
      }
      xhr.onerror = () => reject(new Error('Error de red'))
      xhr.send(fd)
    })

    emit('upload', { file, response: respuesta })
    archivoSeleccionado.value = null
    if (inputRef.value) inputRef.value.value = ''
  } catch (e) {
    error.value = e?.message || 'Error al subir el archivo'
    emit('error', error.value)
  } finally {
    subiendo.value = false
    progreso.value = 0
  }
}

defineExpose({
  /** Permite disparar la subida manualmente si endpoint llegó después. */
  subir,
  /** Lanza el diálogo del navegador. */
  abrirDialogo: () => inputRef.value?.click(),
})
</script>
