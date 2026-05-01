<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">

      <!-- Cabecera -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">Nuevo miembro</h2>
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

        <!-- Militancia -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo <span class="text-red-500">*</span></label>
            <select v-model="form.tipoMiembroId" required class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Seleccionar...</option>
              <option v-for="t in catalogos.tiposMiembro" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado <span class="text-red-500">*</span></label>
            <select v-model="form.estadoId" required class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
              <option value="">Seleccionar...</option>
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

        <!-- Fecha alta -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de alta <span class="text-red-500">*</span></label>
            <input v-model="form.fechaAlta" required type="date" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
          </div>
          <div class="flex items-end pb-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.esVoluntario" type="checkbox" class="w-4 h-4 text-purple-600 border-gray-300 rounded" />
              <span class="text-sm text-gray-700">Es voluntario/a</span>
            </label>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-800">{{ error }}</div>

      </form>

      <!-- Pie -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button @click="$emit('close')" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardar" :disabled="guardando || !formValido" class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 disabled:opacity-50">
          {{ guardando ? 'Guardando...' : 'Crear miembro' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/graphql/client.js'

const emit = defineEmits(['close', 'created'])
const router = useRouter()

const hoy = new Date().toISOString().slice(0, 10)

const form = ref({
  nombre: '',
  apellido1: '',
  apellido2: '',
  sexo: '',
  fechaNacimiento: '',
  email: '',
  telefono: '',
  tipoMiembroId: '',
  estadoId: '',
  agrupacionId: '',
  fechaAlta: hoy,
  esVoluntario: false,
})

const catalogos = ref({ tiposMiembro: [], estadosMiembro: [], agrupaciones: [] })
const guardando = ref(false)
const error = ref('')

const formValido = computed(() =>
  form.value.nombre.trim() &&
  form.value.apellido1.trim() &&
  form.value.tipoMiembroId &&
  form.value.estadoId &&
  form.value.fechaAlta
)

const agrupacionesOrdenadas = computed(() =>
  [...catalogos.value.agrupaciones].sort((a, b) => (b.nivel || 0) - (a.nivel || 0) || a.nombre.localeCompare(b.nombre, 'es'))
)

const QUERY_CATALOGOS = gql`
  query CatalogosNuevoMiembro {
    tiposMiembro(filter: { activo: { eq: true } }) { id nombre }
    estadosMiembro(filter: { activo: { eq: true } }) { id nombre }
    agrupacionesTerritoriales(filter: { activo: { eq: true } }) { id nombre nivel tipo }
  }
`

const MUTATION_CREAR = gql`
  mutation CrearMiembro($data: MiembroCreateInput!) {
    crearMiembro(data: $data) { id nombre apellido1 }
  }
`

async function cargarCatalogos() {
  try {
    const data = await graphqlClient.request(QUERY_CATALOGOS)
    catalogos.value.tiposMiembro = data.tiposMiembro || []
    catalogos.value.estadosMiembro = data.estadosMiembro || []
    catalogos.value.agrupaciones = data.agrupacionesTerritoriales || []

    // Preseleccionar "Activo" si existe
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
  try {
    const data = {
      nombre: form.value.nombre.trim(),
      apellido1: form.value.apellido1.trim(),
      apellido2: form.value.apellido2.trim() || null,
      sexo: form.value.sexo || null,
      fechaNacimiento: form.value.fechaNacimiento || null,
      email: form.value.email.trim() || null,
      telefono: form.value.telefono.trim() || null,
      tipoMiembroId: form.value.tipoMiembroId,
      estadoId: form.value.estadoId,
      agrupacionId: form.value.agrupacionId || null,
      fechaAlta: form.value.fechaAlta,
      esVoluntario: form.value.esVoluntario,
      activo: true,
    }
    const result = await graphqlClient.request(MUTATION_CREAR, { data })
    emit('created')
    router.push(`/miembros/${result.crearMiembro.id}`)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al crear el miembro'
  } finally {
    guardando.value = false
  }
}

onMounted(cargarCatalogos)
</script>
