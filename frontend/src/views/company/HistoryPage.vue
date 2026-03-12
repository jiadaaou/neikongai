<template>
  <div class="history-page">
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters">
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索问题或答案"
            :prefix-icon="Search"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="history-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Clock /></el-icon>
            <span>查询历史</span>
            <el-tag size="small" type="info">共 {{ total }} 条记录</el-tag>
          </div>
          <el-button
            v-if="historyList.length > 0"
            :icon="Delete"
            type="danger"
            plain
            size="small"
            @click="handleClearAll"
          >
            清空历史
          </el-button>
        </div>
      </template>

      <div v-if="historyList.length === 0" class="empty-state">
        <el-icon :size="64" color="#ddd"><DocumentCopy /></el-icon>
        <h3>暂无查询记录</h3>
        <p>您还没有进行过法律咨询</p>
        <el-button type="primary" @click="$router.push('/company/chat')">
          开始咨询
        </el-button>
      </div>

      <div v-else class="history-list">
        <div
          v-for="item in historyList"
          :key="item.id"
          class="history-item"
        >
          <div class="history-header">
            <div class="history-time">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(item.created_at) }}</span>
            </div>
            <el-button
              :icon="Delete"
              link
              type="danger"
              size="small"
              @click="handleDelete(item.id)"
            >
              删除
            </el-button>
          </div>

          <div class="history-question">
            <div class="question-label">
              <el-icon color="#6c63ff"><User /></el-icon>
              <span>问题</span>
            </div>
            <div class="question-content">{{ item.question }}</div>
          </div>

          <div class="history-answer">
            <div class="answer-label">
              <el-icon color="#22c55e"><Cpu /></el-icon>
              <span>回答</span>
            </div>
            <div class="answer-content" v-html="formatMessage(item.answer)"></div>
          </div>

          <div class="history-actions">
            <el-button
              :icon="ChatDotRound"
              size="small"
              @click="handleContinue(item.question)"
            >
              继续对话
            </el-button>
            <el-button
              :icon="CopyDocument"
              size="small"
              @click="handleCopy(item)"
            >
              复制内容
            </el-button>
          </div>
        </div>
      </div>

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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Clock, Delete, DocumentCopy, User, Cpu, ChatDotRound, CopyDocument } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const filters = ref({
  keyword: '',
  dateRange: null
})

const formatMessage = (text) => {
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 1分钟内
  if (diff < 60000) {
    return '刚刚'
  }
  // 1小时内
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 今天
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }
  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }
  // 其他
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (filters.value.keyword) {
      params.append('keyword', filters.value.keyword)
    }

    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.append('start_date', filters.value.dateRange[0].toISOString())
      params.append('end_date', filters.value.dateRange[1].toISOString())
    }

    const response = await fetch(`/api/chat/history?${params}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '获取历史记录失败')
    }

    historyList.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error(error.message || '获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchHistory()
}

const handleReset = () => {
  filters.value = {
    keyword: '',
    dateRange: null
  }
  currentPage.value = 1
  fetchHistory()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchHistory()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchHistory()
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await fetch(`/api/chat/history/${id}`, {
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
    fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await fetch('/api/chat/history/clear', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '清空失败')
    }

    ElMessage.success('已清空所有历史记录')
    fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '清空失败')
    }
  }
}

const handleContinue = (question) => {
  router.push({
    path: '/company/chat',
    query: { q: question }
  })
}

const handleCopy = async (item) => {
  const text = `问题：${item.question}\n\n回答：${item.answer}`
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filter-card,
.history-card {
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #999;
}

.empty-state h3 {
  margin: 1rem 0 0.5rem;
  color: #666;
}

.empty-state p {
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-item {
  padding: 1.5rem;
  background: #f5f7fa;
  border-radius: 12px;
  transition: all 0.3s;
}

.history-item:hover {
  background: #eef1f6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.history-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #999;
  font-size: 0.875rem;
}

.history-question,
.history-answer {
  margin-bottom: 1rem;
}

.question-label,
.answer-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
  color: #1a1a1a;
}

.question-content,
.answer-content {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  line-height: 1.6;
  color: #333;
}

.answer-content {
  border-left: 3px solid var(--success);
}

.history-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.pagination {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}
</style>
