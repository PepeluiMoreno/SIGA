<template>
  <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">

    <!-- Barra de resultados -->
    <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
      <span class="text-sm text-gray-600">
        <strong>{{ items.length }}</strong> {{ descripcion }}
      </span>
      <slot name="toolbar">
        <button v-if="mostrarLimpiar" @click="$emit('limpiar')"
          class="text-sm text-purple-600 hover:text-purple-800">
          Limpiar filtros
        </button>
      </slot>
    </div>

    <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-200">
      <tbody class="bg-white divide-y divide-gray-100">
        <template v-for="fila in filasJerarquicas"
          :key="fila.type === 'agrupacion' ? 'ag-' + fila.agrupacion.id : 'it-' + fila.item.id">

          <!-- Cabecera de agrupación -->
          <tr
            v-if="fila.type === 'agrupacion'"
            class="cursor-pointer select-none bg-purple-50 hover:bg-purple-100 border-t border-purple-100"
            @click="toggleAgrupacion(fila.agrupacion.id)">
            <td :colspan="colspan" class="py-2 pr-4"
              :style="{ paddingLeft: (fila.depth * 20 + 16) + 'px' }">
              <div class="flex items-center gap-2">
                <ChevronRightIcon class="w-3.5 h-3.5 text-purple-400 shrink-0 transition-transform" />
                <span class="text-sm font-semibold text-purple-800">{{ fila.agrupacion.nombre }}</span>
                <span class="text-xs text-purple-400 font-normal">
                  {{ fila.countTotal }} {{ fila.countTotal !== 1 ? itemsLabel : itemLabel }}
                </span>
              </div>
            </td>
          </tr>

          <!-- Cabecera de columnas: DEBAJO del nombre del grupo de primer nivel, al desplegarse -->
          <tr v-if="fila.type === 'agrupacion' && fila.depth === 0 && !fila.colapsada && $slots.columns"
            class="bg-gray-50 border-b border-gray-200">
            <slot name="columns" />
          </tr>

          <!-- Fila de item (slot) -->
          <tr v-else class="hover:bg-gray-50">
            <slot name="row" :item="fila.item" :depth="fila.depth" />
          </tr>

        </template>

        <!-- Sin agrupación -->
        <template v-if="sinAgrupacion.length > 0">
          <tr class="cursor-pointer select-none bg-purple-50 hover:bg-purple-100 border-t border-purple-100"
            @click="toggleAgrupacion('__sin__')">
            <td :colspan="colspan" class="py-2 px-4">
              <div class="flex items-center gap-2">
                <ChevronRightIcon class="w-3.5 h-3.5 text-purple-400 shrink-0 transition-transform" />
                <span class="text-sm font-semibold text-purple-800">Sin agrupación asignada</span>
                <span class="text-xs text-purple-400">{{ sinAgrupacion.length }}</span>
              </div>
            </td>
          </tr>
          <template v-if="!colapsadas.has('__sin__')">
            <tr v-if="$slots.columns" class="bg-gray-50 border-b border-gray-200">
              <slot name="columns" />
            </tr>
            <tr v-for="item in sinAgrupacion" :key="'sin-' + item.id" class="hover:bg-gray-50">
              <slot name="row" :item="item" :depth="1" />
            </tr>
          </template>
        </template>

      </tbody>
    </table></div>
  </div>
</template>

<script setup>
import { ChevronRightIcon } from '@heroicons/vue/24/outline'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  items:       { type: Array, default: () => [] },
  agrupaciones: { type: Array, default: () => [] },
  descripcion: { type: String, default: '' },
  itemLabel:   { type: String, default: 'elemento' },
  itemsLabel:  { type: String, default: 'elementos' },
  colspan:     { type: Number, default: 4 },
  mostrarLimpiar: { type: Boolean, default: true },
})
defineEmits(['limpiar'])

const colapsadas = ref(new Set())

// Inicializar todas colapsadas cuando llegan items
watch(() => props.items, (items) => {
  if (items.length > 0) {
    colapsadas.value = new Set([
      ...props.agrupaciones.map(a => a.id),
      '__sin__',
    ])
  }
}, { immediate: true })

function toggleAgrupacion(id) {
  const s = new Set(colapsadas.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  colapsadas.value = s
}

function getDescendantIds(rootId) {
  const ids = new Set()
  const queue = [rootId]
  while (queue.length) {
    const id = queue.shift()
    ids.add(id)
    props.agrupaciones.filter(a => a.agrupacionPadreId === id).forEach(a => queue.push(a.id))
  }
  return ids
}

// Items con agrupación
const itemsConAgrupacion = computed(() =>
  props.items.filter(i => i.agrupacion?.id)
)

// Items sin agrupación
const sinAgrupacion = computed(() =>
  props.items.filter(i => !i.agrupacion?.id).sort(alphaItem)
)

function alphaItem(a, b) {
  const ka = sortKey(a)
  const kb = sortKey(b)
  return ka.localeCompare(kb, 'es')
}
function sortKey(item) {
  // Soporta tanto miembro (apellido1) como usuario (email)
  return `${item.apellido1 || ''}${item.apellido2 || ''}${item.nombre || item.email || ''}`
}

// Mapa agrupacionId → items directos
const itemsPorAgrupacion = computed(() => {
  const map = {}
  itemsConAgrupacion.value.forEach(i => {
    const key = i.agrupacion.id
    if (!map[key]) map[key] = []
    map[key].push(i)
  })
  return map
})

const filasJerarquicas = computed(() => {
  const rows = []
  const mapa = itemsPorAgrupacion.value
  const alpha = (a, b) => a.nombre.localeCompare(b.nombre, 'es')

  const contarTotal = (agrupId) => {
    const ids = getDescendantIds(agrupId)
    return itemsConAgrupacion.value.filter(i => ids.has(i.agrupacion?.id)).length
  }

  const walk = (agrup, depth) => {
    const total = contarTotal(agrup.id)
    if (total === 0) return

    const colapsada = colapsadas.value.has(agrup.id)
    rows.push({ type: 'agrupacion', agrupacion: agrup, depth, countTotal: total, colapsada })

    if (!colapsada) {
      const directos = (mapa[agrup.id] || []).slice().sort(alphaItem)
      directos.forEach(item => rows.push({ type: 'item', item, depth: depth + 1 }))
      props.agrupaciones
        .filter(a => a.agrupacionPadreId === agrup.id)
        .sort(alpha)
        .forEach(hijo => walk(hijo, depth + 1))
    }
  }

  props.agrupaciones.filter(a => !a.agrupacionPadreId).sort(alpha).forEach(r => walk(r, 0))
  return rows
})
</script>
