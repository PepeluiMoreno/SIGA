<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto flex justify-center">
          <img src="@/assets/logo.png" alt="Europa Laica" class="h-20 w-auto" />
        </div>
        <h2 class="mt-6 text-center text-xl font-extrabold text-purple-700">
          SIGA (beta release)
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Inicia sesión para acceder al sistema
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
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm"
              placeholder="Correo electrónico"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Contraseña</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm"
              placeholder="Contraseña"
            />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.remember"
              type="checkbox"
              class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Recordarme
            </label>
          </div>

          <div class="text-sm">
            <a href="#" class="font-medium text-purple-600 hover:text-purple-500">
              ¿Olvidaste tu contraseña?
            </a>
          </div>
        </div>

        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <span class="text-red-400">⚠️</span>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">{{ error }}</h3>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 transition-colors"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? "Iniciando sesión..." : "Iniciar sesión" }}
          </button>
        </div>
      </form>

      <div class="text-center">
        <p class="text-xs text-gray-500">
          © {{ new Date().getFullYear() }} Europa Laica - Todos los derechos reservados
        </p>
        <a href="https://laicismo.org" target="_blank" class="text-xs text-purple-600 hover:text-purple-500">
          laicismo.org
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth.js"

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: "",
  password: "",
  remember: false
})

const loading = ref(false)
const error = ref("")

const handleLogin = async () => {
  loading.value = true
  error.value = ""

  try {
    await authStore.login(form.value.email.trim(), form.value.password)
  } catch (err) {
    console.error("Login failed", err)
    error.value = "Credenciales incorrectas. Por favor, verifica tu email y contraseña."
    loading.value = false
    return
  }

  try {
    await router.push("/")
  } catch (err) {
    console.error("Post-login navigation failed", err)
    window.location.assign("/")
    return
  } finally {
    loading.value = false
  }
}
</script>
