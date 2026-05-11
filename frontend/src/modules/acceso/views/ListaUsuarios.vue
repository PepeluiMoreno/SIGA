<template>
  <AppLayout title="Usuarios" subtitle="Usuarios con acceso a la aplicación">

    <!-- Filtros -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar por nombre, apellido o email…"
      create-label="Nuevo usuario"
      create-route="/usuarios/crear"
      :fields="filterFields"
      description="usuarios con acceso a SIGA"
      :lazy="true"
      :loading="loading"
      class="mb-4"
      @apply="applyClientFilters"
      @clear="limpiarFiltros"
    />

    <!-- Loading -->
    <EstadoCarga v-if="loading" mensaje="Cargando usuarios…" />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <p class="text-red-700 font-medium">Error al cargar datos</p>
      <p class="text-red-600 text-sm mt-1">{{ error.message || error }}</p>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="usuariosFiltrados.length === 0"
      class="bg-white border border-gray-200 rounded-lg p-12 text-center text-gray-500">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <p class="text-lg">No hay usuarios con los filtros seleccionados</p>
    </div>

    <!-- Tabla jerárquica -->
    <TablaJerarquica
      v-else
      :items="usuariosFiltrados"
      :agrupaciones="agrupaciones"
      descripcion="usuarios con acceso a la app"
      item-label="usuario"
      items-label="usuarios"
      :colspan="5"
      @limpiar="limpiarFiltros"
    >
      <template #row="{ item, depth }">
        <!-- Nombre miembro -->
        <td class="py-3 pr-4" :style="{ paddingLeft: (depth * 20 + 16) + 'px' }">
          <div class="flex items-center gap-3">
            <div class="h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-white text-xs font-medium bg-purple-500">
              {{ getInitials(item.nombre, item.apellido1) }}
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900">
                {{ item.apellido1 }}{{ item.apellido2 ? ' ' + item.apellido2 : '' }}, {{ item.nombre }}
              </div>
              <div class="flex items-center gap-2 mt-0.5">
                <span v-if="item.tipoMiembro" class="text-xs text-gray-400">{{ item.tipoMiembro.nombre }}</span>
              </div>
            </div>
          </div>
        </td>

        <!-- Email + activo -->
        <td class="px-4 py-3">
          <div class="text-sm text-gray-800">{{ item.usuario?.email || item.email || '—' }}</div>
          <span class="inline-flex mt-1 px-2 py-0.5 text-xs font-medium rounded-full"
            :class="item.usuario?.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
            {{ item.usuario?.activo ? 'Activo' : 'Inactivo' }}
          </span>
        </td>

        <!-- Roles -->
        <td class="px-4 py-3">
          <div class="flex flex-wrap gap-1">
            <span v-for="ur in (item.usuario?.roles ?? []).filter(r => r.activo !== false)" :key="ur.id"
              class="inline-flex items-center px-1.5 py-0.5 text-xs rounded-full border"
              :class="TIPO_ROL_BADGE[ur.rol?.tipo] ?? 'bg-gray-50 text-gray-600 border-gray-200'"
              :title="ur.rol?.nombre">
              {{ ur.rol?.nombre }}
            </span>
            <span v-if="!(item.usuario?.roles?.filter(r => r.activo !== false).length)" class="text-xs text-gray-400 italic">Sin roles</span>
          </div>
        </td>

        <!-- Último acceso -->
        <td class="px-4 py-3 text-sm text-gray-500">{{ formatFecha(item.usuario?.ultimoAcceso) }}</td>

        <!-- Acciones -->
        <td class="px-4 py-3 text-right">
          <button @click="abrirPanel(item)"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors"
            :class="panelMiembro?.id === item.id
              ? 'bg-purple-600 text-white border-purple-600'
              : 'text-purple-700 border-purple-200 bg-purple-50 hover:bg-purple-100'">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            Roles
          </button>
        </td>
      </template>
    </TablaJerarquica>

    <!-- ── Modal centrado: gestión de roles ─────────────────────────────── -->
    <Transition name="modal">
      <div v-if="panelMiembro"
        class="fixed inset-0 z-40 flex items-center justify-center p-4"
        @click.self="cerrarPanel">
      <div class="relative w-full max-w-lg max-h-[90vh] flex flex-col bg-white rounded-xl shadow-2xl border border-gray-200">

        <!-- Cabecera -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50 flex-shrink-0">
          <div class="flex items-center gap-3 min-w-0">
            <div class="h-9 w-9 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
              <span class="text-sm font-semibold text-purple-700">{{ getInitials(panelMiembro.nombre, panelMiembro.apellido1) }}</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ panelMiembro.apellido1 }} {{ panelMiembro.apellido2 || '' }}, {{ panelMiembro.nombre }}</p>
              <p class="text-xs text-gray-500 truncate">{{ panelMiembro.usuario?.email }}</p>
            </div>
          </div>
          <button @click="cerrarPanel" class="p-1.5 rounded-lg hover:bg-gray-200 transition-colors text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Buscador roles -->
        <div class="px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
          <div class="relative">
            <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input v-model="busquedaRol" type="text" placeholder="Buscar rol…"
              class="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none" />
          </div>
        </div>

        <!-- Error panel -->
        <div v-if="errorPanel"
          class="mx-4 mt-3 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 flex-shrink-0">
          {{ errorPanel }}
        </div>

        <!-- Lista de roles -->
        <div v-if="cargandoPanel" class="flex-1 flex items-center justify-center">
          <div class="h-6 w-6 rounded-full border-4 border-purple-500 border-t-transparent animate-spin"></div>
        </div>

        <div v-else class="flex-1 overflow-y-auto">
          <div v-for="grupo in rolesPorTipo" :key="grupo.tipo" class="mb-1">
            <div class="sticky top-0 z-10 flex items-center gap-2 px-4 py-1.5 bg-gray-50 border-b border-gray-100">
              <span class="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full"
                :class="TIPO_ROL_BADGE[grupo.tipo] ?? 'bg-gray-100 text-gray-600 border border-gray-200'">
                {{ TIPO_ROL_LABEL[grupo.tipo] ?? grupo.tipo }}
              </span>
              <span class="text-xs text-gray-400 ml-auto">{{ grupo.roles.length }} roles</span>
            </div>

            <div v-for="rol in grupo.roles" :key="rol.id"
              class="flex items-start gap-3 px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors">

              <div class="flex items-center pt-0.5">
                <button @click="toggleRol(rol)"
                  :disabled="pendienteRolId === rol.id"
                  class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none flex-shrink-0"
                  :class="estaAsignado(rol.id) ? 'bg-purple-600' : 'bg-gray-200'"
                  :title="estaAsignado(rol.id) ? 'Revocar rol' : 'Asignar rol'">
                  <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
                    :class="estaAsignado(rol.id) ? 'translate-x-4' : 'translate-x-0.5'"></span>
                  <span v-if="pendienteRolId === rol.id"
                    class="absolute inset-0 flex items-center justify-center">
                    <span class="h-3 w-3 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
                  </span>
                </button>
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900">{{ rol.nombre }}</span>
                  <code class="text-xs font-mono text-gray-400">{{ rol.codigo }}</code>
                </div>
                <p v-if="rol.descripcion" class="text-xs text-gray-500 mt-0.5 truncate">{{ rol.descripcion }}</p>

                <!-- Selector de territorio para roles TERRITORIAL -->
                <div v-if="estaAsignado(rol.id) && rol.tipo === 'TERRITORIAL' && agrupaciones.length > 0" class="mt-2">
                  <label class="block text-xs text-gray-500 mb-1">Territorio de aplicación</label>
                  <select
                    :value="agrupacionDeRolAsignado(rol.id)"
                    @change="cambiarAgrupacion(rol, $event.target.value || null)"
                    class="w-full text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none">
                    <option value="">Todos los territorios (global)</option>
                    <option v-for="ag in agrupaciones" :key="ag.id" :value="ag.id">{{ ag.nombre }}</option>
                  </select>
                </div>

                <div v-else-if="estaAsignado(rol.id) && agrupacionDeRolAsignado(rol.id)" class="mt-1">
                  <span class="inline-flex items-center gap-1 text-xs text-green-700 bg-green-50 border border-green-200 px-1.5 py-0.5 rounded">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    </svg>
                    {{ agrupacionNombre(agrupacionDeRolAsignado(rol.id)) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="rolesPorTipo.length === 0" class="text-center py-8 text-sm text-gray-400">
            No hay roles disponibles
          </div>
        </div>

      </div><!-- /inner modal box -->
      </div>
    </Transition>

    <!-- Overlay -->
    <Transition name="fade">
      <div v-if="panelMiembro" class="fixed inset-0 z-30 bg-black/40" @click="cerrarPanel"></div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import TablaJerarquica from '@/components/common/TablaJerarquica.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useGraphQL } from '@/composables/useGraphQL.js'
import { GET_MIEMBROS, GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import { GET_ROLES, ASIGNAR_ROL_USUARIO, REVOCAR_ROL_USUARIO } from '@/graphql/queries/administracion.js'
import { GET_TIPOS_VINCULACION } from '@/graphql/queries/usuarios.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'

const { loading, error, query } = useGraphQL()

// ── Estilos de roles ─────────────────────────────────────────────────────────
const TIPO_ROL_BADGE = {
  SISTEMA:       'bg-red-50 text-red-700 border border-red-200',
  FUNCIONAL:     'bg-purple-50 text-purple-700 border border-purple-200',
  TERRITORIAL:   'bg-green-50 text-green-700 border border-green-200',
  ORGANIZACION:  'bg-blue-50 text-blue-700 border border-blue-200',
  PERSONALIZADO: 'bg-gray-50 text-gray-600 border border-gray-200',
}
const TIPO_ROL_LABEL = {
  SISTEMA: 'Sistema', FUNCIONAL: 'Funcional', TERRITORIAL: 'Territorial',
  ORGANIZACION: 'Organización', PERSONALIZADO: 'Personalizado',
}
const TIPO_ROL_ORDEN = ['SISTEMA', 'FUNCIONAL', 'TERRITORIAL', 'ORGANIZACION', 'PERSONALIZADO']

// ── Datos ─────────────────────────────────────────────────────────────────────
const allMiembros      = ref([])   // todos los miembros con usuario
const agrupaciones     = ref([])   // árbol territorial
const todosRoles       = ref([])   // catálogo de roles para el panel
const tiposVinculacion = ref([])   // catálogo de tipos de vinculación

// ── UI ────────────────────────────────────────────────────────────────────────
const searchQuery = ref('')
const filters     = ref({ activo: false, agrupacion: '', tipoVinculacion: '' })

// Panel
const panelMiembro   = ref(null)
const panelRoles     = ref([])
const cargandoPanel  = ref(false)
const errorPanel     = ref('')
const busquedaRol    = ref('')
const pendienteRolId = ref(null)

// ── Computed: filtros ─────────────────────────────────────────────────────────
const agrupacionesJerarquicas = computed(() => {
  const lista = agrupaciones.value
  if (!lista.length) return []
  const buildTree = (padreId = null, nivel = 0) => {
    const hijos = lista
      .filter(a => a.agrupacionPadreId === padreId)
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    const resultado = []
    for (const ag of hijos) {
      const indent = '  '.repeat(nivel)
      resultado.push({ ...ag, displayNombre: indent + ag.nombre })
      resultado.push(...buildTree(ag.id, nivel + 1))
    }
    return resultado
  }
  return buildTree(null, 0)
})

const filterFields = computed(() => [
  {
    key: 'agrupacion',
    label: 'Agrupación',
    type: 'select',
    options: agrupacionesJerarquicas.value.map(a => ({ value: a.id, label: a.displayNombre })),
    allLabel: 'Todas las agrupaciones',
    width: 'w-72',
  },
  {
    key: 'tipoVinculacion',
    label: 'Tipo de vinculación',
    type: 'select',
    options: tiposVinculacion.value.map(t => ({ value: t.id, label: t.nombre })),
    allLabel: 'Todos los tipos',
    width: 'w-64',
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

  if (filters.value.tipoVinculacion) {
    list = list.filter(m => m.usuario?.tipoVinculacion?.id === filters.value.tipoVinculacion)
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

function agrupacionNombre(id) {
  if (!id) return ''
  return agrupaciones.value.find(a => a.id === id)?.nombre ?? id.slice(0, 8) + '…'
}

function estaAsignado(rolId) {
  return panelRoles.value.some(ur => ur.rol?.id === rolId)
}

function agrupacionDeRolAsignado(rolId) {
  return panelRoles.value.find(ur => ur.rol?.id === rolId)?.agrupacionId ?? null
}

// ── Panel de roles ────────────────────────────────────────────────────────────
const rolesPorTipo = computed(() => {
  const q = busquedaRol.value.trim().toLowerCase()
  const agrupados = {}
  for (const rol of todosRoles.value) {
    if (!rol.activo) continue
    if (q && !rol.nombre.toLowerCase().includes(q) && !rol.codigo.toLowerCase().includes(q)) continue
    const tipo = rol.tipo ?? 'PERSONALIZADO'
    if (!agrupados[tipo]) agrupados[tipo] = []
    agrupados[tipo].push(rol)
  }
  return TIPO_ROL_ORDEN.filter(t => agrupados[t]?.length).map(t => ({ tipo: t, roles: agrupados[t] }))
})

async function abrirPanel(miembro) {
  if (panelMiembro.value?.id === miembro.id) { cerrarPanel(); return }
  panelMiembro.value  = miembro
  panelRoles.value    = [...(miembro.usuario?.roles ?? [])]
  busquedaRol.value   = ''
  errorPanel.value    = ''
  pendienteRolId.value = null

  if (!todosRoles.value.length) {
    cargandoPanel.value = true
    try {
      const data = await graphqlClient.request(GET_ROLES)
      todosRoles.value = data.roles ?? []
    } finally {
      cargandoPanel.value = false
    }
  }
}

function cerrarPanel() {
  panelMiembro.value = null
  panelRoles.value   = []
}

async function toggleRol(rol) {
  if (pendienteRolId.value) return
  errorPanel.value    = ''
  pendienteRolId.value = rol.id
  const usuarioId = panelMiembro.value.usuario?.id
  if (!usuarioId) { pendienteRolId.value = null; return }

  try {
    if (estaAsignado(rol.id)) {
      await graphqlClient.request(REVOCAR_ROL_USUARIO, { usuarioId, rolId: rol.id })
      panelRoles.value = panelRoles.value.filter(ur => ur.rol?.id !== rol.id)
    } else {
      const res = await graphqlClient.request(ASIGNAR_ROL_USUARIO, { usuarioId, rolId: rol.id, agrupacionId: null })
      panelRoles.value.push({ id: res.asignarRolUsuario, agrupacionId: null, rol })
    }
    sincronizarMiembroLocal(panelMiembro.value.id)
  } catch (e) {
    errorPanel.value = e?.response?.errors?.[0]?.message ?? 'Error al cambiar el rol'
  } finally {
    pendienteRolId.value = null
  }
}

async function cambiarAgrupacion(rol, agrupacionId) {
  if (pendienteRolId.value) return
  errorPanel.value    = ''
  pendienteRolId.value = rol.id
  const usuarioId = panelMiembro.value.usuario?.id
  if (!usuarioId) { pendienteRolId.value = null; return }

  try {
    await graphqlClient.request(REVOCAR_ROL_USUARIO, { usuarioId, rolId: rol.id })
    const res = await graphqlClient.request(ASIGNAR_ROL_USUARIO, { usuarioId, rolId: rol.id, agrupacionId: agrupacionId || null })
    panelRoles.value = panelRoles.value.filter(ur => ur.rol?.id !== rol.id)
    panelRoles.value.push({ id: res.asignarRolUsuario, agrupacionId: agrupacionId || null, rol })
    sincronizarMiembroLocal(panelMiembro.value.id)
  } catch (e) {
    errorPanel.value = e?.response?.errors?.[0]?.message ?? 'Error al cambiar territorio'
  } finally {
    pendienteRolId.value = null
  }
}

function sincronizarMiembroLocal(miembroId) {
  const idx = allMiembros.value.findIndex(m => m.id === miembroId)
  if (idx !== -1) {
    allMiembros.value[idx] = {
      ...allMiembros.value[idx],
      usuario: { ...allMiembros.value[idx].usuario, roles: [...panelRoles.value] },
    }
  }
}

// ── Limpia filtros ────────────────────────────────────────────────────────────
function limpiarFiltros() {
  filters.value  = { activo: false, agrupacion: '', tipoVinculacion: '' }
  searchQuery.value = ''
}

function applyClientFilters() {}

// ── Carga inicial ─────────────────────────────────────────────────────────────
async function cargar() {
  try {
    const [miembrosData, agrupData, rolesData, vinculData] = await Promise.all([
      query(GET_MIEMBROS),
      query(GET_AGRUPACIONES),
      graphqlClient.request(GET_ROLES),
      graphqlClient.request(GET_TIPOS_VINCULACION),
    ])
    // Solo miembros con usuario
    allMiembros.value      = (miembrosData?.miembros ?? []).filter(m => m.usuario != null)
    agrupaciones.value     = agrupData?.agrupacionesTerritoriales ?? []
    todosRoles.value       = rolesData?.roles ?? []
    tiposVinculacion.value = (vinculData?.tiposVinculacion ?? []).filter(t => t.activo)
  } catch (e) {
    console.error('Error al cargar usuarios:', e)
  }
}

onMounted(cargar)
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
