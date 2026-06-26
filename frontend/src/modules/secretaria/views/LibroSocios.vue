<template>
  <AppLayout title="Libro de Socios" subtitle="Generación y custodia del Libro de Socios (Ley Orgánica 1/2002)">

    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
      <p class="text-sm text-gray-600 max-w-xl leading-relaxed">
        El Libro de Socios debe estar actualizado y disponible para inspección en cualquier momento.
        Cada generación queda registrada con la fecha de corte y el número de socios.
      </p>
      <button v-if="tienePermiso('SEC_LIBRO_SOCIOS_GENERAR')"
        @click="abrirGeneracion"
        class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors flex-shrink-0">
        <ArrowPathIcon class="w-4 h-4" /> Generar ahora
      </button>
    </div>

    <!-- KPIs del último snapshot -->
    <div v-if="ultimoSnapshot" class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <InfoCard icon="✅" bg-class="bg-purple-50 border-purple-200"
        :items="[{ label: 'Socios activos', value: ultimoSnapshot.totalSociosActivos }]" />
      <InfoCard icon="📤" bg-class="bg-gray-50 border-gray-200"
        :items="[{ label: 'En situación de baja', value: ultimoSnapshot.totalSociosBaja }]" />
      <InfoCard icon="📊" bg-class="bg-gray-50 border-gray-200"
        :items="[{ label: 'Total histórico', value: ultimoSnapshot.totalSociosHistorico }]" />
      <InfoCard icon="📅" bg-class="bg-gray-50 border-gray-200"
        :items="[{ label: 'Fecha de corte', value: formatFecha(ultimoSnapshot.fechaCorte) }]"
        :description="`Generado: ${formatFechaHora(ultimoSnapshot.fechaGeneracion)}`" />
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando historial…" />

    <div v-else-if="snapshots.length === 0"
      class="bg-white rounded-lg border border-gray-200 shadow p-12 text-center text-gray-500">
      <BookOpenIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
      <p class="font-medium text-gray-700">No hay generaciones registradas</p>
      <p class="text-sm mt-1">Genera el primer Libro de Socios con el botón de arriba.</p>
    </div>

    <div v-else>
      <h3 class="text-sm font-medium text-gray-700 mb-3">Historial de generaciones</h3>
      <div class="bg-white rounded-lg border border-gray-200 shadow overflow-hidden">
        <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha corte</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Activos</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Histórico</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Motivo</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generado</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PDF</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(s, i) in snapshots" :key="s.id"
              :class="i === 0 ? 'bg-purple-50/40' : 'hover:bg-gray-50 transition-colors'">
              <td class="px-4 py-3 font-medium text-gray-900">
                {{ formatFecha(s.fechaCorte) }}
                <span v-if="i === 0"
                  class="ml-2 inline-flex px-1.5 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                  actual
                </span>
              </td>
              <td class="px-4 py-3 font-semibold text-gray-800">{{ s.totalSociosActivos }}</td>
              <td class="px-4 py-3 text-gray-500">{{ s.totalSociosHistorico }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ s.motivo ?? '—' }}</td>
              <td class="px-4 py-3 text-gray-400 text-xs">{{ formatFechaHora(s.fechaGeneracion) }}</td>
              <td class="px-4 py-3">
                <button v-if="s.tienePdf" @click="descargarPdf(s)"
                  class="text-purple-600 hover:text-purple-800 text-xs font-medium underline">Descargar</button>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
            </tr>
          </tbody>
        </table></div>
      </div>
    </div>

    <!-- Modal: Generar -->
    <Teleport to="body">
      <div v-if="modalGeneracion"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalGeneracion = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Generar Libro de Socios</h2>
            <button @click="modalGeneracion = false" class="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de corte</label>
              <input type="date" v-model="formGen.fechaCorte"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
              <input type="text" v-model="formGen.motivo"
                placeholder="Asamblea anual, inspección registral, cierre de ejercicio…"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
          </div>
          <p v-if="errorModal" class="mx-6 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {{ errorModal }}
          </p>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modalGeneracion = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
            <button @click="ejecutarGeneracion" :disabled="generando"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
              <ArrowPathIcon class="w-4 h-4" :class="generando ? 'animate-spin' : ''" />
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
import InfoCard from '@/components/common/InfoCard.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { useAuthStore } from '@/stores/auth.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import { GET_LIBRO_SOCIOS_SNAPSHOTS, GENERAR_LIBRO_SOCIOS } from '@/graphql/queries/secretaria.js'
import { BookOpenIcon, ArrowPathIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const authStore = useAuthStore()
const loading   = ref(false)
const generando = ref(false)
const snapshots = ref([])
const modalGeneracion = ref(false)
const errorModal = ref('')
const formGen = ref({ fechaCorte: '', motivo: '' })

const ultimoSnapshot = computed(() => snapshots.value[0] ?? null)

const formatFecha     = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : '—'

const cargar = async () => {
  loading.value = true
  try {
    const data = await executeQuery(GET_LIBRO_SOCIOS_SNAPSHOTS)
    snapshots.value = data?.libroSociosSnapshots ?? []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const abrirGeneracion = () => {
  formGen.value = { fechaCorte: new Date().toISOString().split('T')[0], motivo: '' }
  modalGeneracion.value = true
}

const ejecutarGeneracion = async () => {
  generando.value = true
  try {
    await executeMutation(GENERAR_LIBRO_SOCIOS, {
      fechaCorte: formGen.value.fechaCorte || null,
      motivo: formGen.value.motivo || null,
    })
    modalGeneracion.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.message ?? 'Error al generar el libro'
  } finally {
    generando.value = false
  }
}

async function descargarPdf(s) {
  try {
    const resp = await fetch(`/api/secretaria/libro-socios/${s.id}/pdf`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!resp.ok) throw new Error('No se pudo descargar el PDF.')
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `libro_socios_${s.fechaCorte}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
  }
}

onMounted(cargar)
</script>
