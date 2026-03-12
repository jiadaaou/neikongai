import { useUserStore } from '@/stores/user'

export default async function request(url, options = {}) {
  const userStore = useUserStore()
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }
  
  // 添加认证 token
  if (userStore.token) {
    headers['Authorization'] = `Bearer ${userStore.token}`
  }
  
  const response = await fetch(url, {
    ...options,
    headers
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || 'Request failed')
  }
  
  return response.json()
}
