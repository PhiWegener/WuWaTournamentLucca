<script setup lang="ts">
defineProps<{
  name: string
  rank?: number
  avatar?: string
  team?: string
}>()
</script>

<template>
  <div class="player-card">
    <img class="avatar" :src="avatar || '/placeholder-player.png'" />
    <div class="info">
      <h3>{{ name }}</h3>
      <p v-if="team">Team: {{ team }}</p>
      <p v-if="rank">Rank: #{{ rank }}</p>
    </div>
  </div>
</template>

<style scoped>
.player-card {
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border);
  border-radius: var(--radius);
  padding: var(--space-md);
  display: flex;
  gap: 1rem;
  align-items: center;
  transition: var(--transition);
  box-shadow: var(--ww-shadow);
}

.player-card:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: var(--radius);
  object-fit: cover;
}
</style>

