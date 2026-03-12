import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ========== 公开区域 ==========
  {
    path: '/',
    redirect: '/admin/knowledge/dashboard'
  },
  
  // ========== 认证区域（保留但不强制）==========
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
  
  // ========== 企业用户后台（暂时开放）==========
  {
    path: '/company',
    component: () => import('@/layouts/CompanyLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/company/chat'
      },
      {
        path: 'chat',
        name: 'CompanyChat',
        component: () => import('@/views/company/ChatPage.vue'),
        meta: { title: 'AI法律问答 - 内控AI' }
      },
      {
        path: 'history',
        name: 'CompanyHistory',
        component: () => import('@/views/company/HistoryPage.vue'),
        meta: { title: '查询历史 - 内控AI' }
      }
    ]
  },
  
  // ========== 超级管理员后台（移除权限检查）==========
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/admin/knowledge/dashboard'
      },
      
      // ==========================================
      // 法律知识库模块（新增，无需登录）
      // ==========================================
      {
        path: 'knowledge/dashboard',
        name: 'KnowledgeDashboard',
        component: () => import('@/views/admin/knowledge/Dashboard.vue'),
        meta: { title: '知识库仪表盘 - 内控AI' }
      },
      
      // 法律层级管理 - 汇总页面
      {
        path: 'knowledge/hierarchy',
        name: 'LegalHierarchy',
        component: () => import('@/views/admin/knowledge/Hierarchy.vue'),
        meta: { title: '法律层级管理 - 内控AI' }
      },
      
      // 法律层级管理 - 各个层级详情页
      {
        path: 'knowledge/hierarchy/:level',
        name: 'HierarchyDetail',
        component: () => import('@/views/admin/knowledge/HierarchyDetail.vue'),
        meta: { title: '法律层级详情 - 内控AI' }
      },
      
      {
        path: 'knowledge/standards',
        name: 'IndustryStandards',
        component: () => import('@/views/admin/knowledge/IndustryStandards.vue'),
        meta: { title: '行业准则管理 - 内控AI' }
      },
      {
        path: 'knowledge/monitor',
        name: 'VectorMonitor',
        component: () => import('@/views/admin/knowledge/VectorMonitor.vue'),
        meta: { title: '向量监控 - 内控AI' }
      },
      
      // ==========================================
      // 法律管理（原有页面）
      // ==========================================
      {
        path: 'laws',
        name: 'AdminLaws',
        component: () => import('@/views/admin/LawsList.vue'),
        meta: { title: '法律分类管理 - 内控AI' }
      },
      {
        path: 'laws/:id',
        name: 'AdminLawDetail',
        component: () => import('@/views/admin/LawDetail.vue'),
        meta: { title: '文档详情 - 内控AI' }
      },
      {
        path: 'standards',
        name: 'AdminStandards',
        component: () => import('@/views/admin/StandardsList.vue'),
        meta: { title: '标准分类管理 - 内控AI' }
      },
      {
        path: 'standards/:id',
        name: 'AdminStandardDetail',
        component: () => import('@/views/admin/StandardDetail.vue'),
        meta: { title: '标准详情 - 内控AI' }
      },
      
      // ==========================================
      // 其他管理页面（原有）
      // ==========================================
      {
        path: 'companies',
        name: 'AdminCompanies',
        component: () => import('@/views/admin/CompaniesPage.vue'),
        meta: { title: '企业管理 - 内控AI' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersPage.vue'),
        meta: { title: '用户管理 - 内控AI' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 简化的路由守卫（只设置标题，不检查权限）
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '内控AI'
  
  // 直接放行所有请求
  next()
})

export default router


