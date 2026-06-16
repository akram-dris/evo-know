import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
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
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    if (role === 'Reader') {
      next({ name: 'KnowledgeBase' })
    } else {
      next({ name: 'Dashboard' })
    }
  } else if (token && role === 'Reader' && to.name !== 'KnowledgeBase') {
    next({ name: 'KnowledgeBase' })
  } else if (token && role !== 'Admin' && to.name === 'Users') {
    if (role === 'Reader') {
      next({ name: 'KnowledgeBase' })
    } else {
      next({ name: 'Dashboard' })
    }
  } else {
    next()
  }
})

export default router
