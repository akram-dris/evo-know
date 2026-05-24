import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/prediction',
    name: 'Prediction',
    component: () => import('../views/Prediction.vue')
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue')
  },
  {
    path: '/fusion',
    name: 'Fusion',
    component: () => import('../views/Fusion.vue')
  },
  {
    path: '/consistency',
    name: 'Consistency',
    component: () => import('../views/Consistency.vue')
  },
  {
    path: '/discovery',
    name: 'Discovery',
    component: () => import('../views/Discovery.vue')
  },
  {
    path: '/knowledge-base',
    name: 'KnowledgeBase',
    component: () => import('../views/KnowledgeBase.vue')
  },
  {
    path: '/audit',
    name: 'Audit',
    component: () => import('../views/Audit.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
