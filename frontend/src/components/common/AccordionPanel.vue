<template>
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
    <button
      type="button"
      @click="toggle"
      class="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
    >
      <div class="flex items-center gap-3">
        <slot name="title">
          <h2 class="text-sm font-semibold text-slate-800">{{ title }}</h2>
          <span v-if="count !== null" class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">{{ count }}</span>
        </slot>
      </div>
      <div class="flex items-center gap-2" @click.stop>
        <slot name="actions" />
        <ChevronDownIcon
          class="w-4 h-4 text-slate-400 transition-transform duration-200"
          :class="open ? 'rotate-180' : ''"
        />
      </div>
    </button>
    <div v-show="open" class="border-t border-slate-100">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject, onMounted, getCurrentInstance } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: { type: String, default: '' },
  count: { type: [Number, String, null], default: null },
  defaultOpen: { type: Boolean, default: true },
})

const uid = getCurrentInstance().uid
const group = inject('accordionGroup', null)
const _open = ref(!group && props.defaultOpen)

const open = computed(() => group ? group.activeId.value === uid : _open.value)

function toggle() {
  if (group) {
    group.activate(open.value ? null : uid)
  } else {
    _open.value = !_open.value
  }
}

onMounted(() => {
  if (group && props.defaultOpen) {
    group.claimDefault(uid)
  }
})

watch(() => props.defaultOpen, (v) => {
  if (!group) _open.value = v
})
</script>
