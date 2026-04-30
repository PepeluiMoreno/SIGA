<template>
  <AppLayout title="Usuarios" subtitle="Gestión de usuarios del sistema SIGA">
    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">👥</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total usuarios</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">✅</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Activos</p>
            <p class="text-xl font-bold text-green-600">{{ resumen.activos }}</p>
          </div>
        </div>
      </div>
      <div class="bg-yellow-50 rounded-lg shadow p-4 border border-yellow-100">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-yellow-100 flex items-center justify-center mr-3">
            <span class="text-lg">🕒</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Acceso hoy</p>
            <p class="text-xl font-bold text-yellow-600">{{ resumen.activosHoy }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="mb-6 bg-white rounded-lg shadow p-4 border border-gray-100">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por email..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="filters.activo" class="border border-gray-300 rounded-lg px-3 py-2">
            <option value="">Todos</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600">Cargando usuarios...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden border border-gray-100">
      <div v-if="usuariosFiltrados.length === 0" class="text-center py-12">
        <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
          <span class="text-4xl">👤</span>
        </div>
        <h3 class="text-sm font-medium text-gray-900">No hay usuarios</h3>
        <p class="text-sm text-gray-500 mt-1">No se encontraron usuarios con los filtros seleccionados.</p>
      </div>

      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último acceso</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="u in usuariosFiltrados" :key="u.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                  <span class="text-sm font-medium text-purple-700">{{ iniciales(u.email) }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ u.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="u.activo ? 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800' : 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800'">
                {{ u.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatFecha(u.ultimoAcceso) }}
            </td>
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

const USUARIOS_QUERY = gql`
  query Usuarios {
    usuarios {
      id
      email
      activo
      ultimoAcceso
    }
  }
`

const loading = ref(false)
const error = ref('')
const usuarios = ref([])
const searchQuery = ref('')
const filters = ref({ activo: '' })

const usuariosFiltrados = computed(() => {
  return usuarios.value.filter((u) => {
    if (searchQuery.value && !u.email.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    if (filters.value.activo === 'true' && !u.activo) return false
    if (filters.value.activo === 'false' && u.activo) return false
    return true
  })
})

const resumen = computed(() => {
  const total = usuarios.value.length
  const activos = usuarios.value.filter((u) => u.activo).length
  const hoy = new Date().toISOString().slice(0, 10)
  const activosHoy = usuarios.value.filter((u) => u.ultimoAcceso?.slice(0, 10) === hoy).length
  return { total, activos, activosHoy }
})

function iniciales(email) {
  if (!email) return '??'
  return email.slice(0, 2).toUpperCase()
}

function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(USUARIOS_QUERY)
    usuarios.value = data.usuarios
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando usuarios'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
