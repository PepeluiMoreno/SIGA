<template>
  <div class="min-h-screen" style="background-color: var(--t-page-bg)">
    <!-- Header -->
    <header class="shadow-sm border-b sticky top-0 z-20"
      style="background-color: var(--t-topbar); border-color: var(--t-border)">
      <div class="flex items-stretch h-16">
        <!-- Zona del logo: ancho del sidebar; su borde derecho prolonga hacia arriba el del sidebar -->
        <div class="flex items-center gap-3 shrink-0 px-4 lg:px-6 lg:w-64 lg:border-r" style="border-color: var(--t-border)">
          <button @click="sidebarOpen = !sidebarOpen"
            class="lg:hidden p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors">
            <XMarkIcon v-if="sidebarOpen" class="w-6 h-6" />
            <Bars3Icon v-else class="w-6 h-6" />
          </button>
          <img v-if="orgConfigStore.logo" :src="orgConfigStore.logo" alt="Logo organización"
            class="h-9 w-auto max-w-[160px] object-contain" />
        </div>

        <!-- Zona de contenido: título de la vista (izq) + acciones (der), alineado con el contenido -->
        <div class="flex-1 min-w-0 flex items-center gap-3 px-4 sm:px-6 lg:px-8">
          <div class="flex-1 min-w-0">
            <div v-if="title" class="flex items-center gap-3 min-w-0">
              <span v-if="icon" class="text-2xl leading-none shrink-0 select-none">{{ icon }}</span>
              <div class="min-w-0">
                <h1 class="text-xl font-bold text-slate-800 leading-tight truncate">{{ title }}</h1>
                <p v-if="subtitle" class="text-sm text-slate-400 leading-tight truncate">{{ subtitle }}</p>
              </div>
            </div>
          </div>

          <!-- Acciones de la vista (Nuevo…) + Volver + chrome global -->
          <div class="flex items-center gap-2 shrink-0">
            <slot name="actions" />
            <button v-if="canGoBack" type="button" @click="goBack"
              class="inline-flex items-center gap-1.5 h-8 px-3 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
              <ChevronLeftIcon class="w-3.5 h-3.5" />
              Volver
            </button>
            <span class="h-5 w-px bg-slate-200 mx-1 hidden sm:block" />
            <NotificacionesBell />
          </div>
        </div>
      </div>
    </header>

    <div class="flex">
      <!-- Backdrop (mobile) -->
      <div v-if="sidebarOpen" @click="sidebarOpen = false"
        class="fixed inset-0 z-30 bg-black/40 lg:hidden" />

      <!-- Sidebar -->
      <aside
        class="sidebar-aside fixed top-16 left-0 bottom-0 z-40 w-64 flex flex-col transform transition-transform duration-300 ease-in-out lg:sticky lg:top-16 lg:min-h-[calc(100vh-64px)] lg:shrink-0 lg:translate-x-0"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'">

        <nav class="flex-1 p-3 overflow-y-auto flex flex-col">

          <!-- Módulos principales (empujan hacia arriba) -->
          <div class="flex-1 space-y-0">

            <!-- Dashboard + Mis datos -->
            <ul class="space-y-1 mb-1">
              <li>
                <router-link to="/"
                  class="nav-item"
                  :class="$route.path === '/' ? 'active' : 'inactive'">
                  <HomeIcon class="nav-icon" />
                  <span>Dashboard</span>
                </router-link>
              </li>
              <li>
                <router-link to="/mis-datos"
                  class="nav-item"
                  :class="$route.path === '/mis-datos' ? 'active' : 'inactive'">
                  <UserCircleIcon class="nav-icon" />
                  <span>Mis datos</span>
                </router-link>
              </li>
              <li v-if="orgConfigStore.chatActivo">
                <router-link to="/chat"
                  class="nav-item"
                  :class="$route.path === '/chat' ? 'active' : 'inactive'">
                  <ChatBubbleLeftRightIcon class="nav-icon" />
                  <span>Chat interno</span>
                </router-link>
              </li>
            </ul>

            <hr class="nav-sep" />

            <!-- Membresía -->
            <div v-if="tieneAlguno('SOC_LIST','AGR_EDIT','NOM_CREATE','HAB_LIST')" class="mb-1">
              <button @click="toggleSection('membresia')" class="section-btn">
                <span>Membresía</span>
                <ChevronDownIcon class="chevron" :class="openSections.membresia ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.membresia }">
                <ul class="space-y-1 pb-1">
                  <li v-if="tienePermiso('CONTACTO_LIST')">
                    <router-link to="/contactos" class="nav-item"
                      :class="$route.path.startsWith('/contactos') ? 'active' : 'inactive'">
                      <UserGroupIcon class="nav-icon" /><span>Contactos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('SOC_LIST')">
                    <router-link to="/miembros" class="nav-item"
                      :class="$route.path.startsWith('/miembros') ? 'active' : 'inactive'">
                      <UserIcon class="nav-icon" /><span>{{ orgConfigStore.Miembros }}</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('AGR_EDIT')">
                    <router-link to="/agrupaciones" class="nav-item"
                      :class="$route.path.startsWith('/agrupaciones') ? 'active' : 'inactive'">
                      <MapPinIcon class="nav-icon" /><span>Organización Territorial</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('VOL_LIST')">
                    <router-link to="/voluntarios" class="nav-item"
                      :class="$route.path.startsWith('/voluntarios') ? 'active' : 'inactive'">
                      <HeartIcon class="nav-icon" /><span>Voluntariado</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Actividades -->
            <div v-if="tieneAlguno('CAMP_LIST','ACT_LIST','TEAM_LIST')" class="mb-1">
              <button @click="toggleSection('actividades')" class="section-btn">
                <span>Actividades</span>
                <ChevronDownIcon class="chevron" :class="openSections.actividades ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.actividades }">
                <ul class="space-y-1 pb-1">
                  <li v-if="tienePermiso('CAMP_LIST')">
                    <router-link to="/campanias" class="nav-item"
                      :class="$route.path.startsWith('/campanias') ? 'active' : 'inactive'">
                      <FlagIcon class="nav-icon" /><span>Campañas</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('CAMP_LIST')">
                    <router-link to="/memoria-anual" class="nav-item"
                      :class="$route.path === '/memoria-anual' ? 'active' : 'inactive'">
                      <BookOpenIcon class="nav-icon" /><span>Memoria Anual</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('ACT_LIST')">
                    <router-link to="/actividades" class="nav-item"
                      :class="$route.path.startsWith('/actividades') ? 'active' : 'inactive'">
                      <CalendarDaysIcon class="nav-icon" /><span>Actividades</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('TEAM_LIST')">
                    <router-link to="/grupos" class="nav-item"
                      :class="$route.path.startsWith('/grupos') ? 'active' : 'inactive'">
                      <UserGroupIcon class="nav-icon" /><span>Grupos de Trabajo</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Económico (sidebar minimalista: solo Tesorería + Contabilidad) -->
            <div v-if="tieneAlguno('ECO_INFORME_FINANCIERO_VER','ECO_CUOTA_GENERAR','ECO_REMESA_CREAR','ECO_DONACION_REGISTRAR')" class="mb-1">
              <button @click="toggleSection('economico')" class="section-btn">
                <span>Económico</span>
                <ChevronDownIcon class="chevron" :class="openSections.economico ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.economico }">
                <ul class="space-y-1 pb-1">
                  <li v-if="tienePermiso('ECO_INFORME_FINANCIERO_VER')">
                    <router-link to="/economico/tesoreria" class="nav-item"
                      :class="$route.path.startsWith('/economico/tesoreria') ? 'active' : 'inactive'">
                      <BuildingLibraryIcon class="nav-icon" /><span>Tesorería</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('ECO_INFORME_FINANCIERO_VER') && orgConfigStore.usaPresupuesto">
                    <router-link to="/economico/presupuesto" class="nav-item"
                      :class="$route.path.startsWith('/economico/presupuesto') ? 'active' : 'inactive'">
                      <ChartBarIcon class="nav-icon" /><span>Presupuestos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('ECO_INFORME_FINANCIERO_VER')">
                    <router-link to="/economico/contabilidad" class="nav-item"
                      :class="$route.path.startsWith('/economico/contabilidad') ? 'active' : 'inactive'">
                      <CalculatorIcon class="nav-icon" /><span>Contabilidad</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Presidencia -->
            <div class="mb-1">
              <button @click="toggleSection('presidencia')" class="section-btn">
                <span>Presidencia</span>
                <ChevronDownIcon class="chevron" :class="openSections.presidencia ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.presidencia }">
                <ul class="space-y-1 pb-1">
                  <li>
                    <router-link to="/presidencia" class="nav-item"
                      :class="$route.path === '/presidencia' ? 'active' : 'inactive'">
                      <HomeIcon class="nav-icon" /><span>Cuadro de mando</span>
                    </router-link>
                  </li>
                  <li>
                    <router-link to="/presidencia/acuerdos" class="nav-item"
                      :class="$route.path.startsWith('/presidencia/acuerdos') ? 'active' : 'inactive'">
                      <ClipboardDocumentCheckIcon class="nav-icon" /><span>Acuerdos</span>
                    </router-link>
                  </li>
                  <li>
                    <router-link to="/presidencia/mandatos" class="nav-item"
                      :class="$route.path.startsWith('/presidencia/mandatos') ? 'active' : 'inactive'">
                      <UserGroupIcon class="nav-icon" /><span>Mandatos</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Secretaría -->
            <div v-if="tieneAlguno('SEC_REUNION_LISTAR','SEC_ACTA_LISTAR','SEC_LIBRO_SOCIOS_CONSULTAR','SEC_CONVENIO_LISTAR')" class="mb-1">
              <button @click="toggleSection('secretaria')" class="section-btn">
                <span>Secretaría</span>
                <ChevronDownIcon class="chevron" :class="openSections.secretaria ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.secretaria }">
                <ul class="space-y-1 pb-1">
                  <li v-if="tienePermiso('SEC_REUNION_LISTAR')">
                    <router-link to="/secretaria/reuniones" class="nav-item"
                      :class="$route.path.startsWith('/secretaria/reuniones') ? 'active' : 'inactive'">
                      <CalendarDaysIcon class="nav-icon" /><span>Reuniones</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('SEC_ACUERDO_LISTAR')">
                    <router-link to="/secretaria/acuerdos" class="nav-item"
                      :class="$route.path.startsWith('/secretaria/acuerdos') ? 'active' : 'inactive'">
                      <ClipboardDocumentCheckIcon class="nav-icon" /><span>Acuerdos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('SEC_ACTA_LISTAR')">
                    <router-link to="/secretaria/actas" class="nav-item"
                      :class="$route.path.startsWith('/secretaria/actas') ? 'active' : 'inactive'">
                      <DocumentTextIcon class="nav-icon" /><span>Libro de Actas</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('SEC_LIBRO_SOCIOS_CONSULTAR')">
                    <router-link to="/secretaria/libro-socios" class="nav-item"
                      :class="$route.path.startsWith('/secretaria/libro-socios') ? 'active' : 'inactive'">
                      <BookOpenIcon class="nav-icon" /><span>Libro de Socios</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('SEC_CONVENIO_LISTAR')">
                    <router-link to="/secretaria/convenios" class="nav-item"
                      :class="$route.path.startsWith('/secretaria/convenios') ? 'active' : 'inactive'">
                      <DocumentCheckIcon class="nav-icon" /><span>Convenios</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Protección de Datos (RGPD) -->
            <div v-if="tieneAlguno('RGPD_RAT_LEER','RGPD_SOLICITUD_LEER','RGPD_CONSENTIMIENTO_LEER','RGPD_BRECHA_LEER','RGPD_AUDITORIA_LEER')" class="mb-1">
              <button @click="toggleSection('rgpd')" class="section-btn">
                <span>Protección de Datos</span>
                <ChevronDownIcon class="chevron" :class="openSections.rgpd ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.rgpd }">
                <ul class="space-y-1 pb-1">
                  <li>
                    <router-link to="/rgpd" class="nav-item"
                      :class="$route.path === '/rgpd' ? 'active' : 'inactive'">
                      <ShieldCheckIcon class="nav-icon" /><span>Panel RGPD</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_RAT_LEER')">
                    <router-link to="/rgpd/encargados" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/encargados') ? 'active' : 'inactive'">
                      <BuildingOffice2Icon class="nav-icon" /><span>Encargados</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_RAT_LEER')">
                    <router-link to="/rgpd/actividades" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/actividades') ? 'active' : 'inactive'">
                      <ClipboardDocumentListIcon class="nav-icon" /><span>RAT (art. 30)</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_CLAUSULA_GESTIONAR')">
                    <router-link to="/rgpd/clausulas" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/clausulas') ? 'active' : 'inactive'">
                      <DocumentTextIcon class="nav-icon" /><span>Cláusulas</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_CONSENTIMIENTO_LEER')">
                    <router-link to="/rgpd/consentimientos" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/consentimientos') ? 'active' : 'inactive'">
                      <CheckCircleIcon class="nav-icon" /><span>Consentimientos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_SOLICITUD_LEER')">
                    <router-link to="/rgpd/solicitudes" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/solicitudes') ? 'active' : 'inactive'">
                      <UserIcon class="nav-icon" /><span>Solicitudes ARSULIPO</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_BRECHA_LEER')">
                    <router-link to="/rgpd/brechas" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/brechas') ? 'active' : 'inactive'">
                      <ShieldExclamationIcon class="nav-icon" /><span>Brechas de seguridad</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('RGPD_AUDITORIA_LEER')">
                    <router-link to="/rgpd/auditoria" class="nav-item"
                      :class="$route.path.startsWith('/rgpd/auditoria') ? 'active' : 'inactive'">
                      <EyeIcon class="nav-icon" /><span>Auditoría de accesos</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>

            <hr class="nav-sep" />

            <!-- Ayuda -->
            <div class="mb-1">
              <button @click="toggleSection('ayuda')" class="section-btn">
                <span>Ayuda</span>
                <ChevronDownIcon class="chevron" :class="openSections.ayuda ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.ayuda }">
                <ul class="space-y-1 pb-1">
                  <li>
                    <a href="https://laicismo.org" target="_blank" class="nav-item inactive">
                      <GlobeAltIcon class="nav-icon" /><span>Web Europa Laica</span>
                    </a>
                  </li>
                  <li>
                    <RouterLink to="/ayuda" class="nav-item" :class="$route.path === '/ayuda' ? 'active' : 'inactive'">
                      <BookOpenIcon class="nav-icon" /><span>Documentación</span>
                    </RouterLink>
                  </li>
                </ul>
              </div>
            </div>

          </div><!-- /módulos principales -->

          <!-- Papelera -->
          <div class="px-1 pb-1">
            <router-link to="/papelera" class="nav-item"
              :class="$route.path.startsWith('/papelera') ? 'active' : 'inactive'">
              <TrashIcon class="nav-icon" /><span>Papelera</span>
            </router-link>
          </div>

          <!-- Configuración — anclada al fondo -->
          <div class="mt-auto pt-2">
            <hr class="nav-sep" />
            <div v-if="tieneAlguno('CFG_VIEW','CFG_EDIT','CAT_ACT_MANAGE','USR_LIST','ROL_LIST','PERM_ASSIGN','AUD_VIEW')" class="mb-1">
              <button @click="toggleSection('configuracion')" class="section-btn">
                <span>Configuración</span>
                <ChevronDownIcon class="chevron" :class="openSections.configuracion ? '' : '-rotate-90'" />
              </button>
              <div class="accordion-wrap" :class="{ closed: !openSections.configuracion }">
                <ul class="space-y-1 pb-1">
                  <li v-if="tienePermiso('CFG_VIEW')">
                    <router-link to="/configuracion/general" class="nav-item"
                      :class="$route.path.startsWith('/configuracion/general') ? 'active' : 'inactive'">
                      <BuildingOffice2Icon class="nav-icon" /><span>Parámetros Generales</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('CAT_ACT_MANAGE')">
                    <router-link to="/parametrizacion/catalogos" class="nav-item"
                      :class="$route.path.startsWith('/parametrizacion/catalogos') ? 'active' : 'inactive'">
                      <ListBulletIcon class="nav-icon" /><span>Catálogos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('CFG_EDIT')">
                    <router-link to="/parametrizacion/temas" class="nav-item"
                      :class="$route.path.startsWith('/parametrizacion/temas') ? 'active' : 'inactive'">
                      <SwatchIcon class="nav-icon" /><span>Temas de color</span>
                    </router-link>
                  </li>
                  <li v-if="tieneAlguno('USR_LIST','ROL_LIST','PERM_ASSIGN','AUD_VIEW')" class="pt-2 pb-0.5 px-3">
                    <span class="text-[10px] font-semibold text-purple-500 uppercase tracking-wider">Control de Acceso</span>
                  </li>
                  <li v-if="tienePermiso('USR_LIST')">
                    <router-link to="/usuarios" class="nav-item"
                      :class="$route.path.startsWith('/usuarios') ? 'active' : 'inactive'">
                      <UsersIcon class="nav-icon" /><span>Usuarios</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('ROL_LIST')">
                    <router-link to="/roles" class="nav-item"
                      :class="$route.path.startsWith('/roles') ? 'active' : 'inactive'">
                      <KeyIcon class="nav-icon" /><span>Roles y Permisos</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('PERM_ASSIGN')">
                    <router-link to="/transacciones" class="nav-item"
                      :class="$route.path.startsWith('/transacciones') ? 'active' : 'inactive'">
                      <ListBulletIcon class="nav-icon" /><span>Catálogo RBAC</span>
                    </router-link>
                  </li>
                  <li v-if="tienePermiso('AUD_VIEW')">
                    <router-link to="/auditoria" class="nav-item"
                      :class="$route.path.startsWith('/auditoria') ? 'active' : 'inactive'">
                      <ClipboardDocumentListIcon class="nav-icon" /><span>Auditoría</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>
          </div>

        </nav>

        <!-- Backend status indicator -->
        <BackendStatus />

        <!-- User Panel -->
        <div class="border-t border-purple-800">
          <div class="p-4 bg-purple-800">
            <div class="flex items-center">
              <AvatarImg
                :src="authStore.userFotoUrl"
                :nombre="authStore.userNombre"
                :apellido="authStore.userApellido"
                size="md"
                class="flex-shrink-0" />
              <div class="ml-3 flex-1 min-w-0">
                <p class="text-white font-medium text-sm truncate">{{ userName }}</p>
                <p class="text-purple-300 text-xs truncate">{{ userRole }}</p>
              </div>
            </div>
            <div class="mt-2 flex items-center text-purple-300 text-xs">
              <span class="mr-1">🕒</span>
              <span>Sesión: {{ sessionTime }}</span>
            </div>
          </div>
          <div class="p-3">
            <button @click="logout"
              class="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-white bg-purple-700 rounded-md hover:bg-purple-600 transition-colors">
              <span class="mr-2">🚪</span>
              <span>Cerrar sesión</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- Scroll to top button -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-2"
      >
        <button v-if="showScrollTop"
          @click="scrollToTop"
          class="fixed bottom-6 right-6 z-50 w-10 h-10 rounded-full bg-purple-600 text-white shadow-lg flex items-center justify-center hover:bg-purple-700 transition-colors"
          title="Volver arriba">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
          </svg>
        </button>
      </Transition>

      <!-- Main content -->
      <main class="flex-1 min-w-0 overflow-hidden lg:h-[calc(100vh-64px)]" style="background-color: var(--t-page-bg)">
        <div class="h-full flex flex-col w-full px-4 sm:px-6 lg:px-6">
          <div ref="mainRef" class="flex-1 min-h-0 overflow-y-auto pt-5" :class="$slots.footer ? 'pb-2' : 'pb-4'" @scroll="onMainScroll">
            <!-- fluid: ancho completo (vistas con FilterRail). Por defecto, el contenido se
                 limita al ancho del cuerpo de una vista con filtro y se centra en el espacio. -->
            <div :class="fluid ? 'w-full' : 'w-full lg:max-w-[calc(100%-19rem)] lg:mx-auto'">
              <slot />
            </div>
          </div>
          <div v-if="$slots.footer" class="flex-shrink-0 border-t border-slate-200 bg-white py-3 flex items-center gap-3">
            <slot name="footer" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { usePermisos } from '@/composables/usePermisos.js'
