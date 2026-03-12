<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
      <div class="logo-container">
        <el-icon v-if="!isCollapse" :size="32" color="#1890ff"><Management /></el-icon>
        <span v-if="!isCollapse" class="logo-text">内控AI管理后台</span>
        <el-icon v-else class="logo-icon" :size="24"><Management /></el-icon>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <!-- 知识库仪表盘 -->
        <el-menu-item index="/admin/knowledge/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>知识库仪表盘</template>
        </el-menu-item>

        <!-- 法律层级管理（带二级菜单，展开显示各个法律层级）-->
        <el-sub-menu index="hierarchy">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>法律层级管理</span>
          </template>
          <el-menu-item index="/admin/knowledge/hierarchy">
            <el-icon><Menu /></el-icon>
            <template #title>全部层级（汇总）</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge/hierarchy/xianfa">
            <el-icon><Document /></el-icon>
            <template #title>宪法</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge/hierarchy/falv">
            <el-icon><Document /></el-icon>
            <template #title>法律</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge/hierarchy/xingzhengfagui">
            <el-icon><Document /></el-icon>
            <template #title>行政法规</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge/hierarchy/difangxingfagui">
            <el-icon><Document /></el-icon>
            <template #title>地方性法规</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge/hierarchy/sifajieshi">
            <el-icon><Document /></el-icon>
            <template #title>司法解释</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 行业准则管理 -->
        <el-menu-item index="/admin/knowledge/standards">
          <el-icon><Document /></el-icon>
          <template #title>行业准则管理</template>
        </el-menu-item>

        <!-- 向量监控 -->
        <el-menu-item index="/admin/knowledge/monitor">
          <el-icon><Monitor /></el-icon>
          <template #title>向量监控</template>
        </el-menu-item>

        <el-divider />

        <!-- 法律文档管理（原有）-->
        <el-menu-item index="/admin/laws">
          <el-icon><Files /></el-icon>
          <template #title>法律文档管理</template>
        </el-menu-item>

        <!-- 企业管理（原有）-->
        <el-menu-item index="/admin/companies">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>企业管理</template>
        </el-menu-item>

        <!-- 用户管理（原有）-->
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>

      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon v-if="isCollapse"><DArrowRight /></el-icon>
        <el-icon v-else><DArrowLeft /></el-icon>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="top-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Management,
  DataAnalysis,
  FolderOpened,
  Document,
  Monitor,
  Files,
  OfficeBuilding,
  User,
  DArrowLeft,
  DArrowRight,
  Menu
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑
const breadcrumbs = computed(() => {
  const crumbs = []
  if (route.path.includes('/knowledge/dashboard')) {
    crumbs.push({ title: '知识库仪表盘', path: '/admin/knowledge/dashboard' })
  } else if (route.path.includes('/knowledge/hierarchy')) {
    crumbs.push({ title: '法律层级管理', path: '/admin/knowledge/hierarchy' })
    if (route.params.level) {
      const levelNames = {
        xianfa: '宪法',
        falv: '法律',
        xingzhengfagui: '行政法规',
        difangxingfagui: '地方性法规',
        sifajieshi: '司法解释'
      }
      crumbs.push({ title: levelNames[route.params.level] || route.params.level })
    }
  } else if (route.path.includes('/knowledge/standards')) {
    crumbs.push({ title: '行业准则管理', path: '/admin/knowledge/standards' })
  } else if (route.path.includes('/knowledge/monitor')) {
    crumbs.push({ title: '向量监控', path: '/admin/knowledge/monitor' })
  } else if (route.path.includes('/laws')) {
    crumbs.push({ title: '法律文档管理', path: '/admin/laws' })
  } else if (route.path.includes('/companies')) {
    crumbs.push({ title: '企业管理', path: '/admin/companies' })
  } else if (route.path.includes('/users')) {
    crumbs.push({ title: '用户管理', path: '/admin/users' })
  }
  return crumbs
})

// 切换折叠
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.sidebar {
  background: #001529;
  transition: width 0.3s;
  position: relative;
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  background: #002140;
  color: #fff;
  gap: 12px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
}

.logo-icon {
  font-size: 24px;
}

.sidebar-menu {
  border: none;
  background: #001529;
}

.sidebar-menu ::v-deep(.el-menu-item),
.sidebar-menu ::v-deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.65);
}

.sidebar-menu ::v-deep(.el-menu-item:hover),
.sidebar-menu ::v-deep(.el-sub-menu__title:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-menu ::v-deep(.el-menu-item.is-active) {
  color: #fff;
  background: #1890ff !important;
}

.sidebar-menu ::v-deep(.el-sub-menu.is-opened .el-sub-menu__title) {
  background: rgba(255, 255, 255, 0.05) !important;
}

.sidebar-menu ::v-deep(.el-menu) {
  background: #000c17 !important;
}

.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  cursor: pointer;
  color: #fff;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.top-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}

.el-divider {
  margin: 12px 0;
  background: rgba(255, 255, 255, 0.1);
}
</style>
