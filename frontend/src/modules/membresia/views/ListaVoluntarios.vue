<template>
  <AppLayout title="Voluntarios" subtitle="Gestión del voluntariado de Europa Laica">
    <!-- Resumen -->
    <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center mr-3">
            <span class="text-lg">❤️</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total voluntarios</p>
            <p class="text-xl font-bold text-purple-600">{{ resumen.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center mr-3">
            <span class="text-lg">✅</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Disponibles</p>
            <p class="text-xl font-bold text-green-600">{{ resumen.disponibles }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
            <span class="text-lg">🚩</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">En campaña activa</p>
            <p class="text-xl font-bold text-blue-600">{{ resumen.enCampania }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <FilterBar
      v-model="filters"
      v-model:search="searchQuery"
      search-placeholder="Buscar voluntarios…"
      :fields="filterFields"
      :lazy="true"
      :loading="loading"
      class="mb-6"
      @apply="aplicarFiltros"
    />

    <!-- Loading -->
    <EstadoCarga v-if="loading" mensaje="Cargando voluntarios..." />

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <span class="text-red-400 mr-3">⚠️</span>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al cargar voluntarios</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Lista de voluntarios -->
    <div v-else class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-if="!filtersApplied" class="col-span-full bg-white rounded-lg shadow">
        <EstadoPendiente />
      </div>
      <div v-else-if="voluntariosFiltrados.length === 0" class="col-span-full text-center py-12 bg-white rounded-lg shadow">
        <span class="text-4xl">❤️</span>
        <h3 class="text-sm font-medium text-gray-900 mt-4">No hay voluntarios</h3>
        <p class="text-sm text-gray-500 mt-1">Prueba con otros filtros.</p>
      </div>

      <div
        v-for="v in voluntariosFiltrados"
        :key="v.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center">
              <div class="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                <span class="text-lg font-medium text-purple-700">{{ iniciales(v) }}</span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ nombreCompleto(v) }}</h3>
                <p v-if="v.profesion" class="text-sm text-gray-500">{{ v.profesion }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span v-if="v.disponibilidad" :class="getDisponibilidadClass(v.disponibilidad)">
                {{ v.disponibilidad }}
              </span>
              <button v-if="puedeGestionar" @click="abrirEdit(v)"
                class="text-slate-400 hover:text-indigo-600" title="Editar voluntariado">
                <PencilSquareIcon class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div class="space-y-2 text-sm text-gray-600 mb-4">
            <div v-if="v.email" class="flex items-center">
              <span class="mr-2">📧</span>
              <span>{{ v.email }}</span>
            </div>
            <div v-if="v.telefono" class="flex items-center">
              <span class="mr-2">📱</span>
              <span>{{ v.telefono }}</span>
            </div>
            <div v-if="v.horasDisponiblesSemana" class="flex items-center">
              <span class="mr-2">⏰</span>
              <span>{{ v.horasDisponiblesSemana }} h/semana disponibles</span>
            </div>
          </div>

          <div v-if="v.intereses" class="mb-4">
            <p class="text-xs text-gray-500 mb-1">Intereses:</p>
            <p class="text-sm text-gray-700">{{ v.intereses }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: editar voluntariado por delegación -->
    <div v-if="modalEdit.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 space-y-5">
        <h3 class="text-lg font-semibold text-slate-900">
          Voluntariado — {{ modalEdit.voluntario ? nombreCompleto(modalEdit.voluntario) : '' }}
        </h3>

        <!-- Perfil -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Disponibilidad</label>
            <select v-model="modalEdit.form.disponibilidad" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
              <option value="">—</option>
              <option value="DISPONIBLE">Disponible</option>
              <option value="OCUPADO">En campaña</option>
              <option value="INACTIVO">Inactivo</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Horas/semana</label>
            <input v-model.number="modalEdit.form.horasDisponiblesSemana" type="number" min="0"
              class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-slate-700 mb-1">Profesión</label>
            <input v-model="modalEdit.form.profesion" type="text"
              class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-slate-700 mb-1">Intereses</label>
            <textarea v-model="modalEdit.form.intereses" rows="2"
              class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"></textarea>
          </div>
          <label class="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" v-model="modalEdit.form.puedeConducir" class="rounded border-slate-300 text-indigo-600" />
            Puede conducir
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" v-model="modalEdit.form.vehiculoPropio" class="rounded border-slate-300 text-indigo-600" />
            Vehículo propio
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" v-model="modalEdit.form.disponibilidadViajar" class="rounded border-slate-300 text-indigo-600" />
            Disponible para viajar
          </label>
        </div>

        <!-- Habilidades -->
        <div class="border-t border-slate-100 pt-4">
          <p class="text-sm font-medium text-slate-700 mb-2">Habilidades</p>
          <div v-if="modalEdit.habilidades.length" class="flex flex-wrap gap-2 mb-3">
            <span v-for="h in modalEdit.habilidades" :key="h.id"
              class="inline-flex items-center gap-1 text-xs bg-indigo-50 text-indigo-700 rounded-full pl-3 pr-1 py-1">
              {{ nombreHabilidad(h.habilidadId) }}<template v-if="h.nivelId"> · {{ nombreNivel(h.nivelId) }}</template>
              <button @click="quitarHab(h)" class="hover:text-red-600 p-0.5" title="Quitar">
                <XMarkIcon class="w-3.5 h-3.5" />
              </button>
            </span>
          </div>
          <p v-else class="text-xs text-slate-400 mb-3">Sin habilidades asignadas.</p>
          <div class="flex flex-wrap items-end gap-2">
            <select v-model="modalEdit.nuevaHab" class="h-9 px-2 text-sm border border-slate-300 rounded-lg bg-white">
              <option value="">Habilidad…</option>
              <option v-for="hc in habilidadesDisponibles" :key="hc.id" :value="hc.id">{{ hc.nombre }}</option>
            </select>
            <select v-model="modalEdit.nuevoNivel" class="h-9 px-2 text-sm border border-slate-300 rounded-lg bg-white">
              <option value="">Nivel (opc.)</option>
              <option v-for="n in nivelesCat" :key="n.id" :value="n.id">{{ n.nombre }}</option>
            </select>
            <button @click="anadirHab" :disabled="!modalEdit.nuevaHab"
              class="h-9 px-3 text-sm font-medium rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 disabled:opacity-50">
              Añadir
            </button>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <button @click="modalEdit.visible = false" class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cerrar</button>
          <button @click="guardarPerfil" :disabled="modalEdit.guardando"
            class="h-9 px-5 text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
            {{ modalEdit.guardando ? 'Guardando…' : 'Guardar perfil' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_VOLUNTARIOS, GET_CATALOGO_HABILIDADES, GET_HABILIDADES_MIEMBRO,
  GESTIONAR_PERFIL_VOLUNTARIO, ASIGNAR_HABILIDAD_VOLUNTARIO, QUITAR_HABILIDAD_VOLUNTARIO,
} from '@/graphql/queries/voluntariado.js'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import EstadoPendiente from '@/components/common/EstadoPendiente.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { useToast } from '@/composables/useToast'
import { PencilSquareIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const { tienePermiso } = usePermisos()
const toast = useToast()
const puedeGestionar = computed(() => tienePermiso('MEMBRESIA_VOLUNTARIO_GESTIONAR'))

const loading = ref(false)
const error = ref('')
const voluntarios = ref([])
const searchQuery = ref('')
const filtersApplied = ref(false)
const filters = ref({ disponibilidad: '', activo: '' })

const filterFields = [
  {
    key: 'disponibilidad', label: 'Disponibilidad', type: 'select', allLabel: 'Cualquier disponibilidad',
    options: [
      { value: 'DISPONIBLE', label: 'Disponible' },
      { value: 'OCUPADO',    label: 'En campaña' },
      { value: 'INACTIVO',   label: 'Inactivo' },
    ],
  },
  {
    key: 'activo', label: 'Estado', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }],
    isActive: (v) => v !== '',
  },
]

const resumen = computed(() => ({
  total: voluntarios.value.length,
  disponibles: voluntarios.value.filter(v => v.disponibilidad === 'DISPONIBLE').length,
  enCampania: voluntarios.value.filter(v => v.disponibilidad === 'OCUPADO').length,
}))

const voluntariosFiltrados = computed(() => {
  let result = voluntarios.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(v =>
      v.nombre?.toLowerCase().includes(q) ||
      v.apellido1?.toLowerCase().includes(q) ||
      v.email?.toLowerCase().includes(q)
    )
  }
  if (filters.value.disponibilidad) {
    result = result.filter(v => v.disponibilidad === filters.value.disponibilidad)
  }
  if (filters.value.activo !== '') {
    result = result.filter(v => String(v.activo) === filters.value.activo)
  }
  return result
})

function iniciales(v) {
  return `${v.nombre?.[0] ?? ''}${v.apellido1?.[0] ?? ''}`.toUpperCase()
}

function nombreCompleto(v) {
  return [v.nombre, v.apellido1, v.apellido2].filter(Boolean).join(' ')
}

function getDisponibilidadClass(d) {
  const classes = {
    DISPONIBLE: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
    OCUPADO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    INACTIVO: 'inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
  }
  return classes[d] || classes.INACTIVO
}

// ── Edición por delegación (gestionarPerfilVoluntario + habilidades) ──
const habilidadesCat = ref([])
const nivelesCat = ref([])
const modalEdit = ref({ visible: false, voluntario: null, form: {}, habilidades: [], guardando: false, nuevaHab: '', nuevoNivel: '' })

const nombreHabilidad = (id) => habilidadesCat.value.find(h => h.id === id)?.nombre || '—'
const nombreNivel = (id) => nivelesCat.value.find(n => n.id === id)?.nombre || ''
const habilidadesDisponibles = computed(() =>
  habilidadesCat.value.filter(h => !modalEdit.value.habilidades.some(mh => mh.habilidadId === h.id))
)

async function cargarCatalogoHabilidades() {
  try {
    const d = await executeQuery(GET_CATALOGO_HABILIDADES)
    habilidadesCat.value = d.habilidades || []
    nivelesCat.value = (d.nivelesHabilidad || []).slice().sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0))
  } catch { /* silencioso */ }
}

async function abrirEdit(v) {
  if (!habilidadesCat.value.length) await cargarCatalogoHabilidades()
  modalEdit.value = {
    visible: true, voluntario: v, guardando: false, nuevaHab: '', nuevoNivel: '',
    habilidades: [],
    form: {
      disponibilidad: v.disponibilidad || '',
      horasDisponiblesSemana: v.horasDisponiblesSemana ?? null,
      profesion: v.profesion || '',
      intereses: v.intereses || '',
      puedeConducir: !!v.puedeConducir,
      vehiculoPropio: !!v.vehiculoPropio,
      disponibilidadViajar: !!v.disponibilidadViajar,
    },
  }
  try {
    const d = await executeQuery(GET_HABILIDADES_MIEMBRO, { id: v.id })
    modalEdit.value.habilidades = d.miembrosHabilidades || []
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error cargando habilidades')
  }
}

async function guardarPerfil() {
  modalEdit.value.guardando = true
  try {
    await executeMutation(GESTIONAR_PERFIL_VOLUNTARIO, {
      data: { miembroId: modalEdit.value.voluntario.id, ...modalEdit.value.form },
    })
    toast.success('Perfil de voluntariado actualizado')
    modalEdit.value.visible = false
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error guardando el perfil')
  } finally {
    modalEdit.value.guardando = false
  }
}

async function anadirHab() {
  if (!modalEdit.value.nuevaHab) return
  try {
    await executeMutation(ASIGNAR_HABILIDAD_VOLUNTARIO, {
      miembroId: modalEdit.value.voluntario.id,
      habilidadId: modalEdit.value.nuevaHab,
      nivelId: modalEdit.value.nuevoNivel || null,
    })
    const d = await executeQuery(GET_HABILIDADES_MIEMBRO, { id: modalEdit.value.voluntario.id })
    modalEdit.value.habilidades = d.miembrosHabilidades || []
    modalEdit.value.nuevaHab = ''
    modalEdit.value.nuevoNivel = ''
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error asignando habilidad')
  }
}

async function quitarHab(h) {
  try {
    await executeMutation(QUITAR_HABILIDAD_VOLUNTARIO, {
      miembroId: modalEdit.value.voluntario.id, habilidadId: h.habilidadId,
    })
    modalEdit.value.habilidades = modalEdit.value.habilidades.filter(x => x.id !== h.id)
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error quitando habilidad')
  }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const data = await executeQuery(GET_VOLUNTARIOS)
    voluntarios.value = data.voluntariosEnAmbito || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando voluntarios'
  } finally {
    loading.value = false
  }
}

async function aplicarFiltros() {
  await cargar()
  filtersApplied.value = true
}

onMounted(() => {})
</script>
