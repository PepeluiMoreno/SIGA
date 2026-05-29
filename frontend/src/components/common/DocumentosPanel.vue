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

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">Nombre (opcional)</label>
          <input v-model="metadatos.nombre" type="text" placeholder="Acta de la asamblea…"
            class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div v-if="tipoDocOptions?.length">
          <label class="block text-xs font-medium text-slate-700 mb-1">Tipo</label>
          <select v-model="metadatos.tipoDoc"
            class="h-9 w-full px-2 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option v-for="o in tipoDocOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
      </div>

      <UploadFile
        :endpoint="uploadEndpoint"
        :extra-params="extraParamsSubida"
        :accept="accept"
        :max-size-m-b="maxSizeMB"
        @upload="onSubido"
        @error="error = $event"
      />

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import UploadFile from './UploadFile.vue'
import { useConfirm } from '@/composables/useConfirm'

const confirmar = useConfirm()

const props = defineProps({
  documentos: { type: Array, default: () => [] },
  uploadEndpoint: { type: String, required: true },
  deleteFn: { type: Function, default: null },
  tipoDocOptions: { type: Array, default: () => [] },
  defaultTipoDoc: { type: String, default: 'otro' },
  readonly: { type: Boolean, default: false },
  urlBase: { type: String, default: '/api/uploads/' },
  /** MIME types o extensiones aceptadas. */
  accept: { type: String, default: '' },
  /** Tamaño máximo en MB. */
  maxSizeMB: { type: Number, default: 10 },
})

const emit = defineEmits(['change'])

const error = ref('')
const metadatos = ref({ nombre: '', tipoDoc: props.defaultTipoDoc })

// Los metadatos viajan como query-params al endpoint (patrón existente
// en /upload/actividades/{id}/documentos y similares).
const extraParamsSubida = computed(() => {
  const p = {}
  if (metadatos.value.nombre)  p.nombre   = metadatos.value.nombre
  if (metadatos.value.tipoDoc) p.tipo_doc = metadatos.value.tipoDoc
  return p
})

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

function onSubido() {
  // Limpiar metadatos para la siguiente subida y notificar al padre.
  metadatos.value = { nombre: '', tipoDoc: props.defaultTipoDoc }
  error.value = ''
  emit('change')
}

async function eliminar(doc) {
  if (!props.deleteFn) return
  const ok = await confirmar({
    titulo: 'Eliminar documento',
    mensaje: `¿Eliminar el documento «${doc.nombre || doc.nombreArchivo}»?`,
    variante: 'critica',
    etiquetaConfirmar: 'Eliminar',
  })
  if (!ok) return
  try {
    await props.deleteFn(doc)
    emit('change')
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || e?.message || 'Error al eliminar'
  }
}
</script>
