<template>
  <AppLayout title="Nuevo usuario" subtitle="Crea las credenciales de acceso al sistema">

    <!-- ══ Modal: coincidencia con socio existente ════════════════════════════ -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="modalVisible"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
          @click.self="candidato?.tieneAcceso ? cerrarYReinicializar() : rechazarCoincidencia()">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
            <!-- Cabecera modal -->
            <div class="px-6 pt-6 pb-4 flex items-start gap-4">
              <div class="shrink-0 w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                <UserCircleIcon class="w-6 h-6 text-amber-600" />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-base font-semibold text-slate-800">¿Es para este socio?</h3>
                <p class="text-sm text-slate-500 mt-1">
                  Hay registrado un socio con ese nombre
                  <template v-if="candidato?.agrupacion">
                    perteneciente a <strong class="text-slate-700">{{ candidato.agrupacion.nombre }}</strong>
                  </template>.
                  ¿Se trata de la cuenta de usuario para esa persona?
                </p>
              </div>
            </div>

            <!-- Ficha del socio -->
            <div class="mx-6 mb-4 p-3 bg-slate-50 rounded-xl border border-slate-200">
              <p class="text-sm font-semibold text-slate-800">
                {{ candidato?.apellido1 }} {{ candidato?.apellido2 ?? '' }}, {{ candidato?.nombre }}
              </p>
              <div class="flex flex-wrap gap-x-3 mt-0.5">
                <span v-if="candidato?.tipoMiembro" class="text-xs text-slate-500">
                  {{ candidato.tipoMiembro.nombre }}
                </span>
                <span v-if="candidato?.email" class="text-xs text-slate-400">{{ candidato.email }}</span>
              </div>
              <div v-if="candidato?.tieneAcceso"
                class="mt-2 flex items-center gap-1.5 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1.5">
                <ExclamationTriangleIcon class="w-4 h-4 shrink-0" />
                Este socio ya tiene un usuario en el sistema
              </div>
            </div>

            <!-- Botones: si ya tiene cuenta solo permitir reiniciar -->
            <div class="px-6 pb-5 flex justify-end gap-3">
              <template v-if="candidato?.tieneAcceso">
                <button type="button" @click="cerrarYReinicializar"
                  class="px-5 py-2 text-sm font-semibold text-white bg-slate-600 rounded-lg hover:bg-slate-700 transition-colors">
                  Entendido, empezar de nuevo
                </button>
              </template>
              <template v-else>
                <button type="button" @click="rechazarCoincidencia"
                  class="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
                  No, es diferente
                </button>
                <button type="button" @click="aceptarCoincidencia"
                  class="px-5 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
                  Sí, es para esta persona
                </button>
              </template>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ══ Formulario ═════════════════════════════════════════════════════════ -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-3 pb-20">

      <!-- ══ 1. Identificación ═══════════════════════════════════════════════ -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-slate-400"></span>
          <h2 class="text-sm font-semibold text-slate-800">Identificación</h2>
        </div>
        <div class="px-5 py-4">

          <!-- Socio aceptado: ficha compacta -->
          <div v-if="miembroAceptado"
            class="flex items-center justify-between gap-3 p-3 bg-indigo-50 border border-indigo-200 rounded-xl">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-indigo-900">
                {{ miembroAceptado.apellido1 }} {{ miembroAceptado.apellido2 ?? '' }}, {{ miembroAceptado.nombre }}
              </p>
              <p class="text-xs text-indigo-500 mt-0.5">
                {{ miembroAceptado.tipoMiembro?.nombre }}
                <template v-if="miembroAceptado.agrupacion">
                  · {{ miembroAceptado.agrupacion.nombre }}
                </template>
              </p>
            </div>
            <button type="button" @click="limpiarCoincidencia"
              class="shrink-0 text-xs text-indigo-500 hover:text-indigo-700 underline">
              Cambiar
            </button>
          </div>

          <!-- Campos de nombre (cuando no hay socio aceptado) -->
          <div v-else class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <!-- Nombre -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.nombre"
                  type="text"
                  placeholder="Nombre"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300"
                />
              </div>
              <!-- Apellido 1 -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  Primer apellido <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.apellido1"
                  type="text"
                  placeholder="Apellido 1"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300"
                />
              </div>
            </div>
            <!-- Apellido 2 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">
                Segundo apellido
                <span class="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              </label>
              <input
                v-model="form.apellido2"
                type="text"
                placeholder="Apellido 2"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300"
              />
            </div>
            <!-- Indicador de búsqueda -->
            <p v-if="buscando" class="text-xs text-slate-400 italic">Buscando coincidencias…</p>
            <p v-else-if="sinCoincidencias" class="text-xs text-slate-400">
              No hay ningún socio registrado con ese nombre — elige el tipo de vinculación abajo.
            </p>
          </div>

        </div>
      </section>

      <!-- ══ 2. Vinculación (cuando no hay socio aceptado) ══════════════════ -->
      <section v-if="mostrarVinculacion"
        class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-amber-500"></span>
          <h2 class="text-sm font-semibold text-slate-800">Vinculación con la organización</h2>
        </div>
        <div class="px-5 py-4 space-y-4">

          <div>
            <label for="tipo-vinculacion" class="block text-sm font-medium text-slate-700 mb-1.5">
              Tipo de vinculación
            </label>
            <select id="tipo-vinculacion" v-model="form.tipoVinculacionId"
              class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
              <option value="">— Sin especificar —</option>
              <option v-for="t in tiposVinculacion" :key="t.id" :value="t.id">
                {{ t.nombre }}
              </option>
            </select>
          </div>

          <div v-if="tipoSeleccionado?.requiereEntidad">
            <label for="entidad" class="block text-sm font-medium text-slate-700 mb-1.5">
              {{ tipoSeleccionado.nombre.toLowerCase().includes('asociac') ? 'Asociación amiga' : 'Empresa' }}
            </label>
            <input id="entidad" v-model="form.entidadVinculacion" type="text"
              placeholder="Nombre de la entidad"
              class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300" />
          </div>

        </div>
      </section>

      <!-- ══ 3. Credenciales ════════════════════════════════════════════════ -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
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

          <!-- Modo email de activación: oculta campos de contraseña -->
          <div v-if="form.enviarEmailBienvenida"
            class="flex items-start gap-2.5 px-3 py-2.5 bg-indigo-50 border border-indigo-200 rounded-lg text-xs text-indigo-700">
            <svg class="w-4 h-4 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span>Se enviará un enlace al email del usuario para que establezca su propia contraseña. No es necesario definirla aquí.</span>
          </div>

          <!-- Campos de contraseña (solo si NO se envía email) -->
          <template v-else>
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
                <button type="button" tabindex="-1"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <EyeSlashIcon v-if="showPassword" class="w-4 h-4" />
                  <EyeIcon v-else class="w-4 h-4" />
                </button>
              </div>
              <ErrorAlert v-if="errors.password" :message="errors.password" />
              <div v-if="form.password" class="mt-2">
                <div class="flex gap-1 mb-1">
                  <div v-for="i in 4" :key="i"
                    class="h-1 flex-1 rounded-full transition-colors duration-300"
                    :class="strengthBarColor(i)" />
                </div>
                <p class="text-xs" :class="strengthTextClass">{{ strengthLabel }}</p>
              </div>
            </div>

            <div>
              <label for="confirm" class="block text-sm font-medium text-slate-700 mb-1.5">
                Confirmar contraseña <span class="text-red-500">*</span>
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
          </template>

        </div>
      </section>

      <!-- ══ 4. Configuración ════════════════════════════════════════════════ -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
          <h2 class="text-sm font-semibold text-slate-800">Configuración</h2>
        </div>
        <div class="px-5 py-4 space-y-3">
          <!-- Enviar email de activación -->
          <div class="flex items-center justify-between py-2 px-3 bg-slate-50 rounded-lg border border-slate-200">
            <div>
              <p class="text-sm font-medium text-slate-700">Enviar enlace de activación</p>
              <p class="text-xs text-slate-500">El usuario establece su contraseña por email (requiere SMTP)</p>
            </div>
            <button type="button"
              @click="form.enviarEmailBienvenida = !form.enviarEmailBienvenida"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1"
              :class="form.enviarEmailBienvenida ? 'bg-indigo-600' : 'bg-slate-300'">
              <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="form.enviarEmailBienvenida ? 'translate-x-6' : 'translate-x-1'" />
            </button>
          </div>
          <!-- Usuario activo -->
          <div class="flex items-center justify-between py-2 px-3 bg-slate-50 rounded-lg border border-slate-200">
            <div>
              <p class="text-sm font-medium text-slate-700">Usuario activo</p>
              <p class="text-xs text-slate-500">Podrá iniciar sesión inmediatamente</p>
            </div>
            <button type="button"
              @click="form.activo = !form.activo"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1"
              :class="form.activo ? 'bg-indigo-600' : 'bg-slate-300'">
              <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="form.activo ? 'translate-x-6' : 'translate-x-1'" />
            </button>
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

    <!-- ══ Barra de acciones fija ═════════════════════════════════════════════ -->
    <div class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-sm border-t border-slate-200 shadow-[0_-4px_16px_-4px_rgba(0,0,0,0.08)]">
      <div class="max-w-screen-xl mx-auto px-6 py-3 flex items-center justify-between">
        <p v-if="serverError" class="flex items-center gap-1.5 text-xs text-red-600">
          <ExclamationCircleIcon class="w-4 h-4 shrink-0" />
          {{ serverError }}
        </p>
        <div v-else></div>
        <div class="flex items-center gap-3">
          <button type="button" @click="$router.back()"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
            <ChevronLeftIcon class="w-4 h-4" />
            Cancelar
          </button>
          <button type="button" :disabled="submitting || success"
            @click="handleSubmit"
            class="inline-flex items-center gap-2 px-6 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-sm transition-colors">
            <span v-if="submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
            <CheckIcon v-else class="w-4 h-4" />
            Crear usuario
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  EyeIcon, EyeSlashIcon, CheckIcon,
  ExclamationCircleIcon, ChevronLeftIcon,
  UserCircleIcon, ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { CREAR_USUARIO, GET_TIPOS_VINCULACION, GET_MIEMBROS_SIMPLE } from '@/graphql/queries/usuarios.js'

