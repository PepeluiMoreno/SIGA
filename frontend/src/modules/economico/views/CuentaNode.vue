<template>
  <div>
    <!-- Fila de la cuenta -->
    <div
      class="flex items-center gap-2 px-2 py-1.5 hover:bg-purple-50/60 group"
      :class="{ 'bg-amber-50/40': matchesSearch }"
      :style="{ paddingLeft: (12 + (cuenta.nivel - 1) * 20) + 'px' }"
    >
      <!-- Caret expandir/colapsar -->
      <button
        v-if="cuenta.hijos && cuenta.hijos.length"
        @click="toggleNodo(cuenta.id)"
        class="w-4 h-4 flex items-center justify-center text-gray-400 hover:text-purple-600"
        :title="expanded ? 'Colapsar' : 'Expandir'"
      >
        <span v-if="expanded">▼</span>
        <span v-else>▶</span>
      </button>
      <span v-else class="w-4 h-4 inline-block" />

      <!-- Código -->
      <span
        class="font-mono text-xs text-gray-600 w-16 shrink-0"
        :class="{ 'font-bold text-gray-800': cuenta.nivel === 1 }"
      >{{ cuenta.codigo }}</span>

      <!-- Nombre -->
      <span
        class="text-sm flex-1 truncate"
        :class="cuenta.nivel === 1 ? 'font-semibold text-gray-900' : 'text-gray-700'"
      >
        <span v-html="resaltado" />
        <span v-if="!cuenta.activa" class="ml-2 text-[10px] uppercase text-gray-400">(inactiva)</span>
        <span v-if="cuenta.esDotacion" class="ml-2 text-[10px] uppercase text-amber-700 bg-amber-50 border border-amber-200 rounded px-1">dotación</span>
      </span>

      <!-- Tipo -->
      <span class="text-[10px] uppercase tracking-wide rounded px-1.5 py-0.5 shrink-0" :class="badgeTipo(cuenta.tipo)">
        {{ cuenta.tipo }}
      </span>

      <!-- Saldo (solo hojas con saldo) -->
      <span
        v-if="cuenta.permiteAsiento && saldoFormateado"
        class="font-mono text-xs w-28 text-right shrink-0"
        :class="saldoColor"
      >{{ saldoFormateado }}</span>
      <span v-else class="w-28 shrink-0" />

      <!-- Acciones -->
      <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        <button
          v-if="cuenta.nivel < 3"
          @click="$emit('add-sub', cuenta)"
          class="p-1.5 rounded-md text-gray-400 hover:text-green-600 hover:bg-green-50 transition-colors"
          title="Añadir subcuenta"
        >
          <PlusCircleIcon class="w-4 h-4" />
        </button>
        <button
          @click="$emit('editar', cuenta)"
          class="p-1.5 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
          title="Editar"
        >
          <PencilIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Hijos (recursivo) -->
    <div v-if="cuenta.hijos && cuenta.hijos.length && expanded" class="border-l border-gray-100">
      <CuentaNode
        v-for="hijo in cuenta.hijos"
        :key="hijo.id"
        :cuenta="hijo"
        :saldos="saldos"
        :busqueda="busqueda"
        @add-sub="(c) => $emit('add-sub', c)"
        @editar="(c) => $emit('editar', c)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { PlusCircleIcon, PencilIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  cuenta:   { type: Object, required: true },
  saldos:   { type: Object, default: () => ({}) },
  busqueda: { type: String, default: '' },
})

defineEmits(['add-sub', 'editar'])

// Objeto reactivo y función inyectados desde Contabilidad.vue
const expandedMap = inject('expandedMap')
const toggleNodo  = inject('toggleNodo')

const expanded = computed(() => !!expandedMap[props.cuenta.id])

const matchesSearch = computed(() => {
  if (!props.busqueda) return false
  const q = props.busqueda.toLowerCase()
  return (
    String(props.cuenta.codigo).toLowerCase().includes(q) ||
    (props.cuenta.nombre || '').toLowerCase().includes(q)
  )
})

const resaltado = computed(() => {
  if (!props.busqueda) return escapeHtml(props.cuenta.nombre || '')
  const nombre = props.cuenta.nombre || ''
  const safe = escapeHtml(nombre)
  const q = props.busqueda.toLowerCase()
  const idx = nombre.toLowerCase().indexOf(q)
  if (idx === -1) return safe
  const before = escapeHtml(nombre.slice(0, idx))
  const match = escapeHtml(nombre.slice(idx, idx + props.busqueda.length))
  const after = escapeHtml(nombre.slice(idx + props.busqueda.length))
  return `${before}<mark class="bg-yellow-200 rounded">${match}</mark>${after}`
})

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

const saldo = computed(() => props.saldos[props.cuenta.codigo])
const saldoFormateado = computed(() => {
  const s = saldo.value
  if (s === undefined || s === null || Math.abs(s) < 0.005) return ''
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(s)
})
const saldoColor = computed(() => {
  const s = saldo.value || 0
  return s >= 0 ? 'text-gray-700' : 'text-red-600'
})

function badgeTipo(tipo) {
  return ({
    ACTIVO:     'bg-blue-100 text-blue-700',
    PASIVO:     'bg-red-100 text-red-700',
    PATRIMONIO: 'bg-purple-100 text-purple-700',
    INGRESO:    'bg-green-100 text-green-700',
    GASTO:      'bg-orange-100 text-orange-700',
  })[tipo] || 'bg-gray-100 text-gray-600'
}
</script>
