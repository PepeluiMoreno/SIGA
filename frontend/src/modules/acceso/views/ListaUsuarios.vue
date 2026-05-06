<template>
  <AppLayout title="Usuarios" subtitle="Gestión de usuarios del sistema SIGA">

    <!-- Header -->
    <div class="flex justify-end mb-4">
      <router-link to="/usuarios/crear"
        class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition shadow-sm">
        <PlusIcon class="w-4 h-4" />
        Nuevo usuario
      </router-link>
    </div>

    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-purple-50 rounded-lg p-4 border border-purple-100">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <UsersIcon class="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p class="text-xs text-gray-500">Total usuarios</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-green-50 rounded-lg p-4 border border-green-100">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
            <CheckCircleIcon class="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p class="text-xs text-gray-500">Activos</p>
            <p class="text-xl font-bold text-green-600">{{ resumen.activos }}</p>
          </div>
        </div>
      </div>
      <div class="bg-amber-50 rounded-lg p-4 border border-amber-100">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-lg bg-amber-100 flex items-center justify-center">
            <ClockIcon class="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p class="text-xs text-gray-500">Acceso hoy</p>
            <p class="text-xl font-bold text-amber-600">{{ resumen.activosHoy }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="mb-4 bg-white rounded-lg border border-gray-200 p-3 flex flex-col md:flex-row md:items-center gap-3">
      <div class="relative flex-1">
        <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        <input v-model="searchQuery" type="text" placeholder="Buscar por email…"
          class="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none" />
      </div>
      <select v-model="filters.activo"
        class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-1 focus:ring-purple-500 focus:outline-none">
        <option value="">Todos</option>
        <option value="true">Activos</option>
        <option value="false">Inactivos</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="h-8 w-8 rounded-full border-4 border-purple-600 border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
    </div>

    <!-- Tabla -->
    <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div v-if="usuariosFiltrados.length === 0" class="text-center py-12 text-gray-400 text-sm">
        No hay usuarios con los filtros seleccionados.
      </div>
      <table v-else class="min-w-full divide-y divide-gray-100">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-12"></th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Roles</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Último acceso</th>
            <th class="px-4 py-2.5 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="u in usuariosFiltrados" :key="u.id"
            class="hover:bg-gray-50 transition-colors"
            :class="panelUsuario?.id === u.id ? 'bg-purple-50/50' : ''">
            <td class="px-4 py-3">
              <div class="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <span class="text-xs font-semibold text-purple-700">{{ iniciales(u.email) }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ u.email }}</td>
            <td class="px-4 py-3">
              <span class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                :class="u.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
                {{ u.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span v-for="ur in (u.roles ?? [])" :key="ur.id"
                  class="inline-flex items-center gap-1 px-1.5 py-0.5 text-xs rounded-full border"
                  :class="TIPO_ROL_BADGE[ur.rol?.tipo] ?? 'bg-gray-50 text-gray-600 border-gray-200'"
                  :title="ur.rol?.nombre">
                  {{ ur.rol?.nombre }}
                  <span v-if="ur.agrupacionId" class="text-gray-400"
                    :title="agrupacionNombre(ur.agrupacionId)">
                    · {{ agrupacionNombre(ur.agrupacionId, true) }}
                  </span>
                </span>
                <span v-if="!(u.roles?.length)" class="text-xs text-gray-400 italic">Sin roles</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm text-gray-500">{{ formatFecha(u.ultimoAcceso) }}</td>
            <td class="px-4 py-3 text-right">
              <button @click="abrirPanel(u)"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors"
                :class="panelUsuario?.id === u.id
                  ? 'bg-purple-600 text-white border-purple-600'
                  : 'text-purple-700 border-purple-200 bg-purple-50 hover:bg-purple-100'">
                <ShieldCheckIcon class="w-3.5 h-3.5" />
                Roles
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Panel lateral: gestión de roles ─────────────────────────────── -->
    <Transition name="panel">
      <div v-if="panelUsuario"
        class="fixed inset-y-0 right-0 z-40 w-[480px] max-w-full flex flex-col bg-white border-l border-gray-200 shadow-2xl">

        <!-- Cabecera del panel -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50 flex-shrink-0">
          <div class="flex items-center gap-3 min-w-0">
            <div class="h-9 w-9 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
              <span class="text-sm font-semibold text-purple-700">{{ iniciales(panelUsuario.email) }}</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ panelUsuario.email }}</p>
              <p class="text-xs text-gray-500">{{ panelRoles.length }} rol{{ panelRoles.length !== 1 ? 'es' : '' }} asignado{{ panelRoles.length !== 1 ? 's' : '' }}</p>
            </div>
          </div>
          <button @click="cerrarPanel" class="p-1.5 rounded-lg hover:bg-gray-200 transition-colors text-gray-400 hover:text-gray-600">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Buscador roles -->
        <div class="px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
            <input v-model="busquedaRol" type="text" placeholder="Buscar rol…"
              class="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none" />
          </div>
        </div>

        <!-- Error panel -->
        <div v-if="errorPanel"
          class="mx-4 mt-3 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 flex-shrink-0">
          {{ errorPanel }}
        </div>

        <!-- Lista de roles disponibles -->
        <div v-if="cargandoPanel" class="flex-1 flex items-center justify-center">
          <div class="h-6 w-6 rounded-full border-4 border-purple-500 border-t-transparent animate-spin"></div>
        </div>

        <div v-else class="flex-1 overflow-y-auto">
          <div v-for="grupo in rolesPorTipo" :key="grupo.tipo" class="mb-1">
            <!-- Cabecera de grupo tipo -->
            <div class="sticky top-0 z-10 flex items-center gap-2 px-4 py-1.5 bg-gray-50 border-b border-gray-100">
              <span class="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full"
                :class="TIPO_ROL_BADGE[grupo.tipo] ?? 'bg-gray-100 text-gray-600 border border-gray-200'">
                {{ TIPO_ROL_LABEL[grupo.tipo] ?? grupo.tipo }}
              </span>
              <span class="text-xs text-gray-400 ml-auto">{{ grupo.roles.length }} roles</span>
            </div>

            <!-- Roles del grupo -->
            <div v-for="rol in grupo.roles" :key="rol.id"
              class="flex items-start gap-3 px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors">

              <!-- Toggle asignación -->
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
                  <span v-if="!rol.activo"
                    class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">inactivo</span>
                </div>
                <p v-if="rol.descripcion" class="text-xs text-gray-500 mt-0.5 truncate">{{ rol.descripcion }}</p>

                <!-- Selector de territorio para roles TERRITORIAL -->
                <div v-if="estaAsignado(rol.id) && rol.tipo === 'TERRITORIAL' && agrupaciones.length > 0"
                  class="mt-2">
                  <label class="block text-xs text-gray-500 mb-1">Territorio de aplicación</label>
                  <select
                    :value="agrupacionDeRolAsignado(rol.id)"
                    @change="cambiarAgrupacion(rol, $event.target.value || null)"
                    class="w-full text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none">
                    <option value="">Todos los territorios (global)</option>
                    <option v-for="ag in agrupaciones" :key="ag.id" :value="ag.id">
                      {{ ag.nombre }}
                    </option>
                  </select>
                </div>

                <!-- Badge territorio si ya asignado con scope -->
                <div v-else-if="estaAsignado(rol.id) && agrupacionDeRolAsignado(rol.id)"
                  class="mt-1">
                  <span class="inline-flex items-center gap-1 text-xs text-green-700 bg-green-50 border border-green-200 px-1.5 py-0.5 rounded">
                    <MapPinIcon class="w-3 h-3" />
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

      </div>
    </Transition>

    <!-- Overlay para cerrar el panel -->
    <Transition name="fade">
      <div v-if="panelUsuario" class="fixed inset-0 z-30 bg-black/20" @click="cerrarPanel"></div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import {
  GET_ROLES,
  ASIGNAR_ROL_USUARIO,
  REVOCAR_ROL_USUARIO,
} from '@/graphql/queries/administracion.js'
import { GET_AGRUPACIONES_TERRITORIALES } from '@/graphql/queries/catalogos.js'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  UsersIcon,
  CheckCircleIcon,
  ClockIcon,
  ShieldCheckIcon,
  XMarkIcon,
  MapPinIcon,
} from '@heroicons/vue/24/outline'

