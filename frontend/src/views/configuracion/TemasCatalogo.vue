<template>
  <AppLayout title="Temas de color" subtitle="Catálogo de temas visuales de la aplicación">
    <div class="flex gap-5 h-full">

      <!-- Lista de temas -->
      <div class="flex-1 min-w-0 overflow-y-auto space-y-2 pr-1">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs text-gray-500">{{ temas.length }} temas disponibles</p>
          <button @click="abrirNuevo"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
            <PlusIcon class="w-4 h-4" /> Nuevo tema
          </button>
        </div>

        <div v-if="cargando" class="text-sm text-gray-400 text-center py-8">Cargando temas…</div>

        <div v-for="t in temas" :key="t.id"
          class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center gap-4 hover:border-gray-300 transition-colors">
          <!-- Banda de colores -->
          <div class="flex rounded-lg overflow-hidden flex-shrink-0 shadow-sm">
            <div v-for="(c, i) in bandaColores(t)" :key="i"
              class="w-5 h-10" :style="{ backgroundColor: c }" />
          </div>
          <!-- Sidebar preview -->
          <div class="w-8 h-10 rounded-md flex-shrink-0 shadow-sm" :style="{ backgroundColor: t.sidebar }" />
          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-sm text-gray-900">{{ t.nombre }}</span>
              <span v-if="t.sistema"
                class="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500 uppercase tracking-wide">
                Sistema
              </span>
              <span v-if="!t.activo"
                class="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-red-50 text-red-500 uppercase tracking-wide">
                Inactivo
              </span>
            </div>
          </div>
          <!-- Acciones -->
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <button @click="abrirEditar(t)"
              class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Editar">
              <PencilIcon class="w-4 h-4" />
            </button>
            <button v-if="!t.sistema" @click="confirmarEliminar(t)"
              class="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
              title="Eliminar">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Panel editor -->
      <div v-if="editando" class="w-96 flex-shrink-0 bg-white rounded-xl border border-gray-200 flex flex-col overflow-hidden">
        <!-- Cabecera -->
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
          <h3 class="font-semibold text-gray-900 text-sm">
            {{ esNuevo ? 'Nuevo tema' : 'Editar tema' }}
          </h3>
          <button @click="cerrarEditor" class="text-gray-400 hover:text-gray-600 transition-colors">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          <!-- Nombre -->
          <div>
            <label class="editor-label">Nombre del tema</label>
            <input v-model="form.nombre" @input="autoSlug" type="text" class="editor-input" placeholder="Mi tema" />
          </div>

          <!-- Preview de fondo de página -->
          <div class="rounded-lg border border-gray-100 p-3 flex gap-3 items-center"
            :style="{ backgroundColor: form.pageBg }">
            <div class="w-10 h-16 rounded-md shadow" :style="{ backgroundColor: form.sidebar }" />
            <div class="flex-1 space-y-1.5">
              <div class="h-5 rounded-md shadow-sm flex items-center justify-center"
                :style="{ backgroundColor: form.topbar }">
                <div class="w-10 h-2 rounded" :style="{ backgroundColor: form.t200 }" />
              </div>
              <div class="h-8 rounded-md flex items-center justify-center"
                :style="{ backgroundColor: form.cardBg, border: `1px solid ${form.borderColor}` }">
                <div class="w-6 h-3 rounded-sm" :style="{ backgroundColor: form.t600 }" />
              </div>
              <div class="text-[8px] font-medium" :style="{ color: form.textMain }">Texto principal</div>
            </div>
          </div>

          <!-- Paleta primaria -->
          <div>
            <p class="editor-label mb-2">Paleta de color primario</p>
            <div class="space-y-1">
              <div v-for="shade in shades" :key="shade.key" class="flex items-center gap-2">
                <input type="color" v-model="form[shade.key]"
                  class="w-8 h-6 rounded cursor-pointer border-0 p-0 bg-transparent" />
                <div class="flex-1 h-5 rounded" :style="{ backgroundColor: form[shade.key] }" />
                <span class="text-[10px] font-mono text-gray-400 w-16 text-right">{{ shade.label }}</span>
                <span class="text-[10px] font-mono text-gray-500 w-16">{{ form[shade.key] }}</span>
              </div>
            </div>
          </div>

          <!-- Colores estructurales -->
          <div>
            <p class="editor-label mb-2">Estructura de la interfaz</p>
            <div class="space-y-2">
              <div v-for="s in structural" :key="s.key" class="flex items-center gap-3">
                <input type="color" v-model="form[s.key]"
                  class="w-8 h-6 rounded cursor-pointer border-0 p-0 bg-transparent flex-shrink-0" />
                <div class="flex-1">
                  <p class="text-xs font-medium text-gray-700 leading-none">{{ s.label }}</p>
                  <p class="text-[10px] text-gray-400 mt-0.5 font-mono">{{ s.var }}</p>
                </div>
                <span class="text-[10px] font-mono text-gray-500 w-16 text-right">{{ form[s.key] }}</span>
              </div>
            </div>
          </div>

          <!-- Activo -->
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="form.activo"
              class="h-3.5 w-3.5 rounded border-gray-300 text-purple-600" />
            <span class="text-xs text-gray-700">Tema activo (disponible para seleccionar)</span>
          </label>
        </div>

        <!-- Footer -->
        <div class="px-4 py-3 border-t border-gray-100 flex items-center gap-2">
          <button @click="guardar" :disabled="guardando"
            class="flex-1 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
          <button @click="previsualizar" type="button"
            class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Previsualizar tema en vivo">
            👁
          </button>
          <button @click="cerrarEditor" type="button"
            class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
        </div>
        <p v-if="errorGuardar" class="px-4 pb-2 text-xs text-red-500">{{ errorGuardar }}</p>
      </div>

    </div>

    <!-- Confirm delete -->
    <div v-if="eliminando" class="fixed inset-0 bg-black/30 z-50 flex items-center justify-center">
      <div class="bg-white rounded-xl shadow-xl p-5 max-w-sm w-full mx-4">
        <h3 class="font-semibold text-gray-900 mb-2">Eliminar tema</h3>
        <p class="text-sm text-gray-600 mb-4">
          ¿Eliminar el tema <strong>{{ eliminando.nombre }}</strong>? Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-2 justify-end">
          <button @click="eliminando = null"
            class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
            Cancelar
          </button>
          <button @click="ejecutarEliminar"
            class="px-3 py-1.5 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { PlusIcon, PencilIcon, TrashIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const orgConfigStore = useOrgConfigStore()

