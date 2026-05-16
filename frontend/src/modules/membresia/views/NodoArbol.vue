<template>
  <div :class="profundidad > 0 ? 'ml-8 border-l-2 border-gray-100 pl-4' : ''">

    <!-- ── Nodo raíz ──────────────────────────────────────────────────────── -->
    <div v-if="!nodo.agrupacionPadreId"
      class="flex items-center gap-4 px-5 py-4 rounded-xl bg-indigo-700 text-white mb-3 shadow-md group">
      <div class="flex-shrink-0 w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
        <BuildingOffice2Icon class="w-7 h-7 text-white" />
      </div>
      <div class="flex-1 min-w-0 flex items-center gap-x-4 gap-y-1 flex-wrap">
        <span class="font-bold text-base leading-tight">{{ nodo.nombre }}</span>
        <span v-if="nodo.tipoUnidad" class="text-xs text-indigo-200 font-medium">{{ nodo.tipoUnidad.nombre }}</span>
        <div v-if="nodo.email" class="flex items-center gap-1 text-xs text-indigo-100">
          <EnvelopeIcon class="w-3.5 h-3.5 shrink-0" /><span>{{ nodo.email }}</span>
        </div>
        <div v-if="nodo.telefono" class="flex items-center gap-1 text-xs text-indigo-100">
          <PhoneIcon class="w-3.5 h-3.5 shrink-0" /><span>{{ nodo.telefono }}</span>
        </div>
        <div v-if="conteo" class="flex items-center gap-1 text-xs text-indigo-100">
          <UserGroupIcon class="w-3.5 h-3.5 shrink-0" /><span>{{ conteo.militantes }} militantes</span>
        </div>
        <div v-if="conteo?.voluntarios" class="flex items-center gap-1 text-xs text-rose-300">
          <HeartIcon class="w-3.5 h-3.5 shrink-0" /><span>{{ conteo.voluntarios }} voluntarios</span>
        </div>
      </div>
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
        <router-link :to="`/agrupaciones/${nodo.id}`" title="Ver detalle"
          class="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
          <EyeIcon class="w-4 h-4 text-white" />
        </router-link>
        <button @click="$emit('editar', nodo)" title="Editar"
          class="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
          <PencilIcon class="w-4 h-4 text-white" />
        </button>
        <button @click="!esNivelMasBajo && $emit('anadir-hijo', nodo)"
          :title="esNivelMasBajo ? 'Nivel más bajo: no se pueden añadir sub-unidades' : 'Añadir sub-unidad'"
          :class="esNivelMasBajo ? 'p-1.5 rounded-lg bg-white/5 opacity-40 cursor-not-allowed' : 'p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors'">
          <PlusCircleIcon class="w-4 h-4 text-white" />
        </button>
      </div>
    </div>

    <!-- ── Fila de rama ───────────────────────────────────────────────────── -->
    <div v-else
      class="flex items-center gap-3 px-4 py-2.5 rounded-lg border border-gray-100 bg-white hover:shadow-sm transition-shadow group mb-1.5">

      <!-- Avatar coordinador (solo si hay coordinador asignado) -->
      <div v-if="coordinador" class="flex-shrink-0">
        <img v-if="coordinador.fotoUrl" :src="coordinador.fotoUrl" :alt="nombreCoordinador"
          class="h-9 w-9 rounded-full object-cover ring-1 ring-gray-200" />
        <div v-else class="h-9 w-9 rounded-full flex items-center justify-center text-sm font-bold ring-1 ring-gray-100"
          :class="natConfig.bg + ' ' + natConfig.text">
          {{ inicialesCoordinador }}
        </div>
      </div>

      <!-- Todo el contenido en una sola fila -->
      <div class="flex-1 min-w-0 flex items-center gap-x-3 gap-y-0.5 flex-wrap">

        <!-- Nombre + nombre corto + tipo -->
        <span class="font-semibold text-gray-900 text-sm leading-tight">{{ nodo.nombre }}</span>
        <span v-if="nodo.nombreCorto && nodo.nombreCorto !== nodo.nombre"
          class="text-xs text-gray-400">({{ nodo.nombreCorto }})</span>
        <span v-if="nodo.tipoUnidad"
          class="text-xs px-1.5 py-0.5 rounded font-medium"
          :class="natConfig.badge">
          {{ nodo.tipoUnidad.nombre }}
        </span>

        <!-- Separador visual -->
        <span class="text-gray-300 select-none">·</span>

        <!-- Nombre del coordinador -->
        <span v-if="coordinador" class="text-sm text-gray-600">{{ nombreCoordinador }}</span>
        <span v-else class="text-xs text-gray-400 italic">Sin responsable</span>

        <!-- Contacto -->
        <div v-if="nodo.email" class="flex items-center gap-1 text-xs text-gray-500">
          <EnvelopeIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" /><span>{{ nodo.email }}</span>
        </div>
        <div v-if="nodo.telefono" class="flex items-center gap-1 text-xs text-gray-500">
          <PhoneIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" /><span>{{ nodo.telefono }}</span>
        </div>

        <!-- Conteos -->
        <div v-if="conteo" class="flex items-center gap-1 text-xs text-gray-500">
          <UserGroupIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" /><span>{{ conteo.militantes }}</span>
        </div>
        <div v-if="conteo?.voluntarios" class="flex items-center gap-1 text-xs text-rose-500">
          <HeartIcon class="w-3.5 h-3.5 text-rose-400 shrink-0" /><span>{{ conteo.voluntarios }}</span>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
        <router-link :to="`/agrupaciones/${nodo.id}`" title="Ver detalle"
          class="p-1.5 rounded-md text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
          <EyeIcon class="w-4 h-4" />
        </router-link>
        <button @click="$emit('editar', nodo)" title="Editar"
          class="p-1.5 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
          <PencilIcon class="w-4 h-4" />
        </button>
        <button
          @click="!esNivelMasBajo && $emit('anadir-hijo', nodo)"
          :title="esNivelMasBajo ? 'Nivel más bajo: no se pueden añadir sub-unidades' : 'Añadir sub-unidad'"
          :class="esNivelMasBajo ? 'p-1.5 rounded-md text-gray-200 cursor-not-allowed' : 'p-1.5 rounded-md text-gray-400 hover:text-green-600 hover:bg-green-50 transition-colors'">
          <PlusCircleIcon class="w-4 h-4" />
        </button>
        <button
          @click="nodo.hijos?.length ? null : $emit('eliminar', nodo)"
          :title="nodo.hijos?.length ? 'No se puede archivar: tiene sub-unidades' : 'Archivar'"
          :class="nodo.hijos?.length ? 'p-1.5 rounded-md text-gray-200 cursor-not-allowed' : 'p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors'">
          <TrashIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Hijos recursivos -->
    <NodoArbol
      v-for="hijo in nodo.hijos"
      :key="hijo.id"
      :nodo="hijo"
      :tipos="tipos"
      :profundidad="profundidad + 1"
      :coordinador-map="coordinadorMap"
      :conteo-map="conteoMap"
      @editar="$emit('editar', $event)"
      @eliminar="$emit('eliminar', $event)"
      @anadir-hijo="$emit('anadir-hijo', $event)"
    />

  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  BuildingOffice2Icon,
  MapPinIcon, WrenchScrewdriverIcon, GlobeAltIcon, BuildingOfficeIcon, Squares2X2Icon,
  PencilIcon, PlusCircleIcon, TrashIcon, EyeIcon,
  EnvelopeIcon, PhoneIcon, UserGroupIcon, HeartIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  nodo:           { type: Object, required: true },
  tipos:          { type: Array, default: () => [] },
  profundidad:    { type: Number, default: 0 },
  coordinadorMap: { type: Object, default: () => ({}) },
  conteoMap:      { type: Object, default: () => ({}) },
})

