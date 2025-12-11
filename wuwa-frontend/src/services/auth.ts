import api from './api'

export async function login(username: string, password: string) {
  const res = await api.post('/auth/login', { username, password })
  localStorage.setItem('token', res.data.access_token)
}

export function logout() {
  localStorage.removeItem('token')
}

export function isAuthenticated() {
  return !!localStorage.getItem('token')
}

