<template>
  <div class="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">

    <!-- ── Cabecera ───────────────────────────────────────────────── -->
    <div
      class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-slate-50 transition-colors"
      @click="open = !open"
    >
      <button class="text-slate-400 hover:text-slate-600 shrink-0" tabindex="-1">
        <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-90': open }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </button>

      <span class="font-semibold text-slate-800 flex-1 truncate">{{ actividad.nombre }}</span>

      <span v-if="actividad.tipoActividad" class="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-50 text-indigo-700">
        {{ actividad.tipoActividad.nombre }}
      </span>

      <span
        v-if="actividad.estado"
        class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
        :style="{ background: actividad.estado.color + '20', color: actividad.estado.color }"
      >
        {{ actividad.estado.nombre }}
      </span>

      <span v-if="actividad.fechaInicio" class="hidden md:block text-xs text-slate-400">
        {{ fmtDate(actividad.fechaInicio) }}
        <template v-if="actividad.fechaFin"> – {{ fmtDate(actividad.fechaFin) }}</template>
      </span>

      <span v-if="totalPresupuesto > 0" class="hidden lg:block text-xs font-semibold text-slate-600">
        {{ formatEuros(totalPresupuesto) }}
      </span>

      <span v-if="actividad.responsable" class="hidden lg:block text-xs text-slate-500 truncate max-w-[120px]">
        {{ actividad.responsable.nombre }} {{ actividad.responsable.apellido1 }}
      </span>

      <div v-if="!readonly" class="flex gap-1 shrink-0 ml-1">
        <button
          class="p-1 text-slate-400 hover:text-red-500 rounded transition-colors"
          title="Eliminar actividad"
          @click.stop="$emit('delete', actividad.id)"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ── Cuerpo expandible ──────────────────────────────────────── -->
    <Transition name="slide">
      <div v-if="open" class="border-t border-slate-100 divide-y divide-slate-100">

        <!-- Detalles básicos -->
        <div class="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div>
            <p class="text-xs text-slate-400 mb-0.5">Descripción</p>
            <template v-if="!readonly">
              <textarea v-model="local.descripcion" rows="2" class="w-full h-10 px-2.5 py-1.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300" @change="emitChange" />
            </template>
            <p v-else class="text-sm text-slate-700 bg-slate-50 rounded-lg px-2.5 py-1.5 min-h-[2.5rem]">{{ actividad.descripcion || '—' }}</p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <p class="text-xs text-slate-400 mb-0.5">Fecha inicio</p>
              <input v-if="!readonly" v-model="local.fechaInicio" type="date" class="w-full h-10 px-2.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300" @change="emitChange" />
              <p v-else class="text-sm text-slate-700 bg-slate-50 rounded-lg px-2.5 py-1.5 h-10 flex items-center">{{ fmtDate(actividad.fechaInicio) || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-400 mb-0.5">Fecha fin</p>
              <input v-if="!readonly" v-model="local.fechaFin" type="date" class="w-full h-10 px-2.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300" @change="emitChange" />
              <p v-else class="text-sm text-slate-700 bg-slate-50 rounded-lg px-2.5 py-1.5 h-10 flex items-center">{{ fmtDate(actividad.fechaFin) || '—' }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <p class="text-xs text-slate-400 mb-0.5">Lugar</p>
              <input v-if="!readonly" v-model="local.lugar" type="text" class="w-full h-10 px-2.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300" @change="emitChange" />
              <p v-else class="text-sm text-slate-700 bg-slate-50 rounded-lg px-2.5 py-1.5 h-10 flex items-center">{{ actividad.lugar || '—' }}</p>
            </div>
            <div class="flex items-center gap-2 pt-5">
              <input v-if="!readonly" id="online" v-model="local.esOnline" type="checkbox" class="rounded border-slate-300 text-indigo-600" @change="emitChange" />
              <span v-else class="text-xs font-medium px-2 py-0.5 rounded-full" :class="actividad.esOnline ? 'bg-sky-100 text-sky-700' : 'bg-slate-100 text-slate-500'">
                {{ actividad.esOnline ? 'Online' : 'Presencial' }}
              </span>
              <label v-if="!readonly" for="online" class="text-xs text-slate-500">Online</label>
            </div>
          </div>
        </div>

        <!-- Presupuesto de la actividad -->
        <div class="px-4 py-3">
          <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Presupuesto</h4>

          <table v-if="(local.partidas?.length || !readonly)" class="w-full text-sm mb-2">
            <thead>
              <tr class="text-xs text-slate-400 uppercase">
                <th class="text-left font-medium pb-1">Concepto</th>
                <th class="text-left font-medium pb-1 w-24">Tipo</th>
                <th class="text-right font-medium pb-1 w-24">Estimado</th>
                <th class="text-right font-medium pb-1 w-24">Real</th>
                <th v-if="!readonly" class="w-8" />
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in local.partidas" :key="i" class="border-t border-slate-100">
                <td class="py-1 pr-2">
                  <input v-if="!readonly" v-model="p.concepto" type="text" class="w-full h-8 px-2 text-sm border border-slate-200 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-300" />
                  <span v-else>{{ p.concepto }}</span>
                </td>
                <td class="py-1 pr-2">
                  <select v-if="!readonly" v-model="p.tipoPartida" class="w-full h-8 px-1 text-sm border border-slate-200 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-300">
                    <option value="gasto">Gasto</option>
                    <option value="ingreso">Ingreso</option>
                  </select>
                  <span v-else class="inline-flex items-center px-1.5 py-0.5 rounded text-xs" :class="p.tipoPartida === 'gasto' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
                    {{ p.tipoPartida === 'gasto' ? 'Gasto' : 'Ingreso' }}
                  </span>
                </td>
                <td class="py-1 pr-2 text-right">
                  <input v-if="!readonly" v-model="p.importeEstimado" type="number" min="0" step="0.01" class="w-full h-8 px-2 text-sm text-right border border-slate-200 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-300" />
                  <span v-else>{{ formatEuros(p.importeEstimado) }}</span>
                </td>
                <td class="py-1 pr-2 text-right">
                  <input v-if="!readonly" v-model="p.importeReal" type="number" min="0" step="0.01" class="w-full h-8 px-2 text-sm text-right border border-slate-200 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-300" />
                  <span v-else>{{ p.importeReal != null ? formatEuros(p.importeReal) : '—' }}</span>
                </td>
                <td v-if="!readonly" class="py-1">
                  <button class="p-1 text-slate-300 hover:text-red-500" @click="local.partidas.splice(i, 1)">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </td>
              </tr>
              <tr v-if="!local.partidas?.length && readonly">
                <td colspan="4" class="py-2 text-slate-400 text-sm italic">Sin partidas</td>
              </tr>
            </tbody>
          </table>

          <div class="flex items-center justify-between">
            <button
              v-if="!readonly"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
              @click="local.partidas.push({ concepto: '', tipoPartida: 'gasto', importeEstimado: 0, importeReal: null, orden: local.partidas.length })"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
              Añadir partida
            </button>
            <p class="text-xs text-slate-400 ml-auto">
              Total gastos: <strong class="text-slate-700">{{ formatEuros(totalGastos) }}</strong>
            </p>
          </div>
        </div>

        <!-- Recursos humanos / Participaciones -->
        <div class="px-4 py-3">
          <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Recursos humanos</h4>

          <div v-if="actividad.participaciones?.length || !readonly" class="space-y-1 mb-2">
            <div
              v-for="p in actividad.participaciones"
              :key="p.id"
              class="flex items-center gap-2 text-sm py-1 border-b border-slate-100 last:border-0"
            >
              <img v-if="p.miembro?.fotoUrl" :src="p.miembro.fotoUrl" class="w-6 h-6 rounded-full object-cover shrink-0" />
              <span v-else class="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs flex items-center justify-center font-semibold shrink-0">
                {{ (p.miembro?.nombre ?? p.nombreExterno ?? '?')[0] }}
              </span>
              <span class="flex-1 text-slate-700">
                {{ p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : p.nombreExterno }}
              </span>
              <span class="text-xs text-slate-400 px-1.5 py-0.5 bg-slate-50 rounded">{{ p.rol }}</span>
              <span class="text-xs text-slate-400">{{ p.horasAportadas ?? '0' }}h</span>
              <span class="text-xs" :class="p.asistio === true ? 'text-green-600' : p.asistio === false ? 'text-red-500' : 'text-slate-300'">
                {{ p.asistio === true ? '✓' : p.asistio === false ? '✗' : '·' }}
              </span>
            </div>
            <p v-if="!actividad.participaciones?.length" class="text-sm text-slate-400 italic">Sin participantes</p>
          </div>

          <button
            v-if="!readonly"
            class="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            @click="$emit('add-participacion', actividad.id)"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
            Añadir participante
          </button>
        </div>

        <!-- Tareas -->
        <div class="px-4 py-3">
          <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Tareas</h4>

          <div class="space-y-1 mb-2">
            <div
              v-for="t in actividad.tareas"
              :key="t.id"
              class="flex items-center gap-2 text-sm py-1.5 border-b border-slate-100 last:border-0"
            >
              <span
                class="shrink-0 w-2 h-2 rounded-full"
                :style="{ background: t.estado?.color ?? '#94a3b8' }"
              />
              <span class="flex-1 text-slate-700 truncate">{{ t.titulo }}</span>
              <span v-if="t.responsable" class="text-xs text-slate-400 truncate max-w-[100px]">{{ t.responsable.nombre }}</span>
              <span v-if="t.horasEstimadas" class="text-xs text-slate-400 shrink-0">{{ t.horasEstimadas }}h</span>
              <button
                v-if="!readonly"
                class="p-1 text-slate-300 hover:text-red-500 shrink-0"
                @click="$emit('delete-tarea', t.id)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <p v-if="!actividad.tareas?.length" class="text-sm text-slate-400 italic">Sin tareas</p>
          </div>

          <button
            v-if="!readonly"
            class="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            @click="$emit('add-tarea', actividad.id)"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
            Añadir tarea
          </button>
        </div>

        <!-- Partes de trabajo -->
        <div class="px-4 py-3">
          <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Partes de trabajo</h4>

          <div class="space-y-1 mb-2">
            <div
              v-for="r in actividad.registrosTrabajo"
              :key="r.id"
              class="flex items-center gap-2 text-sm py-1 border-b border-slate-100 last:border-0"
            >
              <span class="text-xs text-slate-400 shrink-0 w-20">{{ fmtDate(r.fecha) }}</span>
              <span class="flex-1 text-slate-700 truncate">
                {{ r.miembro ? `${r.miembro.nombre} ${r.miembro.apellido1}` : '—' }}
              </span>
              <span class="text-xs text-slate-400 shrink-0">{{ r.horas }}h</span>
              <span class="text-xs px-1.5 py-0.5 rounded bg-slate-50 text-slate-500 shrink-0">{{ r.tipo }}</span>
              <span class="text-xs text-slate-400 truncate max-w-[120px]">{{ r.descripcion }}</span>
              <button
                v-if="!readonly"
                class="p-1 text-slate-300 hover:text-red-500 shrink-0"
                @click="$emit('delete-registro', r.id)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <p v-if="!actividad.registrosTrabajo?.length" class="text-sm text-slate-400 italic">Sin partes registrados</p>
          </div>

          <div class="flex items-center justify-between">
            <button
              v-if="!readonly"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
              @click="$emit('add-registro', actividad.id)"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
              Registrar parte
            </button>
            <p v-if="totalHoras > 0" class="text-xs text-slate-400 ml-auto">
              Total: <strong class="text-slate-700">{{ totalHoras }} h</strong>
            </p>
          </div>
        </div>

        <!-- Documentación -->
        <div class="px-4 py-3">
          <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Documentación</h4>

          <div v-if="actividad.documentos?.length" class="space-y-1 mb-2">
            <div
              v-for="d in actividad.documentos"
              :key="d.id"
              class="flex items-center gap-2 text-sm py-1 border-b border-slate-100 last:border-0"
            >
              <span class="text-lg shrink-0">{{ iconoDoc(d.tipoDoc) }}</span>
              <span class="flex-1 text-slate-700 truncate">{{ d.nombre }}</span>
              <span class="text-xs px-1.5 py-0.5 bg-slate-50 text-slate-500 rounded shrink-0">{{ d.tipoDoc }}</span>
              <span class="text-xs text-slate-400 shrink-0">{{ fmtSize(d.tamanyo) }}</span>
              <a
                :href="`/api/uploads/${d.ruta}`"
                target="_blank"
                class="p-1 text-slate-400 hover:text-indigo-600"
                title="Descargar"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              </a>
              <button
                v-if="!readonly"
                class="p-1 text-slate-300 hover:text-red-500 shrink-0"
                @click="$emit('delete-documento', d.id)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <p v-else class="text-sm text-slate-400 italic mb-2">Sin documentos</p>

          <label
            v-if="!readonly"
            class="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 cursor-pointer"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
            Subir documento
            <input type="file" class="hidden" @change="e => $emit('upload-documento', { actividadId: actividad.id, file: e.target.files[0] })" />
          </label>
        </div>

      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  actividad: { type: Object, required: true },
  readonly: { type: Boolean, default: false },
  defaultOpen: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update', 'delete',
  'add-participacion', 'add-tarea', 'add-registro',
  'delete-tarea', 'delete-registro', 'delete-documento',
  'upload-documento',
])

const open = ref(props.defaultOpen)

const local = ref({
  descripcion: props.actividad.descripcion ?? '',
  fechaInicio: props.actividad.fechaInicio ?? null,
  fechaFin: props.actividad.fechaFin ?? null,
  lugar: props.actividad.lugar ?? '',
  esOnline: props.actividad.esOnline ?? false,
  partidas: (props.actividad.partidas ?? []).map(p => ({ ...p })),
})

watch(() => props.actividad, (a) => {
  local.value = {
    descripcion: a.descripcion ?? '',
    fechaInicio: a.fechaInicio ?? null,
    fechaFin: a.fechaFin ?? null,
    lugar: a.lugar ?? '',
    esOnline: a.esOnline ?? false,
    partidas: (a.partidas ?? []).map(p => ({ ...p })),
  }
}, { deep: true })

function emitChange() {
  emit('update', { id: props.actividad.id, ...local.value })
}

const totalPresupuesto = computed(() =>
  (local.value.partidas ?? [])
    .filter(p => p.tipoPartida === 'gasto')
    .reduce((s, p) => s + (parseFloat(p.importeEstimado) || 0), 0)
)

const totalGastos = totalPresupuesto

const totalHoras = computed(() =>
  (props.actividad.registrosTrabajo ?? [])
    .reduce((s, r) => s + (parseFloat(r.horas) || 0), 0)
)

function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatEuros(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(parseFloat(n) || 0)
}

function fmtSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function iconoDoc(tipo) {
  const map = { acta: '📋', informe: '📄', foto: '🖼️', material: '📦', factura: '🧾', ticket: '🧾', presupuesto: '💰' }
  return map[tipo] ?? '📎'
}
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: max-height 0.2s ease, opacity 0.2s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-enter-to, .slide-leave-from {
  max-height: 2000px;
  opacity: 1;
}
</style>
