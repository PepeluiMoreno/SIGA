<template>
  <!-- Pantalla 5.2 — Catálogo de motivos de reducción de cuota (Flujo 1, D1.1) -->
  <AppLayout title="Motivos de reducción de cuota" subtitle="Catálogo de razones por las que un socio paga menos">

    <div class="bg-amber-50 border border-amber-100 rounded-lg p-3 text-sm text-amber-800 mb-4">
      <strong>Regla del sistema (D1.4):</strong> los motivos con reducción del <b>100%</b> excluyen al socio del proceso —
      no se le emite cuota. Para socios que pagan 0€ pero sí deben aparecer, usa otro modelo.
    </div>

    <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div class="flex justify-between items-center p-4 border-b border-slate-100">
        <h3 class="font-semibold text-slate-800">{{ motivos.length }} motivos registrados</h3>
        <button @click="abrirModal()" class="btn-primary text-sm">+ Nuevo motivo</button>
      </div>
      <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600">
          <tr>
            <th class="px-3 py-2 text-left w-full sm:w-32">Código</th>
            <th class="px-3 py-2 text-left">Nombre</th>
            <th class="px-3 py-2 text-right w-full sm:w-32">% Reducción</th>
            <th class="px-3 py-2 text-center w-24">Efecto</th>
            <th class="px-3 py-2 text-center w-20">Activo</th>
            <th class="px-3 py-2 text-center w-20">Editar</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="!motivos.length">
            <td colspan="6" class="text-center text-slate-400 py-8">No hay motivos registrados.</td>
          </tr>
          <tr v-for="m in motivos" :key="m.id" class="hover:bg-slate-50">
            <td class="px-3 py-1.5 font-mono text-xs">{{ m.codigo }}</td>
            <td class="px-3 py-1.5">{{ m.nombre }}<p class="text-xs text-slate-500" v-if="m.descripcion">{{ m.descripcion }}</p></td>
            <td class="px-3 py-1.5 text-right font-mono">{{ m.porcentajeReduccion }}%</td>
            <td class="px-3 py-1.5 text-center">
              <span v-if="m.porcentajeReduccion >= 100" class="text-xs bg-amber-100 text-amber-700 rounded px-2 py-0.5">EXCLUIDO</span>
              <span v-else class="text-xs text-slate-500">paga {{ (100 - m.porcentajeReduccion).toFixed(0) }}%</span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span v-if="m.activo" class="text-green-600">✓</span>
              <span v-else class="text-slate-400">✗</span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <button @click="abrirModal(m)" class="text-blue-600 hover:underline text-xs">Editar</button>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- Modal alta/edición -->
    <div v-if="modal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modal = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">
          {{ form.id ? 'Editar motivo' : 'Nuevo motivo de reducción' }}
        </h3>
        <div class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Código *</label>
              <input v-model="form.codigo" :disabled="!!form.id" class="input font-mono uppercase" placeholder="JOVEN" />
              <p v-if="form.id" class="text-xs text-slate-400 mt-0.5">El código no se puede cambiar después de creado.</p>
            </div>
            <div>
              <label class="label">% Reducción *</label>
              <input
                v-model.number="form.porcentajeReduccion"
                type="number" min="0" max="100" step="0.01"
                :disabled="porcentajeBloqueado"
                class="input disabled:bg-amber-50 disabled:text-amber-900"
              />
              <p v-if="porcentajeBloqueado" class="text-xs text-amber-700 mt-0.5">
                🔒 Este motivo ya tiene cuotas con recibo emitido. El porcentaje queda congelado (D1.5).
                Para cambiar la rebaja de un socio: anular su cuota → cambiar de motivo → re-emitir.
              </p>
              <p v-else-if="form.porcentajeReduccion >= 100" class="text-xs text-amber-600 mt-0.5">
                ≥100% → excluye al socio del proceso (D1.4)
              </p>
            </div>
          </div>
          <div>
            <label class="label">Nombre *</label>
            <input v-model="form.nombre" class="input" placeholder="Estudiante / Joven" />
          </div>
          <div>
            <label class="label">Descripción</label>
            <textarea v-model="form.descripcion" class="input h-20" placeholder="Cuota reducida para socios menores de 30 años o estudiantes acreditados" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Orden</label>
              <input v-model.number="form.orden" type="number" class="input" />
            </div>
            <div>
              <label class="label">Activo</label>
              <select v-model="form.activo" class="input">
                <option :value="true">Sí</option>
                <option :value="false">No</option>
              </select>
            </div>
          </div>
        </div>
        <ErrorAlert v-if="error" :message="error" />
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modal = false" class="btn-secondary">Cancelar</button>
          <button @click="guardar" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_MOTIVOS_REDUCCION,
  CREATE_MOTIVO_REDUCCION,
  UPDATE_MOTIVO_REDUCCION,
  MOTIVO_TIENE_RECIBOS,
} from '@/graphql/queries/financiero'

const { query, mutation } = useGraphQL()

const motivos = ref([])
const modal = ref(false)
const form = ref({})
const guardando = ref(false)
const error = ref('')
const porcentajeBloqueado = ref(false)  // D1.5

const cargar = async () => {
  const data = await query(GET_MOTIVOS_REDUCCION)
  motivos.value = (data.motivosReduccionCuota || []).slice().sort((a, b) => a.orden - b.orden)
}

const abrirModal = async (m = null) => {
  form.value = m
    ? { ...m }
    : { codigo: '', nombre: '', descripcion: '', porcentajeReduccion: 0, orden: 0, activo: true }
  error.value = ''
  porcentajeBloqueado.value = false
  modal.value = true
  // D1.5: si es edición, consultar si el % está congelado
  if (m?.id) {
    try {
      const data = await query(MOTIVO_TIENE_RECIBOS, { motivoId: m.id })
      porcentajeBloqueado.value = !!data.motivoTieneRecibos
    } catch (e) {
      console.warn('No se pudo comprobar el estado del motivo:', e?.message)
    }
  }
}

const guardar = async () => {
  error.value = ''
  if (!form.value.codigo || !form.value.nombre) { error.value = 'Código y nombre son obligatorios'; return }
  if (form.value.porcentajeReduccion < 0 || form.value.porcentajeReduccion > 100) {
    error.value = 'El porcentaje debe estar entre 0 y 100'; return
  }
  guardando.value = true
  try {
    if (form.value.id) {
      const f = form.value
      await mutation(UPDATE_MOTIVO_REDUCCION, {
        id: f.id,
        codigo: f.codigo,
        nombre: f.nombre,
        porcentajeReduccion: porcentajeBloqueado.value ? null : f.porcentajeReduccion,
        descripcion: f.descripcion ?? null,
        orden: f.orden ?? null,
        activo: f.activo,
      })
    } else {
      const f = form.value
      await mutation(CREATE_MOTIVO_REDUCCION, {
        codigo: (f.codigo || '').toUpperCase().trim(),
        nombre: f.nombre,
        porcentajeReduccion: f.porcentajeReduccion ?? 0,
        descripcion: f.descripcion ?? null,
        orden: f.orden ?? 0,
        activo: f.activo !== false,
      })
    }
    modal.value = false
    await cargar()
  } catch (e) {
    error.value = e.message || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-slate-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-slate-100; }
</style>
