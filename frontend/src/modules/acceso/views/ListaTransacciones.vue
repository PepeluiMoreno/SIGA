<template>
  <AppLayout title="Transacciones" subtitle="Jerarquía de funcionalidades y operaciones del sistema" fluid>

    <!-- Layout: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">

    <FilterRail storage-key="transacciones">
      <FilterBar
        vertical
        v-model="filters"
        v-model:search="busqueda"
        search-placeholder="Buscar por código, nombre o funcionalidad…"
        :fields="filterFields"
        @clear="limpiarFiltros"
      />

      <!-- Leyenda: el color del nombre de cada operación indica su tipo -->
      <div class="mt-4 pt-3 border-t border-slate-100">
        <span class="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Tipo de operación</span>
        <ul class="space-y-1">
          <li v-for="t in TIPOS" :key="t.value" class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="t.dot"></span>
            <span class="text-xs" :class="t.colorNum">{{ t.label }}</span>
          </li>
        </ul>
      </div>
    </FilterRail>

    <!-- Columna de resultados -->
    <div class="flex-1 min-w-0 w-full">

    <!-- Expandir / colapsar -->
    <div class="flex justify-end gap-2 mb-4">
      <button @click="expandirTodo(true)"
        class="px-2.5 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 bg-white">
        Expandir todo
      </button>
      <button @click="expandirTodo(false)"
        class="px-2.5 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 bg-white">
        Colapsar todo
      </button>
    </div>

    <!-- Estado de carga -->
    <EstadoCarga v-if="loading" mensaje="Cargando catálogo de transacciones..." />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <p class="text-red-700 font-medium">Error al cargar datos</p>
      <p class="text-red-600 text-sm mt-1">{{ error }}</p>
      <button @click="cargar" class="mt-3 text-red-600 hover:text-red-800 text-sm font-medium">
        Reintentar
      </button>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="arbol.length === 0"
      class="bg-white rounded-lg border border-gray-200 p-12 text-center text-gray-500">
      <p class="text-lg">No se encontraron transacciones</p>
      <p class="text-sm mt-1">Prueba con otros filtros</p>
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

          <!-- Cabecera de columnas (alineada con las filas de transacción) -->
          <div class="flex items-center gap-3 pl-16 pr-4 py-1.5 border-t border-gray-100 bg-white">
            <span class="w-4 flex-shrink-0"></span>
            <span class="w-60 flex-shrink-0 text-xs font-semibold text-gray-400 uppercase tracking-wide">Código</span>
            <span class="w-64 flex-shrink-0 text-xs font-semibold text-gray-400 uppercase tracking-wide">Operación</span>
            <span class="w-20 flex-shrink-0 text-center text-xs font-semibold text-gray-400 uppercase tracking-wide">Ámbito</span>
            <span class="flex-1 min-w-0 text-xs font-semibold text-gray-400 uppercase tracking-wide">Roles</span>
          </div>

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
            </button>

            <!-- ── Nivel 3: Transacciones de la funcionalidad ──────── -->
            <div v-show="funcsExpand[func.id]">
              <div v-for="ft in func.transacciones" :key="ft.transaccion.id"
                class="flex items-center gap-3 pl-16 pr-4 py-2 border-l-[3px] border-purple-100 bg-gray-50/60 hover:bg-gray-100/60 transition-colors">
                <span class="w-4 border-t border-gray-300 flex-shrink-0"></span>
                <code class="text-xs font-mono text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded w-60 flex-shrink-0 truncate"
                  :title="ft.transaccion.codigo">{{ ft.transaccion.codigo }}</code>
                <span class="text-sm w-64 flex-shrink-0 truncate" :class="tipoColor(ft.transaccion.tipo)"
                  :title="`${ft.transaccion.nombre} — ${tipoLabel(ft.transaccion.tipo)}`">{{ ft.transaccion.nombre }}</span>
                <span class="inline-flex justify-center w-20 px-2 py-0.5 text-xs rounded-full flex-shrink-0"
                  :class="AMBITO_BADGE[ft.ambito] ?? 'bg-gray-100 text-gray-500'">
                  {{ ambitoLabel(ft.ambito) }}
                </span>
                <span class="flex-1 min-w-0 flex flex-wrap items-center gap-1">
                  <template v-if="rolesDe(ft.transaccion).length">
                    <span v-for="rol in rolesDe(ft.transaccion)" :key="rol.id" :title="rol.nombre"
                      class="text-[10px] font-medium text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                      {{ rol.codigo }}
                    </span>
                  </template>
                  <span v-else
                    class="text-[10px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded"
                    title="Ningún rol tiene asignada esta transacción (solo SUPERADMIN)">
                    sin asignar
                  </span>
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
              <span class="text-sm w-64 flex-shrink-0 truncate" :class="tipoColor(tx.tipo)"
                :title="`${tx.nombre} — ${tipoLabel(tx.tipo)}`">{{ tx.nombre }}</span>
              <span class="w-20 flex-shrink-0"></span>
              <span class="flex-1 min-w-0 flex flex-wrap items-center gap-1">
                <template v-if="rolesDe(tx).length">
                  <span v-for="rol in rolesDe(tx)" :key="rol.id" :title="rol.nombre"
                    class="text-[10px] font-medium text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                    {{ rol.codigo }}
                  </span>
                </template>
                <span v-else
                  class="text-[10px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded"
                  title="Ningún rol tiene asignada esta transacción (solo SUPERADMIN)">
                  sin asignar
                </span>
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>

    </div><!-- /columna de resultados -->
    </div><!-- /layout -->

  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, watch, onActivated } from 'vue'
