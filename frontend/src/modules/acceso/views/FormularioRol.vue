<template>
  <AppLayout
    :title="esEdicion ? `Editar rol: ${form.nombre || '…'}` : 'Nuevo rol'"
    :subtitle="esEdicion && rolOriginal ? `${rolOriginal.codigo} · ${rolOriginal.tipo} · Nivel ${rolOriginal.nivel}` : 'Definición de atributos y permisos'"
  >
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm text-gray-500 mb-4">
      <router-link to="/roles" class="hover:text-purple-600 transition-colors">Roles y permisos</router-link>
      <span>›</span>
      <span class="text-gray-900 font-medium">{{ esEdicion ? (form.nombre || '…') : 'Nuevo rol' }}</span>
    </div>

    <!-- Carga inicial -->
    <div v-if="cargandoRol" class="flex items-center justify-center py-24">
      <div class="h-8 w-8 rounded-full border-4 border-purple-600 border-t-transparent animate-spin"></div>
    </div>
    <div v-else-if="errorCarga" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ errorCarga }}
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-4 lg:h-[calc(100vh-168px)]">

        <!-- ── Col izquierda: atributos básicos ──────────────────────── -->
        <div class="flex flex-col gap-4 min-h-0">
          <section class="bg-white rounded-lg border border-gray-200 flex-shrink-0">
            <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-lg">
              <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Datos del rol</h2>
            </div>
            <div class="px-4 py-4 space-y-4">
              <div>
                <label class="label">Código <span class="text-red-500">*</span></label>
                <input v-model="form.codigo" type="text" class="input font-mono uppercase"
                  placeholder="MI_ROL" :disabled="esEdicion && rolOriginal?.sistema" />
                <p class="text-xs text-gray-400 mt-0.5">Letras mayúsculas, números y guión bajo</p>
              </div>
              <div>
                <label class="label">Nombre <span class="text-red-500">*</span></label>
                <input v-model="form.nombre" type="text" class="input" placeholder="Nombre descriptivo" />
              </div>
              <div>
                <label class="label">Descripción</label>
                <textarea v-model="form.descripcion" rows="3" class="input resize-none"
                  placeholder="Para qué sirve este rol…" />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="flex items-center gap-1 mb-0.5">
                    <label class="text-xs font-medium text-gray-600">Tipo</label>
                    <span class="relative group/tip flex items-center">
                      <InformationCircleIcon class="w-3.5 h-3.5 text-gray-400 cursor-help" />
                      <div class="absolute left-0 top-5 z-50 hidden group-hover/tip:block w-64 rounded-lg border border-gray-200 bg-white shadow-lg p-3 text-xs text-gray-700 space-y-2">
                        <p class="font-semibold text-gray-900 mb-1">Tipos de rol</p>
                        <div v-for="t in TIPOS_ROL_INFO" :key="t.valor" class="flex gap-2">
                          <span class="font-medium shrink-0" :class="t.color">{{ t.etiqueta }}</span>
                          <span class="text-gray-500">{{ t.descripcion }}</span>
                        </div>
                      </div>
                    </span>
                  </div>
                  <select v-model="form.tipo" class="input" :disabled="esEdicion && rolOriginal?.sistema"
                    @change="onTipoChange">
                    <option value="PERSONALIZADO">Personalizado</option>
                    <option value="FUNCIONAL">Funcional</option>
                    <option value="TERRITORIAL">Territorial</option>
                    <option value="ORGANIZACION">Organización</option>
                    <option value="SISTEMA">Sistema</option>
                  </select>
                </div>
                <div>
                  <label class="label">Nivel</label>
                  <input v-model.number="form.nivel" type="number" min="0" max="100" class="input" />
                </div>
              </div>

              <!-- Ámbito territorial: solo visible cuando tipo = TERRITORIAL -->
              <div v-if="form.tipo === 'TERRITORIAL'"
                class="rounded-lg border border-green-200 bg-green-50/60 px-3 py-3 space-y-2">
                <div class="flex items-center justify-between">
                  <p class="text-xs font-semibold text-green-800 uppercase tracking-wide">Ámbito territorial</p>
                  <span v-if="implantacionOrg" class="text-xs text-green-600 bg-green-100 border border-green-200 px-1.5 py-0.5 rounded">
                    Org: {{ implantacionOrg.charAt(0) + implantacionOrg.slice(1).toLowerCase() }}
                  </span>
                </div>
                <div>
                  <label class="label">Nivel de agrupación</label>
                  <select v-model="form.nivelTerritorial" class="input"
                    :class="nivelTerritorialFueraDeRango ? 'border-amber-400 bg-amber-50' : ''">
                    <option value="">— Sin restricción de nivel —</option>
                    <option v-for="nv in nivelesTerritoriales" :key="nv.value" :value="nv.value">
                      {{ nv.label }}
                    </option>
                  </select>
                  <p class="text-xs text-gray-400 mt-0.5">
                    Solo se ofrecen los niveles compatibles con la implantación geográfica de la organización.
                  </p>
                </div>
                <!-- Aviso nivel fuera de rango (rol cargado de BD con valor incompatible) -->
                <div v-if="nivelTerritorialFueraDeRango"
                  class="flex items-start gap-1.5 rounded bg-amber-50 border border-amber-300 px-2 py-1.5 text-xs text-amber-800">
                  <ExclamationTriangleIcon class="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                  El nivel «{{ form.nivelTerritorial }}» no es compatible con la implantación geográfica
                  <strong>{{ implantacionOrg }}</strong> configurada en la organización. Corrígelo antes de guardar.
                </div>
              </div>

              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="form.activo" type="checkbox"
                  class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                <span class="text-xs text-gray-700">Rol activo</span>
              </label>
            </div>
          </section>

          <!-- Error y acciones -->
          <div v-if="errorGuardado"
            class="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700 flex-shrink-0">
            {{ errorGuardado }}
          </div>

          <div class="flex items-center gap-3 flex-shrink-0">
            <button @click="guardar" :disabled="guardando"
              class="px-5 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2">
              <span v-if="guardando"
                class="h-3.5 w-3.5 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
              {{ guardando ? 'Guardando…' : (esEdicion ? 'Guardar cambios' : 'Crear rol') }}
            </button>
            <button type="button" @click="router.push('/roles')"
              class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5">
              <ArrowLeftIcon class="w-3.5 h-3.5" />
              Volver
            </button>
            <span v-if="guardadoOk" class="text-sm text-green-600 flex items-center gap-1">
              <CheckIcon class="w-4 h-4" /> Guardado
            </span>
          </div>
        </div>

        <!-- ── Col derecha: árbol funcionalidades + transacciones ────── -->
        <div class="flex flex-col min-h-0 bg-white rounded-lg border border-gray-200 overflow-hidden">

          <!-- Cabecera del panel -->
          <div class="px-4 py-2 border-b border-gray-100 bg-gray-50 flex items-center justify-between flex-shrink-0">
            <h2 class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Permisos</h2>
            <div v-if="!cargandoFuncs" class="flex items-center gap-3 text-xs text-gray-500">
              <span><span class="font-semibold text-purple-700">{{ selectedFuncIds.length }}</span> funcionalidades</span>
              <span v-if="selectedTxIds.length">
                · <span class="font-semibold text-blue-600">{{ selectedTxIds.length }}</span> permisos directos
              </span>
            </div>
          </div>

          <!-- Buscador -->
          <div class="px-4 py-2 border-b border-gray-100 flex-shrink-0">
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
              <input v-model="busqueda" type="text" placeholder="Buscar funcionalidad o transacción…"
                class="input pl-8 py-1.5 text-sm" />
            </div>
          </div>

          <!-- Cargando -->
          <div v-if="cargandoFuncs" class="flex-1 flex items-center justify-center">
            <div class="h-6 w-6 rounded-full border-4 border-purple-500 border-t-transparent animate-spin"></div>
          </div>

          <!-- Sin resultados -->
          <div v-else-if="funcsPorModulo.length === 0"
            class="flex-1 flex items-center justify-center text-sm text-gray-400">
            {{ busqueda ? `Sin resultados para "${busqueda}"` : 'No hay funcionalidades disponibles' }}
          </div>

          <!-- Árbol -->
          <div v-else class="flex-1 overflow-y-auto">
            <div v-for="grupo in funcsPorModulo" :key="grupo.modulo">

              <!-- Nivel 1: Módulo -->
              <div class="sticky top-0 z-10 flex items-center gap-2 px-4 py-2 bg-gray-50 border-b border-gray-100 cursor-pointer hover:bg-gray-100 select-none"
                @click="toggleModuloExpand(grupo.modulo)">
                <input type="checkbox"
                  :checked="isModuloTodo(grupo.items)"
                  :indeterminate.prop="isModuloParcial(grupo.items)"
                  class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-0 flex-shrink-0"
                  @click.stop
                  @change="toggleModulo(grupo.items, $event.target.checked)" />
                <span class="text-xs font-bold text-gray-500 uppercase tracking-widest flex-1">{{ grupo.modulo }}</span>
                <span class="text-xs text-gray-400 mr-1">
                  {{ grupo.items.filter(f => selectedFuncIds.includes(f.id)).length }}/{{ grupo.items.length }} funcs
                </span>
                <ChevronDownIcon class="w-3.5 h-3.5 text-gray-400 transition-transform flex-shrink-0"
                  :class="expandedModulos[grupo.modulo] === false ? '-rotate-90' : ''" />
              </div>

              <!-- Funcionalidades del módulo -->
              <div v-show="expandedModulos[grupo.modulo] !== false">
                <div v-for="func in grupo.items" :key="func.id">

                  <!-- Nivel 2: Funcionalidad -->
                  <div class="flex items-center gap-2 px-4 py-2.5 border-b border-gray-50 border-l-[3px] cursor-pointer transition-colors select-none"
                    :class="selectedFuncIds.includes(func.id)
                      ? 'border-l-purple-400 bg-purple-50/70 hover:bg-purple-50'
                      : 'border-l-gray-200 hover:bg-gray-50'"
                    @click="toggleFuncExpand(func.id)">
                    <input type="checkbox" :value="func.id" v-model="selectedFuncIds"
                      class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600 focus:ring-purple-500 flex-shrink-0"
                      @click.stop @change="onFuncChange(func)" />
                    <ChevronRightIcon class="w-3 h-3 text-gray-400 flex-shrink-0 transition-transform duration-150"
                      :class="expandedFuncs[func.id] ? 'rotate-90' : ''" />
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium"
                        :class="selectedFuncIds.includes(func.id) ? 'text-purple-900' : 'text-gray-800'">
                        {{ func.nombre }}
                      </span>
                      <span class="ml-2 text-xs font-mono text-gray-400">{{ func.codigo }}</span>
                    </div>
                    <div class="flex items-center gap-1.5 flex-shrink-0">
                      <span v-if="func.sistema"
                        class="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">sistema</span>
                      <!-- mini contadores de transacciones por tipo -->
                      <span v-for="tc in func.tipoCounts" :key="tc.value"
                        class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs"
                        :class="tc.bg" :title="tc.label">
                        <span class="w-1.5 h-1.5 rounded-full" :class="tc.dot"></span>{{ tc.count }}
                      </span>
                    </div>
                  </div>

                  <!-- Nivel 3: Transacciones -->
                  <div v-show="expandedFuncs[func.id]">
                    <div v-for="ft in func.transacciones" :key="ft.transaccion.id"
                      class="flex items-center gap-2 pl-10 pr-4 py-1.5 border-b border-gray-50 border-l-[3px] transition-colors"
                      :class="selectedFuncIds.includes(func.id)
                        ? 'border-l-purple-200 bg-purple-50/40'
                        : 'border-l-gray-100 hover:bg-gray-50'">

                      <!-- Si la funcionalidad está seleccionada: pill "heredado" -->
                      <span v-if="selectedFuncIds.includes(func.id)"
                        class="text-xs text-purple-400 bg-purple-100 px-1.5 py-0.5 rounded flex-shrink-0">
                        heredado
                      </span>
                      <!-- Si no: checkbox individual para asignación directa -->
                      <input v-else type="checkbox" :value="ft.transaccion.id" v-model="selectedTxIds"
                        class="h-3.5 w-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0"
                        @click.stop />

                      <code class="text-xs font-mono text-gray-600 bg-gray-100 px-1.5 py-0.5 rounded w-52 flex-shrink-0 truncate"
                        :class="selectedFuncIds.includes(func.id) ? 'text-purple-600 bg-purple-100' : ''"
                        :title="ft.transaccion.codigo">{{ ft.transaccion.codigo }}</code>
                      <span class="text-xs text-gray-600 flex-1 truncate" :title="ft.transaccion.nombre">
                        {{ ft.transaccion.nombre }}
                      </span>
                      <span class="inline-flex justify-center w-24 px-1.5 py-0.5 text-xs font-medium rounded-full flex-shrink-0"
                        :class="TIPO_MAP[ft.transaccion.tipo?.toLowerCase()]?.badge ?? 'bg-gray-100 text-gray-600'">
                        {{ TIPO_MAP[ft.transaccion.tipo?.toLowerCase()]?.label ?? ft.transaccion.tipo }}
                      </span>
                      <span class="inline-flex justify-center w-20 px-1.5 py-0.5 text-xs rounded-full flex-shrink-0"
                        :class="AMBITO_BADGE[ft.ambito] ?? 'bg-gray-100 text-gray-500'">
                        {{ AMBITO_LABEL[ft.ambito] ?? ft.ambito }}
                      </span>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_ROLES, CREAR_ROL, ACTUALIZAR_ROL, GET_FUNCIONALIDADES_TODAS } from '@/graphql/queries/administracion.js'
