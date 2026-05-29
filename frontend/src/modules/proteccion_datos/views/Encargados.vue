<template>
  <AppLayout
    title="Encargados del tratamiento"
    subtitle="Proveedores que tratan datos por cuenta de la organización (art. 28 RGPD)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por nombre, NIF o servicio…"
      create-label="+ Nuevo encargado"
      :fields="camposFiltro"
      @create="abrirAlta()"
    />

    <EstadoCarga v-if="loading" mensaje="Cargando encargados…" class="mt-6" />

    <div v-else class="mt-3 bg-white border border-slate-200 rounded-xl overflow-hidden">
      <ResponsiveTable
        :columnas="columnas"
        :filas="filtrados"
        clave-fila="id"
        :row-class="() => 'cursor-pointer'"
        vacio-texto="No hay encargados registrados"
        @row-click="abrirEdicion"
      >
        <template #cell-nombre="{ fila }">
          <div class="font-medium text-slate-800">{{ fila.nombre }}</div>
          <div v-if="fila.nif" class="text-[10px] text-slate-500 font-mono">{{ fila.nif }}</div>
        </template>
        <template #cell-contratoFirmado="{ fila }">
          <span :class="badgeContrato(fila.contratoFirmado)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
            {{ fila.contratoFirmado ? 'Firmado' : 'Pendiente' }}
          </span>
        </template>
        <template #cell-transferenciaInternacional="{ fila }">
          <span v-if="fila.transferenciaInternacional" class="text-amber-700 text-xs">⚠️ TID</span>
          <span v-else class="text-slate-400 text-xs">No</span>
        </template>
        <template #cell-activo="{ fila }">
          <span :class="fila.activo ? 'text-emerald-600' : 'text-slate-400'" class="text-xs">
            {{ fila.activo ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </ResponsiveTable>
    </div>

    <BaseModal
      v-model="modalAbierto"
      :title="modoEdicion ? 'Editar encargado' : 'Nuevo encargado'"
      size="2xl">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="lbl">Nombre <span class="req">*</span></label>
            <input v-model="form.nombre" type="text" required maxlength="200" class="inp" />
          </div>
          <div>
            <label class="lbl">NIF</label>
            <input v-model="form.nif" type="text" maxlength="30" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Servicio prestado <span class="req">*</span></label>
            <input v-model="form.servicio" type="text" required maxlength="300" class="inp"
              placeholder="Hosting, SMTP, gestoría, pasarela de pago…" />
          </div>
          <div>
            <label class="lbl">Email de contacto</label>
            <input v-model="form.contactoEmail" type="email" maxlength="200" class="inp" />
          </div>
          <div>
            <label class="lbl">Teléfono de contacto</label>
            <input v-model="form.contactoTelefono" type="text" maxlength="50" class="inp" />
          </div>
          <div>
            <label class="lbl">País de alojamiento</label>
            <input v-model="form.paisAlojamiento" type="text" maxlength="100" class="inp" />
          </div>
          <div class="flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.transferenciaInternacional" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Transferencia internacional</span>
            </label>
          </div>
          <div class="flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.contratoFirmado" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Contrato firmado (art. 28)</span>
            </label>
          </div>
          <div>
            <label class="lbl">Fecha del contrato</label>
            <input v-model="form.contratoFecha" type="date" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">URL del contrato</label>
            <input v-model="form.contratoDocumentoUrl" type="url" maxlength="500" class="inp" />
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.clausulasTipoAepd" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Usa cláusulas tipo aprobadas por la AEPD</span>
            </label>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Notas</label>
            <textarea v-model="form.notas" rows="3" class="inp"></textarea>
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.activo" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Encargado activo</span>
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
  GET_ENCARGADOS, CREATE_ENCARGADO, UPDATE_ENCARGADO, DELETE_ENCARGADOS,
} from '@/modules/proteccion_datos/graphql/queries.js'

const loading = ref(false)
const encargados = ref([])
const busqueda = ref('')
const filtros = ref({ activo: '', contrato: '' })

const camposFiltro = [
  { key: 'activo', label: 'Activos', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }] },
  { key: 'contrato', label: 'Contrato', type: 'select', allLabel: 'Todos',
    options: [{ value: 'true', label: 'Firmado' }, { value: 'false', label: 'Pendiente' }] },
]

const columnas = [
  { key: 'nombre',                     label: 'Nombre' },
  { key: 'servicio',                   label: 'Servicio' },
  { key: 'paisAlojamiento',            label: 'País' },
  { key: 'transferenciaInternacional', label: 'TID', align: 'center' },
  { key: 'contratoFirmado',            label: 'Contrato', align: 'center' },
  { key: 'activo',                     label: 'Estado', align: 'center' },
]

const filtrados = computed(() => {
  let rows = encargados.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(r =>
      (r.nombre || '').toLowerCase().includes(q) ||
      (r.nif || '').toLowerCase().includes(q) ||
      (r.servicio || '').toLowerCase().includes(q)
    )
  }
  if (filtros.value.activo === 'true')  rows = rows.filter(r => r.activo)
  if (filtros.value.activo === 'false') rows = rows.filter(r => !r.activo)
  if (filtros.value.contrato === 'true')  rows = rows.filter(r => r.contratoFirmado)
  if (filtros.value.contrato === 'false') rows = rows.filter(r => !r.contratoFirmado)
  return rows
})

function badgeContrato(firmado) {
  return firmado
    ? 'bg-emerald-100 text-emerald-700'
    : 'bg-amber-100 text-amber-700'
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_ENCARGADOS)
    encargados.value = [...(data.rgpdEncargados || [])].sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''))
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
    id: null, nombre: '', nif: '', servicio: '',
    contactoEmail: '', contactoTelefono: '', paisAlojamiento: '',
    transferenciaInternacional: false,
    contratoFirmado: false, contratoFecha: null, contratoDocumentoUrl: '',
    clausulasTipoAepd: false, notas: '', activo: true,
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
    if (modoEdicion.value) {
      const { id, ...rest } = form.value
      await executeMutation(UPDATE_ENCARGADO, { data: { id, ...rest } })
    } else {
      const { id, ...rest } = form.value
      await executeMutation(CREATE_ENCARGADO, { data: rest })
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
    titulo: 'Eliminar encargado',
    mensaje: `¿Eliminar el encargado «${form.value.nombre}»? Esta acción es reversible (papelera).`,
    variante: 'critica',
    etiquetaConfirmar: 'Eliminar',
  })
  if (!ok) return
  try {
    await executeMutation(DELETE_ENCARGADOS, { filter: { id: { eq: form.value.id } } })
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
</style>
