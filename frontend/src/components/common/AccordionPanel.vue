<template>
  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
    <button
      type="button"
      @click="open = !open"
      class="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
    >
      <div class="flex items-center gap-3">
        <ChevronDownIcon class="w-4 h-4 text-slate-400 transition-transform" :class="open ? '' : '-rotate-90'" />
        <h2 class="text-sm font-semibold text-slate-800">{{ title }}</h2>
        <span v-if="count !== null" class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">{{ count }}</span>
      </div>
      <div class="flex items-center gap-2" @click.stop>
        <slot name="actions" />
      </div>
    </button>
    <div v-show="open" class="border-t border-slate-100">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: { type: String, required: true },
  count: { type: [Number, String, null], default: null },
  defaultOpen: { type: Boolean, default: true },
})

const open = ref(props.defaultOpen)

watch(() => props.defaultOpen, (v) => { open.value = v })
</script>
