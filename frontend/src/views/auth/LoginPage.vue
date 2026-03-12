<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <div class="navbar-brand">
            <svg class="logo-icon" width="40" height="40" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="#6c63ff"/>
              <circle cx="16" cy="16" r="6" stroke="#fff" stroke-width="2"/>
              <circle cx="16" cy="16" r="2" fill="#fff"/>
              <line x1="16" y1="4" x2="16" y2="10" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <line x1="16" y1="22" x2="16" y2="28" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <line x1="4" y1="16" x2="10" y2="16" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <line x1="22" y1="16" x2="28" y2="16" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h2>登录内控AI</h2>
          <p>智能法律合规管理平台</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" class="login-form" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
              show-password
            />
          </el-form-item>
          
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form>

        <div class="login-footer">
          <router-link to="/register" class="link">企业注册</router-link>
          <span class="divider">|</span>
          <router-link to="/" class="link">返回首页</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', form.username)
    formData.append('password', form.password)
    
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '登录失败')
    }
    
    // 保存 token
    userStore.login(data.access_token)
    
    ElMessage.success('登录成功')
    
    // 根据角色跳转
    const user = userStore.currentUser
    let redirect = route.query.redirect
    
    if (!redirect) {
      redirect = user.role === 'SUPER_ADMIN' ? '/admin/laws' : '/company/chat'
    }
    
    router.push(redirect)
  } catch (error) {
    ElMessage.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-box {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.navbar-brand {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.logo-icon {
  display: block;
}

.login-header h2 {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.login-button {
  width: 100%;
  margin-top: 0.5rem;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.link:hover {
  opacity: 0.8;
}

.divider {
  margin: 0 1rem;
  color: #ddd;
}
</style>
