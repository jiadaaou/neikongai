import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  
  // 解析 token 获取用户信息
  const parseToken = (tokenStr) => {
    if (!tokenStr) return null
    try {
      const payload = JSON.parse(atob(tokenStr.split('.')[1]))
      return {
        userId: payload.user_id,
        username: payload.sub,
        role: payload.role || null
      }
    } catch {
      return null
    }
  }
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const currentUser = computed(() => parseToken(token.value))
  const isSuperAdmin = computed(() => currentUser.value?.role === 'SUPER_ADMIN')
  const isCompanyAdmin = computed(() => currentUser.value?.role === 'COMPANY_ADMIN')
  const isCompanyUser = computed(() => currentUser.value?.role === 'COMPANY_USER' || currentUser.value?.role === 'COMPANY_ADMIN')
  
  // 登录
  const login = (tokenStr) => {
    token.value = tokenStr
    localStorage.setItem('token', tokenStr)
  }
  
  // 登出
  const logout = () => {
    token.value = ''
    localStorage.removeItem('token')
  }
  
  return {
    token,
    isLoggedIn,
    currentUser,
    isSuperAdmin,
    isCompanyAdmin,
    isCompanyUser,
    login,
    logout
  }
})
