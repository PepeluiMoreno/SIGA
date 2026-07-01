<template>
  <FormSection title="Contacto" acento="sky">
    <div class="space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <FieldText v-model="m.email" label="Email" type="email" :edit-mode="editMode" />
        <FieldText v-model="m.telefono" label="Teléfono" :edit-mode="editMode" />
        <FieldText v-model="m.telefono2" label="Tel. alternativo" :edit-mode="editMode" />
      </div>
      <div class="grid grid-cols-12 gap-4">
        <div class="col-span-12 sm:col-span-8">
          <FieldText v-model="m.direccion" label="Dirección" :edit-mode="editMode" />
        </div>
        <div class="col-span-6 sm:col-span-2">
          <FieldText v-model="m.codigoPostal" label="CP" :edit-mode="editMode" />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Ubicación (municipio / provincia)</label>
        <EntidadGeograficaSelect v-model="m.entidadGeograficaId" :editing="editMode" :niveles="[2, 3]" />
      </div>
    </div>
  </FormSection>
</template>

<script setup>
/**
 * SeccionContacto — grupo de campos de contacto (email/tel/dirección/ubicación),
 * idéntico en las fichas de Socio, Contacto y Personal. Fuente única para que se
 * vean iguales. Ver feedback_ficha_uniforme_socios.
 *
 * Trabaja sobre el objeto pasado en `modelValue` (lo muta in situ, patrón de las
 * fichas). Campos esperados: email, telefono, telefono2, direccion, codigoPostal,
 * entidadGeograficaId.
 */
import FormSection from '@/components/common/FormSection.vue'
import FieldText from '@/components/common/form/FieldText.vue'
import EntidadGeograficaSelect from '@/components/common/EntidadGeograficaSelect.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  editMode:   { type: Boolean, default: false },
})
const m = props.modelValue
</script>
