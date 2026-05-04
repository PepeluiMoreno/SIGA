<template>
  <AppLayout :title="isEdit ? 'Editar Campaña' : 'Nueva Campaña'"
             :subtitle="isEdit ? campania.nombre : 'Completa las secciones para crear la campaña'">

    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-3 max-w-5xl">

      <!-- ── Identidad ─────────────────────────────────────────────────── -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <button type="button" @click="toggle('identidad')" :class="sectionBtn">
          <span class="flex items-center gap-2"><span>🚩</span><span>Identidad</span></span>
          <ChevronDownIcon :class="['w-4 h-4 text-gray-400 transition-transform', open.identidad ? 'rotate-180' : '']" />
        </button>
        <div v-show="open.identidad" class="px-4 pb-4 pt-3 border-t border-gray-100 grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label :class="lbl">Nombre *</label>
            <input v-model="campania.nombre" type="text" required :class="inp" placeholder="Nombre de la campaña" />
          </div>
          <div>
            <label :class="lbl">Lema</label>
            <input v-model="campania.lema" type="text" :class="inp" placeholder="Eslogan breve" />
          </div>
          <div>
            <label :class="lbl">URL externa</label>
            <input v-model="campania.url_externa" type="url" :class="inp" placeholder="https://…" />
          </div>
          <div>
            <label :class="lbl">Tipo *</label>
            <select v-model="campania.tipo_campania_id" required :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="t in tiposCampania" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label :class="lbl">Estado *</label>
            <select v-model="campania.estado_campania_id" required :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="e in estadosCampania" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
          <div>
            <label :class="lbl">Agrupación</label>
            <select v-model="campania.agrupacion_id" :class="inp">
              <option value="">— Todas —</option>
              <option v-for="a in agrupaciones" :key="a.id" :value="a.id">{{ a.nombre }}</option>
            </select>
          </div>
          <div>
            <label :class="lbl">Responsable</label>
            <select v-model="campania.responsable_id" :class="inp">
              <option value="">— Sin asignar —</option>
              <option v-for="m in miembros" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label :class="lbl">Descripción corta</label>
            <input v-model="campania.descripcion_corta" type="text" :class="inp" placeholder="Resumen en una frase" />
          </div>
        </div>
      </div>

      <!-- ── Planificación ─────────────────────────────────────────────── -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <button type="button" @click="toggle('planificacion')" :class="sectionBtn">
          <span class="flex items-center gap-2"><span>📅</span><span>Planificación</span></span>
          <ChevronDownIcon :class="['w-4 h-4 text-gray-400 transition-transform', open.planificacion ? 'rotate-180' : '']" />
        </button>
        <div v-show="open.planificacion" class="px-4 pb-4 pt-3 border-t border-gray-100 grid grid-cols-2 gap-3">
          <div>
            <label :class="lbl">Inicio planificado</label>
            <input v-model="campania.fecha_inicio_plan" type="date" :class="inp" />
          </div>
          <div>
            <label :class="lbl">Fin planificado</label>
            <input v-model="campania.fecha_fin_plan" type="date" :class="inp" />
          </div>
          <div class="col-span-2">
            <label :class="lbl">Objetivo principal</label>
            <textarea v-model="campania.objetivo_principal" rows="3" :class="inp" placeholder="Describe el objetivo principal de la campaña…" />
          </div>
        </div>
      </div>

      <!-- ── Dotación Económica ─────────────────────────────────────────── -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <button type="button" @click="toggle('presupuesto')" :class="sectionBtn">
          <span class="flex items-center gap-2"><span>💶</span><span>Dotación Económica</span></span>
          <ChevronDownIcon :class="['w-4 h-4 text-gray-400 transition-transform', open.presupuesto ? 'rotate-180' : '']" />
        </button>
        <div v-show="open.presupuesto" class="px-4 pb-4 pt-3 border-t border-gray-100">
          <table class="w-full text-xs">
            <thead>
              <tr class="text-left text-gray-500 border-b border-gray-200">
                <th class="pb-1.5 font-medium pl-1">Concepto de gasto</th>
                <th class="pb-1.5 font-medium w-16 text-right">Cant.</th>
                <th class="pb-1.5 font-medium w-32 text-right">Importe unit. (€)</th>
                <th class="pb-1.5 font-medium w-24 text-right pr-2">Total (€)</th>
                <th class="w-6"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in partidas" :key="p._id" class="border-b border-gray-100">
                <td class="py-1 pl-1 pr-2">
                  <input v-model="p.concepto" type="text" :class="inp" placeholder="Ej: Impresión carteles" />
                </td>
                <td class="py-1 pr-2">
                  <input v-model.number="p.cantidad" type="number" min="1" :class="inp + ' text-right'" />
                </td>
                <td class="py-1 pr-2">
                  <input v-model.number="p.importeUnitario" type="number" min="0" step="0.01" :class="inp + ' text-right'" placeholder="0.00" />
                </td>
                <td class="py-1 pr-2 text-right font-semibold text-gray-700">
                  {{ fmt((p.cantidad || 0) * (p.importeUnitario || 0)) }}
                </td>
                <td class="py-1 text-center">
                  <button type="button" @click="partidas.splice(i, 1)" class="text-gray-300 hover:text-red-500 text-base leading-none">✕</button>
                </td>
              </tr>
              <tr v-if="!partidas.length">
                <td colspan="5" class="py-3 text-center text-gray-400 italic">Sin partidas de gasto</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="border-t-2 border-gray-300">
                <td colspan="3" class="pt-2 pl-1 text-xs font-semibold text-gray-700">Total dotación económica</td>
                <td class="pt-2 pr-2 text-right font-bold text-purple-700 text-sm">{{ fmt(totalPresupuesto) }} €</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
          <button type="button" @click="addPartida" class="mt-2 text-xs text-purple-600 hover:text-purple-800 flex items-center gap-1">
            <span class="text-sm font-bold">+</span> Añadir partida de gasto
          </button>
        </div>
      </div>

      <!-- ── Dotación de Recursos Humanos ──────────────────────────────── -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <button type="button" @click="toggle('equipos')" :class="sectionBtn">
          <span class="flex items-center gap-2"><span>🧩</span><span>Dotación de Recursos Humanos</span></span>
          <ChevronDownIcon :class="['w-4 h-4 text-gray-400 transition-transform', open.equipos ? 'rotate-180' : '']" />
        </button>
        <div v-show="open.equipos" class="px-4 pb-4 pt-3 border-t border-gray-100">
          <p class="text-xs text-gray-500 mb-3">
            Fase de diseño: define qué tareas componen la campaña y qué habilidades (y cuántas horas) necesita cada una.
            No se asignan personas todavía.
          </p>
          <table class="w-full text-xs">
            <thead>
              <tr class="text-left text-gray-500 border-b border-gray-200">
                <th class="pb-1.5 font-medium pl-1 w-1/4">Tarea</th>
                <th class="pb-1.5 font-medium w-1/4">Descripción</th>
                <th class="pb-1.5 font-medium w-1/4">Habilidad requerida</th>
                <th class="pb-1.5 font-medium w-24 text-right pr-2">Horas est.</th>
                <th class="w-6"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(t, i) in tareas" :key="t._id" class="border-b border-gray-100">
                <td class="py-1 pl-1 pr-2">
                  <input v-model="t.nombre" type="text" :class="inp" placeholder="Ej: Diseño materiales" />
                </td>
                <td class="py-1 pr-2">
                  <input v-model="t.descripcion" type="text" :class="inp" placeholder="Qué implica esta tarea" />
                </td>
                <td class="py-1 pr-2">
                  <select v-model="t.skillId" :class="inp">
                    <option value="">— Sin especificar —</option>
                    <optgroup v-for="cat in skillsByCategoria" :key="cat.nombre" :label="cat.nombre">
                      <option v-for="s in cat.skills" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                    </optgroup>
                  </select>
                </td>
                <td class="py-1 pr-2">
                  <input v-model.number="t.horasEstimadas" type="number" min="0" step="0.5" :class="inp + ' text-right'" placeholder="0" />
                </td>
                <td class="py-1 text-center">
                  <button type="button" @click="tareas.splice(i, 1)" class="text-gray-300 hover:text-red-500 text-base leading-none">✕</button>
                </td>
              </tr>
              <tr v-if="!tareas.length">
                <td colspan="5" class="py-3 text-center text-gray-400 italic">
                  Sin requerimientos de recursos humanos definidos
                </td>
              </tr>
            </tbody>
            <tfoot v-if="tareas.length > 0">
              <tr class="border-t-2 border-gray-300">
                <td colspan="3" class="pt-2 pl-1 text-xs font-semibold text-gray-700">Total horas estimadas</td>
                <td class="pt-2 pr-2 text-right font-bold text-purple-700 text-sm">{{ totalHoras }} h</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
          <button type="button" @click="addTarea" class="mt-2 text-xs text-purple-600 hover:text-purple-800 flex items-center gap-1">
            <span class="text-sm font-bold">+</span> Añadir requerimiento de habilidad
          </button>
        </div>
      </div>

      <!-- ── Error + Acciones ─────────────────────────────────────────── -->
      <div v-if="error" class="px-3 py-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">{{ error }}</div>

      <div class="flex justify-end gap-2 pt-1">
        <router-link to="/campanias"
          class="px-4 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
          Cancelar
        </router-link>
        <button type="submit" :disabled="submitting"
          class="px-5 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2">
          <span v-if="submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></span>
          {{ isEdit ? 'Actualizar' : 'Crear' }} campaña
        </button>
      </div>

    </form>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'
