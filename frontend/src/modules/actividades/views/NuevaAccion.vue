<template>
  <AppLayout title="Nueva acción" subtitle="Crear una nueva acción">
    <div class="max-w-3xl">

    <form @submit.prevent="guardar" class="space-y-5 bg-white rounded-xl border border-slate-200 p-6">
      <!-- Nombre -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Nombre *</label>
        <input
          v-model="form.nombre"
          required
          type="text"
          class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- Tipo y Estado -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Tipo *</label>
          <select
            v-model="form.tipoAccionId"
            required
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Seleccionar tipo…</option>
            <option v-for="t in tiposAccion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Estado *</label>
          <select
            v-model="form.estadoId"
            required
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Seleccionar estado…</option>
            <option v-for="e in estadosAccion" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
        </div>
      </div>

      <!-- Descripción -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
        <textarea
          v-model="form.descripcion"
          rows="3"
          class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
        />
      </div>

      <!-- Fechas y horas -->
      <div class="grid grid-cols-4 gap-3">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-slate-700 mb-1">Fecha inicio</label>
          <input
            v-model="form.fechaInicio"
            type="date"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-slate-700 mb-1">Hora inicio</label>
          <input
            v-model="form.horaInicio"
            type="time"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-slate-700 mb-1">Fecha fin</label>
          <input
            v-model="form.fechaFin"
            type="date"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-slate-700 mb-1">Hora fin</label>
          <input
            v-model="form.horaFin"
            type="time"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      <!-- Lugar (condicional según tipo) -->
      <div v-if="tipoSeleccionado?.tieneLugar">
        <label class="block text-sm font-medium text-slate-700 mb-1">Lugar</label>
        <input
          v-model="form.lugar"
          type="text"
          class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- Online -->
      <div class="flex items-center gap-2">
        <input id="esOnline" v-model="form.esOnline" type="checkbox" class="rounded border-slate-300 text-indigo-600" />
        <label for="esOnline" class="text-sm text-slate-700">Es online</label>
      </div>
      <div v-if="form.esOnline">
        <label class="block text-sm font-medium text-slate-700 mb-1">URL online</label>
        <input
          v-model="form.urlOnline"
          type="url"
          class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- Error -->
      <div v-if="error" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{{ error }}</div>

      <!-- Botones -->
      <div class="flex justify-end gap-3 pt-2 border-t border-slate-100">
        <button
          type="button"
          @click="$router.back()"
          class="h-10 px-4 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          :disabled="saving"
          class="h-10 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {{ saving ? 'Guardando…' : 'Crear acción' }}
        </button>
      </div>
    </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_TIPOS_ACCION, GET_ESTADOS_ACCION, CREAR_ACCION } from '../graphql/queries.js'

const router = useRouter()

const tiposAccion = ref([])
const estadosAccion = ref([])
const saving = ref(false)
const error = ref('')

const form = ref({
  nombre: '',
  tipoAccionId: '',
  estadoId: '',
  descripcion: '',
  fechaInicio: '',
  horaInicio: '',
  fechaFin: '',
  horaFin: '',
  lugar: '',
  esOnline: false,
  urlOnline: '',
})

const tipoSeleccionado = computed(() =>
  tiposAccion.value.find(t => t.id === form.value.tipoAccionId) || null
)

onMounted(async () => {
  const [rTipos, rEstados] = await Promise.all([
    graphqlClient.request(GET_TIPOS_ACCION),
    graphqlClient.request(GET_ESTADOS_ACCION),
  ])
  tiposAccion.value = rTipos.tiposAccion || []
  estadosAccion.value = rEstados.estadosAccion || []
  const inicial = estadosAccion.value.find(e => e.esInicial)
  if (inicial) form.value.estadoId = inicial.id
})

async function guardar() {
  saving.value = true
  error.value = ''
  try {
    const data = {
      nombre: form.value.nombre,
      tipoAccionId: form.value.tipoAccionId,
      estadoId: form.value.estadoId,
      descripcion: form.value.descripcion || null,
      fechaInicio: form.value.fechaInicio || null,
      horaInicio: form.value.horaInicio || null,
      fechaFin: form.value.fechaFin || null,
      horaFin: form.value.horaFin || null,
      lugar: form.value.lugar || null,
      esOnline: form.value.esOnline,
      urlOnline: form.value.urlOnline || null,
    }
    const res = await graphqlClient.request(CREAR_ACCION, { data })
    const id = res.crearAccion?.id
    router.push(`/acciones/${id}`)
  } catch (e) {
    error.value = e.message || 'Error al crear la acción'
  } finally {
    saving.value = false
  }
}
</script>
