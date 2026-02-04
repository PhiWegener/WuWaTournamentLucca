import { isAuthenticated } from '@/services/auth'

export function adminGuard(to: any, from: any, next: any) {
  if (!isAuthenticated()) {
    next('/login')
  } else {
    next()
  }
}

