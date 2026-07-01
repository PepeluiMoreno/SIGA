<template>
  <AppLayout title="Nueva actividad" :subtitle="campaniaNombre ? `Campaña: ${campaniaNombre}` : 'Crear una nueva actividad'">
    <template #actions>
      <FormActions submit-text="Crear actividad" :loading="saving"
        @cancel="$router.back()" @submit="guardar" />
    </template>
    <div class="w-full">

    <!-- Contexto campaña -->
    <div v-if="campaniaId" class="mb-4 flex items-center gap-2 text-xs text-slate-500">
      <router-link :to="`/campanias/${campaniaId}`"
        class="inline-flex items-center gap-1 text-indigo-600 hover:underline font-medium">
        <ChevronLeftIcon class="w-3.5 h-3.5" />
        {{ campaniaNombre || 'Campaña' }}
      </router-link>
      <span class="text-slate-300">/</span>
      <span>Nueva actividad</span>
    </div>

    <form id="nueva-actividad-form" @submit.prevent="guardar" class="space-y-5 bg-white rounded-xl border border-slate-200 p-6">
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
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Tipo *</label>
          <select
            v-model="form.tipoActividadId"
            required
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Seleccionar tipo…</option>
            <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
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

      <!-- Carácter temporal -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Carácter *</label>
        <div class="space-y-1.5">
          <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
            <input type="radio" v-model="form.caracter" value="PUNTUAL" />
            <span>Puntual <span class="text-slate-400 text-xs">(con fecha concreta)</span></span>
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
            <input type="radio" v-model="form.caracter" value="RECURRENTE" />
            <span>Recurrente <span class="text-slate-400 text-xs">(con periodicidad — plantilla o instancia)</span></span>
          </label>
          <label class="flex items-center gap-2 text-sm cursor-pointer"
                 :class="campaniaId ? 'text-slate-300 cursor-not-allowed' : 'text-slate-700'">
            <input type="radio" v-model="form.caracter" value="PERMANENTE" :disabled="!!campaniaId" />
            <span>
              Permanente
              <span class="text-slate-400 text-xs">
                (sin fin; solo fuera de campaña{{ campaniaId ? ' — no disponible al venir de una campaña' : '' }})
              </span>
            </span>
          </label>
        </div>
      </div>

      <!-- Fechas y horas -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
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

      <!-- Lugar y ubicación (condicional según tipo) -->
      <template v-if="tipoSeleccionado?.tieneLugar">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Lugar (nombre del espacio)</label>
          <input v-model="form.lugar" type="text"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div class="grid grid-cols-6 gap-2">
          <div class="col-span-3">
            <label class="block text-sm font-medium text-slate-700 mb-1">Dirección postal</label>
            <input v-model="form.direccion" type="text"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium text-slate-700 mb-1">Localidad</label>
            <input v-model="form.localidad" type="text"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div class="col-span-1">
            <label class="block text-sm font-medium text-slate-700 mb-1">Provincia</label>
            <input v-model="form.provincia" type="text"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>
      </template>

      <!-- Online — plataforma + campos dinámicos del catálogo -->
      <div class="flex items-center gap-2">
        <input id="esOnline" v-model="form.esOnline" type="checkbox" class="rounded border-slate-300 text-indigo-600" />
        <label for="esOnline" class="text-sm text-slate-700">Actividad online (videoreunión)</label>
      </div>
      <div v-if="form.esOnline" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
        <PlataformaTelematicaSelector
          ref="selectorPlataformaRef"
          v-model:plataforma-id="form.plataformaTelematicaId"
          v-model:datos-conexion="form.datosConexion"
          :requerido="true" />
      </div>

      <!-- Error -->
      <ErrorAlert v-if="error" :message="error" />

      <!-- Botones -->
    </form>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import PlataformaTelematicaSelector from '@/components/common/PlataformaTelematicaSelector.vue'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FormActions from '@/components/common/FormActions.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_TIPOS_ACCION, GET_ESTADOS_ACCION, CREAR_ACCION } from '../graphql/queries.js'

