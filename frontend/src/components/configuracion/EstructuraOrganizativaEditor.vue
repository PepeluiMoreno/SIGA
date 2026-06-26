<template>
  <div>
    <ErrorAlert v-if="errorMsg" :message="errorMsg" class="mb-3" />

    <!-- Modelo de estructura (solo en uso embebido; en Parámetros lo pinta el padre arriba) -->
    <fieldset v-if="mostrarRadiogroup && nodoRaizActual" class="rounded-xl border border-slate-200 bg-white px-3 pt-1.5 pb-3 mb-4">
      <legend class="px-1.5 text-[11px] font-medium text-slate-500">
        Modelo de estructura de «{{ nodoRaizActual.nombre }}»
      </legend>
      <div class="flex flex-col sm:flex-row gap-2.5 mt-1">
        <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="!distribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
          <input type="radio" class="mt-0.5 accent-indigo-600" :checked="!distribuida" :disabled="guardando" @change="setDistribuida(false)" />
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800">Centralizada</span>
            <span class="block text-xs text-slate-500 leading-snug mt-0.5">La estructura interna se define aquí, igual para todas las unidades.</span>
          </span>
        </label>
        <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="distribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
          <input type="radio" class="mt-0.5 accent-indigo-600" :checked="distribuida" :disabled="guardando" @change="setDistribuida(true)" />
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800">Distribuida</span>
            <span class="block text-xs text-slate-500 leading-snug mt-0.5">Cada unidad de este nivel define su propia subestructura.</span>
          </span>
        </label>
      </div>
    </fieldset>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

      <!-- IZQUIERDA · grid de niveles (nivel · ámbito · denominación) -->
      <div>
        <table class="w-full text-sm border-collapse border border-slate-200">
          <thead>
            <tr class="bg-slate-50 text-left text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              <th class="px-2 py-2 border-b border-slate-200 w-14 text-center">Nivel</th>
              <th class="px-3 py-2 border-b border-slate-200">Nombre</th>
              <th class="px-3 py-2 border-b border-slate-200 w-32">Ámbito</th>
              <th class="px-3 py-2 border-b border-slate-200">Denominación</th>
              <th class="px-1 py-2 border-b border-slate-200 w-px"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="item in arbolPlano" :key="item.id">
              <!-- Lectura -->
              <tr v-if="editandoId !== item.id" class="group border-b border-slate-100 hover:bg-slate-50">
                <td class="px-2 py-1.5 align-middle text-center text-slate-400 tabular-nums">{{ item.depth + 1 }}</td>
                <td class="px-3 py-1.5 align-middle">
                  <span class="block truncate" :class="item.depth === 0 ? 'font-medium text-slate-800' : 'text-slate-700'">{{ item.nombre }}</span>
                </td>
                <td class="px-3 py-1.5 align-middle text-slate-600">
                  {{ item.ambitoGeografico?.nombre || '—' }}
                </td>
                <td class="px-3 py-1.5 align-middle text-slate-600">
                  <span class="block truncate"
                    :title="item.denominacionPlural ? `${item.denominacionSingular} / ${item.denominacionPlural}` : (item.denominacionSingular || '')">{{ item.denominacionSingular || '—' }}</span>
                </td>
                <td class="px-1 py-1 align-middle">
                  <div class="flex items-center justify-end gap-0.5 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
                    <button v-if="puedeSubir(item)" type="button" @click="promover(item)" :disabled="guardando"
                      title="Subir un nivel (promover)"
                      class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">↑</button>
                    <button v-if="prevSiblingOf(item)" type="button" @click="demover(item)" :disabled="guardando"
                      title="Bajar un nivel (anidar en el anterior)"
                      class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">↓</button>
                    <span class="w-px h-4 bg-slate-200 mx-0.5" />
                    <button v-if="puedeSuperior(item)" type="button" @click="añadirSuperior(item)" :disabled="guardando"
                      title="Insertar un nivel por encima de este"
                      class="w-7 h-7 grid place-items-center text-xs font-mono text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">⊕↑</button>
                    <button type="button" @click="añadirHijo(item)" :disabled="guardando"
                      title="Añadir un subnivel (hijo)"
                      class="w-7 h-7 grid place-items-center text-xs font-mono text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">⊕↓</button>
                    <span class="w-px h-4 bg-slate-200 mx-0.5" />
                    <button type="button" @click="iniciarEdicion(item)"
                      title="Editar nombre, ámbito y denominación"
                      class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50">✎</button>
                    <button v-if="puedeEliminar(item)" type="button" @click="iniciarEliminar(item)" :disabled="guardando"
                      title="Eliminar nivel"
                      class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-red-500 rounded hover:bg-red-50 disabled:opacity-30">×</button>
                  </div>
                </td>
              </tr>

              <!-- Edición: mini-formulario con etiquetas (ocupa toda la fila) -->
              <tr v-else class="border-t border-purple-200">
                <td colspan="5" class="py-2">
                  <div class="rounded-lg border border-purple-300 bg-purple-50/40 p-2.5 space-y-2">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-3 gap-y-2">
                      <label class="block">
                        <span class="block text-[11px] font-medium text-slate-500 mb-0.5">Nombre del nivel</span>
                        <input v-model="formNombre" type="text" autofocus
                          class="w-full border border-slate-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
                          @keydown.enter.prevent="guardar(item)"
                          @keydown.escape="editandoId = null" />
                      </label>
                      <label class="block">
                        <span class="block text-[11px] font-medium text-slate-500 mb-0.5">Ámbito geográfico</span>
                        <select v-model="formAmbitoId"
                          class="w-full border border-slate-300 rounded px-2 py-1 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500">
                          <option value="">— sin ámbito —</option>
                          <option v-for="a in ambitosOrdenados" :key="a.id" :value="a.id">{{ a.nombre }}</option>
                        </select>
                      </label>
                      <label class="block">
                        <span class="block text-[11px] font-medium text-slate-500 mb-0.5">Denominación de la unidad (singular)</span>
                        <input v-model="formDenomSingular" type="text" placeholder="p.ej. Agrupación Provincial"
                          class="w-full border border-slate-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                      </label>
                      <label class="block">
                        <span class="block text-[11px] font-medium text-slate-500 mb-0.5">Denominación de la unidad (plural)</span>
                        <input v-model="formDenomPlural" type="text" placeholder="p.ej. Agrupaciones Provinciales"
                          class="w-full border border-slate-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                      </label>
                    </div>
                    <div class="flex justify-end gap-2">
                      <button type="button" @click="editandoId = null"
                        class="text-xs px-2.5 py-1 text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
                      <button type="button" @click="guardar(item)"
                        class="text-xs px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700">Guardar</button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>

        <div class="flex items-center pt-2 mt-1 border-t border-slate-100">
          <button v-if="!scoped" type="button" @click="añadirRaiz" :disabled="guardando"
            class="inline-flex items-center gap-1.5 text-xs font-medium text-purple-600 hover:text-purple-800 disabled:opacity-40">
            <span class="grid place-items-center w-5 h-5 rounded-full border border-purple-300 text-purple-500 font-mono leading-none">+</span>
            Añadir nivel raíz
          </button>
          <button v-else-if="nodoScope" type="button" @click="añadirHijo(nodoScope)" :disabled="guardando"
            class="inline-flex items-center gap-1.5 text-xs font-medium text-purple-600 hover:text-purple-800 disabled:opacity-40">
            <span class="grid place-items-center w-5 h-5 rounded-full border border-purple-300 text-purple-500 font-mono leading-none">+</span>
            Añadir subnivel
          </button>
        </div>

        <p class="text-[11px] text-slate-400 leading-tight pt-1.5">
          Al pasar el ratón por un nivel: <span class="font-mono">↑</span> subir ·
          <span class="font-mono">↓</span> anidar · <span class="font-mono">⊕↑</span> insertar encima ·
          <span class="font-mono">⊕↓</span> subnivel · <span class="font-mono">✎</span> editar ·
          <span class="font-mono">×</span> borrar
        </p>
      </div>

      <!-- DERECHA · vista del árbol en tiempo real -->
      <div class="lg:border-l lg:border-slate-100 lg:pl-6">
        <div class="rounded-xl border border-slate-200 bg-slate-50/60 p-4 min-h-[7rem]">
          <div v-if="arbolPreview.length">
            <div v-for="node in arbolPreview" :key="node.id"
              class="flex items-center leading-7 rounded transition-colors"
              :class="node.editing ? 'bg-purple-100/70 ring-1 ring-purple-200' : ''">
              <span v-for="(v, i) in node.vlines" :key="i"
                class="inline-block w-5 flex-shrink-0 text-center font-mono text-slate-300 select-none">{{ v ? '│' : '' }}</span>
              <span class="inline-block w-5 flex-shrink-0 text-center font-mono select-none"
                :class="node.depth === 0 ? 'text-purple-400' : 'text-slate-300'">{{ node.depth === 0 ? '●' : (node.isLast ? '└' : '├') }}</span>
              <span class="flex items-center gap-1.5 min-w-0 px-1">
                <span class="truncate" :class="node.depth === 0 ? 'text-sm font-semibold text-slate-800' : 'text-sm text-slate-700'">{{ node.nombre || 'Sin nombre' }}</span>
                <span v-if="node.ambitoNombre"
                  class="flex-shrink-0 px-1.5 py-0.5 text-[10px] rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200 leading-none">{{ node.ambitoNombre }}</span>
                <span v-if="node.denominacionSingular"
                  class="flex-shrink-0 text-xs text-slate-400 italic truncate">→ {{ node.denominacionSingular }}</span>
              </span>
            </div>
          </div>
          <p v-else class="text-sm text-slate-400 italic text-center py-6">Aún no hay niveles definidos.</p>
        </div>

        <p class="text-xs text-gray-400 pt-2">
          <template v-if="arbolPlano.length <= 1">Organización simple (sin subniveles)</template>
          <template v-else>Organización extendida · {{ arbolPlano.filter(n => n.depth > 0).map(n => n.nombre).join(' › ') }}</template>
        </p>
      </div>

    </div>
  </div>

  <!-- Modal confirmación de borrado -->
  <Teleport to="body">
    <div v-if="pendingDelete" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-5 max-w-sm w-full mx-4">
        <h3 class="font-semibold text-gray-900 mb-3">Eliminar nivel «{{ pendingDelete.nombre }}»</h3>
        <p v-if="pendingDelete.nHijos > 0 || pendingDelete.nUnidades > 0"
          class="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-3 mb-4">
          <strong>Atención:</strong> este nivel tiene
          <template v-if="pendingDelete.nHijos > 0">
            {{ pendingDelete.nHijos }} subnivel{{ pendingDelete.nHijos > 1 ? 'es' : '' }}
          </template>
          <template v-if="pendingDelete.nHijos > 0 && pendingDelete.nUnidades > 0"> y </template>
          <template v-if="pendingDelete.nUnidades > 0">
            {{ pendingDelete.nUnidades }} órgano{{ pendingDelete.nUnidades > 1 ? 's' : '' }} asignado{{ pendingDelete.nUnidades > 1 ? 's' : '' }}
          </template>.
          Se reasignarán al nivel padre antes de eliminar.
        </p>
        <p v-else class="text-sm text-gray-500 mb-4">Esta acción no se puede deshacer.</p>
        <div class="flex justify-end gap-2">
          <button type="button" @click="pendingDelete = null"
            class="text-sm px-3 py-1.5 border border-gray-200 rounded hover:bg-gray-50">Cancelar</button>
          <button type="button" @click="confirmarEliminar" :disabled="guardando"
            class="text-sm px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-40">
            {{ pendingDelete.nHijos > 0 || pendingDelete.nUnidades > 0 ? 'Reasignar y eliminar' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import { graphqlClient } from '@/graphql/client.js'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { GET_AMBITOS_GEOGRAFICOS } from '@/graphql/queries/catalogos.js'

const props = defineProps({
  // Ancla opcional. Si se indica, el editor solo muestra/edita el subárbol que
  // cuelga de este nivel; reutilizable en la edición de cada agrupación, que
  // arranca en su propio nivel geográfico. Sin prop = árbol completo (matriz).
  nivelRaizId: { type: String, default: null },
  // Si es false, el editor no pinta su radiogroup centralizada/distribuida
  // (lo pinta el contenedor, p.ej. Parámetros Generales lo coloca arriba).
  mostrarRadiogroup: { type: Boolean, default: true },
})

const { tipos, unidades, cargarTipos, cargarArbol, crearTipo, actualizarTipo, actualizarUnidad, eliminarTipo } = useUnidadesOrganizativas()
const orgConfig = useOrgConfigStore()

async function recargarConfig() {
  orgConfig.invalidate()
  await orgConfig.fetchConfig()
}

const editandoId    = ref(null)
const formNombre    = ref('')
const formAmbitoId  = ref('')
const formDenomSingular = ref('')
const formDenomPlural   = ref('')
const guardando     = ref(false)
const errorMsg      = ref('')
const pendingDelete = ref(null)

const ambitos = ref([])
const ambitosOrdenados = computed(() =>
  [...ambitos.value].sort((a, b) => a.granularidad - b.granularidad)
)

async function cargarAmbitos() {
  try {
    const data = await graphqlClient.request(GET_AMBITOS_GEOGRAFICOS)
    ambitos.value = data.ambitosGeograficos ?? []
  } catch { /* no bloquea */ }
}

const tiposTerritoriales = computed(() =>
  tipos.value.filter(t => t.naturaleza === 'TERRITORIAL')
)

const buildTree = (lista) => {
  const map = {}
  const raices = []
  lista.forEach(t => { map[t.id] = { ...t, hijos: [] } })
  lista.forEach(t => {
    if (t.padreTipoId && map[t.padreTipoId]) {
      map[t.padreTipoId].hijos.push(map[t.id])
    } else {
      raices.push(map[t.id])
    }
  })
  return raices
}

const raicesReales = computed(() => buildTree(tiposTerritoriales.value))

const buscarNodo = (nodos, id) => {
  for (const n of nodos) {
    if (n.id === id) return n
    const f = buscarNodo(n.hijos || [], id)
    if (f) return f
  }
  return null
}

// Nodo ancla del scope (si se indicó nivelRaizId)
const nodoScope = computed(() =>
  props.nivelRaizId ? buscarNodo(raicesReales.value, props.nivelRaizId) : null
)

// Raíces efectivas: con scope, solo el nodo ancla; sin scope, las raíces reales
const raices = computed(() =>
  nodoScope.value ? [nodoScope.value] : raicesReales.value
)

const scoped = computed(() => !!props.nivelRaizId)

// Nodo cuya bandera centralizada/distribuida gobierna este editor (recursivo:
// cada nivel decide cómo se organiza el subárbol que cuelga de él)
const nodoRaizActual = computed(() =>
  nodoScope.value ?? (raicesReales.value.length ? raicesReales.value[0] : null)
)
const distribuida = computed(() => !!nodoRaizActual.value?.estructuraDistribuida)

const setDistribuida = async (val) => {
  const nodo = nodoRaizActual.value
  if (!nodo || guardando.value || distribuida.value === val) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({ id: nodo.id, estructuraDistribuida: val })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al cambiar el modelo de estructura'
  } finally {
    guardando.value = false
  }
}

// ── Guardas de límite del scope ───────────────────────────────────────────────
const esAncla       = (item) => scoped.value && item.id === props.nivelRaizId
const puedeSubir    = (item) => item.depth > 0 && !(scoped.value && item.padreTipoId === props.nivelRaizId)
const puedeSuperior = (item) => !esAncla(item)
const puedeEliminar = (item) => !esAncla(item) && (item.depth > 0 || raices.value.length > 1)

const arbolPlano = computed(() => {
  const lista = []
  const dfs = (nodo, depth) => {
    lista.push({ ...nodo, depth })
    nodo.hijos.forEach(h => dfs(h, depth + 1))
  }
  raices.value.forEach(r => dfs(r, 0))
  return lista
})

// Vista previa en tiempo real: refleja el árbol y superpone los valores del
// formulario sobre el nodo que se está editando (sin esperar al guardado).
const arbolPreview = computed(() => {
  const out = []
  const overlay = (nodo) => {
    const editing = nodo.id === editandoId.value
    return {
      id: nodo.id,
      editing,
      nombre: editing ? formNombre.value : nodo.nombre,
      denominacionSingular: editing ? formDenomSingular.value : nodo.denominacionSingular,
      ambitoNombre: editing
        ? (ambitos.value.find(a => a.id === formAmbitoId.value)?.nombre ?? null)
        : (nodo.ambitoGeografico?.nombre ?? null),
    }
  }
  // vlines: por cada nivel ancestro, si dibujar barra vertical (el ancestro tiene hermano siguiente)
  const dfs = (nodo, depth, vlines, isLast) => {
    out.push({ ...overlay(nodo), depth, isLast, vlines: [...vlines] })
    const hijos = nodo.hijos || []
    hijos.forEach((h, i) => dfs(h, depth + 1, [...vlines, !isLast], i === hijos.length - 1))
  }
  const rs = raices.value
  rs.forEach((r, i) => dfs(r, 0, [], i === rs.length - 1))
  return out
})

const idsDescendientes = (nodo) => {
  const ids = new Set([nodo.id])
  const dfs = (n) => n.hijos?.forEach(h => { ids.add(h.id); dfs(h) })
  dfs(nodo)
  return ids
}

// Devuelve el hermano anterior (mismo padre, aparece antes en el DFS)
const prevSiblingOf = (nodo) => {
  const idx = arbolPlano.value.findIndex(n => n.id === nodo.id)
  if (idx <= 0) return null
  return arbolPlano.value.slice(0, idx).reverse().find(n => n.padreTipoId === nodo.padreTipoId) || null
}

const iniciarEdicion = (tipo) => {
  formNombre.value   = tipo.nombre
  formAmbitoId.value = tipo.ambitoGeograficoId ?? ''
  formDenomSingular.value = tipo.denominacionSingular ?? ''
  formDenomPlural.value   = tipo.denominacionPlural ?? ''
  editandoId.value   = tipo.id
}

const guardar = async (tipo) => {
  if (!formNombre.value.trim()) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({
      id: tipo.id,
      nombre: formNombre.value.trim(),
      ambitoGeograficoId: formAmbitoId.value || null,
      denominacionSingular: formDenomSingular.value.trim() || null,
      denominacionPlural: formDenomPlural.value.trim() || null,
    })
    editandoId.value = null
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar el nivel'
  } finally {
    guardando.value = false
  }
}

