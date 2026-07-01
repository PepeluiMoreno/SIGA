<template>
  <AppLayout :title="titulo" subtitle="Edita las metas, presupuesto, actividades y tareas predefinidos">

    <div v-if="cargando" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-sm font-medium text-red-800">Error al cargar la plantilla</p>
      <p class="text-sm text-red-700 mt-1">{{ error }}</p>
    </div>

    <template v-else-if="plantilla">
      <div class="space-y-3">

        <!-- Cabecera general (siempre visible) -->
        <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
            <h2 class="text-sm font-semibold text-slate-800">Datos generales</h2>
          </div>
          <div class="px-5 py-4 grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div class="col-span-2">
              <label :class="lbl">Nombre <span class="text-red-400">*</span></label>
              <input v-model="form.nombre" type="text" :class="inp" @blur="guardarCabecera" />
            </div>
            <div class="col-span-2">
              <label :class="lbl">Descripción</label>
              <input v-model="form.descripcion" type="text" :class="inp" @blur="guardarCabecera" placeholder="Descripción opcional" />
            </div>
            <div>
              <label :class="lbl">Tipo de campaña</label>
              <div class="h-10 px-3 flex items-center text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg">
                {{ plantilla.tipoCampania?.nombre || '—' }}
              </div>
            </div>
            <div class="flex items-end pb-1">
              <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                <input type="checkbox" v-model="form.activo" @change="guardarCabecera"
                  class="w-4 h-4 rounded text-indigo-600 border-slate-300 focus:ring-indigo-500" />
                Plantilla activa
              </label>
            </div>
          </div>
        </section>

        <!-- Acordeones (exclusivos: abrir uno cierra los demás) -->
        <AccordionGroup class="space-y-3">

          <!-- 1 · METAS -->
          <AccordionPanel :default-open="true">
            <template #title>
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
              <h2 class="text-sm font-semibold text-slate-800">Metas predefinidas</h2>
              <span v-if="metas.length" class="px-2 py-0.5 bg-violet-50 text-violet-700 border border-violet-200 text-xs font-semibold rounded-full">{{ metas.length }}</span>
            </template>
            <div class="px-5 py-4 space-y-3">
              <div v-if="metas.length" class="rounded-lg border border-slate-200 overflow-hidden">
                <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <span class="col-span-4">Tipo de meta</span>
                  <span class="col-span-2">Unidad</span>
                  <span class="col-span-2">Valor sugerido</span>
                  <span class="col-span-3">Notas</span>
                  <span class="col-span-1"></span>
                </div>
                <div v-for="(m, i) in metas" :key="m.id ?? i"
                  class="grid grid-cols-12 gap-2 px-4 py-2 items-center border-b border-slate-100 last:border-0"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
                  <div class="col-span-4">
                    <select v-model="m.tipoMetaId" :class="inpSm" @change="guardarTodasMetas">
                      <option value="">— Tipo —</option>
                      <option v-for="t in tiposMeta" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                    </select>
                  </div>
                  <div class="col-span-2 text-xs text-slate-500">{{ unidadMeta(m.tipoMetaId) }}</div>
                  <div class="col-span-2">
                    <input v-model.number="m.valorSugerido" type="number" min="0" step="1" :class="inpSm"
                      placeholder="—" @blur="guardarTodasMetas" />
                  </div>
                  <div class="col-span-3">
                    <input v-model="m.notas" type="text" :class="inpSm" placeholder="Notas…" @blur="guardarTodasMetas" />
                  </div>
                  <div class="col-span-1 flex justify-end">
                    <button @click="eliminarMeta(i)" class="p-1 rounded text-slate-300 hover:text-red-500 transition-colors">
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
              <button @click="agregarMeta"
                class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                <PlusIcon class="w-3.5 h-3.5" /> Añadir meta
              </button>
            </div>
          </AccordionPanel>

          <!-- 2 · PRESUPUESTO -->
          <AccordionPanel :default-open="false">
            <template #title>
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-emerald-500"></span>
              <h2 class="text-sm font-semibold text-slate-800">Partidas presupuestarias</h2>
              <span v-if="partidas.length" class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-full">{{ partidas.length }}</span>
            </template>
            <div class="px-5 py-4 space-y-3">
              <div v-if="partidas.length" class="rounded-lg border border-slate-200 overflow-hidden">
                <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <span class="col-span-5">Concepto</span>
                  <span class="col-span-2">Tipo</span>
                  <span class="col-span-3 text-right">Importe estimado</span>
                  <span class="col-span-2"></span>
                </div>
                <div v-for="(p, i) in partidas" :key="p.id ?? i"
                  class="grid grid-cols-12 gap-2 px-4 py-2 items-center border-b border-slate-100 last:border-0"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
                  <div class="col-span-5">
                    <input v-model="p.concepto" type="text" :class="inpSm" placeholder="Concepto…" @blur="guardarTodasPartidas" />
                  </div>
                  <div class="col-span-2">
                    <select v-model="p.tipoPartida" :class="inpSm" @change="guardarTodasPartidas">
                      <option value="gasto">Gasto</option>
                      <option value="ingreso">Ingreso</option>
                    </select>
                  </div>
                  <div class="col-span-3">
                    <input v-model.number="p.importeEstimado" type="number" min="0" step="0.01" :class="inpSm"
                      placeholder="0.00" @blur="guardarTodasPartidas" />
                  </div>
                  <div class="col-span-2 flex justify-end">
                    <button @click="eliminarPartida(i)" class="p-1 rounded text-slate-300 hover:text-red-500 transition-colors">
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
              <button @click="agregarPartida"
                class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                <PlusIcon class="w-3.5 h-3.5" /> Añadir partida
              </button>
            </div>
          </AccordionPanel>

          <!-- 3 · ACTIVIDADES -->
          <AccordionPanel :default-open="false">
            <template #title>
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-sky-500"></span>
              <h2 class="text-sm font-semibold text-slate-800">Actividades predefinidas</h2>
              <span v-if="actividades.length" class="px-2 py-0.5 bg-sky-50 text-sky-700 border border-sky-200 text-xs font-semibold rounded-full">{{ actividades.length }}</span>
            </template>
            <div class="px-5 py-4 space-y-4">
              <div v-for="(act, ai) in actividades" :key="act.id ?? ai"
                class="rounded-lg border border-slate-200 overflow-hidden">
                <div class="flex items-center gap-3 px-4 py-2.5 bg-sky-50/60 border-b border-slate-200">
                  <button @click="toggleAct(ai)" class="p-0.5">
                    <ChevronRightIcon class="w-4 h-4 text-slate-400 transition-transform"
                      :class="expandedActs.has(ai) ? 'rotate-90' : ''" />
                  </button>
                  <input v-model="act.nombre" type="text"
                    class="flex-1 text-sm font-medium text-slate-800 bg-transparent border-0 focus:outline-none focus:ring-0 px-0"
                    placeholder="Nombre de la actividad…" @blur="guardarActividad(act)" />
                  <div class="flex items-center gap-2 shrink-0">
                    <select v-model="act.tipoActividadId" :class="inpSm" class="w-full sm:w-36"
                      @change="guardarActividad(act)">
                      <option value="">— Tipo —</option>
                      <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                    </select>
                    <label class="text-xs text-slate-500">día:</label>
                    <input v-model.number="act.duracionDias" type="number" min="0"
                      class="w-14 h-7 px-2 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 text-center"
                      @blur="guardarActividad(act)" />
                    <button @click="eliminarActividad(ai)" class="p-1 rounded text-slate-300 hover:text-red-500 transition-colors">
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <div v-if="expandedActs.has(ai)" class="px-4 py-3 space-y-2 bg-white">
                  <div>
                    <input v-model="act.descripcion" type="text"
                      class="w-full text-xs text-slate-500 border-0 bg-transparent focus:outline-none focus:ring-0 px-0"
                      placeholder="Descripción de la actividad…" @blur="guardarActividad(act)" />
                  </div>
                  <!-- Tareas -->
                  <div class="pl-4 border-l-2 border-slate-200 space-y-2 mt-2">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tareas</p>
                    <div v-for="(t, ti) in act.tareas" :key="t.id ?? ti"
                      class="grid grid-cols-12 gap-1.5 items-center">
                      <input v-model="t.titulo" type="text" :class="inpSm" placeholder="Título de la tarea…"
                        @blur="guardarTarea(t, act.id)" class="col-span-4" />
                      <select v-model="t.habilidadId" :class="inpSm" @change="guardarTarea(t, act.id)" class="col-span-4">
                        <option value="">— Habilidad —</option>
                        <option v-for="h in habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                      </select>
                      <select v-model="t.nivelHabilidadId" :class="inpSm" @change="guardarTarea(t, act.id)" class="col-span-2">
                        <option value="">— Nivel —</option>
                        <option v-for="n in nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                      </select>
                      <input v-model.number="t.horasEstimadas" type="number" min="0" step="0.5"
                        class="col-span-1 h-8 px-2 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 text-right"
                        placeholder="h" @blur="guardarTarea(t, act.id)" />
                      <button @click="eliminarTarea(act, ti)" class="col-span-1 p-1 rounded text-slate-300 hover:text-red-500 transition-colors justify-self-center">
                        <XMarkIcon class="w-3 h-3" />
                      </button>
                    </div>
                    <button @click="agregarTarea(act)"
                      class="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                      <PlusIcon class="w-3 h-3" /> Añadir tarea
                    </button>
                  </div>
                </div>
              </div>
              <button @click="agregarActividad"
                class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                <PlusIcon class="w-3.5 h-3.5" /> Añadir actividad
              </button>
            </div>
          </AccordionPanel>

        </AccordionGroup>

      </div>
    </template>

  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PlusIcon, ChevronRightIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import { graphqlClient } from '@/graphql/client'