import { useSessionGuard, stopSessionGuard } from '@/composables/useSessionGuard.js'
import BackendStatus from '@/components/common/BackendStatus.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import NotificacionesBell from '@/components/common/NotificacionesBell.vue'
import {
  HomeIcon, UserIcon, UsersIcon, MapPinIcon, FlagIcon, UserGroupIcon,
  HeartIcon, KeyIcon, ListBulletIcon, ClipboardDocumentListIcon,
  GlobeAltIcon, BookOpenIcon, CalendarDaysIcon, SwatchIcon,
  BuildingOffice2Icon, BuildingLibraryIcon, CalculatorIcon, CreditCardIcon,
  ArrowsRightLeftIcon, ChartBarIcon, GiftIcon, UserCircleIcon,
  Bars3Icon, XMarkIcon, ChevronDownIcon, ChevronLeftIcon, TrashIcon,
  ClipboardDocumentCheckIcon, DocumentTextIcon, DocumentCheckIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon, ShieldExclamationIcon, CheckCircleIcon, EyeIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  title:    { type: String, default: '' },
  subtitle: { type: String, default: '' },
  icon:     { type: String, default: '' },
  // Ancho completo (para vistas con FilterRail lateral). Por defecto el contenido
  // se limita al ancho del cuerpo de una vista con filtro y se centra.
  fluid:    { type: Boolean, default: false },
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const orgConfigStore = useOrgConfigStore()
const { tienePermiso, tieneAlguno } = usePermisos()

// ── Sidebar mobile (v2) ───────────────────────────────────────────────────────
const sidebarOpen = ref(false)

// ── Volver ────────────────────────────────────────────────────────────────────
const canGoBack = computed(() => !!window.history.state?.back)
function goBack() { router.back() }

// ── Scroll to top ─────────────────────────────────────────────────────────────
const mainRef = ref(null)
const showScrollTop = ref(false)

function onMainScroll() {
  showScrollTop.value = (mainRef.value?.scrollTop || 0) > 300
}

function scrollToTop() {
  mainRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── Secciones colapsables ─────────────────────────────────────────────────────
const openSections = reactive({
  presidencia: false,
  secretaria: false,
  configuracion: true,
  membresia: false,
  actividades: false,
  economico: false,
  rgpd: false,
  ayuda: false,
})

function sectionForPath(path) {
  if (path === '/' || path === '/mis-datos') return null
  if (path.startsWith('/configuracion') || path.startsWith('/parametrizacion') ||
      path.startsWith('/usuarios') || path.startsWith('/roles') ||
      path.startsWith('/transacciones') || path.startsWith('/auditoria'))
    return 'configuracion'
  if (path.startsWith('/contactos') || path.startsWith('/miembros') ||
      path.startsWith('/agrupaciones') ||
      path.startsWith('/voluntarios'))
    return 'membresia'
  if (path.startsWith('/campanias') || path.startsWith('/acciones') ||
      path.startsWith('/grupos'))
    return 'actividades'
  if (path.startsWith('/economico'))
    return 'economico'
  if (path.startsWith('/presidencia'))
    return 'presidencia'
  if (path.startsWith('/secretaria'))
    return 'secretaria'
  if (path.startsWith('/rgpd'))
    return 'rgpd'
  return null
}

function toggleSection(key) {
  const wasOpen = openSections[key]
  for (const k of Object.keys(openSections)) openSections[k] = false
  openSections[key] = !wasOpen
}

// Abrir la sección activa al navegar (y al montar)
watch(() => route.path, (path) => {
  sidebarOpen.value = false
  const s = sectionForPath(path)
  if (s) openSections[s] = true
}, { immediate: true })

// ── Sesión ────────────────────────────────────────────────────────────────────
const userName = computed(() => authStore.userName || 'Usuario')
const userRole = computed(() => authStore.user?.roles?.[0] || 'Usuario')

// El avatar del usuario (foto del miembro vinculado) vive en el store de sesión,
// para que al cambiar la foto desde Mis datos el sidebar se actualice al instante.

// Vigilancia de caducidad de sesión — singleton de módulo (ver useSessionGuard):
// AppLayout se monta por vista y con keep-alive, así que el temporizador NO
// puede vivir aquí o se acumularían intervalos zombis.
const { sessionTime } = useSessionGuard()

onMounted(async () => {
  await orgConfigStore.fetchConfig()
  authStore.cargarPerfilMiembro()
})

const logout = async () => {
  stopSessionGuard()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* Acordeón con animación CSS pura (grid-template-rows) */
.accordion-wrap {
  display: grid;
  grid-template-rows: 1fr;
  transition: grid-template-rows 0.22s ease;
}
.accordion-wrap.closed {
  grid-template-rows: 0fr;
}
.accordion-wrap > ul {
  overflow: hidden;
  min-height: 0;
}

/* Separador entre módulos */
.nav-sep {
  @apply border-0 border-t my-2 mx-1;
  border-color: rgba(255,255,255,0.20);
}

/* Botón de sección */
.section-btn {
  @apply w-full flex items-center justify-between px-3 py-1.5 mb-0.5 rounded-md
         text-xs font-semibold uppercase tracking-wider transition-colors;
  color: rgba(255,255,255,0.65);
}
.section-btn:hover { background-color: rgba(255,255,255,0.12); color: white; }
.chevron {
  @apply w-3.5 h-3.5 flex-shrink-0 transition-transform duration-200;
}

/* Items de navegación */
.nav-item {
  @apply flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors;
}
.nav-item.active   { background-color: rgba(255,255,255,0.18); color: white; }
.nav-item.inactive { color: rgba(255,255,255,0.80); }
.nav-item.inactive:hover { background-color: rgba(255,255,255,0.12); color: white; }
.nav-icon { @apply w-4 h-4 mr-3 flex-shrink-0; color: rgba(255,255,255,0.65); }
.nav-item.active .nav-icon { color: white; }

</style>