// GET_AGRUPACIONES_TERRITORIALES ya no se usa para niveles — los derivamos del config org
import { CheckIcon, MagnifyingGlassIcon, ChevronDownIcon, ChevronRightIcon, InformationCircleIcon, ExclamationTriangleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const route  = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.id)

// ── Niveles territoriales y restricciones por implantación ───────────────────
const QUERY_ORG = `query { parametrosOrganizacion { implantacionGeografica } }`

const TODOS_NIVELES = [
  { value: 'MUNICIPAL',       label: 'Municipal' },
  { value: 'PROVINCIAL',      label: 'Provincial' },
  { value: 'AUTONOMICA',      label: 'Autonómica' },
  { value: 'ESTATAL',         label: 'Estatal' },
  { value: 'SIN_DEMARCACION', label: 'Sin demarcación política' },
]

// Coincide con la lógica de ParametrosGenerales.vue
const NIVELES_POR_IMPLANTACION = {
  LOCAL:          ['MUNICIPAL', 'SIN_DEMARCACION'],
  PROVINCIAL:     ['MUNICIPAL', 'PROVINCIAL', 'SIN_DEMARCACION'],
  NACIONAL:       ['MUNICIPAL', 'PROVINCIAL', 'AUTONOMICA', 'ESTATAL', 'SIN_DEMARCACION'],
  INTERNACIONAL:  null,  // todos
}

