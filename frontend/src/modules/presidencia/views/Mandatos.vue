<template>
  <AppLayout title="Mandatos y Cargos" subtitle="Composición y vigencia de los órganos de gobierno">

    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <select v-model="filtroEstado"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent">
        <option value="ACTIVO">Mandatos activos</option>
        <option value="">Todos</option>
        <option value="FINALIZADO">Finalizados</option>
      </select>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando mandatos…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="mandatosFiltrados.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <UserGroupIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay mandatos con los filtros seleccionados</p>
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 shadow overflow-hidden">
      <div class="overflow-x-auto -mx-1"><<table class="min-w-full divide-y divide-gray-200 text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cargo</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Miembro</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ámbito</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Inicio</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fin</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="m in mandatosFiltrados" :key="m.id"
            class="hover:bg-gray-50 transition-colors"
            :class="proximoVencimiento(m.fechaFin) ? 'bg-amber-50/30' : ''">
            <td class="px-4 py-3 font-semibold text-gray-900">{{ m.cargo?.nombre ?? '—' }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-purple-100 flex items-center justify-center text-xs font-medium text-purple-700 flex-shrink-0">
                  {{ iniciales(m.miembro) }}
                </div>
                <span class="text-gray-800">{{ m.miembro?.nombre }} {{ m.miembro?.apellido1 }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ m.agrupacion?.nombre ?? 'Central' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatFecha(m.fechaInicio) }}</td>
            <td class="px-4 py-3 text-xs"
              :class="proximoVencimiento(m.fechaFin) ? 'text-amber-600 font-semibold' : 'text-gray-500'">
              {{ m.fechaFin ? formatFecha(m.fechaFin) : '—' }}
              <span v-if="proximoVencimiento(m.fechaFin)" class="ml-1">
                ({{ diasRestantes(m.fechaFin) }}d)
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="badgeEstadoMandato(m.estado)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ m.estado }}
              </span>
              <span v-if="proximoVencimiento(m.fechaFin)"
                class="ml-2 inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                Vence pronto
              </span>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { executeQuery } from '@/graphql/client'
import { GET_MANDATOS_VIGENTES } from '@/graphql/queries/presidencia.js'
import { UserGroupIcon } from '@heroicons/vue/24/outline'

const loading  = ref(false)
const error    = ref('')
const mandatos = ref([])
const filtroEstado = ref('ACTIVO')

const formatFecha = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const iniciales   = (m) => m ? `${m.nombre?.[0] ?? ''}${m.apellido1?.[0] ?? ''}`.toUpperCase() : '?'

const diasRestantes = (s) => {
  if (!s) return null
  return Math.ceil((new Date(s) - new Date()) / 86400000)
}
const proximoVencimiento = (s) => {
  const d = diasRestantes(s)
  return d !== null && d >= 0 && d <= 90
}

const badgeEstadoMandato = (e) => ({
  ACTIVO:     'bg-green-100 text-green-700',
  PENDIENTE:  'bg-yellow-100 text-yellow-700',
  FINALIZADO: 'bg-gray-100 text-gray-500',
  RECHAZADO:  'bg-red-100 text-red-700',
}[e] ?? 'bg-gray-100 text-gray-500')

const mandatosFiltrados = computed(() =>
  filtroEstado.value
    ? mandatos.value.filter(m => m.estado === filtroEstado.value)
    : mandatos.value
)

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const data = await executeQuery(GET_MANDATOS_VIGENTES)
    mandatos.value = data?.historialNombramientos ?? []
  } catch (e) {
    error.value = e.message ?? 'Error al cargar mandatos'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
