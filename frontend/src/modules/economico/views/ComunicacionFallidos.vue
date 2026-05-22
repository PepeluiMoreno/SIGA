<template>
  <!-- Pantalla 5.4 — Comunicación a socios con recibo FALLIDO (Flujo 4 / D4.3) -->
  <AppLayout title="Comunicación de fallidos" subtitle="Avisar a socios con recibo devuelto por el banco">

    <!-- Filtros -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-4">
      <div class="flex flex-wrap items-end gap-3">
        <div>
          <label class="label">Ejercicio</label>
          <select v-model="filtroEjercicio" class="input-sm w-full sm:w-32">
            <option value="">Todos</option>
            <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <label class="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" v-model="soloSinNotificar" />
          Solo sin notificar
        </label>
        <div class="ml-auto text-sm text-slate-500">
          {{ filtrados.length }} de {{ recibos.length }} recibos fallidos
        </div>
      </div>
    </div>

    <!-- Tabla recibos -->
    <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600">
          <tr>
            <th class="px-3 py-2 text-left w-10">
              <input type="checkbox" :checked="todosSeleccionados" @change="alternarTodos" />
            </th>
            <th class="px-3 py-2 text-left">Socio</th>
            <th class="px-3 py-2 text-left">Recibo</th>
            <th class="px-3 py-2 text-right">Importe</th>
            <th class="px-3 py-2 text-left">Motivo</th>
            <th class="px-3 py-2 text-left">Email</th>
            <th class="px-3 py-2 text-center">Aviso</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="!filtrados.length">
            <td colspan="7" class="text-center text-slate-400 py-8">No hay recibos fallidos con esos filtros.</td>
          </tr>
          <tr v-for="r in filtrados" :key="r.id" class="hover:bg-slate-50">
            <td class="px-3 py-1.5"><input type="checkbox" :value="r.id" v-model="seleccionados" /></td>
            <td class="px-3 py-1.5">{{ socioNombre(r) }}</td>
            <td class="px-3 py-1.5 font-mono text-xs">{{ r.numeroRecibo }}</td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(r.importe) }}</td>
            <td class="px-3 py-1.5 text-xs text-slate-600 truncate max-w-xs">{{ extraerMotivo(r.observaciones) }}</td>
            <td class="px-3 py-1.5 text-xs">
              <span v-if="r.miembro?.email" class="text-slate-700">{{ r.miembro.email }}</span>
              <span v-else class="text-red-500">— sin email —</span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span v-if="r.fechaAvisoFallido" class="text-xs text-green-700">{{ fechaFmt(r.fechaAvisoFallido) }}</span>
              <span v-else class="text-xs text-slate-400">pendiente</span>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- Barra envío -->
    <div v-if="seleccionados.length" class="mt-4 bg-white border border-indigo-200 rounded-xl p-4">
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex-1 min-w-[280px]">
          <label class="label">Plantilla de email *</label>
          <select v-model="plantillaId" class="input">
            <option value="">— Selecciona plantilla —</option>
            <option v-for="p in plantillas" :key="p.id" :value="p.id">
              {{ p.codigo }} — {{ p.nombre }}
            </option>
          </select>
          <p v-if="plantillaSeleccionada" class="text-xs text-slate-500 mt-1">
            Asunto: <em>{{ plantillaSeleccionada.asunto }}</em>
          </p>
          <p v-if="plantillaSeleccionada?.variablesDisponibles" class="text-xs text-slate-500 mt-1">
            Variables sustituibles: <code class="text-indigo-600">{{ formatoVariables(plantillaSeleccionada.variablesDisponibles) }}</code>
          </p>
        </div>
        <div>
          <p class="text-sm text-slate-700">{{ seleccionados.length }} recibos seleccionados</p>
          <p class="text-xs text-slate-500">Se marcarán como notificados con fecha de hoy</p>
        </div>
        <button @click="enviar" :disabled="!plantillaId || enviando" class="btn-primary">
          {{ enviando ? 'Enviando…' : `Enviar a ${seleccionados.length} socios` }}
        </button>
      </div>
      <p v-if="mensajeResultado" class="text-sm mt-3" :class="mensajeResultado.tipo === 'ok' ? 'text-green-700' : 'text-red-600'">
        {{ mensajeResultado.texto }}
      </p>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_RECIBOS_FALLIDOS,
  GET_PLANTILLAS_EMAIL_ECONOMICO,
  COMUNICAR_RECIBOS_FALLIDOS,
} from '@/graphql/queries/financiero'

const { query: gqlQuery, mutation: gqlMutation } = useGraphQL()

const recibos = ref([])
const plantillas = ref([])
const seleccionados = ref([])
const filtroEjercicio = ref('')
const soloSinNotificar = ref(true)
const plantillaId = ref('')
const enviando = ref(false)
const mensajeResultado = ref(null)

const ejerciciosDisponibles = computed(() => {
  const ys = [...new Set(recibos.value.map(r => r.ejercicio))].sort().reverse()
  return ys
})

const filtrados = computed(() => recibos.value.filter(r => {
  if (filtroEjercicio.value && r.ejercicio !== Number(filtroEjercicio.value)) return false
  if (soloSinNotificar.value && r.fechaAvisoFallido) return false
  return true
}))

const todosSeleccionados = computed(() =>
  filtrados.value.length > 0 && filtrados.value.every(r => seleccionados.value.includes(r.id))
)

const plantillaSeleccionada = computed(() =>
  plantillas.value.find(p => p.id === plantillaId.value)
)

const alternarTodos = () => {
  if (todosSeleccionados.value) {
    seleccionados.value = seleccionados.value.filter(id => !filtrados.value.some(r => r.id === id))
  } else {
    const nuevos = filtrados.value.map(r => r.id).filter(id => !seleccionados.value.includes(id))
    seleccionados.value = [...seleccionados.value, ...nuevos]
  }
}

const socioNombre = (r) => {
  const m = r.miembro
  return m ? `${m.nombre || ''} ${m.apellido1 || ''} ${m.apellido2 || ''}`.trim() : '—'
}

const extraerMotivo = (obs) => {
  if (!obs) return ''
  const m = obs.match(/FALLIDO \[([^\]]+)\]:?\s*(.*)/)
  if (m) return `${m[1]} — ${m[2]}`
  return obs.split('\n').pop()
}

const formatoVariables = (vars) => {
  if (!vars) return ''
  if (Array.isArray(vars)) return vars.map(v => `{${v}}`).join(', ')
  if (typeof vars === 'object') return Object.keys(vars).map(v => `{${v}}`).join(', ')
  return String(vars)
}

const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d)) : ''

const cargar = async () => {
  const data = await gqlQuery(GET_RECIBOS_FALLIDOS)
  recibos.value = data.recibos || []
  const dp = await gqlQuery(GET_PLANTILLAS_EMAIL_ECONOMICO)
  plantillas.value = dp.plantillasEmail || []
}

const enviar = async () => {
  enviando.value = true
  mensajeResultado.value = null
  try {
    const data = await gqlMutation(COMUNICAR_RECIBOS_FALLIDOS, {
      reciboIds: seleccionados.value,
      plantillaEmailId: plantillaId.value,
    })
    mensajeResultado.value = {
      tipo: 'ok',
      texto: `✓ ${data.comunicarRecibosFallidos} recibos marcados como notificados.`,
    }
    seleccionados.value = []
    await cargar()
  } catch (e) {
    mensajeResultado.value = { tipo: 'error', texto: e.message || 'Error al enviar' }
  } finally {
    enviando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.label { @apply block text-sm font-medium text-slate-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
.input-sm { @apply px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
</style>
