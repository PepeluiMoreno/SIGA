<template>
  <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
    <header class="flex items-center gap-3 px-5 py-3 border-b border-slate-200">
      <span class="shrink-0 w-1.5 h-5 rounded-full" :class="acentoClass"></span>
      <h2 class="text-sm font-semibold text-slate-800">{{ title }}</h2>
      <slot name="badge" />
      <div v-if="$slots.actions" class="ml-auto flex items-center gap-2">
        <slot name="actions" />
      </div>
    </header>
    <div :class="bodyClass">
      <slot />
    </div>
  </section>
</template>

<script setup>
/**
 * FormSection — sección estándar de formulario/ficha: card con cabecera de color.
 *
 * Estandariza el patrón repetido (marcador de color + título + card) para dar
 * consistencia a todas las fichas/altas. Ver feedback_profesionalidad_extrema.
 *
 * Uso:
 *   <FormSection title="Identificación" acento="indigo">
 *     <AppFormGrid cols="3"> …campos… </AppFormGrid>
 *   </FormSection>
 *
 * Slots: default (contenido), #badge (chip junto al título), #actions (acciones
 * locales de la sección, a la derecha de la cabecera).
 */
import { computed } from 'vue'

const props = defineProps({
  title:  { type: String, required: true },
  // Color del marcador de la cabecera (mismo lenguaje que el resto de la app).
  acento: { type: String, default: 'indigo' },
  // Padding del cuerpo; 'none' para tablas que llegan al borde.
  bodyPadding: { type: Boolean, default: true },
})

const ACENTOS = {
  indigo: 'bg-indigo-500', sky: 'bg-sky-500', violet: 'bg-violet-500',
  amber: 'bg-amber-500', emerald: 'bg-emerald-500', rose: 'bg-rose-500',
  slate: 'bg-slate-400', purple: 'bg-purple-500', teal: 'bg-teal-500',
}
const acentoClass = computed(() => ACENTOS[props.acento] ?? ACENTOS.indigo)
const bodyClass = computed(() => (props.bodyPadding ? 'p-5' : ''))
</script>
