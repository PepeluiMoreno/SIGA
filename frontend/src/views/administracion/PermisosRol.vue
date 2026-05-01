<template>
  <AppLayout
    :title="`Permisos: ${rol?.nombre || '...'}`"
    :subtitle="rol ? `${rol.codigo} · ${rol.tipo} · Nivel ${rol.nivel}` : ''"
  >
    <!-- Breadcrumb -->
    <div class="mb-4 flex items-center gap-2 text-sm text-gray-500">
      <router-link to="/roles" class="hover:text-purple-600 transition-colors">Roles</router-link>
      <span>›</span>
      <span class="text-gray-900 font-medium">{{ rol?.nombre || '...' }}</span>
      <span>›</span>
      <span class="text-gray-900">Permisos</span>
    </div>

    <!-- Carga inicial -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
      {{ error }}
      <button @click="cargar" class="ml-4 font-medium underline hover:no-underline">Reintentar</button>
    </div>

    <template v-else-if="rol">
      <!-- Mensaje de guardado -->
      <div
        v-if="savedMsg"
        class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 flex items-center gap-2"
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        {{ savedMsg }}
      </div>

      <!-- Dual-list principal -->
      <div class="grid grid-cols-[1fr_52px_1fr] gap-3 items-start">

        <!-- Panel izquierdo: Disponibles -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-semibold text-gray-700">
                Disponibles
                <span class="ml-1 text-xs font-normal text-gray-400">({{ filteredLeft.length }})</span>
              </span>
              <button
                v-if="selectedLeft.length > 0"
                @click="selectedLeft = []"
                class="text-xs text-gray-400 hover:text-gray-600"
              >
                Limpiar ({{ selectedLeft.length }})
              </button>
            </div>
            <input
              v-model="searchLeft"
              type="text"
              placeholder="Buscar transacciones..."
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div class="overflow-y-auto" style="max-height: 60vh">
            <div v-if="filteredLeft.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">
              {{ searchLeft ? 'Sin resultados' : 'Todas las transacciones están autorizadas' }}
            </div>
            <div v-for="group in groupedLeft" :key="group.modulo">
              <!-- Cabecera de módulo -->
              <div
                class="px-3 py-2 bg-gray-50 border-y border-gray-100 flex items-center gap-2 cursor-pointer select-none hover:bg-gray-100"
                @click="expandedLeft[group.modulo] = !expandedLeft[group.modulo]"
              >
                <input
                  type="checkbox"
                  :checked="isAllSelectedLeft(group.items)"
                  :indeterminate="isSomeSelectedLeft(group.items) && !isAllSelectedLeft(group.items)"
                  class="w-3.5 h-3.5 text-purple-600 border-gray-300 rounded focus:ring-0"
                  @click.stop
                  @change="toggleModuleLeft(group.items, $event.target.checked)"
                />
                <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex-1">
                  {{ group.modulo }}
                </span>
                <span class="text-xs text-gray-400">{{ group.items.length }}</span>
                <svg
                  class="w-3.5 h-3.5 text-gray-400 transition-transform"
                  :class="expandedLeft[group.modulo] !== false ? '' : '-rotate-90'"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <!-- Items del módulo -->
              <div v-show="expandedLeft[group.modulo] !== false">
                <label
                  v-for="t in group.items"
                  :key="t.id"
                  class="flex items-start gap-2.5 px-4 py-2 border-b border-gray-50 hover:bg-purple-50 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    :value="t.id"
                    v-model="selectedLeft"
                    class="mt-0.5 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500 focus:ring-offset-0 shrink-0"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-mono text-purple-700 leading-tight">{{ t.codigo }}</div>
                    <div class="text-sm text-gray-700 leading-tight truncate">{{ t.nombre }}</div>
                  </div>
                  <span class="text-xs text-gray-400 shrink-0 pt-0.5">{{ t.tipo }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Botones centrales -->
        <div class="flex flex-col items-center gap-2 pt-14">
          <button
            @click="moverAAutorizadas"
            :disabled="selectedLeft.length === 0"
            class="relative w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all"
            :class="selectedLeft.length > 0
              ? 'border-purple-600 bg-purple-600 text-white hover:bg-purple-700 hover:border-purple-700'
              : 'border-gray-200 bg-white text-gray-300 cursor-not-allowed'"
            title="Autorizar seleccionadas"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
            </svg>
            <span
              v-if="selectedLeft.length > 0"
              class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-purple-100 text-purple-700 text-xs rounded-full flex items-center justify-center font-bold"
            >{{ selectedLeft.length }}</span>
          </button>
          <button
            @click="moverADisponibles"
            :disabled="selectedRight.length === 0"
            class="relative w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all"
            :class="selectedRight.length > 0
              ? 'border-red-500 bg-red-500 text-white hover:bg-red-600 hover:border-red-600'
              : 'border-gray-200 bg-white text-gray-300 cursor-not-allowed'"
            title="Revocar seleccionadas"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
            </svg>
            <span
              v-if="selectedRight.length > 0"
              class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-100 text-red-700 text-xs rounded-full flex items-center justify-center font-bold"
            >{{ selectedRight.length }}</span>
          </button>
        </div>

        <!-- Panel derecho: Autorizadas -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div class="px-4 py-3 bg-purple-50 border-b border-purple-100">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-semibold text-purple-700">
                Autorizadas
                <span class="ml-1 text-xs font-normal text-purple-400">({{ filteredRight.length }})</span>
              </span>
              <button
                v-if="selectedRight.length > 0"
                @click="selectedRight = []"
                class="text-xs text-purple-400 hover:text-purple-600"
              >
                Limpiar ({{ selectedRight.length }})
              </button>
            </div>
            <input
              v-model="searchRight"
              type="text"
              placeholder="Buscar autorizadas..."
              class="w-full px-3 py-1.5 text-sm border border-purple-200 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
            />
          </div>
          <div class="overflow-y-auto" style="max-height: 60vh">
            <div v-if="filteredRight.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">
              {{ searchRight ? 'Sin resultados' : 'Sin transacciones autorizadas' }}
            </div>
            <div v-for="group in groupedRight" :key="group.modulo">
              <!-- Cabecera de módulo -->
              <div
                class="px-3 py-2 bg-purple-50 border-y border-purple-100 flex items-center gap-2 cursor-pointer select-none hover:bg-purple-100"
                @click="expandedRight[group.modulo] = !expandedRight[group.modulo]"
              >
                <input
                  type="checkbox"
                  :checked="isAllSelectedRight(group.items)"
                  :indeterminate="isSomeSelectedRight(group.items) && !isAllSelectedRight(group.items)"
                  class="w-3.5 h-3.5 text-purple-600 border-purple-300 rounded focus:ring-0"
                  @click.stop
                  @change="toggleModuleRight(group.items, $event.target.checked)"
                />
                <span class="text-xs font-semibold text-purple-600 uppercase tracking-wider flex-1">
                  {{ group.modulo }}
                </span>
                <span class="text-xs text-purple-400">{{ group.items.length }}</span>
                <svg
                  class="w-3.5 h-3.5 text-purple-400 transition-transform"
                  :class="expandedRight[group.modulo] !== false ? '' : '-rotate-90'"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <!-- Items del módulo -->
              <div v-show="expandedRight[group.modulo] !== false">
                <label
                  v-for="t in group.items"
                  :key="t.id"
                  class="flex items-start gap-2.5 px-4 py-2 border-b border-purple-50 hover:bg-red-50 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    :value="t.id"
                    v-model="selectedRight"
                    class="mt-0.5 w-4 h-4 text-red-500 border-gray-300 rounded focus:ring-red-500 focus:ring-offset-0 shrink-0"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-mono text-purple-700 leading-tight">{{ t.codigo }}</div>
                    <div class="text-sm text-gray-700 leading-tight truncate">{{ t.nombre }}</div>
                  </div>
                  <span class="text-xs text-gray-400 shrink-0 pt-0.5">{{ t.tipo }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer con acciones -->
      <div class="mt-4 flex items-center justify-between">
        <button
          @click="cancelar"
          :disabled="saving"
          class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          Cancelar cambios
        </button>

        <div class="flex items-center gap-4">
          <span v-if="hasChanges" class="text-sm text-gray-500">
            <span v-if="pendingAdd.length > 0" class="text-green-600 font-medium">+{{ pendingAdd.length }}</span>
            <span v-if="pendingAdd.length > 0 && pendingRemove.length > 0" class="mx-1 text-gray-300">·</span>
            <span v-if="pendingRemove.length > 0" class="text-red-600 font-medium">-{{ pendingRemove.length }}</span>
            <span class="ml-1">cambios pendientes</span>
          </span>
          <span v-else class="text-sm text-gray-400">Sin cambios pendientes</span>
          <button
            @click="guardar"
            :disabled="!hasChanges || saving"
            class="px-5 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="saving" class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
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
  GET_ROL_CON_PERMISOS,
  GET_TRANSACCIONES_TODAS,
  ASIGNAR_TRANSACCION,
  REVOCAR_TRANSACCION,
} from '@/graphql/queries/administracion.js'

const route = useRoute()

const rol = ref(null)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const savedMsg = ref('')

const allTransacciones = ref([])
const authorizedIds = ref([])
const originalIds = ref([])
const rolTransaccionMap = ref({})  // { transaccionId → rolTransaccionId }

const selectedLeft = ref([])
const selectedRight = ref([])
const searchLeft = ref('')
const searchRight = ref('')
const expandedLeft = reactive({})
const expandedRight = reactive({})

// ─── Helpers ───────────────────────────────────────────────────────────────

function groupByModule(items) {
  const map = {}
  for (const t of items) {
    if (!map[t.modulo]) map[t.modulo] = []
    map[t.modulo].push(t)
  }
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b, 'es'))
    .map(([modulo, items]) => ({
      modulo,
      items: items.slice().sort((a, b) => a.codigo.localeCompare(b.codigo)),
    }))
}

