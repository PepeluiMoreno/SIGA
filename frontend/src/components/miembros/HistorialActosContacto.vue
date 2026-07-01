<template>
  <div>
    <div v-if="cargando" class="text-sm text-slate-400 py-4">Cargando historial…</div>

    <div v-else-if="!actos.length" class="text-sm text-slate-400 py-4">
      Sin actos registrados (firmas, asistencias o donaciones).
    </div>

    <!-- Línea de tiempo cronológica: cada acto es una línea de detalle expresiva. -->
    <ol v-else class="relative border-l border-slate-200 ml-2 space-y-4">
      <li v-for="(acto, i) in actos" :key="i" class="ml-4">
        <!-- Punto de la línea, coloreado por tipo de acto -->
        <span class="absolute -left-[5px] mt-1.5 w-2.5 h-2.5 rounded-full ring-2 ring-white"
          :class="colorPunto(acto.tipo)"></span>
        <div class="flex flex-wrap items-baseline gap-x-2">
          <time class="text-xs font-medium text-slate-500 tabular-nums">{{ fmtFecha(acto.fecha) }}</time>
          <p class="text-sm text-slate-800">{{ frase(acto) }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { graphqlClient } from '@/graphql/client.js'

const props = defineProps({
  contactoId: { type: String, required: true },
})

const Q = `
  query HistorialContacto($id: UUID!) {
    historialContacto(contactoId: $id) {
      tipo fecha entidadNombre importe verificado
    }
  }`

const actos = ref([])
const cargando = ref(false)

async function cargar() {
  if (!props.contactoId) return
  cargando.value = true
  try {
    const d = await graphqlClient.request(Q, { id: props.contactoId })
    actos.value = d.historialContacto || []
  } catch {
    actos.value = []
  } finally {
    cargando.value = false
  }
}

// Frase de detalle por acto, tipo "En tal fecha firmó en apoyo de la campaña X".
function frase(a) {
  const campania = a.entidadNombre ? `«${a.entidadNombre}»` : '(sin especificar)'
  if (a.tipo === 'FIRMA') {
    const verif = a.verificado ? '' : ' (pendiente de verificar)'
    return `Firmó en apoyo de la campaña ${campania}${verif}.`
  }
  if (a.tipo === 'ASISTENCIA') {
    return `Asistió a la actividad ${campania}.`
  }
  if (a.tipo === 'DONACION') {
    const imp = a.importe != null ? `${fmtEur(a.importe)} ` : ''
    return a.entidadNombre
      ? `Donó ${imp}en la campaña ${campania}.`
      : `Realizó una donación${a.importe != null ? ` de ${fmtEur(a.importe)}` : ''}.`
  }
  return campania
}

function colorPunto(tipo) {
  return { FIRMA: 'bg-teal-500', ASISTENCIA: 'bg-sky-500', DONACION: 'bg-amber-500' }[tipo] || 'bg-slate-400'
}

function fmtFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function fmtEur(n) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n)
}

onMounted(cargar)
watch(() => props.contactoId, cargar)
</script>
