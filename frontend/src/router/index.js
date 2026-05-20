import { createRouter, createWebHistory } from 'vue-router'
import { useDebugStore } from '@/stores/debug.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { usePermisos } from '@/composables/usePermisos.js'

// Vistas globales (no pertenecen a un módulo específico)
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'
import MisDatos from '@/views/MisDatos.vue'

// === Módulo: ACCESO ===
import ListaUsuarios from '@/modules/acceso/views/ListaUsuarios.vue'

// === Módulo: MEMBRESIA ===
import ListaMiembros from '@/modules/membresia/views/ListaMiembros.vue'
import ListaAgrupaciones from '@/modules/membresia/views/ListaAgrupaciones.vue'
import DetalleAgrupacionesTerritoriales from '@/modules/membresia/views/DetalleAgrupacionesTerritoriales.vue'

// === Módulo: CONFIGURACION ===
import EstructuraOrganizativa from '@/views/parametrizacion/EstructuraOrganizativa.vue'

// === Módulo: ACTIVIDADES ===
import ListaGrupos from '@/modules/actividades/views/ListaGrupos.vue'

// === Módulo: ECONOMICO ===
import ListaFinanciero from '@/modules/economico/views/ListaFinanciero.vue'
import Tesoreria from '@/modules/economico/views/Tesoreria.vue'
import Contabilidad from '@/modules/economico/views/Contabilidad.vue'
import Cuotas from '@/modules/economico/views/Cuotas.vue'
import Remesas from '@/modules/economico/views/Remesas.vue'
import Presupuesto from '@/modules/economico/views/Presupuesto.vue'
import Donaciones from '@/modules/economico/views/Donaciones.vue'

// === Módulo: MEMBRESIA - Voluntariado ===
import ListaVoluntarios from '@/modules/membresia/views/ListaVoluntarios.vue'

// === Módulo: PRESIDENCIA ===
import PresidenciaDashboard from '@/modules/presidencia/views/Dashboard.vue'
import PresidenciaMandatos from '@/modules/presidencia/views/Mandatos.vue'
import PresidenciaSeguimiento from '@/modules/presidencia/views/SeguimientoAcuerdos.vue'

// === Módulo: SECRETARIA ===
import Reuniones from '@/modules/secretaria/views/Reuniones.vue'
import Actas from '@/modules/secretaria/views/Actas.vue'
import Acuerdos from '@/modules/secretaria/views/Acuerdos.vue'
import LibroSocios from '@/modules/secretaria/views/LibroSocios.vue'
import Convenios from '@/modules/secretaria/views/Convenios.vue'

// === Módulo: CONFIGURACION ===

