<template>
  <AppLayout
    :title="isEdit ? 'Editar campaña' : 'Nueva campaña'"
    :subtitle="isEdit ? campania.nombre : 'Rellena los datos para registrar la nueva campaña'">

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-3 pb-20">

      <!-- ══ 1 · DATOS GENERALES (fijo) ══════════════════════════════════════════ -->
      <section :class="cardCls">
        <div :class="fixedHeader">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-purple-500"></span>
          <h2 :class="titleCls">Datos generales</h2>
        </div>
        <div class="px-5 py-4 grid grid-cols-12 gap-x-3 gap-y-3">

          <!-- Nombre | Tipo | Estado -->
          <div class="col-span-5">
            <label :class="lbl">Nombre <span class="text-red-400">*</span></label>
            <input v-model="campania.nombre" type="text" required :class="inp"
              placeholder="Nombre de la campaña" maxlength="200" autofocus />
          </div>
          <div class="col-span-5">
            <label :class="lbl">Tipo <span class="text-red-400">*</span></label>
            <select v-model="campania.tipo_campania_id" required :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="t in tiposCampania" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label :class="lbl">Estado <span class="text-red-400">*</span></label>
            <select v-model="campania.estado_campania_id" required :class="inp">
              <option value="">—</option>
              <option v-for="e in estadosCampania" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>

          <!-- Ámbito | Lema | URL -->
          <div class="col-span-4">
            <label :class="lbl">Ámbito de la campaña</label>
            <select v-model="campania.agrupacion_id" :class="inp">
              <option value="">— General (todas las agrupaciones) —</option>
              <template v-for="grupo in agrupacionesPorNivel" :key="grupo.nombre">
                <optgroup :label="grupo.nombre">
                  <option v-for="a in grupo.items" :key="a.id" :value="a.id">{{ a.nombre }}</option>
                </optgroup>
              </template>
            </select>
          </div>
          <div class="col-span-4">
            <label :class="lbl">Lema</label>
            <input v-model="campania.lema" type="text" :class="inp"
              placeholder="Frase breve de la campaña" maxlength="200" />
          </div>
          <div class="col-span-4">
            <label :class="lbl">URL externa</label>
            <div :class="inputGroupCls">
              <span :class="prefixCls">
                <LinkIcon class="w-3.5 h-3.5" />
              </span>
              <input v-model="campania.url_externa" type="url" :class="inputGroupInp"
                placeholder="https://laicismo.org/…" />
            </div>
          </div>

        </div>
      </section>

      <!-- ══ 2 · PLANIFICACIÓN ══════════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="open.plan = !open.plan" :class="accordionBtn(open.plan)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-sky-500"></span>
            <h2 :class="titleCls">Planificación temporal</h2>
          </span>
          <ChevronDownIcon :class="chevronCls(open.plan)" />
        </button>
        <div v-show="open.plan" class="px-5 py-4">
          <div class="flex flex-wrap gap-4 items-end">
            <div class="w-60">
              <label :class="lbl">Modalidad</label>
              <select v-model="campania.modalidad" :class="inp">
                <option v-for="m in MODALIDADES" :key="m.value" :value="m.value">
                  {{ m.label }} — {{ m.desc }}
                </option>
              </select>
            </div>
            <div class="w-36">
              <label :class="lbl">Fecha de inicio</label>
              <input v-model="campania.fecha_inicio" type="date" :class="inp" />
            </div>
            <div class="w-36">
              <label :class="lbl">
                Fecha de fin
                <span v-if="campania.modalidad === 'permanente'" class="text-slate-400 font-normal ml-1">— sin fin</span>
              </label>
              <input v-model="campania.fecha_fin" type="date" :class="inp"
                :disabled="campania.modalidad === 'permanente'" />
            </div>
          </div>
        </div>
      </section>

      <!-- ══ 3 · DESCRIPCIÓN Y OBJETIVOS ═══════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="open.desc = !open.desc" :class="accordionBtn(open.desc)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
            <h2 :class="titleCls">Descripción y objetivos</h2>
          </span>
          <ChevronDownIcon :class="chevronCls(open.desc)" />
        </button>
        <div v-show="open.desc" class="px-5 py-4 space-y-3">
          <div>
            <label :class="lbl">Descripción corta</label>
            <input v-model="campania.descripcion_corta" type="text" :class="inp"
              placeholder="Resumen para listados (máx. 300 car.)" maxlength="300" />
          </div>
          <div class="grid grid-cols-5 gap-4">
            <div class="col-span-3">
              <label :class="lbl">Descripción completa</label>
              <textarea v-model="campania.descripcion_larga" rows="4" :class="inp"
                placeholder="Contexto, motivación y alcance de la campaña…"
                @input="autoResize" />
            </div>
            <div class="col-span-2">
              <label :class="lbl">Objetivo principal</label>
              <textarea v-model="campania.objetivo_principal" rows="4" :class="inp"
                placeholder="¿Qué resultado concreto se persigue?"
                @input="autoResize" />
            </div>
          </div>
        </div>
      </section>

      <!-- ══ 4 · PRESUPUESTO ════════════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="open.presupuesto = !open.presupuesto" :class="accordionBtn(open.presupuesto)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-emerald-500"></span>
            <h2 :class="titleCls">Presupuesto</h2>
            <span v-if="partidas.length"
              class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-full tabular-nums">
              {{ fmtEur(totalPresupuesto) }} €
            </span>
          </span>
          <ChevronDownIcon :class="chevronCls(open.presupuesto)" />
        </button>
        <div v-show="open.presupuesto" class="px-5 pb-4 pt-2">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Concepto</th>
                <th class="pb-2 w-52 text-left text-xs font-semibold text-slate-400">Partida</th>
                <th class="pb-2 w-36 text-right text-xs font-semibold text-slate-400 pr-1">Importe</th>
                <th class="w-7"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!partidas.length">
                <td colspan="4" class="py-5 text-center text-xs text-slate-400 italic">
                  Sin partidas — pulsa «Añadir»
                </td>
              </tr>
              <tr v-for="(p, i) in partidas" :key="p._id" class="group border-b border-slate-50">
                <td class="py-1.5 pr-3">
                  <input v-model="p.concepto" type="text" :class="inpSm"
                    placeholder="Ej. Impresión de carteles" />
                </td>
                <td class="py-1.5 pr-3">
                  <input v-model="p.partida" type="text" :class="inpSm"
                    placeholder="Partida presupuestaria" />
                </td>
                <td class="py-1.5 pr-1">
                  <div :class="inputGroupSmCls">
                    <span :class="prefixSmCls">€</span>
                    <input v-model.number="p.importe" type="number" min="0" step="0.01"
                      :class="inputGroupInpSm + ' text-right tabular-nums'" placeholder="0,00" />
                  </div>
                </td>
                <td class="py-1.5 pl-1">
                  <button type="button" @click="partidas.splice(i, 1)"
                    class="p-1 text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <XMarkIcon class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
              <tr v-if="partidas.length" class="border-t-2 border-slate-200">
                <td colspan="2" class="pt-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Total</td>
                <td class="pt-2 pr-1 text-right font-bold tabular-nums text-sm text-emerald-700">
                  {{ fmtEur(totalPresupuesto) }} €
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
          <button type="button" @click="addPartida"
            class="mt-2.5 inline-flex items-center gap-1.5 text-xs text-emerald-600 hover:text-emerald-800 font-medium transition-colors">
            <PlusIcon class="w-3.5 h-3.5" /> Añadir partida
          </button>
        </div>
      </section>

      <!-- ══ 5 · RECURSOS HUMANOS ═══════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="open.rrhh = !open.rrhh" :class="accordionBtn(open.rrhh)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-amber-500"></span>
            <h2 :class="titleCls">Recursos humanos</h2>
            <span v-if="requerimientos.length"
              class="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold rounded-full tabular-nums">
              {{ totalHoras }} h
            </span>
          </span>
          <ChevronDownIcon :class="chevronCls(open.rrhh)" />
        </button>
        <div v-show="open.rrhh" class="px-5 pb-4 pt-3 space-y-3">

          <!-- Responsable combobox -->
          <div class="flex flex-wrap gap-3 items-end">
            <div class="w-72">
              <label :class="lbl">
                Responsable
                <span v-if="campania.agrupacion_id" class="text-slate-400 font-normal ml-1 text-xs">
                  — miembros de {{ agrupacionSeleccionada?.nombre }}
                </span>
              </label>
              <div class="relative">
                <input
                  v-model="responsableSearch"
                  type="text"
                  :class="inp"
                  placeholder="Buscar por nombre…"
                  autocomplete="off"
                  @focus="showResponsableList = true"
                  @blur="onResponsableBlur"
                />
                <div v-if="showResponsableList && filteredResponsables.length"
                  class="absolute z-30 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-52 overflow-y-auto">
                  <button type="button"
                    v-for="m in filteredResponsables" :key="m.id"
                    @mousedown="selectResponsable(m)"
                    class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                    {{ m.nombre }} {{ m.apellido1 }}
                  </button>
                </div>
                <div v-if="campania.responsable_id && !showResponsableList"
                  class="absolute right-2 top-1/2 -translate-y-1/2">
                  <button type="button" @click="clearResponsable"
                    class="p-0.5 rounded text-slate-400 hover:text-gray-600 transition-colors">
                    <XMarkIcon class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Tabla de requerimientos -->
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Tarea</th>
                <th class="pb-2 w-52 text-left text-xs font-semibold text-slate-400">Habilidad requerida</th>
                <th class="pb-2 w-32 text-left text-xs font-semibold text-slate-400">Nivel</th>
                <th class="pb-2 w-24 text-right text-xs font-semibold text-slate-400 pr-1">Horas</th>
                <th class="w-7"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!requerimientos.length">
                <td colspan="5" class="py-5 text-center text-xs text-slate-400 italic">
                  Sin tareas definidas — pulsa «Añadir»
                </td>
              </tr>
              <tr v-for="(r, i) in requerimientos" :key="r._id" class="group border-b border-slate-50">
                <td class="py-1.5 pr-3">
                  <input v-model="r.tarea" type="text" :class="inpSm"
                    placeholder="Descripción de la tarea" />
                </td>
                <td class="py-1.5 pr-3">
                  <select v-model="r.habilidadId" :class="inpSm">
                    <option value="">— Cualquiera —</option>
                    <optgroup v-for="cat in habilidadesPorCategoria" :key="cat.categoria" :label="cat.categoria">
                      <option v-for="h in cat.habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                    </optgroup>
                  </select>
                </td>
                <td class="py-1.5 pr-3">
                  <select v-model="r.nivel" :class="inpSm">
                    <option v-for="n in NIVELES" :key="n.value" :value="n.value">{{ n.label }}</option>
                  </select>
                </td>
                <td class="py-1.5 pr-1">
                  <div :class="inputGroupSmCls">
                    <input v-model.number="r.horas" type="number" min="0" step="0.5"
                      :class="inputGroupInpSm + ' text-right tabular-nums'" placeholder="0" />
                    <span :class="suffixSmCls">h</span>
                  </div>
                </td>
                <td class="py-1.5 pl-1">
                  <button type="button" @click="requerimientos.splice(i, 1)"
                    class="p-1 text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <XMarkIcon class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
              <tr v-if="requerimientos.length" class="border-t-2 border-slate-200">
                <td colspan="3" class="pt-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Total horas</td>
                <td class="pt-2 pr-1 text-right font-bold tabular-nums text-sm text-amber-700">
                  {{ totalHoras }} h
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
          <button type="button" @click="addRequerimiento"
            class="mt-1 inline-flex items-center gap-1.5 text-xs text-amber-600 hover:text-amber-800 font-medium transition-colors">
            <PlusIcon class="w-3.5 h-3.5" /> Añadir tarea
          </button>
        </div>
      </section>

    </form>

    <!-- ══ Barra de acciones fija ═════════════════════════════════════════════ -->
    <div class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-sm border-t border-slate-200 shadow-[0_-4px_16px_-4px_rgba(0,0,0,0.08)]">
      <div class="max-w-screen-xl mx-auto px-6 py-3 flex items-center justify-between">
        <div>
          <p v-if="error" class="flex items-center gap-1.5 text-xs text-red-600">
            <ExclamationCircleIcon class="w-4 h-4 shrink-0" />
            {{ error }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/campanias"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
            <ChevronLeftIcon class="w-4 h-4" />
            Cancelar
          </router-link>
          <button type="submit" form="campania-form" :disabled="submitting"
            @click="handleSubmit"
            class="inline-flex items-center gap-2 px-6 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-sm transition-colors">
            <span v-if="submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
            <CheckIcon v-else class="w-4 h-4" />
            {{ isEdit ? 'Actualizar campaña' : 'Crear campaña' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronDownIcon, ChevronLeftIcon, CheckIcon,
  ExclamationCircleIcon, PlusIcon, XMarkIcon, LinkIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'
import {
  GET_CAMPANIA, GET_TIPOS_CAMPANIA, GET_ESTADOS_CAMPANIA,
  CREAR_CAMPANIA, ACTUALIZAR_CAMPANIA, GET_HABILIDADES,
} from '@/modules/comunicaciones/graphql/queries.js'
import { GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'

const GET_MIEMBROS_SIMPLE = `
  query MiembrosSimple {
    miembros { id nombre apellido1 agrupacion { id } usuario { id activo } }
  }
`

// ── Constantes ───────────────────────────────────────────────────────────────
const MODALIDADES = [
  { value: 'permanente',  label: 'Permanente',  desc: 'Sin fecha de fin' },
  { value: 'recurrente',  label: 'Recurrente',  desc: 'Periódica' },
  { value: 'determinada', label: 'Determinada', desc: 'Fechas concretas' },
  { value: 'puntual',     label: 'Puntual',     desc: 'Acción única' },
]
const NIVELES = [
  { value: 'basico',     label: 'Básico' },
  { value: 'intermedio', label: 'Intermedio' },
  { value: 'avanzado',   label: 'Avanzado' },
  { value: 'experto',    label: 'Experto' },
]

// ── Estilos (palette: slate + indigo) ────────────────────────────────────────
const cardCls      = 'rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden'
const fixedHeader  = 'flex items-center gap-3 px-5 py-3.5 border-b border-slate-200'
const titleCls     = 'text-sm font-semibold text-slate-800'
const lbl          = 'block text-sm font-medium text-slate-700 mb-1.5'
const inp          = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
                     'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
                     'bg-white placeholder:text-slate-300 disabled:bg-slate-50 disabled:text-slate-400'
const inpSm        = 'w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-lg transition-all ' +
                     'focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 ' +
                     'bg-white placeholder:text-slate-300'

// Input group (prefijo/sufijo)
const inputGroupCls   = 'flex h-10 rounded-lg border border-slate-300 overflow-hidden transition-all focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500'
const prefixCls       = 'px-2.5 flex items-center bg-slate-50 border-r border-slate-200 text-slate-400 text-sm shrink-0'
const inputGroupInp   = 'flex-1 px-3 text-sm bg-white focus:outline-none placeholder:text-slate-300'
const inputGroupSmCls = 'flex rounded-lg border border-slate-300 overflow-hidden transition-all focus-within:ring-1 focus-within:ring-indigo-500 focus-within:border-indigo-500'
const prefixSmCls     = 'px-2 flex items-center bg-slate-50 border-r border-slate-200 text-slate-400 text-sm shrink-0'
const suffixSmCls     = 'px-2 flex items-center bg-slate-50 border-l border-slate-200 text-slate-400 text-sm shrink-0'
const inputGroupInpSm = 'flex-1 px-2 py-1.5 text-sm bg-white focus:outline-none placeholder:text-slate-300'

const accordionBtn = (isOpen) =>
  'w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/60 transition-colors ' +
  (isOpen ? 'border-b border-slate-200' : '')
const chevronCls = (isOpen) =>
  'w-4 h-4 text-slate-400 transition-transform duration-200 ' + (isOpen ? 'rotate-180' : '')

// ── Estado de acordeones ─────────────────────────────────────────────────────
const open = reactive({ plan: true, desc: true, presupuesto: false, rrhh: false })

// ── Router ───────────────────────────────────────────────────────────────────
const route      = useRoute()
const router     = useRouter()
const isEdit     = computed(() => !!route.params.id && !route.path.includes('/nueva'))
const loading    = ref(false)
const submitting = ref(false)
const error      = ref(null)

// ── Modelo ───────────────────────────────────────────────────────────────────
const campania = ref({
  nombre: '', lema: '', descripcion_corta: '', descripcion_larga: '',
  url_externa: '', tipo_campania_id: '', estado_campania_id: '',
  modalidad: 'determinada', fecha_inicio: '', fecha_fin: '',
  objetivo_principal: '', responsable_id: '', agrupacion_id: '',
})

// ── Presupuesto ──────────────────────────────────────────────────────────────
const partidas = ref([])
let _pid = 0
const addPartida = () => partidas.value.push({ _id: ++_pid, concepto: '', partida: '', importe: null })
const totalPresupuesto = computed(() => partidas.value.reduce((s, p) => s + (p.importe || 0), 0))
const fmtEur = (n) => Number(n || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

// ── RRHH ─────────────────────────────────────────────────────────────────────
const requerimientos = ref([])
let _rid = 0
const addRequerimiento = () =>
  requerimientos.value.push({ _id: ++_rid, tarea: '', habilidadId: '', nivel: 'intermedio', horas: null })
const totalHoras = computed(() => requerimientos.value.reduce((s, r) => s + (r.horas || 0), 0))

// ── Combobox responsable ─────────────────────────────────────────────────────
const responsableSearch   = ref('')
const showResponsableList = ref(false)

const filteredResponsables = computed(() => {
  const q = responsableSearch.value.trim().toLowerCase()
  if (q.length < 2) return []
  return responsablesCandidatos.value
    .filter(m => `${m.nombre} ${m.apellido1}`.toLowerCase().includes(q))
    .slice(0, 12)
})

function selectResponsable(m) {
  campania.value.responsable_id = m.id
  responsableSearch.value = `${m.nombre} ${m.apellido1}`
  showResponsableList.value = false
}
function clearResponsable() {
  campania.value.responsable_id = ''
  responsableSearch.value = ''
}
function onResponsableBlur() {
  setTimeout(() => { showResponsableList.value = false }, 150)
}

// ── Auto-resize textarea ─────────────────────────────────────────────────────
function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// ── Catálogos ────────────────────────────────────────────────────────────────
const tiposCampania   = ref([])
const estadosCampania = ref([])
const miembros        = ref([])
const agrupaciones    = ref([])
const habilidades     = ref([])

const habilidadesPorCategoria = computed(() => {
  const map = {}
  habilidades.value.forEach(h => {
    if (!map[h.categoria]) map[h.categoria] = []
    map[h.categoria].push(h)
  })
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b, 'es'))
    .map(([categoria, habs]) => ({ categoria, habilidades: habs }))
})

const agrupacionesPorNivel = computed(() => {
  const map = {}
  agrupaciones.value.forEach(a => {
    const nombre = a.tipoUnidad?.nombre || 'Sin clasificar'
    const nivel  = a.tipoUnidad?.nivel  ?? 99
    const key    = `${String(nivel).padStart(3, '0')}__${nombre}`
    if (!map[key]) map[key] = { nivel, nombre, items: [] }
    map[key].items.push(a)
  })
  return Object.values(map)
    .sort((a, b) => a.nivel - b.nivel)
    .map(g => ({ ...g, items: g.items.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')) }))
})

const agrupacionSeleccionada = computed(() =>
  agrupaciones.value.find(a => a.id === campania.value.agrupacion_id) ?? null
)

const responsablesCandidatos = computed(() => {
  const activos = miembros.value.filter(m => m.usuario?.activo)
  if (!campania.value.agrupacion_id) return activos
  return activos.filter(m => m.agrupacion_id === campania.value.agrupacion_id)
})

// ── Carga ────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadCatalogos()
  if (isEdit.value) await loadCampania()
})

async function loadCatalogos() {
  const [rTipos, rEstados, rMbs, rAgrs, rHabs] = await Promise.allSettled([
    executeQuery(GET_TIPOS_CAMPANIA),
    executeQuery(GET_ESTADOS_CAMPANIA),
    executeQuery(GET_MIEMBROS_SIMPLE),
    executeQuery(GET_AGRUPACIONES),
    executeQuery(GET_HABILIDADES),
  ])

  if (rTipos.status === 'fulfilled')
    tiposCampania.value = (rTipos.value.tiposCampania || []).filter(t => t.activo)
  else console.error('tipos:', rTipos.reason)

  if (rEstados.status === 'fulfilled') {
    estadosCampania.value = (rEstados.value.estadosCampania || []).filter(e => e.activo)
      .sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
    if (!isEdit.value && !campania.value.estado_campania_id) {
      const inicial = estadosCampania.value.find(e => e.nombre === 'Borrador') ?? estadosCampania.value[0]
      if (inicial) campania.value.estado_campania_id = inicial.id
    }
  } else console.error('estados:', rEstados.reason)

  if (rMbs.status === 'fulfilled')
    miembros.value = (rMbs.value.miembros || []).map(m => ({
      id: m.id, nombre: m.nombre, apellido1: m.apellido1,
      agrupacion_id: m.agrupacion?.id || null,
      usuario: m.usuario || null,
    }))
  else console.error('miembros:', rMbs.reason)

  if (rAgrs.status === 'fulfilled')
    agrupaciones.value = rAgrs.value.agrupacionesTerritoriales || []
  else console.error('agrupaciones:', rAgrs.reason)

  if (rHabs.status === 'fulfilled')
    habilidades.value = (rHabs.value.habilidades || []).filter(h => h.activo)
  else console.error('habilidades:', rHabs.reason)
}

async function loadCampania() {
  loading.value = true
  try {
    const data = await executeQuery(GET_CAMPANIA, { id: route.params.id })
    const c = data.campanias?.[0]
    if (c) {
      campania.value = {
        nombre:             c.nombre || '',
        lema:               c.lema || '',
        descripcion_corta:  c.descripcionCorta || '',
        descripcion_larga:  c.descripcionLarga || '',
        url_externa:        c.urlExterna || '',
        tipo_campania_id:   c.tipoCampania?.id || '',
        estado_campania_id: c.estado?.id || '',
        modalidad:          c.plan?.modalidad || 'determinada',
        fecha_inicio:       c.fechaInicioPlan || '',
        fecha_fin:          c.fechaFinPlan || '',
        objetivo_principal: c.objetivoPrincipal || '',
        responsable_id:     c.responsable?.id || '',
        agrupacion_id:      c.agrupacion?.id || '',
      }
      if (c.responsable) {
        responsableSearch.value = `${c.responsable.nombre} ${c.responsable.apellido1}`
      }
    }
  } catch {
    error.value = 'Error al cargar la campaña'
  } finally {
    loading.value = false
  }
}

// ── Submit ───────────────────────────────────────────────────────────────────
async function handleSubmit() {
  error.value = null
  if (!campania.value.nombre?.trim()) { error.value = 'El nombre de la campaña es obligatorio.'; return }
  if (!campania.value.tipo_campania_id) { error.value = 'Selecciona un tipo de campaña.'; return }
  if (!campania.value.estado_campania_id) { error.value = 'Selecciona un estado.'; return }

  submitting.value = true
  try {
    const base = {
      nombre:              campania.value.nombre.trim(),
      tipoCampaniaId:      campania.value.tipo_campania_id,
      estadoId:            campania.value.estado_campania_id,
      lema:                campania.value.lema || null,
      descripcionCorta:    campania.value.descripcion_corta || null,
      descripcionLarga:    campania.value.descripcion_larga || null,
      urlExterna:          campania.value.url_externa || null,
      objetivoPrincipal:   campania.value.objetivo_principal || null,
      modalidad:           campania.value.modalidad || null,
      fechaInicio:         campania.value.fecha_inicio || null,
      fechaFin:            campania.value.modalidad === 'permanente' ? null : (campania.value.fecha_fin || null),
      responsableId:       campania.value.responsable_id || null,
      agrupacionId:        campania.value.agrupacion_id || null,
      presupuestoAsignado: totalPresupuesto.value || 0,
    }
    if (isEdit.value) {
      const res = await executeMutation(ACTUALIZAR_CAMPANIA, { data: { campaniaId: route.params.id, ...base } })
      router.push(`/campanias/${res.actualizarCampaniaConPlan.id}`)
    } else {
      const res = await executeMutation(CREAR_CAMPANIA, { data: base })
      router.push(`/campanias/${res.crearCampaniaConPlan.id}`)
    }
  } catch (e) {
    console.error('Error guardando campaña:', e)
    error.value = e?.response?.errors?.[0]?.message || 'Error al guardar. Por favor, inténtalo de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>
