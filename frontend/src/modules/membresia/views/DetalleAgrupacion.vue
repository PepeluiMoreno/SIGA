<template>
  <AppLayout
    :title="agrupacion?.nombre || 'Agrupación'"
    :subtitle="agrupacion?.tipoUnidad?.nombre || ''">

    <div class="flex items-center justify-between mb-4">
      <router-link to="/agrupaciones"
        class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition-colors">
        <ChevronLeftIcon class="w-4 h-4" /> Volver al árbol
      </router-link>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
      {{ error }}
    </div>
    <div v-else-if="!agrupacion" class="rounded-xl border border-slate-200 bg-white px-6 py-10 text-center text-sm text-slate-500">
      Agrupación no encontrada.
    </div>

    <div v-else class="space-y-3">

      <!-- ══ 1 · DATOS GENERALES ════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('info')" :class="accordionBtn(open.info)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
            <h2 :class="titleCls">Datos generales</h2>
          </span>
          <ChevronDownIcon :class="chevronCls(open.info)" />
        </button>
        <div v-show="open.info" class="px-5 py-4 grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
          <div class="col-span-4">
            <p :class="lbl">Nombre oficial</p>
            <p class="text-slate-800 font-medium">{{ agrupacion.nombre }}</p>
          </div>
          <div class="col-span-2">
            <p :class="lbl">Nombre corto</p>
            <p class="text-slate-700">{{ agrupacion.nombreCorto || '—' }}</p>
          </div>
          <div class="col-span-3">
            <p :class="lbl">Tipo de unidad</p>
            <p class="text-slate-700">{{ agrupacion.tipoUnidad?.nombre || '—' }}</p>
          </div>
          <div class="col-span-3">
            <p :class="lbl">Depende de</p>
            <p class="text-slate-700">{{ agrupacion.agrupacionPadreId ? '—' : '(unidad raíz)' }}</p>
          </div>
          <div class="col-span-4" v-if="agrupacion.email">
            <p :class="lbl">Email</p>
            <a :href="`mailto:${agrupacion.email}`" class="text-indigo-600 hover:underline">{{ agrupacion.email }}</a>
          </div>
          <div class="col-span-3" v-if="agrupacion.telefono">
            <p :class="lbl">Teléfono</p>
            <p class="text-slate-700">{{ agrupacion.telefono }}</p>
          </div>
          <div class="col-span-5" v-if="agrupacion.web">
            <p :class="lbl">Web</p>
            <a :href="agrupacion.web" target="_blank" rel="noopener" class="text-indigo-600 hover:underline">{{ agrupacion.web }}</a>
          </div>
          <div class="col-span-12" v-if="agrupacion.descripcion">
            <p :class="lbl">Descripción</p>
            <p class="text-slate-700">{{ agrupacion.descripcion }}</p>
          </div>
        </div>
      </section>

      <!-- ══ 2 · CARGOS REGISTRADOS ════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('cargos')" :class="accordionBtn(open.cargos)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
            <h2 :class="titleCls">Cargos registrados</h2>
            <span v-if="todosRegistros.length"
              class="px-2 py-0.5 bg-violet-50 text-violet-700 border border-violet-200 text-xs font-semibold rounded-full tabular-nums">
              {{ todosRegistros.length }}
            </span>
          </span>
          <ChevronDownIcon :class="chevronCls(open.cargos)" />
        </button>
        <div v-show="open.cargos" class="px-5 pb-4 pt-2">

          <!-- Barra de acción -->
          <div class="flex justify-end mb-3">
            <button type="button" @click="abrirRegistro(null)"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-violet-50 text-violet-700 hover:bg-violet-100 border border-violet-200 transition-colors">
              <PlusIcon class="w-3.5 h-3.5" /> Registrar cargo
            </button>
          </div>

          <div v-if="!todosRegistros.length"
            class="py-8 text-center text-xs text-slate-400 italic">
            Sin cargos registrados para esta unidad.
          </div>
          <table v-else class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 w-36">Cargo</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Titular</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 hidden md:table-cell">Localidad</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 w-28 hidden sm:table-cell">Desde</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 w-24 hidden lg:table-cell">Estado</th>
                <th class="w-20"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reg in todosRegistros" :key="reg.id"
                class="group border-b border-slate-50 last:border-0">
                <td class="py-2.5 pr-3">
                  <span class="text-sm font-medium text-slate-700">{{ reg.rol?.nombre || '—' }}</span>
                </td>
                <td class="py-2.5 pr-3">
                  <span class="text-sm text-slate-800">
                    {{ reg.miembro?.nombre }} {{ reg.miembro?.apellido1 }}
                  </span>
                </td>
                <td class="py-2.5 pr-3 text-sm text-slate-500 hidden md:table-cell">
                  {{ reg.agrupacion?.nombre || '—' }}
                </td>
                <td class="py-2.5 pr-3 text-sm text-slate-500 tabular-nums hidden sm:table-cell">
                  {{ fmtFecha(reg.fechaInicio) }}
                </td>
                <td class="py-2.5 pr-3 hidden lg:table-cell">
                  <span class="px-2 py-0.5 text-xs rounded-full font-medium"
                    :class="estadoBadge(reg.estado)">
                    {{ reg.estado }}
                  </span>
                </td>
                <td class="py-2.5" v-if="!reg._esHijo">
                  <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity justify-end">
                    <button type="button" @click="abrirRegistro(reg)"
                      class="p-1 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                      title="Editar">
                      <PencilIcon class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="reg.estado === 'ACTIVO'" type="button"
                      @click="cesarRegistro(reg)"
                      class="p-1 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                      title="Dar de baja">
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
                <td v-else class="py-2.5"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ══ Modal registro de cargo ════════════════════════════════════════ -->
    <div v-if="modal.visible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">
            {{ modal.editandoId ? 'Editar registro de cargo' : 'Registrar cargo' }}
          </h3>
          <button @click="modal.visible = false" class="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <!-- Cargo (solo lectura si editando, selector si nuevo) -->
          <div v-if="!modal.editandoId">
            <label :class="lbl">Cargo <span class="text-red-400">*</span></label>
            <select v-model="modal.rolId" :class="inp">
              <option value="">— Seleccionar cargo —</option>
              <option v-for="r in rolesTerritoriales" :key="r.id" :value="r.id">{{ r.nombre }}</option>
            </select>
          </div>
          <div v-else>
            <label :class="lbl">Cargo</label>
            <p class="text-sm text-slate-700 font-medium">{{ modal.rolNombre }}</p>
          </div>

          <!-- Buscador de miembro -->
          <div>
            <label :class="lbl">Titular <span class="text-red-400">*</span></label>
            <div class="relative">
              <input v-model="modal.miembroSearch" type="text" :class="inp"
                placeholder="Buscar por nombre…" autocomplete="off"
                @focus="modal.showList = true" @blur="ocultarLista" />
              <div v-if="modal.showList && miembrosFiltrados.length"
                class="absolute z-30 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-44 overflow-y-auto">
                <button type="button" v-for="m in miembrosFiltrados" :key="m.id"
                  @mousedown="seleccionarMiembro(m)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                  {{ m.nombre }} {{ m.apellido1 }}
                </button>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label :class="lbl">Fecha inicio <span class="text-red-400">*</span></label>
              <input v-model="modal.fechaInicio" type="date" :class="inp" />
            </div>
            <div>
              <label :class="lbl">Fecha fin</label>
              <input v-model="modal.fechaFin" type="date" :class="inp" />
            </div>
          </div>
          <div>
            <label :class="lbl">Observaciones</label>
            <textarea v-model="modal.observaciones" rows="2" :class="inpTa"
              placeholder="Notas sobre el cargo…"></textarea>
          </div>
          <p v-if="modal.error" class="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ modal.error }}</p>
        </div>
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
          <button @click="modal.visible = false"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="guardarRegistro"
            :disabled="!modal.miembroId || !modal.fechaInicio || (!modal.editandoId && !modal.rolId) || modal.guardando"
            class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium">
            <span v-if="modal.guardando" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full mr-1"></span>
            {{ modal.editandoId ? 'Guardar' : 'Registrar' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import {
  ChevronDownIcon, ChevronLeftIcon,
  PencilIcon, PlusIcon, XMarkIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'

const route = useRoute()
const agrupacionId = computed(() => route.params.id)

// ── Estilos ─────────────────────────────────────────────────────────────────
const cardCls = 'rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden'
const titleCls = 'text-sm font-semibold text-slate-800'
const lbl = 'block text-sm font-medium text-slate-700 mb-1.5'
const inp = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
            'bg-white placeholder:text-slate-300'
const inpTa = 'w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
              'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
              'bg-white placeholder:text-slate-300'

const accordionBtn = (isOpen) =>
  'w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/60 transition-colors ' +
  (isOpen ? 'border-b border-slate-200' : '')
const chevronCls = (isOpen) =>
  'w-4 h-4 text-slate-400 transition-transform duration-200 ' + (isOpen ? 'rotate-180' : '')

// ── Acordeones ───────────────────────────────────────────────────────────────
const open = reactive({ info: true, cargos: true })

function togglePanel(key) {
  if (open[key]) { open[key] = false; return }
  const prevOpen = Object.keys(open).filter(k => open[k])
  open[key] = true
  nextTick(() => {
    if (document.documentElement.scrollHeight > window.innerHeight && prevOpen.length)
      open[prevOpen[prevOpen.length - 1]] = false
  })
}

// ── Estado ───────────────────────────────────────────────────────────────────
const loading             = ref(false)
const error               = ref(null)
const agrupacion          = ref(null)
const nombramientos       = ref([])   // registros directos de esta unidad
const nombramientosHijos  = ref([])   // registros de unidades hijas
const rolesTerritoriales  = ref([])   // roles organizacionales territoriales
const miembros            = ref([])   // miembros para el buscador

// ── Computed ─────────────────────────────────────────────────────────────────
// Todos los registros activos: directos primero, luego hijos (marcados)
const todosRegistros = computed(() => [
  ...nombramientos.value,
  ...nombramientosHijos.value.map(r => ({ ...r, _esHijo: true })),
])

// Rol más probable para el selector: el que corresponde al nivel en la jerarquía
const rolSugerido = computed(() => {
  const nivel = agrupacion.value?.tipoUnidad?.nivel
  if (nivel === 1) return rolesTerritoriales.value.find(r => r.codigo === 'COORDINADOR')
  if (nivel === 2) return rolesTerritoriales.value.find(r => r.codigo === 'COORD_PROV')
  if (nivel === 3) return rolesTerritoriales.value.find(r => r.codigo === 'COORD_LOCAL')
  return rolesTerritoriales.value[0] ?? null
})

// ── Helpers ──────────────────────────────────────────────────────────────────
const fmtFecha = (d) => d ? new Date(d + 'T00:00:00').toLocaleDateString('es-ES') : '—'
const estadoBadge = (e) => ({
  ACTIVO:      'bg-green-100 text-green-800',
  PENDIENTE:   'bg-yellow-100 text-yellow-800',
  EN_REVISION: 'bg-blue-100 text-blue-800',
  FINALIZADO:  'bg-slate-100 text-slate-600',
  RECHAZADO:   'bg-red-100 text-red-700',
}[e] ?? 'bg-slate-100 text-slate-600')

// ── Queries ───────────────────────────────────────────────────────────────────
const Q_AGRUPACION = `
  query Agrupacion($id: UUID!) {
    unidadesOrganizativas(filter: { id: { eq: $id } }) {
      id nombre nombreCorto descripcion email telefono web activo
      tipoId agrupacionPadreId
      tipoUnidad { id nombre naturaleza nivel }
    }
  }
`
const Q_ROLES_TERRITORIALES = `
  query RolesTerritoriales {
    roles(filter: { tipo: { eq: "ORGANIZACION" }, eliminado: { eq: false } }) {
      id codigo nombre nivel esTerritorial nivelTerritorial
    }
  }
`
const Q_NOMBRAMIENTOS = `
  query Nombramientos($agrupacionId: UUID!) {
    historialNombramientos(filter: { agrupacionId: { eq: $agrupacionId }, estado: { eq: "ACTIVO" } }) {
      id rolId estado fechaInicio fechaFin observaciones
      miembro { id nombre apellido1 }
      rol { id codigo nombre }
      agrupacion { id nombre }
    }
  }
`
const Q_HIJOS = `
  query AgrupacionesHijas($padreId: UUID!) {
    unidadesOrganizativas(filter: { agrupacionPadreId: { eq: $padreId }, activo: { eq: true } }) {
      id nombre
    }
  }
`
const Q_MIEMBROS = `
  query MiembrosAgrupacion($agrupacionId: UUID!) {
    miembros(filter: { agrupacionId: { eq: $agrupacionId }, eliminado: { eq: false } }) {
      id nombre apellido1
    }
  }
`

// ── Carga ────────────────────────────────────────────────────────────────────
onMounted(cargar)

async function cargar() {
  loading.value = true
  error.value = null
  try {
    const [rAgr, rRoles, rNombr, rHijos, rMbs] = await Promise.allSettled([
      executeQuery(Q_AGRUPACION, { id: agrupacionId.value }),
      executeQuery(Q_ROLES_TERRITORIALES),
      executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: agrupacionId.value }),
      executeQuery(Q_HIJOS, { padreId: agrupacionId.value }),
      executeQuery(Q_MIEMBROS, { agrupacionId: agrupacionId.value }),
    ])
    if (rAgr.status === 'fulfilled')
      agrupacion.value = rAgr.value.unidadesOrganizativas?.[0] ?? null
    if (rRoles.status === 'fulfilled')
      rolesTerritoriales.value = (rRoles.value.roles ?? [])
        .filter(r => r.esTerritorial)
        .sort((a, b) => (a.nivel ?? 99) - (b.nivel ?? 99))
    if (rNombr.status === 'fulfilled')
      nombramientos.value = rNombr.value.historialNombramientos ?? []
    if (rMbs.status === 'fulfilled')
      miembros.value = (rMbs.value.miembros ?? [])
        .sort((a, b) => `${a.nombre} ${a.apellido1}`.localeCompare(`${b.nombre} ${b.apellido1}`, 'es'))

    // Cargar registros de unidades hijas
    if (rHijos.status === 'fulfilled') {
      const hijos = rHijos.value.unidadesOrganizativas ?? []
      if (hijos.length) {
        await cargarNombramientosHijos(hijos.map(h => h.id))
      }
    }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando la agrupación'
  } finally {
    loading.value = false
  }
}

async function cargarNombramientosHijos(ids) {
  // Carga secuencial por cada hijo (strawchemy puede no soportar filtro `in` para UUID)
  const resultados = await Promise.allSettled(
    ids.map(id => executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: id }))
  )
  nombramientosHijos.value = resultados
    .filter(r => r.status === 'fulfilled')
    .flatMap(r => r.value.historialNombramientos ?? [])
}

