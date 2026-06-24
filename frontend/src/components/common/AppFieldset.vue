<template>
  <section class="fieldset" role="group" :aria-labelledby="title ? headingId : undefined">
    <h3 v-if="title || $slots.legend" :id="headingId" class="fieldset-legend">
      <component :is="icon" v-if="icon" class="w-4 h-4 text-purple-600 shrink-0" />
      <slot name="legend">{{ title }}</slot>
      <span v-if="$slots.accion" class="ml-auto"><slot name="accion" /></span>
    </h3>

    <AppFormGrid v-if="cols" :cols="cols">
      <slot />
    </AppFormGrid>
    <template v-else>
      <slot />
    </template>
  </section>
</template>

<script setup>
/**
 * AppFieldset — grupo de campos enmarcado, titulado y con grid opcional.
 *
 *   <AppFieldset title="Datos de contacto" cols="2">
 *     <AppFormField label="Email"><AppInput v-model="email" width="lg" /></AppFormField>
 *     <AppFormField label="Teléfono"><AppInput v-model="tel" width="sm" /></AppFormField>
 *   </AppFieldset>
 */
import AppFormGrid from './AppFormGrid.vue'

defineProps({
  title: { type: String, default: '' },
  icon:  { type: [Object, Function], default: null },
  /** Si se indica, envuelve el contenido en un AppFormGrid con esas columnas */
  cols:  { type: String, default: '' },
})

const headingId = `fieldset-${Math.random().toString(36).slice(2, 7)}`
</script>
