import { createRouter, createWebHistory } from 'vue-router'
import Alerting from '../views/Alerting.vue'

const routes = [
  {
    path: '/',
    name: 'Alerting',
    component: Alerting
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