async function recargarNombramientos() {
  const [rNombr, rHijos] = await Promise.allSettled([
    executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: agrupacionId.value }),
    executeQuery(Q_HIJOS, { padreId: agrupacionId.value }),
  ])
  if (rNombr.status === 'fulfilled')
    nombramientos.value = rNombr.value.historialNombramientos ?? []
  if (rHijos.status === 'fulfilled') {
    const hijos = rHijos.value.unidadesOrganizativas ?? []
    if (hijos.length) await cargarNombramientosHijos(hijos.map(h => h.id))
    else nombramientosHijos.value = []
  }
}

// ── Modal registro ────────────────────────────────────────────────────────────
const modal = reactive({
  visible: false, editandoId: null, guardando: false, error: null,
  rolId: '', rolNombre: '',
  miembroId: null, miembroSearch: '', showList: false,
  fechaInicio: '', fechaFin: '', observaciones: '',
})

const miembrosFiltrados = computed(() => {
  const q = modal.miembroSearch.trim().toLowerCase()
  if (q.length < 2) return []
  return miembros.value
    .filter(m => `${m.nombre} ${m.apellido1}`.toLowerCase().includes(q))
    .slice(0, 10)
})

function abrirRegistro(registro = null) {
  const hoy = new Date().toISOString().split('T')[0]
  Object.assign(modal, {
    visible: true, error: null, guardando: false, showList: false,
    rolId: registro?.rolId ?? (rolSugerido.value?.id ?? ''),
    rolNombre: registro?.rol?.nombre ?? '',
    editandoId: registro?.id ?? null,
    miembroId: registro?.miembro?.id ?? null,
    miembroSearch: registro?.miembro
      ? `${registro.miembro.nombre} ${registro.miembro.apellido1}`
      : '',
    fechaInicio: registro?.fechaInicio ?? hoy,
    fechaFin: registro?.fechaFin ?? '',
    observaciones: registro?.observaciones ?? '',
  })
}

