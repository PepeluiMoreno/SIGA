<template>
  <AppLayout title="Roles y permisos" subtitle="Roles del sistema, sus funcionalidades y transacciones autorizadas" fluid>

    <!-- Acción principal en el topbar (estándar global) -->
    <template v-if="tienePermiso('ACCESO_ROL_CREAR')" #actions>
      <router-link to="/roles/nuevo"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nuevo rol
      </router-link>
    </template>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

    <FilterRail storage-key="roles">
      <FilterBar
        vertical
        v-model="filters"
        v-model:search="busqueda"
        search-placeholder="Buscar por nombre o código…"
        :fields="filterFields"
        @clear="limpiarFiltros"
      />
    </FilterRail>

    <!-- Columna de resultados -->
    <div class="flex-1 min-w-0 w-full">

    <!-- Estado carga / error -->
    <EstadoCarga v-if="loading" />
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
      <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
    </div>

    <!-- Tabla -->
    <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="rolesFiltrados"
        :orden-inicial="{ key: 'nombre', dir: 'asc' }"
        vacio-texto="No hay roles definidos">

        <template #cell-nombre="{ fila: r }">
          <div class="flex items-center gap-1.5">
            <span class="text-sm font-medium text-gray-900">{{ r.nombre }}</span>
            <span v-if="r.sistema" class="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">sistema</span>
          </div>
          <!-- El código (clave técnica del rol) no se muestra en la lista: repite
               el nombre. Se edita en el formulario del rol, no aquí. La búsqueda
               por código sigue funcionando (ver `rolesFiltrados`). -->
          <div v-if="r.descripcion" class="text-xs text-gray-400 truncate">{{ r.descripcion }}</div>
        </template>

        <template #cell-tipo="{ fila: r }">
          <span :class="tipoBadge(r.tipo)" class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full">{{ r.tipo }}</span>
        </template>

        <template #cell-funcionalidades="{ fila: r }">
          <span :class="r.funcionalidades?.length ? 'text-gray-700' : 'text-amber-500 font-medium'">
            {{ r.funcionalidades?.length ?? 0 }}
          </span>
        </template>

        <template #cell-activo="{ fila: r }">
          <button @click.stop="toggleActivo(r)"
            :disabled="r.sistema || toggling === r.id"
            :title="r.sistema ? 'Los roles de sistema no se pueden desactivar' : (r.activo ? 'Desactivar' : 'Activar')"
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
            :class="[r.activo ? 'bg-green-500' : 'bg-gray-300', (r.sistema || toggling === r.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer']">
            <span class="sr-only">{{ r.activo ? 'Activo' : 'Inactivo' }}</span>
            <span :class="r.activo ? 'translate-x-5' : 'translate-x-1'"
              class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform shadow-sm"></span>
          </button>
        </template>

        <template #cell-acciones="{ fila: r }">
          <div class="flex items-center justify-end gap-1.5">
            <router-link :to="`/roles/${r.id}/editar`"
              class="p-1.5 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
              title="Editar rol, funcionalidades y permisos">
              <PencilIcon class="w-4 h-4" />
            </router-link>
            <button v-if="!r.sistema" @click.stop="confirmarEliminar(r)"
              class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
              title="Eliminar">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </template>
      </ResponsiveTable>
    </div>

    </div><!-- /columna de resultados -->
    </div><!-- /layout -->

    <!-- Modal confirmar eliminar -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0 scale-95" enter-active-class="transition duration-150 ease-out"
        leave-to-class="opacity-0 scale-95" leave-active-class="transition duration-100 ease-in">
        <div v-if="modalEliminar" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="modalEliminar = false"></div>
          <div class="relative bg-white rounded-xl shadow-xl max-w-sm w-full p-6">
            <div class="flex items-center gap-3 mb-3">
              <div class="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center"
                :class="borradoPermanente ? 'bg-red-100' : 'bg-amber-100'">
                <ExclamationTriangleIcon class="w-5 h-5" :class="borradoPermanente ? 'text-red-600' : 'text-amber-600'" />
              </div>
              <h3 class="text-sm font-semibold text-gray-900">
                {{ borradoPermanente ? 'Borrar rol definitivamente' : 'Enviar rol a la papelera' }}
              </h3>
            </div>
            <p class="text-sm text-gray-600 mb-1">
              ¿Eliminar el rol <span class="font-semibold">{{ rolAEliminar?.nombre }}</span>?
            </p>
            <p class="text-xs text-gray-400 mb-4">
              Se enviará a la papelera, desde donde podrás restaurarlo.
            </p>

            <!-- Escotilla de borrado físico: intencionado y explícito -->
            <label class="flex items-start gap-2 mb-5 p-2.5 rounded-lg border cursor-pointer transition-colors"
              :class="borradoPermanente ? 'border-red-300 bg-red-50' : 'border-gray-200 hover:bg-gray-50'">
              <input type="checkbox" v-model="borradoPermanente"
                class="mt-0.5 w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500" />
              <span class="text-xs" :class="borradoPermanente ? 'text-red-700' : 'text-gray-600'">
                <span class="font-semibold">Borrado permanente.</span>
                Elimina el rol de la base de datos junto con sus asignaciones a usuarios,
                funcionalidades y transacciones. <span class="font-semibold">No se puede deshacer.</span>
              </span>
            </label>

            <div class="flex justify-end gap-3">
              <button @click="modalEliminar = false"
                class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Cancelar
              </button>
              <button @click="eliminar" :disabled="eliminando"
                class="px-4 py-1.5 text-sm font-medium text-white rounded-lg disabled:opacity-50 transition-colors flex items-center gap-2"
                :class="borradoPermanente ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-600 hover:bg-amber-700'">
                <span v-if="eliminando" class="h-3.5 w-3.5 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
                {{ eliminando ? 'Eliminando…' : (borradoPermanente ? 'Borrar definitivamente' : 'Enviar a la papelera') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onActivated } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import { graphqlClient } from '@/graphql/client.js'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_ROLES, ACTUALIZAR_ROL, ELIMINAR_ROL } from '@/graphql/queries/administracion.js'
