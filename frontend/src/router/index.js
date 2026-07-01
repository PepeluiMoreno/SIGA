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

// === Módulo: ACTIVIDADES ===
import ListaGrupos from '@/modules/actividades/views/ListaGrupos.vue'

// === Módulo: ECONOMICO ===
import ListaEconomico from '@/modules/economico/views/ListaEconomico.vue'
import Tesoreria from '@/modules/economico/views/Tesoreria.vue'
import Contabilidad from '@/modules/economico/views/Contabilidad.vue'
import Cuotas from '@/modules/economico/views/Cuotas.vue'
import Remesas from '@/modules/economico/views/Remesas.vue'
import Recibos from '@/modules/economico/views/Recibos.vue'
import Conciliacion from '@/modules/economico/views/Conciliacion.vue'
import Cierre from '@/modules/economico/views/Cierre.vue'
import CuentasAnuales from '@/modules/economico/views/CuentasAnuales.vue'
import Modelo182 from '@/modules/economico/views/Modelo182.vue'
import ComunicacionFallidos from '@/modules/economico/views/ComunicacionFallidos.vue'
import CuotasEjercicio from '@/modules/economico/views/CuotasEjercicio.vue'
import MotivosReduccionCuota from '@/modules/economico/views/MotivosReduccionCuota.vue'
import Presupuesto from '@/modules/economico/views/Presupuesto.vue'
import Donaciones from '@/modules/economico/views/Donaciones.vue'
import ReglasContables from '@/modules/economico/views/ReglasContables.vue'

// === Módulo: MEMBRESIA - Voluntariado ===

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