// ── Constantes de estilo ───────────────────────────────────────────────────────
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

// ── Queries ───────────────────────────────────────────────────────────────────
const USUARIOS_QUERY = `
  query Usuarios {
    usuarios {
      id
      email
      activo
      ultimoAcceso
      roles {
        id
        agrupacionId
        rol {
          id
          codigo
          nombre
          tipo
          nivel
          activo
        }
      }
    }
  }
`

// ── Estado ─────────────────────────────────────────────────────────────────────
const loading    = ref(false)
const error      = ref('')
const usuarios   = ref([])
const searchQuery = ref('')
const filters    = ref({ activo: '' })

// Panel
const panelUsuario   = ref(null)   // usuario seleccionado
const panelRoles     = ref([])     // UsuarioRol[] del usuario en el panel
const cargandoPanel  = ref(false)
const errorPanel     = ref('')
const busquedaRol    = ref('')
const pendienteRolId = ref(null)  // rol en proceso de toggle

// Catálogos
const todosRoles    = ref([])
const agrupaciones  = ref([])

// ── Computed ────────────────────────────────────────────────────────────────────
const usuariosFiltrados = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return usuarios.value.filter(u => {
    if (q && !u.email.toLowerCase().includes(q)) return false
    if (filters.value.activo === 'true'  && !u.activo) return false
    if (filters.value.activo === 'false' &&  u.activo) return false
    return true
  })
})

