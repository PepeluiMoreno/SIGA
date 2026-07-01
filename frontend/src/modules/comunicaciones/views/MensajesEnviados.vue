<template>
  <AppLayout title="Mensajes enviados"
    subtitle="Histórico de correos enviados desde la aplicación">

    <!-- Buscador simple -->
    <div class="mb-4">
      <div class="relative max-w-md">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        <input v-model="busqueda" type="text" placeholder="Buscar por asunto o destinatario…"
          class="w-full h-10 pl-9 pr-3 text-sm border border-slate-300 rounded-lg bg-white
                 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" />
      </div>
    </div>

    <!-- Carga -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <p class="text-red-700 font-medium">No se pudo cargar el histórico</p>
      <p class="text-red-600 text-sm mt-1">{{ error }}</p>
      <button @click="cargar" class="mt-3 text-red-600 hover:text-red-800 text-sm font-medium">Reintentar</button>
    </div>

    <template v-else>
      <!-- Vacío -->
      <div v-if="!mensajes.length" class="py-16 text-center text-slate-400">
        <EnvelopeIcon class="w-12 h-12 mx-auto mb-3 text-slate-300" />
        <p class="text-base font-medium text-slate-600">Aún no se ha enviado ningún mensaje</p>
        <p class="text-sm mt-1">Los correos que envíes desde la aplicación quedarán registrados aquí.</p>
      </div>

      <!-- Sin resultados de búsqueda -->
      <div v-else-if="!mensajesFiltrados.length" class="py-12 text-center text-slate-400">
        <p class="text-base font-medium text-slate-600">Sin mensajes que coincidan con «{{ busqueda }}»</p>
        <button @click="busqueda = ''" class="mt-2 text-sm text-indigo-600 hover:text-indigo-800 font-medium">Limpiar búsqueda</button>
      </div>

      <!-- Tabla -->
      <div v-else class="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
              <th class="px-4 py-3">Fecha</th>
              <th class="px-4 py-3">Asunto</th>
              <th class="px-4 py-3">Destinatarios</th>
              <th class="px-4 py-3">Remitente</th>
              <th class="px-4 py-3 text-center">Envíos</th>
              <th class="px-4 py-3 text-right">Ver</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="m in mensajesFiltrados" :key="m.id" class="hover:bg-slate-50/60">
              <td class="px-4 py-3 whitespace-nowrap text-slate-500 tabular-nums">{{ fmtFecha(m.enviadoEn) }}</td>
              <td class="px-4 py-3 font-medium text-slate-800 max-w-xs truncate">{{ m.asunto }}</td>
              <td class="px-4 py-3 text-slate-600 max-w-xs truncate">{{ m.para }}</td>
              <td class="px-4 py-3 text-slate-600 whitespace-nowrap">{{ m.remitenteNombre || '—' }}</td>
              <td class="px-4 py-3 text-center">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="m.errores ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'">
                  {{ m.enviados }}/{{ m.total }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button @click="abrir(m)" class="text-slate-400 hover:text-indigo-600 transition-colors" title="Ver mensaje">
                  <EyeIcon class="w-5 h-5 inline" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Modal de detalle: muestra el mensaje tal cual se envió -->
    <div v-if="detalle" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="detalle = null">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <h3 class="font-semibold text-slate-800">{{ detalle.asunto }}</h3>
          <button @click="detalle = null" class="text-slate-400 hover:text-slate-700"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="px-5 py-4 overflow-y-auto space-y-3">
          <div class="grid grid-cols-[auto,1fr] gap-x-3 gap-y-1 text-sm">
            <span class="text-slate-400">Enviado</span><span class="text-slate-700">{{ fmtFecha(detalle.enviadoEn) }} · por {{ detalle.remitenteNombre || '—' }}</span>
            <span class="text-slate-400">Para</span><span class="text-slate-700 break-words">{{ detalle.para || '—' }}</span>
            <template v-if="detalle.cc"><span class="text-slate-400">CC</span><span class="text-slate-700 break-words">{{ detalle.cc }}</span></template>
            <template v-if="detalle.cco"><span class="text-slate-400">CCO</span><span class="text-slate-700 break-words">{{ detalle.cco }}</span></template>
            <span class="text-slate-400">Resultado</span>
            <span class="text-slate-700">{{ detalle.enviados }} de {{ detalle.total }} entregados</span>
          </div>
          <div v-if="detalle.errores" class="rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800 whitespace-pre-line">
            {{ detalle.errores }}
          </div>
          <div class="border border-slate-200 rounded-lg p-4 text-sm text-slate-800 prose prose-sm max-w-none" v-html="detalle.cuerpoHtml"></div>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client.js'
import { MagnifyingGlassIcon, EnvelopeIcon, EyeIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const loading = ref(true)
const error = ref('')
const mensajes = ref([])
const busqueda = ref('')
const detalle = ref(null)

const Q = `
  query MensajesEnviados($limite: Int!, $offset: Int!) {
    mensajesEnviados(limite: $limite, offset: $offset) {
      id enviadoEn asunto cuerpoHtml para cc cco enviados total errores remitenteNombre
    }
  }`

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const d = await executeQuery(Q, { limite: 100, offset: 0 })
    mensajes.value = d.mensajesEnviados || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || e?.message || 'Error de conexión.'
  } finally {
    loading.value = false
  }
}

const mensajesFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return mensajes.value
  return mensajes.value.filter(m =>
    (m.asunto || '').toLowerCase().includes(q) ||
    (m.para || '').toLowerCase().includes(q)
  )
})

function abrir(m) { detalle.value = m }

function fmtFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(cargar)
</script>
