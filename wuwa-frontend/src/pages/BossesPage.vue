<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import WWBossDetail from '@/components/ui/WWBossDetail.vue'
</script>

<template>
  <main class="page fx-grid">
    <WWPanel title="Bosses">
      <WWBossDetail
        name="Tempest Mephis"
        :health="82"
        description="A fast and deadly Aero predator."
      />
      <WWBossDetail
        name="Inferno Rider"
        :health="60"
        description="A mounted Havoc powerhouse."
      />
    </WWPanel>
  </main>
</template>

