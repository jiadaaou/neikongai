<template>
  <el-container class="company-layout">
    <el-aside width="240px" class="sidebar">
      <div class="sidebar-brand">
        <svg class="logo-icon" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="#6c63ff"/>
          <circle cx="16" cy="16" r="6" stroke="#fff" stroke-width="2"/>
          <circle cx="16" cy="16" r="2" fill="#fff"/>
        </svg>
        <span class="brand-text">内控AI</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/company/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI法律问答</span>
        </el-menu-item>
        <el-menu-item index="/company/history">
          <el-icon><Document /></el-icon>
          <span>查询历史</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="40" style="background: var(--primary-color)">
            {{ userStore.currentUser?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-details">
            <div class="user-name">{{ userStore.currentUser?.username }}</div>
            <div class="user-role">企业用户</div>
          </div>
        </div>
        <el-button text @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <div class="header-actions">
            <el-badge :value="3" class="notification-badge">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Document, Bell, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/company/chat': 'AI法律问答',
    '/company/history': '查询历史'
  }
  return titles[route.path] || '企业后台'
})

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.company-layout {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-text {
  color: white;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 1rem 0;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  margin: 0.25rem 1rem;
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 600;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.user-role {
  font-size: 0.875rem;
  opacity: 0.7;
}

.logout-btn {
  width: 100%;
  color: white;
  justify-content: flex-start;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.header {
  background: white;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 2rem;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: #1a1a1a;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.notification-badge {
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
}

.notification-badge:hover {
  color: var(--primary-color);
}

.main-content {
  background: #f5f7fa;
  padding: 2rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