// Configuración de rutas
const routes = [
  {
    path: '/',
    component: Dashboard,
    name: 'Dashboard',
    meta: { requiresAuth: true }
  },
  {
    path: '/mis-datos',
    component: MisDatos,
    name: 'MisDatos',
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    component: Login,
    name: 'Login',
    meta: { guest: true }
  },
  {
    path: '/inicializacion',
    component: () => import('@/views/Inicializacion.vue'),
    name: 'Inicializacion',
    meta: { public: true }
  },

  // ─── ACCESO ───────────────────────────────────────────────────────────────
  {
    path: '/usuarios',
    component: ListaUsuarios,
    name: 'Usuarios',
    meta: { requiresAuth: true, requiredPermission: 'USR_LIST' }
  },
  {
    path: '/usuarios/crear',
    component: () => import('@/modules/acceso/views/CrearUsuario.vue'),
    name: 'CrearUsuario',
    meta: { requiresAuth: true, requiredPermission: 'USR_CREATE' }
  },
  {
    path: '/roles',
    component: () => import('@/modules/acceso/views/ListaRoles.vue'),
    name: 'Roles',
    meta: { requiresAuth: true, requiredPermission: 'ROL_LIST' }
  },
  {
    path: '/roles/nuevo',
    component: () => import('@/modules/acceso/views/FormularioRol.vue'),
    name: 'NuevoRol',
    meta: { requiresAuth: true, requiredPermission: 'ROL_CREATE' }
  },
  {
    path: '/roles/:id/editar',
    component: () => import('@/modules/acceso/views/FormularioRol.vue'),
    name: 'EditarRol',
    meta: { requiresAuth: true, requiredPermission: 'ROL_EDIT' }
  },
  {
    path: '/roles/:id/permisos',
    component: () => import('@/modules/acceso/views/PermisosRol.vue'),
    name: 'PermisosRol',
    meta: { requiresAuth: true, requiredPermission: 'ROL_EDIT' }
  },
  {
    path: '/transacciones',
    component: () => import('@/modules/acceso/views/ListaTransacciones.vue'),
    name: 'Transacciones',
    meta: { requiresAuth: true, requiredPermission: 'PERM_ASSIGN' }
  },
  {
    path: '/auditoria',
    component: () => import('@/modules/acceso/views/LogAuditoria.vue'),
    name: 'Auditoria',
    meta: { requiresAuth: true, requiredPermission: 'AUD_VIEW' }
  },

  // ─── MEMBRESIA ────────────────────────────────────────────────────────────
  {
    path: '/miembros',
    component: ListaMiembros,
    name: 'Miembros',
    meta: { requiresAuth: true, requiredPermission: 'SOC_LIST' }
  },
  {
    path: '/miembros/nuevo',
    component: () => import('@/modules/membresia/views/DetalleMiembro.vue'),
    name: 'NuevoMiembro',
    meta: { requiresAuth: true, requiredPermission: 'SOC_CREATE' }
  },
  {
    path: '/miembros/:id',
    component: () => import('@/modules/membresia/views/DetalleMiembro.vue'),
    name: 'DetalleMiembro',
    meta: { requiresAuth: true, requiredPermission: 'SOC_LIST' }
  },
  {
    path: '/agrupaciones',
    component: DetalleAgrupacionesTerritoriales,
    name: 'Agrupaciones',
    meta: { requiresAuth: true, requiredPermission: 'AGR_EDIT' }
  },
  {
    path: '/configuracion/estructura',
    component: EstructuraOrganizativa,
    name: 'EstructuraOrganizativa',
    meta: { requiresAuth: true, requiredPermission: 'CFG_EDIT' }
  },
  {
    path: '/agrupaciones/:id',
    component: () => import('@/modules/membresia/views/DetalleAgrupacion.vue'),
    name: 'DetalleAgrupacion',
    meta: { requiresAuth: true }
  },
  {
    path: '/agrupaciones/:id/junta',
    component: () => import('@/modules/acceso/views/GestionJunta.vue'),
    name: 'GestionJunta',
    meta: { requiresAuth: true, requiredPermission: 'NOM_CREATE' }
  },
  {
    path: '/juntas',
    component: () => import('@/modules/membresia/views/JuntasDirectivas.vue'),
    name: 'JuntasDirectivas',
    meta: { requiresAuth: true, requiredPermission: 'NOM_CREATE' }
  },
  {
    path: '/voluntarios',
    component: ListaVoluntarios,
    name: 'Voluntarios',
    meta: { requiresAuth: true, requiredPermission: 'HAB_LIST' }
  },

  // ─── ACTIVIDADES / GRUPOS ─────────────────────────────────────────────────
  {
    path: '/grupos',
    component: ListaGrupos,
    name: 'Grupos',
    meta: { requiresAuth: true, requiredPermission: 'TEAM_LIST' }
  },
  {
    path: '/grupos/nuevo',
    component: () => import('@/modules/actividades/views/NuevoGrupo.vue'),
    name: 'NuevoGrupo',
    meta: { requiresAuth: true, requiredPermission: 'TEAM_CREATE' }
  },
  {
    path: '/grupos/:id',
    component: () => import('@/modules/actividades/views/DetalleGrupo.vue'),
    name: 'DetalleGrupo',
    meta: { requiresAuth: true, requiredPermission: 'TEAM_LIST' }
  },
  // Redirects legacy URLs
  { path: '/eventos', redirect: '/actividades' },
  { path: '/eventos/:id', redirect: to => `/actividades/${to.params.id}` },
  { path: '/acciones', redirect: '/actividades' },
  { path: '/acciones/nueva', redirect: '/actividades/nueva' },
  { path: '/acciones/:id', redirect: to => `/actividades/${to.params.id}` },
  {
    path: '/actividades',
    component: () => import('@/modules/actividades/views/ListaAcciones.vue'),
    name: 'Actividades',
    meta: { requiresAuth: true, requiredPermission: 'ACT_LIST' }
  },
  {
    path: '/actividades/nueva',
    component: () => import('@/modules/actividades/views/NuevaAccion.vue'),
    name: 'NuevaActividad',
    meta: { requiresAuth: true, requiredPermission: 'ACT_CREATE' }
  },
  {
    path: '/actividades/:id',
    component: () => import('@/modules/actividades/views/DetalleAccion.vue'),
    name: 'DetalleActividad',
    meta: { requiresAuth: true, requiredPermission: 'ACT_LIST' }
  },

  // ─── COMUNICACIONES ───────────────────────────────────────────────────────
  {
    path: '/campanias',
    component: () => import('@/modules/comunicaciones/views/ListaCampanias.vue'),
    name: 'Campañas',
    meta: { requiresAuth: true, requiredPermission: 'CAMP_LIST' }
  },
  {
    path: '/campanias/nueva',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'NuevaCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMP_CREATE' }
  },
  {
    path: '/campanias/:id',
    component: () => import('@/modules/comunicaciones/views/DetalleCampania.vue'),
    name: 'DetalleCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMP_LIST' },
    props: true
  },
  {
    path: '/campanias/:id/editar',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'EditarCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMP_EDIT' },
    props: true
  },
  {
    path: '/memoria-anual',
    component: () => import('@/modules/comunicaciones/views/MemoriaAnual.vue'),
    name: 'MemoriaAnual',
    meta: { requiresAuth: true, requiredPermission: 'CAMP_LIST' }
  },

  // ─── ECONOMICO ────────────────────────────────────────────────────────────
  { path: '/financiero', redirect: '/economico' },
  {
    path: '/economico/tesoreria',
    component: Tesoreria,
    name: 'Tesoreria',
    meta: { requiresAuth: true, requiredPermission: 'FIN_REPORTS' }
  },
  {
    path: '/economico/contabilidad',
    component: Contabilidad,
    name: 'Contabilidad',
    meta: { requiresAuth: true, requiredPermission: 'FIN_REPORTS' }
  },
  {
    path: '/economico/cuotas',
    component: Cuotas,
    name: 'Cuotas',
    meta: { requiresAuth: true, requiredPermission: 'CUOT_GENERATE' }
  },
  {
    path: '/economico/remesas',
    component: Remesas,
    name: 'Remesas',
    meta: { requiresAuth: true, requiredPermission: 'REM_CREATE' }
  },
  {
    path: '/economico/presupuesto',
    component: Presupuesto,
    name: 'Presupuesto',
    meta: { requiresAuth: true, requiredPermission: 'FIN_REPORTS' }
  },
  {
    path: '/economico/donaciones',
    component: Donaciones,
    name: 'Donaciones',
    meta: { requiresAuth: true, requiredPermission: 'DON_CREATE' }
  },

  // ─── PRESIDENCIA ──────────────────────────────────────────────────────────
  {
    path: '/presidencia',
    component: PresidenciaDashboard,
    name: 'PresidenciaDashboard',
    meta: { requiresAuth: true }
  },
  {
    path: '/presidencia/mandatos',
    component: PresidenciaMandatos,
    name: 'PresidenciaMandatos',
    meta: { requiresAuth: true }
  },
  {
    path: '/presidencia/acuerdos',
    component: PresidenciaSeguimiento,
    name: 'PresidenciaSeguimiento',
    meta: { requiresAuth: true }
  },

  // ─── SECRETARIA ───────────────────────────────────────────────────────────
  {
    path: '/secretaria/reuniones',
    component: Reuniones,
    name: 'Reuniones',
    meta: { requiresAuth: true, requiredPermission: 'SEC_REUNION_LISTAR' }
  },
  {
    path: '/secretaria/actas',
    component: Actas,
    name: 'Actas',
    meta: { requiresAuth: true, requiredPermission: 'SEC_ACTA_LISTAR' }
  },
  {
    path: '/secretaria/acuerdos',
    component: Acuerdos,
    name: 'Acuerdos',
    meta: { requiresAuth: true, requiredPermission: 'SEC_ACUERDO_LISTAR' }
  },
  {
    path: '/secretaria/libro-socios',
    component: LibroSocios,
    name: 'LibroSocios',
    meta: { requiresAuth: true, requiredPermission: 'SEC_LIBRO_SOCIOS_CONSULTAR' }
  },
  {
    path: '/secretaria/convenios',
    component: Convenios,
    name: 'Convenios',
    meta: { requiresAuth: true, requiredPermission: 'SEC_CONVENIO_LISTAR' }
  },
  // ─── PAPELERA ─────────────────────────────────────────────────────────────
  {
    path: '/papelera',
    component: () => import('@/views/PapeleraView.vue'),
    meta: { requiresAuth: true },
  },

  // ─── CONFIGURACION ────────────────────────────────────────────────────────
  {
    path: '/configuracion',
    redirect: '/configuracion/general',
  },
  {
    path: '/configuracion/general',
    component: () => import('@/modules/configuracion/views/ParametrosGenerales.vue'),
    name: 'ParametrosGenerales',
    meta: { requiresAuth: true, requiredPermission: 'CFG_VIEW' }
  },
  {
    path: '/parametrizacion',
    redirect: '/parametrizacion/catalogos',
  },
  {
    path: '/parametrizacion/catalogos',
    component: () => import('@/modules/configuracion/views/GestorCatalogos.vue'),
    name: 'Catalogos',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/tipos-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/TiposMiembro.vue'),
    name: 'TiposMiembro',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/estados-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosMiembro.vue'),
    name: 'EstadosMiembro',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/motivos-baja',
    component: () => import('@/modules/configuracion/views/catalogos/MotivosBaja.vue'),
    name: 'MotivosBaja',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/estados-cuota',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosCuota.vue'),
    name: 'EstadosCuota',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/temas',
    component: () => import('@/views/configuracion/TemasCatalogo.vue'),
    name: 'TemasCatalogo',
    meta: { requiresAuth: true, requiredPermission: 'CFG_EDIT' }
  },
  // Catálogos de campañas
  {
    path: '/parametrizacion/tipos-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/TiposCampania.vue'),
    name: 'TiposCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/estados-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/EstadosCampania.vue'),
    name: 'EstadosCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/tipos-meta-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/TiposMetaCampania.vue'),
    name: 'TiposMetaCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/canales-difusion',
    component: () => import('@/modules/comunicaciones/views/catalogos/CanalesDifusion.vue'),
    name: 'CanalesDifusion',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  // Plantillas de campaña
  {
    path: '/parametrizacion/plantillas-campania',
    component: () => import('@/modules/comunicaciones/views/PlantillasCampania.vue'),
    name: 'PlantillasCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/parametrizacion/plantillas-campania/:id',
    component: () => import('@/modules/comunicaciones/views/DetallePlantilla.vue'),
    name: 'DetallePlantilla',
    meta: { requiresAuth: true, requiredPermission: 'CAT_ACT_MANAGE' }
  },
  {
    path: '/ayuda',
    component: () => import('@/views/Ayuda.vue'),
    name: 'Ayuda',
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de navegación
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('siga_token')
  const debugStore = useDebugStore()
  const orgConfigStore = useOrgConfigStore()

  if (debugStore.enabled) {
    debugStore.refreshSnapshot()
    debugStore.addEvent('router.beforeEach', 'Evaluando navegación', {
      from: from.fullPath,
      to: to.fullPath,
      requiresAuth: Boolean(to.meta.requiresAuth),
      guest: Boolean(to.meta.guest),
      isAuthenticated,
    })
  }

  // Comprobación de inicialización (solo si el backend está disponible)
  if (to.name !== 'Inicializacion') {
    const initialized = await orgConfigStore.checkInitialized()
    if (initialized === false) {
      next('/inicializacion')
      return
    }
  } else {
    // Si ya está inicializado, no dejar entrar en /inicializacion
    const initialized = await orgConfigStore.checkInitialized()
    if (initialized) {
      next('/login')
      return
    }
    next()
    return
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.guest && isAuthenticated) {
    next('/')
    return
  }

  // Comprobación de permisos
  if (to.meta.requiredPermission && isAuthenticated) {
    const permisos = usePermisos()
    if (!permisos.loaded.value) {
      await permisos.cargar()
    }
    if (!permisos.tienePermiso(to.meta.requiredPermission)) {
      next('/')
      return
    }
  }

  next()
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
