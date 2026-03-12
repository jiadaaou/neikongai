<template>
  <div class="users-page">
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters">
        <el-form-item label="用户名">
          <el-input
            v-model="filters.username"
            placeholder="搜索用户名"
            :prefix-icon="Search"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部角色" clearable @change="handleSearch">
            <el-option label="超级管理员" value="SUPER_ADMIN" />
            <el-option label="企业管理员" value="COMPANY_ADMIN" />
            <el-option label="企业用户" value="COMPANY_USER" />
          </el-select>
        </el-form-item>
        <el-form-item label="企业">
          <el-select
            v-model="filters.company_id"
            placeholder="全部企业"
            clearable
            filterable
            @change="handleSearch"
            style="width: 200px"
          >
            <el-option
              v-for="company in companyList"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><User /></el-icon>
            <span>用户列表</span>
            <el-tag size="small" type="info">共 {{ total }} 个用户</el-tag>
          </div>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            添加用户
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="所属企业" min-width="200">
          <template #default="{ row }">
            {{ row.company_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login ? formatTime(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="warning"
              link
              size="small"
              :icon="Key"
              @click="handleResetPassword(row)"
            >
              重置密码
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        class="pagination"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!form.id">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码（不少于6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="超级管理员" value="SUPER_ADMIN" />
            <el-option label="企业管理员" value="COMPANY_ADMIN" />
            <el-option label="企业用户" value="COMPANY_USER" />
          </el-select>
        </el-form-item>
        <el-form-item
          label="所属企业"
          prop="company_id"
          v-if="form.role !== 'SUPER_ADMIN'"
        >
          <el-select
            v-model="form.company_id"
            placeholder="请选择企业"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="company in companyList"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="用户详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ viewData.username }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="getRoleType(viewData.role)">
            {{ getRoleText(viewData.role) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="所属企业">
          {{ viewData.company_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.is_active ? 'success' : 'danger'">
            {{ viewData.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(viewData.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatTime(viewData.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后登录">
          {{ viewData.last_login ? formatTime(viewData.last_login) : '从未登录' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, User, Plus, View, Edit, Delete, Key } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const formRef = ref(null)

const tableData = ref([])
const companyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  username: '',
  role: '',
  company_id: null
})

const form = reactive({
  id: null,
  username: '',
  password: '',
  role: '',
  company_id: null,
  is_active: true
})

const viewData = ref({})

const dialogTitle = computed(() => {
  return form.id ? '编辑用户' : '添加用户'
})

const validatePassword = (rule, value, callback) => {
  if (!form.id && !value) {
    callback(new Error('请输入密码'))
  } else if (!form.id && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  company_id: [
    {
      required: true,
      message: '请选择所属企业',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (form.role !== 'SUPER_ADMIN' && !value) {
          callback(new Error('请选择所属企业'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 监听角色变化，清空企业选择
watch(() => form.role, (newRole) => {
  if (newRole === 'SUPER_ADMIN') {
    form.company_id = null
  }
})

const getRoleText = (role) => {
  const roles = {
    'SUPER_ADMIN': '超级管理员',
    'COMPANY_ADMIN': '企业管理员',
    'COMPANY_USER': '企业用户'
  }
  return roles[role] || role
}

const getRoleType = (role) => {
  const types = {
    'SUPER_ADMIN': 'danger',
    'COMPANY_ADMIN': 'warning',
    'COMPANY_USER': 'info'
  }
  return types[role] || 'info'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

const fetchCompanies = async () => {
  try {
    const response = await fetch('/api/admin/companies?page=1&page_size=1000', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })

    const data = await response.json()

    if (response.ok) {
      companyList.value = data.items || []
    }
  } catch (error) {
    console.error('获取企业列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (filters.username) {
      params.append('username', filters.username)
    }
    if (filters.role) {
      params.append('role', filters.role)
    }
    if (filters.company_id) {
      params.append('company_id', filters.company_id)
    }

    const response = await fetch(`/api/admin/users?${params}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '获取用户列表失败')
    }

    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  filters.username = ''
  filters.role = ''
  filters.company_id = null
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

const handleAdd = () => {
  dialogVisible.value = true
}

const handleView = (row) => {
  viewData.value = { ...row }
  viewDialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    username: row.username,
    password: '',
    role: row.role,
    company_id: row.company_id,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

const handleResetPassword = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码（不少于6位）', '重置密码', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'password',
      inputPattern: /.{6,}/,
      inputErrorMessage: '密码长度不能少于6位'
    })

    const response = await fetch(`/api/admin/users/${row.id}/reset-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ new_password: value })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '重置密码失败')
    }

    ElMessage.success('密码重置成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '重置密码失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })

    const response = await fetch(`/api/admin/users/${row.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '删除失败')
    }

    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true

  try {
    const url = form.id
      ? `/api/admin/users/${form.id}`
      : '/api/admin/users'

    const body = {
      username: form.username,
      role: form.role,
      company_id: form.role === 'SUPER_ADMIN' ? null : form.company_id,
      is_active: form.is_active
    }

    if (!form.id) {
      body.password = form.password
    }

    const response = await fetch(url, {
      method: form.id ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '操作失败')
    }

    ElMessage.success(form.id ? '更新成功' : '添加成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    role: '',
    company_id: null,
    is_active: true
  })
  formRef.value?.clearValidate()
}

onMounted(() => {
  fetchCompanies()
  fetchData()
})
</script>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filter-card,
.table-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.pagination {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
}
</style>
