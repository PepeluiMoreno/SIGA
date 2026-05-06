<template>
  <div class="flex justify-end mb-2">
    <button
      @click="handleBack"
      class="px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900"
    >
      ← Volver
    </button>
  </div>
  <div class="bg-white rounded-lg shadow">
    <div v-if="!isCreateMode" class="px-6 py-4 border-b border-gray-200">
      <div class="flex flex-wrap justify-between items-center gap-3">
        <div class="flex-1 min-w-0">
          <div v-if="!isCreateMode">
            <h2 class="text-xl font-semibold text-gray-900">{{ nombreCompleto || 'Cargando...' }}</h2>
            <p v-if="miembro.tipoMiembro || miembro.estado" class="text-sm text-gray-600">
              {{ miembro.tipoMiembro?.nombre }}{{ miembro.tipoMiembro && miembro.estado ? ' - ' : '' }}{{ miembro.estado?.nombre }}
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <button
            v-if="!isCreateMode && miembro.id"
            @click="toggleEditMode"
            class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700"
          >
            {{ editMode ? 'Cancelar' : 'Editar' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="p-8 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600">{{ isCreateMode ? 'Preparando formulario...' : 'Cargando ficha de militancia...' }}</p>
    </div>

    <div v-else-if="error" class="p-8 text-center">
      <p class="text-red-600">{{ error }}</p>
      <button @click="handleBack" class="mt-4 text-purple-600 hover:underline">
        Volver a la lista
      </button>
    </div>

    <div v-else class="p-6">
      <div v-if="saveMessage" class="mb-4 rounded-md bg-green-50 border border-green-200 p-3 text-sm text-green-800">
        {{ saveMessage }}
      </div>

      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex flex-wrap gap-x-8 gap-y-2">
          <button
            v-for="tab in availableTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <div v-show="activeTab === 'personal'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <h3 class="text-lg font-semibold text-gray-900 border-b border-purple-200 pb-2">Identificación</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldText v-model="miembro.nombre" label="Nombre *" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.apellido1" label="Primer apellido *" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.apellido2" label="Segundo apellido" :edit-mode="editMode || isCreateMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldSelect
              v-model="miembro.sexo"
              label="Sexo"
              :edit-mode="editMode || isCreateMode"
              :options="sexoOptions"
            />
            <FieldText v-model="miembro.fechaNacimiento" label="Fecha de nacimiento" type="date" :edit-mode="editMode || isCreateMode" />
            <FieldSelect
              v-model="miembro.paisNacimientoId"
              label="País de nacimiento"
              :edit-mode="editMode || isCreateMode"
              :options="catalogos.paises"
              option-label="nombre"
              option-value="id"
              empty-label="Sin especificar"
            />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-12 gap-4">
            <div class="col-span-3">
              <FieldSelect
                v-model="miembro.tipoDocumento"
                label="Tipo de documento *"
                :edit-mode="editMode || isCreateMode"
                :options="tipoDocumentoOptions"
              />
            </div>
            <div class="col-span-4">
              <FieldText v-model="miembro.numeroDocumento" label="Número de documento *" :edit-mode="editMode || isCreateMode" />
            </div>
            <div class="col-span-5">
              <FieldSelect
                v-model="miembro.paisDocumentoId"
                label="País de expedición"
                :edit-mode="editMode || isCreateMode"
                :options="catalogos.paises"
                option-label="nombre"
                option-value="id"
                empty-label="Sin especificar"
              />
            </div>
          </div>
        </section>

        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <h3 class="text-lg font-semibold text-gray-900 border-b border-purple-200 pb-2">Contacto</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldText v-model="miembro.email" label="Email" type="email" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.telefono" label="Teléfono *" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.telefono2" label="Teléfono alternativo" :edit-mode="editMode || isCreateMode" />
          </div>
          <FieldText v-model="miembro.direccion" label="Dirección" :edit-mode="editMode || isCreateMode" />
          <div class="grid grid-cols-1 sm:grid-cols-12 gap-4">
            <div class="col-span-2">
              <FieldSelect
                v-model="miembro.paisDomicilioId"
                label="País"
                :edit-mode="editMode || isCreateMode"
                :options="catalogos.paises"
                option-label="nombre"
                option-value="id"
                empty-label="Sin especificar"
              />
            </div>
            <div class="col-span-3">
              <FieldSelect
                v-model="miembro.provinciaId"
                label="Provincia"
                :edit-mode="editMode || isCreateMode"
                :options="catalogos.provincias"
                option-label="nombre"
                option-value="id"
                empty-label="Sin especificar"
              />
            </div>
            <div class="col-span-5">
              <FieldText v-model="miembro.localidad" label="Localidad" :edit-mode="editMode || isCreateMode" />
            </div>
            <div class="col-span-2">
              <FieldText v-model="miembro.codigoPostal" label="CP" :edit-mode="editMode || isCreateMode" />
            </div>
          </div>
        </section>
      </div>

      <div v-show="activeTab === 'personal'" class="mt-6">
        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <FieldTextarea v-model="miembro.observaciones" label="Observaciones" :edit-mode="editMode || isCreateMode" rows="6" />
        </section>
      </div>

      <div v-show="activeTab === 'membresia'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <h3 class="text-lg font-semibold text-gray-900 border-b border-purple-200 pb-2">Estado de militancia</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldSelect
              v-model="miembro.estadoId"
              label="Estado *"
              :edit-mode="editMode || isCreateMode"
              :options="catalogos.estadosMiembro"
              option-label="nombre"
              option-value="id"
            />
            <FieldText v-model="miembro.fechaAlta" label="Fecha de alta *" type="date" :edit-mode="editMode || isCreateMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.fechaBaja" label="Fecha de baja" type="date" :edit-mode="editMode || isCreateMode" />
            <FieldSelect
              v-model="miembro.agrupacionId"
              label="Agrupación territorial"
              :edit-mode="editMode || isCreateMode"
              :options="catalogos.agrupaciones"
              option-label="nombre"
              option-value="id"
              empty-label="Sin asignar"
            />
          </div>
          <FieldSelect
            v-model="miembro.cargoId"
            label="Cargo"
            :edit-mode="editMode || isCreateMode"
            :options="catalogos.tiposCargo"
            option-label="nombre"
            option-value="id"
            empty-label="Sin cargo"
          />
        </section>

        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <h3 class="text-lg font-semibold text-gray-900 border-b border-purple-200 pb-2">Estado y RGPD</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldCheckbox v-model="miembro.esVoluntario" label="Miembro colaborador" :edit-mode="editMode || isCreateMode" />
            <FieldCheckbox v-model="miembro.esSocioHonor" label="Socio de honor" :edit-mode="editMode || isCreateMode" />
            <FieldCheckbox v-model="miembro.solicitaSupresionDatos" label="Solicita supresión de datos" :edit-mode="editMode || isCreateMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldCheckbox v-model="miembro.datosAnonimizados" label="Datos anonimizados" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.fechaSolicitudSupresion" label="Solicitud RGPD" type="date" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.fechaLimiteRetencion" label="Límite retención" type="date" :edit-mode="editMode || isCreateMode" />
          </div>
          <FieldText v-model="miembro.fechaAnonimizacion" label="Anonimización" type="date" :edit-mode="editMode || isCreateMode" />
        </section>
      </div>

      <div v-show="activeTab === 'pagoCuotas'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4 rounded-lg border border-purple-200 bg-purple-50/40 p-4">
          <h3 class="text-lg font-semibold text-gray-900 border-b border-purple-200 pb-2">Datos de pago</h3>
          <FieldSelect
            v-model="miembro.formaPagoId"
            label="Forma de pago"
            :edit-mode="editMode || isCreateMode"
            :options="catalogos.formasPago"
            option-label="nombre"
            option-value="id"
            empty-label="Sin especificar"
          />
          <FieldText v-model="miembro.iban" label="IBAN" :edit-mode="editMode || isCreateMode" />
        </section>
      </div>

      <div v-show="activeTab === 'voluntariado'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Disponibilidad</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.disponibilidad" label="Disponibilidad" :edit-mode="editMode || isCreateMode" />
            <FieldText v-model="miembro.horasDisponiblesSemana" label="Horas/semana" type="number" :edit-mode="editMode || isCreateMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldCheckbox v-model="miembro.puedeConducir" label="Puede conducir" :edit-mode="editMode || isCreateMode" />
            <FieldCheckbox v-model="miembro.vehiculoPropio" label="Vehículo propio" :edit-mode="editMode || isCreateMode" />
            <FieldCheckbox v-model="miembro.disponibilidadViajar" label="Disponibilidad para viajar" :edit-mode="editMode || isCreateMode" />
          </div>
        </section>

        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Perfil y experiencia</h3>
          <FieldText v-model="miembro.profesion" label="Profesión" :edit-mode="editMode || isCreateMode" />
          <FieldText v-model="miembro.nivelEstudios" label="Nivel de estudios" :edit-mode="editMode || isCreateMode" />
          <FieldTextarea v-model="miembro.intereses" label="Intereses" :edit-mode="editMode || isCreateMode" rows="3" />
          <FieldTextarea v-model="miembro.experienciaVoluntariado" label="Experiencia en voluntariado" :edit-mode="editMode || isCreateMode" rows="3" />
          <FieldTextarea v-model="miembro.observacionesVoluntariado" label="Observaciones de voluntariado" :edit-mode="editMode || isCreateMode" rows="3" />
        </section>
      </div>

      <!-- Tab: Habilidades -->
      <div v-show="activeTab === 'skills'" class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Habilidades y competencias</h3>
          <button
            @click="mostrarFormSkill = !mostrarFormSkill"
            class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700"
          >
            + Añadir habilidad
          </button>
        </div>

        <!-- Formulario nueva habilidad -->
        <div v-if="mostrarFormSkill" class="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Habilidad del catálogo</label>
              <select v-model="nuevaSkill.skillId" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option value="">Seleccionar...</option>
                <option v-for="s in skillsCatalogo" :key="s.id" :value="s.id">{{ s.nombre }}{{ s.categoria ? ` (${s.categoria})` : '' }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nivel</label>
              <select v-model="nuevaSkill.nivel" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option value="">Sin especificar</option>
                <option value="BASICO">Básico</option>
                <option value="INTERMEDIO">Intermedio</option>
                <option value="AVANZADO">Avanzado</option>
                <option value="EXPERTO">Experto</option>
              </select>
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="mostrarFormSkill = false; nuevaSkill = { skillId: '', nivel: '' }" class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50">Cancelar</button>
            <button @click="guardarSkill" :disabled="!nuevaSkill.skillId" class="px-3 py-1.5 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50">Guardar</button>
          </div>
        </div>

        <!-- Lista de habilidades del miembro -->
        <div v-if="loadingSkills" class="text-center py-6 text-gray-500 text-sm">Cargando habilidades...</div>
        <div v-else-if="miembroSkills.length === 0" class="text-center py-8 text-gray-400 text-sm">No hay habilidades registradas para este miembro.</div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div v-for="ms in miembroSkills" :key="ms.id" class="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-4 py-3">
            <div>
              <p class="text-sm font-medium text-gray-900">{{ ms.skill?.nombre }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <span v-if="ms.nivel" class="text-xs text-gray-500">{{ ms.nivel }}</span>
                <span v-if="ms.validado" class="text-xs text-green-600 font-medium">✓ Validado</span>
              </div>
            </div>
            <button @click="eliminarSkill(ms.id)" class="text-xs text-red-500 hover:text-red-700 ml-3">Eliminar</button>
          </div>
        </div>
      </div>

      <!-- Tab: Franjas de disponibilidad -->
      <div v-show="activeTab === 'franjas'" class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Franjas horarias semanales</h3>
          <button
            @click="mostrarFormFranja = !mostrarFormFranja"
            class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700"
          >
            + Añadir franja
          </button>
        </div>

        <!-- Formulario nueva franja -->
        <div v-if="mostrarFormFranja" class="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Día</label>
              <select v-model="nuevaFranja.diaSemana" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option v-for="(dia, i) in diasSemana" :key="i" :value="i">{{ dia }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Hora inicio</label>
              <input v-model="nuevaFranja.horaInicio" type="time" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Hora fin</label>
              <input v-model="nuevaFranja.horaFin" type="time" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="mostrarFormFranja = false; nuevaFranja = { diaSemana: 0, horaInicio: '', horaFin: '' }" class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50">Cancelar</button>
            <button @click="guardarFranja" :disabled="!nuevaFranja.horaInicio || !nuevaFranja.horaFin" class="px-3 py-1.5 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50">Guardar</button>
          </div>
        </div>

        <!-- Tabla visual por días -->
        <div v-if="loadingFranjas" class="text-center py-6 text-gray-500 text-sm">Cargando franjas...</div>
        <div v-else-if="franjas.length === 0" class="text-center py-8 text-gray-400 text-sm">No hay franjas de disponibilidad registradas.</div>
        <div v-else class="space-y-2">
          <div v-for="(dia, i) in diasSemana" :key="i" class="flex items-center gap-3">
            <span class="w-12 text-sm font-medium text-gray-600">{{ dia }}</span>
            <div class="flex flex-wrap gap-2 flex-1">
              <div
                v-for="f in franjasPorDia[i]"
                :key="f.id"
                class="flex items-center gap-2 bg-purple-100 text-purple-800 text-xs font-medium px-3 py-1 rounded-full"
              >
                <span>{{ f.horaInicio }} – {{ f.horaFin }}</span>
                <button @click="eliminarFranja(f.id)" class="text-purple-500 hover:text-red-600 font-bold leading-none">×</button>
              </div>
            </div>
            <span v-if="!franjasPorDia[i]?.length" class="text-xs text-gray-300 italic">Sin disponibilidad</span>
          </div>
        </div>
      </div>

      <div v-if="editMode || isCreateMode" class="mt-8 pt-6 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          {{ isCreateMode ? 'Cancelar' : 'Cancelar cambios' }}
        </button>
        <button
          @click="handleSave"
          :disabled="loading || !formValido"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {{ isCreateMode ? 'Crear miembro' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/graphql/client.js'
import { useMiembro } from '@/composables/useMiembro'

const route = useRoute()
const router = useRouter()
const editMode = ref(false)
const activeTab = ref('personal')
const saveMessage = ref('')

const {
  miembro,
  catalogos,
  loading,
  error,
  isCreateMode,
  nombreCompleto,
  loadCatalogos,
  fetchMiembro,
  saveMiembro,
  resetMiembro,
} = useMiembro()

const detectCreateMode = route.name === 'NuevoMiembro'

if (detectCreateMode) {
  resetMiembro()
  isCreateMode.value = true
  editMode.value = true
}

const tabs = [
  { id: 'personal', name: 'Datos personales' },
  { id: 'membresia', name: 'Militancia' },
  { id: 'pagoCuotas', name: 'Pago de cuotas' },
  { id: 'voluntariado', name: 'Disponibilidad y perfil' },
  { id: 'skills', name: 'Habilidades' },
  { id: 'franjas', name: 'Horarios' },
]

const availableTabs = computed(() => {
  if (isCreateMode.value) {
    return tabs.filter(t => !['skills', 'franjas'].includes(t.id))
  }
  return tabs
})

const formValido = computed(() => {
  if (!isCreateMode.value) return true
  const m = miembro.value
  return !!(
    m.nombre?.trim() &&
    m.apellido1?.trim() &&
    m.tipoDocumento &&
    m.numeroDocumento?.trim() &&
    m.telefono?.trim() &&
    m.estadoId &&
    m.fechaAlta
  )
})

const sexoOptions = [
  { value: 'H', label: 'Hombre' },
  { value: 'M', label: 'Mujer' },
  { value: 'X', label: 'Otro / no especificado' },
]

const tipoDocumentoOptions = [
  { value: 'DNI', label: 'DNI' },
  { value: 'NIE', label: 'NIE' },
  { value: 'NIF', label: 'NIF' },
  { value: 'TIE', label: 'TIE (Tarjeta Identidad Extranjero)' },
  { value: 'PASAPORTE', label: 'Pasaporte' },
  { value: 'OTRO', label: 'Otro documento' },
]

// ── Skills ────────────────────────────────────────────────────────────────
const miembroSkills = ref([])
const skillsCatalogo = ref([])
const loadingSkills = ref(false)
const mostrarFormSkill = ref(false)
const nuevaSkill = ref({ skillId: '', nivel: '' })

const QUERY_SKILLS_MIEMBRO = gql`
  query MiembroSkills($miembroId: UUID!) {
    miembrosSkills(filter: { miembroId: { eq: $miembroId } }) {
      id miembroId nivel validado
      skill { id nombre categoria }
    }
  }
`
const QUERY_SKILLS_CATALOGO = gql`
  query Skills { skills(filter: { activo: { eq: true } }) { id nombre categoria } }
`
const MUTATION_CREATE_SKILL = gql`
  mutation CrearMiembroSkill($data: MiembroSkillCreateInput!) {
    crearMiembroSkill(data: $data) { id }
  }
`
const MUTATION_DELETE_SKILL = gql`
  mutation EliminarMiembroSkills($filter: MiembroSkillFilter!) {
    eliminarMiembrosSkill(filter: $filter) { id }
  }
`

async function cargarSkills() {
  if (!miembro.value.id) return
  loadingSkills.value = true
  try {
    const [r1, r2] = await Promise.all([
      graphqlClient.request(QUERY_SKILLS_MIEMBRO, { miembroId: miembro.value.id }),
      graphqlClient.request(QUERY_SKILLS_CATALOGO),
    ])
    miembroSkills.value = r1.miembrosSkills || []
    skillsCatalogo.value = r2.skills || []
  } finally {
    loadingSkills.value = false
  }
}

async function guardarSkill() {
  if (!nuevaSkill.value.skillId || !miembro.value.id) return
  await graphqlClient.request(MUTATION_CREATE_SKILL, {
    data: {
      miembroId: miembro.value.id,
      skillId: nuevaSkill.value.skillId,
      nivel: nuevaSkill.value.nivel || null,
      validado: false,
    },
  })
  mostrarFormSkill.value = false
  nuevaSkill.value = { skillId: '', nivel: '' }
  await cargarSkills()
}

async function eliminarSkill(id) {
  await graphqlClient.request(MUTATION_DELETE_SKILL, { filter: { id: { eq: id } } })
  await cargarSkills()
}

// ── Franjas de disponibilidad ──────────────────────────────────────────────
const franjas = ref([])
const loadingFranjas = ref(false)
const mostrarFormFranja = ref(false)
const nuevaFranja = ref({ diaSemana: 0, horaInicio: '', horaFin: '' })
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const franjasPorDia = computed(() => {
  const grupos = {}
  for (const f of franjas.value) {
    if (!grupos[f.diaSemana]) grupos[f.diaSemana] = []
    grupos[f.diaSemana].push(f)
  }
  return grupos
})

const QUERY_FRANJAS = gql`
  query Franjas($miembroId: UUID!) {
    franjasDisponibilidad(filter: { miembroId: { eq: $miembroId }, activa: { eq: true } }) {
      id diaSemana horaInicio horaFin notas activa
    }
  }
`
const MUTATION_CREATE_FRANJA = gql`
  mutation CrearFranja($data: FranjaDisponibilidadCreateInput!) {
    crearFranjaDisponibilidad(data: $data) { id }
  }
`
const MUTATION_DELETE_FRANJA = gql`
  mutation EliminarFranjas($filter: FranjaDisponibilidadFilter!) {
    eliminarFranjasDisponibilidad(filter: $filter) { id }
  }
`

async function cargarFranjas() {
  if (!miembro.value.id) return
  loadingFranjas.value = true
  try {
    const r = await graphqlClient.request(QUERY_FRANJAS, { miembroId: miembro.value.id })
    franjas.value = (r.franjasDisponibilidad || []).sort((a, b) => a.diaSemana - b.diaSemana || a.horaInicio.localeCompare(b.horaInicio))
  } finally {
    loadingFranjas.value = false
  }
}

async function guardarFranja() {
  if (!nuevaFranja.value.horaInicio || !nuevaFranja.value.horaFin || !miembro.value.id) return
  await graphqlClient.request(MUTATION_CREATE_FRANJA, {
    data: {
      miembroId: miembro.value.id,
      diaSemana: nuevaFranja.value.diaSemana,
      horaInicio: nuevaFranja.value.horaInicio,
      horaFin: nuevaFranja.value.horaFin,
      activa: true,
    },
  })
  mostrarFormFranja.value = false
  nuevaFranja.value = { diaSemana: 0, horaInicio: '', horaFin: '' }
  await cargarFranjas()
}

async function eliminarFranja(id) {
  await graphqlClient.request(MUTATION_DELETE_FRANJA, { filter: { id: { eq: id } } })
  await cargarFranjas()
}

const handleBack = () => {
  router.push('/miembros')
}

const handleCancel = () => {
  if (isCreateMode.value) {
    router.push('/miembros')
    return
  }
  if (originalSnapshot.value) {
    miembro.value = structuredClone(originalSnapshot.value)
  }
  editMode.value = false
}

const handleSave = async () => {
  try {
    if (isCreateMode.value) {
      const created = await saveMiembro()
      if (created?.id) {
        router.push(`/miembros/${created.id}`)
      }
    } else {
      await saveMiembro()
      saveMessage.value = 'Ficha de militancia actualizada correctamente.'
      editMode.value = false
      window.setTimeout(() => {
        saveMessage.value = ''
      }, 3000)
    }
  } catch {
    saveMessage.value = ''
  }
}

const originalSnapshot = ref(null)

const toggleEditMode = () => {
  if (!editMode.value) {
    originalSnapshot.value = structuredClone(miembro.value)
    editMode.value = true
    saveMessage.value = ''
    return
  }

  if (originalSnapshot.value) {
    miembro.value = structuredClone(originalSnapshot.value)
  }
  editMode.value = false
}

onMounted(async () => {
  await loadCatalogos()
  if (isCreateMode.value) {
    const espana = catalogos.value.paises.find(p => p.codigo === 'ES')
    if (espana) miembro.value.paisDomicilioId = espana.id
    return
  }
  if (route.params.id) {
    await Promise.all([fetchMiembro(route.params.id), cargarSkills(), cargarFranjas()])
  }
})

const FieldText = defineComponent({
  props: {
    modelValue: { type: [String, Number], default: '' },
    label: { type: String, required: true },
    type: { type: String, default: 'text' },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('div', [
      h('label', { class: 'block text-sm font-medium text-gray-700' }, props.label),
      props.editMode
        ? h('input', {
            class: 'mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500',
            type: props.type,
            value: props.modelValue ?? '',
            onInput: (event) => emit('update:modelValue', event.target.value),
          })
        : h('div', { class: 'mt-1 p-2 bg-gray-50 rounded text-sm min-h-[42px]' }, formatDisplay(props.modelValue)),
    ])
  },
})

const FieldTextarea = defineComponent({
  props: {
    modelValue: { type: String, default: '' },
    label: { type: String, required: true },
    rows: { type: [Number, String], default: 4 },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('div', [
      h('label', { class: 'block text-sm font-medium text-gray-700' }, props.label),
      props.editMode
        ? h('textarea', {
            class: 'mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500',
            rows: props.rows,
            value: props.modelValue ?? '',
            onInput: (event) => emit('update:modelValue', event.target.value),
          })
        : h('div', { class: 'mt-1 p-2 bg-gray-50 rounded text-sm min-h-[60px] whitespace-pre-wrap' }, formatDisplay(props.modelValue)),
    ])
  },
})

const FieldSelect = defineComponent({
  props: {
    modelValue: { default: null },
    label: { type: String, required: true },
    options: { type: Array, default: () => [] },
    optionLabel: { type: String, default: 'label' },
    optionValue: { type: String, default: 'value' },
    emptyLabel: { type: String, default: 'Sin especificar' },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const displayValue = computed(() => {
      const current = props.options.find((item) => item?.[props.optionValue] === props.modelValue)
      return current?.[props.optionLabel] || props.emptyLabel
    })

    return () => h('div', [
      h('label', { class: 'block text-sm font-medium text-gray-700' }, props.label),
      props.editMode
        ? h(
            'select',
            {
              class: 'mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500',
              value: props.modelValue ?? '',
              onChange: (event) => emit('update:modelValue', event.target.value || null),
            },
            [
              h('option', { value: '' }, props.emptyLabel),
              ...props.options.map((item) =>
                h('option', { value: item?.[props.optionValue] }, item?.[props.optionLabel] || ''),
              ),
            ],
          )
        : h('div', { class: 'mt-1 p-2 bg-gray-50 rounded text-sm min-h-[42px]' }, displayValue.value),
    ])
  },
})

const FieldCheckbox = defineComponent({
  props: {
    modelValue: { type: Boolean, default: false },
    label: { type: String, required: true },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('label', { class: 'flex items-center rounded bg-gray-50 px-3 py-2 min-h-[42px]' }, [
      h('input', {
        type: 'checkbox',
        class: 'rounded border-gray-300 text-purple-600 focus:ring-purple-500',
        checked: props.modelValue,
        disabled: !props.editMode,
        onChange: (event) => emit('update:modelValue', event.target.checked),
      }),
      h('span', { class: 'ml-2 text-sm text-gray-700' }, props.label),
    ])
  },
})

function formatDisplay(value) {
  return value === null || value === undefined || value === '' ? '-' : String(value)
}
</script>
