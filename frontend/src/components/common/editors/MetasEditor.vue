<template>
  <div class="space-y-3">
    <!-- Modo editable: tabla con inputs -->
    <template v-if="editable">
      <div v-if="modelValue.length" class="rounded-lg border border-slate-200 overflow-hidden">
        <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <span class="col-span-5">Tipo de meta</span>
          <span class="col-span-2">Unidad</span>
          <span class="col-span-2 text-right">Valor</span>
          <span class="col-span-2">Notas</span>
          <span class="col-span-1"></span>
        </div>
        <div v-for="(m, i) in modelValue" :key="m.id ?? m._id ?? i"
          class="grid grid-cols-12 gap-2 px-4 py-2 items-center border-b border-slate-100 last:border-0"
          :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
          <div class="col-span-5">
            <select :value="m[fTipo]" class="w-full h-8 px-2 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              @change="set(m, fTipo, $event.target.value); emitChange()">
              <option value="">— Tipo —</option>
              <option v-for="t in tiposMeta" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="col-span-2 text-xs text-slate-500">{{ unidadDe(m[fTipo]) }}</div>
          <div class="col-span-2">
            <input :value="m[fValor]" type="number" min="0" step="1"
              class="w-full h-8 px-2 text-sm text-right border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="—" @input="setNum(m, fValor, $event.target.value)" @blur="emitBlur" />
          </div>
          <div class="col-span-2">
            <input :value="m.notas" type="text"
              class="w-full h-8 px-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Notas…" @input="set(m, 'notas', $event.target.value)" @blur="emitBlur" />
          </div>
          <div class="col-span-1 flex justify-end">
            <button type="button" title="Eliminar meta" @click="eliminar(i)"
              class="p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      <button type="button" @click="agregar"
        class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
        <PlusIcon class="w-3.5 h-3.5" /> Añadir meta
      </button>
    </template>

    <!-- Modo lectura: tabla con planificado / real / % -->
    <template v-else>
      <div v-if="modelValue.length" class="rounded-lg border border-slate-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="text-left px-4 py-2">Meta</th>
              <th class="text-left px-4 py-2">Unidad</th>
              <th class="text-right px-4 py-2">Planificado</th>
              <th class="text-right px-4 py-2">Real</th>
              <th class="text-right px-4 py-2">%</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, i) in modelValue" :key="m.id ?? i" class="border-b border-slate-100 last:border-0">
              <td class="px-4 py-2 text-slate-800">{{ m.tipoMeta?.nombre ?? '—' }}</td>
              <td class="px-4 py-2 text-slate-500">{{ m.tipoMeta?.unidadMedida ?? '—' }}</td>
              <td class="px-4 py-2 text-right text-slate-700">{{ m[fValor] ?? '—' }}</td>
              <td class="px-4 py-2 text-right text-slate-700">{{ m[fReal] ?? '—' }}</td>
              <td class="px-4 py-2 text-right font-medium" :class="pct(m) >= 100 ? 'text-emerald-600' : 'text-amber-600'">
                {{ pctText(m) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-sm text-slate-400 italic">Sin metas definidas.</p>
    </template>
  </div>
</template>

<script setup>
/**
 * MetasEditor — editor/visor reutilizable de metas de campaña o plantilla.
 *
 * Unifica el bloque de metas duplicado en DetallePlantilla, CampaniaForm y
 * DetalleCampania. Las divergencias de nomenclatura (valorSugerido vs
 * valor_planificado, camelCase vs snake_case) se resuelven con props de nombre
 * de campo (fieldTipo/fieldValor/fieldReal). Ver feedback_profesionalidad_extrema.
 *
 * v-model = array de metas (se muta in situ y se emite update:modelValue).
 * @blur → emite 'persist' (para el guardado por @blur de plantilla).
 */
import { computed } from 'vue'
import { PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  tiposMeta:  { type: Array, default: () => [] },
  editable:   { type: Boolean, default: true },
  // Nombres de campo (para cubrir camelCase / snake_case entre vistas).
  fieldTipo:  { type: String, default: 'tipoMetaId' },
  fieldValor: { type: String, default: 'valorSugerido' },
  fieldReal:  { type: String, default: 'valorReal' },
})
const emit = defineEmits(['update:modelValue', 'persist'])

const fTipo = computed(() => props.fieldTipo).value
const fValor = computed(() => props.fieldValor).value
const fReal = computed(() => props.fieldReal).value

function unidadDe(tipoId) {
  return props.tiposMeta.find((t) => t.id === tipoId)?.unidadMedida || '—'
}
function set(m, k, v) { m[k] = v }
function setNum(m, k, v) { m[k] = v === '' ? null : Number(v); emitChange() }
function emitChange() { emit('update:modelValue', props.modelValue) }
function emitBlur() { emit('persist') }
function agregar() {
  props.modelValue.push({ id: null, [fTipo]: '', [fValor]: null, notas: '', orden: props.modelValue.length + 1 })
  emitChange()
}
function eliminar(i) { props.modelValue.splice(i, 1); emitChange(); emit('persist') }

function pct(m) {
  const plan = Number(m[fValor]) || 0
  const real = Number(m[fReal]) || 0
  return plan ? (real / plan) * 100 : 0
}
function pctText(m) {
  const plan = Number(m[fValor]) || 0
  return plan ? `${Math.round(pct(m))}%` : '—'
}
</script>
