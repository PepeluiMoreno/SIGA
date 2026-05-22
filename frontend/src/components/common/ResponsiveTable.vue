<template>
  <div>
    <!-- ░░ DESKTOP: tabla clásica (sm y superior) ░░ -->
    <div class="hidden sm:block overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase tracking-wide">
          <tr>
            <th
              v-for="col in columnas"
              :key="col.key"
              class="px-3 py-2 font-semibold whitespace-nowrap"
              :class="alignClass(col.align)"
              :style="col.width ? { width: col.width } : null"
            >{{ col.label }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="(fila, i) in filas"
            :key="rowKey(fila, i)"
            class="hover:bg-slate-50 transition-colors"
            :class="rowClass ? rowClass(fila) : ''"
            @click="$emit('row-click', fila)"
          >
            <td
              v-for="col in columnas"
              :key="col.key"
              class="px-3 py-2"
              :class="[alignClass(col.align), col.cellClass]"
            >
              <!-- Slot personalizado por columna, o valor plano -->
              <slot :name="`cell-${col.key}`" :fila="fila" :valor="valor(fila, col.key)">
                {{ formatear(fila, col) }}
              </slot>
            </td>
          </tr>
          <tr v-if="!filas.length">
            <td :colspan="columnas.length" class="px-3 py-8 text-center text-slate-400 text-sm">
              {{ vacioTexto }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ░░ MÓVIL: tarjetas etiqueta-valor (por debajo de sm) ░░ -->
    <div class="sm:hidden space-y-3">
      <div
        v-for="(fila, i) in filas"
        :key="rowKey(fila, i)"
        class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
        :class="rowClass ? rowClass(fila) : ''"
        @click="$emit('row-click', fila)"
      >
        <!-- Cabecera de la tarjeta = primera columna destacada -->
        <div class="px-4 py-2.5 bg-slate-50 border-b border-slate-100 flex items-center justify-between gap-2">
          <div class="font-medium text-slate-800 text-sm min-w-0 truncate">
            <slot :name="`cell-${columnas[0].key}`" :fila="fila" :valor="valor(fila, columnas[0].key)">
              {{ formatear(fila, columnas[0]) }}
            </slot>
          </div>
          <!-- Si hay columna marcada como 'acciones', va arriba a la derecha -->
          <div v-if="colAcciones" class="shrink-0" @click.stop>
            <slot :name="`cell-${colAcciones.key}`" :fila="fila" :valor="valor(fila, colAcciones.key)" />
          </div>
        </div>

        <!-- Resto de columnas como pares etiqueta : valor -->
        <dl class="px-4 py-2 divide-y divide-slate-50">
          <div
            v-for="col in columnasResto"
            :key="col.key"
            class="flex items-start justify-between gap-3 py-1.5"
          >
            <dt class="text-xs text-slate-500 shrink-0 pt-0.5">{{ col.label }}</dt>
            <dd class="text-sm text-slate-800 text-right min-w-0">
              <slot :name="`cell-${col.key}`" :fila="fila" :valor="valor(fila, col.key)">
                {{ formatear(fila, col) }}
              </slot>
            </dd>
          </div>
        </dl>
      </div>

      <div v-if="!filas.length" class="text-center text-slate-400 text-sm py-8">
        {{ vacioTexto }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /**
   * Columnas: [{ key, label, align?, width?, cellClass?, formato?, oculta?, esAcciones? }]
   *  - align: 'left' | 'center' | 'right'
   *  - formato: fn(valor, fila) => string  (opcional)
   *  - esAcciones: true marca la columna de botones (en móvil va en la cabecera de tarjeta)
   *  - ocultaEnMovil: true → no se muestra en la vista de tarjetas
   */
  columnas:   { type: Array, required: true },
  filas:      { type: Array, default: () => [] },
  /** key única por fila, o función fn(fila) => string */
  claveFila:  { type: [String, Function], default: 'id' },
  rowClass:   { type: Function, default: null },
  vacioTexto: { type: String, default: 'No hay registros' },
})

defineEmits(['row-click'])

const colAcciones = computed(() => props.columnas.find(c => c.esAcciones) ?? null)

// Resto de columnas en móvil: todo menos la primera y la de acciones, respetando ocultaEnMovil
const columnasResto = computed(() =>
  props.columnas.filter((c, idx) =>
    idx !== 0 && !c.esAcciones && !c.ocultaEnMovil
  )
)

function valor(fila, key) {
  // Soporta keys anidadas tipo 'estado.nombre'
  return key.split('.').reduce((o, k) => (o == null ? o : o[k]), fila)
}

function formatear(fila, col) {
  const v = valor(fila, col.key)
  return col.formato ? col.formato(v, fila) : (v ?? '—')
}

function rowKey(fila, i) {
  if (typeof props.claveFila === 'function') return props.claveFila(fila)
  return valor(fila, props.claveFila) ?? i
}

function alignClass(align) {
  return { left: 'text-left', center: 'text-center', right: 'text-right' }[align] ?? 'text-left'
}
</script>
