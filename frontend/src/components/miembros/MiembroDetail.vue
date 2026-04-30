<template>
  <div class="bg-white rounded-lg shadow">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ nombreCompleto || 'Cargando...' }}</h2>
          <p v-if="miembro.tipoMiembro || miembro.estado" class="text-sm text-gray-600">
            {{ miembro.tipoMiembro?.nombre }}{{ miembro.tipoMiembro && miembro.estado ? ' - ' : '' }}{{ miembro.estado?.nombre }}
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="$router.push('/miembros')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Volver
          </button>
          <button
            v-if="miembro.id"
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
      <p class="mt-2 text-gray-600">Cargando ficha de militancia...</p>
    </div>

    <div v-else-if="error" class="p-8 text-center">
      <p class="text-red-600">{{ error }}</p>
      <button @click="$router.push('/miembros')" class="mt-4 text-purple-600 hover:underline">
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
            v-for="tab in tabs"
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
        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Identificación</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldText v-model="miembro.nombre" label="Nombre" :edit-mode="editMode" />
            <FieldText v-model="miembro.apellido1" label="Primer apellido" :edit-mode="editMode" />
            <FieldText v-model="miembro.apellido2" label="Segundo apellido" :edit-mode="editMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldSelect
              v-model="miembro.sexo"
              label="Sexo"
              :edit-mode="editMode"
              :options="sexoOptions"
            />
            <FieldText v-model="miembro.fechaNacimiento" label="Fecha de nacimiento" type="date" :edit-mode="editMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.tipoDocumento" label="Tipo de documento" :edit-mode="editMode" />
            <FieldText v-model="miembro.numeroDocumento" label="Número de documento" :edit-mode="editMode" />
          </div>
          <FieldSelect
            v-model="miembro.paisDocumentoId"
            label="País del documento"
            :edit-mode="editMode"
            :options="catalogos.paises"
            option-label="nombre"
            option-value="id"
            empty-label="Sin especificar"
          />
        </section>

        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Contacto</h3>
          <FieldText v-model="miembro.email" label="Email" type="email" :edit-mode="editMode" />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.telefono" label="Teléfono" :edit-mode="editMode" />
            <FieldText v-model="miembro.telefono2" label="Teléfono 2" :edit-mode="editMode" />
          </div>
          <FieldText v-model="miembro.direccion" label="Dirección" :edit-mode="editMode" />
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldText v-model="miembro.codigoPostal" label="Código postal" :edit-mode="editMode" />
            <FieldText v-model="miembro.localidad" label="Localidad" :edit-mode="editMode" />
            <FieldSelect
              v-model="miembro.provinciaId"
              label="Provincia"
              :edit-mode="editMode"
              :options="catalogos.provincias"
              option-label="nombre"
              option-value="id"
              empty-label="Sin especificar"
            />
          </div>
          <FieldSelect
            v-model="miembro.paisDomicilioId"
            label="País de domicilio"
            :edit-mode="editMode"
            :options="catalogos.paises"
            option-label="nombre"
            option-value="id"
            empty-label="Sin especificar"
          />
        </section>
      </div>

      <div v-show="activeTab === 'membresia'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Estado de militancia</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldSelect
              v-model="miembro.tipoMiembroId"
              label="Tipo de miembro"
              :edit-mode="editMode"
              :options="catalogos.tiposMiembro"
              option-label="nombre"
              option-value="id"
            />
            <FieldSelect
              v-model="miembro.estadoId"
              label="Estado"
              :edit-mode="editMode"
              :options="catalogos.estadosMiembro"
              option-label="nombre"
              option-value="id"
            />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.fechaAlta" label="Fecha de alta" type="date" :edit-mode="editMode" />
            <FieldText v-model="miembro.fechaBaja" label="Fecha de baja" type="date" :edit-mode="editMode" />
          </div>
          <FieldSelect
            v-model="miembro.agrupacionId"
            label="Agrupación territorial"
            :edit-mode="editMode"
            :options="catalogos.agrupaciones"
            option-label="nombre"
            option-value="id"
            empty-label="Sin asignar"
          />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldSelect
              v-model="miembro.cargoId"
              label="Cargo"
              :edit-mode="editMode"
              :options="catalogos.tiposCargo"
              option-label="nombre"
              option-value="id"
              empty-label="Sin cargo"
            />
            <FieldText v-model="miembro.iban" label="IBAN" :edit-mode="editMode" />
          </div>
          <FieldSelect
            v-model="miembro.motivoBajaId"
            label="Motivo de baja"
            :edit-mode="editMode"
            :options="catalogos.motivosBaja"
            option-label="nombre"
            option-value="id"
            empty-label="Sin motivo"
          />
          <FieldTextarea v-model="miembro.motivoBajaTexto" label="Detalle de baja" :edit-mode="editMode" rows="3" />
        </section>

        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Estado y RGPD</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldCheckbox v-model="miembro.activo" label="Miembro activo" :edit-mode="editMode" />
            <FieldCheckbox v-model="miembro.esVoluntario" label="Miembro colaborador" :edit-mode="editMode" />
            <FieldCheckbox v-model="miembro.solicitaSupresionDatos" label="Solicita supresión de datos" :edit-mode="editMode" />
            <FieldCheckbox v-model="miembro.datosAnonimizados" label="Datos anonimizados" :edit-mode="editMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldText v-model="miembro.fechaSolicitudSupresion" label="Solicitud RGPD" type="date" :edit-mode="editMode" />
            <FieldText v-model="miembro.fechaLimiteRetencion" label="Límite retención" type="date" :edit-mode="editMode" />
            <FieldText v-model="miembro.fechaAnonimizacion" label="Anonimización" type="date" :edit-mode="editMode" />
          </div>
        </section>
      </div>

      <div v-show="activeTab === 'voluntariado'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Disponibilidad</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldText v-model="miembro.disponibilidad" label="Disponibilidad" :edit-mode="editMode" />
            <FieldText v-model="miembro.horasDisponiblesSemana" label="Horas/semana" type="number" :edit-mode="editMode" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FieldCheckbox v-model="miembro.puedeConducir" label="Puede conducir" :edit-mode="editMode" />
            <FieldCheckbox v-model="miembro.vehiculoPropio" label="Vehículo propio" :edit-mode="editMode" />
            <FieldCheckbox v-model="miembro.disponibilidadViajar" label="Disponibilidad para viajar" :edit-mode="editMode" />
          </div>
        </section>

        <section class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Perfil y experiencia</h3>
          <FieldText v-model="miembro.profesion" label="Profesión" :edit-mode="editMode" />
          <FieldText v-model="miembro.nivelEstudios" label="Nivel de estudios" :edit-mode="editMode" />
          <FieldTextarea v-model="miembro.intereses" label="Intereses" :edit-mode="editMode" rows="3" />
          <FieldTextarea v-model="miembro.experienciaVoluntariado" label="Experiencia en voluntariado" :edit-mode="editMode" rows="3" />
          <FieldTextarea v-model="miembro.observacionesVoluntariado" label="Observaciones de voluntariado" :edit-mode="editMode" rows="3" />
        </section>
      </div>

      <div v-show="activeTab === 'observaciones'" class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Observaciones generales</h3>
        <FieldTextarea v-model="miembro.observaciones" label="Observaciones" :edit-mode="editMode" rows="8" />
      </div>

      <div v-if="editMode" class="mt-8 pt-6 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="toggleEditMode"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          @click="handleSave"
          :disabled="loading"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          Guardar cambios
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMiembro } from '@/composables/useMiembro'

const route = useRoute()
const editMode = ref(false)
const activeTab = ref('personal')
const saveMessage = ref('')

const tabs = [
  { id: 'personal', name: 'Datos personales' },
  { id: 'membresia', name: 'Militancia' },
  { id: 'voluntariado', name: 'Disponibilidad y perfil' },
  { id: 'observaciones', name: 'Observaciones' },
]

const {
  miembro,
  catalogos,
  loading,
  error,
  nombreCompleto,
  loadCatalogos,
  fetchMiembro,
  saveMiembro,
} = useMiembro()

const sexoOptions = [
  { value: 'H', label: 'Hombre' },
  { value: 'M', label: 'Mujer' },
  { value: 'X', label: 'Otro / no especificado' },
]

onMounted(async () => {
  await loadCatalogos()
  if (route.params.id) {
    await fetchMiembro(route.params.id)
  }
})

const handleSave = async () => {
  try {
    await saveMiembro()
    saveMessage.value = 'Ficha de militancia actualizada correctamente.'
    editMode.value = false
    window.setTimeout(() => {
      saveMessage.value = ''
    }, 3000)
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
