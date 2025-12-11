<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale } from 'chart.js'

Chart.register(BarElement, CategoryScale, LinearScale)

defineProps<{
  resonators: string[]
  pickRates: number[]
}>()
</script>

<template>
  <div class="chart-panel">
    <h3>Resonator Pick Rate</h3>

    <Bar
      :data="{
        labels: resonators,
        datasets: [{
          label: 'Pick Rate %',
          data: pickRates,
          backgroundColor: '#2a6f99'
        }]
      }"
      :options="{
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

