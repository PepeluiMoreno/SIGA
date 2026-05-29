<template>
  <AppLayout
    title="Registro de Actividades de Tratamiento (RAT)"
    subtitle="Inventario formal de tratamientos de datos personales (art. 30 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por nombre o finalidad…"
      create-label="+ Nueva actividad"
      :fields="camposFiltro"
      @create="abrirAlta()"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando RAT…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtradas"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        vacio-texto="No hay actividades registradas"
        @row-click="abrirEdicion"
      >
        <template #cell-nombre="{ fila }">
          <div class="font-medium text-slate-800">{{ fila.nombre }}</div>
          <div v-if="fila.finalidad" class="text-[11px] text-slate-500 line-clamp-1">{{ fila.finalidad }}</div>
        </template>
        <template #cell-baseJuridica="{ fila }">
          <span class="text-[10px] uppercase rounded-full px-2 py-0.5 bg-indigo-100 text-indigo-700">
            {{ fila.baseJuridica }}
          </span>
        </template>
        <template #cell-datosSensibles="{ fila }">
          <span v-if="fila.datosSensibles" class="text-rose-700 text-xs">⚠️ Art. 9</span>
          <span v-else class="text-slate-400 text-xs">No</span>
        </template>
        <template #cell-activa="{ fila }">
          <span :class="fila.activa ? 'text-emerald-600' : 'text-slate-400'" class="text-xs">
            {{ fila.activa ? 'Activa' : 'Suspendida' }}
          </span>
        </template>
      </ResponsiveTable>
    </div>

    <BaseModal
      v-model="modalAbierto"
      :title="modoEdicion ? 'Editar actividad RAT' : 'Nueva actividad RAT'"
      size="2xl">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="md:col-span-2">
            <label class="lbl">Nombre <span class="req">*</span></label>
            <input v-model="form.nombre" type="text" required maxlength="200" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Finalidad <span class="req">*</span></label>
            <textarea v-model="form.finalidad" rows="2" required class="inp"
              placeholder="Para qué se tratan los datos (gestión de socios, cobro, comunicación…)"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Descripción</label>
            <textarea v-model="form.descripcion" rows="2" class="inp"></textarea>
          </div>
          <div>
            <label class="lbl">Base jurídica (art. 6) <span class="req">*</span></label>
            <select v-model="form.baseJuridica" required class="inp">
              <option value="">Selecciona…</option>
              <option v-for="b in BASES" :key="b" :value="b">{{ b }}</option>
            </select>
          </div>
          <div>
            <label class="lbl">Detalle de la base jurídica</label>
            <input v-model="form.baseJuridicaDetalle" type="text" class="inp"
              placeholder="Artículo o norma concreta" />
          </div>
          <div>
            <label class="lbl">Categorías de interesados</label>
            <input v-model="form.categoriasInteresados" type="text" class="inp"
              placeholder="Socios, voluntarios, donantes…" />
          </div>
          <div>
            <label class="lbl">Categorías de datos</label>
            <input v-model="form.categoriasDatos" type="text" class="inp"
              placeholder="Identificativos, económicos, contacto…" />
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.datosSensibles" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Trata categorías especiales del art. 9 (salud, religión, etc.)</span>
            </label>
          </div>
          <div v-if="form.datosSensibles" class="md:col-span-2">
            <label class="lbl">Detalle de datos sensibles</label>
            <input v-model="form.datosSensiblesDetalle" type="text" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Destinatarios de cesión</label>
            <textarea v-model="form.destinatariosCesion" rows="2" class="inp"
              placeholder="Hacienda, banco, federación, plataforma…"></textarea>
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.transferenciasInternacionales" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Transferencias internacionales (fuera del EEE)</span>
            </label>
          </div>
          <div v-if="form.transferenciasInternacionales">
            <label class="lbl">Países</label>
            <input v-model="form.transferenciasPaises" type="text" class="inp" />
          </div>
          <div v-if="form.transferenciasInternacionales">
            <label class="lbl">Garantías</label>
            <input v-model="form.transferenciasGarantias" type="text" class="inp"
              placeholder="Cláusulas tipo, decisión adecuación, BCR…" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Plazo de conservación</label>
            <textarea v-model="form.plazoConservacion" rows="2" class="inp"
              placeholder="Texto libre + norma que lo justifica"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Medidas de seguridad</label>
            <textarea v-model="form.medidasSeguridad" rows="2" class="inp"></textarea>
          </div>
          <div>
            <label class="lbl">Fecha alta de la actividad</label>
            <input v-model="form.fechaAltaActividad" type="date" class="inp" />
          </div>
          <div>
            <label class="lbl">Fecha de revisión</label>
            <input v-model="form.fechaRevision" type="date" class="inp" />
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.activa" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Actividad activa</span>
            </label>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button v-if="modoEdicion" type="button" @click="eliminar"
            class="text-sm text-red-600 hover:text-red-700 mr-auto">Eliminar</button>
          <button type="button" @click="modalAbierto = false"
            class="text-sm px-3 h-9 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50">Cancelar</button>
          <button type="submit" :disabled="guardando"
            class="text-sm px-4 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_ACTIVIDADES_TRATAMIENTO,
  CREATE_ACTIVIDAD_TRATAMIENTO,
  UPDATE_ACTIVIDAD_TRATAMIENTO,
  DELETE_ACTIVIDADES_TRATAMIENTO,
} from '@/modules/proteccion_datos/graphql/queries.js'