import {
  GET_CAMPANIA, GET_TIPOS_CAMPANIA, GET_ESTADOS_CAMPANIA,
  GET_SKILLS, CREAR_CAMPANIA, ACTUALIZAR_CAMPANIA,
} from '@/modules/comunicaciones/graphql/queries.js'
import { GET_MIEMBROS, GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'

const route   = useRoute()
const router  = useRouter()
const isEdit  = computed(() => !!route.params.id && !route.path.includes('/nueva'))
const loading = ref(false)
const submitting = ref(false)
const error   = ref(null)

// Estilos comunes
const sectionBtn = 'w-full flex items-center justify-between px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 transition-colors'
const lbl = 'block text-xs font-medium text-gray-600 mb-0.5'
const inp = 'w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-purple-500 focus:border-transparent'

// Estado de secciones abiertas
const open = reactive({ identidad: true, planificacion: false, presupuesto: false, equipos: false })
const toggle = (k) => { open[k] = !open[k] }

// ── Formulario ────────────────────────────────────────────────────────────
const campania = ref({
  nombre: '', lema: '', descripcion_corta: '', descripcion_larga: '',
  url_externa: '', tipo_campania_id: '', estado_campania_id: '',
  fecha_inicio_plan: '', fecha_fin_plan: '', fecha_inicio_real: '', fecha_fin_real: '',
  objetivo_principal: '', responsable_id: '', agrupacion_id: '',
})

// Partidas de gasto
const partidas = ref([])
let _pid = 0
const addPartida = () => partidas.value.push({ _id: ++_pid, concepto: '', cantidad: 1, importeUnitario: 0 })
const totalPresupuesto = computed(() =>
  partidas.value.reduce((s, p) => s + (p.cantidad || 0) * (p.importeUnitario || 0), 0)
)

// Tareas / equipos
const tareas = ref([])
let _tid = 0
const addTarea = () => tareas.value.push({ _id: ++_tid, nombre: '', descripcion: '', skillId: '', horasEstimadas: 0 })
const totalHoras = computed(() => tareas.value.reduce((s, t) => s + (t.horasEstimadas || 0), 0))

// Catálogos
const tiposCampania   = ref([])
const estadosCampania = ref([])
const miembros        = ref([])
const agrupaciones    = ref([])
const skills          = ref([])

const skillsByCategoria = computed(() => {
  const cats = {}
  for (const s of skills.value) {
    const c = s.categoria || 'General'
    if (!cats[c]) cats[c] = { nombre: c, skills: [] }
    cats[c].skills.push(s)
  }
  return Object.values(cats)
})

const fmt = (n) => Number(n || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

// ── Carga ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadCatalogos()
  if (isEdit.value) await loadCampania()
})