// Conjunto de permisos OPERATIVOS del módulo económico: tener CUALQUIERA de ellos
// da acceso al panel de Tesorería y al índice económico (que son operativos, no
// "ver informes"). Cada sub-pantalla concreta (cuotas, remesas…) sigue exigiendo
// su permiso específico. `ECO_INFORME_FINANCIERO_VER` se incluye para que quien
// solo consulta informes también entre.
const ECO_OPERATIVO = [
  'ECO_CUOTA_LISTAR',
  'ECO_REMESA_LISTAR',
  'ECO_RECIBO_LISTAR',
  'ECO_DONACION_LISTAR',
  'ECO_JUSTIFICANTE_LISTAR',
  'ECO_CONCILIACION_LISTAR',
  'ECO_CUENTAS_ANUALES_LISTAR',
  'ECO_MODELO182_LISTAR',
  'ECO_ESTRUCTURA_CONTABLE_LISTAR',
  'ECO_INFORME_FINANCIERO_VER',
]

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
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_USUARIO_LISTAR' }
  },
  {
    path: '/usuarios/crear',
    component: () => import('@/modules/acceso/views/CrearUsuario.vue'),
    name: 'CrearUsuario',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_USUARIO_CREAR' }
  },
  {
    path: '/roles',
    component: () => import('@/modules/acceso/views/ListaRoles.vue'),
    name: 'Roles',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_ROL_LISTAR' }
  },
  {
    path: '/roles/nuevo',
    component: () => import('@/modules/acceso/views/FormularioRol.vue'),
    name: 'NuevoRol',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_ROL_CREAR' }
  },
  {
    path: '/roles/:id/editar',
    component: () => import('@/modules/acceso/views/FormularioRol.vue'),
    name: 'EditarRol',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_ROL_EDITAR' }
  },
  {
    path: '/roles/:id/permisos',
    component: () => import('@/modules/acceso/views/PermisosRol.vue'),
    name: 'PermisosRol',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_ROL_EDITAR' }
  },
  {
    path: '/transacciones',
    component: () => import('@/modules/acceso/views/ListaTransacciones.vue'),
    name: 'Transacciones',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_ROL_ASIGNAR' }
  },
  {
    path: '/auditoria',
    component: () => import('@/modules/acceso/views/LogAuditoria.vue'),
    name: 'Auditoria',
    meta: { requiresAuth: true, requiredPermission: 'ACCESO_AUDITORIA_LEER' }
  },

  // ─── MEMBRESIA ────────────────────────────────────────────────────────────
  {
    path: '/miembros',
    component: ListaMiembros,
    name: 'Miembros',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_MIEMBRO_LISTAR' }
  },
  {
    path: '/miembros/nuevo',
    component: () => import('@/modules/membresia/views/DetalleMiembro.vue'),
    name: 'NuevoMiembro',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_MIEMBRO_CREAR' }
  },
  {
    path: '/miembros/:id',
    component: () => import('@/modules/membresia/views/DetalleMiembro.vue'),
    name: 'DetalleMiembro',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_MIEMBRO_LISTAR' }
  },
  {
    // Directorio CRM contacto-céntrico (PF+PJ, vinculaciones). MVP: gateado con
    path: '/contactos',
    component: () => import('@/modules/membresia/views/ListaContactos.vue'),
    name: 'Contactos',
    meta: { requiresAuth: true, requiredPermission: 'CONTACTO_LISTAR' }
  },
  {
    path: '/contactos/nuevo',
    component: () => import('@/modules/membresia/views/DetalleContacto.vue'),
    name: 'NuevoContacto',
    meta: { requiresAuth: true, requiredPermission: 'CONTACTO_CREAR' }
  },
  {
    path: '/contactos/:id',
    component: () => import('@/modules/membresia/views/DetalleContacto.vue'),
    name: 'DetalleContacto',
    meta: { requiresAuth: true, requiredPermission: 'CONTACTO_VER' }
  },
  {
    path: '/agrupaciones',
    component: DetalleAgrupacionesTerritoriales,
    name: 'Agrupaciones',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_AGRUPACION_EDITAR' }
  },
  {
    path: '/agrupaciones/nueva',
    component: () => import('@/modules/membresia/views/DetalleAgrupacion.vue'),
    name: 'NuevaAgrupacion',
    meta: { requiresAuth: true, requiredPermission: 'CFG_TERRITORIO_CREAR' }
  },
  {
    path: '/agrupaciones/:id',
    component: () => import('@/modules/membresia/views/DetalleAgrupacion.vue'),
    name: 'DetalleAgrupacion',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_AGRUPACION_EDITAR' }
  },
  {
    path: '/agrupaciones/:id/junta',
    component: () => import('@/modules/acceso/views/GestionJunta.vue'),
    name: 'GestionJunta',
    meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_CARGO_ASIGNAR' }
  },

  // ─── ACTIVIDADES / GRUPOS ─────────────────────────────────────────────────
  {
    path: '/grupos',
    component: ListaGrupos,
    name: 'Grupos',
    meta: { requiresAuth: true, requiredPermission: 'GRUPO_LISTAR' }
  },
  {
    path: '/grupos/nuevo',
    component: () => import('@/modules/actividades/views/NuevoGrupo.vue'),
    name: 'NuevoGrupo',
    meta: { requiresAuth: true, requiredPermission: 'GRUPO_CREAR' }
  },
  {
    path: '/grupos/:id',
    component: () => import('@/modules/actividades/views/DetalleGrupo.vue'),
    name: 'DetalleGrupo',
    meta: { requiresAuth: true, requiredPermission: 'GRUPO_LISTAR' }
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
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_LISTAR' }
  },
  {
    path: '/actividades/nueva',
    component: () => import('@/modules/actividades/views/NuevaAccion.vue'),
    name: 'NuevaActividad',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CREAR' }
  },
  {
    path: '/actividades/:id',
    component: () => import('@/modules/actividades/views/DetalleAccion.vue'),
    name: 'DetalleActividad',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_LISTAR' }
  },

  // ─── COMUNICACIONES ───────────────────────────────────────────────────────
  {
    path: '/campanias',
    component: () => import('@/modules/comunicaciones/views/ListaCampanias.vue'),
    name: 'Campañas',
    meta: { requiresAuth: true, requiredPermission: 'CAMPANA_LISTAR' }
  },
  {
    path: '/chat',
    component: () => import('@/modules/comunicaciones/views/MisCanalesChat.vue'),
    name: 'MisCanalesChat',
    meta: { requiresAuth: true }
  },
  {
    path: '/campanias/nueva',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'NuevaCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMPANA_CREAR' }
  },
  {
    path: '/campanias/:id',
    component: () => import('@/modules/comunicaciones/views/DetalleCampania.vue'),
    name: 'DetalleCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMPANA_LISTAR' },
    props: true
  },
  {
    path: '/campanias/:id/editar',
    component: () => import('@/modules/comunicaciones/views/CampaniaForm.vue'),
    name: 'EditarCampania',
    meta: { requiresAuth: true, requiredPermission: 'CAMPANA_EDITAR' },
    props: true
  },
  {
    path: '/memoria-anual',
    component: () => import('@/modules/comunicaciones/views/MemoriaAnual.vue'),
    name: 'MemoriaAnual',
    meta: { requiresAuth: true, requiredPermission: 'CAMPANA_LISTAR' }
  },

  // ─── ECONOMICO ────────────────────────────────────────────────────────────
  { path: '/financiero', redirect: '/economico' },
  {
    path: '/economico',
    name: 'Economico',
    component: ListaEconomico,
    // Índice del módulo: abre con cualquier permiso económico de lectura/operación.
    meta: { requiresAuth: true, requiredPermission: ECO_OPERATIVO },
  },
  {
    path: '/economico/tesoreria',
    component: Tesoreria,
    name: 'Tesoreria',
    // Panel operativo de tesorería: abre con cualquier permiso operativo (no es solo informes).
    meta: { requiresAuth: true, requiredPermission: ECO_OPERATIVO }
  },
  {
    path: '/economico/contabilidad',
    component: Contabilidad,
    name: 'Contabilidad',
    meta: { requiresAuth: true, requiredPermission: ['ECO_ESTRUCTURA_CONTABLE_LISTAR', 'ECO_INFORME_FINANCIERO_VER'] }
  },
  {
    path: '/economico/reglas-contables',
    component: ReglasContables,
    // Configuración de reglas contables: es gestión, no "ver informes".
    meta: { requiresAuth: true, requiredPermission: 'ECO_ESTRUCTURA_CONTABLE_GESTIONAR' }
  },
  {
    path: '/economico/cuotas',
    component: Cuotas,
    name: 'Cuotas',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CUOTA_GENERAR' }
  },
  {
    path: '/economico/remesas',
    component: Remesas,
    name: 'Remesas',
    meta: { requiresAuth: true, requiredPermission: 'ECO_REMESA_CREAR' }
  },
  {
    path: '/economico/recibos',
    component: Recibos,
    name: 'Recibos',
    meta: { requiresAuth: true, requiredPermission: 'ECO_RECIBO_LISTAR' }
  },
  {
    path: '/economico/conciliacion',
    component: Conciliacion,
    name: 'Conciliacion',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CONCILIACION_LISTAR' }
  },
  {
    path: '/economico/cierre-ejercicio',
    component: Cierre,
    name: 'Cierre',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CIERRE_CONSULTAR' }
  },
  {
    path: '/economico/cuentas-anuales',
    component: CuentasAnuales,
    name: 'CuentasAnuales',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CUENTAS_ANUALES_LISTAR' }
  },
  {
    path: '/economico/modelo-182',
    component: Modelo182,
    name: 'Modelo182',
    meta: { requiresAuth: true, requiredPermission: 'ECO_MODELO182_LISTAR' }
  },
  {
    path: '/economico/comunicacion-fallidos',
    component: ComunicacionFallidos,
    name: 'ComunicacionFallidos',
    meta: { requiresAuth: true, requiredPermission: 'ECO_RECIBO_NOTIFICAR_FALLIDOS' }
  },
  {
    path: '/economico/cuotas-ejercicio',
    component: CuotasEjercicio,
    name: 'CuotasEjercicio',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CUOTA_CONFIGURAR' }
  },
  {
    path: '/parametrizacion/motivos-reduccion-cuota',
    component: MotivosReduccionCuota,
    name: 'MotivosReduccionCuota',
    meta: { requiresAuth: true, requiredPermission: 'ECO_CUOTA_MOTIVO_REDUCCION_GESTIONAR' }
  },
  {
    path: '/economico/presupuesto',
    component: Presupuesto,
    name: 'Presupuesto',
    meta: { requiresAuth: true, requiredPermission: 'ECO_INFORME_FINANCIERO_VER', requiereFeature: 'usaPresupuesto' }
  },
  {
    path: '/economico/presupuesto-evolucion',
    component: () => import('@/modules/economico/views/EvolucionPresupuestaria.vue'),
    name: 'EvolucionPresupuestaria',
    meta: { requiresAuth: true, requiredPermission: 'ECO_INFORME_FINANCIERO_VER', requiereFeature: 'usaPresupuesto' }
  },
  {
    path: '/economico/donaciones',
    component: Donaciones,
    name: 'Donaciones',
    meta: { requiresAuth: true, requiredPermission: 'ECO_DONACION_REGISTRAR' }
  },

  // ─── PRESIDENCIA ──────────────────────────────────────────────────────────
  {
    path: '/presidencia',
    component: PresidenciaDashboard,
    name: 'PresidenciaDashboard',
    meta: { requiresAuth: true, requiredPermission: 'PRESIDENCIA_CUADRO_MANDO_VER' }
  },
  {
    path: '/presidencia/mandatos',
    component: PresidenciaMandatos,
    name: 'PresidenciaMandatos',
    meta: { requiresAuth: true, requiredPermission: 'PRESIDENCIA_MANDATO_LISTAR' }
  },
  {
    path: '/presidencia/acuerdos',
    component: PresidenciaSeguimiento,
    name: 'PresidenciaSeguimiento',
    meta: { requiresAuth: true, requiredPermission: 'PRESIDENCIA_ACUERDO_SEGUIMIENTO_VER' }
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

  // ─── PROTECCIÓN DE DATOS (RGPD) ───────────────────────────────────────────
  {
    path: '/rgpd',
    component: () => import('@/modules/proteccion_datos/views/IndexRGPD.vue'),
    name: 'RGPDIndex',
    // Índice RGPD: abre con cualquier permiso de lectura de protección de datos.
    meta: { requiresAuth: true, requiredPermission: ['RGPD_RAT_LEER', 'RGPD_SOLICITUD_LEER', 'RGPD_CONSENTIMIENTO_LEER', 'RGPD_BRECHA_LEER', 'RGPD_AUDITORIA_LEER'] },
  },
  {
    path: '/rgpd/encargados',
    component: () => import('@/modules/proteccion_datos/views/Encargados.vue'),
    name: 'RGPDEncargados',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_RAT_LEER' },
  },
  {
    path: '/rgpd/actividades',
    component: () => import('@/modules/proteccion_datos/views/ActividadesTratamiento.vue'),
    name: 'RGPDActividades',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_RAT_LEER' },
  },
  {
    path: '/rgpd/clausulas',
    component: () => import('@/modules/proteccion_datos/views/Clausulas.vue'),
    name: 'RGPDClausulas',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_CLAUSULA_GESTIONAR' },
  },
  {
    path: '/rgpd/consentimientos',
    component: () => import('@/modules/proteccion_datos/views/Consentimientos.vue'),
    name: 'RGPDConsentimientos',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_CONSENTIMIENTO_LEER' },
  },
  {
    path: '/rgpd/solicitudes',
    component: () => import('@/modules/proteccion_datos/views/Solicitudes.vue'),
    name: 'RGPDSolicitudes',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_SOLICITUD_LEER' },
  },
  {
    path: '/rgpd/brechas',
    component: () => import('@/modules/proteccion_datos/views/Brechas.vue'),
    name: 'RGPDBrechas',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_BRECHA_LEER' },
  },
  {
    path: '/rgpd/auditoria',
    component: () => import('@/modules/proteccion_datos/views/Auditoria.vue'),
    name: 'RGPDAuditoria',
    meta: { requiresAuth: true, requiredPermission: 'RGPD_AUDITORIA_LEER' },
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
    meta: { requiresAuth: true, requiredPermission: 'CFG_CONFIGURACION_LEER' }
  },
  {
    path: '/parametrizacion',
    redirect: '/parametrizacion/catalogos',
  },
  {
    path: '/parametrizacion/catalogos',
    component: () => import('@/modules/configuracion/views/GestorCatalogos.vue'),
    name: 'Catalogos',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/tipos-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/TiposMiembro.vue'),
    name: 'TiposMiembro',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/estados-miembro',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosMiembro.vue'),
    name: 'EstadosMiembro',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/motivos-baja',
    component: () => import('@/modules/configuracion/views/catalogos/MotivosBaja.vue'),
    name: 'MotivosBaja',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/estados-cuota',
    component: () => import('@/modules/configuracion/views/catalogos/EstadosCuota.vue'),
    name: 'EstadosCuota',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/plataformas-telematicas',
    component: () => import('@/modules/configuracion/views/catalogos/PlataformasTelematicas.vue'),
    name: 'PlataformasTelematicas',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  // Catálogos de campañas
  {
    path: '/parametrizacion/tipos-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/TiposCampania.vue'),
    name: 'TiposCampania',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/estados-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/EstadosCampania.vue'),
    name: 'EstadosCampania',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/tipos-meta-campania',
    component: () => import('@/modules/comunicaciones/views/catalogos/TiposMetaCampania.vue'),
    name: 'TiposMetaCampania',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/canales-difusion',
    component: () => import('@/modules/comunicaciones/views/catalogos/CanalesDifusion.vue'),
    name: 'CanalesDifusion',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  // Plantillas de campaña
  {
    path: '/parametrizacion/plantillas-campania',
    component: () => import('@/modules/comunicaciones/views/PlantillasCampania.vue'),
    name: 'PlantillasCampania',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
  },
  {
    path: '/parametrizacion/plantillas-campania/:id',
    component: () => import('@/modules/comunicaciones/views/DetallePlantilla.vue'),
    name: 'DetallePlantilla',
    meta: { requiresAuth: true, requiredPermission: 'ACTIVIDAD_CATALOGO_GESTIONAR' }
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

// Rutas autenticadas universales: accesibles por cualquier usuario logueado SIN
// permiso específico (panel propio, datos propios, chat, ayuda, papelera). Son la
// ÚNICA excepción al default-deny del guard; cualquier otra ruta autenticada debe
// declarar `requiredPermission`.
const RUTAS_UNIVERSALES = new Set([
  '/',
  '/mis-datos',
  '/chat',
  '/ayuda',
  '/papelera',
])

// Guard de navegación
router.beforeEach(async (to, from, next) => {
  // El token vive en localStorage (Recordarme) o en sessionStorage
  const isAuthenticated = !!(localStorage.getItem('siga_token') || sessionStorage.getItem('siga_token'))
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

  // Comprobación de funcionalidad activada (feature flag de organización)
  if (to.meta.requiereFeature && isAuthenticated) {
    await orgConfigStore.fetchConfig()
    if (!orgConfigStore[to.meta.requiereFeature]) {
      next('/')
      return
    }
  }

  // Comprobación de permisos — DEFAULT-DENY.
  // Toda ruta autenticada debe declarar `requiredPermission` (string = un permiso,
  // o array = se exige tener ALGUNO). Si una ruta autenticada NO declara permiso y
  // NO está en la allowlist de rutas universales, se DENIEGA. Así un olvido futuro
  // bloquea en vez de abrir un agujero (seguro por construcción).
  if (to.meta.requiresAuth && isAuthenticated) {
    const permisos = usePermisos()
    if (!permisos.loaded.value) {
      await permisos.cargar()
    }
    const requerido = to.meta.requiredPermission
    if (requerido) {
      // string → un permiso; array → basta con tener alguno (OR).
      const ok = Array.isArray(requerido)
        ? permisos.tieneAlguno(...requerido)
        : permisos.tienePermiso(requerido)
      if (!ok) {
        next('/')
        return
      }
    } else if (!RUTAS_UNIVERSALES.has(to.path)) {
      // Ruta autenticada sin permiso declarado y fuera de la allowlist → denegar.
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
