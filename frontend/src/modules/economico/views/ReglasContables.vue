<template>
  <AppLayout title="Reglas contables" subtitle="Configuración del mapeo automático apunte → asiento PCESFL">

    <div class="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-700">
      Cada regla define qué cuentas contables se usan al registrar automáticamente
      un asiento cuando entra un apunte de caja. El sistema busca la regla más
      específica (con origen) antes de la comodín (sin origen).
    </div>

    <div class="flex justify-between items-center mb-4">
      <h3 class="font-semibold text-gray-800">Reglas activas</h3>
      <button @click="abrirNuevaRegla" class="btn-primary">+ Nueva regla</button>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Origen</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Cuenta DEBE</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Cuenta HABER</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Orden</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Activa</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="r in reglas" :key="r.id" class="hover:bg-gray-50" :class="!r.activa ? 'opacity-40' : ''">
            <td class="px-3 py-2">
              <span v-if="r.origen" class="text-xs bg-purple-100 text-purple-700 rounded px-1.5 py-0.5">{{ r.origen }}</span>
              <span v-else class="text-xs text-gray-400 italic">Comodín</span>
            </td>
            <td class="px-3 py-2">
              <span class="text-xs rounded px-1.5 py-0.5"
                :class="r.tipoApunte === 'INGRESO' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ r.tipoApunte }}
              </span>
            </td>
            <td class="px-3 py-2 text-center font-mono font-bold text-gray-700">{{ r.cuentaDebeCodig }}</td>
            <td class="px-3 py-2 text-center font-mono font-bold text-gray-700">{{ r.cuentaHaberCodigo }}</td>
            <td class="px-3 py-2 text-gray-600 text-xs max-w-xs truncate">{{ r.descripcion }}</td>
            <td class="px-3 py-2 text-center text-gray-500">{{ r.orden }}</td>
            <td class="px-3 py-2 text-center">
              <span v-if="r.activa" class="text-green-500">✓</span>
              <span v-else class="text-gray-300">✗</span>
            </td>
            <td class="px-3 py-2 text-center">
              <button @click="editarRegla(r)" class="text-xs text-purple-600 hover:underline mr-2">Editar</button>
              <button v-if="r.activa" @click="desactivarRegla(r.id)" class="text-xs text-red-500 hover:underline">Desactivar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!reglas.length" class="text-center text-gray-400 py-8">
      No hay reglas. El sistema usará el mapa por defecto hardcodeado.
    </p>

    <LoadSpinner v-if="loading" />

    <!-- MODAL regla -->
    <div v-if="modalRegla" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalRegla = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">{{ editando ? 'Editar regla' : 'Nueva regla contable' }}</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Origen (vacío = comodín)</label>
              <select v-model="form.origen" class="input">
                <option value="">-- Comodín (cualquier origen) --</option>
                <option value="CUOTA">CUOTA</option>
                <option value="DONACION">DONACION</option>
                <option value="REMESA">REMESA</option>
                <option value="PAGO">PAGO</option>
                <option value="MANUAL">MANUAL</option>
              </select>
            </div>
            <div>
              <label class="label">Tipo de apunte *</label>
              <select v-model="form.tipoApunte" class="input">
                <option value="INGRESO">INGRESO</option>
                <option value="GASTO">GASTO</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Cuenta DEBE (código) *</label>
              <input v-model="form.cuentaDebe" class="input font-mono" placeholder="572" />
              <p class="text-xs text-gray-400 mt-1">Ej: 572 = Bancos c/c</p>
            </div>
            <div>
              <label class="label">Cuenta HABER (código) *</label>
              <input v-model="form.cuentaHaber" class="input font-mono" placeholder="721" />
              <p class="text-xs text-gray-400 mt-1">Ej: 721 = Cuotas socios</p>
            </div>
          </div>
          <div>
            <label class="label">Descripción</label>
            <input v-model="form.descripcion" class="input" placeholder="Ej: Cobro cuota socio → Banco / Cuotas" />
          </div>
          <div>
            <label class="label">Orden (menor = mayor prioridad)</label>
            <input type="number" v-model="form.orden" class="input" min="1" max="999" />
          </div>
        </div>
        <p v-if="errorModal" class="text-red-600 text-sm mt-2">{{ errorModal }}</p>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalRegla = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarRegla" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { useGraphQL } from '@/composables/useGraphQL'

const { query, mutation, loading } = useGraphQL()

const reglas = ref([])
const modalRegla = ref(false)
const editando = ref(null)
const guardando = ref(false)
const errorModal = ref('')

const form = ref({ origen: '', tipoApunte: 'INGRESO', cuentaDebe: '', cuentaHaber: '', descripcion: '', orden: 10 })

const GET_REGLAS = `query { reglasContables { id origen tipoApunte cuentaDebe:cuentaDebeCodig cuentaHaber:cuentaHaberCodigo descripcion orden activa } }`
const CREATE_REGLA = `mutation CrearReglaContable($input: ReglaContableCreateInput!) { crearReglaContable(data: $input) { id } }`
const UPDATE_REGLA = `mutation ActualizarReglaContable($input: ReglaContableUpdateInput!) { actualizarReglaContable(data: $input) { id } }`
const DESACTIVAR_REGLA = `mutation DesactivarRegla($input: ReglaContableUpdateInput!) { actualizarReglaContable(data: $input) { id activa } }`

const cargarReglas = async () => {
  const data = await query(GET_REGLAS)
  reglas.value = data.reglasContables ?? []
}

const abrirNuevaRegla = () => {
  editando.value = null
  form.value = { origen: '', tipoApunte: 'INGRESO', cuentaDebe: '', cuentaHaber: '', descripcion: '', orden: 10 }
  errorModal.value = ''
  modalRegla.value = true
}

const editarRegla = (r) => {
  editando.value = r.id
  form.value = { origen: r.origen ?? '', tipoApunte: r.tipoApunte, cuentaDebe: r.cuentaDebe, cuentaHaber: r.cuentaHaber, descripcion: r.descripcion ?? '', orden: r.orden }
  errorModal.value = ''
  modalRegla.value = true
}

const guardarRegla = async () => {
  errorModal.value = ''
  if (!form.value.cuentaDebe || !form.value.cuentaHaber) { errorModal.value = 'Las cuentas son obligatorias'; return }
  guardando.value = true
  try {
    const input = {
      origen: form.value.origen || null,
      tipoApunte: form.value.tipoApunte,
      cuentaDebeCodig: form.value.cuentaDebe,
      cuentaHaberCodigo: form.value.cuentaHaber,
      descripcion: form.value.descripcion,
      orden: Number(form.value.orden),
      ...(editando.value ? { id: editando.value } : {}),
    }
    const mut = editando.value ? UPDATE_REGLA : CREATE_REGLA
    await mutation(mut, { input })
    modalRegla.value = false
    await cargarReglas()
  } catch (e) {
    errorModal.value = e.message || 'Error al guardar'
  } finally { guardando.value = false }
}

const desactivarRegla = async (id) => {
  if (!confirm('¿Desactivar esta regla?')) return
  await mutation(DESACTIVAR_REGLA, { input: { id, activa: false } })
  await cargarReglas()
}

onMounted(cargarReglas)
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium disabled:opacity-50; }
.btn-secondary { @apply px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400; }
</style>