function matchesSearch(t, q) {
  if (!q) return true
  const s = q.toLowerCase()
  return t.codigo.toLowerCase().includes(s) || t.nombre.toLowerCase().includes(s)
}

// ─── Computed ──────────────────────────────────────────────────────────────

const filteredLeft = computed(() =>
  allTransacciones.value
    .filter(t => !authorizedIds.value.includes(t.id))
    .filter(t => matchesSearch(t, searchLeft.value))
)

const filteredRight = computed(() =>
  allTransacciones.value
    .filter(t => authorizedIds.value.includes(t.id))
    .filter(t => matchesSearch(t, searchRight.value))
)

const groupedLeft = computed(() => groupByModule(filteredLeft.value))
const groupedRight = computed(() => groupByModule(filteredRight.value))

const pendingAdd = computed(() =>
  authorizedIds.value.filter(id => !originalIds.value.includes(id))
)
const pendingRemove = computed(() =>
  originalIds.value.filter(id => !authorizedIds.value.includes(id))
)
const hasChanges = computed(() => pendingAdd.value.length > 0 || pendingRemove.value.length > 0)

// ─── Auto-expand módulos al cargar ─────────────────────────────────────────

watch(groupedLeft, (groups) => {
  groups.forEach(g => {
    if (expandedLeft[g.modulo] === undefined) expandedLeft[g.modulo] = true
  })
}, { immediate: true })

