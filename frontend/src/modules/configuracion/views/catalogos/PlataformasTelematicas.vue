<template>
  <AppLayout
    title="Plataformas telemáticas"
    subtitle="Catálogo de productos de videoreunión disponibles para las reuniones telemáticas">

    <div class="mb-3 flex justify-between items-center">
      <router-link to="/parametrizacion/catalogos" class="text-sm text-slate-600 hover:text-slate-900 inline-flex items-center gap-1">
        <ArrowLeftIcon class="w-4 h-4" /> Volver a Catálogos
      </router-link>
      <button @click="abrirAlta()"
        class="text-sm px-3 h-9 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 inline-flex items-center gap-1.5">
        <PlusIcon class="w-4 h-4" /> Nueva plataforma
      </button>
    </div>

    <EstadoCarga v-if="loading" mensaje="Cargando plataformas…" />

    <div v-else class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left w-12"></th>
            <th class="px-3 py-2 text-left">Código / Nombre</th>
            <th class="px-3 py-2 text-left">Descripción</th>
            <th class="px-3 py-2 text-center w-24">Activa</th>
            <th class="px-3 py-2 text-center w-20">Orden</th>
            <th class="px-3 py-2 w-24"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="p in plataformas" :key="p.id" class="hover:bg-slate-50">
            <td class="px-3 py-2 text-2xl">{{ p.icono || '📹' }}</td>
            <td class="px-3 py-2">
              <div class="font-medium text-slate-800">{{ p.nombre }}</div>
              <div class="font-mono text-[10px] text-slate-500">{{ p.codigo }}</div>
            </td>
            <td class="px-3 py-2 text-xs text-slate-600">{{ p.descripcion || '—' }}</td>
            <td class="px-3 py-2 text-center">
              <button @click="toggleActiva(p)"
                :class="p.activa ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                class="text-[10px] uppercase rounded-full px-2 py-0.5 hover:opacity-80">
                {{ p.activa ? 'Sí' : 'No' }}
              </button>
            </td>
            <td class="px-3 py-2 text-center text-xs text-slate-600">{{ p.orden }}</td>
            <td class="px-3 py-2 text-right">
              <button @click="abrirEdicion(p)" class="text-xs text-indigo-600 hover:underline">Editar</button>
            </td>
          </tr>
          <tr v-if="!plataformas.length">
            <td colspan="6" class="px-3 py-8 text-center text-slate-400 text-sm">
              No hay plataformas registradas
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppDrawer v-model="modalAbierto"
      :title="modoEdicion ? 'Editar plataforma' : 'Nueva plataforma telemática'"
      size="xl">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="lbl">Código <span class="req">*</span></label>
            <input v-model="form.codigo" type="text" required maxlength="40"
              :disabled="modoEdicion && form.esInmutable"
              class="inp uppercase" placeholder="JITSI, ZOOM…" />
          </div>
          <div>
            <label class="lbl">Nombre <span class="req">*</span></label>
            <input v-model="form.nombre" type="text" required maxlength="100" class="inp" />
          </div>
          <div>
            <label class="lbl">Icono (emoji)</label>
            <input v-model="form.icono" type="text" maxlength="10" class="inp" placeholder="📹" />
          </div>
          <div>
            <label class="lbl">Orden</label>
            <input v-model.number="form.orden" type="number" min="0" class="inp" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">Descripción</label>
            <textarea v-model="form.descripcion" rows="2" class="inp"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="lbl">URL base</label>
            <input v-model="form.urlBase" type="url" maxlength="300" class="inp"
              placeholder="https://meet.jit.si/" />
          </div>
          <div class="md:col-span-2">
            <label class="lbl">
              Esquema de campos (JSON)
              <span class="text-xs text-slate-500 ml-2">Lista de objetos {key, label, tipo, requerido, placeholder}</span>
            </label>
            <textarea v-model="form.camposEsquema" rows="6"
              class="inp font-mono text-xs"
              placeholder='[{"key":"url","label":"URL","tipo":"url","requerido":true}]'></textarea>
            <p v-if="errorEsquema" class="mt-1 text-xs text-red-600">{{ errorEsquema }}</p>
          </div>
          <div class="md:col-span-2 flex items-end">
            <label class="inline-flex items-center gap-2 h-10">
              <input v-model="form.activa" type="checkbox" class="rounded" />
              <span class="text-sm text-slate-700">Plataforma activa (visible en convocatorias)</span>
            </label>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
          <button v-if="modoEdicion && !form.esInmutable" type="button" @click="eliminar"
            class="text-sm text-red-600 hover:text-red-700 mr-auto">Eliminar</button>
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
import { useConfirm } from '@/composables/useConfirm'
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import { ArrowLeftIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_PLATAFORMAS_TELEMATICAS,
  CREATE_PLATAFORMA_TELEMATICA,
  UPDATE_PLATAFORMA_TELEMATICA,
  DELETE_PLATAFORMAS_TELEMATICAS,
} from '@/graphql/queries/secretaria.js'