import { gql } from 'graphql-request'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import { graphqlClient } from '@/graphql/client.js'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'
import EstadoCarga from '@/components/common/EstadoCarga.vue'

defineOptions({ name: 'ListaTransacciones' })

const QUERY = gql`
  query Jerarquia {
    funcionalidades {
      id
      codigo
      nombre
      descripcion
      modulo
      activa
      transacciones {
        ambito
        transaccion {
          id
          codigo
          nombre
          tipo
          activa
          roles { rol { id codigo nombre } }
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
      roles { rol { id codigo nombre } }
    }
  }
`

// ── Catálogos de estilos ────────────────────────────────────────────────────

const TIPOS = [
  { value: 'consulta',      label: 'Consulta',      colorNum: 'text-blue-600',  dot: 'bg-blue-400' },
  { value: 'escritura',     label: 'Escritura',     colorNum: 'text-green-600', dot: 'bg-green-400' },
  { value: 'aprobacion',    label: 'Aprobación',    colorNum: 'text-amber-600', dot: 'bg-amber-400' },
  { value: 'critica',       label: 'Crítica',       colorNum: 'text-red-600',   dot: 'bg-red-400' },
  { value: 'configuracion', label: 'Configuración', colorNum: 'text-gray-600',  dot: 'bg-gray-400' },
]
const TIPO_MAP = Object.fromEntries(TIPOS.map(t => [t.value, t]))

// El catálogo antiguo declaraba los tipos con el vocabulario de GraphQL
// (CONSULTA/MUTACION/APROBACION). Se traduce al de negocio mientras queden
// filas sin migrar en BD.
const TIPO_LEGACY = { mutacion: 'escritura' }

function normalizarTipo(tipo) {
  const t = tipo?.toLowerCase() ?? ''
  return TIPO_LEGACY[t] ?? t
}

const AMBITO_BADGE = {
  GLOBAL:      'bg-blue-50 text-blue-600',
  TERRITORIAL: 'bg-green-50 text-green-600',
  PROPIO:      'bg-orange-50 text-orange-600',
}
const AMBITO_LABEL = { GLOBAL: 'Global', TERRITORIAL: 'Territorial', PROPIO: 'Propio' }

// Etiqueta legible del tipo: el color es la señal visual, pero el nombre debe
// seguir disponible en el `title` para quien no distinga los colores.
function tipoLabel(tipo) {
  return TIPO_MAP[normalizarTipo(tipo)]?.label ?? tipo ?? '—'
}

// SUPERADMIN se omite: el arranque lo enlaza a todas las transacciones, así que
// mostrarlo en cada fila no distingue unas de otras. Una transacción sin más
// roles que él es, a efectos de reparto, una transacción sin asignar.
function rolesDe(transaccion) {
  return (transaccion.roles ?? [])
    .map(rt => rt.rol)
    .filter(rol => rol && rol.codigo !== 'SUPERADMIN')
    .sort((a, b) => a.codigo.localeCompare(b.codigo, 'es'))
}
function ambitoLabel(ambito) {
  return AMBITO_LABEL[ambito?.toUpperCase()] ?? ambito ?? '—'
}

