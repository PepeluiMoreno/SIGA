<template>
  <AppLayout title="Parámetros Generales" subtitle="Datos de la organización">
    <div v-if="errorCarga" class="mb-3 rounded-md bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-700 flex items-center gap-2">
      <span>⚠</span> {{ errorCarga }}
    </div>
    <form @submit.prevent="guardar" class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:h-[calc(100vh-140px)]">

      <!-- Col izquierda: Identidad + Contacto + Logotipo -->
      <div class="flex flex-col gap-4 min-h-0">

        <!-- Identidad -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Identidad</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="sm:col-span-2">
              <label class="label">Nombre de la organización <span class="text-red-500">*</span></label>
              <input v-model="form.nombre" type="text" class="input" placeholder="Nombre completo" />
            </div>
            <div>
              <label class="label">NIF <span class="text-red-500">*</span></label>
              <input v-model="form.nif" type="text" class="input" placeholder="G00000000" />
            </div>
            <div>
              <label class="label">Tipo de entidad</label>
              <select v-model="form.tipo_entidad" class="input">
                <option value="ASOCIACION">Asociación</option>
                <option value="FUNDACION">Fundación</option>
                <option value="COOPERATIVA">Cooperativa</option>
                <option value="OTRO">Otro</option>
              </select>
            </div>
            <div>
              <label class="label">Implantación geográfica</label>
              <select v-model="form.implantacion_geografica" class="input">
                <option value="">— Seleccionar —</option>
                <option value="LOCAL">Local</option>
                <option value="PROVINCIAL">Provincial</option>
                <option value="NACIONAL">Nacional</option>
                <option value="INTERNACIONAL">Internacional</option>
              </select>

              <!-- Impacto en roles territoriales -->
              <div v-if="cargandoImpacto" class="mt-2 flex items-center gap-1.5 text-xs text-gray-400">
                <span class="h-3 w-3 rounded-full border-2 border-gray-300 border-t-transparent animate-spin"></span>
                Verificando impacto en roles…
              </div>
              <div v-else-if="rolesAfectados.length" class="mt-2 rounded-lg border border-amber-300 bg-amber-50 p-3 space-y-2">
                <div class="flex items-center gap-1.5 text-xs font-semibold text-amber-800">
                  <ExclamationTriangleIcon class="w-4 h-4 flex-shrink-0" />
                  {{ rolesAfectados.length }} rol{{ rolesAfectados.length > 1 ? 'es' : '' }} con nivel incompatible
                </div>
                <p class="text-xs text-amber-700">
                  Los siguientes roles tienen un ámbito territorial que ya no es válido con la implantación
                  <strong>{{ LABEL_IMPLANTACION[form.implantacion_geografica] ?? form.implantacion_geografica }}</strong>.
                  Puedes guardar este cambio y corregirlos después.
                </p>
                <ul class="space-y-1">
                  <li v-for="rol in rolesAfectados" :key="rol.id"
                    class="flex items-center justify-between gap-2 text-xs bg-white rounded border border-amber-200 px-2 py-1">
                    <span>
                      <code class="font-mono text-amber-900">{{ rol.codigo }}</code>
                      <span class="text-gray-600 ml-1">{{ rol.nombre }}</span>
                    </span>
                    <span class="flex items-center gap-2 flex-shrink-0">
                      <span class="text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded">{{ rol.nivelTerritorial }}</span>
                      <router-link :to="`/roles/${rol.id}/editar`"
                        class="text-purple-600 hover:text-purple-800 underline">
                        Editar
                      </router-link>
                    </span>
                  </li>
                </ul>
              </div>
              <div v-else-if="impactoVerificado && !rolesAfectados.length && form.implantacion_geografica"
                class="mt-1.5 flex items-center gap-1 text-xs text-green-600">
                <CheckCircleIcon class="w-3.5 h-3.5" />
                Ningún rol territorial afectado
              </div>
            </div>
            <div>
              <label class="label">Tipo de agrupación territorial</label>
              <select v-model="form.tipo_agrupacion_territorial" class="input">
                <option v-for="op in opcionesAgrupacion" :key="op.value" :value="op.value">{{ op.label }}</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Contacto -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Contacto</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Teléfono <span class="text-red-500">*</span></label>
              <input v-model="form.telefono" type="tel" class="input" placeholder="+34 900 000 000" />
            </div>
            <div>
              <label class="label">Email <span class="text-red-500">*</span></label>
              <input v-model="form.email" type="email" class="input" placeholder="info@organización.org" />
            </div>
            <div class="sm:col-span-2">
              <label class="label">Sitio web</label>
              <input v-model="form.web" type="url" class="input" placeholder="https://www.organización.org" />
            </div>
          </div>
        </section>

        <!-- Logotipo -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Logotipo</h2>
          </div>
          <div class="px-4 py-3 flex items-center gap-4">
            <!-- Preview -->
            <div class="w-20 h-20 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center overflow-hidden flex-shrink-0">
              <img v-if="form.logo" :src="form.logo" alt="Logo" class="w-full h-full object-contain p-1" />
              <span v-else class="text-2xl text-gray-300">🏛</span>
            </div>
            <!-- Controls -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <label class="cursor-pointer px-3 py-1.5 text-xs font-medium bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-gray-700">
                  {{ form.logo ? 'Cambiar imagen' : 'Seleccionar imagen' }}
                  <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp"
                    class="hidden" @change="handleLogoChange" />
                </label>
                <button v-if="form.logo" type="button" @click="eliminarLogo"
                  class="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-md hover:bg-red-50 transition-colors">
                  Eliminar
                </button>
              </div>
              <p class="text-xs text-gray-400 mt-1.5">PNG, JPG, SVG, WEBP · máx. 300 KB</p>
              <p v-if="logoError" class="text-xs text-red-500 mt-1">{{ logoError }}</p>
            </div>
          </div>
        </section>

      </div>

      <!-- Col derecha: Sede social + Redes sociales -->
      <div class="flex flex-col gap-4 min-h-0">

        <!-- Sede social -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Sede social</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="sm:col-span-2">
              <label class="label">Dirección</label>
              <input v-model="form.sede_social" type="text" class="input" placeholder="Calle, número, piso..." />
            </div>
            <div>
              <label class="label">Localidad</label>
              <input v-model="form.localidad" type="text" class="input" />
            </div>
            <div>
              <label class="label">Código postal</label>
              <input v-model="form.cp" type="text" class="input" placeholder="28001" maxlength="10" />
            </div>
            <div>
              <label class="label">Provincia</label>
              <input v-model="form.provincia" type="text" class="input" />
            </div>
            <div>
              <label class="label">País</label>
              <input v-model="form.pais" type="text" class="input" />
            </div>
          </div>
        </section>

        <!-- Funcionalidades -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Funcionalidades</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 gap-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.multiterritorial" type="checkbox"
                class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
              <span class="text-xs text-gray-700">Organización multiterritorial (gestiona varias agrupaciones con territorios diferenciados)</span>
            </label>
            <label :class="['flex items-start gap-2', form.tipo_entidad === 'FUNDACION' ? 'opacity-75' : 'cursor-pointer']">
              <input v-model="form.contabilidad_compleja" type="checkbox"
                :disabled="form.tipo_entidad === 'FUNDACION'"
                class="h-3.5 w-3.5 mt-0.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500 flex-shrink-0" />
              <span class="text-xs text-gray-700">
                Contabilidad según Plan General Contable
                <span class="text-gray-400">(RD 1491/2011 — obligatorio para fundaciones)</span>
              </span>
            </label>
          </div>
        </section>

        <!-- Redes sociales -->
        <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Redes sociales</h2>
          </div>
          <div class="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="red in redesSociales" :key="red.key">
              <label class="label">{{ red.label }}</label>
              <div class="flex">
                <span class="inline-flex items-center px-2 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-400 text-xs whitespace-nowrap">
                  {{ red.prefix }}
                </span>
                <input v-model="form[red.key]" type="text" :placeholder="red.placeholder"
                  class="input rounded-l-none flex-1" />
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
import { RouterLink, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { ExclamationTriangleIcon, CheckCircleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const router = useRouter()

const orgConfigStore = useOrgConfigStore()

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
  implantacion_geografica: '',
  tipo_agrupacion_territorial: '',
  multiterritorial: false,
})