const router = useRouter()

// ── Estado del formulario ────────────────────────────────────────────────────
const loading = ref(true)
const form = ref({
  nombre: '', apellido1: '', apellido2: '',
  email: '', password: '', confirm: '', activo: true,
  tipoVinculacionId: '', entidadVinculacion: '',
  enviarEmailBienvenida: true,
})
const errors       = ref({ email: '', password: '', confirm: '' })
const showPassword = ref(false)
const submitting   = ref(false)
const serverError  = ref('')
const success      = ref(false)

// ── Catálogos ────────────────────────────────────────────────────────────────
const tiposVinculacion = ref([])
const todosMiembros    = ref([])

const tipoSeleccionado = computed(() =>
  tiposVinculacion.value.find(t => t.id === form.value.tipoVinculacionId) ?? null
)

// ── Match con socio existente ────────────────────────────────────────────────
const candidato       = ref(null)   // candidato actual en el modal
const modalVisible    = ref(false)
const miembroAceptado = ref(null)   // socio confirmado
const yaRechazado     = ref(false)  // el usuario rechazó la coincidencia
const buscando        = ref(false)
const sinCoincidencias = ref(false)

// La sección de vinculación manual se muestra solo si no hay socio aceptado
const mostrarVinculacion = computed(() => miembroAceptado.value === null)

