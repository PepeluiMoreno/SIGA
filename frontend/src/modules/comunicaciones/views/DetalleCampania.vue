<template>
  <AppLayout :title="titulo" :subtitle="subtitulo">
    <div v-if="cargando" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-slate-600 text-sm">Cargando campaña...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-sm font-medium text-red-800">Error al cargar la campaña</p>
      <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
      <button @click="cargarTodo" class="mt-2 text-sm text-red-600 hover:text-red-500">Intentar de nuevo</button>
    </div>

    <div v-else-if="campania" class="bg-white rounded-lg shadow">
      <div class="px-6 pt-4">
        <DetailHeader fallback="/campanias" />
      </div>

      <!-- Pestañas -->
      <div class="border-b border-slate-200">
        <nav class="flex space-x-8 px-6" aria-label="Tabs">
          <button
            v-for="tab in pestanas"
            :key="tab.id"
            @click="tabActiva = tab.id"
            :class="[
              tabActiva === tab.id
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-1.5'
            ]"
          >
            {{ tab.nombre }}
            <span v-if="tab.contador != null" class="bg-slate-100 text-slate-700 text-xs font-medium px-2 py-0.5 rounded-full">
              {{ tab.contador }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Contenido -->
      <div class="p-6">
        <InformacionGeneralTab v-if="tabActiva === 'informacion'" :campania="campania" />

        <ActividadesTab v-else-if="tabActiva === 'actividades'" :actividades="actividades" />

        <!-- Equipos de trabajo -->
        <div v-else-if="tabActiva === 'equipos'" class="space-y-4">
          <div class="flex justify-between items-center">
            <p class="text-sm text-slate-500">Grupos de trabajo asignados a esta campaña</p>
            <router-link
              to="/grupos"
              class="text-sm text-indigo-600 hover:text-indigo-800"
            >Ver todos los grupos</router-link>
          </div>

          <div v-if="cargandoEquipos" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
          </div>

          <div v-else-if="grupos.length === 0" class="text-center py-12 border-2 border-dashed border-slate-200 rounded-lg">
            <p class="text-slate-500 text-sm">No hay equipos de trabajo asignados a esta campaña</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="grupo in grupos"
              :key="grupo.id"
              class="border border-slate-200 rounded-lg p-4 hover:border-indigo-300 hover:shadow-sm transition-all"
            >
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h4 class="font-medium text-slate-900">{{ grupo.nombre }}</h4>
                  <p class="text-xs text-slate-500 mt-0.5">{{ grupo.tipoGrupo?.nombre }}</p>
                </div>
                <span
                  :class="grupo.activo ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'"
                  class="text-xs font-medium px-2 py-0.5 rounded-full"
                >
                  {{ grupo.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </div>

              <div class="space-y-1 text-sm text-slate-600">
                <div v-if="grupo.coordinador" class="flex items-center gap-2">
                  <span class="text-slate-400">Coord.:</span>
                  <span>{{ grupo.coordinador.nombre }} {{ grupo.coordinador.apellido1 }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400">Miembros:</span>
                  <span>{{ grupo.miembros?.filter(m => m.activo).length ?? 0 }} activos</span>
                </div>
                <div v-if="grupo.fechaInicio" class="flex items-center gap-2">
                  <span class="text-slate-400">Inicio:</span>
                  <span>{{ formatFecha(grupo.fechaInicio) }}</span>
                </div>
              </div>

              <div class="mt-3 pt-3 border-t border-slate-100">
                <router-link
                  :to="`/grupos/${grupo.id}`"
                  class="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                >Ver equipo →</router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Participantes -->
        <div v-else-if="tabActiva === 'participantes'" class="space-y-4">
          <div class="flex justify-between items-center">
            <p class="text-sm text-slate-500">Personas registradas como participantes en esta campaña</p>
          </div>

          <div v-if="cargandoParticipantes" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
          </div>

          <div v-else-if="participantes.length === 0" class="text-center py-12 border-2 border-dashed border-slate-200 rounded-lg">
            <p class="text-slate-500 text-sm">No hay participantes registrados en esta campaña</p>
          </div>

          <div v-else>
            <!-- Resumen -->
            <div class="grid grid-cols-3 gap-4 mb-4">
              <div class="bg-slate-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-slate-800">{{ participantes.length }}</div>
                <div class="text-xs text-slate-500 mt-0.5">Total</div>
              </div>
              <div class="bg-green-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-green-700">{{ participantesConfirmados }}</div>
                <div class="text-xs text-slate-500 mt-0.5">Confirmados</div>
              </div>
              <div class="bg-indigo-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-indigo-700">{{ totalHoras }}</div>
                <div class="text-xs text-slate-500 mt-0.5">Horas totales</div>
              </div>
            </div>

            <!-- Tabla -->
            <div class="overflow-x-auto rounded-lg border border-slate-200">
              <table class="min-w-full divide-y divide-slate-200 text-sm">
                <thead class="bg-slate-50">
                  <tr>
                    <th class="px-4 py-3 text-left font-medium text-slate-600">Participante</th>
                    <th class="px-4 py-3 text-left font-medium text-slate-600">Rol</th>
                    <th class="px-4 py-3 text-left font-medium text-slate-600">Horas</th>
                    <th class="px-4 py-3 text-left font-medium text-slate-600">Estado</th>
                    <th class="px-4 py-3 text-left font-medium text-slate-600">Inscripción</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-slate-100">
                  <tr v-for="p in participantes" :key="p.id" class="hover:bg-slate-50">
                    <td class="px-4 py-3">
                      <span v-if="nombreMiembro(p.miembroId)" class="font-medium text-slate-800">
                        {{ nombreMiembro(p.miembroId) }}
                      </span>
                      <span v-else class="text-slate-400 text-xs font-mono">{{ p.miembroId?.slice(0,8) }}…</span>
                    </td>
                    <td class="px-4 py-3 text-slate-600">{{ p.rolParticipante?.nombre ?? '—' }}</td>
                    <td class="px-4 py-3 text-slate-600">{{ p.horasAportadas ?? '—' }}</td>
                    <td class="px-4 py-3">
                      <span
                        :class="p.confirmado ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                        class="text-xs font-medium px-2 py-0.5 rounded-full"
                      >
                        {{ p.confirmado ? 'Confirmado' : 'Pendiente' }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-slate-500">{{ formatFecha(p.fechaInscripcion) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <RecursosTab
          v-else-if="tabActiva === 'recursos'"
          :campania="campania"
          :grupos="grupos"
        />

        <ResultadosTab
          v-else-if="tabActiva === 'resultados'"
          :campania="campania"
        />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import DetailHeader from '@/components/common/DetailHeader.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_CAMPANIA } from '@/graphql/queries/campanias'

import InformacionGeneralTab from '@/components/campanias/tabs/InformacionGeneralTab.vue'
import ActividadesTab from '@/components/campanias/tabs/ActividadesTab.vue'
import ResultadosTab from '@/components/campanias/tabs/ResultadosTab.vue'
import RecursosTab from '@/components/campanias/tabs/RecursosTab.vue'

const GQL_GRUPOS_CAMPANIA = `
  query GruposCampania($campaniaId: UUID!) {
    gruposTrabajo(filter: { campaniaId: { eq: $campaniaId } }) {
      id
      nombre
      activo
      fechaInicio
      presupuestoAsignado
      presupuestoEjecutado
      tipoGrupo { id nombre }
      coordinador { id nombre apellido1 }
      miembros { id activo rolGrupo { nombre esCoordinador } }
      tareas { id titulo horasEstimadas horasReales estado { nombre } prioridad }
    }
  }
`

const GQL_PARTICIPANTES_CAMPANIA = `
  query ParticipantesCampania($campaniaId: UUID!) {
    participantesCampania(filter: { campaniaId: { eq: $campaniaId } }) {
      id
      miembroId
      rolParticipante { id nombre }
      horasAportadas
      confirmado
      fechaInscripcion
    }
  }
`

const GQL_MIEMBROS_NOMBRE = `
  query MiembrosNombre {
    miembros {
      id
      nombre
      apellido1
      apellido2
    }
  }
`

const route = useRoute()
const cargando = ref(true)
const error = ref(null)
const campania = ref(null)
const actividades = ref([])

const cargandoEquipos = ref(false)
const grupos = ref([])

const cargandoParticipantes = ref(false)
const participantes = ref([])
const miembrosMap = ref({})

const tabActiva = ref('informacion')

const ESTADOS_CIERRE = ['Finalizada', 'Cancelada']
const esCierre = computed(() => ESTADOS_CIERRE.includes(campania.value?.estado?.nombre))

const titulo = computed(() => campania.value?.nombre ?? '')
const subtitulo = computed(() => campania.value?.tipoCampania?.nombre ?? '')

const participantesConfirmados = computed(() => participantes.value.filter(p => p.confirmado).length)
const totalHoras = computed(() => {
  const s = participantes.value.reduce((acc, p) => acc + (parseFloat(p.horasAportadas) || 0), 0)
  return s % 1 === 0 ? s : s.toFixed(1)
})

const pestanas = computed(() => {
  const tabs = [
    { id: 'informacion', nombre: 'Información' },
    { id: 'actividades', nombre: 'Tareas', contador: actividades.value.length || null },
    { id: 'equipos', nombre: 'Equipos', contador: grupos.value.length || null },
    { id: 'participantes', nombre: 'Participantes', contador: participantes.value.length || null },
    { id: 'recursos', nombre: 'Recursos' },
  ]
  if (esCierre.value) tabs.push({ id: 'resultados', nombre: 'Resultados' })
  return tabs
})

function nombreMiembro(id) {
  const m = miembrosMap.value[id]
  if (!m) return null
  return [m.nombre, m.apellido1, m.apellido2].filter(Boolean).join(' ')
}

function formatFecha(f) {
  if (!f) return '—'
  try {
    return new Date(f).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return f }
}

async function cargarCampania() {
  cargando.value = true
  error.value = null
  try {
    const data = await graphqlClient.request(GET_CAMPANIA, { id: route.params.id })
    if (!data.campanias?.length) throw new Error('Campaña no encontrada')
    campania.value = data.campanias[0]
    actividades.value = campania.value.actividades || []
  } catch (err) {
    error.value = err
  } finally {
    cargando.value = false
  }
}

async function cargarEquipos() {
  cargandoEquipos.value = true
  try {
    const data = await graphqlClient.request(GQL_GRUPOS_CAMPANIA, { campaniaId: route.params.id })
    grupos.value = data.gruposTrabajo ?? []
  } catch (err) {
    console.error('Error cargando equipos:', err)
  } finally {
    cargandoEquipos.value = false
  }
}

async function cargarParticipantes() {
  cargandoParticipantes.value = true
  try {
    const [dataP, dataM] = await Promise.all([
      graphqlClient.request(GQL_PARTICIPANTES_CAMPANIA, { campaniaId: route.params.id }),
      graphqlClient.request(GQL_MIEMBROS_NOMBRE),
    ])
    participantes.value = dataP.participantesCampania ?? []
    const map = {}
    for (const m of dataM.miembros ?? []) map[m.id] = m
    miembrosMap.value = map
  } catch (err) {
    console.error('Error cargando participantes:', err)
  } finally {
    cargandoParticipantes.value = false
  }
}

async function cargarTodo() {
  await cargarCampania()
  if (!error.value) {
    cargarEquipos()
    cargarParticipantes()
  }
}

onMounted(cargarTodo)
</script>
