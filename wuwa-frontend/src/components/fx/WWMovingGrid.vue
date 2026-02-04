<template>
  <div class="moving-grid"><slot /></div>
</template>

<style scoped>
.moving-grid {
  position: relative;
}

.moving-grid::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  animation: gridMove 12s linear infinite;
  pointer-events: none;
}

@keyframes gridMove {
  from { background-position: 0 0; }
  to   { background-position: 100px 200px; }
}
</style>