// ── Tipos de rol: descripciones para tooltip ──────────────────────────────────
const TIPOS_ROL_INFO = [
  { valor: 'FUNCIONAL',     etiqueta: 'Funcional',     color: 'text-purple-700', descripcion: 'Agrupa permisos por área de gestión (tesorería, secretaría, comunicación…).' },
  { valor: 'TERRITORIAL',   etiqueta: 'Territorial',   color: 'text-green-700',  descripcion: 'Aplica dentro de un ámbito geográfico concreto (provincial, local…). Requiere nivel de agrupación.' },
  { valor: 'ORGANIZACION',  etiqueta: 'Organización',  color: 'text-blue-700',   descripcion: 'Vinculado a la estructura orgánica (comité ejecutivo, asamblea…).' },
  { valor: 'PERSONALIZADO', etiqueta: 'Personalizado', color: 'text-gray-700',   descripcion: 'De propósito general, compuesto manualmente con funcionalidades sueltas.' },
  { valor: 'SISTEMA',       etiqueta: 'Sistema',       color: 'text-red-700',    descripcion: 'Gestionado internamente. No debe modificarse manualmente.' },
]

// ── Estilos ───────────────────────────────────────────────────────────────────
const TIPOS = [
  { value: 'consulta',      label: 'Consulta',      badge: 'bg-blue-50 text-blue-700',    bg: 'bg-blue-50 text-blue-600',   dot: 'bg-blue-400' },
  { value: 'escritura',     label: 'Escritura',     badge: 'bg-green-50 text-green-700',  bg: 'bg-green-50 text-green-600', dot: 'bg-green-400' },
  { value: 'aprobacion',    label: 'Aprobación',    badge: 'bg-amber-50 text-amber-700',  bg: 'bg-amber-50 text-amber-600', dot: 'bg-amber-400' },
  { value: 'critica',       label: 'Crítica',       badge: 'bg-red-50 text-red-700',      bg: 'bg-red-50 text-red-600',     dot: 'bg-red-400' },
  { value: 'configuracion', label: 'Configuración', badge: 'bg-gray-100 text-gray-600',   bg: 'bg-gray-100 text-gray-500',  dot: 'bg-gray-400' },
]
const TIPO_MAP    = Object.fromEntries(TIPOS.map(t => [t.value, t]))
const AMBITO_BADGE = { GLOBAL: 'bg-blue-50 text-blue-600', TERRITORIAL: 'bg-green-50 text-green-600', PROPIO: 'bg-orange-50 text-orange-600' }
const AMBITO_LABEL = { GLOBAL: 'Global', TERRITORIAL: 'Territorial', PROPIO: 'Propio' }

