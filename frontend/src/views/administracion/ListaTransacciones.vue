<template>
  <AppLayout title="Transacciones" subtitle="Catálogo de operaciones del sistema (RBAC)">

    <!-- Filtros -->
    <div class="mb-4 bg-white rounded-lg shadow p-4 border border-gray-100">
      <div class="flex flex-col md:flex-row gap-3">
        <div class="flex-1">
          <input
            v-model="busqueda"
            type="text"
            placeholder="Buscar por código o nombre..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
          />
        </div>
        <select v-model="filtroModulo" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">Todos los módulos</option>
          <option v-for="mod in modulos" :key="mod" :value="mod">{{ mod }}</option>
        </select>
        <select v-model="filtroTipo" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">Todos los tipos</option>
          <option value="QUERY">Query</option>
          <option value="MUTATION">Mutation</option>
        </select>
        <button
          v-if="busqueda || filtroModulo || filtroTipo"
          @click="busqueda = ''; filtroModulo = ''; filtroTipo = ''"
          class="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Limpiar
        </button>
      </div>
    </div>

    <!-- Resumen -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div class="bg-white rounded-lg shadow p-3 border border-gray-100 text-center">
        <p class="text-2xl font-bold text-purple-600">{{ transaccionesFiltradas.length }}</p>
        <p class="text-xs text-gray-500 mt-1">Mostradas</p>
      </div>
      <div class="bg-white rounded-lg shadow p-3 border border-gray-100 text-center">
        <p class="text-2xl font-bold text-blue-600">{{ totalQueries }}</p>
        <p class="text-xs text-gray-500 mt-1">Queries</p>
      </div>
      <div class="bg-white rounded-lg shadow p-3 border border-gray-100 text-center">
        <p class="text-2xl font-bold text-green-600">{{ totalMutations }}</p>
        <p class="text-xs text-gray-500 mt-1">Mutations</p>
      </div>
      <div class="bg-white rounded-lg shadow p-3 border border-gray-100 text-center">
        <p class="text-2xl font-bold text-gray-600">{{ modulos.length }}</p>
        <p class="text-xs text-gray-500 mt-1">Módulos</p>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600 text-sm">Cargando transacciones...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <!-- Vista agrupada por módulo -->
    <div v-else>
      <div v-if="transaccionesFiltradas.length === 0" class="bg-white rounded-lg shadow p-12 text-center border border-gray-100">
        <p class="text-gray-500">No se encontraron transacciones con los filtros aplicados.</p>
      </div>

      <div v-for="(txs, modulo) in porModulo" :key="modulo" class="mb-4">
        <div class="bg-white rounded-lg shadow border border-gray-100 overflow-hidden">
          <!-- Cabecera módulo -->
          <div class="px-4 py-3 bg-purple-50 border-b border-purple-100 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-purple-700 uppercase tracking-wider">{{ modulo }}</span>
              <span class="text-xs text-purple-500">({{ txs.length }})</span>
            </div>
          </div>

          <!-- Tabla -->
          <table class="min-w-full divide-y divide-gray-100">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-56">Código</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Tipo</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20 hidden md:table-cell">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="tx in txs" :key="tx.id" class="hover:bg-gray-50">
                <td class="px-4 py-2.5">
                  <code class="text-xs font-mono text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded">{{ tx.codigo }}</code>
                </td>
                <td class="px-4 py-2.5">
                  <p class="text-sm text-gray-900">{{ tx.nombre }}</p>
                  <p v-if="tx.descripcion" class="text-xs text-gray-500 mt-0.5">{{ tx.descripcion }}</p>
                </td>
                <td class="px-4 py-2.5">
                  <span
                    class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                    :class="tx.tipo === 'QUERY' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'"
                  >
                    {{ tx.tipo }}
                  </span>
                </td>
                <td class="px-4 py-2.5 hidden md:table-cell">
                  <span
                    class="inline-flex px-2 py-0.5 text-xs rounded-full"
                    :class="tx.activa ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  >
                    {{ tx.activa ? 'Activa' : 'Inactiva' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'

const QUERY = gql`
  query Transacciones {
    transacciones {
      id
      codigo
      nombre
      descripcion
      modulo
      tipo
      activa
      sistema
    }
  }
`

const loading = ref(false)
const error = ref('')
const transacciones = ref([])

const busqueda = ref('')
const filtroModulo = ref('')
const filtroTipo = ref('')

const modulos = computed(() => {
  const set = new Set(transacciones.value.map((t) => t.modulo))
  return [...set].sort()
})

const transaccionesFiltradas = computed(() => {
  return transacciones.value.filter((t) => {
    if (filtroModulo.value && t.modulo !== filtroModulo.value) return false
    if (filtroTipo.value && t.tipo !== filtroTipo.value) return false
    if (busqueda.value) {
      const q = busqueda.value.toLowerCase()
      return t.codigo.toLowerCase().includes(q) || t.nombre.toLowerCase().includes(q)
    }
    return true
  })
})

const porModulo = computed(() => {
  const grupos = {}
  for (const tx of transaccionesFiltradas.value) {
    if (!grupos[tx.modulo]) grupos[tx.modulo] = []
    grupos[tx.modulo].push(tx)
  }
  // Ordenar por módulo y dentro por código
  return Object.fromEntries(
    Object.entries(grupos)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([mod, txs]) => [mod, txs.sort((a, b) => a.codigo.localeCompare(b.codigo))])
  )
})

const totalQueries = computed(() => transaccionesFiltradas.value.filter((t) => t.tipo === 'QUERY').length)
const totalMutations = computed(() => transaccionesFiltradas.value.filter((t) => t.tipo === 'MUTATION').length)

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(QUERY)
    transacciones.value = data.transacciones || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando transacciones'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