const LABEL_IMPLANTACION = {
  LOCAL: 'Local', PROVINCIAL: 'Provincial', NACIONAL: 'Nacional', INTERNACIONAL: 'Internacional',
}

// ── Impacto en roles territoriales ────────────────────────────────────────────
const QUERY_ROLES_TERRITORIALES = `
  query {
    roles {
      id codigo nombre tipo nivelTerritorial activo
    }
  }
`

const rolesAfectados    = ref([])
const cargandoImpacto   = ref(false)
const impactoVerificado = ref(false)
let   implantacionAlCargar = ''   // valor original al montar; para detectar cambios del usuario

async function verificarImpacto(nuevaImplantacion) {
  const permitidos = PERMITIDAS[nuevaImplantacion] ?? null
  // Si no hay restricción (null) o no hay implantación elegida, no hay conflicto
  if (!permitidos || !nuevaImplantacion) {
    rolesAfectados.value = []
    impactoVerificado.value = !!nuevaImplantacion
    return
  }
  cargandoImpacto.value = true
  impactoVerificado.value = false
  try {
    const data = await graphqlClient.request(QUERY_ROLES_TERRITORIALES)
    const todos = data.roles ?? []
    rolesAfectados.value = todos.filter(r =>
      r.tipo === 'TERRITORIAL'
      && r.nivelTerritorial
      && r.nivelTerritorial !== 'SIN_DEMARCACION'
      && !permitidos.includes(r.nivelTerritorial)
    )
  } catch {
    rolesAfectados.value = []
  } finally {
    cargandoImpacto.value   = false
    impactoVerificado.value = true
  }
}

