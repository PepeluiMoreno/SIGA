<template>
  <div class="relative" ref="raiz">
    <!-- Campana -->
    <button @click="toggle"
      class="p-2 rounded-md relative transition-colors"
      style="color: var(--t-text-muted, #6b7280)"
      :aria-label="`Notificaciones${noLeidas > 0 ? ': ' + noLeidas + ' sin leer' : ''}`">
      <BellIcon class="w-6 h-6" />
      <span v-if="noLeidas > 0"
        class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center
               text-[11px] font-semibold text-white bg-red-500 rounded-full">
        {{ noLeidas > 99 ? '99+' : noLeidas }}
      </span>
    </button>

    <!-- Panel -->
    <transition
      enter-active-class="transition ease-out duration-150"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1">
      <div v-if="abierto"
        class="absolute right-0 mt-2 w-80 sm:w-96 max-h-[70vh] flex flex-col rounded-lg shadow-lg border z-50 overflow-hidden"
        style="background-color: var(--t-card, #fff); border-color: var(--t-border, #e5e7eb)">

        <!-- Cabecera -->
        <div class="flex items-center justify-between px-4 py-3 border-b"
          style="border-color: var(--t-border, #e5e7eb)">
          <h3 class="text-sm font-semibold" style="color: var(--t-text, #111827)">Notificaciones</h3>
          <button v-if="noLeidas > 0" @click="marcarTodas"
            class="text-xs font-medium text-blue-600 hover:text-blue-700">
            Marcar todas como leídas
          </button>
        </div>

        <!-- Lista -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="cargando" class="px-4 py-8 text-center text-sm" style="color: var(--t-text-muted, #6b7280)">
            Cargando…
          </div>
          <div v-else-if="notificaciones.length === 0"
            class="px-4 py-10 text-center text-sm" style="color: var(--t-text-muted, #6b7280)">
            No tienes notificaciones
          </div>
          <ul v-else>
            <li v-for="n in notificaciones" :key="n.id"
              @click="abrir(n)"
              class="px-4 py-3 border-b cursor-pointer transition-colors hover:bg-black/[0.03]"
              :style="{ borderColor: 'var(--t-border, #e5e7eb)', backgroundColor: n.leida ? 'transparent' : 'var(--t-accent-soft, rgba(59,130,246,0.06))' }">
              <div class="flex items-start gap-2">
                <span v-if="!n.leida" class="mt-1.5 h-2 w-2 rounded-full bg-blue-500 shrink-0"></span>
                <span v-else class="mt-1.5 h-2 w-2 shrink-0"></span>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium truncate" style="color: var(--t-text, #111827)">{{ n.titulo }}</p>
                  <p class="text-xs mt-0.5 line-clamp-2" style="color: var(--t-text-muted, #6b7280)">{{ n.mensaje }}</p>
                  <p class="text-[11px] mt-1" style="color: var(--t-text-muted, #9ca3af)">{{ formatear(n.fechaCreacion) }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { BellIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_NO_LEIDAS, GET_MIS_NOTIFICACIONES, MARCAR_LEIDA, MARCAR_TODAS_LEIDAS,
} from '@/modules/comunicaciones/graphql/notificaciones'

const router = useRouter()
const { query, mutation } = useGraphQL()

const abierto = ref(false)
const cargando = ref(false)
const noLeidas = ref(0)
const notificaciones = ref([])
const raiz = ref(null)
let intervalo = null

async function cargarContador() {
  try {
    const data = await query(GET_NO_LEIDAS)
    noLeidas.value = data?.misNotificacionesNoLeidas ?? 0
  } catch { /* silencioso: el badge no debe romper el layout */ }
}

async function cargarLista() {
  cargando.value = true
  try {
    const data = await query(GET_MIS_NOTIFICACIONES)
    notificaciones.value = data?.misNotificaciones ?? []
  } catch {
    notificaciones.value = []
  } finally {
    cargando.value = false
  }
}

async function toggle() {
  abierto.value = !abierto.value
  if (abierto.value) await cargarLista()
}

async function marcarTodas() {
  try {
    await mutation(MARCAR_TODAS_LEIDAS)
    notificaciones.value = notificaciones.value.map(n => ({ ...n, leida: true }))
    noLeidas.value = 0
  } catch { /* no-op */ }
}

async function abrir(n) {
  if (!n.leida) {
    try {
      await mutation(MARCAR_LEIDA, { notificacionId: n.id })
      n.leida = true
      noLeidas.value = Math.max(0, noLeidas.value - 1)
    } catch { /* no-op */ }
  }
  if (n.urlAccion) {
    abierto.value = false
    // urlAccion es una ruta interna de la app (p. ej. /secretaria/actas)
    if (n.urlAccion.startsWith('/')) router.push(n.urlAccion)
    else window.open(n.urlAccion, '_blank')
  }
}

function formatear(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const ahora = new Date()
  const difMin = Math.round((ahora - d) / 60000)
  if (difMin < 1) return 'ahora'
  if (difMin < 60) return `hace ${difMin} min`
  if (difMin < 1440) return `hace ${Math.round(difMin / 60)} h`
  return d.toLocaleDateString()
}

function clickFuera(e) {
  if (raiz.value && !raiz.value.contains(e.target)) abierto.value = false
}

onMounted(() => {
  cargarContador()
  document.addEventListener('click', clickFuera)
  // Refresco periódico del contador (sin tiempo real; ligero).
  intervalo = setInterval(cargarContador, 60000)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', clickFuera)
  if (intervalo) clearInterval(intervalo)
})
</script>