const selectorPlataformaRef = ref(null)

const router = useRouter()
const route  = useRoute()

const campaniaId     = route.query.campaniaId || null
const campaniaNombre = ref(route.query.campaniaNombre || null)

const tiposActividad = ref([])
const estadosAccion = ref([])
const saving = ref(false)
const error = ref('')

const form = ref({
  nombre: '',
  tipoActividadId: '',
  estadoId: '',
  descripcion: '',
  caracter: 'PUNTUAL',  // PUNTUAL | RECURRENTE | PERMANENTE
  fechaInicio: '',
  horaInicio: '',
  fechaFin: '',
  horaFin: '',
  lugar: '',
  direccion: '',
  localidad: '',
  provincia: '',
  duracionHoras: null,
  duracionDias: null,
  esOnline: false,
  urlOnline: '',
  plataformaTelematicaId: '',
  datosConexion: {},
})

const tipoSeleccionado = computed(() =>
  tiposActividad.value.find(t => t.id === form.value.tipoActividadId) || null
)

onMounted(async () => {
  const [rTipos, rEstados] = await Promise.all([
    graphqlClient.request(GET_TIPOS_ACCION),
    graphqlClient.request(GET_ESTADOS_ACCION),
  ])
  tiposActividad.value = rTipos.tiposActividad || []
  estadosAccion.value = rEstados.estadosAccion || []
  const inicial = estadosAccion.value.find(e => e.esInicial)
  if (inicial) form.value.estadoId = inicial.id
})

async function guardar() {
  saving.value = true
  error.value = ''
  if (form.value.esOnline) {
    const errPlat = selectorPlataformaRef.value?.validar() || ''
    if (errPlat) { error.value = errPlat; saving.value = false; return }
  }
  try {
    // PERMANENTE no admite ni campaña ni recurrencia ni fecha_fin.
    const esPermanente = form.value.caracter === 'PERMANENTE'
    const datosConexion = form.value.esOnline && Object.keys(form.value.datosConexion).length
      ? JSON.stringify(form.value.datosConexion)
      : null
    const plat = selectorPlataformaRef.value?.getPlataformaActual?.()
    const data = {
      nombre: form.value.nombre,
      tipoActividadId: form.value.tipoActividadId,
      estadoId: form.value.estadoId,
      descripcion: form.value.descripcion || null,
      caracter: form.value.caracter,
      esRecurrente: form.value.caracter === 'RECURRENTE',
      fechaInicio: form.value.fechaInicio || null,
      horaInicio: form.value.horaInicio || null,
      fechaFin: esPermanente ? null : (form.value.fechaFin || null),
      horaFin: form.value.horaFin || null,
      lugar: form.value.lugar || null,
      direccion: form.value.direccion || null,
      localidad: form.value.localidad || null,
      provincia: form.value.provincia || null,
      duracionHoras: form.value.duracionHoras || null,
      duracionDias: form.value.duracionDias || null,
      esOnline: form.value.esOnline,
      // Conservamos urlOnline (legacy) tomando la URL de los datos si existe.
      urlOnline: form.value.esOnline
        ? (form.value.datosConexion.url || form.value.urlOnline || null)
        : null,
      plataformaTelematicaId: form.value.esOnline ? (form.value.plataformaTelematicaId || null) : null,
      datosConexionTelematica: datosConexion,
      ...(campaniaId && !esPermanente ? { campaniaId } : {}),
    }
    const res = await graphqlClient.request(CREAR_ACCION, { data })
    const id = res.crearActividad?.id
    // Volver a la campaña si venimos de una
    if (campaniaId) router.push(`/campanias/${campaniaId}`)
    else router.push(`/actividades/${id}`)
  } catch (e) {
    error.value = e.message || 'Error al crear la actividad'
  } finally {
    saving.value = false
  }
}
</script>