const loading = ref(false)
const plataformas = ref([])
const modalAbierto = ref(false)
const modoEdicion = ref(false)
const guardando = ref(false)
const errorEsquema = ref('')
const form = ref(estadoInicial())

function estadoInicial() {
  return {
    id: null, codigo: '', nombre: '', descripcion: '',
    icono: '📹', activa: true, orden: 100, urlBase: '',
    camposEsquema: '[\n  {"key": "url", "label": "URL de la reunión", "tipo": "url", "requerido": true}\n]',
    esInmutable: false,
  }
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_PLATAFORMAS_TELEMATICAS)
    plataformas.value = [...(data.plataformasTelematicas || [])].sort((a, b) =>
      (a.orden || 0) - (b.orden || 0) || (a.nombre || '').localeCompare(b.nombre || ''))
  } finally {
    loading.value = false
  }
}

function abrirAlta() {
  modoEdicion.value = false
  form.value = estadoInicial()
  errorEsquema.value = ''
  modalAbierto.value = true
}

function abrirEdicion(p) {
  modoEdicion.value = true
  form.value = { ...estadoInicial(), ...p }
  errorEsquema.value = ''
  modalAbierto.value = true
}

async function toggleActiva(p) {
  try {
    await executeMutation(UPDATE_PLATAFORMA_TELEMATICA, {
      data: { id: p.id, activa: !p.activa },
    })
    await cargar()
  } catch (e) {
    useToast().error('Error: ' + (e.message || e))
  }
}

async function guardar() {
  // Validación del JSON antes de enviar
  if (form.value.camposEsquema) {
    try {
      const parsed = JSON.parse(form.value.camposEsquema)
      if (!Array.isArray(parsed)) {
        errorEsquema.value = 'El esquema debe ser un array.'
        return
      }
    } catch (e) {
      errorEsquema.value = 'JSON inválido: ' + e.message
      return
    }
  }
  errorEsquema.value = ''
  guardando.value = true
  try {
    const { id, esInmutable, ...rest } = form.value
    if (modoEdicion.value) {
      await executeMutation(UPDATE_PLATAFORMA_TELEMATICA, { data: { id, ...rest } })
    } else {
      await executeMutation(CREATE_PLATAFORMA_TELEMATICA, { data: rest })
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
    titulo: 'Eliminar plataforma',
    mensaje: `¿Eliminar la plataforma «${form.value.nombre}»?`,
    variante: 'critica',
    etiquetaConfirmar: 'Eliminar',
  })
  if (!ok) return
  try {
    await executeMutation(DELETE_PLATAFORMAS_TELEMATICAS, { filter: { id: { eq: form.value.id } } })
    modalAbierto.value = false
    await cargar()
  } catch (e) {
    useToast().error('Error: ' + (e.message || e))
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
