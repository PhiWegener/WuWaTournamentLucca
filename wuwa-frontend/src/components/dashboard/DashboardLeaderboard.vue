<script setup lang="ts">
defineProps<{
  players: { name: string; team: string; score: number }[]
}>()

const sorted = [...__props.players].sort((a, b) => b.score - a.score)
</script>

<template>
  <div class="leaderboard">
    <h3 class="title">Leaderboard</h3>
    <table class="table">
      <thead>
        <tr>
          <th>Player</th>
          <th>Team</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in sorted" :key="p.name">
          <td>{{ p.name }}</td>
          <td>{{ p.team }}</td>
          <td class="highlight">{{ p.score }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.leaderboard {
  padding: 1.5rem;
  background: var(--ww-bg-panel);
  border-radius: var(--radius-lg);
  border: 1px solid var(--ww-border);
}

.title {
  margin-bottom: 1rem;
}

.highlight {
  color: var(--ww-accent-light);
  font-weight: bold;
}
</style>