// ── Estado ────────────────────────────────────────────────────────────────────
const cargandoRol        = ref(false)
const errorCarga         = ref('')
const rolOriginal        = ref(null)
const cargandoFuncs      = ref(false)
const allFuncionalidades = ref([])
const selectedFuncIds    = ref([])
const selectedTxIds      = ref([])  // transacciones asignadas directamente
const expandedModulos    = reactive({})
const expandedFuncs      = reactive({})
const busqueda           = ref('')
const guardando          = ref(false)
const guardadoOk         = ref(false)
const errorGuardado      = ref('')

const implantacionOrg      = ref('')   // 'LOCAL' | 'PROVINCIAL' | 'NACIONAL' | 'INTERNACIONAL'
const nivelesTerritoriales = computed(() => {
  const permitidos = NIVELES_POR_IMPLANTACION[implantacionOrg.value] ?? null
  return permitidos
    ? TODOS_NIVELES.filter(n => permitidos.includes(n.value))
    : TODOS_NIVELES
})
const nivelTerritorialFueraDeRango = computed(() =>
  form.tipo === 'TERRITORIAL'
  && form.nivelTerritorial
  && form.nivelTerritorial !== 'SIN_DEMARCACION'
  && !nivelesTerritoriales.value.some(n => n.value === form.nivelTerritorial)
)