defineEmits(['editar', 'eliminar', 'anadir-hijo'])

const NAT = {
  TERRITORIAL:    { icon: MapPinIcon,            bg: 'bg-blue-100',   text: 'text-blue-700',   badge: 'bg-blue-50 text-blue-700'     },
  FUNCIONAL:      { icon: WrenchScrewdriverIcon, bg: 'bg-green-100',  text: 'text-green-700',  badge: 'bg-green-50 text-green-700'   },
  PROGRAMATICA:   { icon: GlobeAltIcon,          bg: 'bg-purple-100', text: 'text-purple-700', badge: 'bg-purple-50 text-purple-700' },
  ADMINISTRATIVA: { icon: BuildingOfficeIcon,    bg: 'bg-gray-100',   text: 'text-gray-700',   badge: 'bg-gray-100 text-gray-700'    },
}
const DEFAULT_NAT = { icon: Squares2X2Icon, bg: 'bg-slate-100', text: 'text-slate-600', badge: 'bg-slate-50 text-slate-600' }

const natConfig = computed(() => NAT[props.nodo.tipoUnidad?.naturaleza] ?? DEFAULT_NAT)
const coordinador = computed(() => props.coordinadorMap[props.nodo.id] ?? null)
const conteo = computed(() => props.conteoMap[props.nodo.id] ?? null)
const esNivelMasBajo = computed(() =>
  !!props.nodo.tipoId && !props.tipos.some(t => t.padreTipoId === props.nodo.tipoId)
)

const nombreCoordinador = computed(() => {
  const c = coordinador.value
  if (!c) return ''
  return [c.nombre, c.apellido1].filter(Boolean).join(' ')
})

const inicialesCoordinador = computed(() => {
  const c = coordinador.value
  if (!c) return props.nodo.nombre?.[0]?.toUpperCase() ?? '?'
  const initials = `${c.nombre?.[0] ?? ''}${c.apellido1?.[0] ?? ''}`.toUpperCase()
  return initials || (props.nodo.nombre?.[0]?.toUpperCase() ?? '?')
})
</script>