function ocultarLista() {
  setTimeout(() => { modal.showList = false }, 150)
}

function seleccionarMiembro(m) {
  modal.miembroId = m.id
  modal.miembroSearch = `${m.nombre} ${m.apellido1}`
  modal.showList = false
}

async function guardarRegistro() {
  modal.guardando = true
  modal.error = null
  try {
    const data = {
      miembroId: modal.miembroId,
      rolId: modal.rolId,
      agrupacionId: agrupacionId.value,
      fechaInicio: modal.fechaInicio,
      fechaFin: modal.fechaFin || null,
      observaciones: modal.observaciones || null,
      estado: 'ACTIVO',
    }
    if (modal.editandoId) {
      await executeMutation(
        `mutation ActualizarRegistro($data: HistorialNombramientoUpdateInput!) {
           actualizarHistorialNombramiento(data: $data) { id }
         }`,
        { data: { id: modal.editandoId, ...data } }
      )
    } else {
      await executeMutation(
        `mutation CrearRegistro($data: HistorialNombramientoCreateInput!) {
           crearHistorialNombramiento(data: $data) { id }
         }`,
        { data }
      )
    }
    modal.visible = false
    await recargarNombramientos()
  } catch (e) {
    modal.error = e?.response?.errors?.[0]?.message || 'Error al guardar el registro'
  } finally {
    modal.guardando = false
  }
}

async function cesarRegistro(reg) {
  if (!confirm(`¿Dar de baja a ${reg.miembro?.nombre} ${reg.miembro?.apellido1} en el cargo?`)) return
  await executeMutation(
    `mutation CesarRegistro($data: HistorialNombramientoUpdateInput!) {
       actualizarHistorialNombramiento(data: $data) { id }
     }`,
    { data: { id: reg.id, estado: 'FINALIZADO', fechaFin: new Date().toISOString().split('T')[0] } }
  )
  await recargarNombramientos()
}
</script>
