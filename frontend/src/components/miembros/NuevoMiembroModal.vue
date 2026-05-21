<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">

      <!-- Cabecera -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">Nuevo {{ orgConfig.miembro }}</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
      </div>

      <!-- Cuerpo -->
      <form @submit.prevent="guardar" class="px-6 py-5 space-y-5">

        <!-- Nombre -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre <span class="text-red-500">*</span></label>
            <input v-model="form.nombre" required type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Primer apellido <span class="text-red-500">*</span></label>
            <input v-model="form.apellido1" required type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Segundo apellido</label>
            <input v-model="form.apellido2" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
          </div>
        </div>

        <!-- Sexo + fecha nacimiento -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
            <select v-model="form.sexo" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Sin especificar</option>
              <option value="H">Hombre</option>
              <option value="M">Mujer</option>
              <option value="X">Otro</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de nacimiento</label>
            <input v-model="form.fechaNacimiento" type="date" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
        </div>

        <!-- Contacto -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="form.email" type="email" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
            <input v-model="form.telefono" type="tel" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
        </div>

        <!-- Membresía -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="form.tipoMiembroId" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Sin asignar</option>
              <option v-for="t in catalogos.tiposMiembro" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select v-model="form.estadoId" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Sin asignar</option>
              <option v-for="e in catalogos.estadosMiembro" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Agrupación</label>
            <select v-model="form.agrupacionId" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Sin asignar</option>
              <option v-for="a in agrupacionesOrdenadas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
            </select>
          </div>
        </div>

        <!-- Fecha alta + voluntario -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de alta</label>
            <input v-model="form.fechaAlta" type="date" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div class="flex items-end pb-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.esVoluntario" type="checkbox" class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
              <span class="text-sm text-gray-700">Es voluntario/a</span>
            </label>
          </div>
        </div>

        <!-- ══ Sección: Crear acceso al sistema ══════════════════════════════ -->
        <div class="rounded-lg border border-dashed border-indigo-300 bg-indigo-50/40">
          <!-- Toggle cabecera -->
          <button type="button" @click="crearAcceso = !crearAcceso"
            class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors">
            <div class="flex items-center gap-2.5">
              <KeyIcon class="w-4 h-4" />
              <span>Crear cuenta de acceso al sistema</span>
            </div>
            <span class="text-xs px-2 py-0.5 rounded-full"
              :class="crearAcceso ? 'bg-indigo-600 text-white' : 'bg-indigo-100 text-indigo-500'">
              {{ crearAcceso ? 'Sí' : 'No' }}
            </span>
          </button>

          <!-- Campos de acceso (desplegables) -->
          <div v-if="crearAcceso" class="px-4 pb-4 space-y-3 border-t border-indigo-100 pt-3">
            <p class="text-xs text-indigo-600">
              Se creará el {{ orgConfig.miembro }} y su usuario en una única operación atómica.
            </p>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  Email de acceso <span class="text-red-500">*</span>
                </label>
                <input v-model="acceso.email" type="email" autocomplete="off"
                  :placeholder="form.email || 'email@example.com'"
                  class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  Tipo de vinculación
                </label>
                <select v-model="acceso.tipoVinculacionId"
                  class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option value="">— Auto (Socio) —</option>
                  <option v-for="t in catalogos.tiposVinculacion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">
                Contraseña <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input v-model="acceso.password"
                  :type="showPwd ? 'text' : 'password'"
                  autocomplete="new-password" placeholder="Mínimo 8 caracteres"
                  class="h-9 w-full px-3 pr-9 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white placeholder:text-slate-300" />
                <button type="button" tabindex="-1" @click="showPwd = !showPwd"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs">
                  {{ showPwd ? '🙈' : '👁' }}
                </button>
              </div>
            </div>

            <!-- Error de acceso -->
            <ErrorAlert v-if="errorAcceso" :message="errorAcceso" />
          </div>
        </div>

        <!-- Error general -->
        <ErrorAlert v-if="error" :message="error" />

      </form>

      <!-- Pie -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button @click="$emit('close')" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardar" :disabled="guardando || !formValido" class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 disabled:opacity-50">
          {{ guardando ? 'Guardando...' : `Crear ${orgConfig.miembro}` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig'

const emit = defineEmits(['close', 'created'])
const router = useRouter()
const orgConfig = useOrgConfigStore()

const hoy = new Date().toISOString().slice(0, 10)

const form = ref({
  nombre: '', apellido1: '', apellido2: '',
  sexo: '', fechaNacimiento: '', email: '', telefono: '',
  tipoMiembroId: '', estadoId: '', agrupacionId: '',
  fechaAlta: hoy, esVoluntario: false,
})

// Sección de acceso (opcional)
const crearAcceso = ref(false)
const acceso      = ref({ email: '', password: '', tipoVinculacionId: '' })
const showPwd     = ref(false)
const errorAcceso = ref('')

const catalogos = ref({ tiposMiembro: [], estadosMiembro: [], agrupaciones: [], tiposVinculacion: [] })
const guardando = ref(false)
const error = ref('')

const formValido = computed(() => {
  if (!form.value.nombre.trim() || !form.value.apellido1.trim()) return false
  if (crearAcceso.value) {
    if (!acceso.value.email.trim() || acceso.value.password.length < 8) return false
  }
  return true
})

const agrupacionesOrdenadas = computed(() =>
  [...catalogos.value.agrupaciones].sort((a, b) => ((b.tipoUnidad?.nivel || 0) - (a.tipoUnidad?.nivel || 0)) || a.nombre.localeCompare(b.nombre, 'es'))
)

const QUERY_CATALOGOS = gql`
  query CatalogosNuevoMiembro {
    tiposMiembro(filter: { activo: { eq: true } }) { id nombre }
    estadosMiembro(filter: { activo: { eq: true } }) { id nombre }
    unidadesOrganizativas(filter: { activo: { eq: true } }) { id nombre tipoUnidad { nivel } }
    tiposVinculacion(filter: { activo: { eq: true } }) { id nombre requiereEntidad }
  }
`

const MUTATION_CREAR = gql`
  mutation CrearMiembro($data: MiembroCreateInput!) {
    crearMiembro(data: $data) { id nombre apellido1 }
  }
`

const MUTATION_CREAR_CON_ACCESO = gql`
  mutation CrearMiembroConAcceso(
    $data: MiembroCreateInput!
    $email: String!
    $password: String!
    $tipoVinculacionId: UUID
    $activoUsuario: Boolean
  ) {
    crearMiembroConAcceso(
      data: $data
      email: $email
      password: $password
      tipoVinculacionId: $tipoVinculacionId
      activoUsuario: $activoUsuario
    ) { id nombre apellido1 }
  }
`

async function cargarCatalogos() {
  try {
    const alpha = (a, b) => a.nombre.localeCompare(b.nombre, 'es')
    const data = await graphqlClient.request(QUERY_CATALOGOS)
    catalogos.value.tiposMiembro    = (data.tiposMiembro || []).sort(alpha)
    catalogos.value.estadosMiembro  = (data.estadosMiembro || []).sort(alpha)
    catalogos.value.agrupaciones    = data.unidadesOrganizativas || []
    catalogos.value.tiposVinculacion = (data.tiposVinculacion || []).sort(alpha)

    const activo = catalogos.value.estadosMiembro.find(e => e.nombre === 'Activo')
    if (activo) form.value.estadoId = activo.id
  } catch (e) {
    error.value = 'Error cargando catálogos'
  }
}

async function guardar() {
  if (!formValido.value || guardando.value) return
  guardando.value = true
  error.value = ''
  errorAcceso.value = ''

  try {
    const data = {
      nombre: form.value.nombre.trim(),
      apellido1: form.value.apellido1.trim(),
      apellido2: form.value.apellido2.trim() || null,
      sexo: form.value.sexo || null,
      fechaNacimiento: form.value.fechaNacimiento || null,
      email: form.value.email.trim() || null,
      telefono: form.value.telefono.trim() || null,
      tipoMiembroId: form.value.tipoMiembroId || null,
      estadoId: form.value.estadoId || null,
      agrupacionId: form.value.agrupacionId || null,
      fechaAlta: form.value.fechaAlta || null,
      esVoluntario: form.value.esVoluntario,
      activo: true,
    }

    let result
    if (crearAcceso.value) {
      // Auto-tipo: si no eligió, intentar con 'Socio'
      const autoTipo = catalogos.value.tiposVinculacion.find(
        t => t.nombre.toLowerCase().includes('socio') && !t.nombre.toLowerCase().includes('amiga')
      )
      result = await graphqlClient.request(MUTATION_CREAR_CON_ACCESO, {
        data,
        email:             acceso.value.email.trim(),
        password:          acceso.value.password,
        tipoVinculacionId: acceso.value.tipoVinculacionId || autoTipo?.id || null,
        activoUsuario:     true,
      })
      emit('created')
      router.push(`/miembros/${result.crearMiembroConAcceso.id}`)
    } else {
      result = await graphqlClient.request(MUTATION_CREAR, { data })
      emit('created')
      router.push(`/miembros/${result.crearMiembro.id}`)
    }
  } catch (e) {
    const msg = e?.response?.errors?.[0]?.message || `Error al crear el ${orgConfig.miembro}`
    if (msg.toLowerCase().includes('email') || msg.toLowerCase().includes('usuario')) {
      errorAcceso.value = msg
    } else {
      error.value = msg
    }
  } finally {
    guardando.value = false
  }
}

onMounted(cargarCatalogos)
</script>
