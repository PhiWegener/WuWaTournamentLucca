<script setup lang="ts">
import { ref } from 'vue'
import { login } from '@/services/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function submit() {
  try {
    await login(username.value, password.value)
    router.push('/admin')
  } catch {
    error.value = 'Invalid username or password'
  }
}
</script>

<template>
  <div class="login-container fx-grid">
    <div class="login-box fx-glow">
      <h2>Admin Login</h2>
      <input v-model="username" placeholder="Username" />
      <input v-model="password" type="password" placeholder="Password" />
      <button class="ww-btn" @click="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  margin-top: 120px;
}

.login-box {
  width: 300px;
  padding: 2rem;
  background: var(--ww-bg-panel);
  border: 1px solid var(--ww-border-light);
  border-radius: var(--radius-lg);
}
.error {
  color: #ff6b6b;
}
</style>

