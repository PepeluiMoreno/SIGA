<template>
  <AppLayout
    title="Cláusulas informativas"
    subtitle="Textos versionados que se muestran al interesado al recoger sus datos (art. 13/14 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por código o finalidad…"
      create-label="+ Nueva cláusula"
      :fields="camposFiltro"
      @create="abrirAlta()"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando cláusulas…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtradas"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        vacio-texto="No hay cláusulas registradas"
        @row-click="abrirEdicion"
      >
        <template #cell-codigo="{ fila }">
          <div class="font-mono text-xs text-slate-700">{{ fila.codigo }}</div>
          <div class="text-[10px] text-slate-500">v{{ fila.version }}</div>
        </template>
        <template #cell-vigente="{ fila }">
          <span :class="fila.vigente ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.vigente ? 'Vigente' : 'Archivada' }}
          </span>
        </template>
      </ResponsiveTable>
    </div>

    <AppDrawer
      v-model="modalAbierto"
      :title="modoEdicion ? 'Editar cláusula' : 'Nueva cláusula informativa'"
      size="xl">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="lbl">Código <span class="req">*</span></label>
            <select v-model="form.codigo" required class="inp">
              <option value="">Selecciona…</option>
              <option v-for="c in CODIGOS" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="lbl">Versión <span class="req">*</span></label>
            <input v-model.number="form.version" type="number" min="1" required class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Finalidad corta <span class="req">*</span></label>
            <input v-model="form.finalidadCorta" type="text" required maxlength="300" class="inp"
              placeholder="Resumen de una línea para listas y selectores" />
          </div>
          <div>
            <label class="lbl">Vigente desde</label>
            <input v-model="form.fechaVigenciaDesde" type="date" class="inp" />
          </div>
          <div>
            <label class="lbl">Vigente hasta</label>
            <input v-model="form.fechaVigenciaHasta" type="date" class="inp" />
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.vigente" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Versión vigente (se muestra al usuario)</span>
            </label>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Texto informativo (markdown) <span class="req">*</span></label>
            <textarea v-model="form.texto" rows="10" required class="inp font-mono text-xs"
              placeholder="Responsable, finalidad, base jurídica, destinatarios, plazo, derechos, DPD…"></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button type="button" @click="modalAbierto = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit" :disabled="guardando"
            class="text-sm px-4 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </form>
    </AppDrawer>
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import { hoyISO } from '@/utils/fecha.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_CLAUSULAS, CREATE_CLAUSULA, UPDATE_CLAUSULA,
} from '@/modules/proteccion_datos/graphql/queries.js'

const CODIGOS = [
  'ALTA_SOCIO', 'ALTA_VOLUNTARIADO', 'DONACION',
  'CONTACTO_WEB', 'COMUNICACIONES_INFORMATIVAS',
  'CESION_IMAGEN', 'DATOS_SALUD',
]

const loading = ref(false)
const clausulas = ref([])
const busqueda = ref('')
const filtros = ref({ vigente: '' })

const camposFiltro = [
  { key: 'vigente', label: 'Estado', type: 'select', allLabel: 'Todas',
    options: [{ value: 'true', label: 'Vigentes' }, { value: 'false', label: 'Archivadas' }] },
]

const columnas = [
  { key: 'codigo',             label: 'Código' },
  { key: 'finalidadCorta',     label: 'Finalidad' },
  { key: 'fechaVigenciaDesde', label: 'Desde', align: 'center' },
  { key: 'vigente',            label: 'Estado', align: 'center' },
]

const filtradas = computed(() => {
  let rows = clausulas.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.codigo || '').toLowerCase().includes(q) ||
      (r.finalidadCorta || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.vigente === 'true')  rows = rows.filter(r => r.vigente)
  if (filtros.value.vigente === 'false') rows = rows.filter(r => !r.vigente)
  return rows
})

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_CLAUSULAS)
    clausulas.value = [...(data.rgpdClausulas || [])].sort((a, b) =>
      (a.codigo || '').localeCompare(b.codigo || '') || b.version - a.version)
  } finally {
    loading.value = false
  }
}

const modalAbierto = ref(false)
const modoEdicion  = ref(false)
const guardando    = ref(false)
const form = ref(estadoInicial())

function estadoInicial() {
  return {
    id: null, codigo: '', version: 1, vigente: true,
    fechaVigenciaDesde: null, fechaVigenciaHasta: null,
    finalidadCorta: '', texto: '',
  }
}

function abrirAlta() {
  modoEdicion.value = false
  // Alta: fecha de inicio de vigencia = hoy por defecto (no se toca al editar).
  form.value = { ...estadoInicial(), fechaVigenciaDesde: hoyISO() }
  modalAbierto.value = true
}

function abrirEdicion(fila) {
  modoEdicion.value = true
  form.value = { ...estadoInicial(), ...fila }
  modalAbierto.value = true
}

async function guardar() {
  guardando.value = true
  try {
    const { id, ...rest } = form.value
    if (modoEdicion.value) {
      await executeMutation(UPDATE_CLAUSULA, { data: { id, ...rest } })
    } else {
      await executeMutation(CREATE_CLAUSULA, { data: rest })
    }
    modalAbierto.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error al guardar: ' + (e.message || e))
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.lbl { @apply block text-xs font-medium text-slate-700 mb-1; }
.req { @apply text-red-500; }
.inp {
  @apply h-10 w-full px-3 text-sm border border-slate-300 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
textarea.inp { @apply h-auto py-2; }
select.inp { @apply pr-8; }
</style>
