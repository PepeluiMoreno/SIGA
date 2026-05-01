<template>
  <AppLayout title="Roles" subtitle="Roles del sistema y sus permisos">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-purple-50 rounded-lg shadow p-4 border border-purple-100">
        <p class="text-sm text-gray-500">Total roles</p>
        <p class="text-xl font-bold text-purple-600">{{ roles.length }}</p>
      </div>
      <div class="bg-green-50 rounded-lg shadow p-4 border border-green-100">
        <p class="text-sm text-gray-500">Activos</p>
        <p class="text-xl font-bold text-green-600">{{ rolesActivos }}</p>
      </div>
      <div class="bg-blue-50 rounded-lg shadow p-4 border border-blue-100">
        <p class="text-sm text-gray-500">Del sistema</p>
        <p class="text-xl font-bold text-blue-600">{{ rolesSistema }}</p>
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
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nivel</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permisos</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="r in roles" :key="r.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{{ r.codigo }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <div>{{ r.nombre }}</div>
              <div v-if="r.descripcion" class="text-xs text-gray-500">{{ r.descripcion }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="tipoClass(r.tipo)">{{ r.tipo }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ r.nivel }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ r.transacciones?.length || 0 }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="r.activo ? 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800' : 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'">
                {{ r.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
              <router-link
                :to="`/roles/${r.id}/permisos`"
                class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                Permisos
              </router-link>
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

const ROLES_QUERY = gql`
  query Roles {
    roles {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      activo
      sistema
      transacciones {
        id
      }
    }
  }
`

const loading = ref(false)
const error = ref('')
const roles = ref([])

const rolesActivos = computed(() => roles.value.filter((r) => r.activo).length)
const rolesSistema = computed(() => roles.value.filter((r) => r.sistema).length)

function tipoClass(tipo) {
  const map = {
    SISTEMA: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    ORGANIZACION: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    TERRITORIAL: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    FUNCIONAL: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    PERSONALIZADO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return map[tipo] || map.PERSONALIZADO
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(ROLES_QUERY)
    roles.value = (data.roles || []).slice().sort((a, b) => b.nivel - a.nivel)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando roles'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
