<script setup lang="ts">
defineProps<{
  teamA: string
  teamB: string
  scoreA: number
  scoreB: number
}>()
</script>

<template>
  <div class="match">
    <div class="team">{{ teamA }}</div>
    <div class="score">{{ scoreA }} : {{ scoreB }}</div>
    <div class="team">{{ teamB }}</div>
  </div>
</template>

<style scoped>
.match {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  padding: var(--space-md);
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border);
  border-radius: var(--radius);
  text-align: center;
  transition: var(--transition);
}

.match:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}

.score {
  font-size: 1.4rem;
  color: var(--ww-accent-light);
  font-weight: bold;
}
</style>

