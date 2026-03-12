import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  // ========== 公开区域 ==========
  {
    path: '/',
    redirect: '/admin/knowledge/dashboard'
  },
  
  // ========== 认证区域 ==========
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: { title: '登录 - 内控AI', public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterPage.vue'),
    meta: { title: '注册 - 内控AI', public: true }
  },
  
  // ========== 企业用户后台（需要登录）==========
  {
    path: '/company',
    component: () => import('@/layouts/CompanyLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/company/chat'
      },
      {
        path: 'chat',
        name: 'CompanyChat',
        component: () => import('@/views/company/ChatPage.vue'),
        meta: { title: 'AI法律问答 - 内控AI', requiresAuth: true }
      },
      {
        path: 'history',
        name: 'CompanyHistory',
        component: () => import('@/views/company/HistoryPage.vue'),
        meta: { title: '查询历史 - 内控AI', requiresAuth: true }
      }
    ]
  },
  
  // ========== 超级管理员后台（需要管理员权限）==========
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/knowledge/dashboard'
      },
      
      // ==========================================
      // 法律知识库模块
      // ==========================================
      {
        path: 'knowledge/dashboard',
        name: 'KnowledgeDashboard',
        component: () => import('@/views/admin/knowledge/Dashboard.vue'),
        meta: { title: '知识库仪表盘 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      
      // 法律层级管理 - 汇总页面
      {
        path: 'knowledge/hierarchy',
        name: 'LegalHierarchy',
        component: () => import('@/views/admin/knowledge/Hierarchy.vue'),
        meta: { title: '法律层级管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      
      // 法律层级管理 - 各个层级详情页
      {
        path: 'knowledge/hierarchy/:level',
        name: 'HierarchyDetail',
        component: () => import('@/views/admin/knowledge/HierarchyDetail.vue'),
        meta: { title: '法律层级详情 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      
      {
        path: 'knowledge/standards',
        name: 'IndustryStandards',
        component: () => import('@/views/admin/knowledge/IndustryStandards.vue'),
        meta: { title: '行业准则管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'knowledge/monitor',
        name: 'VectorMonitor',
        component: () => import('@/views/admin/knowledge/VectorMonitor.vue'),
        meta: { title: '向量监控 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      
      // ==========================================
      // 法律管理
      // ==========================================
      {
        path: 'laws',
        name: 'AdminLaws',
        component: () => import('@/views/admin/LawsList.vue'),
        meta: { title: '法律分类管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'laws/:id',
        name: 'AdminLawDetail',
        component: () => import('@/views/admin/LawDetail.vue'),
        meta: { title: '文档详情 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'standards',
        name: 'AdminStandards',
        component: () => import('@/views/admin/StandardsList.vue'),
        meta: { title: '标准分类管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'standards/:id',
        name: 'AdminStandardDetail',
        component: () => import('@/views/admin/StandardDetail.vue'),
        meta: { title: '标准详情 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      
      // ==========================================
      // 其他管理页面
      // ==========================================
      {
        path: 'companies',
        name: 'AdminCompanies',
        component: () => import('@/views/admin/CompaniesPage.vue'),
        meta: { title: '企业管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersPage.vue'),
        meta: { title: '用户管理 - 内控AI', requiresAuth: true, requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：验证登录状态和管理员权限
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '内控AI'

  const userStore = useUserStore()

  // 需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 需要管理员角色（super_admin 或 company_admin）
  if (to.meta.requiresAdmin) {
    const role = userStore.currentUser?.role
    const isAdmin = role === 'super_admin' || role === 'company_admin' ||
                    role === 'SUPER_ADMIN' || role === 'COMPANY_ADMIN'
    if (!isAdmin) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

export default router


