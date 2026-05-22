<template>
  <AppLayout title="Campañas" subtitle="Gestión de campañas y actividades">

    <!-- KPI strip -->
    <section v-if="allCampanias.length" class="mb-4 bg-white border border-slate-200 rounded-xl px-5 py-3 grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-2 text-sm">
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Total</span>
        <span class="text-2xl font-bold text-slate-800 tabular-nums">{{ allCampanias.length }}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">En curso</span>
        <span class="text-2xl font-bold text-indigo-600 tabular-nums">{{ kpiEnCurso }}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Borradores</span>
        <span class="text-2xl font-bold text-amber-500 tabular-nums">{{ kpiBorradores }}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400 font-medium uppercase tracking-wide">Este año ({{ anioActual }})</span>
        <span class="text-2xl font-bold text-emerald-600 tabular-nums">{{ kpiEsteAnio }}</span>
      </div>
    </section>

    <!-- FilterBar -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar por nombre o lema…"
      :create-label="tienePermiso('CAMP_CREATE') ? 'Nueva campaña' : ''"
      create-route="/campanias/nueva"
      :fields="filterFields"
      :lazy="false"
      :loading="loading"
      class="mb-4"
    />

    <!-- Carga -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <p class="text-red-700 font-medium">Error al cargar campañas</p>
      <p class="text-red-600 text-sm mt-1">{{ error }}</p>
      <button @click="cargar" class="mt-3 text-red-600 hover:text-red-800 text-sm font-medium">Reintentar</button>
    </div>

    <template v-else>
      <!-- Sin resultados -->
      <div v-if="campaniasFiltradas.length === 0 && allCampanias.length > 0"
        class="py-12 text-center text-slate-400">
        <MagnifyingGlassIcon class="w-12 h-12 mx-auto mb-3 text-slate-300" />
        <p class="text-base font-medium text-slate-600">Sin campañas con esos filtros</p>
        <button @click="limpiarFiltros" class="mt-2 text-sm text-indigo-600 hover:text-indigo-800 font-medium">
          Limpiar filtros
        </button>
      </div>

      <!-- Sin datos en absoluto -->
      <div v-else-if="allCampanias.length === 0"
        class="py-16 text-center text-slate-400">
        <RectangleStackIcon class="w-12 h-12 mx-auto mb-3 text-slate-300" />
        <p class="text-base font-medium text-slate-600">No hay campañas todavía</p>
        <router-link v-if="tienePermiso('CAMP_CREATE')" to="/campanias/nueva"
          class="mt-3 inline-flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 font-medium">
          <PlusIcon class="w-4 h-4" /> Crear primera campaña
        </router-link>
      </div>

      <!-- Cabecera de resultados -->
      <div v-else class="space-y-4">
        <div class="flex items-center justify-between text-sm">
          <span class="text-slate-500">
            <strong class="text-slate-800">{{ campaniasFiltradas.length }}</strong>
            {{ campaniasFiltradas.length === 1 ? 'campaña' : 'campañas' }}
            <template v-if="hasFiltros"> · filtradas</template>
          </span>
          <button v-if="hasFiltros" @click="limpiarFiltros"
            class="text-indigo-600 hover:text-indigo-800 font-medium">
            Limpiar filtros
          </button>
        </div>

        <!-- Grid de tarjetas -->
        <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 xl:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="c in campaniasFiltradas"
            :key="c.id"
            class="bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer flex flex-col"
            @click="router.push(`/campanias/${c.id}`)">

            <!-- Cabecera de tarjeta -->
            <div class="px-5 pt-4 pb-3 flex items-start justify-between gap-2">
              <span
                class="inline-flex items-center px-2.5 py-0.5 text-xs font-semibold rounded-full border"
                :style="estadoBadgeStyle(c.estado)">
                {{ c.estado?.nombre ?? '—' }}
              </span>
              <span v-if="c.tipoCampania"
                class="shrink-0 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 rounded-full">
                {{ c.tipoCampania.nombre }}
              </span>
            </div>

            <!-- Cuerpo de tarjeta -->
            <div class="px-5 pb-4 flex-1 flex flex-col gap-1.5">
              <h3 class="text-sm font-semibold text-slate-900 leading-snug">{{ c.nombre }}</h3>
              <p v-if="c.lema" class="text-xs text-slate-400 italic">"{{ c.lema }}"</p>
              <p v-if="c.descripcionCorta" class="text-xs text-slate-500 line-clamp-2 mt-0.5">{{ c.descripcionCorta }}</p>

              <!-- Meta-info -->
              <div class="mt-auto pt-3 space-y-1 text-xs text-slate-500">
                <div v-if="c.responsable" class="flex items-center gap-1.5">
                  <UserIcon class="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  {{ c.responsable.nombre }} {{ c.responsable.apellido1 }}
                </div>
                <div v-if="c.fechaInicioPlan" class="flex items-center gap-1.5">
                  <CalendarIcon class="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  {{ fmtDate(c.fechaInicioPlan) }}
                  <template v-if="c.fechaFinPlan"> – {{ fmtDate(c.fechaFinPlan) }}</template>
                  <template v-else-if="c.periodicidad === 'permanente'">
                    <span class="text-sky-600 font-medium">· Permanente</span>
                  </template>
                </div>
                <div class="flex items-center gap-3">
                  <span v-if="c.agrupacion" class="flex items-center gap-1">
                    <MapPinIcon class="w-3.5 h-3.5 text-slate-400" />
                    {{ c.agrupacion.nombre }}
                  </span>
                  <span v-if="c.actividades?.length" class="flex items-center gap-1">
                    <BoltIcon class="w-3.5 h-3.5 text-slate-400" />
                    {{ c.actividades.length }} {{ c.actividades.length === 1 ? 'actividad' : 'actividades' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Pie de tarjeta -->
            <div class="px-4 py-2.5 border-t border-slate-100 flex items-center justify-between">
              <div class="flex items-center gap-1">
                <button v-if="esEliminable(c) && tienePermiso('CAMP_DELETE')"
                  @click.stop="campanaAEliminar = c"
                  class="p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
                  title="Eliminar">
                  <TrashIcon class="w-4 h-4" />
                </button>
                <router-link v-if="esEditable(c)"
                  :to="`/campanias/${c.id}/editar`"
                  class="p-1.5 text-slate-300 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                  title="Editar"
                  @click.stop>
                  <PencilSquareIcon class="w-4 h-4" />
                </router-link>
              </div>
              <router-link :to="`/campanias/${c.id}`"
                class="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
                @click.stop>
                Ver ficha <ArrowRightIcon class="w-3.5 h-3.5" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </template>

  </AppLayout>

  <!-- Modal confirmar eliminación -->
  <div v-if="campanaAEliminar" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
      <h3 class="text-base font-semibold text-slate-900">¿Eliminar campaña?</h3>
      <p class="text-sm text-slate-600">
        Se eliminará «<strong>{{ campanaAEliminar.nombre }}</strong>». Esta acción no se puede deshacer.
      </p>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
        <button @click="campanaAEliminar = null"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="eliminarCampania" :disabled="eliminando"
          class="h-9 px-5 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
          {{ eliminando ? '…' : 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  TrashIcon, PencilSquareIcon, PlusIcon, ArrowRightIcon,
  MagnifyingGlassIcon, RectangleStackIcon, UserIcon, CalendarIcon, MapPinIcon, BoltIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import { usePermisos } from '@/composables/usePermisos.js'
import { GET_CAMPANIAS, GET_TIPOS_CAMPANIA, GET_ESTADOS_CAMPANIA } from '@/graphql/queries/campanias'

const router = useRouter()
const { tienePermiso } = usePermisos()

const ELIMINAR_CAMPANIA = `
  mutation EliminarCampania($id: UUID!) {
    eliminarCampanias(filter: { id: { eq: $id } }) { id }
  }
`

// ── Estado ────────────────────────────────────────────────────────────────────
const allCampanias    = ref([])
const tiposCampania   = ref([])
const estadosCampania = ref([])
const loading         = ref(false)
const error           = ref(null)
const campanaAEliminar = ref(null)
const eliminando       = ref(false)

const searchQuery = ref('')
const filters = ref({ estados: [], tipos: [], anios: [] })

// ── KPIs globales ─────────────────────────────────────────────────────────────
const anioActual = new Date().getFullYear()

const kpiEnCurso = computed(() =>
  allCampanias.value.filter(c => {
    const n = c.estado?.nombre?.toLowerCase() ?? ''
    return n.includes('curso') || n.includes('ejecuc') || n.includes('activ')
  }).length
)
const kpiBorradores = computed(() =>
  allCampanias.value.filter(c => c.estado?.nombre?.toLowerCase().includes('borrador')).length
)
const kpiEsteAnio = computed(() =>
  allCampanias.value.filter(c => {
    if (!c.fechaInicioPlan) return false
    return new Date(c.fechaInicioPlan).getFullYear() === anioActual
  }).length
)

// ── Catálogos para filtros ─────────────────────────────────────────────────────
const aniosDisponibles = computed(() => {
  const years = new Set()
  allCampanias.value.forEach(c => {
    if (c.fechaInicioPlan) years.add(new Date(c.fechaInicioPlan).getFullYear())
    if (c.fechaFinPlan)    years.add(new Date(c.fechaFinPlan).getFullYear())
  })
  if (!years.size) years.add(anioActual)
  return [...years].sort((a, b) => b - a)
})

const filterFields = computed(() => [
  {
    key: 'estados', label: 'Estado', type: 'multiselect', allLabel: 'Todos los estados',
    options: [...estadosCampania.value]
      .sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
      .map(e => ({ value: e.id, label: e.nombre })),
  },
  {
    key: 'tipos', label: 'Tipo', type: 'multiselect', allLabel: 'Todos los tipos',
    options: [...tiposCampania.value]
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
      .map(t => ({ value: t.id, label: t.nombre })),
  },
  {
    key: 'anios', label: 'Año', type: 'multiselect', allLabel: 'Todos los años',
    options: aniosDisponibles.value.map(y => ({ value: y, label: String(y) })),
  },
])

// ── Filtrado ──────────────────────────────────────────────────────────────────
const hasFiltros = computed(() =>
  searchQuery.value.trim() ||
  filters.value.estados.length ||
  filters.value.tipos.length ||
  filters.value.anios.length
)

const campaniasFiltradas = computed(() => {
  let list = allCampanias.value

  const q = searchQuery.value.trim().toLowerCase()
  if (q) list = list.filter(c =>
    c.nombre?.toLowerCase().includes(q) ||
    c.lema?.toLowerCase().includes(q) ||
    c.descripcionCorta?.toLowerCase().includes(q)
  )

  if (filters.value.estados.length)
    list = list.filter(c => c.estado && filters.value.estados.includes(c.estado.id))

  if (filters.value.tipos.length)
    list = list.filter(c => c.tipoCampania && filters.value.tipos.includes(c.tipoCampania.id))

  if (filters.value.anios.length) {
    list = list.filter(c => {
      const ini = c.fechaInicioPlan ? new Date(c.fechaInicioPlan).getFullYear() : null
      const fin = c.fechaFinPlan    ? new Date(c.fechaFinPlan).getFullYear()    : null
      return filters.value.anios.some(y => {
        if (ini && fin) return ini <= y && fin >= y
        if (ini) return ini === y
        if (fin) return fin === y
        return false
      })
    })
  }

  return list
})

// ── Helpers ───────────────────────────────────────────────────────────────────
const esEditable   = (c) => !['finaliz', 'cancelad'].some(k => c.estado?.nombre?.toLowerCase().includes(k))
const esEliminable = (c) =>  c.estado?.nombre?.toLowerCase().includes('borrador')

function estadoBadgeStyle(estado) {
  if (!estado?.color) return {}
  const hex = estado.color.replace('#', '')
  const r = parseInt(hex.slice(0, 2), 16)
  const g = parseInt(hex.slice(2, 4), 16)
  const b = parseInt(hex.slice(4, 6), 16)
  return {
    backgroundColor: `rgba(${r},${g},${b},0.12)`,
    borderColor:     `rgba(${r},${g},${b},0.35)`,
    color:           estado.color,
  }
}

function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function limpiarFiltros() {
  searchQuery.value = ''
  filters.value = { estados: [], tipos: [], anios: [] }
}

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargar() {
  loading.value = true
  error.value = null
  try {
    const [rCamp, rTipos, rEstados] = await Promise.allSettled([
      executeQuery(GET_CAMPANIAS),
      executeQuery(GET_TIPOS_CAMPANIA),
      executeQuery(GET_ESTADOS_CAMPANIA),
    ])
    if (rCamp.status === 'fulfilled')    allCampanias.value    = rCamp.value.campanias || []
    if (rTipos.status === 'fulfilled')   tiposCampania.value   = (rTipos.value.tiposCampania || []).filter(t => t.activo)
    if (rEstados.status === 'fulfilled') estadosCampania.value = (rEstados.value.estadosCampania || []).filter(e => e.activo)
  } catch (e) {
    error.value = e?.message || 'Error al cargar'
  } finally {
    loading.value = false
  }
}

async function eliminarCampania() {
  if (!campanaAEliminar.value) return
  eliminando.value = true
  try {
    await executeMutation(ELIMINAR_CAMPANIA, { id: campanaAEliminar.value.id })
    allCampanias.value = allCampanias.value.filter(c => c.id !== campanaAEliminar.value.id)
    campanaAEliminar.value = null
  } catch (e) {
    console.error('Error eliminando campaña:', e)
  } finally {
    eliminando.value = false
  }
}

onMounted(cargar)
</script>
