<template>
  <div class="ww-glow"><slot /></div>
</template>

<style scoped>
.ww-glow {
  animation: glowPulse 2.5s infinite alternate;
}

@keyframes glowPulse {
  from { filter: drop-shadow(0 0 4px rgba(108,188,255,.2)); }
  to   { filter: drop-shadow(0 0 10px rgba(108,188,255,.5)); }
}
</style>

