<template>
  <AppLayout :title="titulo" :subtitle="subtitulo">
    <!-- Botón volver y acciones -->
    <div class="mb-6 flex justify-between items-center">
      <router-link to="/parametrizacion" class="text-gray-600 hover:text-gray-900 flex items-center gap-2">
        <ArrowLeftIcon class="w-5 h-5" />
        Volver a Parametrización
      </router-link>
      <AppButton
        @click="abrirModalCrear"
        class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700"
      >
        <PlusIcon class="w-5 h-5" />
        Nuevo {{ nombreSingular }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-gray-600">Cargando...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <span class="text-red-400 mr-3">Error</span>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al cargar datos</h3>
          <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
        </div>
      </div>
    </div>

    <!-- Tabla -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div v-if="items.length === 0" class="text-center py-12">
        <div class="mx-auto h-12 w-12 text-gray-400 mb-4 text-4xl">{{ icono }}</div>
        <h3 class="text-sm font-medium text-gray-900">No hay registros</h3>
        <p class="text-sm text-gray-500 mt-1">Crea el primer {{ nombreSingular.toLowerCase() }}</p>
      </div>

      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="col in columnas"
              :key="col.key"
              :class="[
                'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider',
                col.centered ? 'text-center' : 'text-left'
              ]"
            >
              {{ col.label }}
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50">
            <td
              v-for="col in columnas"
              :key="col.key"
              :class="[
                'px-6 py-4',
                col.type === 'multiline' ? '' : 'whitespace-nowrap',
                col.centered ? 'text-center' : ''
              ]"
            >
              <!-- Tipo checkbox (visual) -->
              <template v-if="col.type === 'checkbox'">
                <CheckIcon class="w-5 h-5 ['text-green-600', col.centered ? 'mx-auto' : '']" />
                <XMarkIcon class="w-5 h-5 ['  text-gray-300', col.centered ? 'mx-auto' : '']" />
              </template>

              <!-- Tipo boolean (texto Sí/No) - mantener por compatibilidad -->
              <template v-else-if="col.type === 'boolean'">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                    item[col.key] ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ item[col.key] ? 'Sí' : 'No' }}
                </span>
              </template>

              <!-- Tipo color -->
              <template v-else-if="col.type === 'color'">
                <div class="flex items-center gap-2">
                  <span
                    class="w-6 h-6 rounded-full border border-gray-300"
                    :style="{ backgroundColor: item[col.key] || '#6C757D' }"
                  ></span>
                  <span class="text-sm text-gray-500">{{ item[col.key] }}</span>
                </div>
              </template>

              <!-- Tipo activo/en uso (especial) -->
              <template v-else-if="col.key === 'activo'">
                <CheckIcon class="w-5 h-5 text-green-600" />
                <XMarkIcon class="w-5 h-5 text-gray-300" />
              </template>

              <!-- Tipo texto multilinea (para descripciones) -->
              <template v-else-if="col.type === 'multiline'">
                <span class="text-sm text-gray-900 block max-w-xs whitespace-normal">
                  {{ item[col.key] ?? '-' }}
                </span>
              </template>

              <!-- Tipo texto normal -->
              <template v-else>
                <!-- Si es columna nombre y tiene color, mostrar como badge -->
                <span
                  v-if="col.key === 'nombre' && item.color"
                  class="inline-flex px-2 py-1 text-sm font-medium rounded-full text-gray-900"
                  :style="{ backgroundColor: item.color + '30' }"
                >
                  {{ item[col.key] ?? '-' }}
                </span>
                <span v-else class="text-sm text-gray-900">{{ item[col.key] ?? '-' }}</span>
              </template>
            </td>

            <!-- Acciones -->
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button
                @click="abrirModalEditar(item)"
                class="text-purple-600 hover:text-purple-900 mr-3"
              >
                Editar
              </button>
              <button
                @click="confirmarEliminar(item)"
                class="text-red-600 hover:text-red-900"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear/Editar -->
    <div
      v-if="modalAbierto"
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Overlay -->
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          @click="cerrarModal"
        ></div>

        <!-- Modal -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="guardar">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg font-medium text-gray-900 mb-4">
                {{ itemEditando ? 'Editar' : 'Nuevo' }} {{ nombreSingular }}
              </h3>

              <div class="space-y-4">
                <div v-for="campo in campos" :key="campo.name">
                  <!-- Label solo para campos que no son checkbox -->
                  <label
                    v-if="campo.type !== 'checkbox'"
                    :for="campo.name"
                    class="block text-sm font-medium text-gray-700 mb-1"
                  >
                    {{ campo.label }}
                    <span v-if="campo.required" class="text-red-500">*</span>
                  </label>

                  <!-- Input texto -->
                  <input
                    v-if="campo.type === 'text' || !campo.type"
                    :id="campo.name"
                    v-model="formulario[campo.name]"
                    type="text"
                    :required="campo.required"
                    :maxlength="campo.maxLength"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />

                  <!-- Textarea -->
                  <textarea
                    v-else-if="campo.type === 'textarea'"
                    :id="campo.name"
                    v-model="formulario[campo.name]"
                    rows="3"
                    :required="campo.required"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  ></textarea>

                  <!-- Checkbox -->
                  <div v-else-if="campo.type === 'checkbox'" class="flex items-center">
                    <input
                      :id="campo.name"
                      v-model="formulario[campo.name]"
                      type="checkbox"
                      class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <label :for="campo.name" class="ml-2 text-sm text-gray-600">
                      {{ campo.description || campo.label }}
                    </label>
                  </div>

                  <!-- Color picker -->
                  <div v-else-if="campo.type === 'color'" class="flex items-center gap-3">
                    <input
                      :id="campo.name"
                      v-model="formulario[campo.name]"
                      type="color"
                      class="h-10 w-14 p-1 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      v-model="formulario[campo.name]"
                      type="text"
                      pattern="^#[0-9A-Fa-f]{6}$"
                      placeholder="#RRGGBB"
                      class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <!-- Number -->
                  <input
                    v-else-if="campo.type === 'number'"
                    :id="campo.name"
                    v-model.number="formulario[campo.name]"
                    type="number"
                    :min="campo.min"
                    :max="campo.max"
                    :required="campo.required"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />

                  <!-- Select -->
                  <select
                    v-else-if="campo.type === 'select'"
                    :id="campo.name"
                    v-model="formulario[campo.name]"
                    :required="campo.required"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar...</option>
                    <option v-for="opt in campo.options" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
              <button
                type="submit"
                :disabled="guardando"
                class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-purple-600 text-base font-medium text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                {{ guardando ? 'Guardando...' : 'Guardar' }}
              </button>
              <button
                type="button"
                @click="cerrarModal"
                class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:mt-0 sm:w-auto sm:text-sm"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Confirmar Eliminar -->
    <div
      v-if="modalEliminar"
      class="fixed inset-0 z-50 overflow-y-auto"
    >
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          @click="modalEliminar = false"
        ></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10" :class="errorEliminacion ? 'bg-amber-100' : 'bg-red-100'">
                <ExclamationTriangleIcon class="w-6 h-6 text-amber-600" />
                <TrashIcon class="w-6 h-6 text-red-600" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  {{ errorEliminacion ? 'No se puede eliminar' : 'Eliminar ' + nombreSingular }}
                </h3>
                <div class="mt-2">
                  <!-- Mensaje de error -->
                  <div v-if="errorEliminacion" class="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <p class="text-sm text-amber-800">{{ errorEliminacion }}</p>
                  </div>
                  <!-- Confirmación normal -->
                  <p v-else class="text-sm text-gray-500">
                    ¿Estás seguro de que deseas eliminar "{{ itemAEliminar?.nombre }}"?
                    Esta acción no se puede deshacer.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
            <!-- Si hay error, solo mostrar botón Cerrar -->
            <template v-if="errorEliminacion">
              <button
                type="button"
                @click="modalEliminar = false"
                class="w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:w-auto sm:text-sm"
              >
                Cerrar
              </button>
            </template>
            <!-- Si no hay error, mostrar botones normales -->
            <template v-else>
              <button
                type="button"
                @click="eliminar"
                :disabled="eliminando"
                class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                {{ eliminando ? 'Eliminando...' : 'Eliminar' }}
              </button>
              <button
                type="button"
                @click="modalEliminar = false"
                class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:w-auto sm:text-sm"
              >
                Cancelar
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { XMarkIcon, PlusIcon, ArrowLeftIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useToast } from '@/composables/useToast'
import { ref, onMounted, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL.js'
const toast = useToast()

const props = defineProps({
  titulo: { type: String, required: true },
  subtitulo: { type: String, default: '' },
  nombreSingular: { type: String, required: true },
  icono: { type: String, default: '📋' },
  queryName: { type: String, required: true },
  queryString: { type: String, required: true },
  mutationCreate: { type: String, default: null },
  mutationUpdate: { type: String, default: null },
  mutationDelete: { type: String, default: null },
  columnas: { type: Array, required: true },
  campos: { type: Array, required: true },
  orderBy: { type: String, default: null },
})

const emit = defineEmits(['created', 'updated', 'deleted'])

const { loading, error, query, mutation } = useGraphQL()

const items = ref([])
const modalAbierto = ref(false)
const modalEliminar = ref(false)
const itemEditando = ref(null)
const itemAEliminar = ref(null)
const guardando = ref(false)
const eliminando = ref(false)
const formulario = ref({})
const errorEliminacion = ref(null)

// Inicializar formulario con valores por defecto
const inicializarFormulario = () => {
  const form = {}
  props.campos.forEach(campo => {
    if (campo.type === 'checkbox') {
      form[campo.name] = campo.default ?? false
    } else if (campo.type === 'number') {
      form[campo.name] = campo.default ?? 0
    } else if (campo.type === 'color') {
      form[campo.name] = campo.default ?? '#6C757D'
    } else {
      form[campo.name] = campo.default ?? ''
    }
  })
  return form
}

const cargarDatos = async () => {
  try {
    const data = await query(props.queryString)
    if (data && data[props.queryName]) {
      let resultado = data[props.queryName]
      // Ordenar si se especifica orderBy
      if (props.orderBy) {
        resultado = [...resultado].sort((a, b) => {
          const valA = a[props.orderBy]
          const valB = b[props.orderBy]
          if (typeof valA === 'number' && typeof valB === 'number') {
            return valA - valB
          }
          return String(valA).localeCompare(String(valB))
        })
      }
      items.value = resultado
    }
  } catch (err) {
    console.error('Error cargando datos:', err)
  }
}

const abrirModalCrear = () => {
  itemEditando.value = null
  formulario.value = inicializarFormulario()
  modalAbierto.value = true
}

const abrirModalEditar = (item) => {
  itemEditando.value = item
  formulario.value = { ...item }
  modalAbierto.value = true
}

const cerrarModal = () => {
  modalAbierto.value = false
  itemEditando.value = null
  formulario.value = {}
}

const guardar = async () => {
  guardando.value = true
  try {
    // Preparar data (Strawchemy usa 'data' en vez de 'input')
    const data = {}
    props.campos.forEach(campo => {
      if (formulario.value[campo.name] !== undefined && formulario.value[campo.name] !== '') {
        data[campo.name] = formulario.value[campo.name]
      }
    })

    if (itemEditando.value && props.mutationUpdate) {
      // Actualizar - incluir el id en el data para update_by_pk
      data.id = itemEditando.value.id
      await mutation(props.mutationUpdate, { data })
      emit('updated', itemEditando.value)
    } else if (props.mutationCreate) {
      // Crear
      await mutation(props.mutationCreate, { data })
      emit('created')
    }

    cerrarModal()
    await cargarDatos()
  } catch (err) {
    console.error('Error guardando:', err)
    toast.error('Error al guardar: ' + err.message)
  } finally {
    guardando.value = false
  }
}

const confirmarEliminar = (item) => {
  itemAEliminar.value = item
  errorEliminacion.value = null
  modalEliminar.value = true
}

const eliminar = async () => {
  if (!props.mutationDelete || !itemAEliminar.value) return

  eliminando.value = true
  errorEliminacion.value = null
  try {
    // Strawchemy delete usa filter con id.eq (sin guión bajo)
    await mutation(props.mutationDelete, {
      filter: { id: { eq: itemAEliminar.value.id } }
    })
    emit('deleted', itemAEliminar.value)
    modalEliminar.value = false
    itemAEliminar.value = null
    await cargarDatos()
  } catch (err) {
    console.error('Error eliminando:', err)
    // Detectar error de FK (registro en uso)
    const errorMsg = err.message || ''
    if (errorMsg.includes('ForeignKeyViolation') || errorMsg.includes('viola la llave foránea')) {
      errorEliminacion.value = `No se puede eliminar "${itemAEliminar.value?.nombre}" porque está siendo utilizado por otros registros del sistema. Para deshabilitarlo, edítalo y desmarca la opción "En uso".`
    } else {
      errorEliminacion.value = 'Error al eliminar: ' + errorMsg
    }
  } finally {
    eliminando.value = false
  }
}

onMounted(() => {
  cargarDatos()
})
</script>