import { PencilIcon, TrashIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'

defineOptions({ name: 'ListaRoles' })

const { tienePermiso } = usePermisos()
const loading       = ref(false)
const error         = ref('')
const roles         = ref([])
const busqueda      = ref('')
const filters       = ref({ tipo: [], activo: [] })

const columnas = [
  { key: 'nombre',           label: 'Nombre',          ordenable: true },
  { key: 'tipo',             label: 'Tipo',            ordenable: true },
  { key: 'nivel',            label: 'Nivel',           align: 'center', ordenable: true },
  { key: 'funcionalidades',  label: 'Funcionalidades', align: 'center', ordenable: true,
    valorOrden: r => r.funcionalidades?.length ?? 0 },
  { key: 'transacciones',    label: 'Permisos',        align: 'center', ordenable: true,
    valorOrden: r => r.transacciones?.length ?? 0,
    formato: (_v, r) => r.transacciones?.length ?? 0 },
  { key: 'activo',           label: 'Activo',          align: 'center', ordenable: true },
  { key: 'acciones',         align: 'right', esAcciones: true },
]

// Filtros como checkboxes multiselección: son OR (marca «Sistema» y «Funcional»
// para ver ambos), y verlos todos a la vez dice qué se puede combinar.
const filterFields = [
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect', allLabel: 'Todos los tipos',
    options: [
      { value: 'SISTEMA',       label: 'Sistema' },
      { value: 'ORGANIZACION',  label: 'Organización' },
      { value: 'TERRITORIAL',   label: 'Territorial' },
      { value: 'FUNCIONAL',     label: 'Funcional' },
      { value: 'PERSONALIZADO', label: 'Personalizado' },
    ],
  },
  {
    key: 'activo', label: 'Estado', type: 'multiselect', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }],
  },
]

const rolesFiltrados = computed(() => {
  let lista = roles.value
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    lista = lista.filter(r => r.nombre?.toLowerCase().includes(q) || r.codigo?.toLowerCase().includes(q))
  }
  const tipos = filters.value.tipo || []
  if (tipos.length) lista = lista.filter(r => tipos.includes(r.tipo))
  const estados = filters.value.activo || []
  if (estados.length) lista = lista.filter(r => estados.includes(String(r.activo)))
  return lista
})
const toggling = ref(null)

const modalEliminar     = ref(false)
const rolAEliminar      = ref(null)
const eliminando        = ref(false)
const borradoPermanente = ref(false)

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
    // El orden lo gobierna ResponsiveTable (columnas ordenables).
    roles.value = data.roles ?? []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al cargar los roles'
  } finally {
    loading.value = false
  }
}

function limpiarFiltros() {
  busqueda.value = ''
  filters.value = { tipo: [], activo: [] }
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
  // Siempre desmarcado al abrir: el borrado permanente ha de reafirmarse.
  borradoPermanente.value = false
  modalEliminar.value = true
}

async function eliminar() {
  if (!rolAEliminar.value) return
  const id = rolAEliminar.value.id
  eliminando.value = true
  try {
    // El borrado lógico siempre precede al físico: el rol pasa por la papelera
    // aunque se haya pedido el borrado permanente.
    await graphqlClient.request(ELIMINAR_ROL, { id, hard: false })
    if (borradoPermanente.value) {
      await graphqlClient.request(ELIMINAR_ROL, { id, hard: true })
    }
    roles.value = roles.value.filter(r => r.id !== id)
    modalEliminar.value = false
    rolAEliminar.value = null
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al eliminar el rol'
    modalEliminar.value = false
  } finally {
    eliminando.value = false
  }
}

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso
// (p. ej. al volver de editar un rol), evitando mostrar datos obsoletos.
onActivated(cargar)
</script>
