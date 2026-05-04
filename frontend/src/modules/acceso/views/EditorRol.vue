<template>
  <AppLayout
    :title="`Editor de rol: ${rol?.nombre || '...'}`"
    :subtitle="rol ? `${rol.codigo} · ${rol.tipo} · Nivel ${rol.nivel}` : ''"
  >
    <!-- Breadcrumb -->
    <div class="mb-4 flex items-center gap-2 text-sm text-gray-500">
      <router-link to="/roles" class="hover:text-purple-600 transition-colors">Roles</router-link>
      <span>›</span>
      <span class="text-gray-900 font-medium">{{ rol?.nombre || '...' }}</span>
      <span>›</span>
      <span class="text-gray-900">Funcionalidades</span>
    </div>

    <!-- Tabs: Funcionalidades / Transacciones directas -->
    <div class="mb-4 border-b border-gray-200 flex gap-0">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="px-5 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px"
        :class="activeTab === tab.id
          ? 'border-purple-600 text-purple-700'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
      >
        {{ tab.label }}
        <span class="ml-1.5 text-xs" :class="activeTab === tab.id ? 'text-purple-400' : 'text-gray-400'">
          {{ tab.count.value }}
        </span>
      </button>
    </div>

    <!-- Carga inicial -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
      {{ error }}
      <button @click="cargar" class="ml-4 font-medium underline hover:no-underline">Reintentar</button>
    </div>

    <template v-else-if="rol">
      <!-- Mensaje de éxito -->
      <div
        v-if="savedMsg"
        class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 flex items-center gap-2"
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        {{ savedMsg }}
      </div>

      <!-- TAB: FUNCIONALIDADES -->
      <div v-if="activeTab === 'funcionalidades'">
        <!-- Leyenda de ámbitos -->
        <div class="mb-3 flex items-center gap-4 text-xs text-gray-500">
          <span class="font-medium">Ámbito:</span>
          <span v-for="a in AMBITOS" :key="a.key" class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full" :class="a.dot"></span>
            {{ a.label }}
          </span>
        </div>

        <div class="grid grid-cols-[1fr_52px_1fr] gap-3 items-start">

          <!-- Panel izquierdo: Disponibles -->
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-gray-700">
                  Disponibles
                  <span class="ml-1 text-xs font-normal text-gray-400">({{ filteredFuncLeft.length }})</span>
                </span>
                <button
                  v-if="selectedFuncLeft.length > 0"
                  @click="selectedFuncLeft = []"
                  class="text-xs text-gray-400 hover:text-gray-600"
                >
                  Limpiar ({{ selectedFuncLeft.length }})
                </button>
              </div>
              <input
                v-model="searchFuncLeft"
                type="text"
                placeholder="Buscar funcionalidades..."
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div class="overflow-y-auto" style="max-height: 60vh">
              <div v-if="filteredFuncLeft.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">
                {{ searchFuncLeft ? 'Sin resultados' : 'Todas las funcionalidades están asignadas' }}
              </div>
              <div v-for="group in groupedFuncLeft" :key="group.modulo">
                <div
                  class="px-3 py-2 bg-gray-50 border-y border-gray-100 flex items-center gap-2 cursor-pointer select-none hover:bg-gray-100"
                  @click="expandedFuncLeft[group.modulo] = !expandedFuncLeft[group.modulo]"
                >
                  <input
                    type="checkbox"
                    :checked="isAllSelectedFuncLeft(group.items)"
                    :indeterminate="isSomeSelectedFuncLeft(group.items) && !isAllSelectedFuncLeft(group.items)"
                    class="w-3.5 h-3.5 text-purple-600 border-gray-300 rounded focus:ring-0"
                    @click.stop
                    @change="toggleModuleFuncLeft(group.items, $event.target.checked)"
                  />
                  <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex-1">
                    {{ group.modulo }}
                  </span>
                  <span class="text-xs text-gray-400">{{ group.items.length }}</span>
                  <svg
                    class="w-3.5 h-3.5 text-gray-400 transition-transform"
                    :class="expandedFuncLeft[group.modulo] !== false ? '' : '-rotate-90'"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                <div v-show="expandedFuncLeft[group.modulo] !== false">
                  <label
                    v-for="f in group.items"
                    :key="f.id"
                    class="flex items-start gap-2.5 px-4 py-2.5 border-b border-gray-50 hover:bg-purple-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="f.id"
                      v-model="selectedFuncLeft"
                      class="mt-0.5 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500 shrink-0"
                    />
                    <div class="flex-1 min-w-0">
                      <div class="text-xs font-mono text-purple-700 leading-tight">{{ f.codigo }}</div>
                      <div class="text-sm text-gray-700 leading-tight">{{ f.nombre }}</div>
                      <div class="mt-1 flex flex-wrap gap-1">
                        <span
                          v-for="ft in f.transacciones"
                          :key="ft.transaccion.id"
                          class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs"
                          :class="ambitoClass(ft.ambito)"
                          :title="ft.ambito"
                        >
                          <span class="w-1.5 h-1.5 rounded-full" :class="ambitoDot(ft.ambito)"></span>
                          {{ ft.transaccion.codigo }}
                        </span>
                      </div>
                    </div>
                    <span v-if="f.sistema" class="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded shrink-0">sistema</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="flex flex-col items-center gap-2 pt-14">
            <button
              @click="moverFuncAAsignadas"
              :disabled="selectedFuncLeft.length === 0"
              class="relative w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all"
              :class="selectedFuncLeft.length > 0
                ? 'border-purple-600 bg-purple-600 text-white hover:bg-purple-700'
                : 'border-gray-200 bg-white text-gray-300 cursor-not-allowed'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
              </svg>
              <span
                v-if="selectedFuncLeft.length > 0"
                class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-purple-100 text-purple-700 text-xs rounded-full flex items-center justify-center font-bold"
              >{{ selectedFuncLeft.length }}</span>
            </button>
            <button
              @click="moverFuncADisponibles"
              :disabled="selectedFuncRight.length === 0"
              class="relative w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all"
              :class="selectedFuncRight.length > 0
                ? 'border-red-500 bg-red-500 text-white hover:bg-red-600'
                : 'border-gray-200 bg-white text-gray-300 cursor-not-allowed'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
              </svg>
              <span
                v-if="selectedFuncRight.length > 0"
                class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-100 text-red-700 text-xs rounded-full flex items-center justify-center font-bold"
              >{{ selectedFuncRight.length }}</span>
            </button>
          </div>

          <!-- Panel derecho: Asignadas -->
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 bg-purple-50 border-b border-purple-100">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-purple-700">
                  Asignadas al rol
                  <span class="ml-1 text-xs font-normal text-purple-400">({{ filteredFuncRight.length }})</span>
                </span>
                <button
                  v-if="selectedFuncRight.length > 0"
                  @click="selectedFuncRight = []"
                  class="text-xs text-purple-400 hover:text-purple-600"
                >
                  Limpiar ({{ selectedFuncRight.length }})
                </button>
              </div>
              <input
                v-model="searchFuncRight"
                type="text"
                placeholder="Buscar asignadas..."
                class="w-full px-3 py-1.5 text-sm border border-purple-200 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
              />
            </div>
            <div class="overflow-y-auto" style="max-height: 60vh">
              <div v-if="filteredFuncRight.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">
                {{ searchFuncRight ? 'Sin resultados' : 'Sin funcionalidades asignadas' }}
              </div>
              <div v-for="group in groupedFuncRight" :key="group.modulo">
                <div
                  class="px-3 py-2 bg-purple-50 border-y border-purple-100 flex items-center gap-2 cursor-pointer select-none hover:bg-purple-100"
                  @click="expandedFuncRight[group.modulo] = !expandedFuncRight[group.modulo]"
                >
                  <input
                    type="checkbox"
                    :checked="isAllSelectedFuncRight(group.items)"
                    :indeterminate="isSomeSelectedFuncRight(group.items) && !isAllSelectedFuncRight(group.items)"
                    class="w-3.5 h-3.5 text-purple-600 border-purple-300 rounded focus:ring-0"
                    @click.stop
                    @change="toggleModuleFuncRight(group.items, $event.target.checked)"
                  />
                  <span class="text-xs font-semibold text-purple-600 uppercase tracking-wider flex-1">
                    {{ group.modulo }}
                  </span>
                  <span class="text-xs text-purple-400">{{ group.items.length }}</span>
                  <svg
                    class="w-3.5 h-3.5 text-purple-400 transition-transform"
                    :class="expandedFuncRight[group.modulo] !== false ? '' : '-rotate-90'"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                <div v-show="expandedFuncRight[group.modulo] !== false">
                  <label
                    v-for="f in group.items"
                    :key="f.id"
                    class="flex items-start gap-2.5 px-4 py-2.5 border-b border-purple-50 hover:bg-red-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="f.id"
                      v-model="selectedFuncRight"
                      class="mt-0.5 w-4 h-4 text-red-500 border-gray-300 rounded focus:ring-red-500 shrink-0"
                    />
                    <div class="flex-1 min-w-0">
                      <div class="text-xs font-mono text-purple-700 leading-tight">{{ f.codigo }}</div>
                      <div class="text-sm text-gray-700 leading-tight">{{ f.nombre }}</div>
                      <div class="mt-1 flex flex-wrap gap-1">
                        <span
                          v-for="ft in f.transacciones"
                          :key="ft.transaccion.id"
                          class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs"
                          :class="ambitoClass(ft.ambito)"
                          :title="ft.ambito"
                        >
                          <span class="w-1.5 h-1.5 rounded-full" :class="ambitoDot(ft.ambito)"></span>
                          {{ ft.transaccion.codigo }}
                        </span>
                      </div>
                    </div>
                    <span v-if="f.sistema" class="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded shrink-0">sistema</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-4 flex items-center justify-between">
          <button
            @click="cancelarFunc"
            :disabled="saving"
            class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancelar cambios
          </button>
          <div class="flex items-center gap-4">
            <span v-if="hasFuncChanges" class="text-sm text-gray-500">
              <span v-if="pendingFuncAdd.length > 0" class="text-green-600 font-medium">+{{ pendingFuncAdd.length }}</span>
              <span v-if="pendingFuncAdd.length > 0 && pendingFuncRemove.length > 0" class="mx-1 text-gray-300">·</span>
              <span v-if="pendingFuncRemove.length > 0" class="text-red-600 font-medium">-{{ pendingFuncRemove.length }}</span>
              <span class="ml-1">cambios pendientes</span>
            </span>
            <span v-else class="text-sm text-gray-400">Sin cambios pendientes</span>
            <button
              @click="guardarFunc"
              :disabled="!hasFuncChanges || saving"
              class="px-5 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span v-if="saving" class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
              {{ saving ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </div>
      </div>

      <!-- TAB: TRANSACCIONES DIRECTAS (redirige a la vista existente) -->
      <div v-if="activeTab === 'transacciones'" class="py-6 text-center">
        <p class="text-sm text-gray-500 mb-4">
          Las transacciones directas se gestionan en la vista de permisos granulares.
        </p>
        <router-link
          :to="`/roles/${route.params.id}/permisos`"
          class="px-5 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors"
        >
          Ir a permisos granulares
        </router-link>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'
import {
  GET_ROL_CON_FUNCIONALIDADES,
  GET_FUNCIONALIDADES_TODAS,
  ASIGNAR_FUNCIONALIDAD,
  REVOCAR_FUNCIONALIDAD,
} from '@/graphql/queries/administracion.js'

const route = useRoute()

const AMBITOS = [
  { key: 'GLOBAL',      label: 'Global',      dot: 'bg-blue-500',   badge: 'bg-blue-50 text-blue-700' },
  { key: 'TERRITORIAL', label: 'Territorial',  dot: 'bg-green-500',  badge: 'bg-green-50 text-green-700' },
  { key: 'PROPIO',      label: 'Propio',       dot: 'bg-orange-400', badge: 'bg-orange-50 text-orange-700' },
]

function ambitoDot(ambito) {
  return AMBITOS.find(a => a.key === ambito)?.dot ?? 'bg-gray-400'
}
function ambitoClass(ambito) {
  return AMBITOS.find(a => a.key === ambito)?.badge ?? 'bg-gray-50 text-gray-600'
}

const rol = ref(null)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const savedMsg = ref('')

const allFuncionalidades = ref([])
const assignedFuncIds = ref([])
const originalFuncIds = ref([])
const rolFuncMap = ref({})   // { funcionalidadId → rolFuncionalidadId }

const selectedFuncLeft = ref([])
const selectedFuncRight = ref([])
const searchFuncLeft = ref('')
const searchFuncRight = ref('')
const expandedFuncLeft = reactive({})
const expandedFuncRight = reactive({})

const activeTab = ref('funcionalidades')

const tabs = [
  { id: 'funcionalidades', label: 'Funcionalidades',  count: computed(() => assignedFuncIds.value.length) },
  { id: 'transacciones',   label: 'Transacciones directas', count: computed(() => rol.value?.transacciones?.length ?? 0) },
]

// ─── Helpers ────────────────────────────────────────────────────────────────

function groupByModule(items) {
  const map = {}
  for (const f of items) {
    if (!map[f.modulo]) map[f.modulo] = []
    map[f.modulo].push(f)
  }
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b, 'es'))
    .map(([modulo, items]) => ({
      modulo,
      items: items.slice().sort((a, b) => a.codigo.localeCompare(b.codigo)),
    }))
}

