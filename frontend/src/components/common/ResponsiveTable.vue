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
              :class="[alignClass(col.align), col.ordenable ? 'cursor-pointer select-none hover:text-slate-900' : '']"
              :style="col.width ? { width: col.width } : null"
              :aria-sort="col.ordenable ? ariaSort(col.key) : null"
              @click="col.ordenable && ordenarPor(col.key)"
            >
              <span class="inline-flex items-center gap-1">
                {{ etiquetaColumna(col) }}
                <span v-if="col.ordenable" class="text-[10px] leading-none"
                  :class="orden.key === col.key ? 'text-slate-700' : 'text-slate-300'">
                  {{ orden.key === col.key && orden.dir === 'desc' ? '▼' : '▲' }}
                </span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="(fila, i) in filasPagina"
            :key="rowKey(fila, i)"
            class="hover:bg-slate-50 transition-colors"
            :class="rowClass ? rowClass(fila) : ''"
            @click="$emit('row-click', fila)"
          >
            <!-- El texto largo se corta con elipsis en vez de ensanchar la tabla
                 (que forzaría scroll horizontal); el valor íntegro queda en el
                 `title`. `truncate` necesita una anchura acotada: de ahí el
                 `max-width`, que una columna puede ajustar con `anchoMax`. -->
            <td
              v-for="col in columnas"
              :key="col.key"
              class="px-3 py-2 truncate"
              :class="[alignClass(col.align), col.cellClass]"
              :style="estiloCelda(col)"
              :title="tituloCelda(fila, col)"
            >
              <!-- Slot personalizado por columna, o valor plano -->
              <slot :name="`cell-${col.key}`" :fila="fila" :valor="valor(fila, col.key)">
                {{ formatear(fila, col) }}
              </slot>
            </td>
          </tr>
          <tr v-if="!filasPagina.length">
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
        v-for="(fila, i) in filasPagina"
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

      <div v-if="!filasPagina.length" class="text-center text-slate-400 text-sm py-8">
        {{ vacioTexto }}
      </div>
    </div>

    <!-- ░░ PAGINACIÓN ░░ -->
    <!-- Solo aparece si hay más filas que las que caben en una página: una lista
         corta no debe cargarse con controles que no hacen nada. -->
    <nav
      v-if="totalPaginas > 1"
      class="flex items-center justify-between gap-4 pt-3 mt-3 border-t border-slate-100"
      aria-label="Paginación"
    >
      <p class="text-xs text-slate-500">
        {{ desde }}–{{ hasta }} de {{ totalFilas }}
      </p>

      <div class="flex items-center gap-1">
        <button type="button" class="pag-btn" :disabled="pagina === 1"
          aria-label="Página anterior" @click="irA(pagina - 1)">
          ‹
        </button>

        <button
          v-for="(p, i) in paginasVisibles"
          :key="`${p}-${i}`"
          type="button"
          class="pag-btn"
          :class="p === pagina ? 'bg-indigo-600 text-white border-indigo-600 hover:bg-indigo-600' : ''"
          :disabled="p === '…'"
          :aria-current="p === pagina ? 'page' : null"
          @click="p !== '…' && irA(p)"
        >
          {{ p }}
        </button>

        <button type="button" class="pag-btn" :disabled="pagina === totalPaginas"
          aria-label="Página siguiente" @click="irA(pagina + 1)">
          ›
        </button>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch, useSlots } from 'vue'

const props = defineProps({
  /**
   * Columnas: [{ key, label, align?, width?, cellClass?, formato?, oculta?, esAcciones? }]
   *  - align: 'left' | 'center' | 'right'
   *  - formato: fn(valor, fila) => string  (opcional)
   *  - esAcciones: true marca la columna de botones (en móvil va en la cabecera de tarjeta)
   *  - ocultaEnMovil: true → no se muestra en la vista de tarjetas
   *  - ordenable: true → la cabecera ordena por esta columna al pulsarla
   *  - valorOrden: fn(fila) => any  (clave de ordenación alternativa a `key`)
   *  - anchoMax: string CSS → tope de anchura de la celda antes de truncar
   *              (por defecto `anchoMaxCelda`; `'none'` deja crecer la columna)
   */
  columnas:   { type: Array, required: true },
  filas:      { type: Array, default: () => [] },
  /** key única por fila, o función fn(fila) => string */
  claveFila:  { type: [String, Function], default: 'id' },
  rowClass:   { type: Function, default: null },
  vacioTexto: { type: String, default: 'No hay registros' },
  /** Columna por la que ordenar al montar: { key, dir: 'asc' | 'desc' } */
  ordenInicial: { type: Object, default: null },
  /** Filas por página. `0` desactiva la paginación (se muestran todas). */
  porPagina:  { type: Number, default: 25 },
  /** Tope de anchura por defecto de una celda antes de truncar (CSS). Cada
   *  columna lo ajusta con `anchoMax`; `'none'` la deja crecer. */
  anchoMaxCelda: { type: String, default: '18rem' },
})

defineEmits(['row-click'])

// ── Ordenación por columna (opt-in vía `ordenable`) ──────────────────────────
// Sin columna activa, `filasOrdenadas` es `filas` intacto: las vistas que no
// declaran columnas ordenables conservan el orden que ellas mismas imponen.
const orden = reactive({
  key: props.ordenInicial?.key ?? null,
  dir: props.ordenInicial?.dir ?? 'asc',
})

