<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import WWCardPlayer from '@/components/ui/WWCardPlayer.vue'
</script>

<template>
  <main class="page fx-grid">
    <WWPanel title="Players">
      <div class="grid grid-3">
        <WWCardPlayer name="Kuro" team="Astra" :rank="1" />
        <WWCardPlayer name="Lingyang" team="Tidebreak" :rank="2" />
        <WWCardPlayer name="Baizhi" team="Null Matrix" :rank="3" />
      </div>
    </WWPanel>
  </main>
</template>

