<template>
  <AppLayout title="Libro de Socios" subtitle="Generación y custodia del Libro de Socios (Ley Orgánica 1/2002)">

    <!-- Cabecera con botón -->
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-gray-600 max-w-xl">
        El Libro de Socios debe estar actualizado y disponible para inspección en cualquier momento.
        Cada generación queda registrada con la fecha de corte y el número de socios.
      </p>
      <button v-if="tienePermiso('SEC_LIBRO_SOCIOS_GENERAR')"
        @click="generarSnapshot"
        :disabled="generando"
        class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 ml-4 flex-shrink-0">
        <ArrowPathIcon class="w-4 h-4" :class="generando ? 'animate-spin' : ''" />
        {{ generando ? 'Generando…' : 'Generar ahora' }}
      </button>
    </div>

    <!-- Último snapshot destacado -->
    <div v-if="ultimoSnapshot"
      class="bg-purple-50 border border-purple-200 rounded-xl p-5 mb-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="text-center">
        <p class="text-3xl font-bold text-purple-700">{{ ultimoSnapshot.totalSociosActivos }}</p>
        <p class="text-xs text-purple-600 mt-1">Socios activos</p>
      </div>
      <div class="text-center">
        <p class="text-3xl font-bold text-gray-600">{{ ultimoSnapshot.totalSociosBaja }}</p>
        <p class="text-xs text-gray-500 mt-1">En situación de baja</p>
      </div>
      <div class="text-center">
        <p class="text-3xl font-bold text-gray-700">{{ ultimoSnapshot.totalSociosHistorico }}</p>
        <p class="text-xs text-gray-500 mt-1">Total histórico</p>
      </div>
      <div class="text-center">
        <p class="text-sm font-semibold text-gray-700">{{ formatFecha(ultimoSnapshot.fechaCorte) }}</p>
        <p class="text-xs text-gray-500 mt-1">Fecha de corte</p>
        <p class="text-xs text-gray-400 mt-0.5">Generado: {{ formatFechaHora(ultimoSnapshot.fechaGeneracion) }}</p>
      </div>
    </div>

    <!-- Historial de snapshots -->
    <EstadoCarga v-if="loading" mensaje="Cargando historial…" />

    <div v-else-if="snapshots.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <BookOpenIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay snapshots generados</p>
      <p class="text-sm mt-1">Genera el primer Libro de Socios con el botón de arriba.</p>
    </div>

    <div v-else>
      <h3 class="text-sm font-medium text-gray-700 mb-3">Historial de generaciones</h3>
      <div class="bg-white rounded-lg border border-gray-200 shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha corte</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Activos</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Histórico</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Motivo</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generado</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(s, i) in snapshots" :key="s.id"
              :class="i === 0 ? 'bg-purple-50/50' : 'hover:bg-gray-50'">
              <td class="px-4 py-3 font-medium text-gray-900">
                {{ formatFecha(s.fechaCorte) }}
                <span v-if="i === 0" class="ml-2 text-xs text-purple-600 font-medium">actual</span>
              </td>
              <td class="px-4 py-3 text-gray-700 font-medium">{{ s.totalSociosActivos }}</td>
              <td class="px-4 py-3 text-gray-500">{{ s.totalSociosHistorico }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ s.motivo ?? '—' }}</td>
              <td class="px-4 py-3 text-gray-400 text-xs">{{ formatFechaHora(s.fechaGeneracion) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: motivo de generación -->
    <Teleport to="body">
      <div v-if="modalMotivo" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">Generar Libro de Socios</h2>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de corte</label>
            <input type="date" v-model="formGeneracion.fechaCorte"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
            <input type="text" v-model="formGeneracion.motivo"
              placeholder="Asamblea anual, inspección registral…"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div class="flex justify-end gap-3">
            <button @click="modalMotivo = false" class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="ejecutarGeneracion" :disabled="generando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
              {{ generando ? 'Generando…' : 'Generar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_LIBRO_SOCIOS_SNAPSHOTS, GENERAR_LIBRO_SOCIOS } from '@/graphql/queries/secretaria.js'
import { BookOpenIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const loading   = ref(false)
const generando = ref(false)
const snapshots = ref([])
const modalMotivo = ref(false)
const formGeneracion = ref({ fechaCorte: '', motivo: '' })

const ultimoSnapshot = computed(() => snapshots.value[0] ?? null)

const formatFecha = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s
  ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
  : '—'

const cargar = async () => {
  loading.value = true
  try {
    const data = await executeQuery(GET_LIBRO_SOCIOS_SNAPSHOTS)
    snapshots.value = data?.libroSociosSnapshots ?? []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const generarSnapshot = () => {
  formGeneracion.value = {
    fechaCorte: new Date().toISOString().split('T')[0],
    motivo: '',
  }
  modalMotivo.value = true
}

const ejecutarGeneracion = async () => {
  generando.value = true
  try {
    await executeMutation(GENERAR_LIBRO_SOCIOS, {
      fechaCorte: formGeneracion.value.fechaCorte || null,
      motivo: formGeneracion.value.motivo || null,
    })
    modalMotivo.value = false
    await cargar()
  } catch (e) {
    alert(e.message ?? 'Error al generar el libro')
  } finally {
    generando.value = false
  }
}

onMounted(cargar)
</script>