import {
  GET_PLANTILLA, GET_TIPOS_META, GET_HABILIDADES, GET_NIVELES_HABILIDAD,
  ACTUALIZAR_PLANTILLA,
  GUARDAR_METAS_PLANTILLA, GUARDAR_PARTIDAS_PLANTILLA,
  CREAR_PLANTILLA_ACTIVIDAD, ACTUALIZAR_PLANTILLA_ACTIVIDAD,
  CREAR_PLANTILLA_TAREA, ACTUALIZAR_PLANTILLA_TAREA,
} from '@/modules/comunicaciones/graphql/queries.js'

const GQL_TIPOS_ACTIVIDAD = `query TiposActividad { tiposActividad(filter:{activo:{eq:true}}) { id nombre } }`

const route = useRoute()

const lbl = 'block text-sm font-medium text-slate-700 mb-1.5'
const inp = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg ' +
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
            'bg-white placeholder:text-slate-300'
const inpSm = 'h-8 w-full px-2 py-1 text-sm border border-slate-300 rounded-lg ' +
              'focus:outline-none focus:ring-1 focus:ring-indigo-500 ' +
              'bg-white placeholder:text-slate-300'

const expandedActs = ref(new Set())
function toggleAct(i) {
  const s = new Set(expandedActs.value)
  s.has(i) ? s.delete(i) : s.add(i)
  expandedActs.value = s
}

