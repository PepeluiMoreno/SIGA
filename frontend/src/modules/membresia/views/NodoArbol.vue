<template>
  <div>
    <!-- Fila del nodo (mismo patrón para raíz y ramas) -->
    <div
      class="flex items-center gap-2 px-2 py-2 hover:bg-indigo-50/60 group border-b border-gray-50 last:border-b-0"
      :style="{ paddingLeft: (8 + profundidad * 20) + 'px' }"
    >
      <!-- Caret expandir/colapsar -->
      <button
        v-if="nodo.hijos && nodo.hijos.length"
        @click="toggleNodo(nodo.id)"
        class="w-4 h-4 flex items-center justify-center text-gray-400 hover:text-indigo-600 shrink-0"
        :title="expanded ? 'Colapsar' : 'Expandir'"
      >
        <span v-if="expanded">▼</span>
        <span v-else>▶</span>
      </button>
      <span v-else class="w-4 h-4 inline-block shrink-0" />

      <!-- Avatar coordinador (o icono de unidad si no hay) -->
      <div class="flex-shrink-0">
        <img v-if="coordinador?.fotoUrl" :src="coordinador.fotoUrl" :alt="nombreCoordinador"
          class="h-8 w-8 rounded-full object-cover ring-1 ring-gray-200" />
        <div v-else-if="coordinador" class="h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ring-1 ring-gray-100"
          :class="natConfig.bg + ' ' + natConfig.text">
          {{ inicialesCoordinador }}
        </div>
        <div v-else class="h-8 w-8 rounded-full flex items-center justify-center ring-1 ring-gray-100"
          :class="natConfig.bg + ' ' + natConfig.text">
          <component :is="natConfig.icon" class="w-4 h-4" />
        </div>
      </div>

      <!-- Contenido en una sola fila -->
      <div class="flex-1 min-w-0 flex items-center gap-x-3 gap-y-0.5 flex-wrap">
        <span class="font-semibold text-gray-900 text-sm leading-tight">{{ nodo.nombre }}</span>
        <span v-if="nodo.nombreCorto && nodo.nombreCorto !== nodo.nombre"
          class="text-xs text-gray-400">({{ nodo.nombreCorto }})</span>
        <span v-if="nodo.tipoUnidad"
          class="text-xs px-1.5 py-0.5 rounded font-medium"
          :class="natConfig.badge">
          {{ nodo.tipoUnidad.nombre }}
        </span>

        <span class="text-gray-300 select-none">·</span>

        <span v-if="coordinador" class="text-sm text-gray-600">{{ nombreCoordinador }}</span>
        <span v-else class="text-xs text-gray-400 italic">Sin responsable</span>

        <div v-if="nodo.email" class="flex items-center gap-1 text-xs text-gray-500">
          <EnvelopeIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" /><span>{{ nodo.email }}</span>
        </div>
        <div v-if="nodo.telefono" class="flex items-center gap-1 text-xs text-gray-500">
          <PhoneIcon class="w-3.5 h-3.5 text-gray-400 shrink-0" /><span>{{ nodo.telefono }}</span>
        </div>

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

    <!-- Hijos recursivos (solo si expandido) -->
    <div v-if="nodo.hijos && nodo.hijos.length && expanded">
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
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import {
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
  PROGRAMATICA:   { icon: GlobeAltIcon,          bg: 'bg-indigo-100', text: 'text-indigo-700', badge: 'bg-indigo-50 text-indigo-700' },
  ADMINISTRATIVA: { icon: BuildingOfficeIcon,    bg: 'bg-slate-100',  text: 'text-slate-700',  badge: 'bg-slate-100 text-slate-700'  },
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

// Expandir/colapsar: igual patrón que CuentaNode (inject desde el padre)
const expandedMap = inject('expandedMap')
const toggleNodo  = inject('toggleNodo')
const expanded = computed(() => !!expandedMap[props.nodo.id])
</script>
