<template>
  <AppLayout title="Usuarios" subtitle="Usuarios con acceso a la aplicación" fluid>

    <!-- Acción principal en el topbar (estándar global) -->
    <template v-if="tienePermiso('ACCESO_USUARIO_CREAR')" #actions>
      <router-link to="/usuarios/crear"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nuevo usuario
      </router-link>
    </template>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

      <FilterRail storage-key="usuarios">
        <FilterBar
          vertical
          v-model="filters"
          v-model:search="searchQuery"
          search-placeholder="Buscar por nombre, apellido o email…"
          :fields="filterFields"
          @clear="limpiarFiltros"
        >
          <!-- Filtro por agrupación: buscador de texto (escribes el nombre y
               filtra), no un desplegable. Mismo componente que el panel de roles. -->
          <template #filters-prefix>
            <div>
              <span class="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Agrupación</span>
              <SelectorAgrupacion v-model="filters.agrupacion" :agrupaciones="agrupaciones" />
            </div>
          </template>
        </FilterBar>
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">

        <!-- Estado carga / error -->
        <EstadoCarga v-if="loading" mensaje="Cargando usuarios…" />
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          {{ error.message || error }}
          <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
        </div>

        <!-- Tabla -->
        <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <ResponsiveTable
            :columnas="columnas"
            :filas="usuariosFiltrados"
            :orden-inicial="{ key: 'nombre', dir: 'asc' }"
            vacio-texto="No hay usuarios con los filtros seleccionados">

            <!-- Miembro -->
            <template #cell-nombre="{ fila: item }">
              <div class="flex items-center gap-3">
                <div class="h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-white text-xs font-medium bg-purple-500">
                  {{ getInitials(item.nombre, item.apellido1) }}
                </div>
                <div class="min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">
                    {{ item.apellido1 }}{{ item.apellido2 ? ' ' + item.apellido2 : '' }}, {{ item.nombre }}
                  </div>
                  <div v-if="item.tipoMiembro" class="text-xs text-gray-400 truncate">{{ item.tipoMiembro.nombre }}</div>
                </div>
              </div>
            </template>

            <!-- Email (el estado activo/inactivo va en la columna «Acceso») -->
            <template #cell-email="{ fila: item }">
              <div class="text-sm text-gray-800 truncate">{{ item.usuario?.email || item.email || '—' }}</div>
            </template>

            <!-- Vinculación (la vigente del contacto). La etiqueta del tipo SOCIO
                 deriva de la denominación configurable de la membresía. -->
            <template #cell-vinculacion="{ fila: item }">
              <span v-if="item.vinculacionNombre"
                class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                {{ etiquetaVinculacion(item) }}
              </span>
              <span v-else class="text-xs text-gray-400">—</span>
            </template>

            <!-- Roles -->
            <template #cell-roles="{ fila: item }">
              <div class="flex flex-wrap gap-1">
                <span v-for="ur in (item.usuario?.roles ?? []).filter(r => r.activo !== false)" :key="ur.id"
                  class="inline-flex items-center px-1.5 py-0.5 text-xs rounded-full border"
                  :class="TIPO_ROL_BADGE[ur.rol?.tipo] ?? 'bg-gray-50 text-gray-600 border-gray-200'"
                  :title="ur.rol?.nombre">
                  {{ ur.rol?.nombre }}
                </span>
                <span v-if="!(item.usuario?.roles?.filter(r => r.activo !== false).length)" class="text-xs text-gray-400 italic">Sin roles</span>
              </div>
            </template>

            <!-- Último acceso -->
            <template #cell-ultimoAcceso="{ fila: item }">
              <span class="text-sm text-gray-500">{{ formatFecha(item.usuario?.ultimoAcceso) }}</span>
            </template>

            <!-- Acceso: toggle deslizante (muestra el estado y lo alterna), mismo
                 patrón que la columna «Activo» de ListaRoles. -->
            <template #cell-acceso="{ fila: item }">
              <button v-if="puedeEliminar(item.usuario)"
                @click.stop="toggleActivoUsuario(item.usuario)"
                :disabled="toggling === item.usuario.id"
                :title="item.usuario.activo ? 'Desactivar acceso' : 'Reactivar acceso'"
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                :class="[item.usuario.activo ? 'bg-green-500' : 'bg-gray-300', toggling === item.usuario.id ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer']">
                <span class="sr-only">{{ item.usuario.activo ? 'Activo' : 'Inactivo' }}</span>
                <span :class="item.usuario.activo ? 'translate-x-5' : 'translate-x-1'"
                  class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform shadow-sm"></span>
              </button>
              <!-- Cuentas protegidas (superadmin / propia): estado en texto, sin toggle -->
              <span v-else class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                :class="item.usuario?.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
                {{ item.usuario?.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </template>

            <!-- Acciones: iconos con tooltip, siempre visibles -->
            <template #cell-acciones="{ fila: item }">
              <div class="inline-flex items-center justify-end gap-1">
                <!-- Ver la ficha de la cuenta (página de detalle) -->
                <router-link :to="`/usuarios/${item.id}`" @click.stop
                  class="p-1.5 rounded-md transition-colors text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 inline-flex"
                  title="Ver ficha de la cuenta">
                  <EyeIcon class="w-4 h-4" />
                </router-link>

                <RowActions v-if="puedeEliminar(item.usuario)"
                  :show-edit="false"
                  confirm-title="¿Eliminar usuario permanentemente?"
                  confirm-title-soft="¿Mover usuario a la papelera?"
                  :confirm-text="`Usuario: ${item.usuario.email || item.usuario.username || ''}`"
                  @delete="(opts) => eliminarUsuario(item.usuario, opts)" />
              </div>
            </template>
          </ResponsiveTable>
        </div>

      </div><!-- /columna de resultados -->
    </div><!-- /layout -->

  </AppLayout>
</template>

<script setup>
import { EyeIcon } from '@heroicons/vue/24/outline'
import { ref, computed, onActivated } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import RowActions from '@/components/common/RowActions.vue'
import SelectorAgrupacion from '@/components/common/SelectorAgrupacion.vue'
import { graphqlClient } from '@/graphql/client.js'
import { usePermisos } from '@/composables/usePermisos.js'
import { useGraphQL } from '@/composables/useGraphQL.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { nombreTipoVinculacion } from '@/utils/tipoVinculacion.js'
import { useToast } from '@/composables/useToast'
import { GET_CUENTAS_ACCESO, GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import { GET_TIPOS_VINCULACION, ELIMINAR_USUARIO, DESACTIVAR_USUARIO, ACTIVAR_USUARIO } from '@/graphql/queries/usuarios.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'

defineOptions({ name: 'ListaUsuarios' })

const { tienePermiso } = usePermisos()
const { loading, error, query } = useGraphQL()
const orgConfig = useOrgConfigStore()
const toast = useToast()

// Etiqueta del tipo de vinculación derivando la denominación de la membresía
// (SOCIO → «Socio»/«Asociado»/…). El backend proyecta `vinculacionTipoCodigo`.
const etiquetaVinculacion = (m) =>
  m.vinculacionTipoCodigo
    ? nombreTipoVinculacion(m.vinculacionTipoCodigo, orgConfig, m.vinculacionNombre)
    : m.vinculacionNombre

// Badge de rol en la columna «Roles» (la gestión de roles vive en DetalleUsuario)
const TIPO_ROL_BADGE = {
  SISTEMA:       'bg-red-50 text-red-700 border border-red-200',
  FUNCIONAL:     'bg-purple-50 text-purple-700 border border-purple-200',
  TERRITORIAL:   'bg-green-50 text-green-700 border border-green-200',
  ORGANIZACION:  'bg-blue-50 text-blue-700 border border-blue-200',
  PERSONALIZADO: 'bg-gray-50 text-gray-600 border border-gray-200',
}

// ── Datos ─────────────────────────────────────────────────────────────────────
const allMiembros      = ref([])   // todos los miembros con usuario
const agrupaciones     = ref([])   // árbol territorial (filtro por agrupación)
const tiposVinculacion = ref([])   // catálogo de tipos de vinculación (filtro)

// ── UI ────────────────────────────────────────────────────────────────────────
const searchQuery = ref('')
const filters     = ref({ activo: false, agrupacion: '', tiposVinculacion: [] })

// ── Tabla ───────────────────────────────────────────────────────────────────
const columnas = [
  { key: 'nombre',       label: 'Nombre',         ordenable: true, anchoMax: 'none',
    valorOrden: m => `${m.apellido1 ?? ''} ${m.apellido2 ?? ''} ${m.nombre ?? ''}`.trim() },
  { key: 'email',        label: 'Email',          ordenable: true,
    valorOrden: m => m.usuario?.email || m.email || '' },
  { key: 'vinculacion',  label: 'Vinculación',    ordenable: true,
    valorOrden: m => m.vinculacionNombre || '' },
  { key: 'roles',        label: 'Roles' },
  { key: 'ultimoAcceso', label: 'Último acceso',  ordenable: true,
    valorOrden: m => m.usuario?.ultimoAcceso || '' },
  { key: 'acceso',       label: 'Acceso',         align: 'center', ordenable: true,
    valorOrden: m => (m.usuario?.activo ? 1 : 0) },
  { key: 'acciones',     align: 'right', esAcciones: true },
]

const filterFields = computed(() => [
  {
    key: 'tiposVinculacion',
    label: 'Tipo de vinculación',
    type: 'multiselect',
    options: tiposVinculacion.value.map(t => ({ value: t.id, label: t.nombre })),
    allLabel: 'Todos los tipos',
  },
  {
    key: 'activo',
    label: 'Solo activos',
    type: 'toggle',
  },
])

const getDescendantIds = (rootId) => {
  const ids = new Set()
  const queue = [rootId]
  while (queue.length) {
    const id = queue.shift()
    ids.add(id)
    agrupaciones.value.filter(a => a.agrupacionPadreId === id).forEach(a => queue.push(a.id))
  }
  return ids
}

const usuariosFiltrados = computed(() => {
  let list = allMiembros.value

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(m =>
      m.nombre?.toLowerCase().includes(q) ||
      m.apellido1?.toLowerCase().includes(q) ||
      m.apellido2?.toLowerCase().includes(q) ||
      m.usuario?.email?.toLowerCase().includes(q) ||
      m.email?.toLowerCase().includes(q)
    )
  }

  if (filters.value.activo) {
    list = list.filter(m => m.usuario?.activo === true)
  }

  if (filters.value.agrupacion) {
    const ids = getDescendantIds(filters.value.agrupacion)
    list = list.filter(m => m.agrupacion?.id && ids.has(m.agrupacion.id))
  }

  if (filters.value.tiposVinculacion?.length) {
    list = list.filter(m => filters.value.tiposVinculacion.includes(m.vinculacionTipoId))
  }

  return list
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function getInitials(nombre, apellido1) {
  return `${nombre?.[0] || ''}${apellido1?.[0] || ''}`.toUpperCase()
}

function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? '—' : d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}

// ── Limpia filtros ────────────────────────────────────────────────────────────
function limpiarFiltros() {
  filters.value  = { activo: false, agrupacion: '', tiposVinculacion: [] }
  searchQuery.value = ''
}

// ── Desactivar / eliminar usuario ─────────────────────────────────────────────
function puedeEliminar(usuario) {
  return !!usuario && usuario.username !== 'superadmin' && tienePermiso('ACCESO_USUARIO_ELIMINAR')
}

const toggling = ref(null)   // id del usuario cuyo acceso se está alternando
async function toggleActivoUsuario(usuario) {
  if (toggling.value) return
  const activando = !usuario.activo
  toggling.value = usuario.id
  try {
    await graphqlClient.request(activando ? ACTIVAR_USUARIO : DESACTIVAR_USUARIO, { id: usuario.id })
    toast.success(activando ? 'Acceso reactivado' : 'Acceso desactivado')
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || (activando ? 'No se pudo reactivar' : 'No se pudo desactivar'))
  } finally {
    toggling.value = null
  }
}

async function eliminarUsuario(usuario, opts) {
  try {
    await graphqlClient.request(ELIMINAR_USUARIO, { id: usuario.id, hard: !!opts?.hardDelete })
    toast.success(opts?.hardDelete ? 'Usuario eliminado permanentemente' : 'Usuario movido a la papelera')
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo eliminar')
  }
}

// ── Carga inicial ─────────────────────────────────────────────────────────────
async function cargar() {
  try {
    const [miembrosData, agrupData, vinculData] = await Promise.all([
      query(GET_CUENTAS_ACCESO),
      query(GET_AGRUPACIONES),
      graphqlClient.request(GET_TIPOS_VINCULACION),
    ])
    // cuentasAcceso ya devuelve solo cuentas de acceso (todas tienen usuario); el
    // filtro se mantiene como salvaguarda inocua.
    allMiembros.value      = (miembrosData?.miembros ?? []).filter(m => m.usuario != null)
    agrupaciones.value     = agrupData?.unidadesOrganizativas ?? []
    // Solo los tipos que pueden tener cuenta (SOCIO, VOLUNTARIO, EMPLEADO…): a un
    // donante o simpatizante no se le crea usuario, así que ofrecerlos como filtro
    // de usuarios no tiene sentido —ninguna fila casaría—. Mismo criterio que
    // CrearUsuario (`permiteCuenta`).
    tiposVinculacion.value = (vinculData?.tiposVinculacion ?? [])
      .filter(t => t.activo && t.permiteCuenta)
  } catch (e) {
    console.error('Error al cargar usuarios:', e)
  }
}

// La vista está en <keep-alive>: no se desmonta al navegar, así que `onMounted`
// solo correría una vez. `onActivated` cubre el primer montaje y cada regreso,
// evitando mostrar datos obsoletos.
onActivated(cargar)
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,
.modal-leave-to    { opacity: 0; }

.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to     { opacity: 0; }
</style>