const temas    = ref([])
const cargando = ref(false)
const editando = ref(false)
const esNuevo  = ref(false)
const editObj  = ref(null)
const eliminando    = ref(null)
const guardando     = ref(false)
const errorGuardar  = ref('')

const shades = [
  { key: 't50',  label: '50  — muy claro' },
  { key: 't100', label: '100' },
  { key: 't200', label: '200' },
  { key: 't300', label: '300' },
  { key: 't400', label: '400' },
  { key: 't500', label: '500 — medio' },
  { key: 't600', label: '600 — primario ★' },
  { key: 't700', label: '700' },
  { key: 't800', label: '800' },
  { key: 't900', label: '900 — muy oscuro' },
]

const structural = [
  { key: 'sidebar',     label: 'Barra lateral',   var: '--t-sidebar' },
  { key: 'topbar',      label: 'Cabecera',         var: '--t-topbar' },
  { key: 'pageBg',      label: 'Fondo de página',  var: '--t-page-bg' },
  { key: 'cardBg',      label: 'Fondo de tarjetas', var: '--t-card-bg' },
  { key: 'textMain',    label: 'Texto principal',  var: '--t-text-main' },
  { key: 'textMuted',   label: 'Texto secundario', var: '--t-text-muted' },
  { key: 'borderColor', label: 'Bordes',           var: '--t-border' },
]

const emptyForm = () => ({
  nombre: '', slug: '',
  t50: '#f5f3ff', t100: '#ede9fe', t200: '#ddd6fe', t300: '#c4b5fd', t400: '#a78bfa',
  t500: '#8b5cf6', t600: '#7c3aed', t700: '#6d28d9', t800: '#5b21b6', t900: '#4c1d95',
  sidebar: 'hsl(262,82%,20%)',
  topbar: '#ffffff', pageBg: '#f5f3ff', cardBg: '#ffffff',
  textMain: '#111827', textMuted: '#6b7280', borderColor: '#e5e7eb',
  activo: true,
})

