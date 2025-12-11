<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import WWMatchResult from '@/components/ui/WWMatchResult.vue'
</script>

<template>
  <main class="page fx-grid">
    <WWPanel title="Tournament Schedule">
      <WWMatchResult
        teamA="Team Resonance"
        teamB="Voidwalkers"
        :scoreA="2"
        :scoreB="1"
      />
      <WWMatchResult
        teamA="Astra Rangers"
        teamB="Echo Hunters"
        :scoreA="0"
        :scoreB="2"
      />
    </WWPanel>
  </main>
</template>