function matchesSearch(f, q) {
  if (!q) return true
  const s = q.toLowerCase()
  return f.codigo.toLowerCase().includes(s) || f.nombre.toLowerCase().includes(s)
}

// ─── Computed ────────────────────────────────────────────────────────────────

const filteredFuncLeft = computed(() =>
  allFuncionalidades.value
    .filter(f => !assignedFuncIds.value.includes(f.id))
    .filter(f => matchesSearch(f, searchFuncLeft.value))
)
const filteredFuncRight = computed(() =>
  allFuncionalidades.value
    .filter(f => assignedFuncIds.value.includes(f.id))
    .filter(f => matchesSearch(f, searchFuncRight.value))
)

const groupedFuncLeft = computed(() => groupByModule(filteredFuncLeft.value))
const groupedFuncRight = computed(() => groupByModule(filteredFuncRight.value))

const pendingFuncAdd = computed(() =>
  assignedFuncIds.value.filter(id => !originalFuncIds.value.includes(id))
)
const pendingFuncRemove = computed(() =>
  originalFuncIds.value.filter(id => !assignedFuncIds.value.includes(id))
)
const hasFuncChanges = computed(
  () => pendingFuncAdd.value.length > 0 || pendingFuncRemove.value.length > 0
)

// ─── Auto-expand ────────────────────────────────────────────────────────────

