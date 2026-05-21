<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p class="text-sm text-gray-500 max-w-2xl">
        Las reglas clasifican automáticamente los apuntes según su concepto. Cuando el
        concepto de un movimiento coincide con el patrón de una regla, se le asigna su
        categoría sin intervención. Se aplican en orden de prioridad.
      </p>
      <button v-if="puedeGestionar" @click="abrirNueva"
        class="px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 flex-shrink-0 ml-4">
        + Nueva regla
      </button>
    </div>

    <LoadSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
      {{ error }} <button @click="cargar" class="ml-2 underline">Reintentar</button>
    </div>

    <div v-else-if="reglas.length === 0"
      class="text-center text-gray-400 py-10 border border-dashed border-gray-200 rounded-lg text-sm">
      No hay reglas de clasificación. Crea una para que los movimientos recurrentes
      se clasifiquen solos.
    </div>

    <div v-else class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
      <div v-for="r in reglas" :key="r.id"
        class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
        :class="r.activa ? '' : 'opacity-50'">
        <span class="text-xs font-mono text-gray-400 w-6 text-center flex-shrink-0">{{ r.orden }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">{{ etiquetaCoincidencia(r.tipoCoincidencia) }}</span>
            <span class="font-mono text-sm text-gray-900">«{{ r.patron }}»</span>
            <span class="text-gray-400 text-xs">→</span>
            <span class="text-sm font-medium" :style="{ color: colorCategoria(r.categoriaFiscalId) }">
              {{ nombreCategoria(r.categoriaFiscalId) }}
            </span>
            <span v-if="r.tipoApunte" class="text-xs px-1.5 py-0.5 rounded"
              :class="r.tipoApunte === 'INGRESO' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">
              solo {{ r.tipoApunte === 'INGRESO' ? 'ingresos' : 'gastos' }}
            </span>
            <span v-if="!r.activa" class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">inactiva</span>
          </div>
          <p v-if="r.descripcion" class="text-xs text-gray-400 mt-0.5">{{ r.descripcion }}</p>
        </div>
        <div v-if="puedeGestionar" class="flex items-center gap-1 flex-shrink-0">
          <button @click="abrirEditar(r)" class="text-xs px-2 py-1 rounded text-gray-600 hover:bg-gray-100">Editar</button>
          <button @click="confirmarEliminar(r)" class="text-xs px-2 py-1 rounded text-red-600 hover:bg-red-50">Eliminar</button>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar regla -->
    <Teleport to="body">
      <div v-if="modal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modal = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">{{ modoEdicion ? 'Editar regla' : 'Nueva regla' }}</h2>
            <button @click="modal = false" class="p-1 text-gray-400 hover:text-gray-600 rounded">✕</button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Patrón a buscar <span class="text-red-500">*</span></label>
              <input type="text" v-model="form.patron" placeholder="Endesa"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 font-mono" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Coincidencia</label>
                <select v-model="form.tipoCoincidencia"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                  <option value="CONTIENE">Contiene</option>
                  <option value="EMPIEZA_POR">Empieza por</option>
                  <option value="EXACTO">Exacto</option>
                  <option value="REGEX">Expresión regular</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Aplica a</label>
                <select v-model="form.tipoApunte"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                  <option :value="null">Ingresos y gastos</option>
                  <option value="INGRESO">Solo ingresos</option>
                  <option value="GASTO">Solo gastos</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoría a asignar <span class="text-red-500">*</span></label>
              <select v-model="form.categoriaFiscalId"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                <option :value="null">Selecciona…</option>
                <optgroup label="Ingresos">
                  <option v-for="c in categoriasIngreso" :key="c.id" :value="c.id">{{ c.nombre }}</option>
                </optgroup>
                <optgroup label="Gastos">
                  <option v-for="c in categoriasGasto" :key="c.id" :value="c.id">{{ c.nombre }}</option>
                </optgroup>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Prioridad (orden)</label>
                <input type="number" v-model.number="form.orden" min="1"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div v-if="modoEdicion" class="flex items-end pb-1">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input type="checkbox" v-model="form.activa" class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
                  <span class="text-sm text-gray-700">Activa</span>
                </label>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <input type="text" v-model="form.descripcion"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <ErrorAlert v-if="errorModal" :message="errorModal" />
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modal = false" class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="guardar" :disabled="guardando" class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
              {{ guardando ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal eliminar -->
    <Teleport to="body">
      <div v-if="modalEliminar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalEliminar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">¿Eliminar esta regla?</h2>
          <p class="text-sm text-gray-600">Los apuntes ya clasificados con ella no cambian; solo deja de aplicarse a los nuevos.</p>
          <div class="flex justify-end gap-3">
            <button @click="modalEliminar = false" class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="ejecutarEliminar" :disabled="eliminando" class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
              {{ eliminando ? 'Eliminando…' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { usePermisos } from '@/composables/usePermisos.js'
import {
  GET_REGLAS_CATEGORIZACION, CREAR_REGLA_CATEGORIZACION,
  ACTUALIZAR_REGLA_CATEGORIZACION, ELIMINAR_REGLA_CATEGORIZACION,
  GET_CATEGORIAS_FISCALES,
} from '@/graphql/queries/categorias_fiscales.js'

const { query, mutation } = useGraphQL()
const { tienePermiso } = usePermisos()
const puedeGestionar = computed(() => tienePermiso('ECO_ESTRUCTURA_CONTABLE_GESTIONAR'))

const loading = ref(false)
const error = ref('')
const reglas = ref([])
const categorias = ref([])

const modal = ref(false)
const modalEliminar = ref(false)
const modoEdicion = ref(false)
const guardando = ref(false)
const eliminando = ref(false)
const errorModal = ref('')
const reglaActiva = ref(null)

const form = ref({
  id: null, patron: '', tipoCoincidencia: 'CONTIENE', tipoApunte: null,
  categoriaFiscalId: null, orden: 10, descripcion: '', activa: true,
})

const categoriasIngreso = computed(() => categorias.value.filter(c => c.tipo === 'INGRESO'))
const categoriasGasto = computed(() => categorias.value.filter(c => c.tipo === 'GASTO'))

const nombreCategoria = (id) => categorias.value.find(c => c.id === id)?.nombre ?? '—'
const colorCategoria = (id) => categorias.value.find(c => c.id === id)?.color ?? '#6b7280'

const COINCIDENCIAS = {
  CONTIENE: 'contiene', EMPIEZA_POR: 'empieza por', EXACTO: 'exacto', REGEX: 'regex',
}
const etiquetaCoincidencia = (c) => COINCIDENCIAS[c] ?? c

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const [dataReglas, dataCat] = await Promise.all([
      query(GET_REGLAS_CATEGORIZACION, { activasSolo: false }),
      query(GET_CATEGORIAS_FISCALES, { activasSolo: true }),
    ])
    reglas.value = dataReglas?.reglasCategorizacion ?? []
    categorias.value = dataCat?.categoriasFiscales ?? []
  } catch (e) {
    error.value = e?.message ?? 'Error al cargar las reglas'
  } finally {
    loading.value = false
  }
}

const abrirNueva = () => {
  modoEdicion.value = false
  form.value = { id: null, patron: '', tipoCoincidencia: 'CONTIENE', tipoApunte: null, categoriaFiscalId: null, orden: 10, descripcion: '', activa: true }
  errorModal.value = ''
  modal.value = true
}

const abrirEditar = (r) => {
  modoEdicion.value = true
  form.value = {
    id: r.id, patron: r.patron, tipoCoincidencia: r.tipoCoincidencia,
    tipoApunte: r.tipoApunte, categoriaFiscalId: r.categoriaFiscalId,
    orden: r.orden, descripcion: r.descripcion ?? '', activa: r.activa,
  }
  errorModal.value = ''
  modal.value = true
}

const guardar = async () => {
  errorModal.value = ''
  if (!form.value.patron?.trim()) { errorModal.value = 'El patrón es obligatorio'; return }
  if (!form.value.categoriaFiscalId) { errorModal.value = 'Selecciona la categoría a asignar'; return }
  guardando.value = true
  try {
    if (modoEdicion.value) {
      await mutation(ACTUALIZAR_REGLA_CATEGORIZACION, {
        data: {
          id: form.value.id, patron: form.value.patron.trim(),
          tipoCoincidencia: form.value.tipoCoincidencia, tipoApunte: form.value.tipoApunte,
          categoriaFiscalId: form.value.categoriaFiscalId, orden: form.value.orden,
          descripcion: form.value.descripcion || null, activa: form.value.activa,
        },
      })
    } else {
      await mutation(CREAR_REGLA_CATEGORIZACION, {
        data: {
          patron: form.value.patron.trim(), tipoCoincidencia: form.value.tipoCoincidencia,
          tipoApunte: form.value.tipoApunte, categoriaFiscalId: form.value.categoriaFiscalId,
          orden: form.value.orden, descripcion: form.value.descripcion || null,
        },
      })
    }
    modal.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e?.message ?? 'Error al guardar la regla'
  } finally {
    guardando.value = false
  }
}

const confirmarEliminar = (r) => { reglaActiva.value = r; modalEliminar.value = true }

const ejecutarEliminar = async () => {
  eliminando.value = true
  try {
    await mutation(ELIMINAR_REGLA_CATEGORIZACION, { reglaId: reglaActiva.value.id })
    modalEliminar.value = false
    await cargar()
  } catch (e) {
    error.value = e?.message ?? 'No se pudo eliminar'
  } finally {
    eliminando.value = false
  }
}

onMounted(cargar)
</script>
