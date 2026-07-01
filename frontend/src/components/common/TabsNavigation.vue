<template>
  <!-- Tabsheet canónico del proyecto: "segmented control" — un track gris redondeado
       de fondo, y la solapa ACTIVA como pastilla blanca con sombra que resalta sobre él.
       Estilo único para TODAS las solapas del proyecto. -->
  <div class="inline-flex items-center gap-1 rounded-xl bg-slate-100 p-1" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      type="button"
      role="tab"
      :aria-selected="activeTab === tab.id"
      @click="$emit('tab-change', tab.id)"
      :class="[
        'inline-flex items-center gap-2 whitespace-nowrap rounded-lg px-4 py-2 text-sm transition-all',
        activeTab === tab.id
          ? 'bg-white text-indigo-700 font-semibold shadow-sm'
          : 'text-slate-500 font-medium hover:text-slate-800'
      ]"
    >
      {{ tab.name }}
      <span v-if="tab.count !== undefined && tab.count !== null && tab.count > 0"
        :class="[
          'text-xs font-semibold px-1.5 py-0.5 rounded-full transition-colors',
          activeTab === tab.id ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-200 text-slate-500'
        ]">
        {{ tab.count }}
      </span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  // Array de { id, name, count? }. `count` opcional muestra un badge.
  tabs: { type: Array, required: true },
  activeTab: { type: String, required: true },
})

defineEmits(['tab-change'])
</script>
