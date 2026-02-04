<script setup lang="ts">
defineProps<{
  name: string
  element: string
  rarity: number
  image?: string
}>()
</script>

<template>
  <div class="res-card">
    <img :src="image || '/placeholder-res.png'" class="res-image" />

    <div class="content">
      <h3>{{ name }}</h3>
      <p>Element: {{ element }}</p>
      <p>Rarity: {{ '★'.repeat(rarity) }}</p>
    </div>
  </div>
</template>

<style scoped>
.res-card {
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border);
  border-radius: var(--radius);
  padding: var(--space-md);
  box-shadow: var(--ww-shadow);
  transition: var(--transition);
}

.res-card:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}

.res-image {
  width: 100%;
  border-radius: var(--radius);
  margin-bottom: 1rem;
}
</style>