const form = reactive(emptyForm())

const bandaColores = (t) => [t.t50, t.t100, t.t200, t.t300, t.t400, t.t500, t.t600, t.t700, t.t800, t.t900]

function autoSlug() {
  if (!esNuevo.value) return
  form.slug = form.nombre
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

const GET = `query {
  temasUi {
    id nombre slug
    t50 t100 t200 t300 t400 t500 t600 t700 t800 t900
    sidebar topbar pageBg cardBg textMain textMuted borderColor
    sistema activo eliminado
  }
}`

const CREATE = `mutation($data: TemaUICreateInput!) {
  crearTemaUi(data: $data) { id nombre slug } }`

const UPDATE = `mutation($data: TemaUIUpdateInput!) {
  actualizarTemaUi(data: $data) { id } }`

const DELETE = `mutation($data: TemaUIUpdateInput!) {
  actualizarTemaUi(data: $data) { id } }`

async function cargar() {
  cargando.value = true
  try {
    const d = await graphqlClient.request(GET)
    temas.value = (d.temasUi ?? []).filter(t => !t.eliminado)
    orgConfigStore.setTemas(temas.value.filter(t => t.activo))
  } finally {
    cargando.value = false
  }
}

function abrirNuevo() {
  Object.assign(form, emptyForm())
  esNuevo.value = true
  editObj.value = null
  editando.value = true
  errorGuardar.value = ''
}

function abrirEditar(t) {
  Object.assign(form, {
    nombre: t.nombre, slug: t.slug,
    t50: t.t50, t100: t.t100, t200: t.t200, t300: t.t300, t400: t.t400,
    t500: t.t500, t600: t.t600, t700: t.t700, t800: t.t800, t900: t.t900,
    sidebar: t.sidebar, topbar: t.topbar,
    pageBg: t.pageBg, cardBg: t.cardBg,
    textMain: t.textMain, textMuted: t.textMuted, borderColor: t.borderColor,
    activo: t.activo,
  })
  esNuevo.value = false
  editObj.value = t
  editando.value = true
  errorGuardar.value = ''
}

function cerrarEditor() {
  editando.value = false
  // Revertir preview si estaba en preview
  const slug = orgConfigStore.tema
  const actual = temas.value.find(t => t.slug === slug)
  if (actual) orgConfigStore.applyTheme(actual, orgConfigStore.fuentePrincipal)
}

function previsualizar() {
  orgConfigStore.applyTheme({ ...form, slug: form.slug || '__preview__' }, orgConfigStore.fuentePrincipal)
}

async function guardar() {
  if (!form.nombre.trim() || !form.slug.trim()) {
    errorGuardar.value = 'Nombre e identificador son obligatorios'
    return
  }
  guardando.value = true
  errorGuardar.value = ''
  try {
    const campos = {
      nombre: form.nombre, slug: form.slug,
      t50: form.t50, t100: form.t100, t200: form.t200, t300: form.t300, t400: form.t400,
      t500: form.t500, t600: form.t600, t700: form.t700, t800: form.t800, t900: form.t900,
      sidebar: form.sidebar, topbar: form.topbar,
      pageBg: form.pageBg, cardBg: form.cardBg,
      textMain: form.textMain, textMuted: form.textMuted, borderColor: form.borderColor,
      activo: form.activo,
    }
    if (esNuevo.value) {
      await graphqlClient.request(CREATE, { data: campos })
    } else {
      await graphqlClient.request(UPDATE, { data: { id: editObj.value.id, ...campos } })
    }
    await cargar()
    editando.value = false
  } catch (e) {
    errorGuardar.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

function confirmarEliminar(t) { eliminando.value = t }

async function ejecutarEliminar() {
  try {
    await graphqlClient.request(DELETE, { data: { id: eliminando.value.id, eliminado: true } })
    await cargar()
    eliminando.value = null
  } catch (e) {
    console.error(e)
  }
}

cargar()
</script>

<style scoped>
.editor-label { @apply block text-xs font-medium text-gray-600 mb-0.5; }
.editor-input { @apply w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900 focus:outline-none focus:ring-1 focus:ring-purple-400 focus:border-purple-400; }
</style>
