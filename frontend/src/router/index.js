import { createRouter, createWebHistory } from 'vue-router'
import { useDebugStore } from '@/stores/debug.js'

// Vistas globales (no pertenecen a un módulo específico)
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'

// === Módulo: ACCESO ===
import ListaUsuarios from '@/modules/acceso/views/ListaUsuarios.vue'

// === Módulo: MEMBRESIA ===
import ListaMiembros from '@/modules/membresia/views/ListaMiembros.vue'
import ListaAgrupaciones from '@/modules/membresia/views/ListaAgrupaciones.vue'

// === Módulo: ACTIVIDADES ===
import ListaGrupos from '@/modules/actividades/views/ListaGrupos.vue'

// === Módulo: ECONOMICO ===
import ListaFinanciero from '@/modules/economico/views/ListaFinanciero.vue'

// === Módulo: MEMBRESIA - Voluntariado ===
import ListaVoluntarios from '@/modules/membresia/views/ListaVoluntarios.vue'

// === Módulo: CONFIGURACION ===
import ParametrizacionIndex from '@/modules/configuracion/views/ParametrizacionIndex.vue'

// Configuración de rutas
const routes = [
  {
    path: '/',
    component: Dashboard,
    name: 'Dashboard',
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    component: Login,
    name: 'Login',
    meta: { guest: true }
  },

  // ─── ACCESO ───────────────────────────────────────────────────────────────
  {
    path: '/usuarios',
    component: ListaUsuarios,
    name: 'Usuarios',
    meta: { requiresAuth: true }
  },
  {
    path: '/usuarios/crear',
    component: () => import('@/modules/acceso/views/CrearUsuario.vue'),
    name: 'CrearUsuario',
    meta: { requiresAuth: true }
  },
  {
    path: '/roles',
    component: () => import('@/modules/acceso/views/ListaRoles.vue'),
    name: 'Roles',
    meta: { requiresAuth: true }
  },
  {
    path: '/roles/:id/editor',
    component: () => import('@/modules/acceso/views/EditorRol.vue'),
    name: 'EditorRol',
    meta: { requiresAuth: true }
  },
  {
    path: '/roles/:id/permisos',
    component: () => import('@/modules/acceso/views/PermisosRol.vue'),
    name: 'PermisosRol',
    meta: { requiresAuth: true }
  },
  {
    path: '/transacciones',
    component: () => import('@/modules/acceso/views/ListaTransacciones.vue'),
    name: 'Transacciones',
    meta: { requiresAuth: true }
  },
  {
    path: '/auditoria',
    component: () => import('@/modules/acceso/views/LogAuditoria.vue'),
    name: 'Auditoria',
    meta: { requiresAuth: true }
  },

  // ─── MEMBRESIA ────────────────────────────────────────────────────────────
  {
    path: '/miembros',
    component: ListaMiembros,
    name: 'Miembros',
    meta: { requiresAuth: true }
  },
  {
    path: '/miembros/:id',
    component: () => import('@/modules/membresia/views/DetalleMiembro.vue'),
    name: 'DetalleMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/agrupaciones',
    component: ListaAgrupaciones,
    name: 'Agrupaciones',
    meta: { requiresAuth: true }
  },
  {
    path: '/agrupaciones/:id/junta',
    component: () => import('@/modules/acceso/views/GestionJunta.vue'),
    name: 'GestionJunta',
    meta: { requiresAuth: true }
  },
  {
    path: '/voluntarios',
    component: ListaVoluntarios,
    name: 'Voluntarios',
    meta: { requiresAuth: true }
  },

  // ─── ACTIVIDADES / GRUPOS ─────────────────────────────────────────────────
  {
    path: '/grupos',
    component: ListaGrupos,
    name: 'Grupos',
    meta: { requiresAuth: true }
  },
  {
    path: '/grupos/:id',
    component: () => import('@/modules/actividades/views/DetalleGrupo.vue'),
    name: 'DetalleGrupo',
    meta: { requiresAuth: true }
  },
  {
    path: '/eventos',
    component: () => import('@/modules/actividades/views/ListaEventos.vue'),
    name: 'Eventos',
    meta: { requiresAuth: true }
  },
  {
    path: '/eventos/:id',
    component: () => import('@/modules/actividades/views/DetalleEvento.vue'),
    name: 'DetalleEvento',
    meta: { requiresAuth: true }
  },

  // ─── COMUNICACIONES ───────────────────────────────────────────────────────
  {
    path: '/campanias',
    component: () => import('@/modules/comunicaciones/views/ListaCampanias.vue'),
    name: 'Campañas',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias/nueva',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'NuevaCampania',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias/:id',
    component: () => import('@/modules/comunicaciones/views/DetalleCampania.vue'),
    name: 'DetalleCampania',
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/campanias/:id/editar',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'EditarCampania',
    meta: { requiresAuth: true },
    props: true
  },

  // ─── ECONOMICO ────────────────────────────────────────────────────────────
  {
    path: '/financiero',
    component: ListaFinanciero,
    name: 'Financiero',
    meta: { requiresAuth: true }
  },

  // ─── CONFIGURACION ────────────────────────────────────────────────────────
  {
    path: '/parametrizacion',
    component: ParametrizacionIndex,
    name: 'Parametrizacion',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/tipos-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/TiposMiembro.vue'),
    name: 'TiposMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/estados-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosMiembro.vue'),
    name: 'EstadosMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/motivos-baja',
    component: () => import('@/modules/configuracion/views/catalogos/MotivosBaja.vue'),
    name: 'MotivosBaja',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/estados-cuota',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosCuota.vue'),
    name: 'EstadosCuota',
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de navegación para autenticación
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('siga_token')
  const debugStore = useDebugStore()

  if (debugStore.enabled) {
    debugStore.refreshSnapshot()
    debugStore.addEvent('router.beforeEach', 'Evaluando navegación', {
      from: from.fullPath,
      to: to.fullPath,
      requiresAuth: Boolean(to.meta.requiresAuth),
      guest: Boolean(to.meta.guest),
      isAuthenticated: Boolean(isAuthenticated),
    })
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

router.afterEach((to, from) => {
  const debugStore = useDebugStore()
  if (!debugStore.enabled) return

  debugStore.refreshSnapshot()
  debugStore.addEvent('router.afterEach', 'Navegación completada', {
    from: from.fullPath,
    to: to.fullPath,
  })
})

router.onError((error, to) => {
  const debugStore = useDebugStore()
  if (!debugStore.enabled) return

  debugStore.captureError('router.error', error, {
    to: to?.fullPath,
  })
})

export default router
