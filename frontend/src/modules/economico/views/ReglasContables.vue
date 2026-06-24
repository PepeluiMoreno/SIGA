<template>
  <AppLayout title="Reglas contables" subtitle="Configuración del mapeo automático apunte → asiento PCESFL">
    <div class="page-body">
      <ErrorAlert variant="info">
        Cada regla define qué cuentas contables se usan al registrar automáticamente un asiento
        cuando entra un apunte de caja. El sistema busca la regla más específica (con origen)
        antes de la comodín (sin origen).
      </ErrorAlert>

      <div class="card overflow-hidden">
        <div class="flex justify-between items-center p-4 border-b border-slate-100">
          <h3 class="font-semibold text-gray-800">Reglas activas</h3>
          <AppButton size="sm" :icon="PlusIcon" @click="abrirNuevaRegla">Nueva regla</AppButton>
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
                <td class="px-3 py-2 text-center whitespace-nowrap">
                  <AppButton variant="link" size="xs" @click="editarRegla(r)">Editar</AppButton>
                  <AppButton v-if="r.activa" variant="link" size="xs" class="text-red-500 ml-2" @click="desactivarRegla(r.id)">Desactivar</AppButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-if="!reglas.length && !loading" class="text-center text-gray-400 py-8">
          No hay reglas. El sistema usará el mapa por defecto hardcodeado.
        </p>
        <EstadoCarga v-if="loading" mensaje="Cargando reglas…" />
      </div>
    </div>

    <!-- Alta / edición (drawer; los modales quedan para advertencias) -->
    <AppDrawer v-model="modalRegla" :title="editando ? 'Editar regla' : 'Nueva regla contable'" size="lg">
      <div class="space-y-4">
        <AppFormGrid cols="2">
          <AppFormField label="Origen (vacío = comodín)">
            <AppSelect v-model="form.origen" width="md">
              <option value="">-- Comodín (cualquier origen) --</option>
              <option value="CUOTA">CUOTA</option>
              <option value="DONACION">DONACION</option>
              <option value="REMESA">REMESA</option>
              <option value="PAGO">PAGO</option>
              <option value="MANUAL">MANUAL</option>
            </AppSelect>
          </AppFormField>
          <AppFormField label="Tipo de apunte" required>
            <AppSelect v-model="form.tipoApunte" width="sm">
              <option value="INGRESO">INGRESO</option>
              <option value="GASTO">GASTO</option>
            </AppSelect>
          </AppFormField>
        </AppFormGrid>

        <AppFormGrid cols="2">
          <AppFormField label="Cuenta DEBE (código)" required help="Ej: 572 = Bancos c/c">
            <AppInput v-model="form.cuentaDebe" width="sm" class="font-mono" placeholder="572" />
          </AppFormField>
          <AppFormField label="Cuenta HABER (código)" required help="Ej: 721 = Cuotas socios">
            <AppInput v-model="form.cuentaHaber" width="sm" class="font-mono" placeholder="721" />
          </AppFormField>
        </AppFormGrid>

        <AppFormField label="Descripción">
          <AppInput v-model="form.descripcion" placeholder="Ej: Cobro cuota socio → Banco / Cuotas" />
        </AppFormField>

        <AppFormField label="Orden" help="Menor = mayor prioridad">
          <AppInput v-model="form.orden" type="number" width="xs" />
        </AppFormField>

        <ErrorAlert v-if="errorModal" :message="errorModal" />
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="modalRegla = false">Cancelar</AppButton>
        <AppButton :loading="guardando" @click="guardarRegla">Guardar</AppButton>
      </template>
    </AppDrawer>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import {
  AppLayout, AppButton, AppDrawer,
  AppFormField, AppFormGrid, AppInput, AppSelect, EstadoCarga, ErrorAlert,
} from '@/components/common'
import { useConfirm } from '@/composables/useConfirm'
import { useGraphQL } from '@/composables/useGraphQL'

const confirmDialog = useConfirm()
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
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: '¿Desactivar esta regla?', variante: 'aviso' }))) return
  await mutation(DESACTIVAR_REGLA, { input: { id, activa: false } })
  await cargarReglas()
}

onMounted(cargarReglas)
</script>