const cargando        = ref(true)
const error           = ref(null)
const plantilla       = ref(null)
const tiposMeta       = ref([])
const tiposActividad  = ref([])
const habilidades     = ref([])
const nivelesHabilidad = ref([])

const form = reactive({ nombre: '', descripcion: '', activo: true })
const metas      = ref([])
const partidas   = ref([])
const actividades = ref([])

const titulo = computed(() => form.nombre?.trim() || plantilla.value?.nombre || 'Plantilla')

function unidadMeta(tipoMetaId) {
  return tiposMeta.value.find(t => t.id === tipoMetaId)?.unidadMedida || ''
}

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const [dataP, dataT, dataH, dataN, dataTA] = await Promise.all([
      graphqlClient.request(GET_PLANTILLA, { id: route.params.id }),
      graphqlClient.request(GET_TIPOS_META),
      graphqlClient.request(GET_HABILIDADES),
      graphqlClient.request(GET_NIVELES_HABILIDAD),
      graphqlClient.request(GQL_TIPOS_ACTIVIDAD),
    ])
    const p = dataP.plantillasCampania?.[0]
    if (!p) throw new Error('Plantilla no encontrada')
    plantilla.value = p
    form.nombre      = p.nombre
    form.descripcion = p.descripcion || ''
    form.activo      = p.activo
    metas.value      = (p.metas || []).map(m => ({ ...m, tipoMetaId: m.tipoMeta?.id || '' }))
    partidas.value   = [...(p.partidas || [])]
    actividades.value = (p.actividades || []).map(a => ({
      ...a,
      tipoActividadId: a.tipoActividad?.id || '',
      tareas: (a.tareas || []).map(t => ({ ...t, habilidadId: t.habilidad?.id || '', nivelHabilidadId: t.nivelHabilidad?.id || '' })),
    }))
    tiposMeta.value       = dataT.tiposMetaCampania ?? []
    tiposActividad.value  = (dataTA.tiposActividad ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    habilidades.value     = dataH.habilidades ?? []
    nivelesHabilidad.value = (dataN.nivelesHabilidad ?? []).sort((a, b) => a.orden - b.orden)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || e.message || 'Error'
  } finally {
    cargando.value = false
  }
}

// ── Guardar cabecera ──────────────────────────────────────────────────────────
async function guardarCabecera() {
  if (!form.nombre?.trim()) return
  try {
    await graphqlClient.request(ACTUALIZAR_PLANTILLA, {
      data: { plantillaId: plantilla.value.id, nombre: form.nombre.trim(), descripcion: form.descripcion || null, activo: form.activo },
    })
  } catch (e) { console.error('Error guardando cabecera:', e) }
}

