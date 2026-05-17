<template>
  <div><slot /></div>
</template>

<script setup>
import { provide, ref } from 'vue'

const activeId = ref(null)

provide('accordionGroup', {
  activeId,
  activate(id) { activeId.value = id },
  claimDefault(id) { if (activeId.value === null) activeId.value = id },
})
</script>