// Sube el nodo un nivel (pasa a ser hermano de su padre)
const promover = async (nodo) => {
  if (!nodo.padreTipoId) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    const parent = arbolPlano.value.find(n => n.id === nodo.padreTipoId)
    await actualizarTipo({ id: nodo.id, padreTipoId: parent?.padreTipoId || null })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al subir nivel'
  } finally {
    guardando.value = false
  }
}

// Baja el nodo un nivel (pasa a ser hijo del hermano anterior)
const demover = async (nodo) => {
  const prev = prevSiblingOf(nodo)
  if (!prev) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({ id: nodo.id, padreTipoId: prev.id })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al bajar nivel'
  } finally {
    guardando.value = false
  }
}

// Inserta un nuevo nivel ENTRE el nodo y su padre (splice hacia arriba)
const añadirSuperior = async (nodo) => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    const nuevo = await crearTipo({
      nombre: 'Nuevo nivel',
      naturaleza: 'TERRITORIAL',
      vinculo: nodo.vinculo ?? 'INTERNA',
      padreTipoId: nodo.padreTipoId || null,
      activo: true,
    })
    await actualizarTipo({ id: nodo.id, padreTipoId: nuevo.id })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al insertar nivel superior'
  } finally {
    guardando.value = false
  }
}

// Añade un hijo directo
const añadirHijo = async (padre) => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    await crearTipo({
      nombre: 'Nuevo subnivel',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      padreTipoId: padre.id,
      activo: true,
    })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al crear subnivel'
  } finally {
    guardando.value = false
  }
}