const BASES = [
  'CONSENTIMIENTO', 'EJECUCION_CONTRATO', 'OBLIGACION_LEGAL',
  'INTERES_VITAL', 'INTERES_PUBLICO', 'INTERES_LEGITIMO',
]

const loading = ref(false)
const actividades = ref([])
const busqueda = ref('')
const filtros = ref({ activa: '', sensibles: '' })

const camposFiltro = [
  { key: 'activa', label: 'Estado', type: 'select', allLabel: 'Todas',
    options: [{ value: 'true', label: 'Activas' }, { value: 'false', label: 'Suspendidas' }] },
  { key: 'sensibles', label: 'Datos sensibles', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Sí (art. 9)' }, { value: 'false', label: 'No' }] },
]

const columnas = [
  { key: 'nombre',         label: 'Actividad' },
  { key: 'baseJuridica',   label: 'Base jurídica' },
  { key: 'datosSensibles', label: 'Sensibles', align: 'center' },
  { key: 'fechaRevision',  label: 'Última revisión', align: 'center' },
  { key: 'activa',         label: 'Estado', align: 'center' },
]

const filtradas = computed(() => {
  let rows = actividades.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.nombre || '').toLowerCase().includes(q) ||
      (r.finalidad || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.activa === 'true')  rows = rows.filter(r => r.activa)
  if (filtros.value.activa === 'false') rows = rows.filter(r => !r.activa)
  if (filtros.value.sensibles === 'true')  rows = rows.filter(r => r.datosSensibles)
  if (filtros.value.sensibles === 'false') rows = rows.filter(r => !r.datosSensibles)
  return rows
})

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_ACTIVIDADES_TRATAMIENTO)
    actividades.value = [...(data.rgpdActividadesTratamiento || [])].sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''))
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
    id: null, nombre: '', descripcion: '', finalidad: '',
    baseJuridica: '', baseJuridicaDetalle: '',
    categoriasInteresados: '', categoriasDatos: '',
    datosSensibles: false, datosSensiblesDetalle: '',
    destinatariosCesion: '',
    transferenciasInternacionales: false, transferenciasPaises: '', transferenciasGarantias: '',
    plazoConservacion: '', medidasSeguridad: '',
    activa: true, fechaAltaActividad: null, fechaRevision: null,
  }
}

function abrirAlta() {
  modoEdicion.value = false
  form.value = estadoInicial()
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
    const { id, encargadosRel, ...rest } = form.value
    if (modoEdicion.value) {
      await executeMutation(UPDATE_ACTIVIDAD_TRATAMIENTO, { data: { id, ...rest } })
    } else {
      await executeMutation(CREATE_ACTIVIDAD_TRATAMIENTO, { data: rest })
    }
    modalAbierto.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error al guardar: ' + (e.message || e))
  } finally {
    guardando.value = false
  }
}

async function eliminar() {
  const ok = await useConfirm()({
    titulo: 'Eliminar actividad de tratamiento',
    mensaje: `¿Eliminar la actividad «${form.value.nombre}»?`,
    variante: 'critica',
    etiquetaConfirmar: 'Eliminar',
  })
  if (!ok) return
  try {
    await executeMutation(DELETE_ACTIVIDADES_TRATAMIENTO, { filter: { id: { eq: form.value.id } } })
    modalAbierto.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error al eliminar: ' + (e.message || e))
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
