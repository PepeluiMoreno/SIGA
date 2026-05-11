<template>
  <AppLayout title="Estructura Organizativa" subtitle="Define los tipos de unidades que componen tu organización">

    <!-- ── Niveles territoriales ──────────────────────────────────────────── -->
    <div class="bg-white rounded-lg shadow border border-gray-100 mb-6">
      <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">Jerarquía territorial</h2>
        <p class="text-sm text-gray-500 mt-0.5">Hasta 3 niveles jerárquicos configurables</p>
      </div>
      <div class="divide-y divide-gray-50">
        <div v-for="nivel in [1, 2, 3]" :key="nivel" class="px-6 py-4 flex items-center gap-4">
          <div class="w-8 h-8 rounded-full bg-purple-100 text-purple-700 text-sm font-bold flex items-center justify-center flex-shrink-0">
            {{ nivel }}
          </div>
          <template v-if="tipoNivel(nivel)">
            <div v-if="editandoNivel !== nivel" class="flex-1 flex items-center gap-3">
              <span class="font-medium text-gray-800">{{ tipoNivel(nivel).nombre }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full" :class="vinculoBadge(tipoNivel(nivel).vinculo)">
                {{ tipoNivel(nivel).vinculo }}
              </span>
            </div>
            <div v-else class="flex-1 flex items-center gap-3">
              <input v-model="formNivel.nombre" type="text" class="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm" />
              <select v-model="formNivel.vinculo" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
                <option value="INTERNA">INTERNA</option>
                <option value="FILIAL">FILIAL</option>
                <option value="FEDERADA">FEDERADA</option>
              </select>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <template v-if="editandoNivel === nivel">
                <button @click="guardarNivel(nivel)" class="px-3 py-1.5 bg-purple-600 text-white text-xs rounded hover:bg-purple-700">Guardar</button>
                <button @click="editandoNivel = null" class="px-3 py-1.5 text-gray-600 text-xs border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
              </template>
              <template v-else>
                <button @click="iniciarEdicionNivel(nivel)" class="text-gray-400 hover:text-gray-600 text-sm">✏️</button>
              </template>
            </div>
          </template>
          <template v-else>
            <span class="flex-1 text-sm text-gray-400 italic">Nivel {{ nivel }} no activado</span>
            <button @click="activarNivel(nivel)"
              class="px-3 py-1.5 text-xs border border-purple-300 text-purple-600 rounded hover:bg-purple-50">
              + Activar nivel {{ nivel }}
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- ── Tipos transversales ────────────────────────────────────────────── -->
    <div class="bg-white rounded-lg shadow border border-gray-100">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div>
          <h2 class="font-semibold text-gray-800">Tipos transversales</h2>
          <p class="text-sm text-gray-500 mt-0.5">Secciones funcionales, áreas programáticas y unidades administrativas</p>
        </div>
        <button @click="abrirNuevoTransversal"
          class="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700">
          + Añadir tipo
        </button>
      </div>

      <div v-if="tiposTransversales.length === 0" class="text-center py-10 text-gray-400 text-sm">
        No hay tipos transversales definidos
      </div>

      <div v-else class="divide-y divide-gray-50">
        <div v-for="tipo in tiposTransversales" :key="tipo.id" class="px-6 py-4">
          <div v-if="editandoTransversal !== tipo.id" class="flex items-center gap-3">
            <span class="text-lg">{{ iconNaturaleza(tipo.naturaleza) }}</span>
            <div class="flex-1">
              <span class="font-medium text-gray-800">{{ tipo.nombre }}</span>
              <span class="ml-2 text-xs text-gray-500">{{ tipo.naturaleza }}</span>
            </div>
            <span class="text-xs px-2 py-0.5 rounded-full" :class="vinculoBadge(tipo.vinculo)">{{ tipo.vinculo }}</span>
            <button @click="iniciarEdicionTransversal(tipo)" class="text-gray-400 hover:text-gray-600 text-sm ml-2">✏️</button>
            <button @click="confirmarEliminar(tipo)" class="text-gray-400 hover:text-red-500 text-sm">🗑</button>
          </div>
          <div v-else class="flex items-center gap-3">
            <input v-model="formTransversal.nombre" type="text" placeholder="Nombre" class="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm" />
            <select v-model="formTransversal.naturaleza" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
              <option value="FUNCIONAL">FUNCIONAL</option>
              <option value="PROGRAMATICA">PROGRAMATICA</option>
              <option value="ADMINISTRATIVA">ADMINISTRATIVA</option>
            </select>
            <select v-model="formTransversal.vinculo" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
              <option value="INTERNA">INTERNA</option>
              <option value="FILIAL">FILIAL</option>
              <option value="FEDERADA">FEDERADA</option>
            </select>
            <button @click="guardarTransversal" class="px-3 py-1.5 bg-purple-600 text-white text-xs rounded hover:bg-purple-700">Guardar</button>
            <button @click="editandoTransversal = null" class="px-3 py-1.5 text-gray-600 text-xs border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
          </div>
        </div>
      </div>

      <!-- Formulario nuevo transversal inline -->
      <div v-if="mostrarNuevoTransversal" class="px-6 py-4 bg-purple-50 border-t border-purple-100 flex items-center gap-3">
        <input v-model="formNuevoTransversal.nombre" type="text" placeholder="Nombre del tipo" class="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm" />
        <select v-model="formNuevoTransversal.naturaleza" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
          <option value="FUNCIONAL">FUNCIONAL</option>
          <option value="PROGRAMATICA">PROGRAMATICA</option>
          <option value="ADMINISTRATIVA">ADMINISTRATIVA</option>
        </select>
        <select v-model="formNuevoTransversal.vinculo" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
          <option value="INTERNA">INTERNA</option>
          <option value="FILIAL">FILIAL</option>
          <option value="FEDERADA">FEDERADA</option>
        </select>
        <button @click="crearTransversal" class="px-3 py-1.5 bg-purple-600 text-white text-xs rounded hover:bg-purple-700">Crear</button>
        <button @click="mostrarNuevoTransversal = false" class="px-3 py-1.5 text-gray-600 text-xs border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
      </div>
    </div>

    <!-- Modal confirmación eliminar -->
    <div v-if="tipoAEliminar" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
        <h3 class="font-semibold text-gray-900 mb-2">¿Eliminar tipo?</h3>
        <p class="text-sm text-gray-600 mb-4">
          Se eliminará "{{ tipoAEliminar.nombre }}". Las unidades que lo usen perderán su tipo.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="tipoAEliminar = null" class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancelar</button>
          <button @click="ejecutarEliminar" class="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700">Eliminar</button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'

const { tipos, cargarTipos, crearTipo, actualizarTipo, eliminarTipo } = useUnidadesOrganizativas()

const editandoNivel = ref(null)
const formNivel = ref({ nombre: '', vinculo: 'INTERNA' })

const editandoTransversal = ref(null)
const formTransversal = ref({ nombre: '', naturaleza: 'FUNCIONAL', vinculo: 'INTERNA' })

const mostrarNuevoTransversal = ref(false)
const formNuevoTransversal = ref({ nombre: '', naturaleza: 'FUNCIONAL', vinculo: 'INTERNA' })

const tipoAEliminar = ref(null)

const tiposTerritoriales = computed(() =>
  tipos.value.filter(t => t.naturaleza === 'TERRITORIAL' && t.nivel != null)
)

const tiposTransversales = computed(() =>
  tipos.value.filter(t => t.nivel == null)
)

const tipoNivel = (nivel) => tiposTerritoriales.value.find(t => t.nivel === nivel)

const iconNaturaleza = (n) => ({ TERRITORIAL: '📍', FUNCIONAL: '🔧', PROGRAMATICA: '🌍', ADMINISTRATIVA: '🏢' }[n] ?? '📦')

const vinculoBadge = (v) => ({
  INTERNA:  'bg-green-100 text-green-700',
  FILIAL:   'bg-blue-100 text-blue-700',
  FEDERADA: 'bg-orange-100 text-orange-700',
}[v] ?? 'bg-gray-100 text-gray-600')

const iniciarEdicionNivel = (nivel) => {
  const tipo = tipoNivel(nivel)
  formNivel.value = { nombre: tipo.nombre, vinculo: tipo.vinculo }
  editandoNivel.value = nivel
}

const guardarNivel = async (nivel) => {
  const tipo = tipoNivel(nivel)
  await actualizarTipo({ id: tipo.id, ...formNivel.value })
  editandoNivel.value = null
}

const activarNivel = async (nivel) => {
  await crearTipo({ nombre: `Nivel ${nivel}`, naturaleza: 'TERRITORIAL', vinculo: 'INTERNA', nivel, activo: true })
}

const iniciarEdicionTransversal = (tipo) => {
  formTransversal.value = { nombre: tipo.nombre, naturaleza: tipo.naturaleza, vinculo: tipo.vinculo }
  editandoTransversal.value = tipo.id
}

const guardarTransversal = async () => {
  await actualizarTipo({ id: editandoTransversal.value, ...formTransversal.value })
  editandoTransversal.value = null
}

const abrirNuevoTransversal = () => {
  formNuevoTransversal.value = { nombre: '', naturaleza: 'FUNCIONAL', vinculo: 'INTERNA' }
  mostrarNuevoTransversal.value = true
}

const crearTransversal = async () => {
  if (!formNuevoTransversal.value.nombre.trim()) return
  await crearTipo({ ...formNuevoTransversal.value, activo: true })
  mostrarNuevoTransversal.value = false
}

const confirmarEliminar = (tipo) => { tipoAEliminar.value = tipo }

const ejecutarEliminar = async () => {
  await eliminarTipo(tipoAEliminar.value.id)
  tipoAEliminar.value = null
}

onMounted(cargarTipos)
</script>