watch(groupedFuncLeft, groups => {
  groups.forEach(g => { if (expandedFuncLeft[g.modulo] === undefined) expandedFuncLeft[g.modulo] = true })
}, { immediate: true })

watch(groupedFuncRight, groups => {
  groups.forEach(g => { if (expandedFuncRight[g.modulo] === undefined) expandedFuncRight[g.modulo] = true })
}, { immediate: true })

// ─── Selección por módulo ────────────────────────────────────────────────────

function isAllSelectedFuncLeft(items)  { return items.length > 0 && items.every(f => selectedFuncLeft.value.includes(f.id)) }
function isSomeSelectedFuncLeft(items) { return items.some(f => selectedFuncLeft.value.includes(f.id)) }
function toggleModuleFuncLeft(items, checked) {
  if (checked) items.forEach(f => { if (!selectedFuncLeft.value.includes(f.id)) selectedFuncLeft.value.push(f.id) })
  else selectedFuncLeft.value = selectedFuncLeft.value.filter(id => !items.some(f => f.id === id))
}
function isAllSelectedFuncRight(items)  { return items.length > 0 && items.every(f => selectedFuncRight.value.includes(f.id)) }
function isSomeSelectedFuncRight(items) { return items.some(f => selectedFuncRight.value.includes(f.id)) }
function toggleModuleFuncRight(items, checked) {
  if (checked) items.forEach(f => { if (!selectedFuncRight.value.includes(f.id)) selectedFuncRight.value.push(f.id) })
  else selectedFuncRight.value = selectedFuncRight.value.filter(id => !items.some(f => f.id === id))
}

