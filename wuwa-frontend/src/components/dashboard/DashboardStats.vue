<script setup lang="ts">
defineProps<{
  stats: {
    players: number
    matches: number
    winrate: number
    avgScore: number
  }
}>()
</script>

<template>
  <div class="stats-grid">
    <div class="stat-card fx-glow">
      <h3>Players</h3>
      <p>{{ stats.players }}</p>
    </div>

    <div class="stat-card fx-glow">
      <h3>Matches</h3>
      <p>{{ stats.matches }}</p>
    </div>

    <div class="stat-card fx-glow">
      <h3>Avg Winrate</h3>
      <p>{{ stats.winrate }}%</p>
    </div>

    <div class="stat-card fx-glow">
      <h3>Avg Score</h3>
      <p>{{ stats.avgScore }}</p>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--ww-bg-panel);
  padding: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--ww-border);
  text-align: center;
  box-shadow: var(--ww-shadow);
}

.stat-card:hover {
  border-color: var(--ww-accent);
  box-shadow: var(--ww-glow);
}
</style>

