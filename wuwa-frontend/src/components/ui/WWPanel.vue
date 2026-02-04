<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<template>
  <div class="ww-panel">
    <h2 v-if="title">{{ title }}</h2>
    <slot></slot>
  </div>
</template>

<style scoped>
.ww-panel {
  padding: var(--space-lg);
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--ww-shadow);
  transition: var(--transition);
}

.ww-panel:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}
</style>

