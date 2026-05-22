<template>
  <div class="px-5 py-4">
    <!-- Subacordeón por categoría (nivel 2) -->
    <AccordionGroup>
      <AccordionPanel v-for="grupo in grupos" :key="grupo.clave"
        :title="grupo.nombre" :count="grupo.partidas.length" :default-open="false">
        <template #title>
          <div class="flex items-center justify-between w-full pr-2">
            <span class="text-sm font-medium text-slate-700">{{ grupo.nombre }}</span>
            <span class="text-xs text-gray-500">
              {{ eur(grupo.total) }}
              <span class="text-gray-400">· ejec. {{ eur(grupo.totalEjecutado) }}</span>
            </span>
          </div>
        </template>

        <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500">
            <tr>
              <th class="px-3 py-2 text-left w-full sm:w-28">Código</th>
              <th class="px-3 py-2 text-left">Nombre</th>
              <th class="px-3 py-2 text-right w-full sm:w-32">Presupuestado</th>
              <th class="px-3 py-2 text-right w-full sm:w-28">Ejecutado</th>
              <th class="px-3 py-2 text-right w-24">Desviación</th>
              <th class="px-3 py-2 text-center w-16">%</th>
              <th v-if="editable" class="px-3 py-2 text-center w-20"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="p in grupo.partidas" :key="p.id" class="hover:bg-gray-50 group">
              <td class="px-3 py-1.5 font-mono text-xs text-gray-500">{{ p.codigo }}</td>
              <!-- Nombre: editable inline -->
              <td class="px-3 py-1.5">
                <input v-if="editable" :value="p.nombre"
                  @blur="commit(p, 'nombre', $event.target.value)"
                  @keydown.enter="$event.target.blur()"
                  class="inline-edit" />
                <span v-else>{{ p.nombre }}</span>
              </td>
              <!-- Importe: editable inline -->
              <!-- Importe: editable inline (vigente). Muestra inicial si hubo modificaciones -->
              <td class="px-3 py-1.5 text-right">
                <input v-if="editable" :value="p.importePresupuestado" type="number" step="0.01"
                  @blur="commitImporte(p, $event.target.value)"
                  @keydown.enter="$event.target.blur()"
                  class="inline-edit text-right w-full sm:w-28" />
                <template v-else>
                  <span>{{ eur(p.importePresupuestado) }}</span>
                  <span v-if="p.importeModificaciones" class="block text-[10px] text-gray-400">
                    inicial {{ eur(p.importeInicial) }}
                  </span>
                </template>
              </td>
              <td class="px-3 py-1.5 text-right"
                :class="p.estaSobreejecutada ? 'text-red-600 font-medium' : 'text-gray-500'">
                {{ eur(p.importeEjecutado) }}
              </td>
              <td class="px-3 py-1.5 text-right text-xs"
                :class="desviacion(p) > 0 ? 'text-red-600' : desviacion(p) < 0 ? 'text-green-600' : 'text-gray-400'">
                {{ desviacion(p) >= 0 ? '+' : '' }}{{ eur(desviacion(p)) }}
              </td>
              <td class="px-3 py-1.5 text-center">
                <span class="text-xs px-1.5 py-0.5 rounded"
                  :class="p.estaSobreejecutada ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'">
                  {{ Math.round(p.porcentajeEjecutado || 0) }}%
                </span>
              </td>
              <td v-if="editable" class="px-3 py-1.5 text-center">
                <button @click="$emit('eliminar', p.id)"
                  class="text-xs text-red-500 opacity-0 group-hover:opacity-100 hover:underline transition-opacity">
                  Eliminar
                </button>
              </td>
            </tr>
            <!-- Fila de alta rápida inline -->
            <tr v-if="editable && grupo.clave === filaAltaCategoria" class="bg-purple-50/40">
              <td class="px-3 py-1.5">
                <input v-model="nueva.codigo" placeholder="Código" class="inline-edit font-mono text-xs" />
              </td>
              <td class="px-3 py-1.5">
                <input v-model="nueva.nombre" placeholder="Nombre de la partida" class="inline-edit"
                  @keydown.enter="confirmarAlta(grupo)" />
              </td>
              <td class="px-3 py-1.5 text-right">
                <input v-model.number="nueva.importe" type="number" step="0.01" placeholder="0,00"
                  class="inline-edit text-right w-full sm:w-28" @keydown.enter="confirmarAlta(grupo)" />
              </td>
              <td colspan="4" class="px-3 py-1.5 text-center">
                <button @click="confirmarAlta(grupo)" class="text-xs text-purple-700 font-medium hover:underline mr-2">Añadir</button>
                <button @click="filaAltaCategoria = null" class="text-xs text-gray-400 hover:underline">Cancelar</button>
              </td>
            </tr>
          </tbody>
        </table></div>

        <div v-if="editable && grupo.clave !== filaAltaCategoria" class="px-3 py-2">
          <button @click="abrirAlta(grupo)" class="text-xs text-purple-600 hover:underline">+ Añadir partida</button>
        </div>
      </AccordionPanel>
    </AccordionGroup>

    <!-- Alta en categoría "sin clasificar" cuando no hay ninguna categoría aún -->
    <div v-if="editable && !grupos.length" class="text-center py-6">
      <p class="text-sm text-gray-400 mb-2">No hay partidas de {{ tipo === 'INGRESO' ? 'ingreso' : 'gasto' }}.</p>
      <button @click="abrirAltaSinCategoria" class="text-sm text-purple-600 hover:underline">+ Añadir la primera partida</button>
      <div v-if="filaAltaCategoria === '__sin__'" class="mt-3 flex items-center justify-center gap-2">
        <input v-model="nueva.codigo" placeholder="Código" class="inline-edit font-mono text-xs w-24" />
        <input v-model="nueva.nombre" placeholder="Nombre" class="inline-edit w-full sm:w-48" />
        <input v-model.number="nueva.importe" type="number" step="0.01" placeholder="0,00" class="inline-edit text-right w-24" />
        <button @click="confirmarAltaSinCategoria" class="text-xs text-purple-700 font-medium hover:underline">Añadir</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'

