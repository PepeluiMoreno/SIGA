<template>
  <div class="border border-slate-200 rounded-lg p-3 bg-slate-50">
    <div class="flex items-center gap-2 mb-2">
      <span class="text-xs font-medium text-slate-700">
        {{ label }} <span v-if="required" class="text-red-500">*</span>
      </span>
      <span v-if="tooltip" :title="tooltip"
            class="text-slate-400 hover:text-slate-600 cursor-help select-none">ⓘ</span>
    </div>

    <div class="space-y-2 mb-3">
      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input type="radio" :value="'CAMPANIA'" :checked="modo === 'CAMPANIA'" @change="setModo('CAMPANIA')" />
        <span>De campaña</span>
      </label>
      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input type="radio" :value="'FUERA'" :checked="modo === 'FUERA'" @change="setModo('FUERA')" />
        <span>Fuera de campaña</span>
      </label>
      <label v-if="allowSinImputar" class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input type="radio" :value="'NINGUNA'" :checked="modo === 'NINGUNA'" @change="setModo('NINGUNA')" />
        <span>Sin imputar <span class="text-slate-400">(apunte estructural)</span></span>
      </label>
    </div>

    <!-- A) Actividad de campaña → dos pasos -->
    <div v-if="modo === 'CAMPANIA'" class="grid grid-cols-1 gap-2">
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">Campaña <span v-if="required" class="text-red-500">*</span></label>
        <select :value="campaniaId" @change="setCampania($event.target.value || null)"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400">
          <option :value="null">— Selecciona campaña —</option>
          <option v-for="c in campaniasAbiertas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
        <p v-if="!campaniasAbiertas.length" class="text-xs text-amber-700 mt-1">
          No hay campañas abiertas a imputación.
        </p>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">Actividad de la campaña <span v-if="required" class="text-red-500">*</span></label>
        <select :value="actividadId" @change="setActividad($event.target.value || null)"
                :disabled="!campaniaId"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-slate-100 disabled:text-slate-400">
          <option :value="null">— Selecciona actividad —</option>
          <option v-for="a in actividadesDeCampania" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </select>
        <p v-if="campaniaId && !actividadesDeCampania.length" class="text-xs text-amber-700 mt-1">
          Esta campaña no tiene actividades.
        </p>
      </div>
    </div>

    <!-- B) Fuera de campaña → selector único de actividad, agrupado por tipo -->
    <div v-else-if="modo === 'FUERA'">
      <label class="block text-xs font-medium text-slate-700 mb-1">Actividad <span v-if="required" class="text-red-500">*</span></label>
      <select :value="actividadId" @change="setActividad($event.target.value || null)"
              class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400">
        <option :value="null">— Selecciona actividad —</option>
        <optgroup v-if="actsPorTipo.PERMANENTE.length" label="Permanentes">
          <option v-for="a in actsPorTipo.PERMANENTE" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </optgroup>
        <optgroup v-if="actsPorTipo.PUNTUAL.length" label="Puntuales">
          <option v-for="a in actsPorTipo.PUNTUAL" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </optgroup>
        <optgroup v-if="actsPorTipo.RECURRENTE.length" label="Recurrentes (instancias)">
          <option v-for="a in actsPorTipo.RECURRENTE" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </optgroup>
      </select>
      <p v-if="!actividadesFueraDeCampania.length" class="text-xs text-amber-700 mt-1">
        No hay actividades fuera de campaña.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * Picker reutilizable de imputación a actividad para Tesorería, Justificantes y Contabilidad.
 *
 * Encapsula la taxonomía de actividades de SIGA:
 *  - A) De campaña: se elige campaña → actividad.
 *  - B) Fuera de campaña: selector único de actividad, con las opciones
 *       agrupadas por tipo (Permanentes / Puntuales / Recurrentes) solo a
 *       efectos de presentación. El tipo NO es un dato de la imputación.
 *
 * Plantillas recurrentes (RECURRENTE && padre_id NULL) NUNCA aparecen.
 * Campañas con estado.codigo ∈ {CERRADA, CANCELADA} se excluyen.
 *
 * El valor del componente es un objeto con todo el estado:
 *   { modo, campaniaId, actividadId }
 * El padre lo recibe via v-model y los cambios siguen siendo controlados (single source of truth).
 */
const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    // { modo: 'CAMPANIA'|'FUERA'|'NINGUNA', campaniaId: string|null, actividadId: string|null }
  },
  campanias:   { type: Array, default: () => [] },
  actividades: { type: Array, default: () => [] },
  label:           { type: String, default: 'Imputación a actividad' },
  tooltip:         { type: String, default: '' },
  required:        { type: Boolean, default: true },
  // Cuando true, añade un tercer modo 'NINGUNA' (sin imputar). Usado en Contabilidad
  // (edición de apuntes estructurales sin actividad concreta).
  allowSinImputar: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const modo        = computed(() => props.modelValue?.modo || 'CAMPANIA')
const campaniaId  = computed(() => props.modelValue?.campaniaId ?? null)
const actividadId = computed(() => props.modelValue?.actividadId ?? null)

const update = (patch) => emit('update:modelValue', { ...props.modelValue, ...patch })

const setModo = (m) => update({ modo: m, actividadId: null })
const setCampania = (id) => update({ campaniaId: id, actividadId: null })
const setActividad = (id) => update({ actividadId: id })

// Plantillas recurrentes no son imputables (excluye `caracter=RECURRENTE && padre_id=null`).
const esImputable = (a) => !(a.caracter === 'RECURRENTE' && !a.padreId)

// Campañas que admiten imputación, alfabético.
const CERRADAS = ['CERRADA', 'CANCELADA']
const campaniasAbiertas = computed(() =>
  (props.campanias || [])
    .filter(c => !CERRADAS.includes(c.estado?.codigo))
    .slice()
    .sort((a, b) => (a.nombre || '').localeCompare(b.nombre || '', 'es'))
)

const actividadesDeCampania = computed(() => {
  const id = campaniaId.value
  if (!id) return []
  return (props.actividades || [])
    .filter(a => a.campaniaId === id && esImputable(a))
    .slice()
    .sort((x, y) => (x.nombre || '').localeCompare(y.nombre || '', 'es'))
})

// Todas las actividades fuera de campaña imputables, alfabético.
const actividadesFueraDeCampania = computed(() =>
  (props.actividades || [])
    .filter(a => !a.campaniaId && esImputable(a))
    .slice()
    .sort((x, y) => (x.nombre || '').localeCompare(y.nombre || '', 'es'))
)

// Agrupadas por tipo solo para los <optgroup> del selector.
const actsPorTipo = computed(() => {
  const grupos = { PERMANENTE: [], PUNTUAL: [], RECURRENTE: [] }
  for (const a of actividadesFueraDeCampania.value) {
    (grupos[a.caracter] || grupos.PUNTUAL).push(a)
  }
  return grupos
})
</script>