async function loadCatalogos() {
  try {
    const [tipos, estados, mbs, agrs, sks] = await Promise.all([
      executeQuery(GET_TIPOS_CAMPANIA),
      executeQuery(GET_ESTADOS_CAMPANIA),
      executeQuery(GET_MIEMBROS),
      executeQuery(GET_AGRUPACIONES),
      executeQuery(GET_SKILLS).catch(() => ({ skills: [] })),
    ])
    tiposCampania.value   = (tipos.tiposCampania || []).filter(t => t.activo)
    estadosCampania.value = (estados.estadosCampania || []).filter(e => e.activo).sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
    miembros.value        = (mbs.miembros || []).map(m => ({ id: m.id, nombre: [m.nombre, m.apellido1, m.apellido2].filter(Boolean).join(' ') }))
    agrupaciones.value    = agrs.agrupacionesTerritoriales || []
    skills.value          = (sks.skills || []).filter(s => s.activo)
  } catch (e) {
    console.error('Error cargando catálogos:', e)
  }
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
        fecha_inicio_plan:  c.fechaInicioPlan || '',
        fecha_fin_plan:     c.fechaFinPlan || '',
        fecha_inicio_real:  c.fechaInicioReal || '',
        fecha_fin_real:     c.fechaFinReal || '',
        objetivo_principal: c.objetivoPrincipal || '',
        responsable_id:     c.responsable?.id || '',
        agrupacion_id:      c.agrupacion?.id || '',
      }
    }
  } catch (e) {
    error.value = 'Error al cargar la campaña'
  } finally {
    loading.value = false
  }
}

