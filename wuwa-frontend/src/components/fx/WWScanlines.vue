<template>
  <div class="scanlines"><slot /></div>
</template>

<style scoped>
.scanlines {
  position: relative;
}

.scanlines::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.03) 0px,
    rgba(255,255,255,0.03) 1px,
    transparent 2px,
    transparent 4px
  );
  animation: scanAnim 7s linear infinite;
}

@keyframes scanAnim {
  0% { background-position: 0 0; }
  100% { background-position: 0 200px; }
}
</style>

