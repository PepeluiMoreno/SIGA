<template>
  <DebugPanel />
  <div :class="debug.enabled ? 'pt-44 lg:pt-36' : ''">
    <router-view />
  </div>
</template>

<script setup>
import DebugPanel from '@/components/common/DebugPanel.vue'
import { useDebugStore } from '@/stores/debug.js'

const debug = useDebugStore()
</script>
