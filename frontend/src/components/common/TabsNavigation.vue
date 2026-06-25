<template>
  <div class="border-b border-slate-200">
    <nav class="flex gap-1 px-4" aria-label="Tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('tab-change', tab.id)"
        :class="[
          activeTab === tab.id
            ? 'border-indigo-600 text-indigo-700 bg-indigo-50'
            : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50',
          'whitespace-nowrap py-3 px-3 border-b-2 font-medium text-sm flex items-center rounded-t-md transition-colors'
        ]"
      >
        <span class="mr-2 text-lg">{{ tab.icon }}</span>
        {{ tab.name }}
        <span v-if="tab.count !== undefined && tab.count > 0"
              class="ml-2 bg-indigo-100 text-indigo-700 text-xs font-medium px-2 py-0.5 rounded-full">
          {{ tab.count }}
        </span>
      </button>
    </nav>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    required: true
  },
  activeTab: {
    type: String,
    required: true
  }
})

defineEmits(['tab-change'])
</script>