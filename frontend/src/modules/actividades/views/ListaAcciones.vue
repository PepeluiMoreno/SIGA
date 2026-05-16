<template>
  <AppLayout title="Actividades" subtitle="Reuniones, asambleas, talleres y demás actividades de la organización">
    <div class="flex items-center justify-end mb-6">
      <router-link
        v-if="tienePermiso('ACT_CREATE')"
        to="/actividades/nueva"
        class="inline-flex items-center gap-2 h-10 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Nueva actividad
      </router-link>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3 mb-4">
      <input
        v-model="filtroNombre"
        type="text"
        placeholder="Buscar por nombre…"
        class="h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
      />
      <select
        v-model="filtroTipo"
        class="h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">Todos los tipos</option>
        <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
      </select>
      <select
        v-model="filtroEstado"
        class="h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">Todos los estados</option>
        <option v-for="e in estadosAccion" :key="e.id" :value="e.id">{{ e.nombre }}</option>
      </select>
    </div>

    <!-- Tabla -->
    <div v-if="loading" class="py-12 text-center text-sm text-slate-400">Cargando…</div>
    <div v-else-if="!actividadesFiltradas.length" class="py-12 text-center text-sm text-slate-400">
      No hay actividades que mostrar.
    </div>
    <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Nombre</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Tipo</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Estado</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Fecha</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Campaña</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="actividad in actividadesFiltradas"
            :key="actividad.id"
            class="hover:bg-slate-50 transition-colors"
          >
            <td class="px-4 py-3 font-medium text-slate-900">{{ actividad.nombre }}</td>
            <td class="px-4 py-3 text-slate-500">{{ actividad.tipoActividad?.nombre || '—' }}</td>
            <td class="px-4 py-3">
              <span
                v-if="actividad.estado"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :style="actividad.estado.color ? `background-color: ${actividad.estado.color}22; color: ${actividad.estado.color}` : ''"
                :class="!actividad.estado.color ? 'bg-slate-100 text-slate-600' : ''"
              >
                {{ actividad.estado.nombre }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ actividad.fechaInicio || '—' }}</td>
            <td class="px-4 py-3 text-slate-500">{{ actividad.campania?.nombre || '—' }}</td>
            <td class="px-4 py-3">
              <RowActions
                :show-view="true"
                :show-edit="true"
                confirm-title="¿Eliminar esta actividad?"
                :confirm-text="`«${actividad.nombre}» será eliminada permanentemente.`"
                @view="$router.push(`/actividades/${actividad.id}`)"
                @edit="$router.push(`/actividades/${actividad.id}`)"
                @delete="(opts) => eliminarActividad(actividad, opts)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import RowActions from '@/components/common/RowActions.vue'
import { graphqlClient } from '@/graphql/client'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_ACCIONES, GET_TIPOS_ACCION, GET_ESTADOS_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION } from '../graphql/queries.js'

const { tienePermiso } = usePermisos()
const loading = ref(true)
const actividades = ref([])
const tiposActividad = ref([])
const estadosAccion = ref([])
const filtroNombre = ref('')
const filtroTipo = ref('')
const filtroEstado = ref('')

const actividadesFiltradas = computed(() => {
  let list = actividades.value
  if (filtroNombre.value) {
    const q = filtroNombre.value.toLowerCase()
    list = list.filter(a => a.nombre.toLowerCase().includes(q))
  }
  if (filtroTipo.value) {
    list = list.filter(a => a.tipoActividad?.id === filtroTipo.value)
  }
  if (filtroEstado.value) {
    list = list.filter(a => a.estado?.id === filtroEstado.value)
  }
  return list
})

async function cargar() {
  loading.value = true
  try {
    const [rActividades, rTipos, rEstados] = await Promise.all([
      graphqlClient.request(GET_ACCIONES),
      graphqlClient.request(GET_TIPOS_ACCION),
      graphqlClient.request(GET_ESTADOS_ACCION),
    ])
    actividades.value = rActividades.actividades || []
    tiposActividad.value = rTipos.tiposActividad || []
    estadosAccion.value = rEstados.estadosAccion || []
  } finally {
    loading.value = false
  }
}

async function eliminarActividad(actividad, { hardDelete } = {}) {
  try {
    if (hardDelete) {
      await graphqlClient.request(ELIMINAR_ACCION, { id: actividad.id })
    } else {
      await graphqlClient.request(SOFT_DELETE_ACCION, { id: actividad.id })
    }
    actividades.value = actividades.value.filter(a => a.id !== actividad.id)
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando actividad')
  }
}

onMounted(cargar)
</script>
