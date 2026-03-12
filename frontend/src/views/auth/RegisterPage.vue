<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-box">
        <div class="register-header">
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
          <h2>企业注册</h2>
          <p>创建您的企业账号，开始合规之旅</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" class="register-form" label-position="top">
          <el-form-item label="企业名称" prop="company_name">
            <el-input
              v-model="form.company_name"
              placeholder="请输入企业名称"
              size="large"
              :prefix-icon="OfficeBuilding"
            />
          </el-form-item>

          <el-form-item label="统一社会信用代码" prop="credit_code">
            <el-input
              v-model="form.credit_code"
              placeholder="请输入统一社会信用代码"
              size="large"
              :prefix-icon="Tickets"
            />
          </el-form-item>

          <el-form-item label="联系人姓名" prop="contact_name">
            <el-input
              v-model="form.contact_name"
              placeholder="请输入联系人姓名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="联系电话" prop="phone">
            <el-input
              v-model="form.phone"
              placeholder="请输入联系电话"
              size="large"
              :prefix-icon="Phone"
            />
          </el-form-item>

          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="设置登录用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="设置登录密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirm_password">
            <el-input
              v-model="form.confirm_password"
              type="password"
              placeholder="再次输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="form.agree">
              我已阅读并同意
              <el-link type="primary" :underline="false">《用户协议》</el-link>
              和
              <el-link type="primary" :underline="false">《隐私政策》</el-link>
            </el-checkbox>
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="register-button"
            :disabled="!form.agree"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form>

        <div class="register-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Tickets, User, Phone, Lock } from '@element-plus/icons-vue'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  company_name: '',
  credit_code: '',
  contact_name: '',
  phone: '',
  username: '',
  password: '',
  confirm_password: '',
  agree: false
})

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
  credit_code: [
    { required: true, message: '请输入统一社会信用代码', trigger: 'blur' },
    { pattern: /^[0-9A-Z]{18}$/, message: '请输入正确的统一社会信用代码', trigger: 'blur' }
  ],
  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (!form.agree) {
    ElMessage.warning('请先阅读并同意用户协议和隐私政策')
    return
  }

  loading.value = true

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_name: form.company_name,
        credit_code: form.credit_code,
        contact_name: form.contact_name,
        phone: form.phone,
        username: form.username,
        password: form.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '注册失败')
    }

    ElMessage.success('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.register-container {
  width: 100%;
  max-width: 550px;
}

.register-box {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.register-header {
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

.register-header h2 {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.register-header p {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

.register-form {
  margin-bottom: 1.5rem;
}

.register-button {
  width: 100%;
  margin-top: 0.5rem;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
}

.register-footer {
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.5rem;
  transition: opacity 0.3s;
}

.link:hover {
  opacity: 0.8;
}
</style>
