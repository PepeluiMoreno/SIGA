<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-20">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Hamburger + logo -->
          <div class="flex items-center gap-3">
            <button @click="sidebarOpen = !sidebarOpen"
              class="lg:hidden p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors">
              <XMarkIcon v-if="sidebarOpen" class="w-6 h-6" />
              <Bars3Icon v-else class="w-6 h-6" />
            </button>
            <img v-if="orgConfigStore.logo" :src="orgConfigStore.logo" alt="Logo organización"
              class="h-9 w-auto max-w-[160px] object-contain" />
          </div>

          <!-- Header right -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500 hidden md:block">v1.0</span>
            <button class="p-2 text-gray-500 hover:text-gray-700 relative">
              <span class="text-xl">🔔</span>
              <span class="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>
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
        class="fixed top-16 left-0 bottom-0 z-40 w-64 bg-purple-900 flex flex-col transform transition-transform duration-300 ease-in-out lg:sticky lg:top-16 lg:min-h-[calc(100vh-64px)] lg:shrink-0 lg:translate-x-0"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'">

        <nav class="flex-1 p-3 overflow-y-auto">

          <!-- Dashboard -->
          <ul class="space-y-1 mb-2">
            <li>
              <router-link to="/"
                class="nav-item"
                :class="$route.path === '/' ? 'active' : 'inactive'">
                <HomeIcon class="nav-icon" />
                <span>Dashboard</span>
              </router-link>
            </li>
          </ul>

          <!-- Configuración -->
          <div class="mb-1">
            <button @click="toggleSection('configuracion')" class="section-btn">
              <span>Configuración</span>
              <ChevronDownIcon class="chevron" :class="openSections.configuracion ? '' : '-rotate-90'" />
            </button>
            <div class="accordion-wrap" :class="{ closed: !openSections.configuracion }">
              <ul class="space-y-1 pb-1">
                <li>
                  <router-link to="/configuracion/general" class="nav-item"
                    :class="$route.path.startsWith('/configuracion/general') ? 'active' : 'inactive'">
                    <BuildingOffice2Icon class="nav-icon" /><span>Parámetros Generales</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/parametrizacion/catalogos" class="nav-item"
                    :class="$route.path.startsWith('/parametrizacion/catalogos') ? 'active' : 'inactive'">
                    <ListBulletIcon class="nav-icon" /><span>Catálogos</span>
                  </router-link>
                </li>
                <li class="pt-2 pb-0.5 px-3">
                  <span class="text-[10px] font-semibold text-purple-500 uppercase tracking-wider">Control de Acceso</span>
                </li>
                <li>
                  <router-link to="/usuarios" class="nav-item"
                    :class="$route.path.startsWith('/usuarios') ? 'active' : 'inactive'">
                    <UsersIcon class="nav-icon" /><span>Usuarios</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/roles" class="nav-item"
                    :class="$route.path.startsWith('/roles') ? 'active' : 'inactive'">
                    <KeyIcon class="nav-icon" /><span>Roles y Permisos</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/transacciones" class="nav-item"
                    :class="$route.path.startsWith('/transacciones') ? 'active' : 'inactive'">
                    <ListBulletIcon class="nav-icon" /><span>Catálogo RBAC</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/auditoria" class="nav-item"
                    :class="$route.path.startsWith('/auditoria') ? 'active' : 'inactive'">
                    <ClipboardDocumentListIcon class="nav-icon" /><span>Auditoría</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>

          <!-- Membresía -->
          <div class="mb-1">
            <button @click="toggleSection('membresia')" class="section-btn">
              <span>Membresía</span>
              <ChevronDownIcon class="chevron" :class="openSections.membresia ? '' : '-rotate-90'" />
            </button>
            <div class="accordion-wrap" :class="{ closed: !openSections.membresia }">
              <ul class="space-y-1 pb-1">
                <li>
                  <router-link to="/miembros" class="nav-item"
                    :class="$route.path.startsWith('/miembros') ? 'active' : 'inactive'">
                    <UserIcon class="nav-icon" /><span>Miembros</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/agrupaciones" class="nav-item"
                    :class="$route.path.startsWith('/agrupaciones') ? 'active' : 'inactive'">
                    <MapPinIcon class="nav-icon" /><span>Agrupaciones</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/juntas" class="nav-item"
                    :class="$route.path.startsWith('/juntas') ? 'active' : 'inactive'">
                    <BuildingOffice2Icon class="nav-icon" /><span>Juntas Directivas</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/voluntarios" class="nav-item"
                    :class="$route.path.startsWith('/voluntarios') ? 'active' : 'inactive'">
                    <HeartIcon class="nav-icon" /><span>Voluntariado</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>

          <!-- Actividades -->
          <div class="mb-1">
            <button @click="toggleSection('actividades')" class="section-btn">
              <span>Actividades</span>
              <ChevronDownIcon class="chevron" :class="openSections.actividades ? '' : '-rotate-90'" />
            </button>
            <div class="accordion-wrap" :class="{ closed: !openSections.actividades }">
              <ul class="space-y-1 pb-1">
                <li>
                  <router-link to="/campanias" class="nav-item"
                    :class="$route.path.startsWith('/campanias') ? 'active' : 'inactive'">
                    <FlagIcon class="nav-icon" /><span>Campañas</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/eventos" class="nav-item"
                    :class="$route.path.startsWith('/eventos') ? 'active' : 'inactive'">
                    <CalendarDaysIcon class="nav-icon" /><span>Eventos</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/grupos" class="nav-item"
                    :class="$route.path.startsWith('/grupos') ? 'active' : 'inactive'">
                    <UserGroupIcon class="nav-icon" /><span>Grupos de Trabajo</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>

          <!-- Económico -->
          <div class="mb-1">
            <button @click="toggleSection('economico')" class="section-btn">
              <span>Económico</span>
              <ChevronDownIcon class="chevron" :class="openSections.economico ? '' : '-rotate-90'" />
            </button>
            <div class="accordion-wrap" :class="{ closed: !openSections.economico }">
              <ul class="space-y-1 pb-1">
                <li>
                  <router-link to="/economico/tesoreria" class="nav-item"
                    :class="$route.path.startsWith('/economico/tesoreria') ? 'active' : 'inactive'">
                    <BuildingLibraryIcon class="nav-icon" /><span>Tesorería</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/economico/contabilidad" class="nav-item"
                    :class="$route.path.startsWith('/economico/contabilidad') ? 'active' : 'inactive'">
                    <CalculatorIcon class="nav-icon" /><span>Contabilidad</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/economico/cuotas" class="nav-item"
                    :class="$route.path.startsWith('/economico/cuotas') ? 'active' : 'inactive'">
                    <CreditCardIcon class="nav-icon" /><span>Cuotas</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/economico/remesas" class="nav-item"
                    :class="$route.path.startsWith('/economico/remesas') ? 'active' : 'inactive'">
                    <ArrowsRightLeftIcon class="nav-icon" /><span>Remesas</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/economico/presupuesto" class="nav-item"
                    :class="$route.path.startsWith('/economico/presupuesto') ? 'active' : 'inactive'">
                    <ChartBarIcon class="nav-icon" /><span>Presupuesto</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/economico/donaciones" class="nav-item"
                    :class="$route.path.startsWith('/economico/donaciones') ? 'active' : 'inactive'">
                    <GiftIcon class="nav-icon" /><span>Donaciones</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>

          <!-- Ayuda -->
          <div>
            <button @click="toggleSection('ayuda')" class="section-btn">
              <span>Ayuda</span>
              <ChevronDownIcon class="chevron" :class="openSections.ayuda ? '' : '-rotate-90'" />
            </button>
            <div class="accordion-wrap" :class="{ closed: !openSections.ayuda }">
              <ul class="space-y-1 pb-1">
                <li>
                  <a href="https://laicismo.org" target="_blank"
                    class="nav-item inactive">
                    <GlobeAltIcon class="nav-icon" /><span>Web Europa Laica</span>
                  </a>
                </li>
                <li>
                  <a href="#" class="nav-item inactive">
                    <BookOpenIcon class="nav-icon" /><span>Documentación</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>

        </nav>

        <!-- Backend status indicator -->
        <BackendStatus />

        <!-- User Panel -->
        <div class="border-t border-purple-800">
          <div class="p-4 bg-purple-800">
            <div class="flex items-center">
              <div class="h-9 w-9 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                {{ userInitials }}
              </div>
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

      <!-- Main content -->
      <main class="flex-1 px-4 sm:px-6 pt-4 pb-4 min-w-0 overflow-y-auto lg:h-[calc(100vh-64px)]">
        <div class="mb-3">
          <h1 class="text-lg font-bold text-gray-900">{{ title }}</h1>
          <p v-if="subtitle" class="text-xs text-gray-500">{{ subtitle }}</p>
        </div>
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import BackendStatus from '@/components/common/BackendStatus.vue'
import {
  HomeIcon, UserIcon, UsersIcon, MapPinIcon, FlagIcon, UserGroupIcon,
  HeartIcon, KeyIcon, ListBulletIcon, ClipboardDocumentListIcon,
  GlobeAltIcon, BookOpenIcon, CalendarDaysIcon,
  BuildingOffice2Icon, BuildingLibraryIcon, CalculatorIcon, CreditCardIcon,
  ArrowsRightLeftIcon, ChartBarIcon, GiftIcon,
  Bars3Icon, XMarkIcon, ChevronDownIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const orgConfigStore = useOrgConfigStore()

// ── Sidebar mobile (v2) ───────────────────────────────────────────────────────
const sidebarOpen = ref(false)

// ── Secciones colapsables ─────────────────────────────────────────────────────
const openSections = reactive({
  configuracion: false,
  membresia: false,
  actividades: false,
  economico: false,
  ayuda: false,
})

function sectionForPath(path) {
  if (path.startsWith('/configuracion') || path.startsWith('/parametrizacion') ||
      path.startsWith('/usuarios') || path.startsWith('/roles') ||
      path.startsWith('/transacciones') || path.startsWith('/auditoria'))
    return 'configuracion'
  if (path.startsWith('/miembros') || path.startsWith('/agrupaciones') ||
      path.startsWith('/juntas') || path.startsWith('/voluntarios'))
    return 'membresia'
  if (path.startsWith('/campanias') || path.startsWith('/eventos') ||
      path.startsWith('/grupos'))
    return 'actividades'
  if (path.startsWith('/economico'))
    return 'economico'
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
const userInitials = computed(() => authStore.userInitials || 'US')
const userRole = computed(() => authStore.user?.roles?.[0] || 'Usuario')

const sessionStartTime = ref(Date.now())
const sessionTime = ref('0m')
let sessionTimer = null

function updateSessionTime() {
  const elapsed = Date.now() - sessionStartTime.value
  const minutes = Math.floor(elapsed / 60000)
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  sessionTime.value = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
}

onMounted(() => {
  orgConfigStore.fetchConfig()
  const storedTime = localStorage.getItem('session_start_time')
  if (storedTime) {
    sessionStartTime.value = parseInt(storedTime)
  } else {
    localStorage.setItem('session_start_time', sessionStartTime.value.toString())
  }
  updateSessionTime()
  sessionTimer = setInterval(updateSessionTime, 60000)
})

onUnmounted(() => { if (sessionTimer) clearInterval(sessionTimer) })

const logout = async () => {
  localStorage.removeItem('session_start_time')
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

/* Botón de sección */
.section-btn {
  @apply w-full flex items-center justify-between px-3 py-1.5 mb-0.5 rounded-md
         text-xs font-semibold text-purple-400 uppercase tracking-wider
         hover:text-purple-200 hover:bg-purple-800/40 transition-colors;
}
.chevron {
  @apply w-3.5 h-3.5 flex-shrink-0 transition-transform duration-200;
}

/* Items de navegación */
.nav-item {
  @apply flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors;
}
.nav-item.active  { @apply bg-purple-800 text-white; }
.nav-item.inactive { @apply text-purple-200 hover:bg-purple-800 hover:text-white; }
.nav-icon {
  @apply w-4 h-4 mr-3 flex-shrink-0 text-purple-300;
}
.nav-item.active .nav-icon { @apply text-white; }
</style>
