<template>
  <div class="px-5 py-4">
    <p class="text-sm text-gray-500 mb-3">
      Una vez aprobado el presupuesto, los cambios se registran como modificaciones
      formales y trazables: <strong>transferencias</strong> entre partidas,
      <strong>ampliaciones</strong> (más ingreso del previsto) y <strong>suplementos</strong>.
      No alteran el presupuesto inicial, solo el vigente.
    </p>

    <!-- Formulario de alta -->
    <div v-if="puedeModificar" class="mb-4">
      <div v-if="!mostrarForm">
        <button @click="abrirForm" class="text-sm text-purple-600 hover:underline">+ Registrar modificación</button>
      </div>
      <div v-else class="bg-purple-50/50 border border-purple-100 rounded-lg p-4 space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Tipo</label>
            <select v-model="form.tipo" class="input-sm w-full">
              <option value="TRANSFERENCIA">Transferencia entre partidas</option>
              <option value="AMPLIACION">Ampliación</option>
              <option value="SUPLEMENTO">Suplemento</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Importe (€)</label>
            <input v-model.number="form.importe" type="number" step="0.01" min="0" class="input-sm w-full" />
          </div>
          <div v-if="form.tipo === 'TRANSFERENCIA'">
            <label class="block text-xs font-medium text-gray-600 mb-1">Partida de origen</label>
            <select v-model="form.partidaOrigenId" class="input-sm w-full">
              <option :value="null">Selecciona…</option>
              <option v-for="p in partidas" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Partida de destino</label>
            <select v-model="form.partidaDestinoId" class="input-sm w-full">
              <option :value="null">Selecciona…</option>
              <option v-for="p in partidas" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Motivo</label>
          <input v-model="form.motivo" type="text" placeholder="Justificación de la modificación" class="input-sm w-full" />
        </div>
        <ErrorAlert v-if="errorForm" :message="errorForm" />
        <div class="flex justify-end gap-2">
          <button @click="mostrarForm = false" class="text-sm text-gray-500 hover:underline">Cancelar</button>
          <button @click="registrar" :disabled="guardando"
            class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
            {{ guardando ? 'Registrando…' : 'Registrar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de modificaciones -->
    <div v-if="!modificaciones.length" class="text-center text-gray-400 py-6 text-sm">
      No hay modificaciones registradas.
    </div>
    <div v-else class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
      <div v-for="m in modificaciones" :key="m.id" class="flex items-center gap-3 px-4 py-2.5 text-sm">
        <span class="text-xs px-1.5 py-0.5 rounded font-medium" :class="badgeTipo(m.tipo)">{{ etiquetaTipo(m.tipo) }}</span>
        <div class="flex-1 min-w-0">
          <span class="text-gray-800">
            <template v-if="m.tipo === 'TRANSFERENCIA'">
              {{ nombrePartida(m.partidaOrigenId) }} → {{ nombrePartida(m.partidaDestinoId) }}
            </template>
            <template v-else>{{ nombrePartida(m.partidaDestinoId) }}</template>
          </span>
          <span v-if="m.motivo" class="text-gray-400 text-xs block">{{ m.motivo }}</span>
        </div>
        <span class="text-xs text-gray-400">{{ m.fecha }}</span>
        <span class="font-medium text-gray-700">{{ eur(m.importe) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref } from 'vue'

const props = defineProps({
  modificaciones: { type: Array, default: () => [] },
  partidas: { type: Array, default: () => [] },
  puedeModificar: { type: Boolean, default: false },
})
const emit = defineEmits(['registrar'])

const mostrarForm = ref(false)
const guardando = ref(false)
const errorForm = ref('')
const form = ref({ tipo: 'TRANSFERENCIA', importe: null, partidaOrigenId: null, partidaDestinoId: null, motivo: '' })

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)
const nombrePartida = (id) => {
  const p = props.partidas.find(x => x.id === id)
  return p ? `${p.codigo} — ${p.nombre}` : '—'
}
const TIPOS = { TRANSFERENCIA: 'Transferencia', AMPLIACION: 'Ampliación', SUPLEMENTO: 'Suplemento' }
const etiquetaTipo = (t) => TIPOS[t] ?? t
const badgeTipo = (t) => ({
  TRANSFERENCIA: 'bg-blue-50 text-blue-600',
  AMPLIACION: 'bg-green-50 text-green-600',
  SUPLEMENTO: 'bg-amber-50 text-amber-600',
}[t] ?? 'bg-gray-100 text-gray-600')

const abrirForm = () => {
  form.value = { tipo: 'TRANSFERENCIA', importe: null, partidaOrigenId: null, partidaDestinoId: null, motivo: '' }
  errorForm.value = ''
  mostrarForm.value = true
}

const registrar = async () => {
  errorForm.value = ''
  if (!form.value.importe || form.value.importe <= 0) { errorForm.value = 'Indica un importe positivo'; return }
  if (!form.value.partidaDestinoId) { errorForm.value = 'Selecciona la partida de destino'; return }
  if (form.value.tipo === 'TRANSFERENCIA' && !form.value.partidaOrigenId) {
    errorForm.value = 'Una transferencia necesita partida de origen'; return
  }
  if (!form.value.motivo.trim()) { errorForm.value = 'Indica el motivo'; return }
  guardando.value = true
  try {
    await emit('registrar', {
      tipo: form.value.tipo,
      importe: form.value.importe,
      partidaDestinoId: form.value.partidaDestinoId,
      partidaOrigenId: form.value.tipo === 'TRANSFERENCIA' ? form.value.partidaOrigenId : null,
      motivo: form.value.motivo.trim(),
    })
    mostrarForm.value = false
  } catch (e) {
    errorForm.value = e?.message ?? 'No se pudo registrar'
  } finally {
    guardando.value = false
  }
}
</script>
