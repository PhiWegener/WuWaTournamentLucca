<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import WWMatchResult from '@/components/ui/WWMatchResult.vue'
</script>

<template>
  <main class="page fx-grid">
    <WWPanel title="Match Overview">
      <WWMatchResult teamA="Resonance" teamB="Astra" :scoreA="2" :scoreB="0" />
      <WWMatchResult teamA="Spectra" teamB="Null Matrix" :scoreA="1" :scoreB="2" />
    </WWPanel>
  </main>
</template>

