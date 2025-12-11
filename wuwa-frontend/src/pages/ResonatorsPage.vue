<script setup lang="ts">
import WWPanel from '@/components/ui/WWPanel.vue'
import WWCardResonator from '@/components/ui/WWCardResonator.vue'
</script>

<template>
  <main class="page fx-grid">
    <WWPanel title="Resonators">
      <div class="grid grid-3">
        <WWCardResonator name="Jiyan" element="Aero" :rarity="5" />
        <WWCardResonator name="Yinlin" element="Electro" :rarity="5" />
        <WWCardResonator name="Danjin" element="Havoc" :rarity="4" />
      </div>
    </WWPanel>
  </main>
</template>

