<template>
  <AppLayout title="Parámetros Generales" subtitle="Datos de la organización">
    <div v-if="errorCarga" class="mb-3 rounded-md bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-700 flex items-center gap-2">
      <span>⚠️</span> {{ errorCarga }}
    </div>
    <form @submit.prevent="guardar" class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:h-full">

      <!-- Col izquierda: Identidad + Contacto + Logotipo -->
      <div class="flex flex-col gap-4 min-h-0">

        <!-- Identidad -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Identidad</h2>
          </div>
          <div class="px-4 py-3 space-y-3">
            <!-- Fila 1: Nombre + NIF + Nº registro -->
            <div class="flex items-end gap-2">
              <div class="flex-1 min-w-0">
                <label class="label">Nombre de la organización <span class="text-red-500">*</span></label>
                <input v-model="form.nombre" type="text" class="input w-full" placeholder="Nombre completo" />
              </div>
              <div class="w-28 flex-shrink-0">
                <label class="label">NIF <span class="text-red-500">*</span></label>
                <input v-model="form.nif" type="text" class="input" placeholder="G00000000" maxlength="12" />
              </div>
              <div class="w-32 flex-shrink-0">
                <label class="label">Nº registro</label>
                <input v-model="form.numero_registro" type="text" class="input" placeholder="12345/A" maxlength="40" />
              </div>
            </div>
            <!-- Fila 2: Tipo de entidad · Denominación membresía · Órgano de gobierno -->
            <div class="flex items-end gap-2">
              <div class="w-36 flex-shrink-0">
                <label class="label">Tipo entidad</label>
                <select v-model="form.tipo_entidad" class="input">
                  <option value="ASOCIACION">Asociación</option>
                  <option value="FUNDACION">Fundación</option>
                </select>
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Denominación membresía</label>
                <div class="flex items-center gap-1.5">
                  <input v-model="form.denominacion_miembro" type="text" class="input w-0 flex-1" placeholder="socio" maxlength="30" />
                  <span class="text-gray-400 text-sm flex-shrink-0">/</span>
                  <input v-model="form.denominacion_miembro_plural" type="text" class="input w-0 flex-1" placeholder="socios" maxlength="30" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Órgano de gobierno</label>
                <div class="flex items-center gap-1.5">
                  <input v-model="form.denominacion_organo_gobierno" type="text" class="input w-0 flex-1" placeholder="junta directiva" maxlength="40" />
                  <span class="text-gray-400 text-sm flex-shrink-0">/</span>
                  <input v-model="form.denominacion_organo_gobierno_plural" type="text" class="input w-0 flex-1" placeholder="juntas directivas" maxlength="40" />
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Estructura organizativa -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg flex items-center gap-3">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Estructura organizativa</h2>
            <span v-if="editorRef?.estructuraProtegida" class="text-xs text-amber-600">
              🔒 Protegida — hay datos asociados. Solo se puede renombrar.
            </span>
          </div>
          <div class="px-4 py-3">
            <EstructuraOrganizativaEditor ref="editorRef" />
          </div>
        </section>

        <!-- Identidad visual: Logotipo + Apariencia -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Identidad visual</h2>
          </div>
          <div class="px-4 py-3 flex gap-5">
            <!-- Logotipo -->
            <div class="flex flex-col items-center gap-2 flex-shrink-0">
              <div class="w-28 h-28 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 flex items-center justify-center overflow-hidden">
                <img v-if="form.logo" :src="form.logo" alt="Logo" class="w-full h-full object-contain p-2" />
                <span v-else class="text-4xl text-gray-200">🏛</span>
              </div>
              <div class="flex items-center gap-1.5">
                <label class="cursor-pointer px-2.5 py-1 text-xs font-medium bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-gray-700">
                  {{ form.logo ? 'Cambiar' : 'Seleccionar' }}
                  <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" class="hidden" @change="handleLogoChange" />
                </label>
                <button v-if="form.logo" type="button" @click="eliminarLogo"
                  class="px-2.5 py-1 text-xs font-medium text-red-600 border border-red-200 rounded-md hover:bg-red-50 transition-colors">
                  Eliminar
                </button>
              </div>
              <p class="text-xs text-gray-400 text-center leading-tight">PNG · JPG · SVG<br>máx. 300 KB</p>
              <p v-if="logoError" class="text-xs text-red-500 text-center">{{ logoError }}</p>
            </div>
            <!-- Apariencia -->
            <div class="flex-1 min-w-0 space-y-3">
              <div>
                <label class="label">Tema de color</label>
                <div class="grid grid-cols-3 gap-1.5 mt-1">
                  <button v-for="t in temas" :key="t.slug" type="button"
                    @click="form.tema = t.slug; orgConfigStore.applyTheme(t, form.fuente_principal)"
                    class="rounded-lg border-2 p-1.5 text-center transition-all hover:border-gray-400"
                    :class="form.tema === t.slug ? 'border-gray-700 shadow-sm' : 'border-gray-200'">
                    <div class="flex gap-0.5 mb-0.5 justify-center">
                      <div v-for="c in temaPaleta(t)" :key="c"
                        class="h-3 w-3 rounded-sm" :style="{ backgroundColor: c }" />
                    </div>
                    <span class="text-xs font-medium text-gray-700">{{ t.nombre }}</span>
                  </button>
                </div>
              </div>
              <div>
                <label class="label">Tipografía</label>
                <div class="flex items-center gap-3 mt-1">
                  <select v-model="form.fuente_principal" class="input w-36">
                    <option v-for="f in fuentesDisponibles" :key="f.valor" :value="f.valor">{{ f.nombre }}</option>
                  </select>
                  <span class="text-sm text-gray-500 truncate"
                    :style="{ fontFamily: `'${form.fuente_principal}', sans-serif` }">
                    Aa — texto de ejemplo
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

      </div>

      <!-- Col derecha: Sede social + Funcionalidades + Redes sociales -->
      <div class="flex flex-col gap-4 min-h-0">

        <!-- Sede social -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Sede social</h2>
          </div>
          <div class="px-4 py-3 space-y-2">
            <div>
              <label class="label">Dirección</label>
              <input v-model="form.sede_social" type="text" class="input" placeholder="Calle, número, piso..." />
            </div>
            <div class="flex items-end gap-2">
              <div class="flex-1 min-w-0">
                <label class="label">Localidad</label>
                <input v-model="form.localidad" type="text" class="input" />
              </div>
              <div class="w-20 flex-shrink-0">
                <label class="label">CP</label>
                <input v-model="form.cp" type="text" class="input" placeholder="28001" maxlength="10" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Provincia</label>
                <input v-model="form.provincia" type="text" class="input" />
              </div>
              <div class="w-28 flex-shrink-0">
                <label class="label">País</label>
                <input v-model="form.pais" type="text" class="input" />
              </div>
            </div>
            <div class="flex items-end gap-2">
              <div class="w-36 flex-shrink-0">
                <label class="label">Teléfono <span class="text-red-500">*</span></label>
                <input v-model="form.telefono" type="tel" class="input" placeholder="+34 900 000 000" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Email <span class="text-red-500">*</span></label>
                <input v-model="form.email" type="email" class="input" placeholder="info@organización.org" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Sitio web</label>
                <input v-model="form.web" type="url" class="input" placeholder="https://www.organización.org" />
              </div>
            </div>
          </div>
        </section>

        <!-- Funcionalidades -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Funcionalidades</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 gap-3">
            <label class="flex items-start gap-2 cursor-pointer">
              <input v-model="form.contabilidad_compleja" type="checkbox"
                :disabled="esObligatorioContabilidad"
                class="h-3.5 w-3.5 mt-0.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500 disabled:opacity-60 disabled:cursor-not-allowed" />
              <span class="text-xs text-gray-700">
                Contabilidad según Plan General Contable
                <span class="text-gray-400">(RD 1491/2011 — obligatorio para fundaciones)</span>
              </span>
            </label>
          </div>
        </section>

        <!-- Autenticación -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Autenticación</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 gap-3">
            <div>
              <label class="label">Mecanismo</label>
              <select v-model="form.auth_modo" class="input">
                <option value="LOCAL">Local (usuario/contraseña en SIGA)</option>
                <option value="AUTHELIA">Authelia (forward-auth)</option>
                <option value="OIDC">OIDC / OAuth2</option>
              </select>
            </div>
            <div v-if="form.auth_modo === 'AUTHELIA'">
              <label class="label">URL de Authelia</label>
              <input v-model="form.auth_authelia_url" type="url" class="input" placeholder="https://auth.midominio.org" />
            </div>
            <div v-if="form.auth_modo === 'OIDC'">
              <label class="label">OIDC Issuer URL</label>
              <input v-model="form.auth_oidc_issuer" type="url" class="input" placeholder="https://accounts.google.com" />
            </div>
            <div class="flex gap-3">
              <div class="flex-1">
                <label class="label">Timeout de inactividad (min)</label>
                <input v-model.number="form.session_inactividad_minutos" type="number" min="0" class="input" />
                <p class="text-xs text-gray-400 mt-0.5">0 = sin timeout</p>
              </div>
              <div class="flex-1">
                <label class="label">Sesión máxima (min)</label>
                <input v-model.number="form.session_maximo_minutos" type="number" min="0" class="input" />
                <p class="text-xs text-gray-400 mt-0.5">0 = ilimitada</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Correo electrónico (SMTP) -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Correo electrónico (SMTP)</h2>
          </div>
          <div class="px-4 py-3 space-y-2">
            <!-- Servidor + Puerto -->
            <div class="flex items-end gap-2">
              <div class="flex-1 min-w-0">
                <label class="label">Servidor SMTP</label>
                <input v-model="form.smtp_host" type="text" class="input" placeholder="smtp.ejemplo.org" />
              </div>
              <div class="w-20 flex-shrink-0">
                <label class="label">Puerto</label>
                <input v-model="form.smtp_port" type="text" class="input" placeholder="587" maxlength="5" />
              </div>
            </div>
            <!-- Usuario + Contraseña -->
            <div class="flex items-end gap-2">
              <div class="flex-1 min-w-0">
                <label class="label">Usuario</label>
                <input v-model="form.smtp_usuario" type="text" class="input" autocomplete="off" placeholder="usuario@ejemplo.org" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Contraseña</label>
                <input v-model="form.smtp_password" type="password" class="input" autocomplete="new-password" placeholder="••••••••" />
              </div>
            </div>
            <!-- Dirección remitente -->
            <div>
              <label class="label">Dirección remitente (From)</label>
              <input v-model="form.smtp_from" type="email" class="input" placeholder="noreply@miasociacion.org" />
            </div>
            <!-- TLS / SSL -->
            <div class="flex items-center gap-4 pt-0.5">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="form.smtp_tls" type="checkbox"
                  class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                <span class="text-xs text-gray-700">STARTTLS</span>
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="form.smtp_ssl" type="checkbox"
                  class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                <span class="text-xs text-gray-700">SSL/TLS (puerto 465)</span>
              </label>
            </div>
          </div>
        </section>

        <!-- Redes sociales -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-purple-100 bg-purple-50 rounded-t-lg">
            <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Redes sociales</h2>
          </div>
          <div class="px-3 py-2 grid grid-cols-2 gap-1.5">
            <div v-for="red in redesSociales" :key="red.key" class="flex items-center gap-1.5 min-w-0">
              <div class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0"
                   :style="{ backgroundColor: red.bg, color: red.color }" :title="red.label">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-3 h-3">
                  <path :d="red.path" />
                </svg>
              </div>
              <div class="flex-1 min-w-0 flex items-center border border-gray-200 rounded overflow-hidden
                          focus-within:border-purple-400 focus-within:ring-1 focus-within:ring-purple-400 transition-colors">
                <span v-if="red.handle"
                  class="px-1.5 text-xs text-gray-400 bg-gray-50 border-r border-gray-200 flex-shrink-0 select-none leading-6">
                  {{ red.handle }}
                </span>
                <input v-model="form[red.key]" type="text" :placeholder="red.label"
                  class="flex-1 min-w-0 px-2 py-1 text-xs text-gray-900 placeholder-gray-400 focus:outline-none bg-transparent" />
              </div>
            </div>
          </div>
        </section>

      </div>

      <!-- Fila inferior: botones -->
      <div class="lg:col-span-2 flex items-center gap-3 pt-1">
        <button type="submit" :disabled="guardando"
          class="px-5 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
          {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
        </button>
        <button type="button" @click="router.go(-1)"
          class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5">
          <ArrowLeftIcon class="w-3.5 h-3.5" />
          Volver
        </button>
        <span v-if="guardadoOk" class="text-sm text-green-600 flex items-center gap-1">
          <CheckCircleIcon class="w-4 h-4" />
          Guardado
        </span>
        <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
      </div>

    </form>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { RouterLink, useRouter, onBeforeRouteLeave } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import EstructuraOrganizativaEditor from '@/components/configuracion/EstructuraOrganizativaEditor.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { CheckCircleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const orgConfigStore = useOrgConfigStore()

const editorRef = ref(null)

const guardando = ref(false)
const guardadoOk = ref(false)
const error = ref('')
const errorCarga = ref('')
const logoError = ref('')
const fileInput = ref(null)

const form = reactive({
  nombre: '',
  nif: '',
  tipo_entidad: 'ASOCIACION',
  contabilidad_compleja: false,
  sede_social: '',
  localidad: '',
  cp: '',
  provincia: '',
  pais: 'España',
  telefono: '',
  email: '',
  web: '',
  rrss_twitter: '',
  rrss_facebook: '',
  rrss_instagram: '',
  rrss_linkedin: '',
  rrss_youtube: '',
  logo: '',
  numero_registro: '',
  denominacion_miembro: 'miembro',
  denominacion_miembro_plural: 'miembros',
  denominacion_organo_gobierno: 'junta directiva',
  denominacion_organo_gobierno_plural: 'juntas directivas',
  auth_modo: 'LOCAL',
  auth_authelia_url: '',
  auth_oidc_issuer: '',
  session_inactividad_minutos: 30,
  session_maximo_minutos: 480,
  smtp_host: '',
  smtp_port: '587',
  smtp_usuario: '',
  smtp_password: '',
  smtp_from: '',
  smtp_tls: true,
  smtp_ssl: false,
  tema: 'violeta',
  fuente_principal: 'Inter',
})

// Snapshot del tema/fuente al entrar, para revertir si se sale sin guardar
const temaOriginal = ref(orgConfigStore.temaActivo)
const fuenteOriginal = ref(orgConfigStore.fuentePrincipal)
let guardadoExitoso = false

onBeforeRouteLeave(() => {
  if (!guardadoExitoso && temaOriginal.value) {
    orgConfigStore.applyTheme(temaOriginal.value, fuenteOriginal.value)
  }
})

const temas = computed(() => orgConfigStore.temas)
const temaPaleta = (t) => [t.t50, t.t300, t.t600, t.t800, t.t900]

const fuentesDisponibles = [
  { nombre: 'Inter',          valor: 'Inter' },
  { nombre: 'Poppins',        valor: 'Poppins' },
  { nombre: 'Nunito',         valor: 'Nunito' },
  { nombre: 'Roboto',         valor: 'Roboto' },
  { nombre: 'Open Sans',      valor: 'Open Sans' },
  { nombre: 'Plus Jakarta',   valor: 'Plus Jakarta Sans' },
]

const esObligatorioContabilidad = computed(() => {
  const tipo = (form.tipo_entidad ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  return tipo.includes('fundacion')
})
watch(esObligatorioContabilidad, (val) => { if (val) form.contabilidad_compleja = true })

watch(() => form.fuente_principal, (font) => {
  const t = orgConfigStore.temas.find(t => t.slug === form.tema) ?? form.tema
  orgConfigStore.applyTheme(t, font)
})

const redesSociales = [
  {
    key: 'rrss_twitter', label: 'Twitter / X', handle: '@', placeholder: 'usuario',
    color: '#000', bg: '#f3f4f6',
    path: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z',
  },
  {
    key: 'rrss_facebook', label: 'Facebook', handle: '', placeholder: 'pagina-o-perfil',
    color: '#1877F2', bg: '#eff6ff',
    path: 'M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z',
  },
  {
    key: 'rrss_instagram', label: 'Instagram', handle: '@', placeholder: 'usuario',
    color: '#C13584', bg: '#fdf2f8',
    path: 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z',
  },
  {
    key: 'rrss_linkedin', label: 'LinkedIn', handle: '', placeholder: 'empresa-o-perfil',
    color: '#0A66C2', bg: '#eff6ff',
    path: 'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z',
  },
  {
    key: 'rrss_youtube', label: 'YouTube', handle: '@', placeholder: 'canal',
    color: '#FF0000', bg: '#fff1f2',
    path: 'M23.495 6.205a3.007 3.007 0 00-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 00.527 6.205a31.247 31.247 0 00-.522 5.805 31.247 31.247 0 00.522 5.783 3.007 3.007 0 002.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 002.088-2.088 31.247 31.247 0 00.5-5.783 31.247 31.247 0 00-.5-5.805zM9.609 15.601V8.408l6.264 3.602z',
  },
]

const QUERY_PARAMETROS = `
  query {
    parametrosOrganizacion {
      nombre nif numeroRegistro tipoEntidad contabilidadCompleja
      sedeSocial localidad cp provincia pais
      telefono email web
      rrssTwitter rrssFacebook rrssInstagram rrssLinkedin rrssYoutube
      logo tipoAgrupacionTerritorial denominacionMiembro denominacionMiembroPlural
      denominacionOrganoGobierno denominacionOrganoGobiernoPlural
      authModo authAutheliaUrl authOidcIssuer
      sessionInactividadMinutos sessionMaximoMinutos
      smtpHost smtpPort smtpUsuario smtpPassword smtpFrom smtpTls smtpSsl
      tema fuentePrincipal
    }
  }
`

const MUTATION_GUARDAR = `
  mutation GuardarParametros($datos: ParametrosOrganizacionInput!) {
    guardarParametrosOrganizacion(datos: $datos) {
      nombre logo
    }
  }
`

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

function eliminarLogo() {
  form.logo = ''
  logoError.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

onMounted(async () => {
  if (orgConfigStore.nombre) form.nombre = orgConfigStore.nombre
  if (orgConfigStore.logo)   form.logo   = orgConfigStore.logo

  try {
    const data = await graphqlClient.request(QUERY_PARAMETROS)
    const p = data.parametrosOrganizacion
    form.nombre                = p.nombre               ?? ''
    form.nif                   = p.nif                  ?? ''
    form.numero_registro       = p.numeroRegistro        ?? ''
    form.tipo_entidad          = p.tipoEntidad           ?? 'ASOCIACION'
    form.contabilidad_compleja = p.contabilidadCompleja  ?? false
    form.sede_social           = p.sedeSocial            ?? ''
    form.localidad             = p.localidad             ?? ''
    form.cp                    = p.cp                    ?? ''
    form.provincia             = p.provincia             ?? ''
    form.pais                  = p.pais                  ?? 'España'
    form.telefono              = p.telefono              ?? ''
    form.email                 = p.email                 ?? ''
    form.web                   = p.web                   ?? ''
    form.rrss_twitter          = p.rrssTwitter           ?? ''
    form.rrss_facebook         = p.rrssFacebook          ?? ''
    form.rrss_instagram        = p.rrssInstagram         ?? ''
    form.rrss_linkedin         = p.rrssLinkedin          ?? ''
    form.rrss_youtube          = p.rrssYoutube           ?? ''
    form.logo                       = p.logo                  ?? ''
    form.denominacion_miembro               = p.denominacionMiembro              ?? 'miembro'
    form.denominacion_miembro_plural        = p.denominacionMiembroPlural        ?? 'miembros'
    form.denominacion_organo_gobierno       = p.denominacionOrganoGobierno       ?? 'junta directiva'
    form.denominacion_organo_gobierno_plural= p.denominacionOrganoGobiernoPlural ?? 'juntas directivas'
    orgConfigStore.tipoAgrupacion = p.tipoAgrupacionTerritorial ?? ''
    orgConfigStore.miembro  = form.denominacion_miembro
    orgConfigStore.miembros = form.denominacion_miembro_plural
    form.auth_modo                     = p.authModo                   ?? 'LOCAL'
    form.auth_authelia_url             = p.authAutheliaUrl             ?? ''
    form.auth_oidc_issuer              = p.authOidcIssuer              ?? ''
    form.session_inactividad_minutos   = p.sessionInactividadMinutos   ?? 30
    form.session_maximo_minutos        = p.sessionMaximoMinutos        ?? 480
    form.smtp_host                     = p.smtpHost                    ?? ''
    form.smtp_port                     = p.smtpPort                    ?? '587'
    form.smtp_usuario                  = p.smtpUsuario                 ?? ''
    form.smtp_password                 = p.smtpPassword                ?? ''
    form.smtp_from                     = p.smtpFrom                    ?? ''
    form.smtp_tls                      = p.smtpTls                     ?? true
    form.smtp_ssl                      = p.smtpSsl                     ?? false
    form.tema                          = p.tema                        ?? 'violeta'
    form.fuente_principal              = p.fuentePrincipal             ?? 'Inter'
    temaOriginal.value   = orgConfigStore.temas.find(t => t.slug === form.tema) ?? null
    fuenteOriginal.value = form.fuente_principal
    if (esObligatorioContabilidad.value) form.contabilidad_compleja = true
  } catch (e) {
    errorCarga.value = e?.response?.errors?.[0]?.message
      ?? 'No se pudieron cargar los parámetros. Comprueba la conexión con el servidor.'
  }
})


async function guardar() {
  error.value = ''
  if (!form.nombre.trim())   { error.value = 'El nombre de la organización es obligatorio'; return }
  if (!form.nif.trim())      { error.value = 'El NIF es obligatorio'; return }
  if (!form.telefono.trim()) { error.value = 'El teléfono es obligatorio'; return }
  if (!form.email.trim())    { error.value = 'El email es obligatorio'; return }
  if (!form.logo)            { error.value = 'El logotipo es obligatorio'; return }

  guardando.value = true
  guardadoOk.value = false
  try {
    await graphqlClient.request(MUTATION_GUARDAR, {
      datos: {
        nombre:               form.nombre,
        nif:                  form.nif,
        numeroRegistro:       form.numero_registro,
        tipoEntidad:          form.tipo_entidad,
        contabilidadCompleja: form.contabilidad_compleja,
        sedeSocial:           form.sede_social,
        localidad:            form.localidad,
        cp:                   form.cp,
        provincia:            form.provincia,
        pais:                 form.pais,
        telefono:             form.telefono,
        email:                form.email,
        web:                  form.web,
        rrssTwitter:          form.rrss_twitter,
        rrssFacebook:         form.rrss_facebook,
        rrssInstagram:        form.rrss_instagram,
        rrssLinkedin:         form.rrss_linkedin,
        rrssYoutube:          form.rrss_youtube,
        logo:                         form.logo,
        denominacionMiembro:                 form.denominacion_miembro,
        denominacionMiembroPlural:           form.denominacion_miembro_plural,
        denominacionOrganoGobierno:          form.denominacion_organo_gobierno,
        denominacionOrganoGobiernoPlural:    form.denominacion_organo_gobierno_plural,
        authModo:                     form.auth_modo,
        authAutheliaUrl:              form.auth_authelia_url,
        authOidcIssuer:               form.auth_oidc_issuer,
        sessionInactividadMinutos:    form.session_inactividad_minutos,
        sessionMaximoMinutos:         form.session_maximo_minutos,
        smtpHost:                     form.smtp_host,
        smtpPort:                     form.smtp_port,
        smtpUsuario:                  form.smtp_usuario,
        smtpPassword:                 form.smtp_password,
        smtpFrom:                     form.smtp_from,
        smtpTls:                      form.smtp_tls,
        smtpSsl:                      form.smtp_ssl,
        tema:                         form.tema,
        fuentePrincipal:              form.fuente_principal,
      }
    })
    orgConfigStore.miembro          = form.denominacion_miembro
    orgConfigStore.miembros         = form.denominacion_miembro_plural
    orgConfigStore.organoGobierno   = form.denominacion_organo_gobierno
    orgConfigStore.organoGobiernoPl = form.denominacion_organo_gobierno_plural
    orgConfigStore.applyTheme(form.tema, form.fuente_principal)
    orgConfigStore.markInitialized(form.nombre, form.logo, orgConfigStore.tipoAgrupacion)
    temaOriginal.value   = orgConfigStore.temas.find(t => t.slug === form.tema) ?? null
    fuenteOriginal.value = form.fuente_principal
    guardadoExitoso = true
    guardadoOk.value = true
    setTimeout(() => { guardadoOk.value = false }, 3000)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.label {
  @apply block text-xs font-medium text-gray-600 mb-0.5;
}
.input {
  @apply w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900
         placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500
         focus:outline-none transition-colors;
}
</style>
