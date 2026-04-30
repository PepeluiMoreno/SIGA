# frontend-generator.ps1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

# Crear estructura de directorios
$directories = @(
    "public",
    "src/assets",
    "src/components/common",
    "src/components/miembros",
    "src/components/campanias",
    "src/components/grupos",
    "src/components/financiero",
    "src/components/dashboard",
    "src/composables",
    "src/layouts",
    "src/router",
    "src/stores",
    "src/views/miembros",
    "src/views/campanias",
    "src/views/grupos",
    "src/views/financiero",
    "src/graphql/queries",
    "src/graphql/mutations",
    "src/utils"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $Path $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Creado directorio: $fullPath"
    }
}

# 1. Archivos de configuracion

# package.json
$packageJson = '{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "graphql": "^16.8.0",
    "graphql-request": "^6.1.0",
    "date-fns": "^3.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0",
    "tailwindcss": "^3.0.0",
    "vite": "^5.0.0"
  }
}'
Set-Content -Path (Join-Path $Path "package.json") -Value $packageJson -Encoding UTF8

# vite.config.js
$viteConfig = "import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/graphql': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})"
Set-Content -Path (Join-Path $Path "vite.config.js") -Value $viteConfig -Encoding UTF8

# tailwind.config.js
$tailwindConfig = "/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}"
Set-Content -Path (Join-Path $Path "tailwind.config.js") -Value $tailwindConfig -Encoding UTF8

# postcss.config.js
$postcssConfig = "export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"
Set-Content -Path (Join-Path $Path "postcss.config.js") -Value $postcssConfig -Encoding UTF8

# .env
$envContent = 'VITE_APP_NAME="Sistema de Adminitración Integrarl de Europa Laica"
VITE_GRAPHQL_URL=http://localhost:8000/graphql'
Set-Content -Path (Join-Path $Path ".env") -Value $envContent -Encoding UTF8

# 2. Archivos publicos

# index.html
$indexHtml = '<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sistema de Adminitración Integrarl de Europa Laica</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>'
Set-Content -Path (Join-Path $Path "public/index.html") -Value $indexHtml -Encoding UTF8

# 3. Archivos fuente principales

# main.js
$mainJs = "import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

// Rutas
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue')
  },
  {
    path: '/miembros',
    name: 'Miembros',
    component: () => import('./views/miembros/ListaMiembros.vue'),
  },
  {
    path: '/campanias',
    name: 'Campanias',
    component: () => import('./views/campanias/ListaCampanias.vue'),
  },
  {
    path: '/grupos',
    name: 'Grupos',
    component: () => import('./views/grupos/ListaGrupos.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')"
Set-Content -Path (Join-Path $Path "src/main.js") -Value $mainJs -Encoding UTF8

# style.css
$styleCss = '@tailwind base;
@tailwind components;
@tailwind utilities;'
Set-Content -Path (Join-Path $Path "src/style.css") -Value $styleCss -Encoding UTF8

# App.vue
$appVue = '<template>
  <router-view />
</template>

<script setup>
// App principal
</script>'
Set-Content -Path (Join-Path $Path "src/App.vue") -Value $appVue -Encoding UTF8

# 4. Componentes comunes

# AppLayout.vue
$appLayout = '<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <span class="text-white font-bold">ONG</span>
              </div>
            </div>
            <div class="ml-4">
              <h1 class="text-lg font-semibold text-gray-900">Adminitración Integrarl de Europa Laica</h1>
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <div class="flex">
      <aside class="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-64px)]">
        <nav class="p-4">
          <div class="mb-8">
            <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Navegacion
            </h2>
            <ul class="space-y-1">
              <li>
                <router-link to="/" class="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
                  Dashboard
                </router-link>
              </li>
              <li>
                <router-link to="/miembros" class="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
                  Miembros
                </router-link>
              </li>
              <li>
                <router-link to="/campanias" class="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
                  Campanias
                </router-link>
              </li>
              <li>
                <router-link to="/grupos" class="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
                  Grupos
                </router-link>
              </li>
            </ul>
          </div>
        </nav>
      </aside>
      
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
</script>'
Set-Content -Path (Join-Path $Path "src/components/common/AppLayout.vue") -Value $appLayout -Encoding UTF8

# 5. Stores

# auth.js
$authStore = "import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  const token = ref(localStorage.getItem('token'))
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.nombre || 'Usuario')
  
  function setAuth(data) {
    token.value = data.token
    user.value = data.user
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }
  
  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  async function login(email, password) {
    const mockUser = {
      id: 1,
      nombre: 'Admin',
      apellido1: 'User',
      email: email,
      roles: ['Admin']
    }
    
    setAuth({
      token: 'mock-jwt-token',
      user: mockUser
    })
    
    return mockUser
  }
  
  async function logout() {
    clearAuth()
    router.push('/login')
  }
  
  return {
    token,
    user,
    isAuthenticated,
    userName,
    login,
    logout,
    setAuth,
    clearAuth
  }
})"
Set-Content -Path (Join-Path $Path "src/stores/auth.js") -Value $authStore -Encoding UTF8