const form = reactive({
  codigo: '', nombre: '', descripcion: '',
  tipo: 'PERSONALIZADO', nivel: 0, activo: true,
  nivelTerritorial: '',
})

// ── Árbol computado ───────────────────────────────────────────────────────────
const funcsPorModulo = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  const map = {}

  for (const f of allFuncionalidades.value) {
    const matchFunc = !q || f.nombre.toLowerCase().includes(q) || f.codigo.toLowerCase().includes(q)
    const txsFiltradas = f.transacciones.filter(ft =>
      matchFunc || ft.transaccion.codigo.toLowerCase().includes(q) || ft.transaccion.nombre.toLowerCase().includes(q)
    )
    if (!txsFiltradas.length && !matchFunc) continue

    const counts = {}
    for (const ft of f.transacciones) {
      const k = ft.transaccion.tipo?.toLowerCase()
      counts[k] = (counts[k] ?? 0) + 1
    }
    const tipoCounts = TIPOS.filter(t => counts[t.value]).map(t => ({ ...t, count: counts[t.value] }))

    if (!map[f.modulo]) map[f.modulo] = []
    map[f.modulo].push({ ...f, tipoCounts })
  }

  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b, 'es'))
    .map(([modulo, items]) => ({ modulo, items }))
})

// ── Control de módulos y funcionalidades ─────────────────────────────────────
function isModuloTodo(items)    { return items.length > 0 && items.every(f => selectedFuncIds.value.includes(f.id)) }
function isModuloParcial(items) { return items.some(f => selectedFuncIds.value.includes(f.id)) && !isModuloTodo(items) }

