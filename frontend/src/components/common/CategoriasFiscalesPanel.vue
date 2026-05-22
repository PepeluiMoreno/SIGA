<template>
  <div>
    <p class="text-sm text-gray-500 max-w-2xl mb-4">
      Las categorías fiscales clasifican los ingresos y gastos de la organización
      y determinan su tratamiento en los modelos tributarios. Equivalen al plan de
      cuentas en la contabilidad por partida doble. Edita cualquier campo directamente
      sobre la fila.
    </p>

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

          <div class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            <!-- Filas de categorías -->
            <div v-for="c in grupo.items" :key="c.id"
              class="px-3 py-2.5 hover:bg-gray-50 transition-colors group"
              :class="c.activa ? '' : 'opacity-60'">
              <div class="flex items-center gap-2">
                <!-- Color editable inline -->
                <input v-if="puedeGestionar" type="color" :value="c.color || '#cbd5e1'"
                  @change="commit(c, 'color', $event.target.value)"
                  class="w-5 h-5 rounded cursor-pointer border-0 bg-transparent p-0 flex-shrink-0"
                  title="Color" />
                <span v-else class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: c.color || '#cbd5e1' }"></span>

                <!-- Nombre editable inline -->
                <input v-if="puedeGestionar" :value="c.nombre"
                  @blur="commit(c, 'nombre', $event.target.value)"
                  @keydown.enter="$event.target.blur()"
                  class="inline-edit flex-1 font-medium text-gray-900" />
                <span v-else class="flex-1 font-medium text-gray-900 text-sm">{{ c.nombre }}</span>

                <span class="text-xs text-gray-400 font-mono flex-shrink-0">{{ c.codigo }}</span>

                <button v-if="puedeGestionar" @click="confirmarEliminar(c)"
                  class="text-xs px-2 py-1 rounded text-red-500 opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all flex-shrink-0">
                  Eliminar
                </button>
              </div>

              <!-- Segunda línea: toggles fiscales + casilla + activa, todo inline -->
              <div class="flex items-center flex-wrap gap-x-3 gap-y-1 mt-1.5 ml-7 text-xs">
                <label class="flex items-center gap-1 cursor-pointer select-none"
                  :class="c.computaModelo182 ? 'text-blue-600' : 'text-gray-400'">
                  <input type="checkbox" :checked="c.computaModelo182" :disabled="!puedeGestionar"
                    @change="commit(c, 'computaModelo182', $event.target.checked)"
                    class="w-3.5 h-3.5 text-blue-600 rounded focus:ring-blue-500" />
                  Modelo 182
                </label>
                <label class="flex items-center gap-1 cursor-pointer select-none"
                  :class="c.computaModelo347 ? 'text-purple-600' : 'text-gray-400'">
                  <input type="checkbox" :checked="c.computaModelo347" :disabled="!puedeGestionar"
                    @change="commit(c, 'computaModelo347', $event.target.checked)"
                    class="w-3.5 h-3.5 text-purple-600 rounded focus:ring-purple-500" />
                  Modelo 347
                </label>
                <span class="flex items-center gap-1 text-gray-400">
                  Casilla:
                  <input v-if="puedeGestionar" :value="c.casillaModelo"
                    @blur="commit(c, 'casillaModelo', $event.target.value)"
                    @keydown.enter="$event.target.blur()"
                    placeholder="—"
                    class="inline-edit w-16 text-gray-600" />
                  <span v-else>{{ c.casillaModelo || '—' }}</span>
                </span>
                <label v-if="puedeGestionar" class="flex items-center gap-1 cursor-pointer select-none ml-auto"
                  :class="c.activa ? 'text-green-600' : 'text-gray-400'">
                  <input type="checkbox" :checked="c.activa"
                    @change="commit(c, 'activa', $event.target.checked)"
                    class="w-3.5 h-3.5 text-green-600 rounded focus:ring-green-500" />
                  {{ c.activa ? 'Activa' : 'Inactiva' }}
                </label>
              </div>
            </div>

            <!-- Fila de alta inline -->
            <div v-if="puedeGestionar" class="px-3 py-2">
              <div v-if="altaTipo === grupo.tipo" class="flex items-center gap-2 bg-purple-50/40 rounded p-2">
                <input v-model="nueva.codigo" placeholder="CÓDIGO"
                  class="inline-edit font-mono text-xs w-28 uppercase" />
                <input v-model="nueva.nombre" placeholder="Nombre de la categoría"
                  class="inline-edit flex-1" @keydown.enter="confirmarAlta(grupo.tipo)" />
                <button @click="confirmarAlta(grupo.tipo)" class="text-xs text-purple-700 font-medium hover:underline">Añadir</button>
                <button @click="altaTipo = null" class="text-xs text-gray-400 hover:underline">Cancelar</button>
              </div>
              <button v-else @click="abrirAlta(grupo.tipo)"
                class="text-xs text-purple-600 hover:underline">
                + Nueva categoría de {{ grupo.tipo === 'INGRESO' ? 'ingreso' : 'gasto' }}
              </button>
            </div>
          </div>
        </section>
      </div>
    </template>

    <!-- Modal confirmar eliminar (la única acción que merece confirmación) -->
    <Teleport to="body">
      <div v-if="modalEliminar"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        @click.self="modalEliminar = false">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-900">¿Eliminar esta categoría?</h2>
          <p class="text-sm text-gray-600">
            «{{ categoriaActiva?.nombre }}» se eliminará. Si tiene apuntes asociados no se podrá
            eliminar; en ese caso desactívala con el interruptor de la fila.
          </p>
          <ErrorAlert v-if="errorEliminar" :message="errorEliminar" />
          <div class="flex justify-end gap-3">
            <button @click="modalEliminar = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">Cancelar</button>
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
import ErrorAlert from '@/components/common/ErrorAlert.vue'
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

