<script setup lang="ts">
defineProps<{
  name: string
  health: number
  image?: string
  description?: string
}>()
</script>

<template>
  <div class="boss">
    <img class="boss-img" :src="image || '/placeholder-boss.png'" />

    <div class="info">
      <h2>{{ name }}</h2>
      <p>{{ description }}</p>
      <div class="hp-bar">
        <div class="hp" :style="{ width: health + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.boss {
  display: flex;
  gap: 1.5rem;
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border);
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--ww-shadow);
  transition: var(--transition);
}

.boss:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}

.boss-img {
  width: 180px;
  border-radius: var(--radius);
}

.hp-bar {
  width: 100%;
  height: 12px;
  background: var(--ww-border);
  border-radius: 8px;
  margin-top: 1rem;
  overflow: hidden;
}

.hp {
  height: 100%;
  background: var(--ww-accent);
  transition: width 0.5s ease;
}
</style>

