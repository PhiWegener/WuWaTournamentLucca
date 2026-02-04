<template>
  <div class="admin-sidebar fx-grid">
    <h2 class="title">Admin</h2>

    <RouterLink to="/admin">Dashboard</RouterLink>
    <RouterLink to="/admin/players">Players</RouterLink>
    <RouterLink to="/admin/matches">Matches</RouterLink>
    <RouterLink to="/admin/resonators">Resonators</RouterLink>
    <RouterLink to="/admin/bosses">Bosses</RouterLink>
    <RouterLink to="/admin/schedule">Schedule</RouterLink>

    <button class="logout" @click="$emit('logout')">Logout</button>
  </div>
</template>

<style scoped>
.admin-sidebar {
  width: 260px;
  height: 100vh;
  padding: 1.5rem;
  position: fixed;
  top: 64px; /* below nav bar */
  left: 0;
  background: rgba(10, 12, 14, 0.9);
  border-right: 1px solid var(--ww-border-light);
}
.title {
  color: var(--ww-accent-light);
  margin-bottom: 1rem;
}
.logout {
  margin-top: 2rem;
  color: #ff7777;
}
</style>