function toggleModulo(items, checked) {
  if (checked) {
    items.forEach(f => {
      if (!selectedFuncIds.value.includes(f.id)) selectedFuncIds.value.push(f.id)
      // Al seleccionar funcionalidad, quitar sus transacciones de la selección directa
      const txIds = new Set(f.transacciones.map(ft => ft.transaccion.id))
      selectedTxIds.value = selectedTxIds.value.filter(id => !txIds.has(id))
    })
  } else {
    const ids = new Set(items.map(f => f.id))
    selectedFuncIds.value = selectedFuncIds.value.filter(id => !ids.has(id))
  }
}

function onFuncChange(func) {
  if (selectedFuncIds.value.includes(func.id)) {
    // Funcionalidad recién activada: quitar sus transacciones de la selección directa
    const txIds = new Set(func.transacciones.map(ft => ft.transaccion.id))
    selectedTxIds.value = selectedTxIds.value.filter(id => !txIds.has(id))
  }
}

function toggleModuloExpand(modulo) {
  expandedModulos[modulo] = expandedModulos[modulo] === false ? true : false
}
function toggleFuncExpand(id) {
  expandedFuncs[id] = !expandedFuncs[id]
}

// Auto-expandir módulos y funcionalidades al cargar
watch(funcsPorModulo, (grupos) => {
  for (const g of grupos) {
    if (expandedModulos[g.modulo] === undefined) expandedModulos[g.modulo] = true
    for (const f of g.items) {
      if (expandedFuncs[f.id] === undefined) expandedFuncs[f.id] = false // cerradas por defecto
    }
  }
}, { immediate: true })

// Expandir funcionalidades con búsqueda activa
watch(busqueda, (q) => {
  if (!q) return
  for (const g of funcsPorModulo.value) {
    expandedModulos[g.modulo] = true
    for (const f of g.items) expandedFuncs[f.id] = true
  }
})

// ── Tipo change ───────────────────────────────────────────────────────────────
function onTipoChange() {
  if (form.tipo !== 'TERRITORIAL') {
    form.nivelTerritorial = ''
  }
}

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargarImplantacionOrg() {
  try {
    const data = await graphqlClient.request(QUERY_ORG)
    implantacionOrg.value = data.parametrosOrganizacion?.implantacionGeografica ?? ''
  } catch {
    // no bloqueante; sin restricción si falla
  }
}

