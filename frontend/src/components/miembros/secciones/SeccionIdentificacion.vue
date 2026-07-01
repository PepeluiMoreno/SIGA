<template>
  <FormSection title="Identificación" acento="purple">
    <div class="flex flex-col sm:flex-row gap-5">
      <!-- Panel de la foto: lo aporta la ficha (su lógica de subida difiere) -->
      <div v-if="$slots.foto" class="shrink-0 flex flex-col items-center gap-2 sm:w-40">
        <slot name="foto" />
      </div>

      <!-- Fieldset de identificación, idéntico en todas las fichas de personas -->
      <div class="flex-1 min-w-0 space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldText v-model="m.nombre" label="Nombre *" :edit-mode="editMode" />
          <FieldText v-model="m.apellido1" label="Primer apellido *" :edit-mode="editMode" />
          <FieldText v-model="m.apellido2" label="Segundo apellido" :edit-mode="editMode" />
          <FieldSelect v-model="m.sexo" label="Sexo" :edit-mode="editMode" :options="sexoOptions" />
          <FieldText v-model="m.fechaNacimiento" label="Fecha de nacimiento" type="date" :edit-mode="editMode" />
          <FieldSelect v-model="m.paisNacimientoId" label="País de nacimiento" :edit-mode="editMode"
            :options="paises" option-label="nombre" option-value="id" empty-label="Sin especificar" />
        </div>
        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-4 sm:col-span-3">
            <FieldSelect v-model="m.tipoDocumento" label="Tipo doc." :edit-mode="editMode" :options="tipoDocumentoOptions" />
          </div>
          <div class="col-span-8 sm:col-span-4">
            <FieldText v-model="m.numeroDocumento" label="Número" :edit-mode="editMode" />
          </div>
          <div class="col-span-12 sm:col-span-5">
            <FieldSelect v-model="m.paisDocumentoId" label="País expedición" :edit-mode="editMode"
              :options="paises" option-label="nombre" option-value="id" empty-label="Sin especificar" />
          </div>
        </div>
      </div>
    </div>
  </FormSection>
</template>

<script setup>
/**
 * SeccionIdentificacion — fieldset de identificación de una persona (nombre,
 * apellidos, sexo, nacimiento, documento), idéntico en las fichas de Socio,
 * Contacto y Personal. Fuente única para uniformidad. La foto se pasa por el
 * slot #foto (su lógica de subida es propia de cada ficha).
 * Ver feedback_ficha_uniforme_socios.
 */
import FormSection from '@/components/common/FormSection.vue'
import FieldText from '@/components/common/form/FieldText.vue'
import FieldSelect from '@/components/common/form/FieldSelect.vue'

const props = defineProps({
  modelValue:          { type: Object, required: true },
  editMode:            { type: Boolean, default: false },
  paises:              { type: Array, default: () => [] },
  sexoOptions:         { type: Array, default: () => [] },
  tipoDocumentoOptions:{ type: Array, default: () => [] },
})
const m = props.modelValue
</script>
