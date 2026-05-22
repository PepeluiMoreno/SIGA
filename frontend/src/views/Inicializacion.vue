<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 py-10 px-4">
    <div class="w-full max-w-lg space-y-6">

      <!-- Header -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-purple-100 mb-3">
          <span class="text-2xl">🏛</span>
        </div>
        <h1 class="text-xl font-bold text-purple-800">Configuración inicial</h1>
        <p class="mt-1 text-sm text-gray-500">
          Completa los datos de tu organización para activar el sistema
        </p>
      </div>

      <!-- Form card -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

        <!-- Logotipo -->
        <div class="px-6 py-4 border-b border-gray-100">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Logotipo</p>
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center overflow-hidden flex-shrink-0">
              <img v-if="form.logo" :src="form.logo" alt="Logo" class="w-full h-full object-contain p-1" />
              <span v-else class="text-xl text-gray-300">🏛</span>
            </div>
            <div>
              <label class="cursor-pointer inline-flex items-center px-3 py-1.5 text-xs font-medium bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-gray-700">
                {{ form.logo ? 'Cambiar imagen' : 'Seleccionar imagen (opcional)' }}
                <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp"
                  class="hidden" @change="handleLogoChange" />
              </label>
              <p class="text-xs text-gray-400 mt-1">PNG, JPG, SVG, WEBP · máx. 300 KB</p>
              <ErrorAlert v-if="logoError" :message="logoError" />
            </div>
          </div>
        </div>

        <!-- Campos -->
        <div class="px-6 py-4 grid grid-cols-1 gap-3">
          <div>
            <label class="label">Nombre de la organización <span class="text-red-500">*</span></label>
            <input v-model="form.nombre" type="text" class="input" placeholder="Nombre completo" required />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">NIF <span class="text-red-500">*</span></label>
              <input v-model="form.nif" type="text" class="input" placeholder="G00000000" required />
            </div>
            <div>
              <label class="label">Teléfono <span class="text-red-500">*</span></label>
              <input v-model="form.telefono" type="tel" class="input" placeholder="+34 900 000 000" required />
            </div>
          </div>
          <div>
            <label class="label">Email de contacto <span class="text-red-500">*</span></label>
            <input v-model="form.email" type="email" class="input" placeholder="info@organización.org" required />
          </div>
        </div>

        <!-- Error general -->
        <div v-if="error" class="mx-6 mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 border border-red-200">
          {{ error }}
        </div>

        <!-- Botón -->
        <div class="px-6 pb-5">
          <button @click="guardar" :disabled="guardando"
            class="w-full py-2.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
            {{ guardando ? 'Guardando...' : 'Activar sistema' }}
          </button>
        </div>
      </div>

      <p class="text-center text-xs text-gray-400">
        SIGA · Podrás completar el resto de parámetros desde Configuración una vez iniciada sesión
      </p>
    </div>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'

const router = useRouter()
const orgConfigStore = useOrgConfigStore()

const guardando = ref(false)
const error = ref('')
const logoError = ref('')
const fileInput = ref(null)

const form = reactive({
  nombre: '',
  nif: '',
  telefono: '',
  email: '',
  logo: '',
})

const MUTATION = `
  mutation Inicializar($datos: ParametrosOrganizacionInput!) {
    guardarParametrosOrganizacion(datos: $datos) { nombre logo }
  }
`

onMounted(async () => {
  const initialized = await orgConfigStore.checkInitialized()
  if (initialized) router.replace('/login')
})

function handleLogoChange(event) {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 300 * 1024) {
    logoError.value = 'La imagen supera el límite de 300 KB'
    if (fileInput.value) fileInput.value.value = ''
    return
  }
  logoError.value = ''
  const reader = new FileReader()
  reader.onload = (e) => { form.logo = e.target.result }
  reader.readAsDataURL(file)
}

async function guardar() {
  error.value = ''

  if (!form.nombre.trim()) { error.value = 'El nombre de la organización es obligatorio'; return }
  if (!form.nif.trim())    { error.value = 'El NIF es obligatorio'; return }
  if (!form.telefono.trim()) { error.value = 'El teléfono es obligatorio'; return }
  if (!form.email.trim())  { error.value = 'El email es obligatorio'; return }

  guardando.value = true
  try {
    await graphqlClient.request(MUTATION, {
      datos: {
        nombre:   form.nombre.trim(),
        nif:      form.nif.trim(),
        telefono: form.telefono.trim(),
        email:    form.email.trim(),
        logo:     form.logo,
      }
    })
    orgConfigStore.markInitialized(form.nombre.trim(), form.logo)
    router.push('/login')
  } catch (e) {
    const msg = e?.response?.errors?.[0]?.message ?? ''
    if (msg.toLowerCase().includes('autenticaci')) {
      // El sistema ya está configurado — redirigir al login
      router.replace({ path: '/login', query: { hint: 'ya-inicializado' } })
      return
    }
    error.value = msg || 'Error al guardar. Comprueba la conexión con el servidor.'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.label { @apply block text-xs font-medium text-gray-600 mb-0.5; }
.input {
  @apply w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900
         placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500
         focus:outline-none transition-colors;
}
</style>
