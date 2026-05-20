<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p class="text-sm text-gray-500 max-w-2xl">
        Las categorías fiscales clasifican los ingresos y gastos de la organización
        y determinan su tratamiento en los modelos tributarios. Equivalen al plan de
        cuentas en la contabilidad por partida doble.
      </p>
      <button v-if="puedeGestionar" @click="abrirNueva"
        class="px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 flex-shrink-0 ml-4">
        + Nueva categoría
      </button>
    </div>

    <LoadSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
      {{ error }}
      <button @click="cargar" class="ml-2 underline">Reintentar</button>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section v-for="grupo in grupos" :key="grupo.tipo">
          <h3 class="text-sm font-semibold mb-2 flex items-center gap-2"
            :class="grupo.tipo === 'INGRESO' ? 'text-green-700' : 'text-red-700'">
            <span>{{ grupo.tipo === 'INGRESO' ? '↗' : '↘' }}</span>
            {{ grupo.tipo === 'INGRESO' ? 'Ingresos' : 'Gastos' }}
            <span class="text-xs font-normal text-gray-400">({{ grupo.items.length }})</span>
          </h3>

          <div v-if="grupo.items.length === 0"
            class="text-center text-gray-400 py-8 border border-dashed border-gray-200 rounded-lg text-sm">
            No hay categorías de {{ grupo.tipo === 'INGRESO' ? 'ingreso' : 'gasto' }}.
          </div>

          <div v-else class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            <div v-for="c in grupo.items" :key="c.id"
              class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
              :class="c.activa ? '' : 'opacity-50'">
              <span class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                :style="{ backgroundColor: c.color || '#cbd5e1' }"></span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-medium text-gray-900 text-sm">{{ c.nombre }}</span>
                  <span class="text-xs text-gray-400 font-mono">{{ c.codigo }}</span>
                  <span v-if="!c.activa" class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">inactiva</span>
                </div>
                <div class="flex flex-wrap gap-1.5 mt-1">
                  <span v-if="c.computaModelo182"
                    class="text-xs px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100">Modelo 182</span>
                  <span v-if="c.computaModelo347"
                    class="text-xs px-1.5 py-0.5 rounded bg-purple-50 text-purple-600 border border-purple-100">Modelo 347</span>
                  <span v-if="c.casillaModelo"
                    class="text-xs px-1.5 py-0.5 rounded bg-gray-50 text-gray-500 border border-gray-100">Casilla {{ c.casillaModelo }}</span>
                </div>
              </div>
              <div v-if="puedeGestionar" class="flex items-center gap-1 flex-shrink-0">
                <button @click="abrirEditar(c)"
                  class="text-xs px-2 py-1 rounded text-gray-600 hover:bg-gray-100 transition-colors">Editar</button>
                <button @click="confirmarEliminar(c)"
                  class="text-xs px-2 py-1 rounded text-red-600 hover:bg-red-50 transition-colors">Eliminar</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>

    <!-- Modal crear/editar -->
    <Teleport to="body">
      <div v-if="modal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modal = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div class="px-6 pt-6 pb-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">
              {{ modoEdicion ? 'Editar categoría' : 'Nueva categoría fiscal' }}
            </h2>
            <button @click="modal = false" class="p-1 text-gray-400 hover:text-gray-600 rounded">✕</button>
          </div>
          <div class="p-6 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Código <span class="text-red-500">*</span></label>
                <input type="text" v-model="form.codigo" placeholder="ING_CUOTAS" :disabled="modoEdicion"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50 disabled:text-gray-400 font-mono" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tipo <span class="text-red-500">*</span></label>
                <select v-model="form.tipo" :disabled="modoEdicion"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50 disabled:text-gray-400">
                  <option value="INGRESO">Ingreso</option>
                  <option value="GASTO">Gasto</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre <span class="text-red-500">*</span></label>
              <input type="text" v-model="form.nombre" placeholder="Cuotas de asociados"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea v-model="form.descripcion" rows="2"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 resize-none" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Casilla modelo</label>
                <input type="text" v-model="form.casillaModelo" placeholder="130-01"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
                <input type="color" v-model="form.color"
                  class="w-full h-[38px] border border-gray-300 rounded-lg px-1 cursor-pointer" />
              </div>
            </div>
            <div class="space-y-2 pt-1">
              <label class="flex items-center gap-3 cursor-pointer select-none">
                <input type="checkbox" v-model="form.computaModelo182" class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
                <span class="text-sm text-gray-700">Computa en Modelo 182 <span class="text-gray-400 text-xs">(donativos deducibles)</span></span>
              </label>
              <label class="flex items-center gap-3 cursor-pointer select-none">
                <input type="checkbox" v-model="form.computaModelo347" class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
                <span class="text-sm text-gray-700">Computa en Modelo 347 <span class="text-gray-400 text-xs">(operaciones > 3.005,06 €)</span></span>
              </label>
              <label v-if="modoEdicion" class="flex items-center gap-3 cursor-pointer select-none">
                <input type="checkbox" v-model="form.activa" class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
                <span class="text-sm text-gray-700">Categoría activa</span>
              </label>
            </div>
            <p v-if="errorModal" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{{ errorModal }}</p>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            <button @click="modal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="guardar" :disabled="guardando"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
              {{ guardando ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal confirmar eliminar -->
    <Teleport to="body">
      <div v-if="modalEliminar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalEliminar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">¿Eliminar esta categoría?</h2>
          <p class="text-sm text-gray-600">
            «{{ categoriaActiva?.nombre }}» se eliminará. Si tiene apuntes asociados no se podrá
            eliminar; en ese caso desactívala desde el botón Editar.
          </p>
          <p v-if="errorEliminar" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{{ errorEliminar }}</p>
          <div class="flex justify-end gap-3">
            <button @click="modalEliminar = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
            <button @click="ejecutarEliminar" :disabled="eliminando"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
              {{ eliminando ? 'Eliminando…' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { usePermisos } from '@/composables/usePermisos.js'
import {
  GET_CATEGORIAS_FISCALES,
  CREAR_CATEGORIA_FISCAL,
  ACTUALIZAR_CATEGORIA_FISCAL,
  ELIMINAR_CATEGORIA_FISCAL,
} from '@/graphql/queries/categorias_fiscales.js'

const { query, mutation } = useGraphQL()
const { tienePermiso } = usePermisos()

const puedeGestionar = computed(() => tienePermiso('ECO_ESTRUCTURA_CONTABLE_GESTIONAR'))

const loading = ref(false)
const error = ref('')
const categorias = ref([])

const modal = ref(false)
const modalEliminar = ref(false)
const modoEdicion = ref(false)
const guardando = ref(false)
const eliminando = ref(false)
const errorModal = ref('')
const errorEliminar = ref('')
const categoriaActiva = ref(null)

const form = ref({
  id: null, codigo: '', nombre: '', tipo: 'INGRESO', descripcion: '',
  casillaModelo: '', color: '#6366f1',
  computaModelo182: false, computaModelo347: false, activa: true,
})

const grupos = computed(() => [
  { tipo: 'INGRESO', items: categorias.value.filter(c => c.tipo === 'INGRESO') },
  { tipo: 'GASTO',   items: categorias.value.filter(c => c.tipo === 'GASTO') },
])

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const data = await query(GET_CATEGORIAS_FISCALES, { activasSolo: false })
    categorias.value = data?.categoriasFiscales ?? []
  } catch (e) {
    error.value = e?.message ?? 'Error al cargar las categorías fiscales'
  } finally {
    loading.value = false
  }
}

const abrirNueva = () => {
  modoEdicion.value = false
  form.value = {
    id: null, codigo: '', nombre: '', tipo: 'INGRESO', descripcion: '',
    casillaModelo: '', color: '#6366f1',
    computaModelo182: false, computaModelo347: false, activa: true,
  }
  errorModal.value = ''
  modal.value = true
}

const abrirEditar = (c) => {
  modoEdicion.value = true
  form.value = {
    id: c.id, codigo: c.codigo, nombre: c.nombre, tipo: c.tipo,
    descripcion: c.descripcion ?? '', casillaModelo: c.casillaModelo ?? '',
    color: c.color ?? '#6366f1',
    computaModelo182: c.computaModelo182, computaModelo347: c.computaModelo347,
    activa: c.activa,
  }
  errorModal.value = ''
  modal.value = true
}

const guardar = async () => {
  errorModal.value = ''
  if (!form.value.codigo || !form.value.nombre) {
    errorModal.value = 'El código y el nombre son obligatorios'
    return
  }
  guardando.value = true
  try {
    if (modoEdicion.value) {
      await mutation(ACTUALIZAR_CATEGORIA_FISCAL, {
        data: {
          id: form.value.id,
          nombre: form.value.nombre,
          descripcion: form.value.descripcion || null,
          casillaModelo: form.value.casillaModelo || null,
          color: form.value.color || null,
          computaModelo182: form.value.computaModelo182,
          computaModelo347: form.value.computaModelo347,
          activa: form.value.activa,
        },
      })
    } else {
      await mutation(CREAR_CATEGORIA_FISCAL, {
        data: {
          codigo: form.value.codigo,
          nombre: form.value.nombre,
          tipo: form.value.tipo,
          descripcion: form.value.descripcion || null,
          casillaModelo: form.value.casillaModelo || null,
          color: form.value.color || null,
          computaModelo182: form.value.computaModelo182,
          computaModelo347: form.value.computaModelo347,
        },
      })
    }
    modal.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e?.message ?? 'Error al guardar la categoría'
  } finally {
    guardando.value = false
  }
}

const confirmarEliminar = (c) => {
  categoriaActiva.value = c
  errorEliminar.value = ''
  modalEliminar.value = true
}

const ejecutarEliminar = async () => {
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await mutation(ELIMINAR_CATEGORIA_FISCAL, { categoriaId: categoriaActiva.value.id })
    modalEliminar.value = false
    await cargar()
  } catch (e) {
    errorEliminar.value = e?.message ?? 'No se pudo eliminar la categoría'
  } finally {
    eliminando.value = false
  }
}

onMounted(cargar)
</script>
