import { createRouter, createWebHistory } from 'vue-router'

// Importa las vistas
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'
import ListaMiembros from '@/views/miembros/ListaMiembros.vue'
import ListaCampanias from '@/views/campanias/ListaCampanias.vue'
import ListaGrupos from '@/views/grupos/ListaGrupos.vue'
import ListaFinanciero from '@/views/financiero/ListaFinanciero.vue'
import ListaVoluntarios from '@/views/voluntariado/ListaVoluntarios.vue'
import ListaUsuarios from '@/views/usuarios/ListaUsuarios.vue'
import ParametrizacionIndex from '@/views/parametrizacion/ParametrizacionIndex.vue'

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
  {
    path: '/miembros',
    component: ListaMiembros,
    name: 'Miembros',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias',
    component: ListaCampanias,
    name: 'Campañas',
    meta: { requiresAuth: true }
  },
  {
    path: '/grupos',
    component: ListaGrupos,
    name: 'Grupos',
    meta: { requiresAuth: true }
  },
  {
    path: '/financiero',
    component: ListaFinanciero,
    name: 'Financiero',
    meta: { requiresAuth: true }
  },
  {
    path: '/voluntarios',
    component: ListaVoluntarios,
    name: 'Voluntarios',
    meta: { requiresAuth: true }
  },
  {
    path: '/usuarios',
    component: ListaUsuarios,
    name: 'Usuarios',
    meta: { requiresAuth: true }
  },
  {
    path: '/miembros/:id',
    component: () => import('@/views/miembros/DetalleMiembro.vue'),
    name: 'DetalleMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias/:id',
    component: () => import('@/views/campanias/DetalleCampania.vue'),
    name: 'DetalleCampania',
    meta: { requiresAuth: true }
  },
  {
    path: '/grupos/:id',
    component: () => import('@/views/grupos/DetalleGrupo.vue'),
    name: 'DetalleGrupo',
    meta: { requiresAuth: true }
  },
    {
    path: '/campanias/nueva',
    component: () => import('@/views/campanias/CampaniaForm.vue'),
    name: 'NuevaCampania',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias/:id',
    component: () => import('@/views/campanias/DetalleCampania.vue'),
    name: 'DetalleCampania',
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/campanias/:id/editar',
    component: () => import('@/views/campanias/CampaniaForm.vue'),
    name: 'EditarCampania',
    meta: { requiresAuth: true },
    props: true
  },
  // Rutas de Administración
  {
    path: '/roles',
    component: () => import('@/views/administracion/ListaRoles.vue'),
    name: 'Roles',
    meta: { requiresAuth: true }
  },
  {
    path: '/auditoria',
    component: () => import('@/views/administracion/LogAuditoria.vue'),
    name: 'Auditoria',
    meta: { requiresAuth: true }
  },
  // Rutas de Parametrización
  {
    path: '/parametrizacion',
    component: ParametrizacionIndex,
    name: 'Parametrizacion',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/tipos-miembro',
    component: () => import('@/views/parametrizacion/catalogos/TiposMiembro.vue'),
    name: 'TiposMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/estados-miembro',
    component: () => import('@/views/parametrizacion/catalogos/EstadosMiembro.vue'),
    name: 'EstadosMiembro',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/motivos-baja',
    component: () => import('@/views/parametrizacion/catalogos/MotivosBaja.vue'),
    name: 'MotivosBaja',
    meta: { requiresAuth: true }
  },
  {
    path: '/parametrizacion/estados-cuota',
    component: () => import('@/views/parametrizacion/catalogos/EstadosCuota.vue'),
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

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