// ─── Shuttle ────────────────────────────────────────────────────────────────

function moverFuncAAsignadas() {
  selectedFuncLeft.value.forEach(id => { if (!assignedFuncIds.value.includes(id)) assignedFuncIds.value.push(id) })
  selectedFuncLeft.value = []
}
function moverFuncADisponibles() {
  selectedFuncRight.value.forEach(id => {
    const idx = assignedFuncIds.value.indexOf(id)
    if (idx !== -1) assignedFuncIds.value.splice(idx, 1)
  })
  selectedFuncRight.value = []
}
function cancelarFunc() {
  assignedFuncIds.value = [...originalFuncIds.value]
  selectedFuncLeft.value = []
  selectedFuncRight.value = []
}

// ─── Guardar ────────────────────────────────────────────────────────────────

async function guardarFunc() {
  saving.value = true
  error.value = null
  savedMsg.value = ''
  try {
    await Promise.all([
      ...pendingFuncAdd.value.map(id =>
        executeMutation(ASIGNAR_FUNCIONALIDAD, {
          data: { rolId: rol.value.id, funcionalidadId: id },
        })
      ),
      ...pendingFuncRemove.value.map(id => {
        const rfId = rolFuncMap.value[id]
        if (!rfId) return Promise.resolve()
        return executeMutation(REVOCAR_FUNCIONALIDAD, { filter: { id: { eq: rfId } } })
      }),
    ])
    await cargar()
    savedMsg.value = `Cambios guardados: ${pendingFuncAdd.value.length} añadidas, ${pendingFuncRemove.value.length} revocadas.`
    setTimeout(() => { savedMsg.value = '' }, 4000)
  } catch (err) {
    console.error('Error guardando funcionalidades:', err)
    error.value = err?.response?.errors?.[0]?.message || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

// ─── Carga ──────────────────────────────────────────────────────────────────

async function cargar() {
  loading.value = true
  error.value = null
  try {
    const [rolData, funcData] = await Promise.all([
      executeQuery(GET_ROL_CON_FUNCIONALIDADES, { id: route.params.id }),
      executeQuery(GET_FUNCIONALIDADES_TODAS),
    ])

    const rolRaw = rolData.roles?.[0]
    if (!rolRaw) throw new Error('Rol no encontrado')
    rol.value = rolRaw

    allFuncionalidades.value = funcData.funcionalidades || []

    const map = {}
    const ids = []
    for (const rf of rolRaw.funcionalidades || []) {
      if (rf.funcionalidad) {
        map[rf.funcionalidad.id] = rf.id
        ids.push(rf.funcionalidad.id)
      }
    }
    rolFuncMap.value = map
    assignedFuncIds.value = ids
    originalFuncIds.value = [...ids]
    selectedFuncLeft.value = []
    selectedFuncRight.value = []
  } catch (err) {
    console.error('Error cargando editor de rol:', err)
    error.value = err?.response?.errors?.[0]?.message || err.message || 'Error al cargar'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