const props = defineProps({
  tipo: { type: String, required: true },        // INGRESO | GASTO
  partidas: { type: Array, default: () => [] },
  categorias: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false },
})
const emit = defineEmits(['crear', 'actualizar', 'eliminar'])

const filaAltaCategoria = ref(null)
const nueva = ref({ codigo: '', nombre: '', importe: null, categoriaId: null })

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

// Desviación de una partida: ejecutado − presupuestado (positivo = se ha pasado)
const desviacion = (p) =>
  Number(p.importeEjecutado || 0) - Number(p.importePresupuestado || 0)

// Agrupar partidas por categoría
const grupos = computed(() => {
  const mapa = new Map()
  for (const p of props.partidas) {
    const clave = p.categoriaId || '__sin_categoria__'
    if (!mapa.has(clave)) {
      const cat = props.categorias.find(c => c.id === p.categoriaId)
      mapa.set(clave, { clave, nombre: cat?.nombre || 'Sin categoría', categoriaId: p.categoriaId || null, partidas: [], total: 0, totalEjecutado: 0 })
    }
    const g = mapa.get(clave)
    g.partidas.push(p)
    g.total += Number(p.importePresupuestado || 0)
    g.totalEjecutado += Number(p.importeEjecutado || 0)
  }
  return Array.from(mapa.values())
})

const commit = (partida, campo, valor) => {
  if (valor === partida[campo]) return
  emit('actualizar', { id: partida.id, [campo]: valor })
}
const commitImporte = (partida, valor) => {
  const num = parseFloat(valor)
  if (isNaN(num) || num === Number(partida.importePresupuestado)) return
  emit('actualizar', { id: partida.id, importePresupuestado: num })
}

const abrirAlta = (grupo) => {
  filaAltaCategoria.value = grupo.clave
  nueva.value = { codigo: '', nombre: '', importe: null, categoriaId: grupo.categoriaId }
}
const confirmarAlta = (grupo) => {
  if (!nueva.value.codigo || !nueva.value.nombre) return
  emit('crear', {
    codigo: nueva.value.codigo, nombre: nueva.value.nombre, tipo: props.tipo,
    importePresupuestado: Number(nueva.value.importe || 0), categoriaId: grupo.categoriaId,
  })
  filaAltaCategoria.value = null
  nueva.value = { codigo: '', nombre: '', importe: null, categoriaId: null }
}

const abrirAltaSinCategoria = () => {
  filaAltaCategoria.value = '__sin__'
  nueva.value = { codigo: '', nombre: '', importe: null, categoriaId: null }
}
const confirmarAltaSinCategoria = () => {
  if (!nueva.value.codigo || !nueva.value.nombre) return
  emit('crear', {
    codigo: nueva.value.codigo, nombre: nueva.value.nombre, tipo: props.tipo,
    importePresupuestado: Number(nueva.value.importe || 0), categoriaId: null,
  })
  filaAltaCategoria.value = null
  nueva.value = { codigo: '', nombre: '', importe: null, categoriaId: null }
}
</script>

<style scoped>
.inline-edit {
  @apply w-full bg-transparent border border-transparent rounded px-2 py-1 text-sm
         hover:border-gray-200 focus:border-purple-400 focus:bg-white focus:outline-none transition-colors;
}
</style>