// ── Submit ────────────────────────────────────────────────────────────────
async function handleSubmit() {
  submitting.value = true
  error.value = null
  try {
    const payload = {
      nombre:            campania.value.nombre,
      lema:              campania.value.lema || null,
      descripcionCorta:  campania.value.descripcion_corta || null,
      descripcionLarga:  campania.value.descripcion_larga || null,
      urlExterna:        campania.value.url_externa || null,
      tipoCampaniaId:    campania.value.tipo_campania_id,
      estadoId:          campania.value.estado_campania_id,
      fechaInicioPlan:   campania.value.fecha_inicio_plan || null,
      fechaFinPlan:      campania.value.fecha_fin_plan || null,
      fechaInicioReal:   campania.value.fecha_inicio_real || null,
      fechaFinReal:      campania.value.fecha_fin_real || null,
      objetivoPrincipal: campania.value.objetivo_principal || null,
      metaRecaudacion:   totalPresupuesto.value || null,
      responsableId:     campania.value.responsable_id || null,
      agrupacionId:      campania.value.agrupacion_id || null,
    }
    if (isEdit.value) {
      await executeMutation(ACTUALIZAR_CAMPANIA, { data: { id: route.params.id, ...payload } })
      router.push(`/campanias/${route.params.id}`)
    } else {
      const res = await executeMutation(CREAR_CAMPANIA, { data: payload })
      router.push(`/campanias/${res.crearCampania.id}`)
    }
  } catch (e) {
    console.error('Error guardando campaña:', e)
    error.value = 'Error al guardar. Por favor, inténtalo de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>
