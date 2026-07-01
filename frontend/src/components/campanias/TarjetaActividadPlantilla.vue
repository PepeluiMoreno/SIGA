<template>
  <div class="rounded-xl border overflow-hidden transition-colors"
    :class="abierto ? 'border-indigo-200 shadow-sm' : 'border-slate-200 bg-white'">

    <!-- Cabecera (clic para plegar/desplegar) -->
    <div class="flex items-center gap-2 px-3.5 py-2.5 cursor-pointer select-none"
      :class="abierto ? 'bg-indigo-50 border-b border-indigo-100' : 'bg-slate-50/70 hover:bg-slate-100/60'"
      @click="abierto = !abierto">
      <span class="shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center">{{ indice + 1 }}</span>
      <ChevronRightIcon class="w-3 h-3 transition-transform shrink-0" :class="abierto ? 'rotate-90' : ''" />
      <span class="text-sm font-medium flex-1" :class="abierto ? 'text-indigo-900' : 'text-slate-800'">{{ actividad.nombre }}</span>
      <span v-if="actividad.fechaInicio" class="text-xs text-indigo-600 font-medium tabular-nums">
        {{ fmtFechaCorta(actividad.fechaInicio) }}<template v-if="actividad.horaInicio"> · {{ actividad.horaInicio.slice(0,5) }}</template>
      </span>
      <span v-else class="text-xs text-slate-300 italic">sin fecha</span>
      <span v-if="actividad.tareas?.length" class="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-500">
        {{ actividad.tareas.length }}T
      </span>
    </div>

    <!-- Cuerpo editable -->
    <div v-if="abierto" class="px-4 py-3 space-y-3 bg-white">

      <!-- Fechas -->
      <div class="flex flex-wrap items-end gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Inicio</label>
          <div class="flex gap-1">
            <input v-model="actividad.fechaInicio" type="date" :class="inputFecha" />
            <input v-model="actividad.horaInicio" type="time" :class="inputFecha + ' w-24'" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Fin</label>
          <div class="flex gap-1">
            <input v-model="actividad.fechaFin" type="date" :class="inputFecha" />
            <input v-model="actividad.horaFin" type="time" :class="inputFecha + ' w-24'" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Duración est.</label>
          <div class="flex gap-1 items-center">
            <input v-model.number="actividad.duracionDias" type="number" min="0" :class="inputFecha + ' w-14'" />
            <span class="text-xs text-slate-400">d</span>
            <input v-model.number="actividad.duracionHoras" type="number" min="0" step="0.5" :class="inputFecha + ' w-14'" />
            <span class="text-xs text-slate-400">h</span>
          </div>
        </div>
      </div>

      <!-- Responsable + Lugar -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Responsable</label>
          <select v-model="actividad.responsableId" :class="inputCampo">
            <option value="">— Sin asignar —</option>
            <option v-for="m in voluntarios" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Lugar</label>
          <input v-model="actividad.lugar" type="text" :class="inputCampo" placeholder="Nombre del espacio" />
        </div>
      </div>

      <!-- Dirección -->
      <div class="grid grid-cols-12 gap-2">
        <div class="col-span-6">
          <label class="block text-xs font-medium text-slate-500 mb-1">Dirección</label>
          <input v-model="actividad.direccion" type="text" :class="inputCampo" placeholder="Calle, número, piso…" />
        </div>
        <div class="col-span-3">
          <label class="block text-xs font-medium text-slate-500 mb-1">Localidad</label>
          <input v-model="actividad.localidad" type="text" :class="inputCampo" placeholder="Ciudad" />
        </div>
        <div class="col-span-3">
          <label class="block text-xs font-medium text-slate-500 mb-1">Provincia</label>
          <input v-model="actividad.provincia" type="text" :class="inputCampo" placeholder="Prov." />
        </div>
      </div>

      <!-- Tareas -->
      <div v-if="actividad.tareas?.length" class="border-t border-slate-100 pt-2">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Tareas</p>
        <div class="space-y-2">
          <div v-for="(t, ti) in actividad.tareas" :key="ti"
            class="rounded-lg border border-slate-100 bg-slate-50/60 px-3 py-2">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-slate-300 text-xs font-mono shrink-0">{{ ti === actividad.tareas.length - 1 ? '└' : '├' }}</span>
              <span class="flex-1 text-sm font-medium text-slate-700">{{ t.titulo }}</span>
            </div>
            <div class="flex flex-wrap gap-2 pl-4">
              <div>
                <label class="block text-[10px] font-medium text-slate-400 mb-0.5">Horas est.</label>
                <input v-model.number="t.horasEstimadas" type="number" min="0" step="0.5" :class="inputMini + ' w-16'" />
              </div>
              <div>
                <label class="block text-[10px] font-medium text-slate-400 mb-0.5">Habilidad</label>
                <select v-model="t.habilidadId" :class="inputMini">
                  <option value="">— Ninguna —</option>
                  <option v-for="h in habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-[10px] font-medium text-slate-400 mb-0.5">Nivel</label>
                <select v-model="t.nivelHabilidadId" :disabled="!t.habilidadId" :class="inputMini + ' disabled:opacity-40'">
                  <option value="">— Cualquiera —</option>
                  <option v-for="n in nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

/**
 * Tarjeta editable de una actividad de plantilla (al crear campaña desde plantilla).
 * Edita la actividad in situ vía v-model sobre el objeto (mutación directa de props
 * por reactividad de Vue, igual que hacía el form monolítico). No gestiona guardado:
 * el form padre persiste el array completo al crear la campaña.
 */
const props = defineProps({
  actividad:       { type: Object, required: true },
  indice:          { type: Number, default: 0 },
  voluntarios:     { type: Array,  default: () => [] },
  habilidades:     { type: Array,  default: () => [] },
  nivelesHabilidad:{ type: Array,  default: () => [] },
})

const abierto = ref(props.actividad._open ?? false)

const inputFecha = 'px-2 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500'
const inputCampo = 'w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500'
const inputMini  = 'px-2 py-1 text-xs border border-slate-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500'

function fmtFechaCorta(f) {
  if (!f) return ''
  return new Date(f).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}
</script>
