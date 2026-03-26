import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/ConfigView.vue')
  },
  {
    path: '/actions',
    name: 'Actions',
    component: () => import('@/views/ActionsView.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/LogsView.vue')
  },
  {
    path: '/model',
    name: 'Model',
    component: () => import('@/views/ModelView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
