<template>
  <div class="flex items-start justify-between mb-5 gap-4">
    <div class="flex items-center gap-3 min-w-0">
      <!-- Acento vertical -->
      <div class="hidden sm:block w-1 self-stretch rounded-full bg-purple-500 shrink-0" />

      <!-- Icono opcional -->
      <span v-if="icon" class="text-2xl leading-none shrink-0 select-none">{{ icon }}</span>

      <!-- Título + subtítulo -->
      <div class="min-w-0">
        <h1 class="text-xl font-bold text-gray-900 leading-tight truncate">{{ title }}</h1>
        <p v-if="subtitle" class="text-xs text-gray-400 mt-0.5 truncate">{{ subtitle }}</p>
      </div>
    </div>

    <!-- Zona de acciones (botones, badges, etc.) -->
    <div v-if="$slots.actions" class="flex items-center gap-2 shrink-0 pt-0.5">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title:    { type: String, default: '' },
  subtitle: { type: String, default: '' },
  icon:     { type: String, default: '' },
})
</script>
