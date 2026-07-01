<template>
  <div class="space-y-3">
    <!-- Modo editable -->
    <template v-if="editable">
      <div v-if="modelValue.length" class="rounded-lg border border-slate-200 overflow-hidden">
        <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <span class="col-span-6">Concepto</span>
          <span class="col-span-3">Tipo</span>
          <span class="col-span-2 text-right">Importe est.</span>
          <span class="col-span-1"></span>
        </div>
        <div v-for="(p, i) in modelValue" :key="p.id ?? p._id ?? i"
          class="grid grid-cols-12 gap-2 px-4 py-2 items-center border-b border-slate-100 last:border-0"
          :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
          <div class="col-span-6">
            <input :value="p.concepto" type="text" placeholder="Concepto…"
              class="w-full h-8 px-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
              @input="set(p, 'concepto', $event.target.value)" @blur="emitBlur" />
          </div>
          <div class="col-span-3">
            <select :value="p[fTipo]" class="w-full h-8 px-2 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
              @change="set(p, fTipo, $event.target.value); emitChange()">
              <option value="gasto">Gasto</option>
              <option value="ingreso">Ingreso</option>
            </select>
          </div>
          <div class="col-span-2">
            <input :value="p[fImporte]" type="number" min="0" step="0.01" placeholder="0.00"
              class="w-full h-8 px-2 text-sm text-right border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
              @input="setNum(p, fImporte, $event.target.value)" @blur="emitBlur" />
          </div>
          <div class="col-span-1 flex justify-end">
            <button type="button" title="Eliminar partida" @click="eliminar(i)"
              class="p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
        <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-t border-slate-200 text-xs font-semibold text-slate-600">
          <span class="col-span-9 text-right">Total gastos estimados</span>
          <span class="col-span-2 text-right">{{ fmtEur(totalGastos) }}</span>
          <span class="col-span-1"></span>
        </div>
      </div>
      <button type="button" @click="agregar"
        class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
        <PlusIcon class="w-3.5 h-3.5" /> Añadir partida
      </button>
    </template>

    <!-- Modo lectura: est. / real -->
    <template v-else>
      <div v-if="modelValue.length" class="rounded-lg border border-slate-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="text-left px-4 py-2">Concepto</th>
              <th class="text-left px-4 py-2">Tipo</th>
              <th class="text-right px-4 py-2">Estimado</th>
              <th class="text-right px-4 py-2">Real</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p, i) in modelValue" :key="p.id ?? i" class="border-b border-slate-100 last:border-0">
              <td class="px-4 py-2 text-slate-800">{{ p.concepto }}</td>
              <td class="px-4 py-2">
                <span class="px-2 py-0.5 text-xs rounded-full"
                  :class="p[fTipo] === 'ingreso' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'">
                  {{ p[fTipo] === 'ingreso' ? 'Ingreso' : 'Gasto' }}
                </span>
              </td>
              <td class="px-4 py-2 text-right text-slate-700">{{ fmtEur(p[fImporte]) }}</td>
              <td class="px-4 py-2 text-right text-slate-700">{{ p[fReal] != null ? fmtEur(p[fReal]) : '—' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-slate-50 border-t border-slate-200 text-xs font-semibold text-slate-600">
              <td class="px-4 py-2 text-right" colspan="2">Total gastos estimados</td>
              <td class="px-4 py-2 text-right">{{ fmtEur(totalGastos) }}</td>
              <td class="px-4 py-2"></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <p v-else class="text-sm text-slate-400 italic">Sin partidas definidas.</p>
    </template>
  </div>
</template>

<script setup>
/**
 * PresupuestoEditor — editor/visor reutilizable de partidas de presupuesto.
 *
 * Unifica el bloque de partidas duplicado en DetallePlantilla, CampaniaForm y
 * DetalleCampania. Nombres de campo configurables (fieldTipo/fieldImporte/
 * fieldReal) para camelCase (importeEstimado) vs snake_case (importe_estimado).
 * Ver feedback_profesionalidad_extrema.
 */
import { computed } from 'vue'
import { PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue:   { type: Array, default: () => [] },
  editable:     { type: Boolean, default: true },
  fieldTipo:    { type: String, default: 'tipoPartida' },
  fieldImporte: { type: String, default: 'importeEstimado' },
  fieldReal:    { type: String, default: 'importeReal' },
})
const emit = defineEmits(['update:modelValue', 'persist'])

const fTipo = props.fieldTipo
const fImporte = props.fieldImporte
const fReal = props.fieldReal

const totalGastos = computed(() =>
  props.modelValue
    .filter((p) => p[fTipo] === 'gasto')
    .reduce((s, p) => s + (Number(p[fImporte]) || 0), 0)
)
function fmtEur(n) {
  return (Number(n) || 0).toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })
}
function set(p, k, v) { p[k] = v }
function setNum(p, k, v) { p[k] = v === '' ? null : Number(v); emitChange() }
function emitChange() { emit('update:modelValue', props.modelValue) }
function emitBlur() { emit('persist') }
function agregar() {
  props.modelValue.push({ id: null, concepto: '', [fTipo]: 'gasto', [fImporte]: null, orden: props.modelValue.length + 1 })
  emitChange()
}
function eliminar(i) { props.modelValue.splice(i, 1); emitChange(); emit('persist') }
</script>
