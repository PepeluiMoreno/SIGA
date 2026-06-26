<template>
  <div class="space-y-0.5">

    <div
      v-for="item in arbolPlano"
      :key="item.id"
      class="group flex items-center gap-1 min-w-0 py-0.5 px-1 -mx-1 rounded-md hover:bg-slate-50"
      :style="{ paddingLeft: item.depth * 20 + 'px' }"
    >
      <span class="flex-shrink-0 w-4 text-center">
        <span v-if="item.depth === 0" class="text-purple-400 text-xs">●</span>
        <span v-else class="text-gray-300 text-sm">└</span>
      </span>

      <!-- Lectura -->
      <template v-if="editandoId !== item.id">
        <!-- Nombre + badge ámbito inline -->
        <div class="flex-1 flex items-center gap-1.5 min-w-0">
          <span :class="item.depth === 0 ? 'text-sm font-medium text-gray-800' : 'text-sm text-gray-800'" class="truncate">
            {{ item.nombre }}
          </span>
          <span v-if="item.ambitoGeografico"
            class="flex-shrink-0 px-1.5 py-0.5 text-xs rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200 leading-none">
            {{ item.ambitoGeografico.nombre }}
          </span>
          <span v-else
            class="flex-shrink-0 px-1.5 py-0.5 text-xs rounded-full bg-slate-50 text-slate-400 border border-slate-200 leading-none italic">
            sin ámbito
          </span>
          <span v-if="item.denominacionSingular" class="flex-shrink-0 text-xs text-slate-400 italic truncate"
            title="Denominación interna de la unidad en este ámbito">
            → {{ item.denominacionSingular }}
          </span>
        </div>

        <!-- Acciones: se revelan al pasar el ratón sobre la fila -->
        <div class="flex items-center gap-0.5 flex-shrink-0 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
          <button v-if="item.depth > 0" type="button" @click="promover(item)" :disabled="guardando"
            title="Subir un nivel (promover)"
            class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">↑</button>
          <button v-if="prevSiblingOf(item)" type="button" @click="demover(item)" :disabled="guardando"
            title="Bajar un nivel (anidar en el anterior)"
            class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">↓</button>
          <span class="w-px h-4 bg-slate-200 mx-0.5" />
          <button type="button" @click="añadirSuperior(item)" :disabled="guardando"
            title="Insertar un nivel por encima de este"
            class="w-7 h-7 grid place-items-center text-xs font-mono text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">⊕↑</button>
          <button type="button" @click="añadirHijo(item)" :disabled="guardando"
            title="Añadir un subnivel (hijo)"
            class="w-7 h-7 grid place-items-center text-xs font-mono text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50 disabled:opacity-30">⊕↓</button>
          <span class="w-px h-4 bg-slate-200 mx-0.5" />
          <button type="button" @click="iniciarEdicion(item)"
            title="Editar nombre, ámbito y denominación"
            class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-purple-700 rounded hover:bg-purple-50">✎</button>
          <button v-if="item.depth > 0 || raices.length > 1" type="button" @click="iniciarEliminar(item)" :disabled="guardando"
            title="Eliminar nivel"
            class="w-7 h-7 grid place-items-center text-sm text-slate-400 hover:text-red-500 rounded hover:bg-red-50 disabled:opacity-30">×</button>
        </div>
      </template>

      <!-- Edición: mini-formulario con etiquetas -->
      <template v-else>
        <div class="flex-1 min-w-0 rounded-lg border border-purple-300 bg-purple-50/40 p-2.5 space-y-2">
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
      </template>
    </div>

    <div class="flex items-center justify-between gap-3 pt-1.5 border-t border-slate-100 mt-1">
      <button type="button" @click="añadirRaiz" :disabled="guardando"
        class="inline-flex items-center gap-1.5 text-xs font-medium text-purple-600 hover:text-purple-800 disabled:opacity-40">
        <span class="grid place-items-center w-5 h-5 rounded-full border border-purple-300 text-purple-500 font-mono leading-none">+</span>
        Añadir nivel raíz
      </button>
      <span class="hidden sm:block text-[11px] text-slate-400 text-right leading-tight">
        Al pasar el ratón por un nivel: <span class="font-mono">↑</span> subir ·
        <span class="font-mono">↓</span> anidar · <span class="font-mono">⊕↑</span> insertar encima ·
        <span class="font-mono">⊕↓</span> subnivel · <span class="font-mono">✎</span> editar ·
        <span class="font-mono">×</span> borrar
      </span>
    </div>

    <ErrorAlert v-if="errorMsg" :message="errorMsg" />

    <p class="text-xs text-gray-400 pt-0.5">
      <template v-if="arbolPlano.length <= 1">Organización simple (sin subniveles)</template>
      <template v-else>Organización extendida · {{ arbolPlano.filter(n => n.depth > 0).map(n => n.nombre).join(' › ') }}</template>
    </p>

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

const raices = computed(() => buildTree(tiposTerritoriales.value))

const arbolPlano = computed(() => {
  const lista = []
  const dfs = (nodo, depth) => {
    lista.push({ ...nodo, depth })
    nodo.hijos.forEach(h => dfs(h, depth + 1))
  }
  raices.value.forEach(r => dfs(r, 0))
  return lista
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
  await actualizarTipo({
    id: tipo.id,
    nombre: formNombre.value.trim(),
    ambitoGeograficoId: formAmbitoId.value || null,
    denominacionSingular: formDenomSingular.value.trim() || null,
    denominacionPlural: formDenomPlural.value.trim() || null,
  })
  editandoId.value = null
  await recargarConfig()
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
defineExpose({ estructuraProtegida })

onMounted(async () => {
  await Promise.all([cargarTipos(), cargarArbol(), cargarAmbitos()])
  if (tiposTerritoriales.value.length === 0) {
    await crearTipo({
      nombre: 'Asociación',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      activo: true,
    })
  }
})
</script>
