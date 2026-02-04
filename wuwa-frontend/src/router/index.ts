import { createRouter, createWebHistory } from 'vue-router'

// Page imports
import StartPage from '@/pages/StartPage.vue'
import SchedulePage from '@/pages/SchedulePage.vue'
import PlayersPage from '@/pages/PlayersPage.vue'
import MatchesPage from '@/pages/MatchesPage.vue'
import ResonatorsPage from '@/pages/ResonatorsPage.vue'
import BossesPage from '@/pages/BossesPage.vue'
import AboutPage from '@/pages/AboutPage.vue'

// Admin imports
import { adminGuard } from '@/admin/AuthGuard'
import AdminDashboard from '@/admin/pages/AdminDashboard.vue'
import AdminPlayers from '@/admin/pages/AdminPlayers.vue'
import AdminResonators from '@/admin/pages/AdminResonators.vue'
import AdminMatches from '@/admin/pages/AdminMatches.vue'
import AdminBosses from '@/admin/pages/AdminBosses.vue'
import AdminSchedule from '@/admin/pages/AdminSchedule.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public pages
    {
      path: '/',
      name: 'start',
      component: StartPage
    },
    {
      path: '/schedule',
      name: 'schedule',
      component: SchedulePage
    },
    {
      path: '/players',
      name: 'players',
      component: PlayersPage
    },
    {
      path: '/matches',
      name: 'matches',
      component: MatchesPage
    },
    {
      path: '/resonators',
      name: 'resonators',
      component: ResonatorsPage
    },
    {
      path: '/bosses',
      name: 'bosses',
      component: BossesPage
    },
    {
      path: '/about',
      name: 'about',
      component: AboutPage
    },

    // Admin pages
    {
      path: '/admin',
      component: AdminDashboard,
      beforeEnter: adminGuard,
      children: [
        { path: '', component: AdminDashboard }, // Default dashboard
        { path: 'players', component: AdminPlayers },
        { path: 'matches', component: AdminMatches },
        { path: 'resonators', component: AdminResonators },
        { path: 'bosses', component: AdminBosses },
        { path: 'schedule', component: AdminSchedule },
      ]
    },
    {
      path: '/login',
      component: () => import('@/pages/LoginPage.vue')
    }
  ]
})

export default router

