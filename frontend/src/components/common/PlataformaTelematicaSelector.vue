<template>
  <div v-if="loading" class="text-xs text-slate-500 italic">Cargando plataformas…</div>

  <div v-else-if="!plataformasActivas.length"
    class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
    No hay plataformas telemáticas activas en el catálogo.
    <router-link v-if="enlaceCatalogo" to="/parametrizacion/plataformas-telematicas"
      class="underline text-amber-900">Configurar plataformas</router-link>
  </div>

  <div v-else class="space-y-3">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Plataforma <span v-if="requerido" class="text-red-500">*</span>
      </label>
      <select :value="plataformaId" @change="onPlataformaChange($event.target.value)"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
        <option value="">Selecciona…</option>
        <option v-for="p in plataformasActivas" :key="p.id" :value="p.id">
          {{ p.icono || '📹' }} {{ p.nombre }}
        </option>
      </select>
      <p v-if="plataformaSeleccionada?.descripcion"
        class="mt-1 text-[11px] text-slate-500">{{ plataformaSeleccionada.descripcion }}</p>
    </div>

    <div v-for="campo in campos" :key="campo.key">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ campo.label }}
        <span v-if="campo.requerido" class="text-red-500">*</span>
      </label>
      <input
        :type="tipoInput(campo.tipo)"
        :value="datosConexion?.[campo.key] || ''"
        @input="onCampoChange(campo.key, $event.target.value)"
        :placeholder="campo.placeholder || ''"
        :required="!!campo.requerido"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />
    </div>
  </div>
</template>

<script setup>
/**
 * Selector reutilizable de plataforma telemática + campos dinámicos.
 *
 * Uso típico:
 *   <PlataformaTelematicaSelector
 *     v-model:plataforma-id="form.plataformaTelematicaId"
 *     v-model:datos-conexion="form.datosConexion"
 *     :requerido="form.esTelematica" />
 *
 * El componente carga internamente el catálogo de plataformas activas y
 * renderiza dinámicamente los campos definidos en `camposEsquema` de la
 * plataforma seleccionada. La validación de campos requeridos la realiza
 * `validar()` (expuesto via defineExpose): devuelve un mensaje de error o
 * cadena vacía si todo es válido.
 */
import { ref, computed, onMounted } from 'vue'
import { executeQuery } from '@/graphql/client'
import { GET_PLATAFORMAS_TELEMATICAS } from '@/graphql/queries/secretaria.js'

const props = defineProps({
  /** UUID de la plataforma elegida (v-model:plataforma-id). */
  plataformaId:   { type: String, default: '' },
  /** Objeto con los valores de los campos de conexión (v-model:datos-conexion). */
  datosConexion:  { type: Object, default: () => ({}) },
  /** Si true, la plataforma se considera obligatoria; afecta a la validación. */
  requerido:      { type: Boolean, default: false },
  /** Mostrar enlace al catálogo cuando no hay plataformas activas. */
  enlaceCatalogo: { type: Boolean, default: true },
})

const emit = defineEmits(['update:plataformaId', 'update:datosConexion', 'plataforma-seleccionada'])

const loading = ref(false)
const plataformas = ref([])

const plataformasActivas = computed(() =>
  [...plataformas.value]
    .filter(p => p.activa)
    .sort((a, b) => (a.orden || 0) - (b.orden || 0))
)

const plataformaSeleccionada = computed(() =>
  plataformas.value.find(p => p.id === props.plataformaId) || null
)

const campos = computed(() => {
  const esquema = plataformaSeleccionada.value?.camposEsquema
  if (!esquema) return []
  try {
    const parsed = JSON.parse(esquema)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
})

function tipoInput(tipo) {
  if (tipo === 'password') return 'password'
  if (tipo === 'url')      return 'url'
  if (tipo === 'number')   return 'number'
  return 'text'
}

function onPlataformaChange(nuevoId) {
  emit('update:plataformaId', nuevoId || '')
  // Reset de los datos de conexión al cambiar de plataforma
  emit('update:datosConexion', {})
  emit('plataforma-seleccionada', plataformas.value.find(p => p.id === nuevoId) || null)
}

function onCampoChange(key, valor) {
  emit('update:datosConexion', { ...props.datosConexion, [key]: valor })
}

async function cargar() {
  loading.value = true
  try {
    const data = await executeQuery(GET_PLATAFORMAS_TELEMATICAS)
    plataformas.value = data?.plataformasTelematicas || []
  } catch {
    plataformas.value = []
  } finally {
    loading.value = false
  }
}

/**
 * Devuelve un mensaje de error si la validación falla, o cadena vacía si
 * todo está OK. El padre lo invoca antes de enviar el formulario.
 */
function validar() {
  if (!props.requerido) return ''
  if (!props.plataformaId) return 'Selecciona la plataforma de videoreunión'
  for (const campo of campos.value) {
    if (campo.requerido && !props.datosConexion?.[campo.key]) {
      return `Indica "${campo.label}"`
    }
  }
  return ''
}

/** Plataforma seleccionada (objeto), útil al snapshotear nombre. */
function getPlataformaActual() {
  return plataformaSeleccionada.value
}

defineExpose({ validar, getPlataformaActual, recargar: cargar })

onMounted(cargar)
</script>
