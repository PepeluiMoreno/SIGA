<template>
  <section>
    <h2 v-if="titulo" class="text-sm font-semibold text-slate-700 mb-2">{{ titulo }}</h2>
    <div v-if="cargando" class="text-sm text-slate-400">Cargando historial…</div>
    <div v-else-if="!items.length" class="text-sm text-slate-400">Sin vinculación registrada.</div>
    <ul v-else class="border border-slate-200 rounded-lg divide-y divide-slate-100 text-sm">
      <li v-for="v in items" :key="v.id" class="px-4 py-2 flex items-center justify-between">
        <span class="font-medium text-slate-800">{{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}</span>
        <span class="text-xs text-slate-500">
          {{ v.fechaInicio || '?' }} → {{ v.fechaFin || 'vigente' }}
          <span class="ml-1 text-slate-400">({{ v.estado }})</span>
        </span>
      </li>
    </ul>
  </section>
</template>

<script setup>
// Componente reutilizable: muestra la trayectoria de vinculaciones de un contacto
// (facetas vigentes + cerradas). Se usa en Mis datos (propio), en la ficha de admin
// y en la consulta a la Junta Directiva.
//
// Dos modos:
//  - `:vinculaciones="arr"`  → presentacional, el padre ya tiene los datos.
//  - `:contacto-id="id"`     → autónomo, los carga él mismo.
import { ref, watch, onMounted } from 'vue'
import { graphqlClient } from '@/graphql/client.js'
import { VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

const props = defineProps({
  contactoId: { type: String, default: null },
  vinculaciones: { type: Array, default: null },
  titulo: { type: String, default: 'Historial de vinculaciones' },
})

const items = ref(props.vinculaciones || [])
const cargando = ref(false)

watch(() => props.vinculaciones, (v) => { if (v) items.value = v })

async function cargar() {
  if (props.vinculaciones) return       // datos provistos por el padre
  if (!props.contactoId) return
  cargando.value = true
  try {
    const vd = await graphqlClient.request(VINCULACIONES_DE_CONTACTO, { contactoId: props.contactoId })
    items.value = vd.vinculacionesDeContacto || []
  } catch {
    // silencioso: el contenedor decide cómo mostrar errores
  } finally {
    cargando.value = false
  }
}
onMounted(cargar)
</script>