watch(groupedRight, (groups) => {
  groups.forEach(g => {
    if (expandedRight[g.modulo] === undefined) expandedRight[g.modulo] = true
  })
}, { immediate: true })

// ─── Selección por módulo ──────────────────────────────────────────────────

function isAllSelectedLeft(items) {
  return items.length > 0 && items.every(t => selectedLeft.value.includes(t.id))
}
function isSomeSelectedLeft(items) {
  return items.some(t => selectedLeft.value.includes(t.id))
}
function toggleModuleLeft(items, checked) {
  if (checked) {
    items.forEach(t => { if (!selectedLeft.value.includes(t.id)) selectedLeft.value.push(t.id) })
  } else {
    selectedLeft.value = selectedLeft.value.filter(id => !items.some(t => t.id === id))
  }
}

function isAllSelectedRight(items) {
  return items.length > 0 && items.every(t => selectedRight.value.includes(t.id))
}
function isSomeSelectedRight(items) {
  return items.some(t => selectedRight.value.includes(t.id))
}
function toggleModuleRight(items, checked) {
  if (checked) {
    items.forEach(t => { if (!selectedRight.value.includes(t.id)) selectedRight.value.push(t.id) })
  } else {
    selectedRight.value = selectedRight.value.filter(id => !items.some(t => t.id === id))
  }
}