function ordenarPor(key) {
  if (orden.key === key) orden.dir = orden.dir === 'asc' ? 'desc' : 'asc'
  else { orden.key = key; orden.dir = 'asc' }
}

function ariaSort(key) {
  if (orden.key !== key) return 'none'
  return orden.dir === 'asc' ? 'ascending' : 'descending'
}

function claveOrden(fila, col) {
  return col?.valorOrden ? col.valorOrden(fila) : valor(fila, col.key)
}

function comparar(a, b) {
  // Los nulos van siempre al final, sea cual sea la dirección.
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  if (typeof a === 'boolean' && typeof b === 'boolean') return (a === b) ? 0 : (a ? -1 : 1)
  return String(a).localeCompare(String(b), 'es', { numeric: true, sensitivity: 'base' })
}

const filasOrdenadas = computed(() => {
  if (!orden.key) return props.filas
  const col = props.columnas.find(c => c.key === orden.key)
  if (!col) return props.filas
  const signo = orden.dir === 'desc' ? -1 : 1
  return [...props.filas].sort((x, y) => signo * comparar(claveOrden(x, col), claveOrden(y, col)))
})

// ── Paginación en cliente ────────────────────────────────────────────────────
// Las queries de strawchemy no aceptan `limit`/`offset`: la vista trae el
// conjunto entero y aquí se corta. `porPagina: 0` la desactiva.
const pagina = ref(1)

const totalFilas   = computed(() => filasOrdenadas.value.length)
const totalPaginas = computed(() =>
  props.porPagina > 0 ? Math.max(1, Math.ceil(totalFilas.value / props.porPagina)) : 1
)

// Al filtrar, la página actual puede quedar fuera de rango (p. ej. estabas en la
// 7 y el filtro deja 2). Recolocamos en la última válida en vez de mostrar vacío.
watch(totalPaginas, (n) => { if (pagina.value > n) pagina.value = n })
// Un cambio de orden reordena el conjunto entero: volver a la primera página es
// lo esperable, si no la fila que buscabas «salta» a otra página.
watch(() => [orden.key, orden.dir], () => { pagina.value = 1 })

const filasPagina = computed(() => {
  if (props.porPagina <= 0) return filasOrdenadas.value
  const ini = (pagina.value - 1) * props.porPagina
  return filasOrdenadas.value.slice(ini, ini + props.porPagina)
})

const desde = computed(() => (totalFilas.value ? (pagina.value - 1) * props.porPagina + 1 : 0))
const hasta = computed(() => Math.min(pagina.value * props.porPagina, totalFilas.value))

function irA(p) {
  pagina.value = Math.min(Math.max(1, p), totalPaginas.value)
}

// Ventana de páginas: primera, última, la actual y sus vecinas; el hueco se
// colapsa en «…». Evita pintar 200 botones en una lista larga.
const paginasVisibles = computed(() => {
  const total = totalPaginas.value
  const act = pagina.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const nums = new Set([1, total, act, act - 1, act + 1])
  const ordenadas = [...nums].filter(n => n >= 1 && n <= total).sort((a, b) => a - b)

  const salida = []
  let previa = 0
  for (const n of ordenadas) {
    if (previa && n - previa > 1) salida.push('…')
    salida.push(n)
    previa = n
  }
  return salida
})

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

// Tooltip con el valor completo, porque la celda lo trunca. Solo para celdas de
// texto plano: si la vista pinta la celda con un slot (badges, botones), el
// título sería ruido y lo pone ella si lo necesita.
const slots = useSlots()
function tituloCelda(fila, col) {
  if (col.esAcciones || slots[`cell-${col.key}`]) return null
  const t = formatear(fila, col)
  return typeof t === 'string' && t !== '—' ? t : null
}

function rowKey(fila, i) {
  if (typeof props.claveFila === 'function') return props.claveFila(fila)
  return valor(fila, props.claveFila) ?? i
}

function alignClass(align) {
  return { left: 'text-left', center: 'text-center', right: 'text-right' }[align] ?? 'text-left'
}

// La columna de acciones lleva «Acciones» por defecto, para que ninguna tabla
// tenga una cabecera en blanco. La vista puede sobreescribirlo con su `label`.
function etiquetaColumna(col) {
  if (col.label) return col.label
  return col.esAcciones ? 'Acciones' : ''
}

// Tope de anchura que hace efectivo el `truncate`. La columna de acciones no se
// trunca (lleva botones); una columna puede fijar el suyo con `anchoMax` o
// desactivarlo con `'none'`. `width` explícito manda sobre el tope.
function estiloCelda(col) {
  if (col.esAcciones) return null
  const s = {}
  if (col.width) s.width = col.width
  const max = col.anchoMax ?? props.anchoMaxCelda
  if (max && max !== 'none') s.maxWidth = max
  return s
}
</script>

<style scoped>
.pag-btn {
  @apply min-w-[1.75rem] h-7 px-1.5 inline-flex items-center justify-center rounded-md border
         border-slate-200 bg-white text-xs font-medium text-slate-600 transition-colors
         hover:bg-slate-50 hover:text-slate-900
         disabled:opacity-40 disabled:cursor-default disabled:hover:bg-white;
}
</style>
