<template>
  <AppLayout title="Nuevo usuario" subtitle="Dota de cuenta de acceso a un contacto de la organización">
    <template #actions>
      <span v-if="serverError" class="flex items-center gap-1.5 text-xs text-red-600 mr-1">
        <ExclamationCircleIcon class="w-4 h-4 shrink-0" /> {{ serverError }}
      </span>
      <button type="button" @click="$router.back()"
        class="h-8 px-3 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
        Cancelar
      </button>
      <button type="button" :disabled="submitting || success || !contactoElegido" @click="handleSubmit"
        class="inline-flex items-center gap-2 h-8 px-4 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-sm transition-colors">
        <span v-if="submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
        Crear usuario
      </button>
    </template>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="w-3/4 mx-auto space-y-3">

      <!-- ══ 1. Destinatario de la cuenta ════════════════════════════════════ -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-slate-400"></span>
          <h2 class="text-sm font-semibold text-slate-800">¿A qué contacto se le da acceso?</h2>
        </div>

        <div class="px-5 py-4">
          <!-- Contacto elegido: chip compacto -->
          <div v-if="contactoElegido"
            class="flex items-center justify-between gap-3 p-3 bg-indigo-50 border border-indigo-200 rounded-xl">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-indigo-900 truncate">{{ nombreContacto(contactoElegido) }}</p>
              <p class="text-xs text-indigo-500 mt-0.5 truncate">
                {{ contactoElegido.tipoVinculacionNombre }}
                <template v-if="contactoElegido.agrupacion"> · {{ contactoElegido.agrupacion.nombre }}</template>
                <template v-if="contactoElegido.email"> · {{ contactoElegido.email }}</template>
              </p>
            </div>
            <button type="button" @click="quitarContacto"
              class="shrink-0 text-xs text-indigo-500 hover:text-indigo-700 underline">Cambiar</button>
          </div>

          <!-- Buscador: filtro por tipo de vínculo + texto -->
          <div v-else class="space-y-3">
            <div class="flex gap-2">
              <select v-model="filtroTipoId"
                class="h-10 shrink-0 w-44 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                <option value="">Todos los vínculos</option>
                <option v-for="t in tiposDotables" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
              <div class="relative flex-1">
                <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input v-model="texto" type="text" placeholder="Buscar por nombre o apellidos…"
                  class="h-10 w-full pl-9 pr-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300" />
              </div>
            </div>

            <!-- Resultados -->
            <div class="rounded-lg border border-slate-200 divide-y divide-slate-100 max-h-72 overflow-y-auto">
              <p v-if="buscando" class="px-3 py-4 text-xs text-slate-400 italic text-center">Buscando…</p>
              <p v-else-if="resultados.length === 0"
                class="px-3 py-6 text-xs text-slate-400 text-center">
                {{ texto || filtroTipoId ? 'Ningún contacto coincide con el filtro.' : 'No hay contactos a los que dotar de cuenta.' }}
              </p>
              <button v-for="c in resultados" :key="c.id" type="button"
                :disabled="c.tieneAcceso"
                @click="elegirContacto(c)"
                class="w-full flex items-center justify-between gap-3 px-3 py-2 text-left transition-colors"
                :class="c.tieneAcceso ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-50'">
                <div class="min-w-0">
                  <p class="text-sm font-medium text-slate-800 truncate">{{ nombreContacto(c) }}</p>
                  <p class="text-xs text-slate-400 truncate">
                    {{ c.tipoVinculacionNombre }}
                    <template v-if="c.agrupacion"> · {{ c.agrupacion.nombre }}</template>
                  </p>
                </div>
                <span v-if="c.tieneAcceso"
                  class="shrink-0 inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">
                  <CheckCircleIcon class="w-3 h-3" /> Ya tiene cuenta
                </span>
                <ChevronRightIcon v-else class="shrink-0 w-4 h-4 text-slate-300" />
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ══ 2. Credenciales ════════════════════════════════════════════════ -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
          <h2 class="text-sm font-semibold text-slate-800">Credenciales de acceso</h2>
        </div>
        <div class="px-5 py-4 space-y-4">

          <div>
            <label for="email" class="block text-sm font-medium text-slate-700 mb-1.5">
              Correo electrónico <span class="text-red-500">*</span>
            </label>
            <input id="email" v-model="form.email" type="email" autocomplete="off"
              placeholder="usuario@example.com"
              class="h-10 w-full px-3 text-sm border rounded-lg transition-all focus:outline-none focus:ring-2 bg-white placeholder:text-slate-300"
              :class="errors.email
                ? 'border-red-400 bg-red-50 focus:ring-red-400/30 focus:border-red-400'
                : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'"
              @blur="validateEmail" />
            <ErrorAlert v-if="errors.email" :message="errors.email" />
          </div>

          <!-- Modo email de activación -->
          <div v-if="form.enviarEmailBienvenida"
            class="flex items-start gap-2.5 px-3 py-2.5 bg-indigo-50 border border-indigo-200 rounded-lg text-xs text-indigo-700">
            <EnvelopeIcon class="w-4 h-4 mt-0.5 shrink-0" />
            <span>Se enviará un enlace al email para que el usuario establezca su contraseña.</span>
          </div>

          <template v-else>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label for="password" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Contraseña <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input id="password" v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="new-password" placeholder="Mínimo 8 caracteres"
                    class="h-10 w-full px-3 pr-10 text-sm border rounded-lg transition-all focus:outline-none focus:ring-2 bg-white placeholder:text-slate-300"
                    :class="errors.password
                      ? 'border-red-400 bg-red-50 focus:ring-red-400/30 focus:border-red-400'
                      : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'"
                    @blur="validatePassword" />
                  <button type="button" tabindex="-1" @click="showPassword = !showPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    <EyeSlashIcon v-if="showPassword" class="w-4 h-4" />
                    <EyeIcon v-else class="w-4 h-4" />
                  </button>
                </div>
                <ErrorAlert v-if="errors.password" :message="errors.password" />
              </div>
              <div>
                <label for="confirm" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Confirmar <span class="text-red-500">*</span>
                </label>
                <input id="confirm" v-model="form.confirm"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password" placeholder="Repite la contraseña"
                  class="h-10 w-full px-3 text-sm border rounded-lg transition-all focus:outline-none focus:ring-2 bg-white placeholder:text-slate-300"
                  :class="errors.confirm
                    ? 'border-red-400 bg-red-50 focus:ring-red-400/30 focus:border-red-400'
                    : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'"
                  @blur="validateConfirm" />
                <ErrorAlert v-if="errors.confirm" :message="errors.confirm" />
              </div>
            </div>
            <div v-if="form.password" class="flex gap-1">
              <div v-for="i in 4" :key="i"
                class="h-1 flex-1 rounded-full transition-colors duration-300"
                :class="strengthBarColor(i)" />
            </div>
          </template>

          <!-- Configuración inline compacta -->
          <div class="flex flex-wrap items-center gap-x-6 gap-y-2 pt-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <button type="button" @click="form.enviarEmailBienvenida = !form.enviarEmailBienvenida"
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="form.enviarEmailBienvenida ? 'bg-indigo-600' : 'bg-slate-300'">
                <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
                  :class="form.enviarEmailBienvenida ? 'translate-x-5' : 'translate-x-1'" />
              </button>
              <span class="text-sm text-slate-700">Enviar enlace de activación por email</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <button type="button" @click="form.activo = !form.activo"
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="form.activo ? 'bg-indigo-600' : 'bg-slate-300'">
                <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
                  :class="form.activo ? 'translate-x-5' : 'translate-x-1'" />
              </button>
              <span class="text-sm text-slate-700">Usuario activo</span>
            </label>
          </div>
        </div>
      </section>

      <!-- Éxito -->
      <div v-if="success"
        class="flex items-center gap-2.5 px-4 py-3 bg-green-50 border border-green-200 rounded-xl text-sm text-green-700">
        <CheckIcon class="w-4 h-4 shrink-0 text-green-500" />
        <span>Usuario creado correctamente. Redirigiendo…</span>
      </div>

    </form>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  EyeIcon, EyeSlashIcon, CheckIcon, CheckCircleIcon,
  ExclamationCircleIcon, ChevronLeftIcon, ChevronRightIcon,
  EnvelopeIcon, MagnifyingGlassIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { CREAR_USUARIO, GET_TIPOS_VINCULACION, GET_CONTACTOS_DOTABLES } from '@/graphql/queries/usuarios.js'

