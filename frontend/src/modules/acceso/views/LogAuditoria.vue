<template>
  <AppLayout title="Auditoría" subtitle="Registro de acciones del sistema">
    <div class="mb-6 bg-white rounded-lg shadow p-4 border border-gray-100">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por usuario, transacción o entidad..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="filtroAccion" class="border border-gray-300 rounded-lg px-3 py-2">
            <option value="">Todas</option>
            <option v-for="a in acciones" :key="a" :value="a">{{ a }}</option>
          </select>
          <select v-model="filtroExitoso" class="border border-gray-300 rounded-lg px-3 py-2">
            <option value="">Todas</option>
            <option value="true">Exitosas</option>
            <option value="false">Fallidas</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden border border-gray-100">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transacción</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entidad</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resultado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="l in logsFiltrados" :key="l.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-700">{{ formatFecha(l.fechaHora) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ l.usernameSnapshot || '—' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="accionClass(l.accion)">{{ l.accion }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-700">{{ l.transaccionCodigo || '—' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-700">{{ l.entidad || '—' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="l.exitoso ? 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800' : 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800'">
                {{ l.exitoso ? 'OK' : 'Error' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-700 max-w-xs truncate" :title="l.descripcion || ''">{{ l.descripcion || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'

const LOGS_QUERY = gql`
  query LogsAuditoria {
    logsAuditoria {
      id
      fechaHora
      usuarioId
      usernameSnapshot
      accion
      transaccionCodigo
      entidad
      entidadId
      exitoso
      mensajeError
      descripcion
      ipAddress
    }
  }
`

const loading = ref(false)
const error = ref('')
const logs = ref([])
const searchQuery = ref('')
const filtroAccion = ref('')
const filtroExitoso = ref('')

const acciones = ['CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'APROBAR', 'RECHAZAR', 'EXPORTAR', 'LOGIN', 'LOGOUT', 'OTRO']

const logsFiltrados = computed(() => {
  let r = logs.value
  if (filtroAccion.value) r = r.filter((l) => l.accion === filtroAccion.value)
  if (filtroExitoso.value === 'true') r = r.filter((l) => l.exitoso)
  if (filtroExitoso.value === 'false') r = r.filter((l) => !l.exitoso)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter((l) =>
      (l.usernameSnapshot || '').toLowerCase().includes(q) ||
      (l.transaccionCodigo || '').toLowerCase().includes(q) ||
      (l.entidad || '').toLowerCase().includes(q) ||
      (l.descripcion || '').toLowerCase().includes(q),
    )
  }
  return r.slice().sort((a, b) => (b.fechaHora || '').localeCompare(a.fechaHora || ''))
})

function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'medium' })
}

function accionClass(accion) {
  const map = {
    LOGIN: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    LOGOUT: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    CREAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    EDITAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    ELIMINAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    APROBAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    RECHAZAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
    EXPORTAR: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    VER: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    OTRO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return map[accion] || map.OTRO
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(LOGS_QUERY)
    logs.value = data.logsAuditoria || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando auditoría'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
