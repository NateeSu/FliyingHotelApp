import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView_Material.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView_Material.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/UsersView_Material.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN'] }
  },
  // Phase 2: Room Management
  {
    path: '/room-types',
    name: 'RoomTypes',
    component: () => import('@/views/RoomTypesView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN'] }
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: () => import('@/views/RoomsView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECEPTION'] }
  },
  {
    path: '/room-rates',
    name: 'RoomRates',
    component: () => import('@/views/RoomRatesView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN'] }
  },
  // Phase 3: Dashboard
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECEPTION'] }
  },
  // Phase 5: Housekeeping
  {
    path: '/housekeeping',
    name: 'Housekeeping',
    component: () => import('@/views/HousekeepingView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'HOUSEKEEPING', 'RECEPTION'] }
  },
  // Phase 6: Maintenance
  {
    path: '/maintenance',
    name: 'Maintenance',
    component: () => import('@/views/MaintenanceView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'MAINTENANCE', 'RECEPTION'] }
  },
  // Phase 5.1: System Settings
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN'] }
  },
  // Phase 7: Booking System
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/views/BookingCalendarView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECEPTION'] }
  },
  // Phase 7: Customer Management
  {
    path: '/customers',
    name: 'Customers',
    component: () => import('@/views/CustomersView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECEPTION'] }
  },
  // Phase 5.1: Public Task Pages (no authentication required)
  {
    path: '/public/housekeeping/tasks/:taskId',
    name: 'PublicHousekeepingTask',
    component: () => import('@/views/PublicHousekeepingTaskView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/public/maintenance/tasks/:taskId',
    name: 'PublicMaintenanceTask',
    component: () => import('@/views/PublicMaintenanceTaskView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/public/maintenance/report',
    name: 'PublicMaintenanceReport',
    component: () => import('@/views/PublicMaintenanceReportView.vue'),
    meta: { requiresAuth: false }
  },
  // Phase 6: Guest QR Code Ordering (no authentication required)
  {
    path: '/public/guest/room/:roomId/order',
    name: 'GuestOrder',
    component: () => import('@/views/PublicGuestOrderView.vue'),
    meta: { requiresAuth: false }
  },
  // Phase 6: QR Code Manager (Admin only)
  {
    path: '/qrcode-manager',
    name: 'QRCodeManager',
    component: () => import('@/views/QRCodeManagerView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // Redirect to home if already authenticated and trying to access login
    next({ name: 'Home' })
  } else if (to.meta.roles && Array.isArray(to.meta.roles)) {
    // Check role-based access
    if (authStore.hasRole(to.meta.roles as string[])) {
      next()
    } else {
      // Redirect to home if user doesn't have required role
      next({ name: 'Home' })
    }
  } else {
    next()
  }
})

export default router