// Añade un nivel raíz (sin padre)
const añadirRaiz = async () => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    await crearTipo({
      nombre: 'Nuevo nivel',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      padreTipoId: null,
      activo: true,
    })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al crear nivel raíz'
  } finally {
    guardando.value = false
  }
}

const iniciarEliminar = (nodo) => {
  const nHijos    = tipos.value.filter(t => t.padreTipoId === nodo.id).length
  const nUnidades = unidades.value.filter(u => u.tipoId === nodo.id).length
  pendingDelete.value = { ...nodo, nHijos, nUnidades }
}

const confirmarEliminar = async () => {
  const nodo = pendingDelete.value
  if (!nodo) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    const childTipos    = tipos.value.filter(t => t.padreTipoId === nodo.id)
    const childUnidades = unidades.value.filter(u => u.tipoId === nodo.id)
    for (const child of childTipos) {
      await actualizarTipo({ id: child.id, padreTipoId: nodo.padreTipoId || null })
    }
    for (const unit of childUnidades) {
      await actualizarUnidad({ id: unit.id, tipoId: nodo.padreTipoId || null })
    }
    await eliminarTipo(nodo.id)
    await recargarConfig()
    pendingDelete.value = null
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al eliminar'
  } finally {
    guardando.value = false
  }
}

const estructuraProtegida = computed(() => false)
defineExpose({ estructuraProtegida, distribuida, setDistribuida, nodoRaizActual })

onMounted(async () => {
  await Promise.all([cargarTipos(), cargarArbol(), cargarAmbitos()])
  if (!props.nivelRaizId && tiposTerritoriales.value.length === 0) {
    await crearTipo({
      nombre: 'Asociación',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      activo: true,
    })
  }
})
</script>