// ─── Acciones del shuttle ──────────────────────────────────────────────────

function moverAAutorizadas() {
  selectedLeft.value.forEach(id => {
    if (!authorizedIds.value.includes(id)) authorizedIds.value.push(id)
  })
  selectedLeft.value = []
}

function moverADisponibles() {
  selectedRight.value.forEach(id => {
    const idx = authorizedIds.value.indexOf(id)
    if (idx !== -1) authorizedIds.value.splice(idx, 1)
  })
  selectedRight.value = []
}

function cancelar() {
  authorizedIds.value = [...originalIds.value]
  selectedLeft.value = []
  selectedRight.value = []
}

// ─── Guardar ───────────────────────────────────────────────────────────────

async function guardar() {
  saving.value = true
  error.value = null
  savedMsg.value = ''
  try {
    const adds = pendingAdd.value
    const removes = pendingRemove.value

    await Promise.all([
      ...adds.map(id =>
        executeMutation(ASIGNAR_TRANSACCION, {
          data: { rolId: rol.value.id, transaccionId: id },
        })
      ),
      ...removes.map(id => {
        const rtId = rolTransaccionMap.value[id]
        if (!rtId) return Promise.resolve()
        return executeMutation(REVOCAR_TRANSACCION, { filter: { id: { eq: rtId } } })
      }),
    ])

    await cargar()
    savedMsg.value = `Cambios guardados: ${adds.length} añadidos, ${removes.length} revocados.`
    setTimeout(() => { savedMsg.value = '' }, 4000)
  } catch (err) {
    console.error('Error guardando permisos:', err)
    error.value = err?.response?.errors?.[0]?.message || 'Error al guardar los permisos'
  } finally {
    saving.value = false
  }
}

// ─── Carga de datos ────────────────────────────────────────────────────────

async function cargar() {
  loading.value = true
  error.value = null
  try {
    const [rolData, txData] = await Promise.all([
      executeQuery(GET_ROL_CON_PERMISOS, { id: route.params.id }),
      executeQuery(GET_TRANSACCIONES_TODAS),
    ])

    const rolRaw = rolData.roles?.[0]
    if (!rolRaw) throw new Error('Rol no encontrado')
    rol.value = rolRaw

    allTransacciones.value = txData.transacciones || []

    const map = {}
    const ids = []
    for (const rt of rolRaw.transacciones || []) {
      if (rt.transaccion) {
        map[rt.transaccion.id] = rt.id
        ids.push(rt.transaccion.id)
      }
    }
    rolTransaccionMap.value = map
    authorizedIds.value = ids
    originalIds.value = [...ids]
    selectedLeft.value = []
    selectedRight.value = []
  } catch (err) {
    console.error('Error cargando permisos:', err)
    error.value = err?.response?.errors?.[0]?.message || err.message || 'Error al cargar los datos'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
