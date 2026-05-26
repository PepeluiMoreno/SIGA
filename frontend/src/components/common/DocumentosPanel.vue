<template>
  <div class="space-y-3">
    <!-- Lista de documentos -->
    <div v-if="documentos?.length" class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Nombre</th>
            <th class="px-3 py-2 text-left">Tipo</th>
            <th class="px-3 py-2 text-right">Tamaño</th>
            <th class="px-3 py-2 text-center">Subido</th>
            <th class="px-3 py-2 w-20"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="d in documentos" :key="d.id" class="hover:bg-slate-50">
            <td class="px-3 py-2">
              <a :href="urlDescarga(d)" target="_blank" rel="noopener"
                 class="text-indigo-600 hover:underline font-medium">{{ d.nombre || d.nombreArchivo }}</a>
              <p v-if="d.tipoMime" class="text-xs text-slate-400 mt-0.5">{{ d.tipoMime }}</p>
            </td>
            <td class="px-3 py-2">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                {{ etiquetaTipo(d.tipoDoc) }}
              </span>
            </td>
            <td class="px-3 py-2 text-right font-mono text-xs text-slate-600">{{ fmtTamano(d.tamanyo) }}</td>
            <td class="px-3 py-2 text-center text-xs text-slate-500">{{ fmtFecha(d.creadoEn) }}</td>
            <td class="px-3 py-2 text-right">
              <button v-if="!readonly && deleteFn" type="button" @click="eliminar(d)"
                class="text-red-600 hover:text-red-800 text-xs font-medium">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-center text-slate-400 py-6 text-sm border border-dashed border-slate-200 rounded-xl">
      No hay documentos adjuntos.
    </p>

    <!-- Formulario de subida -->
    <div v-if="!readonly" class="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
      <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Adjuntar documento</h4>
      <div class="flex flex-wrap gap-3 items-end">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-xs font-medium text-slate-700 mb-1">Archivo</label>
          <input ref="fileInputRef" type="file" @change="onFileChange"
            class="block w-full text-sm text-slate-700 file:mr-3 file:h-9 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 file:text-sm file:font-medium hover:file:bg-indigo-100" />
        </div>
        <div class="flex-1 min-w-[150px]">
          <label class="block text-xs font-medium text-slate-700 mb-1">Nombre (opcional)</label>
          <input v-model="form.nombre" type="text" placeholder="Acta de la asamblea…"
            class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div v-if="tipoDocOptions?.length" class="min-w-[140px]">
          <label class="block text-xs font-medium text-slate-700 mb-1">Tipo</label>
          <select v-model="form.tipoDoc"
            class="h-9 w-full px-2 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option v-for="o in tipoDocOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
        <button type="button" @click="subir" :disabled="!form.archivo || subiendo"
          class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
          {{ subiendo ? 'Subiendo…' : 'Subir' }}
        </button>
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  documentos: { type: Array, default: () => [] },
  uploadEndpoint: { type: String, required: true },
  deleteFn: { type: Function, default: null },
  tipoDocOptions: { type: Array, default: () => [] },
  defaultTipoDoc: { type: String, default: 'otro' },
  readonly: { type: Boolean, default: false },
  urlBase: { type: String, default: '/api/uploads/' },
})

const emit = defineEmits(['change'])

const fileInputRef = ref(null)
const subiendo = ref(false)
const error = ref('')

const form = ref({ archivo: null, nombre: '', tipoDoc: props.defaultTipoDoc })

function onFileChange(e) {
  const f = e.target.files?.[0]
  form.value.archivo = f || null
  if (f && !form.value.nombre) form.value.nombre = f.name
}

function urlDescarga(d) {
  return d.url || `${props.urlBase}${d.ruta || ''}`
}

function fmtTamano(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function fmtFecha(s) {
  if (!s) return ''
  try { return new Date(s).toLocaleDateString('es-ES') } catch { return s }
}

function etiquetaTipo(tipo) {
  const opt = props.tipoDocOptions.find(o => o.value === tipo)
  return opt?.label || tipo || 'otro'
}

async function subir() {
  if (!form.value.archivo) return
  subiendo.value = true
  error.value = ''
  try {
    const token = localStorage.getItem('siga_token') || sessionStorage.getItem('siga_token')
    const fd = new FormData()
    fd.append('file', form.value.archivo)
    const params = new URLSearchParams()
    if (form.value.nombre) params.set('nombre', form.value.nombre)
    if (form.value.tipoDoc) params.set('tipo_doc', form.value.tipoDoc)
    const sep = props.uploadEndpoint.includes('?') ? '&' : '?'
    const url = params.toString()
      ? `${props.uploadEndpoint}${sep}${params.toString()}`
      : props.uploadEndpoint
    const r = await fetch(url, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: fd,
    })
    if (!r.ok) {
      const txt = await r.text()
      throw new Error(txt || `Error ${r.status}`)
    }
    form.value = { archivo: null, nombre: '', tipoDoc: props.defaultTipoDoc }
    if (fileInputRef.value) fileInputRef.value.value = ''
    emit('change')
  } catch (e) {
    error.value = e?.message || 'Error al subir el documento'
  } finally {
    subiendo.value = false
  }
}

async function eliminar(doc) {
  if (!props.deleteFn) return
  if (!confirm(`¿Eliminar el documento "${doc.nombre || doc.nombreArchivo}"?`)) return
  try {
    await props.deleteFn(doc)
    emit('change')
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || e?.message || 'Error al eliminar'
  }
}
</script>