const redesSociales = [
  { key: 'rrss_twitter',   label: 'X / Twitter',  prefix: 'x.com/',         placeholder: 'usuario' },
  { key: 'rrss_facebook',  label: 'Facebook',      prefix: 'fb.com/',        placeholder: 'pagina' },
  { key: 'rrss_instagram', label: 'Instagram',     prefix: 'instagram.com/', placeholder: 'usuario' },
  { key: 'rrss_linkedin',  label: 'LinkedIn',      prefix: 'linkedin.com/',  placeholder: 'company/nombre' },
  { key: 'rrss_youtube',   label: 'YouTube',       prefix: 'youtube.com/',   placeholder: '@canal' },
]

const TODAS_OPCIONES_AGRUPACION = [
  { value: 'MUNICIPAL',       label: 'Municipal' },
  { value: 'PROVINCIAL',      label: 'Provincial' },
  { value: 'AUTONOMICA',      label: 'Autonómica' },
  { value: 'ESTATAL',         label: 'Estatal' },
  { value: 'CONTINENTAL',     label: 'Continental' },
  { value: 'MUNDIAL',         label: 'Mundial' },
  { value: 'SIN_DEMARCACION', label: 'Sin demarcación política' },
]

const PERMITIDAS = {
  '':              null, // null = todas
  'LOCAL':         ['MUNICIPAL', 'SIN_DEMARCACION'],
  'PROVINCIAL':    ['MUNICIPAL', 'PROVINCIAL', 'SIN_DEMARCACION'],
  'NACIONAL':      ['MUNICIPAL', 'PROVINCIAL', 'AUTONOMICA', 'ESTATAL', 'SIN_DEMARCACION'],
  'INTERNACIONAL': null, // todas
}

const opcionesAgrupacion = computed(() => {
  const permitidas = PERMITIDAS[form.implantacion_geografica]
  if (!permitidas) return TODAS_OPCIONES_AGRUPACION
  return TODAS_OPCIONES_AGRUPACION.filter(o => permitidas.includes(o.value))
})

watch(() => form.implantacion_geografica, (nuevo) => {
  // Ajustar tipo_agrupacion_territorial si ya no es compatible
  const permitidas = PERMITIDAS[nuevo]
  if (permitidas && !permitidas.includes(form.tipo_agrupacion_territorial)) {
    form.tipo_agrupacion_territorial = 'SIN_DEMARCACION'
  }
  // Verificar impacto solo si el usuario ya cambió el valor (no en la carga inicial)
  if (nuevo !== implantacionAlCargar) {
    verificarImpacto(nuevo)
  }
})

watch(() => form.tipo_entidad, (val) => {
  if (val === 'FUNDACION') form.contabilidad_compleja = true
})

const QUERY_PARAMETROS = `
  query {
    parametrosOrganizacion {
      nombre nif tipoEntidad contabilidadCompleja
      sedeSocial localidad cp provincia pais
      telefono email web
      rrssTwitter rrssFacebook rrssInstagram rrssLinkedin rrssYoutube
      logo implantacionGeografica tipoAgrupacionTerritorial
      multiterritorial
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
  // Pre-poblar desde el store lo que ya tenemos (evita parpadeo)
  if (orgConfigStore.nombre) form.nombre = orgConfigStore.nombre
  if (orgConfigStore.logo)   form.logo   = orgConfigStore.logo

  try {
    const data = await graphqlClient.request(QUERY_PARAMETROS)
    const p = data.parametrosOrganizacion
    form.nombre                = p.nombre               ?? ''
    form.nif                   = p.nif                  ?? ''
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
    form.logo                        = p.logo                        ?? ''
    form.implantacion_geografica     = p.implantacionGeografica       ?? ''
    form.tipo_agrupacion_territorial = p.tipoAgrupacionTerritorial    ?? ''
    implantacionAlCargar = form.implantacion_geografica  // registrar valor original
    form.multiterritorial            = p.multiterritorial              ?? false
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
        logo:                       form.logo,
        implantacionGeografica:     form.implantacion_geografica,
        tipoAgrupacionTerritorial:  form.tipo_agrupacion_territorial,
        multiterritorial:           form.multiterritorial,
      }
    })
    orgConfigStore.markInitialized(form.nombre, form.logo)
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
