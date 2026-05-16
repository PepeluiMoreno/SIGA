<template>
  <AppLayout title="Plantillas de campaña" subtitle="Configura las plantillas que pre-rellenan metas, presupuestos y actividades al crear una campaña">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar plantilla…"
      create-label="Nueva plantilla"
      :fields="camposFiltro"
      :lazy="false"
      :loading="cargando"
      :count-text="countText"
      @create="abrirModalCrear"
      class="mb-4"
    />

    <EstadoCarga v-if="cargando" mensaje="Cargando plantillas…" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-sm font-medium text-red-800">Error al cargar plantillas</p>
      <p class="text-sm text-red-700 mt-1">{{ error }}</p>
      <button @click="cargar" class="mt-2 text-sm text-red-600 hover:text-red-800 font-medium">Reintentar</button>
    </div>

    <div v-else class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div v-if="!plantillasFiltradas.length" class="py-16 text-center text-slate-400 text-sm">
        Ninguna plantilla coincide con los filtros.
      </div>
      <table v-else class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Tipo de campaña</th>
            <th class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Nombre</th>
            <th class="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Metas</th>
            <th class="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Actividades</th>
            <th class="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Activa</th>
            <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="p in plantillasFiltradas" :key="p.id" class="hover:bg-slate-50/60 transition-colors">
            <td class="px-5 py-3 text-sm text-slate-700">{{ p.tipoCampania?.nombre || '—' }}</td>
            <td class="px-5 py-3 text-sm font-medium text-slate-900">{{ p.nombre }}</td>
            <td class="px-5 py-3 text-sm text-slate-600 text-center">{{ p.metas?.length ?? 0 }}</td>
            <td class="px-5 py-3 text-sm text-slate-600 text-center">{{ p.actividades?.length ?? 0 }}</td>
            <td class="px-5 py-3 text-center">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="p.activo ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'">
                {{ p.activo ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <router-link :to="`/parametrizacion/plantillas-campania/${p.id}`"
                class="inline-flex items-center gap-1 h-8 px-3 text-xs font-medium text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                <PencilSquareIcon class="w-3.5 h-3.5" /> Editar
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal nueva plantilla -->
    <div v-if="modal.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h3 class="text-base font-semibold text-slate-900">Nueva plantilla de campaña</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">
              Tipo de campaña <span class="text-red-400">*</span>
            </label>
            <select v-model="modal.tipoCampaniaId" :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="t in tiposDisponibles" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
            <p v-if="!tiposDisponibles.length" class="text-xs text-amber-600 mt-1">
              Todos los tipos de campaña ya tienen plantilla asignada.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Nombre <span class="text-red-400">*</span></label>
            <input v-model="modal.nombre" type="text" :class="inp" placeholder="Nombre de la plantilla" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Descripción</label>
            <textarea v-model="modal.descripcion" rows="2" :class="inp" placeholder="Descripción opcional…"></textarea>
          </div>
        </div>
        <p v-if="modal.error" class="text-xs text-red-600">{{ modal.error }}</p>
        <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <button @click="modal.visible = false"
            class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
          <button @click="crearPlantilla" :disabled="modal.submitting || !modal.nombre || !modal.tipoCampaniaId"
            class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
            {{ modal.submitting ? '…' : 'Crear plantilla' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PencilSquareIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_ALL_PLANTILLAS, CREAR_PLANTILLA, GET_TIPOS_CAMPANIA } from '@/modules/comunicaciones/graphql/queries.js'

const router = useRouter()
const cargando      = ref(false)
const error         = ref(null)
const plantillas    = ref([])
const tiposCampania = ref([])

const busqueda = ref('')
const filtros  = ref({ tipoCampania: '', soloActivas: false })

const inp = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg ' +
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
            'bg-white placeholder:text-slate-300'

const modal = ref({ visible: false, tipoCampaniaId: '', nombre: '', descripcion: '', submitting: false, error: null })

const plantillasFiltradas = computed(() => {
  let lista = plantillas.value
  if (filtros.value.tipoCampania) {
    lista = lista.filter(p => p.tipoCampania?.id === filtros.value.tipoCampania)
  }
  if (filtros.value.soloActivas) {
    lista = lista.filter(p => p.activo)
  }
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    lista = lista.filter(p =>
      p.nombre?.toLowerCase().includes(q) ||
      p.tipoCampania?.nombre?.toLowerCase().includes(q)
    )
  }
  return lista
})

const tiposDisponibles = computed(() => {
  const usados = new Set(plantillas.value.map(p => p.tipoCampania?.id).filter(Boolean))
  return tiposCampania.value.filter(t => t.activo && !usados.has(t.id))
})

const camposFiltro = computed(() => [
  {
    key: 'tipoCampania',
    type: 'select',
    label: 'Tipo de campaña',
    allLabel: 'Todos los tipos',
    options: tiposCampania.value.map(t => ({ value: t.id, label: t.nombre })),
  },
  {
    key: 'soloActivas',
    type: 'toggle',
    label: 'Solo activas',
  },
])

const countText = computed(() => {
  const n = plantillasFiltradas.value.length
  return `${n} plantilla${n !== 1 ? 's' : ''}`
})

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const [dataP, dataT] = await Promise.all([
      graphqlClient.request(GET_ALL_PLANTILLAS),
      graphqlClient.request(GET_TIPOS_CAMPANIA),
    ])
    plantillas.value    = dataP.plantillasCampania ?? []
    tiposCampania.value = dataT.tiposCampania ?? []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al cargar'
  } finally {
    cargando.value = false
  }
}

function abrirModalCrear() {
  modal.value = { visible: true, tipoCampaniaId: '', nombre: '', descripcion: '', submitting: false, error: null }
}

async function crearPlantilla() {
  modal.value.submitting = true
  modal.value.error = null
  try {
    const data = await graphqlClient.request(CREAR_PLANTILLA, {
      data: {
        tipoCampaniaId: modal.value.tipoCampaniaId,
        nombre: modal.value.nombre.trim(),
        descripcion: modal.value.descripcion || null,
        activo: true,
      },
    })
    const id = data.crearPlantilla.id
    modal.value.visible = false
    router.push(`/parametrizacion/plantillas-campania/${id}`)
  } catch (e) {
    modal.value.error = e?.response?.errors?.[0]?.message || 'Error al crear'
  } finally {
    modal.value.submitting = false
  }
}

onMounted(cargar)
</script>
