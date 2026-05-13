<template>
  <AppLayout title="Papelera" subtitle="Elementos enviados a la papelera — puedes restaurarlos o eliminarlos definitivamente">

    <!-- Tabs por tipo -->
    <div class="flex gap-2 mb-6 flex-wrap">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="tabActivo = tab.key"
        class="h-9 px-4 text-sm font-medium rounded-lg border transition-colors"
        :class="tabActivo === tab.key
          ? 'bg-indigo-600 text-white border-indigo-600'
          : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-50'"
      >
        {{ tab.label }}
        <span v-if="counts[tab.key]" class="ml-1.5 text-xs opacity-75">({{ counts[tab.key] }})</span>
      </button>
    </div>

    <div v-if="loading" class="py-12 text-center text-sm text-slate-400">Cargando…</div>
    <div v-else-if="!itemsActivos.length" class="py-16 text-center">
      <div class="text-4xl mb-3">🗑️</div>
      <p class="text-sm text-slate-400">La papelera está vacía para esta categoría.</p>
    </div>

    <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Nombre</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Tipo</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Eliminado el</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="item in itemsActivos" :key="item.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3 font-medium text-slate-900">{{ item._nombre }}</td>
            <td class="px-4 py-3 text-slate-500 text-xs">{{ tabs.find(t => t.key === tabActivo)?.label }}</td>
            <td class="px-4 py-3 text-slate-400 text-xs">{{ formatFecha(item.fechaEliminacion) }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2 justify-end">
                <!-- Restaurar -->
                <button
                  @click="restaurar(item)"
                  class="h-8 px-3 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                >
                  Restaurar
                </button>
                <!-- Eliminar definitivamente -->
                <button
                  @click="pendingDelete = item; showConfirm = true"
                  class="h-8 px-3 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
                >
                  Eliminar def.
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal confirmación hard-delete -->
    <ConfirmModal
      v-model="showConfirm"
      title="¿Eliminar definitivamente?"
      title-soft="¿Eliminar definitivamente?"
      :message="pendingDelete ? `«${pendingDelete._nombre}» será eliminado de forma permanente e irrecuperable.` : ''"
      confirm-label="Eliminar para siempre"
      @confirm="confirmarEliminar"
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { graphqlClient } from '@/graphql/client'

const tabs = [
  { key: 'miembros', label: 'Miembros' },
  { key: 'acciones', label: 'Acciones' },
  { key: 'grupos', label: 'Grupos' },
  { key: 'campanias', label: 'Campañas' },
]

const tabActivo = ref('miembros')
const loading = ref(false)
const items = ref({ miembros: [], acciones: [], grupos: [], campanias: [] })
const showConfirm = ref(false)
const pendingDelete = ref(null)

const counts = computed(() => {
  const r = {}
  for (const k of Object.keys(items.value)) {
    r[k] = items.value[k].length
  }
  return r
})

const itemsActivos = computed(() => items.value[tabActivo.value] || [])

const QUERIES = {
  miembros: `query { miembros(filter: { eliminado: { eq: true } }) { id nombre apellido1 fechaEliminacion } }`,
  acciones: `query { acciones(filter: { eliminado: { eq: true } }) { id nombre fechaEliminacion } }`,
  grupos: `query { gruposTrabajo(filter: { eliminado: { eq: true } }) { id nombre fechaEliminacion } }`,
  campanias: `query { campanias(filter: { eliminado: { eq: true } }) { id nombre fechaEliminacion } }`,
}

const RESTORE_QUERY = {
  miembros: `mutation RestaurarMiembro($id: UUID!) { restaurarMiembro(id: $id) { id } }`,
  acciones: `mutation RestaurarAccion($id: UUID!) { restaurarAccion(id: $id) { id } }`,
  grupos: `mutation RestaurarGrupo($id: UUID!) { restaurarGrupoTrabajo(id: $id) { id } }`,
  campanias: `mutation RestaurarCampania($id: UUID!) { restaurarCampania(id: $id) { id } }`,
}

const HARD_DELETE_QUERY = {
  miembros: `mutation EliminarMiembro($id: UUID!) { eliminarMiembros(filter: { id: { eq: $id } }) { id } }`,
  acciones: `mutation EliminarAccion($id: UUID!) { eliminarAcciones(filter: { id: { eq: $id } }) { id } }`,
  grupos: `mutation EliminarGrupo($id: UUID!) { eliminarGruposTrabajo(filter: { id: { eq: $id } }) { id } }`,
  campanias: `mutation EliminarCampania($id: UUID!) { eliminarCampanias(filter: { id: { eq: $id } }) { id } }`,
}

function nombreItem(item, tipo) {
  if (tipo === 'miembros') return `${item.nombre} ${item.apellido1 || ''}`.trim()
  return item.nombre || item.id
}

async function cargarTab(tipo) {
  loading.value = true
  try {
    const data = await graphqlClient.request(QUERIES[tipo])
    const raw = data[tipo === 'grupos' ? 'gruposTrabajo' : tipo] || []
    items.value[tipo] = raw.map(i => ({ ...i, _nombre: nombreItem(i, tipo) }))
  } catch (e) {
    console.error('Error cargando papelera:', e)
  } finally {
    loading.value = false
  }
}

async function restaurar(item) {
  try {
    await graphqlClient.request(RESTORE_QUERY[tabActivo.value], { id: item.id })
    items.value[tabActivo.value] = items.value[tabActivo.value].filter(i => i.id !== item.id)
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error restaurando')
  }
}

async function confirmarEliminar() {
  if (!pendingDelete.value) return
  const item = pendingDelete.value
  pendingDelete.value = null
  try {
    await graphqlClient.request(HARD_DELETE_QUERY[tabActivo.value], { id: item.id })
    items.value[tabActivo.value] = items.value[tabActivo.value].filter(i => i.id !== item.id)
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando')
  }
}

function formatFecha(f) {
  if (!f) return '—'
  return new Date(f).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

watch(tabActivo, (tipo) => cargarTab(tipo))
onMounted(() => cargarTab(tabActivo.value))
</script>