const router = useRouter()

// ── Estado del formulario ────────────────────────────────────────────────────
const loading = ref(true)
const form = ref({
  email: '', password: '', confirm: '', activo: true,
  enviarEmailBienvenida: true,
})
const errors       = ref({ email: '', password: '', confirm: '' })
const showPassword = ref(false)
const submitting   = ref(false)
const serverError  = ref('')
const success      = ref(false)

// ── Selección de contacto ────────────────────────────────────────────────────
const tiposDotables   = ref([])
const filtroTipoId    = ref('')
const texto           = ref('')
const resultados      = ref([])
const buscando        = ref(false)
const contactoElegido = ref(null)

function nombreContacto(c) {
  if (c.tipo === 'PERSONA_JURIDICA') return c.razonSocial || c.nombre || '—'
  return [c.apellido1, c.apellido2].filter(Boolean).join(' ') + (c.nombre ? `, ${c.nombre}` : '')
}

let searchTimer = null
watch([filtroTipoId, texto], () => {
  clearTimeout(searchTimer)
  buscando.value = true
  searchTimer = setTimeout(buscarContactos, 300)
})

async function buscarContactos() {
  try {
    const data = await graphqlClient.request(GET_CONTACTOS_DOTABLES, {
      tipoVinculacionId: filtroTipoId.value || null,
      texto: texto.value.trim() || null,
    })
    resultados.value = data.contactosDotables ?? []
  } catch {
    resultados.value = []
  } finally {
    buscando.value = false
  }
}

