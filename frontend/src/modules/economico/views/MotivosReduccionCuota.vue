<template>
  <!-- Pantalla 5.2 — Catálogo de motivos de reducción de cuota (Flujo 1, D1.1) -->
  <AppLayout title="Motivos de reducción de cuota" subtitle="Catálogo de razones por las que un socio paga menos">
    <div class="page-body">
      <ErrorAlert variant="warning" title="Regla del sistema (D1.4)">
        Los motivos con reducción del <b>100%</b> excluyen al socio del proceso — no se le emite cuota.
        Para socios que pagan 0&euro; pero sí deben aparecer, usa otro modelo.
      </ErrorAlert>

      <div class="card overflow-hidden">
        <div class="flex justify-between items-center p-4 border-b border-slate-100">
          <h3 class="font-semibold text-slate-800">{{ motivos.length }} motivos registrados</h3>
          <AppButton size="sm" :icon="PlusIcon" @click="abrirModal()">Nuevo motivo</AppButton>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
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
                  <AppButton variant="link" size="xs" @click="abrirModal(m)">Editar</AppButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Alta / edición (drawer; los modales quedan para advertencias) -->
    <AppDrawer v-model="modal" :title="form.id ? 'Editar motivo' : 'Nuevo motivo de reducción'" size="md">
      <div class="space-y-4">
        <AppFormGrid cols="2">
          <AppFormField label="Código" required>
            <AppInput v-model="form.codigo" :disabled="!!form.id" width="sm" class="font-mono uppercase" placeholder="JOVEN" />
            <p v-if="form.id" class="field-help">El código no se puede cambiar después de creado.</p>
          </AppFormField>
          <AppFormField label="% Reducción" required>
            <AppInput
              v-model="form.porcentajeReduccion"
              type="number"
              :disabled="porcentajeBloqueado"
              width="sm"
              class="disabled:bg-amber-50 disabled:text-amber-900"
            />
            <p v-if="porcentajeBloqueado" class="text-xs text-amber-700 mt-0.5">
              🔒 Este motivo ya tiene cuotas con recibo emitido. El porcentaje queda congelado (D1.5).
              Para cambiar la rebaja de un socio: anular su cuota → cambiar de motivo → re-emitir.
            </p>
            <p v-else-if="form.porcentajeReduccion >= 100" class="text-xs text-amber-600 mt-0.5">
              ≥100% → excluye al socio del proceso (D1.4)
            </p>
          </AppFormField>
        </AppFormGrid>

        <AppFormField label="Nombre" required>
          <AppInput v-model="form.nombre" placeholder="Estudiante / Joven" />
        </AppFormField>

        <AppFormField label="Descripción">
          <AppTextarea v-model="form.descripcion" :rows="3"
            placeholder="Cuota reducida para socios menores de 30 años o estudiantes acreditados" />
        </AppFormField>

        <AppFormGrid cols="2">
          <AppFormField label="Orden">
            <AppInput v-model="form.orden" type="number" width="xs" />
          </AppFormField>
          <AppFormField label="Activo">
            <select v-model="form.activo" class="control w-field-sm">
              <option :value="true">Sí</option>
              <option :value="false">No</option>
            </select>
          </AppFormField>
        </AppFormGrid>

        <ErrorAlert v-if="error" :message="error" />
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="modal = false">Cancelar</AppButton>
        <AppButton :loading="guardando" @click="guardar">Guardar</AppButton>
      </template>
    </AppDrawer>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import {
  AppLayout, AppButton, AppDrawer,
  AppFormField, AppFormGrid, AppInput, AppTextarea, ErrorAlert,
} from '@/components/common'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_MOTIVOS_REDUCCION,
  CREATE_MOTIVO_REDUCCION,
  UPDATE_MOTIVO_REDUCCION,
  MOTIVO_TIENE_RECIBOS,
} from '@/graphql/queries/economico'

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
