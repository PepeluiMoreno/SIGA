<template>
  <div class="space-y-0.5">

    <!-- Árbol de tipos territoriales -->
    <div
      v-for="item in arbolPlano"
      :key="item.id"
      class="flex items-center gap-1.5 min-w-0"
      :style="{ paddingLeft: item.depth * 20 + 'px' }"
    >
      <span class="flex-shrink-0 w-4 text-center">
        <span v-if="item.depth === 0" class="text-purple-400 text-xs">●</span>
        <span v-else class="text-gray-300 text-sm">└</span>
      </span>

      <!-- Lectura -->
      <template v-if="editandoId !== item.id">
        <!-- Raíz: nombre siempre es el de la organización, no editable aquí -->
        <span v-if="item.depth === 0"
          class="flex-1 text-sm font-medium text-gray-800 truncate">
          {{ orgConfig.nombre || item.nombre }}
        </span>
        <span v-else class="flex-1 text-sm text-gray-800 truncate">{{ item.nombre }}</span>

        <button v-if="item.depth > 0" type="button" @click="iniciarEdicion(item)"
          class="text-xs text-gray-400 hover:text-gray-700 px-1 py-0.5 rounded hover:bg-gray-100 flex-shrink-0">Editar</button>
        <span v-else class="w-8 flex-shrink-0" />

        <button v-if="!estructuraProtegida" type="button" @click="añadirHijo(item)" :disabled="guardando"
          class="text-xs text-purple-500 hover:text-purple-700 px-1 py-0.5 rounded hover:bg-purple-50 disabled:opacity-40 flex-shrink-0">+sub</button>
        <span v-else class="w-8 flex-shrink-0" />

        <!-- La raíz (depth=0) no se puede eliminar: es la propia organización -->
        <button v-if="item.depth > 0 && !estructuraProtegida" type="button" @click="eliminarNivel(item)" :disabled="guardando"
          class="text-xs text-gray-400 hover:text-red-500 px-1 py-0.5 rounded hover:bg-red-50 disabled:opacity-40 flex-shrink-0">✕</button>
        <span v-else class="w-5 flex-shrink-0" />
      </template>

      <!-- Edición inline -->
      <template v-else>
        <input v-model="formNombre" type="text" autofocus
          class="flex-1 min-w-0 border border-purple-400 rounded px-2 py-0.5 text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
          @keydown.enter.prevent="guardar(item)"
          @keydown.escape="editandoId = null" />
        <button type="button" @click="guardar(item)"
          class="text-xs px-2 py-0.5 bg-purple-600 text-white rounded hover:bg-purple-700 flex-shrink-0">OK</button>
        <button type="button" @click="editandoId = null"
          class="text-xs px-1.5 py-0.5 text-gray-500 border border-gray-200 rounded hover:bg-gray-50 flex-shrink-0">✕</button>
      </template>
    </div>

    <p v-if="errorMsg" class="text-xs text-red-500 mt-0.5">{{ errorMsg }}</p>

    <!-- Descripción -->
    <p class="text-xs text-gray-400 pt-0.5">
      <template v-if="arbolPlano.length <= 1">Organización simple (sin subniveles)</template>
      <template v-else>Organización extendida · {{ arbolPlano.filter(n => n.depth > 0).map(n => n.nombre).join(' › ') }}</template>
    </p>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useOrgConfigStore } from '@/stores/orgConfig'

const { tipos, unidades, cargarTipos, cargarArbol, crearTipo, actualizarTipo, eliminarTipo } = useUnidadesOrganizativas()
const orgConfig = useOrgConfigStore()

// Estructura protegida si ya hay agrupaciones en la BD
const estructuraProtegida = computed(() => unidades.value.length > 0)

async function recargarConfig() {
  orgConfig.invalidate()
  await orgConfig.fetchConfig()
}

const editandoId = ref(null)
const formNombre = ref('')
const guardando = ref(false)
const errorMsg = ref('')

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

const descendientes = (nodo) => {
  const ids = [nodo.id]
  const dfs = (n) => n.hijos?.forEach(h => { ids.push(h.id); dfs(h) })
  dfs(nodo)
  return ids
}

const iniciarEdicion = (tipo) => {
  formNombre.value = tipo.nombre
  editandoId.value = tipo.id
}

const guardar = async (tipo) => {
  if (!formNombre.value.trim()) return
  await actualizarTipo({ id: tipo.id, nombre: formNombre.value.trim(), vinculo: tipo.vinculo })
  editandoId.value = null
  await recargarConfig()
}

const añadirHijo = async (padre) => {
  guardando.value = true
  errorMsg.value = ''
  try {
    await crearTipo({
      nombre: 'Nuevo subnivel',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      nivel: (padre.nivel ?? 0) + 1,
      padreTipoId: padre.id,
      activo: true,
    })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al crear'
  } finally {
    guardando.value = false
  }
}

const eliminarNivel = async (nodo) => {
  guardando.value = true
  errorMsg.value = ''
  try {
    const ids = descendientes(nodo)
    for (const id of ids.reverse()) {
      await eliminarTipo(id)
    }
    await recargarConfig()
  } catch (e) {
    errorMsg.value = e?.response?.errors?.[0]?.message ?? 'Error al eliminar'
  } finally {
    guardando.value = false
  }
}

defineExpose({ estructuraProtegida })

onMounted(async () => {
  await Promise.all([cargarTipos(), cargarArbol()])
  // Si no existe ningún tipo territorial, crear automáticamente la raíz
  if (tiposTerritoriales.value.length === 0) {
    await crearTipo({
      nombre: 'Asociación',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      nivel: 1,
      activo: true,
    })
  }
})
</script>