function elegirContacto(c) {
  if (c.tieneAcceso) return
  contactoElegido.value = c
  // Prerrellena el email si el contacto tiene uno y aún no se ha escrito.
  if (c.email && !form.value.email) form.value.email = c.email
}

function quitarContacto() {
  contactoElegido.value = null
}

// ── Fortaleza de contraseña ──────────────────────────────────────────────────
const passwordStrength = computed(() => {
  const p = form.value.password
  if (!p) return 0
  let score = 0
  if (p.length >= 8)  score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/\d/.test(p) && /[^a-zA-Z0-9]/.test(p)) score++
  return score
})
function strengthBarColor(i) {
  const s = passwordStrength.value
  if (i > s) return 'bg-slate-200'
  return ['', 'bg-red-400', 'bg-yellow-400', 'bg-blue-400', 'bg-green-500'][s]
}

// ── Validación ───────────────────────────────────────────────────────────────
function validateEmail() {
  const v = form.value.email.trim()
  if (!v) { errors.value.email = 'El email es obligatorio'; return false }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { errors.value.email = 'Email no válido'; return false }
  errors.value.email = ''; return true
}
function validatePassword() {
  const v = form.value.password
  if (!v) { errors.value.password = 'La contraseña es obligatoria'; return false }
  if (v.length < 8) { errors.value.password = 'Mínimo 8 caracteres'; return false }
  errors.value.password = ''; return true
}
function validateConfirm() {
  if (form.value.confirm !== form.value.password) {
    errors.value.confirm = 'Las contraseñas no coinciden'; return false
  }
  errors.value.confirm = ''; return true
}

// ── Carga inicial ────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [tipos] = await Promise.allSettled([
      graphqlClient.request(GET_TIPOS_VINCULACION),
    ])
    if (tipos.status === 'fulfilled')
      tiposDotables.value = (tipos.value.tiposVinculacion ?? [])
        .filter(t => t.activo && t.permiteCuenta)
    await buscarContactos()
  } finally {
    loading.value = false
  }
})

// ── Submit ───────────────────────────────────────────────────────────────────
async function handleSubmit() {
  if (!contactoElegido.value) { serverError.value = 'Elige primero el contacto al que dar acceso'; return }
  const emailOk = validateEmail()
  const pwdOk = form.value.enviarEmailBienvenida || (validatePassword() & validateConfirm())
  if (!emailOk || !pwdOk) return

  submitting.value = true
  serverError.value = ''
  try {
    await graphqlClient.request(CREAR_USUARIO, {
      email:                  form.value.email.trim(),
      password:               form.value.enviarEmailBienvenida ? null : form.value.password,
      activo:                 form.value.activo,
      miembroId:              contactoElegido.value.id,
      enviarEmailBienvenida:  form.value.enviarEmailBienvenida,
    })
    success.value = true
    setTimeout(() => router.push('/usuarios'), 1500)
  } catch (e) {
    serverError.value = e?.response?.errors?.[0]?.message || 'Error al crear el usuario'
  } finally {
    submitting.value = false
  }
}
</script>
