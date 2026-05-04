<template>
  <AppLayout title="Nuevo usuario" subtitle="Crear credenciales de acceso al sistema">
    <div class="max-w-lg mx-auto">
      <!-- Card -->
      <div class="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-white">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Datos de acceso</h2>
              <p class="text-sm text-gray-500">El usuario podrá iniciar sesión con estas credenciales</p>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Correo electrónico <span class="text-red-500">*</span>
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              autocomplete="off"
              placeholder="usuario@example.com"
              class="w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              :class="errors.email ? 'border-red-400 bg-red-50' : 'border-gray-300'"
              @blur="validateEmail"
            />
            <p v-if="errors.email" class="mt-1 text-xs text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Contraseña <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                placeholder="Mínimo 8 caracteres"
                class="w-full px-4 py-2.5 pr-10 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                :class="errors.password ? 'border-red-400 bg-red-50' : 'border-gray-300'"
                @blur="validatePassword"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                tabindex="-1"
              >
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="mt-1 text-xs text-red-600">{{ errors.password }}</p>
            <!-- Strength indicator -->
            <div v-if="form.password" class="mt-2">
              <div class="flex gap-1 mb-1">
                <div v-for="i in 4" :key="i"
                  class="h-1 flex-1 rounded-full transition-colors duration-300"
                  :class="strengthColor(i)"
                />
              </div>
              <p class="text-xs" :class="strengthTextClass">{{ strengthLabel }}</p>
            </div>
          </div>

          <!-- Confirm password -->
          <div>
            <label for="confirm" class="block text-sm font-medium text-gray-700 mb-1">
              Confirmar contraseña <span class="text-red-500">*</span>
            </label>
            <input
              id="confirm"
              v-model="form.confirm"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              placeholder="Repite la contraseña"
              class="w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              :class="errors.confirm ? 'border-red-400 bg-red-50' : 'border-gray-300'"
              @blur="validateConfirm"
            />
            <p v-if="errors.confirm" class="mt-1 text-xs text-red-600">{{ errors.confirm }}</p>
          </div>

          <!-- Active toggle -->
          <div class="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <p class="text-sm font-medium text-gray-700">Usuario activo</p>
              <p class="text-xs text-gray-500">Podrá iniciar sesión inmediatamente</p>
            </div>
            <button
              type="button"
              @click="form.activo = !form.activo"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
              :class="form.activo ? 'bg-purple-600' : 'bg-gray-300'"
            >
              <span
                class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="form.activo ? 'translate-x-6' : 'translate-x-1'"
              />
            </button>
          </div>

          <!-- Error alert -->
          <div v-if="serverError" class="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p class="text-sm text-red-700">{{ serverError }}</p>
          </div>

          <!-- Success -->
          <div v-if="success" class="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
            <svg class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <div>
              <p class="text-sm font-medium text-green-800">Usuario creado correctamente</p>
              <p class="text-xs text-green-600 mt-0.5">Redirigiendo...</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="$router.back()"
              class="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="loading || success"
              class="flex-1 px-4 py-2.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-60 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
            >
              <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ loading ? 'Creando...' : 'Crear usuario' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { CREAR_USUARIO } from '@/graphql/queries/usuarios.js'

const router = useRouter()

const form = ref({ email: '', password: '', confirm: '', activo: true })
const errors = ref({ email: '', password: '', confirm: '' })
const showPassword = ref(false)
const loading = ref(false)
const serverError = ref('')
const success = ref(false)

// Password strength
const passwordStrength = computed(() => {
  const p = form.value.password
  if (!p) return 0
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/\d/.test(p) && /[^a-zA-Z0-9]/.test(p)) score++
  return score
})

const strengthLabel = computed(() => {
  return ['', 'Débil', 'Regular', 'Buena', 'Fuerte'][passwordStrength.value]
})

const strengthTextClass = computed(() => {
  return ['', 'text-red-500', 'text-yellow-500', 'text-blue-500', 'text-green-600'][passwordStrength.value]
})

function strengthColor(i) {
  const s = passwordStrength.value
  if (i > s) return 'bg-gray-200'
  return ['', 'bg-red-400', 'bg-yellow-400', 'bg-blue-400', 'bg-green-500'][s]
}

function validateEmail() {
  const v = form.value.email.trim()
  if (!v) { errors.value.email = 'El email es obligatorio'; return false }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { errors.value.email = 'Email no válido'; return false }
  errors.value.email = ''
  return true
}

function validatePassword() {
  const v = form.value.password
  if (!v) { errors.value.password = 'La contraseña es obligatoria'; return false }
  if (v.length < 8) { errors.value.password = 'Mínimo 8 caracteres'; return false }
  errors.value.password = ''
  return true
}

function validateConfirm() {
  if (form.value.confirm !== form.value.password) {
    errors.value.confirm = 'Las contraseñas no coinciden'
    return false
  }
  errors.value.confirm = ''
  return true
}

async function handleSubmit() {
  const ok = validateEmail() & validatePassword() & validateConfirm()
  if (!ok) return

  loading.value = true
  serverError.value = ''

  try {
    await graphqlClient.request(CREAR_USUARIO, {
      email: form.value.email.trim(),
      password: form.value.password,
      activo: form.value.activo,
    })
    success.value = true
    setTimeout(() => router.push('/usuarios'), 1500)
  } catch (e) {
    serverError.value = e?.response?.errors?.[0]?.message || 'Error al crear el usuario'
  } finally {
    loading.value = false
  }
}
</script>