// El color del tipo tiñe también el nombre de la operación, para poder leer la
// naturaleza de cada transacción sin recorrer la columna de píldoras.
function tipoColor(tipo) {
  return TIPO_MAP[normalizarTipo(tipo)]?.colorNum ?? 'text-gray-700'
}

// ── Estado ──────────────────────────────────────────────────────────────────

const loading        = ref(false)
const error          = ref('')
const funcionalidades = ref([])
const transacciones  = ref([])
const busqueda       = ref('')
const filters        = ref({ tipo: [], modulo: [], sinAsignar: false })
const modulosExpand  = reactive({})
const funcsExpand    = reactive({})

// Los módulos salen de los datos, no de una lista fija: así un módulo nuevo
// aparece en el filtro sin tocar esta vista.
const modulosDisponibles = computed(() => {
  const nombres = new Set([
    ...funcionalidades.value.map(f => f.modulo),
    ...transacciones.value.map(t => t.modulo),
  ].filter(Boolean))
  return [...nombres].sort((a, b) => a.localeCompare(b, 'es'))
})

const filterFields = computed(() => [
  {
    key: 'modulo', label: 'Módulo', type: 'multiselect', allLabel: 'Todos los módulos',
    options: modulosDisponibles.value.map(m => ({ value: m, label: m.toUpperCase() })),
  },
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect', allLabel: 'Todos los tipos',
    options: TIPOS.map(t => ({ value: t.value, label: t.label })),
  },
  {
    key: 'sinAsignar', label: 'Solo sin asignar', type: 'toggle',
    hint: 'Operaciones que ningún rol puede ejecutar (salvo SUPERADMIN).',
  },
])

// ── Árbol computado ─────────────────────────────────────────────────────────

const arbol = computed(() => {
  const q          = busqueda.value.trim().toLowerCase()
  const tipo       = filters.value.tipo
  const modulo     = filters.value.modulo
  const sinAsignar = filters.value.sinAsignar

  // IDs de transacciones que pertenecen a alguna funcionalidad
  const enFuncionalidad = new Set(
    funcionalidades.value.flatMap(f => f.transacciones.map(ft => ft.transaccion.id))
  )

  // Agrupar por módulo
  const mods = {}

  // Funcionalidades
  for (const func of funcionalidades.value) {
    if (!func.activa) continue
    if (modulo.length && !modulo.includes(func.modulo)) continue

    // Filtrar transacciones de esta funcionalidad
    const txsFiltradas = func.transacciones.filter(ft => {
      const tx = ft.transaccion
      if (tipo.length && !tipo.includes(normalizarTipo(tx.tipo))) return false
      if (sinAsignar && rolesDe(tx).length) return false
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
    mods[m].funcionalidades.push({ ...func, transacciones: txsFiltradas })
  }

  // Transacciones huérfanas
  for (const tx of transacciones.value) {
    if (enFuncionalidad.has(tx.id)) continue
    if (modulo.length && !modulo.includes(tx.modulo)) continue
    if (tipo.length && !tipo.includes(normalizarTipo(tx.tipo))) continue
    if (sinAsignar && rolesDe(tx).length) continue
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

// ── Expandir/colapsar ───────────────────────────────────────────────────────

function expandirTodo(valor) {
  for (const mod of arbol.value) {
    modulosExpand[mod.nombre] = valor
    for (const func of mod.funcionalidades) funcsExpand[func.id] = valor
  }
}

// El árbol arranca colapsado; al filtrar se expande para mostrar los resultados.
watch(
  [busqueda, () => filters.value.tipo, () => filters.value.modulo, () => filters.value.sinAsignar],
  ([q, t, m, s]) => expandirTodo(Boolean(q || t.length || m.length || s)),
)

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

function limpiarFiltros() {
  busqueda.value = ''
  filters.value = { tipo: [], modulo: [], sinAsignar: false }
}

// En <keep-alive>: `onActivated` cubre el montaje inicial y cada regreso.
onActivated(cargar)
</script>
