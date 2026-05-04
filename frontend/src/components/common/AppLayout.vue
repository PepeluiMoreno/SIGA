<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-20">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <img src="@/assets/logo.png" alt="Europa Laica" class="h-10 w-auto" />
            </div>
            
          </div>

          <!-- Header right -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500 hidden md:block">v1.0</span>

            <!-- Notifications -->
            <button class="p-2 text-gray-500 hover:text-gray-700 relative">
              <span class="text-xl">🔔</span>
              <span class="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="flex">
      <!-- Sidebar -->
      <aside class="w-64 bg-purple-900 min-h-[calc(100vh-64px)] flex flex-col sticky top-16">
        <!-- Navigation -->
        <nav class="flex-1 p-4 overflow-y-auto">
          <!-- Dashboard -->
          <div class="mb-5">
            <ul class="space-y-1">
              <li>
                <router-link
                  to="/"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path === '/' ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'"
                >
                  <HomeIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Dashboard</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Membresía -->
          <div class="mb-5">
            <h2 class="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2 px-3">
              Membresía
            </h2>
            <ul class="space-y-1">
              <li>
                <router-link to="/miembros"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/miembros') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <UserIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Miembros</span>
                </router-link>
              </li>
              <li>
                <router-link to="/agrupaciones"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/agrupaciones') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <MapPinIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Agrupaciones</span>
                </router-link>
              </li>
              <li>
                <router-link to="/juntas"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/juntas') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <BuildingOffice2Icon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Juntas Directivas</span>
                </router-link>
              </li>
              <li>
                <router-link to="/voluntarios"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/voluntarios') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <HeartIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Voluntariado</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Actividades -->
          <div class="mb-5">
            <h2 class="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2 px-3">
              Actividades
            </h2>
            <ul class="space-y-1">
              <li>
                <router-link to="/campanias"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/campanias') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <FlagIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Campañas</span>
                </router-link>
              </li>
              <li>
                <router-link to="/eventos"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/eventos') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <CalendarDaysIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Eventos</span>
                </router-link>
              </li>
              <li>
                <router-link to="/grupos"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/grupos') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <UserGroupIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Grupos de Trabajo</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Económico -->
          <div class="mb-5">
            <h2 class="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2 px-3">
              Económico
            </h2>
            <ul class="space-y-1">
              <li>
                <router-link to="/economico/tesoreria"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/tesoreria') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <BuildingLibraryIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Tesorería</span>
                </router-link>
              </li>
              <li>
                <router-link to="/economico/contabilidad"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/contabilidad') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <CalculatorIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Contabilidad</span>
                </router-link>
              </li>
              <li>
                <router-link to="/economico/cuotas"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/cuotas') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <CreditCardIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Cuotas</span>
                </router-link>
              </li>
              <li>
                <router-link to="/economico/remesas"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/remesas') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <ArrowsRightLeftIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Remesas</span>
                </router-link>
              </li>
              <li>
                <router-link to="/economico/presupuesto"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/presupuesto') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <ChartBarIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Presupuesto</span>
                </router-link>
              </li>
              <li>
                <router-link to="/economico/donaciones"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/economico/donaciones') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <GiftIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Donaciones</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Configuración -->
          <div class="mb-6">
            <h2 class="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2 px-3">
              Configuración
            </h2>
            <ul class="space-y-1">
              <li>
                <router-link to="/parametrizacion/sistema"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/parametrizacion/sistema') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <AdjustmentsHorizontalIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Configuración del Sistema</span>
                </router-link>
              </li>
              <li>
                <router-link to="/parametrizacion/catalogos"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/parametrizacion/catalogos') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <ListBulletIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Catálogos</span>
                </router-link>
              </li>
              <li>
                <router-link to="/parametrizacion/colaboraciones"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/parametrizacion/colaboraciones') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <LinkIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Colaboraciones</span>
                </router-link>
              </li>

              <!-- Sub-sección: Control de Acceso -->
              <li class="pt-3 pb-1">
                <span class="text-xs font-medium text-purple-500 uppercase tracking-wider px-3">Control de Acceso</span>
              </li>
              <li>
                <router-link to="/usuarios"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/usuarios') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <UsersIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Usuarios</span>
                </router-link>
              </li>
              <li>
                <router-link to="/roles"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/roles') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <KeyIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Roles y Permisos</span>
                </router-link>
              </li>
              <li>
                <router-link to="/transacciones"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/transacciones') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <ListBulletIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Catálogo RBAC</span>
                </router-link>
              </li>
              <li>
                <router-link to="/auditoria"
                  class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/auditoria') ? 'bg-purple-800 text-white' : 'text-purple-200 hover:bg-purple-800 hover:text-white'">
                  <ClipboardDocumentListIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Auditoría</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Ayuda -->
          <div>
            <h2 class="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-3 px-3">
              Ayuda
            </h2>
            <ul class="space-y-1">
              <li>
                <a href="https://laicismo.org" target="_blank" class="flex items-center px-3 py-2 text-sm font-medium text-purple-200 rounded-md hover:bg-purple-800 hover:text-white transition-colors">
                  <GlobeAltIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Web Europa Laica</span>
                </a>
              </li>
              <li>
                <a href="#" class="flex items-center px-3 py-2 text-sm font-medium text-purple-200 rounded-md hover:bg-purple-800 hover:text-white transition-colors">
                  <BookOpenIcon class="w-5 h-5 mr-3 text-white flex-shrink-0" />
                  <span>Documentación</span>
                </a>
              </li>
            </ul>
          </div>
        </nav>

        <!-- Backend status indicator -->
        <BackendStatus />

        <!-- User Panel (abajo) -->
        <div class="border-t border-purple-800">
          <div class="p-4 bg-purple-800">
            <div class="flex items-center">
              <div class="h-10 w-10 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-medium">
                {{ userInitials }}
              </div>
              <div class="ml-3 flex-1">
                <p class="text-white font-medium text-sm">{{ userName }}</p>
                <p class="text-purple-300 text-xs">{{ userRole }}</p>
              </div>
            </div>
            <div class="mt-2 flex items-center text-purple-300 text-xs">
              <span class="mr-1">🕒</span>
              <span>Sesión: {{ sessionTime }}</span>
            </div>
          </div>
          <div class="p-3">
            <button
              @click="logout"
              class="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-white bg-purple-700 rounded-md hover:bg-purple-600 transition-colors"
            >
              <span class="mr-2">🚪</span>
              <span>Cerrar sesión</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <main class="flex-1 p-6">
        <div class="max-w-7xl mx-auto">
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
            <p v-if="subtitle" class="text-gray-600 mt-1">{{ subtitle }}</p>
          </div>
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import BackendStatus from '@/components/common/BackendStatus.vue'
import {
  HomeIcon,
  UserIcon,
  UsersIcon,
  MapPinIcon,
  FlagIcon,
  UserGroupIcon,
  HeartIcon,
  KeyIcon,
  ListBulletIcon,
  ClipboardDocumentListIcon,
  AdjustmentsHorizontalIcon,
  GlobeAltIcon,
  BookOpenIcon,
  CalendarDaysIcon,
  BuildingOffice2Icon,
  BuildingLibraryIcon,
  CalculatorIcon,
  CreditCardIcon,
  ArrowsRightLeftIcon,
  ChartBarIcon,
  GiftIcon,
  LinkIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.userName || 'Usuario')
const userInitials = computed(() => authStore.userInitials || 'US')
const userRole = computed(() => authStore.user?.roles?.[0] || 'Usuario')

// Session time tracking
const sessionStartTime = ref(Date.now())
const sessionTime = ref('0m')
let sessionTimer = null

const updateSessionTime = () => {
  const elapsed = Date.now() - sessionStartTime.value
  const minutes = Math.floor(elapsed / 60000)
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60

  if (hours > 0) {
    sessionTime.value = `${hours}h ${mins}m`
  } else {
    sessionTime.value = `${mins}m`
  }
}

onMounted(() => {
  // Check if there's a stored session start time
  const storedTime = localStorage.getItem('session_start_time')
  if (storedTime) {
    sessionStartTime.value = parseInt(storedTime)
  } else {
    localStorage.setItem('session_start_time', sessionStartTime.value.toString())
  }

  updateSessionTime()
  sessionTimer = setInterval(updateSessionTime, 60000) // Update every minute
})

onUnmounted(() => {
  if (sessionTimer) {
    clearInterval(sessionTimer)
  }
})

const logout = async () => {
  localStorage.removeItem('session_start_time')
  await authStore.logout()
  router.push('/login')
}
</script>