// ── Metas ─────────────────────────────────────────────────────────────────────
function agregarMeta() {
  metas.value.push({ id: null, tipoMetaId: '', valorSugerido: null, notas: '', orden: metas.value.length + 1 })
}
function eliminarMeta(i) {
  metas.value.splice(i, 1)
  guardarTodasMetas()
}

async function guardarTodasMetas() {
  try {
    const payload = metas.value
      .filter(m => m.tipoMetaId)
      .map((m, i) => ({ tipoMetaId: m.tipoMetaId, valorSugerido: m.valorSugerido ?? null, notas: m.notas || null, orden: i + 1 }))
    const r = await graphqlClient.request(GUARDAR_METAS_PLANTILLA, { plantillaId: plantilla.value.id, metas: payload })
    const saved = r.guardarMetasPlantilla?.metas ?? []
    metas.value = saved.map(m => ({ ...m, tipoMetaId: m.tipoMeta?.id || '' }))
  } catch (e) { console.error('Error guardando metas:', e) }
}

// ── Partidas ──────────────────────────────────────────────────────────────────
function agregarPartida() {
  partidas.value.push({ id: null, concepto: '', tipoPartida: 'gasto', importeEstimado: null, orden: partidas.value.length + 1 })
}
function eliminarPartida(i) {
  partidas.value.splice(i, 1)
  guardarTodasPartidas()
}

async function guardarTodasPartidas() {
  try {
    const payload = partidas.value
      .filter(p => p.concepto?.trim())
      .map((p, i) => ({ concepto: p.concepto.trim(), tipoPartida: p.tipoPartida, importeEstimado: p.importeEstimado ?? null, orden: i + 1 }))
    const r = await graphqlClient.request(GUARDAR_PARTIDAS_PLANTILLA, { plantillaId: plantilla.value.id, partidas: payload })
    partidas.value = [...(r.guardarPartidasPlantilla?.partidas ?? [])]
  } catch (e) { console.error('Error guardando partidas:', e) }
}

// ── Actividades ───────────────────────────────────────────────────────────────
function agregarActividad() {
  const a = { id: null, nombre: '', descripcion: '', duracionDias: 0, tipoActividadId: '', orden: actividades.value.length + 1, tareas: [] }
  actividades.value.push(a)
  expandedActs.value = new Set([...expandedActs.value, actividades.value.length - 1])
}
function eliminarActividad(i) { actividades.value.splice(i, 1) }

async function guardarActividad(act) {
  if (!act.nombre?.trim()) return
  const payload = {
    nombre: act.nombre.trim(),
    descripcion: act.descripcion || null,
    duracionDias: act.duracionDias ?? 0,
    orden: act.orden ?? 1,
    tipoActividadId: act.tipoActividadId || null,
  }
  try {
    if (act.id) {
      await graphqlClient.request(ACTUALIZAR_PLANTILLA_ACTIVIDAD, {
        data: { actividadId: act.id, ...payload },
      })
    } else {
      const r = await graphqlClient.request(CREAR_PLANTILLA_ACTIVIDAD, {
        data: { plantillaId: plantilla.value.id, ...payload },
      })
      act.id = r.crearPlantillaActividad.id
    }
  } catch (e) { console.error('Error guardando actividad:', e) }
}

// ── Tareas ────────────────────────────────────────────────────────────────────
function agregarTarea(act) {
  act.tareas.push({ id: null, titulo: '', horasEstimadas: null, descripcion: '', orden: act.tareas.length + 1, habilidadId: '', nivelHabilidadId: '' })
}
function eliminarTarea(act, ti) { act.tareas.splice(ti, 1) }

async function guardarTarea(t, actividadId) {
  if (!t.titulo?.trim() || !actividadId) return
  try {
    const habilidadId      = t.habilidadId      || null
    const nivelHabilidadId = t.nivelHabilidadId || null
    if (t.id) {
      await graphqlClient.request(ACTUALIZAR_PLANTILLA_TAREA, {
        data: { tareaId: t.id, titulo: t.titulo.trim(), descripcion: t.descripcion || null, horasEstimadas: t.horasEstimadas ?? null, orden: t.orden ?? 1, habilidadId, nivelHabilidadId },
      })
    } else {
      const r = await graphqlClient.request(CREAR_PLANTILLA_TAREA, {
        data: { actividadId, titulo: t.titulo.trim(), descripcion: t.descripcion || null, horasEstimadas: t.horasEstimadas ?? null, orden: t.orden ?? 1, habilidadId, nivelHabilidadId },
      })
      t.id = r.crearPlantillaTarea.id
    }
  } catch (e) { console.error('Error guardando tarea:', e) }
}

onMounted(cargar)
</script>