const modalEliminar = ref(false)
const eliminando = ref(false)
const errorEliminar = ref('')
const categoriaActiva = ref(null)

const altaTipo = ref(null)  // 'INGRESO' | 'GASTO' | null
const nueva = ref({ codigo: '', nombre: '' })

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

// Edición inline: actualiza un único campo. Optimista con recarga al final.
const commit = async (categoria, campo, valor) => {
  // Normalizar
  if (campo === 'casillaModelo') valor = (valor || '').trim()  // '' permite borrarla
  if (campo === 'nombre') {
    valor = (valor || '').trim()
    if (!valor) { await cargar(); return }  // no permitir nombre vacío
  }
  if (categoria[campo] === valor) return  // sin cambios

  // Aplicar localmente (optimista)
  const previo = categoria[campo]
  categoria[campo] = valor
  try {
    await mutation(ACTUALIZAR_CATEGORIA_FISCAL, {
      data: { id: categoria.id, [campo]: valor },
    })
  } catch (e) {
    categoria[campo] = previo  // revertir si falla
    error.value = e?.message ?? 'No se pudo guardar el cambio'
  }
}

const abrirAlta = (tipo) => {
  altaTipo.value = tipo
  nueva.value = { codigo: '', nombre: '' }
}

const confirmarAlta = async (tipo) => {
  const codigo = (nueva.value.codigo || '').trim().toUpperCase()
  const nombre = (nueva.value.nombre || '').trim()
  if (!codigo || !nombre) return
  try {
    await mutation(CREAR_CATEGORIA_FISCAL, {
      data: { codigo, nombre, tipo },
    })
    altaTipo.value = null
    nueva.value = { codigo: '', nombre: '' }
    await cargar()
  } catch (e) {
    error.value = e?.message ?? 'No se pudo crear la categoría'
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

<style scoped>
.inline-edit {
  @apply bg-transparent border border-transparent rounded px-2 py-1 text-sm
         hover:border-gray-200 focus:border-purple-400 focus:bg-white focus:outline-none transition-colors;
}
</style>
