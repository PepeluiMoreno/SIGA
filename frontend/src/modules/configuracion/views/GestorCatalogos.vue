<template>
  <AppLayout title="Catálogos" subtitle="Gestión de tipologías del sistema">
    <div class="flex -mx-4 sm:-mx-6 lg:mx-0 border-t border-gray-200 h-full">

      <!-- ── Panel izquierdo: navegación ─────────────────────────────── -->
      <nav class="w-max min-w-[10rem] flex-shrink-0 border-r border-gray-200 bg-gray-50 overflow-y-auto py-3 px-2">
        <div v-for="(grupo, i) in CATALOGOS" :key="grupo.grupo"
          :class="['mb-1', i > 0 && 'border-t border-gray-200 mt-1 pt-1']">
          <!-- Cabecera acordeón -->
          <button @click="toggleGrupo(grupo.grupo)"
            class="w-full flex items-center justify-between px-2 py-1 rounded hover:bg-gray-100 transition-colors">
            <span class="text-[11px] font-bold text-gray-700 uppercase tracking-widest whitespace-nowrap">
              {{ grupo.grupo }}
            </span>
            <ChevronDownIcon class="w-3 h-3 text-gray-400 flex-shrink-0 transition-transform duration-150"
              :class="grupoAbierto(grupo.grupo) ? '' : '-rotate-90'" />
          </button>
          <!-- Items del grupo -->
          <ul v-show="grupoAbierto(grupo.grupo)" class="space-y-0.5 mt-0.5 mb-1.5">
            <li v-for="cat in grupo.items" :key="cat.key">
              <button @click="seleccionar(cat)"
                :class="[
                  'w-full text-left px-2.5 py-1.5 rounded-md text-sm transition-colors flex items-center justify-between gap-1',
                  catalogoActivo?.key === cat.key
                    ? 'bg-purple-100 text-purple-800 font-semibold'
                    : 'text-gray-600 hover:bg-white hover:text-gray-900 hover:shadow-sm'
                ]">
                <span class="whitespace-nowrap">{{ cat.label }}</span>
                <ChevronRightIcon v-if="cat.tipo === 'link'" class="w-3 h-3 text-gray-300 flex-shrink-0" />
                <span v-else-if="catalogoActivo?.key === cat.key && !cargando"
                  class="text-[10px] bg-purple-200 text-purple-700 rounded-full px-1.5 py-0.5 font-medium flex-shrink-0">
                  {{ items.length }}
                </span>
              </button>
            </li>
          </ul>
        </div>
      </nav>

      <!-- ── Panel derecho: contenido ────────────────────────────────── -->
      <div class="flex-1 flex flex-col min-w-0 bg-white overflow-hidden">

        <!-- Placeholder vacío -->
        <div v-if="!catalogoActivo" class="flex-1 flex flex-col items-center justify-center text-center gap-3 text-gray-400">
          <ClipboardDocumentIcon class="w-12 h-12 opacity-30" />
          <p class="text-sm">Selecciona un catálogo</p>
        </div>

        <template v-else>
          <!-- Cabecera -->
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 flex-shrink-0">
            <div>
              <h2 class="font-semibold text-gray-900 text-base">{{ catalogoActivo.label }}</h2>
              <p class="text-xs text-gray-400 mt-0.5">{{ catalogoActivo.descripcion }}</p>
            </div>
            <button @click="abrirCrear"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors shadow-sm">
              <PlusIcon class="w-4 h-4" />
              Nuevo
            </button>
          </div>

          <!-- Barra búsqueda + filtros opcionales -->
          <div class="px-5 py-2 border-b border-gray-100 flex-shrink-0 flex items-center gap-3">
            <div class="relative max-w-xs flex-1">
              <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              <input v-model="busqueda" type="text" placeholder="Buscar..."
                class="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-md bg-gray-50
                       focus:bg-white focus:border-purple-400 focus:ring-1 focus:ring-purple-400 focus:outline-none transition-colors" />
            </div>
            <select v-if="catalogoActivo?.filtroPorCategoria && filtroCategoriasOpts.length"
              v-model="filtroCategoria"
              class="h-8 px-2 text-sm border border-gray-200 rounded-md bg-gray-50 focus:bg-white focus:border-purple-400 focus:ring-1 focus:ring-purple-400 focus:outline-none transition-colors">
              <option value="">Todas las categorías</option>
              <option v-for="opt in filtroCategoriasOpts" :key="opt.id" :value="opt.id">{{ opt.nombre }}</option>
            </select>
          </div>

          <!-- Cargando -->
          <div v-if="cargando" class="flex-1 flex items-center justify-center">
            <div class="w-7 h-7 rounded-full border-2 border-gray-200 border-t-purple-600 animate-spin"></div>
          </div>

          <!-- Error -->
          <div v-else-if="errorCarga" class="px-5 py-4 text-sm text-red-600 flex items-center gap-2">
            <span>⚠</span> {{ errorCarga }}
          </div>

          <!-- Sin resultados de búsqueda -->
          <div v-else-if="itemsFiltrados.length === 0 && busqueda"
            class="flex-1 flex items-center justify-center text-sm text-gray-400">
            Sin resultados para "{{ busqueda }}"
          </div>

          <!-- Vacío -->
          <div v-else-if="items.length === 0"
            class="flex-1 flex flex-col items-center justify-center text-center gap-2 text-gray-400">
            <InboxIcon class="w-8 h-8 opacity-40" />
            <p class="text-sm">Sin registros. Crea el primero.</p>
          </div>

          <!-- Tabla -->
          <div v-else class="flex-1 overflow-y-auto">
            <table class="w-full text-sm border-collapse">
              <thead class="sticky top-0 bg-white z-10">
                <tr class="border-b border-gray-100">
                  <th v-for="col in catalogoActivo.columnas" :key="col.key"
                    class="text-left px-5 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    {{ col.label }}
                  </th>
                  <th class="px-5 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in itemsFiltrados" :key="item.id"
                  class="border-b border-gray-50 hover:bg-purple-50/40 transition-colors group">

                  <td v-for="col in catalogoActivo.columnas" :key="col.key"
                    class="px-5 py-2.5 align-middle">

                    <!-- Color badge (nombre de estados con color) -->
                    <template v-if="col.key === 'nombre' && item.color">
                      <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-sm font-medium"
                        :style="{ background: item.color + '22', color: item.color, borderColor: item.color + '44' }"
                        style="border-width: 1px; border-style: solid;">
                        <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                          :style="{ background: item.color }"></span>
                        {{ item[col.key] }}
                      </span>
                    </template>

                    <!-- Toggle activo -->
                    <template v-else-if="col.type === 'toggle'">
                      <button @click="toggleActivo(item)" :disabled="toggling === item.id"
                        :class="[
                          'relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none',
                          item[col.key] ? 'bg-purple-500' : 'bg-gray-200',
                          toggling === item.id ? 'opacity-50 cursor-wait' : 'cursor-pointer'
                        ]">
                        <span :class="[
                          'inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-sm transition-transform duration-200',
                          item[col.key] ? 'translate-x-4' : 'translate-x-0.5'
                        ]" />
                      </button>
                    </template>

                    <!-- Bool (checkmark) -->
                    <template v-else-if="col.type === 'bool'">
                      <CheckIcon v-if="item[col.key]" class="w-4 h-4 text-green-500" />
                      <span v-else class="text-gray-300 text-xs">—</span>
                    </template>

                    <!-- Nombre normal (primero = bold) -->
                    <template v-else-if="col.key === 'nombre'">
                      <span class="font-medium text-gray-900">{{ item[col.key] ?? '—' }}</span>
                    </template>

                    <!-- Descripción y otros -->
                    <template v-else>
                      <span class="text-gray-500 text-xs max-w-xs line-clamp-2">
                        {{ col.format ? col.format(item) : (item[col.key] ?? '—') }}
                      </span>
                    </template>
                  </td>

                  <!-- Acciones (aparecen al hacer hover) -->
                  <td class="px-5 py-2.5 text-right">
                    <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button @click="abrirEditar(item)"
                        class="p-1.5 rounded-md text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors"
                        title="Editar">
                        <PencilIcon class="w-3.5 h-3.5" />
                      </button>
                      <button v-if="!item.esInmutable" @click="confirmarEliminar(item)"
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                        title="Eliminar">
                        <TrashIcon class="w-3.5 h-3.5" />
                      </button>
                      <span v-else class="p-1.5 text-gray-300" title="Registro del sistema — no eliminable">
                        <LockClosedIcon class="w-3.5 h-3.5" />
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>

    <!-- ── Modal crear / editar ────────────────────────────────────── -->
    <Transition name="drawer">
      <div v-if="drawerAbierto" class="fixed inset-0 z-50 flex items-center justify-center px-4">
        <div class="fixed inset-0 bg-black/30 backdrop-blur-[1px]" @click="cerrarDrawer" />
        <div class="relative w-full max-w-md bg-white rounded-xl shadow-2xl flex flex-col max-h-[90vh]">

          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-900">
              <template v-if="itemEditando">
                {{ itemEditando.nombre ?? itemEditando.codigo ?? (catalogoActivo?.editPrefix ?? 'Editar') + ' ' + catalogoActivo?.labelSingular }}
              </template>
              <template v-else>
                {{ (catalogoActivo?.createPrefix ?? 'Nuevo') }} {{ catalogoActivo?.labelSingular }}
              </template>
            </h3>
            <button @click="cerrarDrawer"
              class="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            <div v-for="campo in catalogoActivo?.campos" :key="campo.name">
              <label v-if="campo.type !== 'checkbox'" class="block text-xs font-medium text-gray-600 mb-1">
                {{ campo.label }}<span v-if="campo.required" class="text-red-400 ml-0.5">*</span>
              </label>

              <input v-if="campo.type === 'text' || !campo.type"
                v-model="formulario[campo.name]" type="text"
                :required="campo.required" :maxlength="campo.maxLength"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md
                       focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none transition-colors" />

              <textarea v-else-if="campo.type === 'textarea'"
                v-model="formulario[campo.name]" rows="3"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md
                       focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none resize-none transition-colors"></textarea>

              <div v-else-if="campo.type === 'number'">
                <input v-model.number="formulario[campo.name]" type="number" :min="campo.min ?? 0"
                  class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md
                         focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none transition-colors" />
                <p v-if="campo.hint" class="mt-1 text-xs text-gray-400">{{ campo.hint }}</p>
              </div>

              <div v-else-if="campo.type === 'color'" class="space-y-2">
                <div class="flex items-center gap-2 flex-wrap">
                  <button v-for="c in COLORES_PRESET" :key="c" type="button"
                    @click="formulario[campo.name] = c"
                    class="w-7 h-7 rounded-full transition-all border-2"
                    :class="formulario[campo.name] === c ? 'border-gray-700 scale-110' : 'border-transparent hover:scale-105'"
                    :style="{ background: c }" />
                </div>
                <div class="flex items-center gap-2">
                  <label class="relative cursor-pointer">
                    <span class="w-9 h-9 rounded-lg border border-gray-300 block shadow-inner"
                      :style="{ background: formulario[campo.name] || '#6B7280' }"></span>
                    <input v-model="formulario[campo.name]" type="color" class="sr-only" />
                  </label>
                  <input v-model="formulario[campo.name]" type="text" placeholder="#RRGGBB"
                    class="w-28 px-2 py-1 text-xs font-mono border border-gray-300 rounded-md
                           focus:border-purple-400 focus:outline-none" />
                </div>
              </div>

              <div v-else-if="campo.type === 'select'" class="space-y-1.5">
                <div class="flex gap-2">
                  <select v-model="formulario[campo.name]"
                    class="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-md
                           focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none transition-colors">
                    <option value="">{{ campo.emptyLabel ?? 'Sin selección' }}</option>
                    <option v-for="opt in selectOptions[campo.name] ?? []"
                      :key="opt[campo.optionValue ?? 'id']"
                      :value="opt[campo.optionValue ?? 'id']">
                      {{ opt[campo.optionLabel ?? 'nombre'] }}
                    </option>
                  </select>
                  <button v-if="campo.allowCreate" type="button"
                    @click="inlineCreateOpen[campo.name] = !inlineCreateOpen[campo.name]"
                    class="px-2.5 rounded-md border border-gray-300 text-gray-500
                           hover:text-purple-600 hover:border-purple-400 transition-colors"
                    title="Crear nueva categoría">
                    <PlusIcon class="w-4 h-4" />
                  </button>
                </div>
                <div v-if="campo.allowCreate && inlineCreateOpen[campo.name]"
                  class="flex gap-2 p-2.5 bg-purple-50 rounded-md border border-purple-100">
                  <input v-model="inlineCreateValue[campo.name].nombre" type="text"
                    :placeholder="`Nueva ${campo.labelSingular ?? campo.label.toLowerCase()}…`"
                    @keyup.enter="crearInline(campo)"
                    class="flex-1 px-2.5 py-1 text-sm border border-gray-300 rounded
                           focus:border-purple-400 focus:outline-none" />
                  <button type="button" @click="crearInline(campo)"
                    :disabled="inlineCreateLoading[campo.name]"
                    class="px-3 py-1 text-xs bg-purple-600 text-white rounded
                           hover:bg-purple-700 disabled:opacity-50 transition-colors">
                    {{ inlineCreateLoading[campo.name] ? '…' : 'Crear' }}
                  </button>
                </div>
              </div>

              <label v-else-if="campo.type === 'checkbox'"
                class="flex items-center gap-2.5 cursor-pointer select-none mt-1">
                <input v-model="formulario[campo.name]" type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                <span class="text-sm text-gray-700">{{ campo.description || campo.label }}</span>
              </label>
            </div>

            <p v-if="errorGuardado" class="text-xs text-red-600">⚠ {{ errorGuardado }}</p>
          </div>

          <div class="px-5 py-3.5 border-t border-gray-100 flex justify-end gap-2 flex-shrink-0">
            <button type="button" @click="cerrarDrawer"
              class="px-4 py-1.5 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button @click="guardar" :disabled="guardando"
              class="px-4 py-1.5 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700
                     disabled:opacity-50 transition-colors flex items-center gap-1.5">
              <span v-if="guardando" class="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin"></span>
              {{ guardando ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── Modal conflicto estado inicial ─────────────────────────── -->
    <div v-if="modalConfirmInicial" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="fixed inset-0 bg-black/25" @click="modalConfirmInicial = false" />
      <div class="relative bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full">
        <div class="flex items-start gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
            <ExclamationTriangleIcon class="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">Estado inicial ya definido</h3>
            <p class="text-sm text-gray-500 mt-1">
              El estado <strong class="text-gray-800">{{ inicialConflicto?.nombre }}</strong>
              ya está marcado como estado inicial.<br>
              ¿Quieres reemplazarlo por el nuevo?
            </p>
          </div>
        </div>
        <div class="flex justify-end gap-2">
          <button @click="modalConfirmInicial = false"
            class="px-3 py-1.5 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button @click="confirmarCambioInicial" :disabled="guardando"
            class="px-3 py-1.5 text-sm bg-amber-500 text-white rounded-md hover:bg-amber-600 disabled:opacity-50 transition-colors">
            Sí, cambiar
          </button>
        </div>
      </div>
    </div>

    <!-- ── Modal eliminar ───────────────────────────────────────────── -->
    <div v-if="modalEliminar" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="fixed inset-0 bg-black/25" @click="modalEliminar = false" />
      <div class="relative bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full">
        <div class="flex items-start gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
            <TrashIcon class="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">Eliminar registro</h3>
            <p class="text-sm text-gray-500 mt-0.5">
              <strong class="text-gray-700">{{ itemAEliminar?.nombre }}</strong>
            </p>
          </div>
        </div>
        <ErrorAlert v-if="errorEliminar" :message="errorEliminar" />
        <p v-else class="text-sm text-gray-500 mb-5">
          Esta acción eliminará el registro permanentemente y no se puede deshacer.
        </p>
        <div class="flex justify-end gap-2">
          <button @click="modalEliminar = false"
            class="px-3 py-1.5 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button v-if="!errorEliminar" @click="eliminar" :disabled="eliminando"
            class="px-3 py-1.5 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center gap-1.5">
            <span v-if="eliminando" class="w-3 h-3 rounded-full border-2 border-white/40 border-t-white animate-spin"></span>
            {{ eliminando ? 'Eliminando…' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import {
  PlusIcon, MagnifyingGlassIcon, PencilIcon, TrashIcon, CheckIcon, XMarkIcon,
  ChevronDownIcon, ChevronRightIcon, LockClosedIcon,
} from '@heroicons/vue/24/outline'
import * as Q from '@/graphql/queries/catalogos.js'

const router = useRouter()

const sortItems = items => [...items].sort((a, b) => a.label.localeCompare(b.label, 'es'))

// ── Paleta de colores preset ──────────────────────────────────────────────────
const COLORES_PRESET = [
  '#3B82F6', '#6366F1', '#8B5CF6', '#EC4899', '#EF4444',
  '#F97316', '#F59E0B', '#10B981', '#14B8A6', '#6B7280',
]

const orgConfig = useOrgConfigStore()

// ── Acordeón del sidebar ──────────────────────────────────────────────────────
const gruposColapsados = ref({})
function grupoAbierto(nombre) { return !gruposColapsados.value[nombre] }
function toggleGrupo(nombre) { gruposColapsados.value[nombre] = !gruposColapsados.value[nombre] }

// ── Definición de catálogos ───────────────────────────────────────────────────
const CATALOGOS = computed(() => [
  {
    grupo: orgConfig.Miembros,
    items: [
      {
        key: 'tiposMiembro', label: `Tipos de ${orgConfig.miembro}`, labelSingular: `Tipo de ${orgConfig.miembro}`,
        descripcion: 'Socio, Simpatizante, Juvenil…',
        queryName: 'tiposMiembro', query: Q.GET_TIPOS_MIEMBRO,
        mutations: { create: Q.CREATE_TIPO_MIEMBRO, update: Q.UPDATE_TIPO_MIEMBRO, delete: Q.DELETE_TIPO_MIEMBRO },
        columnas: [
          { key: 'nombre',        label: 'Nombre' },
          { key: 'descripcion',   label: 'Descripción' },
          { key: 'requiereCuota', label: 'Cuota', type: 'bool' },
          { key: 'puedeVotar',    label: 'Vota', type: 'bool' },
          { key: 'motivoReduccion', label: 'Motivo reducción',
            format: item => item.motivoReduccion
              ? `${item.motivoReduccion.codigo} (-${item.motivoReduccion.porcentajeReduccion}%)`
              : '—' },
          { key: 'activo',        label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',        label: 'Nombre',        type: 'text',     required: true, maxLength: 100 },
          { name: 'descripcion',   label: 'Descripción',   type: 'textarea' },
          { name: 'requiereCuota', label: 'Requiere cuota', type: 'checkbox', default: true },
          { name: 'puedeVotar',   label: 'Puede votar',    type: 'checkbox', default: false },
          {
            name: 'motivoReduccionId', label: 'Motivo reducción por defecto (Flujo 1 — D1.2)',
            type: 'select',
            optionsQuery: Q.GET_MOTIVOS_REDUCCION_CUOTA,
            optionsQueryName: 'motivosReduccionCuota',
            optionLabel: m => `${m.codigo} — ${m.nombre} (-${m.porcentajeReduccion}%)${m.porcentajeReduccion >= 100 ? ' [excluido]' : ''}`,
            optionValue: m => m.id,
          },
          { name: 'activo',        label: 'En uso',         type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosMiembro', label: 'Situaciones', labelSingular: 'Situación',
        descripcion: 'Alta, Baja, Suspendida…',
        queryName: 'estadosMiembro', query: Q.GET_ESTADOS_MIEMBRO,
        mutations: { create: Q.CREATE_ESTADO_MIEMBRO, update: Q.UPDATE_ESTADO_MIEMBRO, delete: Q.DELETE_ESTADO_MIEMBRO },
        columnas: [
          { key: 'nombre',     label: 'Nombre' },
          { key: 'descripcion',label: 'Descripción' },
          { key: 'orden',      label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',     label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',        type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',   type: 'textarea' },
          { name: 'color',       label: 'Color',         type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',         type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',        type: 'checkbox', default: true },
        ],
      },
      {
        key: 'motivosBaja', label: 'Motivos de baja', labelSingular: 'Motivo de baja',
        descripcion: 'Voluntaria, Impago, Fallecimiento…',
        queryName: 'motivosBaja', query: Q.GET_MOTIVOS_BAJA,
        mutations: { create: Q.CREATE_MOTIVO_BAJA, update: Q.UPDATE_MOTIVO_BAJA, delete: Q.DELETE_MOTIVO_BAJA },
        columnas: [
          { key: 'nombre',                label: 'Nombre' },
          { key: 'descripcion',           label: 'Descripción' },
          { key: 'requiereDocumentacion', label: 'Doc.', type: 'bool' },
          { key: 'activo',                label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',                label: 'Nombre',                  type: 'text',     required: true },
          { name: 'descripcion',           label: 'Descripción',             type: 'textarea' },
          { name: 'requiereDocumentacion', label: 'Requiere documentación',  type: 'checkbox', default: false },
          { name: 'activo',                label: 'En uso',                  type: 'checkbox', default: true },
        ],
      },
      {
        key: 'categoriasHabilidad', label: 'Categorías de habilidad', labelSingular: 'Categoría de habilidad',
        createPrefix: 'Nueva', editPrefix: 'Editar',
        descripcion: 'Técnica, Comunicación, Logística…',
        queryName: 'categoriasHabilidad', query: Q.GET_CATEGORIAS_HABILIDAD,
        mutations: { create: Q.CREATE_CATEGORIA_HABILIDAD, update: Q.UPDATE_CATEGORIA_HABILIDAD, delete: Q.DELETE_CATEGORIA_HABILIDAD },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true, maxLength: 100 },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'nivelesEstudios', label: 'Niveles de estudios', labelSingular: 'Nivel de estudios',
        descripcion: 'Primaria, ESO, Bachillerato, FP, Grado, Máster…',
        queryName: 'nivelesEstudios', query: Q.GET_NIVELES_ESTUDIOS,
        mutations: { create: Q.CREATE_NIVEL_ESTUDIOS, update: Q.UPDATE_NIVEL_ESTUDIOS, delete: Q.DELETE_NIVEL_ESTUDIOS },
        columnas: [
          { key: 'orden',       label: 'Orden' },
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true, maxLength: 100 },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'orden',       label: 'Orden',       type: 'number',   default: 0 },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'nivelesHabilidad', label: 'Niveles de habilidad', labelSingular: 'Nivel de habilidad',
        descripcion: 'Principiante, Suficiente, Bueno, Experto…',
        queryName: 'nivelesHabilidad', query: Q.GET_NIVELES_HABILIDAD,
        mutations: { create: Q.CREATE_NIVEL_HABILIDAD, update: Q.UPDATE_NIVEL_HABILIDAD, delete: Q.DELETE_NIVEL_HABILIDAD },
        columnas: [
          { key: 'orden',       label: 'Orden' },
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true, maxLength: 100 },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'orden',       label: 'Orden',       type: 'number',   default: 0 },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'habilidades', label: 'Habilidades', labelSingular: 'Habilidad',
        createPrefix: 'Nueva', editPrefix: 'Editar',
        descripcion: 'Conocimientos y competencias del voluntariado…',
        queryName: 'habilidades', query: Q.GET_HABILIDADES_CATALOGO,
        mutations: { create: Q.CREATE_HABILIDAD, update: Q.UPDATE_HABILIDAD, delete: Q.DELETE_HABILIDAD },
        filtroPorCategoria: { optionsQuery: Q.GET_CATEGORIAS_HABILIDAD, optionsQueryName: 'categoriasHabilidad' },
        sortFn: (a, b) => {
          const cA = a.categoria?.nombre ?? '', cB = b.categoria?.nombre ?? ''
          if (cA !== cB) return cA.localeCompare(cB, 'es')
          return a.nombre.localeCompare(b.nombre, 'es')
        },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'categoria',   label: 'Categoría', format: item => item.categoria?.nombre ?? '—' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',       label: 'Nombre',      type: 'text',     required: true, maxLength: 150 },
          {
            name: 'categoriaId', label: 'Categoría', type: 'select',
            optionsQuery: Q.GET_CATEGORIAS_HABILIDAD, optionsQueryName: 'categoriasHabilidad',
            optionLabel: 'nombre', optionValue: 'id',
            allowCreate: true, createMutation: Q.CREATE_CATEGORIA_HABILIDAD,
            labelSingular: 'categoría', emptyLabel: 'Sin categoría',
          },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
    ],
  },
  {
    grupo: 'Económico',
    items: [
      {
        key: 'motivosReduccionCuota', label: 'Motivos de reducción de cuota', labelSingular: 'Motivo de reducción',
        descripcion: 'Joven, Parado, Jubilado, Honor… ≥100% excluye al socio del proceso',
        queryName: 'motivosReduccionCuota', query: Q.GET_MOTIVOS_REDUCCION_CUOTA,
        mutations: {
          create: Q.CREATE_MOTIVO_REDUCCION_CUOTA,
          update: Q.UPDATE_MOTIVO_REDUCCION_CUOTA,
          delete: Q.DELETE_MOTIVO_REDUCCION_CUOTA,
        },
        columnas: [
          { key: 'codigo', label: 'Código' },
          { key: 'nombre', label: 'Nombre' },
          { key: 'porcentajeReduccion', label: '% Reducción',
            format: item => `${item.porcentajeReduccion}%${item.porcentajeReduccion >= 100 ? ' (excluye)' : ''}` },
          { key: 'orden', label: 'Orden' },
          { key: 'activo', label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'codigo',  label: 'Código (único, mayúsculas)', type: 'text', required: true, maxLength: 30 },
          { name: 'nombre',  label: 'Nombre',                      type: 'text', required: true, maxLength: 100 },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'porcentajeReduccion', label: '% de reducción (0–100; ≥100 = excluye del proceso, D1.4)',
            type: 'number', required: true, default: 0 },
          { name: 'orden',  label: 'Orden', type: 'number', default: 0 },
          { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
        ],
      },
      {
        key: 'formasPago', label: 'Formas de pago', labelSingular: 'Forma de pago',
        descripcion: 'Transferencia, Domiciliación, Tarjeta…',
        queryName: 'formasPago', query: Q.GET_FORMAS_PAGO_CATALOGO,
        mutations: { create: Q.CREATE_FORMA_PAGO, update: Q.UPDATE_FORMA_PAGO, delete: Q.DELETE_FORMA_PAGO },
        beforeSave: (data) => {
          if (!data.codigo) {
            data.codigo = crypto.randomUUID().replace(/-/g, '').slice(0, 30)
          }
        },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text', required: true, maxLength: 100 },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosCuota', label: 'Estados de cuota', labelSingular: 'Estado de cuota',
        descripcion: 'Pendiente, Pagada, Vencida…',
        queryName: 'estadosCuota', query: Q.GET_ESTADOS_CUOTA,
        mutations: { create: Q.CREATE_ESTADO_CUOTA, update: Q.UPDATE_ESTADO_CUOTA, delete: Q.DELETE_ESTADO_CUOTA },
        columnas: [
          { key: 'nombre',     label: 'Nombre' },
          { key: 'descripcion',label: 'Descripción' },
          { key: 'orden',      label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',     label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',            type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',       type: 'textarea' },
          { name: 'color',       label: 'Color',             type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',             type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',            type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosRemesa', label: 'Estados de remesa', labelSingular: 'Estado de remesa',
        descripcion: 'Borrador, Enviada, Procesada…',
        queryName: 'estadosRemesa', query: Q.GET_ESTADOS_REMESA,
        mutations: { create: Q.CREATE_ESTADO_REMESA, update: Q.UPDATE_ESTADO_REMESA, delete: Q.DELETE_ESTADO_REMESA },
        columnas: [
          { key: 'nombre',     label: 'Nombre' },
          { key: 'descripcion',label: 'Descripción' },
          { key: 'orden',      label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',     label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',            type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',       type: 'textarea' },
          { name: 'color',       label: 'Color',             type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',             type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',            type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosDonacion', label: 'Estados de donación', labelSingular: 'Estado de donación',
        descripcion: 'Pendiente, Recibida, Certificada…',
        queryName: 'estadosDonacion', query: Q.GET_ESTADOS_DONACION,
        mutations: { create: Q.CREATE_ESTADO_DONACION, update: Q.UPDATE_ESTADO_DONACION, delete: Q.DELETE_ESTADO_DONACION },
        columnas: [
          { key: 'nombre',     label: 'Nombre' },
          { key: 'descripcion',label: 'Descripción' },
          { key: 'orden',      label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',     label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',            type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',       type: 'textarea' },
          { name: 'color',       label: 'Color',             type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',             type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',            type: 'checkbox', default: true },
        ],
      },
    ],
  },
  {
    grupo: 'Campañas',
    items: [
      {
        key: 'tiposCampania', label: 'Tipos de campaña', labelSingular: 'Tipo de campaña',
        descripcion: 'Recaudación, Sensibilización…',
        queryName: 'tiposCampania', query: Q.GET_TIPOS_CAMPANIA,
        mutations: { create: Q.CREATE_TIPO_CAMPANIA, update: Q.UPDATE_TIPO_CAMPANIA, delete: Q.DELETE_TIPO_CAMPANIA },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosCampania', label: 'Estados de campaña', labelSingular: 'Estado de campaña',
        descripcion: 'Borrador, Activa, Finalizada…',
        queryName: 'estadosCampania', query: Q.GET_ESTADOS_CAMPANIA,
        mutations: { create: Q.CREATE_ESTADO_CAMPANIA, update: Q.UPDATE_ESTADO_CAMPANIA, delete: Q.DELETE_ESTADO_CAMPANIA },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'orden',       label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',      label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',            type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',       type: 'textarea' },
          { name: 'color',       label: 'Color',             type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',             type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',            type: 'checkbox', default: true },
        ],
      },
      {
        key: 'tiposMetaCampania', label: 'Tipos de meta', labelSingular: 'Tipo de meta',
        descripcion: 'Recaudación (€), Participantes, Firmas…',
        queryName: 'tiposMetaCampania', query: Q.GET_TIPOS_META_CAMPANIA,
        mutations: { create: Q.CREATE_TIPO_META_CAMPANIA, update: Q.UPDATE_TIPO_META_CAMPANIA, delete: Q.DELETE_TIPO_META_CAMPANIA },
        columnas: [
          { key: 'nombre',       label: 'Nombre' },
          { key: 'descripcion',  label: 'Descripción' },
          { key: 'unidadMedida', label: 'Unidad' },
          { key: 'activo',       label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',       label: 'Nombre',          type: 'text',     required: true },
          { name: 'descripcion',  label: 'Descripción',     type: 'textarea' },
          { name: 'unidadMedida', label: 'Unidad de medida', type: 'text',    required: true, placeholder: 'ej: €, personas, firmas' },
          { name: 'activo',       label: 'En uso',          type: 'checkbox', default: true },
        ],
      },
      {
        key: 'tiposCanalDifusion', label: 'Canales de difusión', labelSingular: 'Canal de difusión',
        descripcion: 'Email, Redes sociales, Prensa…',
        queryName: 'tiposCanalDifusion', query: Q.GET_TIPOS_CANAL_DIFUSION,
        mutations: { create: Q.CREATE_TIPO_CANAL_DIFUSION, update: Q.UPDATE_TIPO_CANAL_DIFUSION, delete: Q.DELETE_TIPO_CANAL_DIFUSION },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'plantillasCampania', label: 'Plantillas de campaña', labelSingular: 'Plantilla',
        tipo: 'link', ruta: '/parametrizacion/plantillas-campania',
        descripcion: '1 por tipo de campaña — metas, partidas, actividades y tareas predefinidas',
      },
    ],
  },
  {
    grupo: 'Actividades',
    items: [
      {
        key: 'tiposActividad', label: 'Tipos de actividad', labelSingular: 'Tipo de actividad',
        descripcion: 'Formación, Evento, Reunión…',
        queryName: 'tiposActividad', query: Q.GET_TIPOS_ACTIVIDAD,
        mutations: { create: Q.CREATE_TIPO_ACTIVIDAD, update: Q.UPDATE_TIPO_ACTIVIDAD, delete: Q.DELETE_TIPO_ACTIVIDAD },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
      {
        key: 'estadosActividad', label: 'Estados de actividad', labelSingular: 'Estado de actividad',
        descripcion: 'Propuesta, Aprobada, Completada…',
        queryName: 'estadosActividad', query: Q.GET_ESTADOS_ACTIVIDAD,
        mutations: { create: Q.CREATE_ESTADO_ACTIVIDAD, update: Q.UPDATE_ESTADO_ACTIVIDAD, delete: Q.DELETE_ESTADO_ACTIVIDAD },
        columnas: [
          { key: 'nombre',     label: 'Nombre' },
          { key: 'descripcion',label: 'Descripción' },
          { key: 'orden',      label: 'Orden' },
          { key: 'esInicial',  label: 'Inicial', type: 'bool' },
          { key: 'activo',     label: 'Activo',  type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',            type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción',       type: 'textarea' },
          { name: 'color',       label: 'Color',             type: 'color',    default: '#6B7280' },
          { name: 'orden',       label: 'Orden',             type: 'number',   default: 0 },
          { name: 'esInicial', label: 'Es estado inicial', type: 'checkbox', default: false },
          { name: 'activo',      label: 'En uso',            type: 'checkbox', default: true },
        ],
      },
    ],
  },
  {
    grupo: 'Grupos',
    items: [
      {
        key: 'tiposGrupo', label: 'Tipos de grupo', labelSingular: 'Tipo de grupo',
        descripcion: 'Comisión, Equipo de trabajo…',
        queryName: 'tiposGrupo', query: Q.GET_TIPOS_GRUPO,
        mutations: { create: Q.CREATE_TIPO_GRUPO, update: Q.UPDATE_TIPO_GRUPO, delete: Q.DELETE_TIPO_GRUPO },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
    ],
  },
  {
    grupo: 'Convenios de colaboración',
    items: [
      {
        key: 'estadosConvenio', label: 'Estados de convenio', labelSingular: 'Estado de convenio',
        descripcion: 'Borrador, Vigente, Vencido, Rescindido…',
        queryName: 'estadosConvenio', query: Q.GET_ESTADOS_CONVENIO,
        mutations: { create: Q.CREATE_ESTADO_CONVENIO, update: Q.UPDATE_ESTADO_CONVENIO, delete: Q.DELETE_ESTADO_CONVENIO },
        columnas: [
          { key: 'nombre',      label: 'Nombre' },
          { key: 'descripcion', label: 'Descripción' },
          { key: 'orden',       label: 'Orden' },
          { key: 'activo',      label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',      label: 'Nombre',      type: 'text',     required: true },
          { name: 'descripcion', label: 'Descripción', type: 'textarea' },
          { name: 'orden',       label: 'Orden',       type: 'number',   default: 0 },
          { name: 'activo',      label: 'En uso',      type: 'checkbox', default: true },
        ],
      },
    ],
  },
  {
    grupo: 'Usuarios',
    items: [
      {
        key: 'tiposVinculacion', label: 'Tipos de vinculación', labelSingular: 'Tipo de vinculación',
        descripcion: 'Socio, Simpatizante, Empleado externo…',
        queryName: 'tiposVinculacion', query: Q.GET_TIPOS_VINCULACION_CATALOGO,
        mutations: { create: Q.CREATE_TIPO_VINCULACION, update: Q.UPDATE_TIPO_VINCULACION, delete: Q.DELETE_TIPO_VINCULACION },
        columnas: [
          { key: 'nombre',         label: 'Nombre' },
          { key: 'requiereEntidad', label: 'Requiere entidad', type: 'bool' },
          { key: 'activo',         label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',         label: 'Nombre',                     type: 'text',     required: true, maxLength: 150 },
          { name: 'requiereEntidad', label: 'Requiere especificar entidad', type: 'checkbox', default: false },
          { name: 'activo',         label: 'En uso',                     type: 'checkbox', default: true },
        ],
      },
    ],
  },
  // ── Estructura Organizativa ────────────────────────────────────────────────
  {
    grupo: 'Estructura Organizativa',
    items: [
      {
        key: 'ambitosGeograficos', label: 'Ámbitos geográficos', labelSingular: 'Ámbito geográfico',
        createPrefix: 'Nuevo', editPrefix: 'Editar',
        descripcion: 'Nacional, CCAA, Provincia, Comarca, Municipio…',
        queryName: 'ambitosGeograficos', query: Q.GET_AMBITOS_GEOGRAFICOS,
        mutations: { create: Q.CREATE_AMBITO_GEOGRAFICO, update: Q.UPDATE_AMBITO_GEOGRAFICO, delete: Q.DELETE_AMBITO_GEOGRAFICO },
        sortFn: (a, b) => a.granularidad - b.granularidad || a.nombre.localeCompare(b.nombre, 'es'),
        columnas: [
          { key: 'nombre',       label: 'Nombre' },
          { key: 'granularidad', label: 'Orden' },
          { key: 'descripcion',  label: 'Descripción' },
          { key: 'activo',       label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',       label: 'Nombre',                    type: 'text',   required: true, maxLength: 100 },
          { name: 'descripcion',  label: 'Descripción',               type: 'textarea' },
          {
            name: 'granularidad', label: 'Granularidad (1=más amplio)', type: 'number',
            default: 50,
            hint: 'Número menor = ámbito más amplio. Ej: Nacional=10, CCAA=20, Provincia=30…',
          },
          { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
        ],
      },
      {
        key: 'nivelesOrganizativos', label: 'Niveles organizativos', labelSingular: 'Nivel organizativo',
        createPrefix: 'Nuevo', editPrefix: 'Editar',
        descripcion: 'Tipos de unidades: Sede central, Autonómica, Provincial…',
        queryName: 'nivelesOrganizativos', query: Q.GET_NIVELES_ORGANIZATIVOS,
        mutations: { create: Q.CREATE_NIVEL_ORGANIZATIVO, update: Q.UPDATE_NIVEL_ORGANIZATIVO, delete: Q.DELETE_NIVEL_ORGANIZATIVO },
        sortFn: (a, b) => (a.nivel ?? 99) - (b.nivel ?? 99) || a.nombre.localeCompare(b.nombre, 'es'),
        columnas: [
          { key: 'nivel',            label: 'Nivel' },
          { key: 'nombre',           label: 'Nombre' },
          { key: 'naturaleza',       label: 'Naturaleza' },
          { key: 'ambitoGeografico', label: 'Ámbito geográfico', format: item => item.ambitoGeografico?.nombre ?? '—' },
          { key: 'activo',           label: 'Activo', type: 'toggle' },
        ],
        campos: [
          { name: 'nombre',    label: 'Nombre', type: 'text', required: true, maxLength: 100 },
          {
            name: 'naturaleza', label: 'Naturaleza', type: 'select', required: true,
            optionsStatic: [
              { value: 'TERRITORIAL',    label: 'Territorial' },
              { value: 'FUNCIONAL',      label: 'Funcional' },
              { value: 'PROGRAMATICA',   label: 'Programática' },
              { value: 'ADMINISTRATIVA', label: 'Administrativa' },
            ],
          },
          {
            name: 'vinculo', label: 'Vínculo', type: 'select', required: true,
            optionsStatic: [
              { value: 'INTERNA',  label: 'Interna' },
              { value: 'FILIAL',   label: 'Filial' },
              { value: 'FEDERADA', label: 'Federada' },
            ],
          },
          { name: 'nivel', label: 'Nivel jerárquico (1=raíz)', type: 'number', default: null },
          {
            name: 'padreTipoId', label: 'Tipo padre', type: 'select',
            optionsQuery: Q.GET_NIVELES_ORGANIZATIVOS, optionsQueryName: 'nivelesOrganizativos',
            optionLabel: 'nombre', optionValue: 'id',
            emptyLabel: 'Sin padre (raíz)',
          },
          {
            name: 'ambitoGeograficoId', label: 'Ámbito geográfico', type: 'select',
            optionsQuery: Q.GET_AMBITOS_GEOGRAFICOS, optionsQueryName: 'ambitosGeograficos',
            optionLabel: 'nombre', optionValue: 'id',
            emptyLabel: 'Sin ámbito definido',
          },
          { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
        ],
      },
    ],
  },
].map(g => ({ ...g, items: sortItems(g.items) }))
  .sort((a, b) => a.grupo.localeCompare(b.grupo, 'es'))
)

// ── Estado ────────────────────────────────────────────────────────────────────
const catalogoActivo         = ref(null)
const items                  = ref([])
const busqueda               = ref('')
const filtroCategoria        = ref('')
const filtroCategoriasOpts   = ref([])
const cargando       = ref(false)
const errorCarga     = ref('')
const drawerAbierto  = ref(false)
const itemEditando   = ref(null)
const formulario     = ref({})
const guardando      = ref(false)
const errorGuardado  = ref('')
const toggling       = ref(null)
const modalEliminar       = ref(false)
const itemAEliminar       = ref(null)
const eliminando          = ref(false)
const errorEliminar       = ref('')
const modalConfirmInicial = ref(false)
const inicialConflicto    = ref(null)

// Select con creación inline
const selectOptions      = ref({})
const inlineCreateOpen   = ref({})
const inlineCreateValue  = ref({})
const inlineCreateLoading = ref({})

// ── Computed ──────────────────────────────────────────────────────────────────
const itemsFiltrados = computed(() => {
  let result = items.value
  if (busqueda.value.trim()) {
    const q = busqueda.value.toLowerCase()
    result = result.filter(i => i.nombre?.toLowerCase().includes(q))
  }
  if (filtroCategoria.value) {
    result = result.filter(i => i.categoria?.id === filtroCategoria.value)
  }
  if (catalogoActivo.value?.sortFn) {
    result = [...result].sort(catalogoActivo.value.sortFn)
  }
  return result
})

// ── Funciones ─────────────────────────────────────────────────────────────────
async function cargarDatos() {
  if (!catalogoActivo.value) return
  cargando.value = true
  errorCarga.value = ''
  try {
    const data = await graphqlClient.request(catalogoActivo.value.query)
    items.value = data[catalogoActivo.value.queryName] ?? []
  } catch (e) {
    errorCarga.value = e?.response?.errors?.[0]?.message ?? 'Error al cargar datos'
  } finally {
    cargando.value = false
  }
}

function seleccionar(cat) {
  if (cat.tipo === 'link') {
    router.push(cat.ruta)
    return
  }
  if (catalogoActivo.value?.key === cat.key) return
  catalogoActivo.value = cat
  items.value = []
  busqueda.value = ''
  filtroCategoria.value = ''
  filtroCategoriasOpts.value = []
  if (cat.filtroPorCategoria) {
    graphqlClient.request(cat.filtroPorCategoria.optionsQuery)
      .then(data => { filtroCategoriasOpts.value = data[cat.filtroPorCategoria.optionsQueryName] ?? [] })
      .catch(() => {})
  }
  cargarDatos()
}

function inicializarFormulario() {
  const f = {}
  catalogoActivo.value?.campos.forEach(c => {
    if (c.type === 'checkbox') f[c.name] = c.default ?? false
    else if (c.type === 'number') f[c.name] = c.default ?? 0
    else if (c.type === 'color') f[c.name] = c.default ?? '#6B7280'
    else f[c.name] = c.default ?? ''
  })
  return f
}

function initInlineCreate() {
  const open = {}, vals = {}, loading = {}
  catalogoActivo.value?.campos.forEach(c => {
    if (c.type === 'select') {
      open[c.name] = false
      vals[c.name] = { nombre: '' }
      loading[c.name] = false
    }
  })
  inlineCreateOpen.value = open
  inlineCreateValue.value = vals
  inlineCreateLoading.value = loading
}

async function cargarSelectOptions() {
  for (const campo of catalogoActivo.value?.campos ?? []) {
    if (campo.type !== 'select') continue
    if (campo.optionsStatic) {
      selectOptions.value[campo.name] = campo.optionsStatic
    } else if (campo.optionsQuery) {
      try {
        const data = await graphqlClient.request(campo.optionsQuery)
        selectOptions.value[campo.name] = data[campo.optionsQueryName] ?? []
      } catch {
        selectOptions.value[campo.name] = []
      }
    }
  }
}

async function crearInline(campo) {
  const nombre = inlineCreateValue.value[campo.name]?.nombre?.trim()
  if (!nombre) return
  inlineCreateLoading.value[campo.name] = true
  try {
    const result = await graphqlClient.request(campo.createMutation, {
      data: { nombre, activo: true },
    })
    const created = result[Object.keys(result)[0]]
    selectOptions.value[campo.name] = [...(selectOptions.value[campo.name] ?? []), created]
    formulario.value[campo.name] = created[campo.optionValue ?? 'id']
    inlineCreateOpen.value[campo.name] = false
    inlineCreateValue.value[campo.name] = { nombre: '' }
  } catch {
    // silencioso
  } finally {
    inlineCreateLoading.value[campo.name] = false
  }
}

async function abrirCrear() {
  itemEditando.value = null
  formulario.value = inicializarFormulario()
  errorGuardado.value = ''
  initInlineCreate()
  drawerAbierto.value = true
  await cargarSelectOptions()
}

async function abrirEditar(item) {
  itemEditando.value = item
  formulario.value = { ...item }
  errorGuardado.value = ''
  initInlineCreate()
  drawerAbierto.value = true
  await cargarSelectOptions()
}

function cerrarDrawer() {
  drawerAbierto.value = false
  itemEditando.value = null
}

async function guardar(forzar = false) {
  if (!catalogoActivo.value) return

  // Validación: solo un estado inicial por catálogo
  if (formulario.value.esInicial === true && !forzar) {
    const otro = items.value.find(i =>
      i.esInicial === true && i.id !== itemEditando.value?.id
    )
    if (otro) {
      inicialConflicto.value = otro
      modalConfirmInicial.value = true
      return
    }
  }

  errorGuardado.value = ''
  guardando.value = true
  try {
    const data = {}
    catalogoActivo.value.campos.forEach(c => {
      if (formulario.value[c.name] !== undefined && formulario.value[c.name] !== '') {
        data[c.name] = formulario.value[c.name]
      }
    })
    catalogoActivo.value.beforeSave?.(data)
    const mut = catalogoActivo.value.mutations
    if (itemEditando.value) {
      data.id = itemEditando.value.id
      await graphqlClient.request(mut.update, { data })
    } else {
      await graphqlClient.request(mut.create, { data })
    }
    cerrarDrawer()
    await cargarDatos()
  } catch (e) {
    errorGuardado.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

async function confirmarCambioInicial() {
  const mut = catalogoActivo.value?.mutations?.update
  if (!mut || !inicialConflicto.value) return
  guardando.value = true
  try {
    // Desactivar el estado inicial anterior
    await graphqlClient.request(mut, { data: { id: inicialConflicto.value.id, esInicial: false } })
    modalConfirmInicial.value = false
    inicialConflicto.value = null
    // Guardar el nuevo con forzar=true para evitar el bucle de validación
    await guardar(true)
  } catch (e) {
    errorGuardado.value = e?.response?.errors?.[0]?.message ?? 'Error al actualizar estado inicial'
    modalConfirmInicial.value = false
  } finally {
    guardando.value = false
  }
}

async function toggleActivo(item) {
  if (toggling.value) return
  toggling.value = item.id
  const mut = catalogoActivo.value?.mutations?.update
  if (!mut) return
  try {
    await graphqlClient.request(mut, { data: { id: item.id, activo: !item.activo } })
    item.activo = !item.activo
  } catch (e) {
    // silencioso — el toggle vuelve al estado original visualmente
  } finally {
    toggling.value = null
  }
}

function confirmarEliminar(item) {
  itemAEliminar.value = item
  errorEliminar.value = ''
  modalEliminar.value = true
}

async function eliminar() {
  if (!catalogoActivo.value || !itemAEliminar.value) return
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await graphqlClient.request(catalogoActivo.value.mutations.delete, {
      filter: { id: { eq: itemAEliminar.value.id } },
    })
    modalEliminar.value = false
    itemAEliminar.value = null
    await cargarDatos()
  } catch (e) {
    const msg = e?.response?.errors?.[0]?.message ?? ''
    if (msg.includes('ForeignKey') || msg.includes('foránea') || msg.includes('foreign key')) {
      errorEliminar.value = `"${itemAEliminar.value?.nombre}" está en uso y no puede eliminarse. Desactívalo en su lugar.`
    } else {
      errorEliminar.value = msg || 'Error al eliminar'
    }
  } finally {
    eliminando.value = false
  }
}
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.15s ease;
}
.drawer-enter-active .relative,
.drawer-leave-active .relative {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .relative,
.drawer-leave-to .relative {
  opacity: 0;
  transform: scale(0.96) translateY(-8px);
}
</style>
