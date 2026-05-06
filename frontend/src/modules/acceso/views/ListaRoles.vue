<template>
  <AppLayout title="Roles y permisos" subtitle="Roles del sistema, sus funcionalidades y transacciones autorizadas">

    <!-- Cabecera -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex gap-3">
        <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 text-center min-w-[80px]">
          <p class="text-lg font-bold text-purple-600">{{ roles.length }}</p>
          <p class="text-xs text-gray-500">Total</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 text-center min-w-[80px]">
          <p class="text-lg font-bold text-green-600">{{ roles.filter(r => r.activo).length }}</p>
          <p class="text-xs text-gray-500">Activos</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 text-center min-w-[80px]">
          <p class="text-lg font-bold text-blue-600">{{ roles.filter(r => r.sistema).length }}</p>
          <p class="text-xs text-gray-500">Sistema</p>
        </div>
      </div>
      <router-link to="/roles/nuevo"
        class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors">
        <PlusIcon class="w-4 h-4" />
        Nuevo rol
      </router-link>
    </div>

    <!-- Estado carga / error -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="h-8 w-8 rounded-full border-4 border-purple-600 border-t-transparent animate-spin"></div>
    </div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
      <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
    </div>

    <!-- Tabla -->
    <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-100">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Código</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Nombre</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Tipo</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">Nivel</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">Funcs.</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">Trans.</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">Activo</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="r in roles" :key="r.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 text-sm font-mono text-gray-700 whitespace-nowrap">
              {{ r.codigo }}
              <span v-if="r.sistema" class="ml-1.5 text-xs bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">sistema</span>
            </td>
            <td class="px-4 py-3">
              <div class="text-sm font-medium text-gray-900">{{ r.nombre }}</div>
              <div v-if="r.descripcion" class="text-xs text-gray-400 truncate max-w-xs">{{ r.descripcion }}</div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              <span :class="tipoBadge(r.tipo)" class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full">{{ r.tipo }}</span>
            </td>
            <td class="px-4 py-3 text-sm text-center text-gray-600">{{ r.nivel }}</td>
            <td class="px-4 py-3 text-sm text-center">
              <span :class="r.funcionalidades?.length ? 'text-gray-700' : 'text-amber-500 font-medium'">
                {{ r.funcionalidades?.length ?? 0 }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-center text-gray-600">{{ r.transacciones?.length ?? 0 }}</td>
            <td class="px-4 py-3 text-center">
              <button @click="toggleActivo(r)"
                :disabled="r.sistema || toggling === r.id"
                :title="r.sistema ? 'Los roles de sistema no se pueden desactivar' : (r.activo ? 'Desactivar' : 'Activar')"
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                :class="[r.activo ? 'bg-green-500' : 'bg-gray-300', (r.sistema || toggling === r.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer']">
                <span class="sr-only">{{ r.activo ? 'Activo' : 'Inactivo' }}</span>
                <span :class="r.activo ? 'translate-x-5' : 'translate-x-1'"
                  class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform shadow-sm"></span>
              </button>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right">
              <div class="flex items-center justify-end gap-1.5">
                <router-link :to="`/roles/${r.id}/editar`"
                  class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                  title="Editar rol y funcionalidades">
                  <PencilIcon class="w-3.5 h-3.5" />
                </router-link>
                <router-link :to="`/roles/${r.id}/permisos`"
                  class="p-1.5 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-md transition-colors"
                  title="Permisos granulares (transacciones directas)">
                  <KeyIcon class="w-3.5 h-3.5" />
                </router-link>
                <button v-if="!r.sistema" @click="confirmarEliminar(r)"
                  class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                  title="Eliminar">
                  <TrashIcon class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="roles.length === 0">
            <td colspan="8" class="px-4 py-12 text-center text-sm text-gray-400">No hay roles definidos</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal confirmar eliminar -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0 scale-95" enter-active-class="transition duration-150 ease-out"
        leave-to-class="opacity-0 scale-95" leave-active-class="transition duration-100 ease-in">
        <div v-if="modalEliminar" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="modalEliminar = false"></div>
          <div class="relative bg-white rounded-xl shadow-xl max-w-sm w-full p-6">
            <div class="flex items-center gap-3 mb-3">
              <div class="flex-shrink-0 w-9 h-9 rounded-full bg-red-100 flex items-center justify-center">
                <ExclamationTriangleIcon class="w-5 h-5 text-red-600" />
              </div>
              <h3 class="text-sm font-semibold text-gray-900">Eliminar rol</h3>
            </div>
            <p class="text-sm text-gray-600 mb-1">
              ¿Eliminar el rol <span class="font-semibold">{{ rolAEliminar?.nombre }}</span>?
            </p>
            <p class="text-xs text-gray-400 mb-5">Esta acción no se puede deshacer. Se perderán todas sus funcionalidades y permisos asignados.</p>
            <div class="flex justify-end gap-3">
              <button @click="modalEliminar = false"
                class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Cancelar
              </button>
              <button @click="eliminar" :disabled="eliminando"
                class="px-4 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center gap-2">
                <span v-if="eliminando" class="h-3.5 w-3.5 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
                {{ eliminando ? 'Eliminando…' : 'Eliminar' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_ROLES, ACTUALIZAR_ROL, ELIMINAR_ROL } from '@/graphql/queries/administracion.js'
import { PlusIcon, PencilIcon, TrashIcon, KeyIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const loading  = ref(false)
const error    = ref('')
const roles    = ref([])
const toggling = ref(null)

const modalEliminar = ref(false)
const rolAEliminar  = ref(null)
const eliminando    = ref(false)

const TIPO_BADGE = {
  SISTEMA:       'bg-purple-100 text-purple-800',
  ORGANIZACION:  'bg-blue-100 text-blue-800',
  TERRITORIAL:   'bg-green-100 text-green-800',
  FUNCIONAL:     'bg-yellow-100 text-yellow-800',
  PERSONALIZADO: 'bg-gray-100 text-gray-700',
}
function tipoBadge(tipo) { return TIPO_BADGE[tipo] ?? TIPO_BADGE.PERSONALIZADO }

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(GET_ROLES)
    roles.value = (data.roles ?? []).slice()
      .sort((a, b) => b.nivel - a.nivel || a.nombre.localeCompare(b.nombre, 'es'))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al cargar los roles'
  } finally {
    loading.value = false
  }
}

async function toggleActivo(rol) {
  if (rol.sistema || toggling.value) return
  toggling.value = rol.id
  const nuevoActivo = !rol.activo
  try {
    await graphqlClient.request(ACTUALIZAR_ROL, {
      data: { id: rol.id, activo: nuevoActivo },
    })
    const idx = roles.value.findIndex(r => r.id === rol.id)
    if (idx !== -1) roles.value[idx] = { ...roles.value[idx], activo: nuevoActivo }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al cambiar el estado'
  } finally {
    toggling.value = null
  }
}

function confirmarEliminar(rol) {
  rolAEliminar.value = rol
  modalEliminar.value = true
}

async function eliminar() {
  if (!rolAEliminar.value) return
  eliminando.value = true
  try {
    await graphqlClient.request(ELIMINAR_ROL, {
      filter: { id: { eq: rolAEliminar.value.id } },
    })
    roles.value = roles.value.filter(r => r.id !== rolAEliminar.value.id)
    modalEliminar.value = false
    rolAEliminar.value = null
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al eliminar el rol'
    modalEliminar.value = false
  } finally {
    eliminando.value = false
  }
}

onMounted(cargar)
</script>