# 6. Views principales

# Dashboard.vue
$dashboard = '<template>
  <AppLayout title="Dashboard" subtitle="Resumen general">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <span class="text-lg font-semibold text-blue-600">42</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Miembros</p>
            <p class="text-2xl font-bold text-gray-900">42</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center">
              <span class="text-lg font-semibold text-green-600">8</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Campanias Activas</p>
            <p class="text-2xl font-bold text-gray-900">8</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center">
              <span class="text-lg font-semibold text-purple-600">5</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Grupos Activos</p>
            <p class="text-2xl font-bold text-gray-900">5</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-12 w-12 rounded-lg bg-yellow-100 flex items-center justify-center">
              <span class="text-lg font-semibold text-yellow-600">EUR</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Recaudacion Mes</p>
            <p class="text-2xl font-bold text-gray-900">2,540</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from "@/components/common/AppLayout.vue"
</script>'
Set-Content -Path (Join-Path $Path "src/views/Dashboard.vue") -Value $dashboard -Encoding UTF8

# Login.vue
$login = '<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 rounded-lg bg-blue-600 flex items-center justify-center">
          <span class="text-white font-bold">ONG</span>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sistema de Adminitración Integrarl de Europa Laica
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Inicia sesion para acceder al sistema
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Email"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Contrasena</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Contrasena"
            />
          </div>
        </div>

        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">{{ error }}</h3>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? "Iniciando sesion..." : "Iniciar sesion" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: "",
  password: ""
})

const loading = ref(false)
const error = ref("")

const handleLogin = async () => {
  loading.value = true
  error.value = ""
  
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push("/")
  } catch (err) {
    error.value = "Credenciales incorrectas."
  } finally {
    loading.value = false
  }
}
</script>'
Set-Content -Path (Join-Path $Path "src/views/Login.vue") -Value $login -Encoding UTF8

# ListaMiembros.vue
$listaMiembros = '<template>
  <AppLayout title="Miembros" subtitle="Gestion de miembros y voluntarios">
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex-1">
          <div class="relative">
            <input
              type="text"
              placeholder="Buscar miembros..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div class="absolute left-3 top-2.5">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="flex gap-2">
          <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Filtros
          </button>
          <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Nuevo Miembro
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nombre
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Tipo
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center mr-3">
                  <span class="text-sm font-medium text-gray-700">JP</span>
                </div>
                <div>
                  <div class="text-sm font-medium text-gray-900">Juan Perez</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">juan@email.com</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                miembro
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
              <button class="text-red-600 hover:text-red-900">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from "@/components/common/AppLayout.vue"
</script>'
Set-Content -Path (Join-Path $Path "src/views/miembros/ListaMiembros.vue") -Value $listaMiembros -Encoding UTF8

# Placeholder para otras views
$placeholderView = '<template>
  <AppLayout title="Placeholder" subtitle="En desarrollo">
    <div class="text-center py-12">
      <div class="mx-auto h-12 w-12 text-gray-400">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="mt-2 text-sm font-medium text-gray-900">Pagina en construccion</h3>
      <p class="mt-1 text-sm text-gray-500">Modulo en desarrollo.</p>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from "@/components/common/AppLayout.vue"
</script>'

Set-Content -Path (Join-Path $Path "src/views/campanias/ListaCampanias.vue") -Value $placeholderView -Encoding UTF8
Set-Content -Path (Join-Path $Path "src/views/grupos/ListaGrupos.vue") -Value $placeholderView -Encoding UTF8

# 7. Utils

# api.js
$api = "// Configuracion de API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    return response.json()
  },
  
  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    return response.json()
  },
  
  async put(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    return response.json()
  },
  
  async delete(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
    })
    return response.json()
  },
}"
Set-Content -Path (Join-Path $Path "src/utils/api.js") -Value $api -Encoding UTF8

# formatters.js
$formatters = "// Funciones de formato
export function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES')
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}"
Set-Content -Path (Join-Path $Path "src/utils/formatters.js") -Value $formatters -Encoding UTF8

Write-Host "Estructura frontend generada en: $Path" -ForegroundColor Green