// Temporizador para debounce
let searchTimer = null

watch([() => form.value.nombre, () => form.value.apellido1], () => {
  if (miembroAceptado.value) return  // ya hay socio confirmado
  clearTimeout(searchTimer)
  candidato.value = null
  modalVisible.value = false
  sinCoincidencias.value = false

  const n  = form.value.nombre.trim()
  const a1 = form.value.apellido1.trim()
  if (n.length < 2 || a1.length < 2) { buscando.value = false; return }

  buscando.value = true
  searchTimer = setTimeout(() => {
    buscarCoincidencia(n.toLowerCase(), a1.toLowerCase())
  }, 350)
})

function buscarCoincidencia(n, a1) {
  if (yaRechazado.value) { buscando.value = false; return }
  const matches = todosMiembros.value.filter(m =>
    m.apellido1?.toLowerCase().startsWith(a1) &&
    m.nombre?.toLowerCase().startsWith(n)
  )
  buscando.value = false
  if (matches.length > 0) {
    candidato.value = matches[0]
    modalVisible.value = true
    sinCoincidencias.value = false
  } else {
    sinCoincidencias.value = true
  }
}

function aceptarCoincidencia() {
  miembroAceptado.value = candidato.value
  modalVisible.value = false
  yaRechazado.value = false
  // Auto-set tipo a "Socio"
  const socio = tiposVinculacion.value.find(t => t.nombre.toLowerCase().includes('socio') && !t.nombre.toLowerCase().includes('amiga'))
  if (socio) form.value.tipoVinculacionId = socio.id
}

function rechazarCoincidencia() {
  modalVisible.value = false
  yaRechazado.value = true
  candidato.value = null
  sinCoincidencias.value = true
}

function limpiarCoincidencia() {
  miembroAceptado.value = null
  yaRechazado.value = false
  sinCoincidencias.value = false
  candidato.value = null
  form.value.nombre = ''
  form.value.apellido1 = ''
  form.value.apellido2 = ''
  form.value.tipoVinculacionId = ''
}

function cerrarYReinicializar() {
  modalVisible.value = false
  limpiarCoincidencia()
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
const strengthLabel     = computed(() => ['', 'Débil', 'Regular', 'Buena', 'Fuerte'][passwordStrength.value])
const strengthTextClass = computed(() => ['', 'text-red-500', 'text-yellow-500', 'text-blue-500', 'text-green-600'][passwordStrength.value])
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
    const [vinc, miembros] = await Promise.allSettled([
      graphqlClient.request(GET_TIPOS_VINCULACION),
      graphqlClient.request(GET_MIEMBROS_SIMPLE),
    ])
    if (vinc.status === 'fulfilled')
      tiposVinculacion.value = (vinc.value.tiposVinculacion ?? []).filter(t => t.activo)
    if (miembros.status === 'fulfilled')
      todosMiembros.value = miembros.value.miembros ?? []
  } finally {
    loading.value = false
  }
})

// ── Submit ───────────────────────────────────────────────────────────────────
async function handleSubmit() {
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
      miembroId:              miembroAceptado.value?.id ?? null,
      tipoVinculacionId:      form.value.tipoVinculacionId || null,
      entidadVinculacion:     tipoSeleccionado.value?.requiereEntidad
                                ? (form.value.entidadVinculacion || null)
                                : null,
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

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from,
.modal-fade-leave-to    { opacity: 0; }
</style>
