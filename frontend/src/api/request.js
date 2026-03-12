import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 600000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token 并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误：', error)
    
    let message = '请求失败'
    
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        message = '未登录或登录已过期，请重新登录'
        // 清除过期 token
        localStorage.removeItem('token')
        // 可以跳转到登录页
        // window.location.href = '/login'
      } else if (status === 403) {
        message = '没有权限访问'
      } else if (status === 404) {
        message = '请求的资源不存在'
      } else if (status === 500) {
        message = '服务器错误'
      } else if (data && data.detail) {
        message = data.detail
      }
    } else if (error.request) {
      message = '网络错误，请检查网络连接'
    }
    
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export default request
