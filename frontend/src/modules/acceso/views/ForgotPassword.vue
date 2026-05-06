<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md">

      <!-- Logo / cabecera -->
      <div class="text-center mb-8">
        <div class="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-600 shadow-lg mb-4">
          <LockClosedIcon class="h-7 w-7 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-gray-900">Restablecer contraseña</h1>
        <p class="text-sm text-gray-500 mt-1">
          Introduce tu email y te enviaremos un enlace de acceso
        </p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">

        <!-- Éxito -->
        <div v-if="enviado" class="text-center space-y-4">
          <div class="inline-flex h-12 w-12 items-center justify-center rounded-full bg-green-100 mx-auto">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <p class="text-sm text-gray-700">
            Si existe una cuenta con ese email, recibirás un enlace para restablecer
            tu contraseña en los próximos minutos.
          </p>
          <p class="text-xs text-gray-400">Revisa también la carpeta de spam.</p>
          <router-link to="/login"
            class="block w-full text-center mt-4 px-4 py-2 text-sm font-medium text-purple-700 border border-purple-200 rounded-lg hover:bg-purple-50 transition-colors">
            Volver al inicio de sesión
          </router-link>
        </div>

        <!-- Formulario -->
        <form v-else @submit.prevent="enviar" class="space-y-5">

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="tu@email.com"
              required
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                     focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none"
            />
          </div>

          <!-- Campo honeypot: invisible para usuarios, visible para bots -->
          <input
            v-model="hp"
            type="text"
            name="website"
            tabindex="-1"
            autocomplete="off"
            aria-hidden="true"
            class="absolute -left-[9999px] opacity-0 pointer-events-none h-0"
          />

          <div v-if="error" class="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
            {{ error }}
          </div>

          <button type="submit" :disabled="enviando"
            class="w-full py-2.5 px-4 text-sm font-semibold text-white bg-purple-600 rounded-lg
                   hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2">
            <span v-if="enviando" class="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
            {{ enviando ? 'Enviando…' : 'Enviar enlace' }}
          </button>

          <div class="text-center">
            <router-link to="/login" class="text-sm text-purple-600 hover:text-purple-800 transition-colors">
              ← Volver al inicio de sesión
            </router-link>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { LockClosedIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import { graphqlClient } from '@/graphql/client.js'

const MUTATION = `
  mutation SolicitarReset($email: String!, $honeypot: String!) {
    solicitarResetPassword(email: $email, honeypot: $honeypot)
  }
`

const email    = ref('')
const hp       = ref('')   // honeypot
const enviando = ref(false)
const enviado  = ref(false)
const error    = ref('')

async function enviar() {
  error.value    = ''
  enviando.value = true
  try {
    await graphqlClient.request(MUTATION, { email: email.value.trim(), honeypot: hp.value })
    enviado.value = true
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al enviar el email'
  } finally {
    enviando.value = false
  }
}
</script>