const resumen = computed(() => {
  const total    = usuarios.value.length
  const activos  = usuarios.value.filter(u => u.activo).length
  const hoy      = new Date().toISOString().slice(0, 10)
  const activosHoy = usuarios.value.filter(u => u.ultimoAcceso?.slice(0, 10) === hoy).length
  return { total, activos, activosHoy }
})

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
  return TIPO_ROL_ORDEN
    .filter(t => agrupados[t]?.length)
    .map(t => ({ tipo: t, roles: agrupados[t] }))
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function iniciales(email) {
  return email ? email.slice(0, 2).toUpperCase() : '??'
}
function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? '—' : d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}
function agrupacionNombre(id, corto = false) {
  if (!id) return ''
  const ag = agrupaciones.value.find(a => a.id === id)
  if (!ag) return id.slice(0, 8) + '…'
  return corto ? (ag.nombreCorto || ag.nombre.slice(0, 6)) : ag.nombre
}
function estaAsignado(rolId) {
  return panelRoles.value.some(ur => ur.rol?.id === rolId)
}
function agrupacionDeRolAsignado(rolId) {
  return panelRoles.value.find(ur => ur.rol?.id === rolId)?.agrupacionId ?? null
}

// ── Carga principal ──────────────────────────────────────────────────────────
async function cargar() {
  loading.value = true
  error.value   = ''
  try {
    const data = await graphqlClient.request(USUARIOS_QUERY)
    usuarios.value = data.usuarios
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando usuarios'
  } finally {
    loading.value = false
  }
}

async function cargarCatalogos() {
  const [rolesData, agrupData] = await Promise.all([
    graphqlClient.request(GET_ROLES),
    graphqlClient.request(GET_AGRUPACIONES_TERRITORIALES),
  ])
  todosRoles.value   = rolesData.roles ?? []
  agrupaciones.value = (agrupData.agrupacionesTerritoriales ?? []).filter(a => a.activo)
}

// ── Panel ─────────────────────────────────────────────────────────────────────
async function abrirPanel(usuario) {
  if (panelUsuario.value?.id === usuario.id) {
    cerrarPanel()
    return
  }
  panelUsuario.value  = usuario
  panelRoles.value    = [...(usuario.roles ?? [])]
  busquedaRol.value   = ''
  errorPanel.value    = ''
  pendienteRolId.value = null

  if (!todosRoles.value.length) {
    cargandoPanel.value = true
    try {
      await cargarCatalogos()
    } finally {
      cargandoPanel.value = false
    }
  }
}

function cerrarPanel() {
  panelUsuario.value = null
  panelRoles.value   = []
}

// ── Toggle rol ─────────────────────────────────────────────────────────────────
async function toggleRol(rol) {
  if (pendienteRolId.value) return
  errorPanel.value    = ''
  pendienteRolId.value = rol.id

  const usuarioId = panelUsuario.value.id

  try {
    if (estaAsignado(rol.id)) {
      // Revocar
      await graphqlClient.request(REVOCAR_ROL_USUARIO, { usuarioId, rolId: rol.id })
      panelRoles.value = panelRoles.value.filter(ur => ur.rol?.id !== rol.id)
    } else {
      // Asignar (sin territorio por defecto; se puede cambiar después)
      const id = await graphqlClient.request(ASIGNAR_ROL_USUARIO, {
        usuarioId, rolId: rol.id, agrupacionId: null,
      })
      panelRoles.value.push({ id: id.asignarRolUsuario, agrupacionId: null, rol })
    }
    // Actualizar la tabla local sin recargar
    sincronizarUsuarioLocal(usuarioId)
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
  const usuarioId = panelUsuario.value.id

  try {
    // Revocar y volver a asignar con nuevo territorio
    await graphqlClient.request(REVOCAR_ROL_USUARIO, { usuarioId, rolId: rol.id })
    const id = await graphqlClient.request(ASIGNAR_ROL_USUARIO, {
      usuarioId, rolId: rol.id, agrupacionId: agrupacionId || null,
    })
    panelRoles.value = panelRoles.value.filter(ur => ur.rol?.id !== rol.id)
    panelRoles.value.push({ id: id.asignarRolUsuario, agrupacionId: agrupacionId || null, rol })
    sincronizarUsuarioLocal(usuarioId)
  } catch (e) {
    errorPanel.value = e?.response?.errors?.[0]?.message ?? 'Error al cambiar territorio'
  } finally {
    pendienteRolId.value = null
  }
}

function sincronizarUsuarioLocal(usuarioId) {
  const idx = usuarios.value.findIndex(u => u.id === usuarioId)
  if (idx !== -1) {
    usuarios.value[idx] = { ...usuarios.value[idx], roles: [...panelRoles.value] }
  }
}

// ── Init ───────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([cargar(), cargarCatalogos()])
})
</script>

<style scoped>
.panel-enter-active,
.panel-leave-active { transition: transform 0.25s ease, opacity 0.25s ease; }
.panel-enter-from,
.panel-leave-to    { transform: translateX(100%); opacity: 0; }

.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to     { opacity: 0; }
</style>
