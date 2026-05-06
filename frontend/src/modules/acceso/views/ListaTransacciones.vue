<template>
  <AppLayout title="Transacciones" subtitle="Jerarquía de funcionalidades y operaciones del sistema">

    <!-- Barra de filtros -->
    <div class="mb-4 bg-white rounded-lg border border-gray-200 px-4 py-3 flex flex-col md:flex-row gap-3 items-center">
      <div class="flex-1 relative">
        <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        <input v-model="busqueda" type="text" placeholder="Buscar por código, nombre o funcionalidad…"
          class="w-full pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-1 focus:ring-purple-500 focus:border-purple-500 focus:outline-none" />
      </div>
      <select v-model="filtroTipo"
        class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:ring-1 focus:ring-purple-500 focus:outline-none">
        <option value="">Todos los tipos</option>
        <option v-for="t in TIPOS" :key="t.value" :value="t.value">{{ t.label }}</option>
      </select>
      <button v-if="busqueda || filtroTipo" @click="busqueda = ''; filtroTipo = ''"
        class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 whitespace-nowrap">
        Limpiar
      </button>
      <div class="flex gap-2 md:ml-auto">
        <button @click="expandirTodo(true)"
          class="px-2.5 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
          Expandir todo
        </button>
        <button @click="expandirTodo(false)"
          class="px-2.5 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
          Colapsar todo
        </button>
      </div>
    </div>

    <!-- Estadísticas por tipo -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
      <div v-for="t in TIPOS" :key="t.value"
        class="bg-white rounded-lg border border-gray-200 p-3 text-center cursor-pointer hover:border-purple-300 transition-colors"
        :class="filtroTipo === t.value ? 'ring-2 ring-purple-400 border-purple-300' : ''"
        @click="filtroTipo = filtroTipo === t.value ? '' : t.value">
        <p class="text-xl font-bold" :class="t.colorNum">{{ conteoTipo[t.value] ?? 0 }}</p>
        <p class="text-xs text-gray-500 mt-0.5">{{ t.label }}</p>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="h-8 w-8 rounded-full border-4 border-purple-600 border-t-transparent animate-spin"></div>
    </div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">{{ error }}</div>

    <!-- Sin resultados -->
    <div v-else-if="arbol.length === 0"
      class="bg-white rounded-lg border border-gray-200 p-12 text-center text-sm text-gray-400">
      No hay coincidencias para los filtros aplicados.
    </div>

    <!-- Árbol: Módulo → Funcionalidad → Transacciones -->
    <div v-else class="space-y-2">
      <div v-for="mod in arbol" :key="mod.nombre" class="bg-white rounded-lg border border-gray-200 overflow-hidden">

        <!-- ── Nivel 1: Módulo ────────────────────────────────────────── -->
        <button @click="modulosExpand[mod.nombre] = !modulosExpand[mod.nombre]"
          class="w-full flex items-center gap-3 px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition-colors text-left">
          <ChevronRightIcon class="w-4 h-4 text-gray-400 flex-shrink-0 transition-transform duration-150"
            :class="modulosExpand[mod.nombre] ? 'rotate-90' : ''" />
          <span class="text-xs font-bold text-gray-600 uppercase tracking-widest flex-1">{{ mod.nombre }}</span>
          <span class="text-xs text-gray-400 mr-1">
            {{ mod.funcionalidades.length }} funcionalidad{{ mod.funcionalidades.length !== 1 ? 'es' : '' }}
            · {{ mod.totalTx }} operación{{ mod.totalTx !== 1 ? 'es' : '' }}
          </span>
        </button>

        <div v-show="modulosExpand[mod.nombre]">

          <!-- ── Nivel 2: Funcionalidades ──────────────────────────── -->
          <div v-for="func in mod.funcionalidades" :key="func.id" class="border-t border-gray-100">

            <!-- Fila funcionalidad -->
            <button @click="funcsExpand[func.id] = !funcsExpand[func.id]"
              class="w-full flex items-center gap-3 pl-8 pr-4 py-2 border-l-[3px] border-purple-300 hover:bg-purple-50 transition-colors text-left group">
              <ChevronRightIcon class="w-3.5 h-3.5 text-purple-400 flex-shrink-0 transition-transform duration-150"
                :class="funcsExpand[func.id] ? 'rotate-90' : ''" />
              <div class="flex-1 min-w-0">
                <span class="text-sm font-semibold text-purple-900">{{ func.nombre }}</span>
                <span class="ml-2 text-xs font-mono text-purple-400">{{ func.codigo }}</span>
                <p v-if="func.descripcion" class="text-xs text-gray-400 truncate mt-0.5">{{ func.descripcion }}</p>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span v-if="func.sistema"
                  class="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">sistema</span>
                <!-- mini contadores de tipos -->
                <span v-for="tc in func.tipoCounts" :key="tc.value"
                  class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs"
                  :class="tc.bg" :title="tc.label">
                  <span class="w-1.5 h-1.5 rounded-full" :class="tc.dot"></span>{{ tc.count }}
                </span>
              </div>
            </button>

            <!-- ── Nivel 3: Transacciones de la funcionalidad ──────── -->
            <div v-show="funcsExpand[func.id]">
              <div v-for="ft in func.transacciones" :key="ft.transaccion.id"
                class="flex items-center gap-3 pl-16 pr-4 py-2 border-l-[3px] border-purple-100 bg-gray-50/60 hover:bg-gray-100/60 transition-colors">
                <span class="w-4 border-t border-gray-300 flex-shrink-0"></span>
                <code class="text-xs font-mono text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded w-60 flex-shrink-0 truncate"
                  :title="ft.transaccion.codigo">{{ ft.transaccion.codigo }}</code>
                <span class="text-sm text-gray-700 flex-1 truncate" :title="ft.transaccion.nombre">{{ ft.transaccion.nombre }}</span>
                <span class="inline-flex justify-center w-28 px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0"
                  :class="tipoBadge(ft.transaccion.tipo).badge">
                  {{ tipoBadge(ft.transaccion.tipo).label }}
                </span>
                <span class="inline-flex justify-center w-20 px-2 py-0.5 text-xs rounded-full flex-shrink-0"
                  :class="AMBITO_BADGE[ft.ambito] ?? 'bg-gray-100 text-gray-500'">
                  {{ ambitoLabel(ft.ambito) }}
                </span>
              </div>
            </div>
          </div>

          <!-- ── Transacciones sin funcionalidad (huérfanas) ───────── -->
          <div v-if="mod.huerfanas.length" class="border-t border-dashed border-gray-200">
            <div class="flex items-center gap-2 pl-8 pr-4 py-1.5 bg-gray-50">
              <span class="text-xs text-gray-400 italic">Sin funcionalidad asignada</span>
              <span class="text-xs text-gray-400">({{ mod.huerfanas.length }})</span>
            </div>
            <div v-for="tx in mod.huerfanas" :key="tx.id"
              class="flex items-center gap-3 pl-12 pr-4 py-2 border-l-[3px] border-gray-200 hover:bg-gray-50 transition-colors">
              <span class="w-4 border-t border-gray-200 flex-shrink-0"></span>
              <code class="text-xs font-mono text-gray-600 bg-gray-100 px-1.5 py-0.5 rounded w-60 flex-shrink-0 truncate"
                :title="tx.codigo">{{ tx.codigo }}</code>
              <span class="text-sm text-gray-600 flex-1 truncate" :title="tx.nombre">{{ tx.nombre }}</span>
              <span class="inline-flex justify-center w-28 px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0"
                :class="tipoBadge(tx.tipo).badge">
                {{ tipoBadge(tx.tipo).label }}
              </span>
              <span class="w-20 flex-shrink-0"></span>
            </div>
          </div>

        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { MagnifyingGlassIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

const QUERY = gql`
  query Jerarquia {
    funcionalidades {
      id
      codigo
      nombre
      descripcion
      modulo
      activa
      sistema
      transacciones {
        ambito
        transaccion {
          id
          codigo
          nombre
          tipo
          activa
        }
      }
    }
    transacciones {
      id
      codigo
      nombre
      descripcion
      modulo
      tipo
      activa
    }
  }
`

// ── Catálogos de estilos ────────────────────────────────────────────────────

const TIPOS = [
  { value: 'consulta',      label: 'Consulta',      colorNum: 'text-blue-600',  badge: 'bg-blue-50 text-blue-700',    bg: 'bg-blue-50 text-blue-600',   dot: 'bg-blue-400' },
  { value: 'escritura',     label: 'Escritura',     colorNum: 'text-green-600', badge: 'bg-green-50 text-green-700',  bg: 'bg-green-50 text-green-600', dot: 'bg-green-400' },
  { value: 'aprobacion',    label: 'Aprobación',    colorNum: 'text-amber-600', badge: 'bg-amber-50 text-amber-700',  bg: 'bg-amber-50 text-amber-600', dot: 'bg-amber-400' },
  { value: 'critica',       label: 'Crítica',       colorNum: 'text-red-600',   badge: 'bg-red-50 text-red-700',      bg: 'bg-red-50 text-red-600',     dot: 'bg-red-400' },
  { value: 'configuracion', label: 'Configuración', colorNum: 'text-gray-600',  badge: 'bg-gray-100 text-gray-600',   bg: 'bg-gray-100 text-gray-500',  dot: 'bg-gray-400' },
]
const TIPO_MAP = Object.fromEntries(TIPOS.map(t => [t.value, t]))

const AMBITO_BADGE = {
  GLOBAL:      'bg-blue-50 text-blue-600',
  TERRITORIAL: 'bg-green-50 text-green-600',
  PROPIO:      'bg-orange-50 text-orange-600',
}
const AMBITO_LABEL = { GLOBAL: 'Global', TERRITORIAL: 'Territorial', PROPIO: 'Propio' }

function tipoBadge(tipo) {
  const t = TIPO_MAP[tipo?.toLowerCase()] ?? TIPO_MAP[tipo]
  return t ?? { badge: 'bg-gray-100 text-gray-600', label: tipo ?? '—' }
}
function ambitoLabel(ambito) {
  return AMBITO_LABEL[ambito?.toUpperCase()] ?? ambito ?? '—'
}

// ── Estado ──────────────────────────────────────────────────────────────────

const loading        = ref(false)
const error          = ref('')
const funcionalidades = ref([])
const transacciones  = ref([])
const busqueda       = ref('')
const filtroTipo     = ref('')
const modulosExpand  = reactive({})
const funcsExpand    = reactive({})

// ── Árbol computado ─────────────────────────────────────────────────────────

const arbol = computed(() => {
  const q    = busqueda.value.trim().toLowerCase()
  const tipo = filtroTipo.value

  // IDs de transacciones que pertenecen a alguna funcionalidad
  const enFuncionalidad = new Set(
    funcionalidades.value.flatMap(f => f.transacciones.map(ft => ft.transaccion.id))
  )

  // Agrupar por módulo
  const mods = {}

  // Funcionalidades
  for (const func of funcionalidades.value) {
    if (!func.activa) continue

    // Filtrar transacciones de esta funcionalidad
    const txsFiltradas = func.transacciones.filter(ft => {
      const tx = ft.transaccion
      if (tipo && tx.tipo?.toLowerCase() !== tipo) return false
      if (q) {
        const matchTx = tx.codigo.toLowerCase().includes(q) || tx.nombre.toLowerCase().includes(q)
        const matchFunc = func.nombre.toLowerCase().includes(q) || func.codigo.toLowerCase().includes(q)
        return matchTx || matchFunc
      }
      return true
    })

    if (!txsFiltradas.length) continue

    const m = func.modulo
    if (!mods[m]) mods[m] = { funcionalidades: [], huerfanas: [] }

    // Contadores de tipos para mini badges en la cabecera de funcionalidad
    const counts = {}
    for (const ft of txsFiltradas) {
      const k = ft.transaccion.tipo?.toLowerCase()
      counts[k] = (counts[k] ?? 0) + 1
    }
    const tipoCounts = TIPOS.filter(t => counts[t.value]).map(t => ({ ...t, count: counts[t.value] }))

    mods[m].funcionalidades.push({ ...func, transacciones: txsFiltradas, tipoCounts })
  }

  // Transacciones huérfanas
  for (const tx of transacciones.value) {
    if (enFuncionalidad.has(tx.id)) continue
    if (tipo && tx.tipo?.toLowerCase() !== tipo) continue
    if (q && !tx.codigo.toLowerCase().includes(q) && !tx.nombre.toLowerCase().includes(q)) continue
    const m = tx.modulo
    if (!mods[m]) mods[m] = { funcionalidades: [], huerfanas: [] }
    mods[m].huerfanas.push(tx)
  }

  return Object.entries(mods)
    .sort(([a], [b]) => a.localeCompare(b, 'es'))
    .map(([nombre, { funcionalidades: funcs, huerfanas }]) => ({
      nombre,
      funcionalidades: funcs,
      huerfanas,
      totalTx: funcs.reduce((s, f) => s + f.transacciones.length, 0) + huerfanas.length,
    }))
})

// Conteos globales de tipos (para las tarjetas de stats)
const conteoTipo = computed(() => {
  const c = {}
  for (const tx of transacciones.value) {
    const k = tx.tipo?.toLowerCase()
    c[k] = (c[k] ?? 0) + 1
  }
  return c
})

// ── Expandir/colapsar ───────────────────────────────────────────────────────

function expandirTodo(valor) {
  for (const mod of arbol.value) {
    modulosExpand[mod.nombre] = valor
    for (const func of mod.funcionalidades) funcsExpand[func.id] = valor
  }
}

// Cuando el árbol cambia (filtros), expande automáticamente los resultados nuevos
watch(arbol, (grupos) => {
  for (const mod of grupos) {
    if (modulosExpand[mod.nombre] === undefined) modulosExpand[mod.nombre] = true
    for (const func of mod.funcionalidades) {
      if (funcsExpand[func.id] === undefined) funcsExpand[func.id] = true
    }
  }
}, { immediate: true })

// Si hay búsqueda activa, expandir todo para ver los resultados
watch([busqueda, filtroTipo], ([q, t]) => {
  if (q || t) expandirTodo(true)
})

// ── Carga ───────────────────────────────────────────────────────────────────

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(QUERY)
    funcionalidades.value = data.funcionalidades ?? []
    transacciones.value = data.transacciones ?? []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar los datos'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
