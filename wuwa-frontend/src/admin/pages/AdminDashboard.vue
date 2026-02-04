<script setup lang="ts">
import AdminSidebar from '../components/AdminSidebar.vue'
import { logout } from '@/services/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
function onLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar @logout="onLogout" />

    <div class="admin-content">
      <h1>Admin Dashboard</h1>
      <p>Manage all tournament content.</p>
    </div>
  </div>
</template>

<style scoped>
.admin-content {
  margin-left: 260px;
  padding: 2rem;
}
</style>

