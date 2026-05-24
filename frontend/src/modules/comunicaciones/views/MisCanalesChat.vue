<template>
  <div class="p-4 sm:p-6 lg:p-8">
    <PageHeader titulo="Chat interno" subtitulo="Tus canales de conversación" />

    <div class="mt-4 rounded-lg border" style="border-color: var(--t-border, #e5e7eb); background-color: var(--t-card, #fff)">
      <!-- Aviso si el chat no está activo -->
      <div v-if="!orgConfig.chatActivo" class="px-4 py-10 text-center text-sm" style="color: var(--t-text-muted, #6b7280)">
        El chat interno no está activado en esta organización.
      </div>

      <template v-else>
        <div v-if="cargando" class="px-4 py-10 text-center text-sm" style="color: var(--t-text-muted, #6b7280)">
          Cargando canales…
        </div>

        <div v-else-if="canales.length === 0" class="px-4 py-10 text-center text-sm" style="color: var(--t-text-muted, #6b7280)">
          Todavía no perteneces a ningún canal. Los canales se crean automáticamente
          cuando entras en un grupo de trabajo o tienes un cargo en una unidad.
        </div>

        <ul v-else class="divide-y" style="--tw-divide-opacity: 1">
          <li v-for="c in canales" :key="c.id"
            class="flex items-center justify-between gap-4 px-4 py-3"
            style="border-color: var(--t-border, #e5e7eb)">
            <div class="min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--t-text, #111827)">
                {{ c.nombre || nombrePorOrigen(c.origen) }}
              </p>
              <p class="text-xs mt-0.5" style="color: var(--t-text-muted, #6b7280)">
                {{ etiquetaOrigen(c.origen) }}
                <span v-if="c.archivado" class="ml-1 italic">· archivado</span>
              </p>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <span class="inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full"
                :class="estadoClase(c.estadoSync)">
                {{ etiquetaEstado(c.estadoSync) }}
              </span>
              <button v-if="c.estadoSync === 'ERROR'" @click="reintentar(c)"
                class="text-xs font-medium text-blue-600 hover:text-blue-700"
                :disabled="reintentando === c.id">
                {{ reintentando === c.id ? '…' : 'Reintentar' }}
              </button>
            </div>
          </li>
        </ul>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { useToast } from '@/composables/useToast'
import { GET_MIS_CANALES_CHAT, REINTENTAR_SYNC_CANAL } from '@/modules/comunicaciones/graphql/notificaciones'

const { query, mutation } = useGraphQL()
const orgConfig = useOrgConfigStore()
const toast = useToast()

const cargando = ref(false)
const canales = ref([])
const reintentando = ref(null)

async function cargar() {
  if (!orgConfig.chatActivo) return
  cargando.value = true
  try {
    const data = await query(GET_MIS_CANALES_CHAT)
    canales.value = data?.misCanalesChat ?? []
  } catch {
    canales.value = []
  } finally {
    cargando.value = false
  }
}

async function reintentar(c) {
  reintentando.value = c.id
  try {
    const data = await mutation(REINTENTAR_SYNC_CANAL, { canalId: c.id })
    const r = data?.reintentarSyncCanal
    if (r?.canal) c.estadoSync = r.canal.estadoSync
    toast?.[r?.exito ? 'success' : 'error']?.(r?.mensaje || 'Operación realizada')
  } catch {
    toast?.error?.('No se pudo reintentar la sincronización')
  } finally {
    reintentando.value = null
  }
}

function etiquetaOrigen(o) {
  return o === 'GRUPO_TRABAJO' ? 'Grupo de trabajo'
       : o === 'UNIDAD_ORGANIZATIVA' ? 'Unidad organizativa'
       : o
}
function nombrePorOrigen(o) {
  return o === 'GRUPO_TRABAJO' ? 'Canal de grupo' : 'Canal de unidad'
}
function etiquetaEstado(e) {
  return e === 'OK' ? 'Activo' : e === 'ERROR' ? 'Con incidencia' : 'Pendiente'
}
function estadoClase(e) {
  if (e === 'OK') return 'bg-green-100 text-green-700'
  if (e === 'ERROR') return 'bg-red-100 text-red-700'
  return 'bg-gray-100 text-gray-600'
}

onMounted(cargar)
</script>
