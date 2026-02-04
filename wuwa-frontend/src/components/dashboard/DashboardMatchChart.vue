<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { Chart, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js'

Chart.register(LineElement, PointElement, LinearScale, Title, CategoryScale)

defineProps<{
  matchData: number[]
  labels: string[]
}>()
</script>

<template>
  <div class="chart-panel">
    <h3>Match Score Trend</h3>

    <Line
      :data="{
        labels: labels,
        datasets: [{
          label: 'Match Scores',
          data: matchData,
          borderColor: '#6cbcff',
          backgroundColor: 'rgba(108, 188, 255, 0.3)',
          tension: 0.3
        }]
      }"
      :options="{
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#8cd3ff' } },
          y: { ticks: { color: '#8cd3ff' } }
        }
      }"
    />
  </div>
</template>

<style scoped>
.chart-panel {
  background: var(--ww-bg-panel);
  border-radius: var(--radius-lg);
  border: 1px solid var(--ww-border);
  padding: 1.5rem;
}
</style>