async function cargarFuncionalidades() {
  cargandoFuncs.value = true
  try {
    const data = await graphqlClient.request(GET_FUNCIONALIDADES_TODAS)
    allFuncionalidades.value = (data.funcionalidades ?? [])
      .filter(f => f.activa)
      .sort((a, b) => a.modulo.localeCompare(b.modulo, 'es') || a.nombre.localeCompare(b.nombre, 'es'))
  } finally {
    cargandoFuncs.value = false
  }
}

async function cargarRol(id) {
  cargandoRol.value = true
  errorCarga.value = ''
  try {
    const data = await graphqlClient.request(GET_ROLES)
    const rol = (data.roles ?? []).find(r => r.id === id)
    if (!rol) { errorCarga.value = 'Rol no encontrado'; return }
    rolOriginal.value = rol
    Object.assign(form, {
      codigo:           rol.codigo,
      nombre:           rol.nombre,
      descripcion:      rol.descripcion ?? '',
      tipo:             rol.tipo,
      nivel:            rol.nivel,
      activo:           rol.activo,
      nivelTerritorial: rol.nivelTerritorial ?? '',
    })
    selectedFuncIds.value = (rol.funcionalidades ?? [])
      .filter(rf => rf.funcionalidad)
      .map(rf => rf.funcionalidad.id)
    selectedTxIds.value = (rol.transacciones ?? [])
      .filter(rt => rt.transaccion)
      .map(rt => rt.transaccion.id)
  } catch (e) {
    errorCarga.value = e?.response?.errors?.[0]?.message ?? 'Error al cargar el rol'
  } finally {
    cargandoRol.value = false
  }
}

// ── Guardar ───────────────────────────────────────────────────────────────────
async function guardar() {
  if (!form.codigo.trim()) { errorGuardado.value = 'El código es obligatorio'; return }
  if (!form.nombre.trim()) { errorGuardado.value = 'El nombre es obligatorio'; return }
  if (nivelTerritorialFueraDeRango.value) {
    errorGuardado.value = `El nivel territorial «${form.nivelTerritorial}» no es compatible con la implantación geográfica de la organización`
    return
  }

  errorGuardado.value = ''
  guardando.value = true
  try {
    const esTerritorial = form.tipo === 'TERRITORIAL'
    const nivelTerritorial = esTerritorial && form.nivelTerritorial ? form.nivelTerritorial : null

    if (esEdicion.value) {
      await graphqlClient.request(ACTUALIZAR_ROL, {
        data: {
          id:               rolOriginal.value.id,
          nombre:           form.nombre,
          descripcion:      form.descripcion || null,
          tipo:             form.tipo,
          nivel:            form.nivel,
          activo:           form.activo,
          esTerritorial,
          nivelTerritorial,
          funcionalidadIds: selectedFuncIds.value,
          transaccionIds:   selectedTxIds.value,
          ...(!rolOriginal.value.sistema && { codigo: form.codigo.toUpperCase() }),
        },
      })
      guardadoOk.value = true
      setTimeout(() => router.push('/roles'), 1200)
    } else {
      await graphqlClient.request(CREAR_ROL, {
        data: {
          codigo:           form.codigo.toUpperCase(),
          nombre:           form.nombre,
          descripcion:      form.descripcion || null,
          tipo:             form.tipo,
          nivel:            form.nivel,
          activo:           form.activo,
          esTerritorial,
          nivelTerritorial,
          funcionalidadIds: selectedFuncIds.value,
          transaccionIds:   selectedTxIds.value,
        },
      })
      router.push('/roles')
    }
  } catch (e) {
    errorGuardado.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

// ── Inicialización ────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    cargarFuncionalidades(),
    cargarImplantacionOrg(),
    esEdicion.value ? cargarRol(route.params.id) : Promise.resolve(),
  ])
})
</script>

<style scoped>
.label { @apply block text-xs font-medium text-gray-600 mb-0.5; }
.input {
  @apply w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900
         placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500
         focus:outline-none transition-colors;
}
.input:disabled { @apply bg-gray-50 text-gray-500 cursor-not-allowed; }
</style>
