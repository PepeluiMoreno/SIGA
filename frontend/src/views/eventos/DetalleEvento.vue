<template>
  <AppLayout :title="evento?.nombre || 'Evento'" subtitle="Detalle del evento">
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <div v-else-if="evento">
      <!-- Cabecera -->
      <div class="bg-white rounded-lg shadow p-6 mb-6 border border-gray-100">
        <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-2 mb-3">
              <span
                v-if="evento.tipoEvento"
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800"
              >{{ evento.tipoEvento.nombre }}</span>
              <span
                v-if="evento.estado"
                class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                :style="evento.estado.color ? `background:${evento.estado.color}22;color:${evento.estado.color}` : 'background:#f3f4f6;color:#374151'"
              >{{ evento.estado.nombre }}</span>
            </div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ evento.nombre }}</h1>
            <p v-if="evento.descripcionCorta" class="text-gray-600">{{ evento.descripcionCorta }}</p>
          </div>
          <div class="flex gap-2 flex-shrink-0">
            <router-link
              to="/eventos"
              class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              ← Volver
            </router-link>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Columna principal -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Descripción larga -->
          <div v-if="evento.descripcionLarga" class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h2 class="text-lg font-semibold text-gray-900 mb-3">Descripción</h2>
            <p class="text-gray-700 whitespace-pre-wrap">{{ evento.descripcionLarga }}</p>
          </div>

          <!-- Participantes / Inscripciones -->
          <div class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">
                Participantes
                <span class="ml-2 text-sm font-normal text-gray-500">
                  ({{ evento.participantes?.length ?? 0 }}
                  <template v-if="evento.aforoMaximo"> / {{ evento.aforoMaximo }}</template>)
                </span>
              </h2>
              <button
                v-if="evento.requiereInscripcion"
                class="px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100"
              >
                + Inscribir
              </button>
            </div>

            <div v-if="evento.participantes?.length === 0" class="text-sm text-gray-500 py-4 text-center">
              Sin inscripciones registradas
            </div>
            <table v-else class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Miembro</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="p in evento.participantes" :key="p.id" class="hover:bg-gray-50">
                  <td class="px-4 py-2">
                    {{ p.miembro?.nombre }} {{ p.miembro?.apellido1 }}
                    <span v-if="p.miembro?.email" class="block text-xs text-gray-400">{{ p.miembro.email }}</span>
                  </td>
                  <td class="px-4 py-2 text-gray-600">{{ p.rol }}</td>
                  <td class="px-4 py-2">
                    <span :class="p.confirmado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                      class="inline-flex px-2 py-0.5 text-xs rounded-full font-medium">
                      {{ p.confirmado ? 'Confirmado' : 'Pendiente' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Materiales (cartelería, infografías) -->
          <div class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Materiales</h2>
              <button class="px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100">
                + Añadir material
              </button>
            </div>

            <div v-if="!evento.materiales?.length" class="text-sm text-gray-500 py-4 text-center">
              Sin materiales adjuntos (carteles, infografías, programas...)
            </div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <a
                v-for="m in evento.materiales"
                :key="m.id"
                :href="m.url || '#'"
                :target="m.url ? '_blank' : undefined"
                class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <span class="text-2xl">{{ iconoMaterial(m.tipo) }}</span>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ m.nombre }}</p>
                  <p class="text-xs text-gray-500">{{ m.tipo }}</p>
                </div>
              </a>
            </div>
          </div>
        </div>

        <!-- Columna lateral -->
        <div class="space-y-6">

          <!-- Fechas y lugar -->
          <div class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Fecha y Lugar</h2>
            <div class="space-y-3 text-sm">
              <div class="flex items-start gap-2">
                <span class="text-lg mt-0.5">📅</span>
                <div>
                  <p class="font-medium text-gray-900">{{ formatFechaLarga(evento.fechaInicio) }}</p>
                  <p v-if="evento.fechaFin && evento.fechaFin !== evento.fechaInicio" class="text-gray-500">
                    hasta {{ formatFechaLarga(evento.fechaFin) }}
                  </p>
                  <p v-if="!evento.esTodoDia && evento.horaInicio" class="text-gray-600">
                    {{ evento.horaInicio }}<template v-if="evento.horaFin"> — {{ evento.horaFin }}</template>
                  </p>
                </div>
              </div>

              <div v-if="evento.lugar || evento.ciudad" class="flex items-start gap-2">
                <span class="text-lg mt-0.5">📍</span>
                <div>
                  <p class="font-medium text-gray-900">{{ evento.lugar }}</p>
                  <p v-if="evento.direccion" class="text-gray-500">{{ evento.direccion }}</p>
                  <p v-if="evento.ciudad" class="text-gray-500">{{ evento.ciudad }}</p>
                </div>
              </div>

              <div v-if="evento.esOnline" class="flex items-start gap-2">
                <span class="text-lg mt-0.5">🌐</span>
                <div>
                  <p class="font-medium text-gray-900">Online</p>
                  <a v-if="evento.urlOnline" :href="evento.urlOnline" target="_blank"
                    class="text-purple-600 hover:underline text-xs break-all">
                    {{ evento.urlOnline }}
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Organización -->
          <div class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Organización</h2>
            <div class="space-y-3 text-sm">
              <div v-if="evento.responsable" class="flex items-center gap-2">
                <span>👤</span>
                <div>
                  <p class="text-xs text-gray-500">Responsable</p>
                  <p class="font-medium text-gray-900">{{ evento.responsable.nombre }} {{ evento.responsable.apellido1 }}</p>
                </div>
              </div>
              <div v-if="evento.grupoOrganizador" class="flex items-center gap-2">
                <span>👥</span>
                <div>
                  <p class="text-xs text-gray-500">Grupo organizador</p>
                  <p class="font-medium text-gray-900">{{ evento.grupoOrganizador.nombre }}</p>
                </div>
              </div>
              <div v-if="evento.agrupacion" class="flex items-center gap-2">
                <span>🗺</span>
                <div>
                  <p class="text-xs text-gray-500">Ámbito territorial</p>
                  <p class="font-medium text-gray-900">{{ evento.agrupacion.nombre }}</p>
                </div>
              </div>
              <div v-if="evento.campania" class="flex items-center gap-2">
                <span>🚩</span>
                <div>
                  <p class="text-xs text-gray-500">Campaña de divulgación</p>
                  <router-link :to="`/campanias/${evento.campania.id}`" class="font-medium text-purple-600 hover:underline">
                    {{ evento.campania.nombre }}
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- Inscripciones info -->
          <div v-if="evento.requiereInscripcion" class="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Inscripciones</h2>
            <div class="space-y-2 text-sm">
              <div v-if="evento.aforoMaximo" class="flex justify-between">
                <span class="text-gray-500">Aforo máximo</span>
                <span class="font-medium">{{ evento.aforoMaximo }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Inscritos</span>
                <span class="font-medium">{{ evento.participantes?.length ?? 0 }}</span>
              </div>
              <div v-if="evento.aforoMaximo" class="flex justify-between">
                <span class="text-gray-500">Plazas libres</span>
                <span :class="plazasLibres <= 5 ? 'font-medium text-red-600' : 'font-medium text-green-600'">
                  {{ plazasLibres }}
                </span>
              </div>
              <div v-if="evento.fechaLimiteInscripcion" class="flex justify-between">
                <span class="text-gray-500">Límite inscripción</span>
                <span class="font-medium">{{ formatFechaLarga(evento.fechaLimiteInscripcion) }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery } from '@/graphql/client'
import { GET_EVENTO_BY_ID } from '@/graphql/queries/eventos.js'

const route = useRoute()
const loading = ref(false)
const error = ref('')
const evento = ref(null)

const plazasLibres = computed(() => {
  if (!evento.value?.aforoMaximo) return null
  return Math.max(0, evento.value.aforoMaximo - (evento.value.participantes?.length ?? 0))
})

function formatFechaLarga(fecha) {
  return new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  })
}

function iconoMaterial(tipo) {
  const iconos = {
    CARTEL: '🖼',
    INFOGRAFIA: '📊',
    PROGRAMA: '📋',
    VIDEO: '🎬',
    AUDIO: '🎵',
    DOCUMENTO: '📄',
  }
  return iconos[tipo?.toUpperCase()] || '📎'
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await executeQuery(GET_EVENTO_BY_ID, { id: route.params.id })
    evento.value = (data.eventos || [])[0] || null
    if (!evento.value) error.value = 'Evento no encontrado'
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando el evento'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
