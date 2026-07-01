<template>
  <div class="space-y-3">
    <div v-if="cargando" class="text-center py-4 text-slate-400 text-sm">Cargando disponibilidad…</div>

    <template v-else>
      <!-- Lista de franjas: cada una = días en circulitos + tramo horario -->
      <div v-if="franjas.length" class="space-y-2">
        <div v-for="(f, i) in franjas" :key="i"
          class="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5">
          <!-- Días en circulitos -->
          <div class="flex items-center gap-1">
            <button v-for="(d, di) in DIAS" :key="di" type="button"
              :disabled="!editMode"
              @click="toggleDia(f, di)"
              class="w-8 h-8 rounded-full text-xs font-semibold transition-colors disabled:cursor-default"
              :class="f.dias.includes(di)
                ? 'bg-indigo-600 text-white'
                : (editMode ? 'bg-slate-100 text-slate-500 hover:bg-slate-200' : 'bg-slate-50 text-slate-300')">
              {{ d }}
            </button>
          </div>
          <!-- Tramo horario -->
          <div class="flex items-center gap-1.5 text-sm">
            <span class="text-slate-400 text-xs">de</span>
            <input v-model="f.horaInicio" type="time" :disabled="!editMode"
              class="h-8 px-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-50 disabled:text-slate-500" />
            <span class="text-slate-400 text-xs">a</span>
            <input v-model="f.horaFin" type="time" :disabled="!editMode"
              class="h-8 px-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-50 disabled:text-slate-500" />
          </div>
          <button v-if="editMode" type="button" title="Quitar franja" @click="quitarFranja(i)"
            class="ml-auto p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors">
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
      <p v-else class="text-sm text-slate-400 italic">Sin franjas de disponibilidad.</p>

      <!-- Acciones (solo edición) -->
      <div v-if="editMode" class="flex items-center gap-3">
        <button type="button" @click="agregarFranja"
          class="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
          <PlusIcon class="w-3.5 h-3.5" /> Añadir franja
        </button>
        <button type="button" @click="guardar" :disabled="guardando"
          class="inline-flex items-center gap-2 h-8 px-3 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ guardando ? 'Guardando…' : 'Guardar disponibilidad' }}
        </button>
        <span v-if="guardadoOk" class="text-xs text-emerald-600 font-medium">✓ Guardado</span>
      </div>
      <ErrorAlert v-if="error" :message="error" />
      <p class="text-xs text-slate-400">
        Marca los días de cada franja e indica el tramo horario. Ej.: lunes y miércoles de 17:00 a 19:00; viernes de 15:00 a 21:00.
      </p>
    </template>
  </div>
</template>

<script setup>
/**
 * FranjasDisponibilidad — editor de franjas de disponibilidad de un voluntario.
 *
 * Cada franja son varios días (en circulitos) + un tramo horario, de modo que
 * "lunes y miércoles de 17 a 19" es UNA franja con L y X marcados. Al guardar se
 * expande a una fila por (día, tramo) que persiste guardarFranjasDisponibilidad
 * (ancla al voluntario del contacto). Ver feedback_profesionalidad_extrema.
 */
import { ref, onMounted, watch } from 'vue'
import { PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { graphqlClient } from '@/graphql/client'

const props = defineProps({
  contactoId: { type: String, default: null },
  editMode:   { type: Boolean, default: false },
})

const DIAS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']  // 0=Lunes … 6=Domingo

const franjas = ref([])   // [{ dias: [int], horaInicio, horaFin }]
const cargando = ref(false)
const guardando = ref(false)
const guardadoOk = ref(false)
const error = ref('')

const QUERY = `
  query FranjasContacto($contactoId: UUID!) {
    franjasDisponibilidadContacto(contactoId: $contactoId) { diaSemana horaInicio horaFin }
  }
`
const MUTATION = `
  mutation GuardarFranjas($contactoId: UUID!, $franjas: [FranjaDisponibilidadInput!]!) {
    guardarFranjasDisponibilidad(contactoId: $contactoId, franjas: $franjas)
  }
`

// Agrupa las filas (día, tramo) por tramo horario → una franja con varios días.
function agrupar(filas) {
  const porTramo = {}
  for (const f of filas) {
    const k = `${f.horaInicio}|${f.horaFin}`
    ;(porTramo[k] ||= { dias: [], horaInicio: f.horaInicio?.slice(0, 5), horaFin: f.horaFin?.slice(0, 5) }).dias.push(f.diaSemana)
  }
  return Object.values(porTramo)
}

async function cargar() {
  if (!props.contactoId) { franjas.value = []; return }
  cargando.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(QUERY, { contactoId: props.contactoId })
    franjas.value = agrupar(data.franjasDisponibilidadContacto || [])
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando la disponibilidad'
  } finally {
    cargando.value = false
  }
}

function toggleDia(f, di) {
  if (!props.editMode) return
  const idx = f.dias.indexOf(di)
  idx >= 0 ? f.dias.splice(idx, 1) : f.dias.push(di)
}
function agregarFranja() { franjas.value.push({ dias: [], horaInicio: '', horaFin: '' }) }
function quitarFranja(i) { franjas.value.splice(i, 1) }

async function guardar() {
  guardando.value = true
  guardadoOk.value = false
  error.value = ''
  try {
    // Expandir a una fila por (día, tramo); descartar franjas incompletas.
    const payload = []
    for (const f of franjas.value) {
      if (!f.horaInicio || !f.horaFin || !f.dias.length) continue
      for (const d of f.dias) payload.push({ diaSemana: d, horaInicio: f.horaInicio, horaFin: f.horaFin })
    }
    await graphqlClient.request(MUTATION, { contactoId: props.contactoId, franjas: payload })
    guardadoOk.value = true
    setTimeout(() => { guardadoOk.value = false }, 2500)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error guardando la disponibilidad'
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
watch(() => props.contactoId, cargar)
</script>
