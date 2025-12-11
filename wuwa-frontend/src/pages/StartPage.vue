<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import DashboardStats from '@/components/dashboard/DashboardStats.vue'
import DashboardLeaderboard from '@/components/dashboard/DashboardLeaderboard.vue'
import DashboardMatchChart from '@/components/dashboard/DashboardMatchChart.vue'
import DashboardResonatorChart from '@/components/dashboard/DashboardResonatorChart.vue'

// Mock Data (replace with API later)
const stats = {
  players: 24,
  matches: 16,
  winrate: 57,
  avgScore: 134
}

const leaderboard = [
  { name: 'Kuro', team: 'Astra', score: 330 },
  { name: 'Lingyang', team: 'Tidebreak', score: 301 },
  { name: 'Baizhi', team: 'Null Matrix', score: 260 },
  { name: 'Jiyan', team: 'Resonance', score: 240 }
]

const matchLabels = ['R1', 'R2', 'R3', 'R4', 'R5']
const matchScores = [120, 134, 128, 150, 142]

const resonators = ['Jiyan', 'Yinlin', 'Chixia', 'Taoqi']
const picks = [82, 67, 44, 32]
</script>

<template>
  <main class="page fx-grid fx-scanlines">
    <WWPanel title="Tournament Dashboard">

      <!-- Stats -->
      <DashboardStats :stats="stats" />

      <div class="grid dashboard-grid">
        <!-- Left Column: Leaderboard -->
        <DashboardLeaderboard :players="leaderboard" />

        <!-- Right Column: Charts -->
        <div class="grid charts-grid">
          <DashboardMatchChart
            :labels="matchLabels"
            :matchData="matchScores"
          />

          <DashboardResonatorChart
            :resonators="resonators"
            :pickRates="picks"
          />
        </div>
      </div>

    </WWPanel>
  </main>
</template>

<style scoped>
.dashboard-grid {
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
}

.charts-grid {
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

/* Responsive */
@media (max-width: 850px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>

