import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../pages/Dashboard.vue'
import Landing from '../pages/Landing.vue'
import Run from '../pages/Run.vue'
import Models from '../pages/Models.vue'
import Prompts from '../pages/Prompts.vue'
import History from '../pages/History.vue'
import Settings from '../pages/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Landing },
    { path: '/run', component: Run },
    { path: '/dashboard', component: Dashboard },
    { path: '/tasks', redirect: '/run' },
    { path: '/models', component: Models },
    { path: '/prompts', component: Prompts },
    { path: '/history', component: History },
    { path: '/settings', component: Settings },
  ],
})

export default router
