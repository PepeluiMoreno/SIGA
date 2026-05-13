<template>
  <AppLayout title="Acciones" subtitle="Eventos, reuniones, talleres y demás acciones de la organización">
    <!-- Cabecera -->
    <div class="flex items-center justify-end mb-6">
      <router-link
        to="/acciones/nueva"
        class="inline-flex items-center gap-2 h-10 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Nueva acción
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
        <option v-for="t in tiposAccion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
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
    <div v-else-if="!accionesFiltradas.length" class="py-12 text-center text-sm text-slate-400">
      No hay acciones que mostrar.
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
            v-for="accion in accionesFiltradas"
            :key="accion.id"
            class="hover:bg-slate-50 transition-colors"
          >
            <td class="px-4 py-3 font-medium text-slate-900">{{ accion.nombre }}</td>
            <td class="px-4 py-3 text-slate-500">{{ accion.tipoAccion?.nombre || '—' }}</td>
            <td class="px-4 py-3">
              <span
                v-if="accion.estado"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :style="accion.estado.color ? `background-color: ${accion.estado.color}22; color: ${accion.estado.color}` : ''"
                :class="!accion.estado.color ? 'bg-slate-100 text-slate-600' : ''"
              >
                {{ accion.estado.nombre }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ accion.fechaInicio || '—' }}</td>
            <td class="px-4 py-3 text-slate-500">{{ accion.iniciativa?.nombre || '—' }}</td>
            <td class="px-4 py-3">
              <RowActions
                :show-view="true"
                :show-edit="true"
                confirm-title="¿Eliminar esta acción?"
                :confirm-text="`«${accion.nombre}» será eliminada permanentemente.`"
                @view="$router.push(`/acciones/${accion.id}`)"
                @edit="$router.push(`/acciones/${accion.id}`)"
                @delete="(opts) => eliminarAccion(accion, opts)"
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
import { GET_ACCIONES, GET_TIPOS_ACCION, GET_ESTADOS_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION } from '../graphql/queries.js'

const loading = ref(true)
const acciones = ref([])
const tiposAccion = ref([])
const estadosAccion = ref([])
const filtroNombre = ref('')
const filtroTipo = ref('')
const filtroEstado = ref('')

const accionesFiltradas = computed(() => {
  let list = acciones.value
  if (filtroNombre.value) {
    const q = filtroNombre.value.toLowerCase()
    list = list.filter(a => a.nombre.toLowerCase().includes(q))
  }
  if (filtroTipo.value) {
    list = list.filter(a => a.tipoAccion?.id === filtroTipo.value)
  }
  if (filtroEstado.value) {
    list = list.filter(a => a.estado?.id === filtroEstado.value)
  }
  return list
})

async function cargar() {
  loading.value = true
  try {
    const [rAcciones, rTipos, rEstados] = await Promise.all([
      graphqlClient.request(GET_ACCIONES),
      graphqlClient.request(GET_TIPOS_ACCION),
      graphqlClient.request(GET_ESTADOS_ACCION),
    ])
    acciones.value = rAcciones.acciones || []
    tiposAccion.value = rTipos.tiposAccion || []
    estadosAccion.value = rEstados.estadosAccion || []
  } finally {
    loading.value = false
  }
}

async function eliminarAccion(accion, { hardDelete } = {}) {
  try {
    if (hardDelete) {
      await graphqlClient.request(ELIMINAR_ACCION, { id: accion.id })
    } else {
      await graphqlClient.request(SOFT_DELETE_ACCION, { id: accion.id })
    }
    acciones.value = acciones.value.filter(a => a.id !== accion.id)
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando acción')
  }
}

onMounted(cargar)
</script>
