<template>
  <tr class="hover:bg-slate-50 transition-colors">
    <td class="px-4 py-3 font-medium text-slate-900" :class="indent ? 'pl-10' : ''">
      {{ actividad.nombre }}
      <span v-if="esPlantilla"
        class="ml-2 text-xs px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 align-middle">Plantilla</span>
    </td>
    <td class="px-4 py-3 text-slate-500">{{ actividad.tipoActividad?.nombre || '—' }}</td>
    <td class="px-4 py-3 text-slate-500">{{ caracterLabel }}</td>
    <td class="px-4 py-3">
      <span
        v-if="actividad.estado"
        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
        :style="actividad.estado.color ? `background-color: ${actividad.estado.color}22; color: ${actividad.estado.color}` : ''"
        :class="!actividad.estado.color ? 'bg-slate-100 text-slate-600' : ''"
      >
        {{ actividad.estado.nombre }}
      </span>
      <span v-else class="text-slate-400">—</span>
    </td>
    <td class="px-4 py-3 text-slate-500">{{ actividad.fechaInicio || '—' }}</td>
    <td class="px-4 py-3">
      <RowActions
        :show-view="true"
        :show-edit="true"
        confirm-title="¿Eliminar esta actividad?"
        :confirm-text="`«${actividad.nombre}» será eliminada permanentemente.`"
        @view="abrir"
        @edit="abrir"
        @delete="(opts) => $emit('delete', opts)"
      />
    </td>
  </tr>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import RowActions from '@/components/common/RowActions.vue'

const props = defineProps({
  actividad: { type: Object, required: true },
  // true para filas anidadas bajo una campaña (sangría visual del árbol)
  indent: { type: Boolean, default: false },
})

defineEmits(['delete'])

const router = useRouter()
const abrir = () => router.push(`/actividades/${props.actividad.id}`)

// Plantilla recurrente: caracter RECURRENTE sin padre. No es imputable y se marca.
const esPlantilla = computed(() =>
  props.actividad.caracter === 'RECURRENTE' && !props.actividad.padreId
)

const caracterLabel = computed(() => {
  const c = props.actividad.caracter
  if (c === 'PERMANENTE') return 'Permanente'
  if (c === 'PUNTUAL') return 'Puntual'
  if (c === 'RECURRENTE') return esPlantilla.value ? 'Recurrente (plantilla)' : 'Recurrente (instancia)'
  return '—'
})
</script>
