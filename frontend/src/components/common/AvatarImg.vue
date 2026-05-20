<template>
  <div
    class="rounded-full overflow-hidden bg-indigo-100 flex items-center justify-center shrink-0 select-none"
    :style="{ width: sizeMap[size] + 'px', height: sizeMap[size] + 'px' }"
  >
    <img
      v-if="src"
      :src="fullSrc"
      :alt="alt"
      class="w-full h-full object-cover"
      @error="imgError = true"
    />
    <span
      v-else
      class="font-semibold text-indigo-700"
      :style="{ fontSize: sizeMap[size] * 0.38 + 'px' }"
    >
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: null },
  nombre: { type: String, default: '' },
  apellido: { type: String, default: '' },
  alt: { type: String, default: 'Avatar' },
  size: { type: String, default: 'md', validator: (v) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(v) },
})

const sizeMap = { xs: 24, sm: 32, md: 40, lg: 56, xl: 80 }

const imgError = ref(false)

// Resetear el flag de error si cambia el src (p.ej. tras subir nueva foto).
watch(() => props.src, () => { imgError.value = false })

const fullSrc = computed(() => {
  if (!props.src || imgError.value) return null
  if (props.src.startsWith('http') || props.src.startsWith('data:')) return props.src
  // Ruta relativa del servidor: anteponer origen
  return window.location.origin + props.src.replace('/api', '')
})

const initials = computed(() => {
  const n = (props.nombre || '').trim()
  const a = (props.apellido || '').trim()
  if (!n && !a) return '?'
  return ((n[0] || '') + (a[0] || '')).toUpperCase()
})
</script>
