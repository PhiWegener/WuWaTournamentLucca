<script setup lang="ts">
defineProps<{
  label: string
  variant?: 'default' | 'accent' | 'danger' | 'holo'
}>()
</script>

<template>
  <button
    class="ww-btn"
    :class="[variant || 'default']"
  >
    <slot>{{ label }}</slot>
  </button>
</template>

<style scoped>
.ww-btn {
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius);
  border: 1px solid var(--ww-border-light);
  background: var(--ww-bg-panel);
  color: var(--ww-text);
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
}

/* Default */
.default:hover {
  border-color: var(--ww-accent);
  color: var(--ww-accent-light);
  box-shadow: var(--ww-glow);
}

/* Accent */
.accent {
  background: var(--ww-accent-dark);
  border-color: var(--ww-accent);
}
.accent:hover {
  background: var(--ww-accent);
  box-shadow: var(--ww-glow);
}

/* Danger */
.danger {
  background: var(--ww-danger);
  border-color: #ff9999;
}

/* Hologram – animated WW-style */
.holo {
  border-color: var(--ww-accent);
  background: transparent;
  color: var(--ww-accent-light);
  position: relative;
  overflow: hidden;
}

.holo::after {
  content: "";
  position: absolute;
  inset: 0;
  border: 1px solid var(--ww-accent);
  opacity: 0.4;
  filter: blur(2px);
  animation: holoPulse 2s infinite alternate;
}

@keyframes holoPulse {
  from { opacity: 0.3; }
  to   { opacity: 0.7; }
}
</style>

