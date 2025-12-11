<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <!-- Top Navigation -->
  <nav class="ww-topnav fx-grid fx-scanlines">
    <div class="left">
      <img
        alt="Tournament Logo"
        class="nav-logo"
        src="@/assets/ww-tournament-logo.svg"
      />
      <span class="title">Wuthering Waves Esports Tournament</span>
    </div>

    <div class="links">
      <RouterLink to="/">Dashboard</RouterLink>
      <RouterLink to="/schedule">Schedule</RouterLink>
      <RouterLink to="/players">Players</RouterLink>
      <RouterLink to="/matches">Matches</RouterLink>
      <RouterLink to="/resonators">Resonators</RouterLink>
      <RouterLink to="/bosses">Bosses</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </div>
  </nav>

  <!-- Actual Page Content -->
  <main class="page-container">
    <RouterView />
  </main>
</template>

<style scoped>
/* ========= TOP NAVIGATION ========== */
.ww-topnav {
  position: fixed;      /* Make it truly stick to the top */
  top: 0;
  left: 0;
  right: 0;

  z-index: 1000;
  height: 64px;

  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 0 1.5rem;
  background: rgba(10, 12, 14, 0.85);
  backdrop-filter: blur(10px);

  border-bottom: 1px solid var(--ww-border-light);
  box-shadow: var(--ww-shadow);
}

/* Add spacing so content doesn't hide behind the fixed nav */
.page-container {
  padding-top: 80px; /* slightly larger than nav */
}


/* ========= NAV LEFT SECTION ========= */

.left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.nav-logo {
  height: 42px;
  width: 42px;
  object-fit: contain;
  filter: drop-shadow(0 0 6px rgba(108,188,255,0.4));
}

.title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ww-accent-light);
  letter-spacing: 0.5px;
}


/* ========= NAV LINKS ========== */

.links {
  display: flex;
  gap: 1rem;
}

.links a {
  padding: 0.4rem 0.8rem;
  border-left: 1px solid var(--ww-border);
  color: var(--ww-text);
  transition: var(--transition-fast);
}

.links a:first-child {
  border-left: none;
}

.links a.router-link-exact-active {
  color: var(--ww-accent-light);
  font-weight: bold;
  text-shadow: var(--ww-glow);
}

.links a:hover {
  color: var(--ww-accent);
}
</style>

