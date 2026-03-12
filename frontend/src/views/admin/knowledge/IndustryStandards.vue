<template>
  <div class="standards-page">
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>行业准则管理</h2>
          <p class="subtitle">管理各行业的合规准则和标准文档</p>
        </div>
        <div class="header-actions">
          <el-button :icon="Upload" @click="showUploadDialog = true">
            批量导入
          </el-button>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建准则
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-top: 24px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="准则总数" :value="statistics.total">
            <template #prefix>
              <el-icon color="#1890ff"><Document /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">本月新增 12</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="覆盖行业" :value="statistics.industries">
            <template #prefix>
              <el-icon color="#52c41a"><OfficeBuilding /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="info" size="small">较上月 +2</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待审核" :value="statistics.pending">
            <template #prefix>
              <el-icon color="#faad14"><Warning /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="warning" size="small">需处理</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="引用次数" :value="statistics.references">
            <template #prefix>
              <el-icon color="#722ed1"><Link /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">+15.3%</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <el-card style="margin-top: 24px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="行业分类">
          <el-select v-model="searchForm.industry" placeholder="全部行业" clearable style="width: 180px;">
            <el-option label="建筑工程" value="construction" />
            <el-option label="财务会计" value="finance" />
            <el-option label="人力资源" value="hr" />
            <el-option label="安全管理" value="safety" />
            <el-option label="更多行业" value="more" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 150px;">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索准则名称、编号"
            :prefix-icon="Search"
            clearable
            style="width: 250px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 准则列表 -->
    <el-card style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>行业准则列表（共 {{ total }} 条）</span>
          <div>
            <el-button-group>
              <el-button :icon="Grid" :type="viewMode === 'card' ? 'primary' : ''" @click="viewMode = 'card'">
                卡片
              </el-button>
              <el-button :icon="List" :type="viewMode === 'table' ? 'primary' : ''" @click="viewMode = 'table'">
                列表
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 卡片视图 -->
      <el-row v-if="viewMode === 'card'" :gutter="16">
        <el-col v-for="item in standardsList" :key="item.id" :span="8" style="margin-bottom: 16px;">
          <el-card shadow="hover" class="standard-card">
            <div class="card-header-info">
              <el-tag :type="getStatusType(item.status)" size="small">
                {{ getStatusText(item.status) }}
              </el-tag>
              <el-tag size="small" effect="plain">{{ item.industry }}</el-tag>
            </div>
            <h3 class="standard-title">{{ item.name }}</h3>
            <p class="standard-code">编号：{{ item.code }}</p>
            <p class="standard-desc">{{ item.description }}</p>
            <el-divider style="margin: 12px 0;" />
            <div class="card-footer-info">
              <div class="info-item">
                <el-icon><Document /></el-icon>
                <span>{{ item.chapters }} 章节</span>
              </div>
              <div class="info-item">
                <el-icon><View /></el-icon>
                <span>{{ item.views }} 查看</span>
              </div>
              <div class="info-item">
                <el-icon><Clock /></el-icon>
                <span>{{ item.updateTime }}</span>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="primary" link :icon="View" @click="handleView(item)">查看</el-button>
              <el-button type="primary" link :icon="Edit" @click="handleEdit(item)">编辑</el-button>
              <el-button type="primary" link :icon="Download" @click="handleDownload(item)">下载</el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(item)">删除</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 表格视图 -->
      <el-table v-else :data="standardsList" style="width: 100%;">
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="准则名称" min-width="250">
          <template #default="{ row }">
            <div class="standard-name-cell">
              <el-icon color="#1890ff"><Document /></el-icon>
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="code">{{ row.code }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="industry" label="行业" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.industry }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chapters" label="章节数" width="100" align="center" />
        <el-table-column prop="views" label="查看次数" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link :icon="Download" @click="handleDownload(row)">下载</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingItem ? '编辑准则' : '创建准则'"
      width="800px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="准则名称" required>
          <el-input v-model="formData.name" placeholder="请输入准则名称" />
        </el-form-item>
        <el-form-item label="准则编号" required>
          <el-input v-model="formData.code" placeholder="如：GB/T 19001-2016" />
        </el-form-item>
        <el-form-item label="所属行业" required>
          <el-select v-model="formData.industry" placeholder="请选择行业" style="width: 100%;">
            <el-option label="建筑工程" value="construction" />
            <el-option label="财务会计" value="finance" />
            <el-option label="人力资源" value="hr" />
            <el-option label="安全管理" value="safety" />
          </el-select>
        </el-form-item>
        <el-form-item label="准则描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入准则描述"
          />
        </el-form-item>
        <el-form-item label="文档上传">
          <el-upload
            drag
            :auto-upload="false"
            accept=".pdf,.doc,.docx"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="pending">待审核</el-radio>
            <el-radio label="published">发布</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="批量导入准则" width="600px">
      <el-upload
        drag
        multiple
        :auto-upload="false"
        accept=".pdf,.doc,.docx,.zip"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持批量上传 PDF、Word 格式，或上传 ZIP 压缩包
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchUpload">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Plus,
  Edit,
  Delete,
  Search,
  Upload,
  View,
  Download,
  Document,
  Refresh,
  Grid,
  List,
  OfficeBuilding,
  Warning,
  Link,
  Clock,
  UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 统计数据
const statistics = ref({
  total: 156,
  industries: 28,
  pending: 12,
  references: 3456
})

// 搜索表单
const searchForm = ref({
  industry: '',
  status: '',
  keyword: ''
})

// 视图模式
const viewMode = ref('table')

// 准则列表（模拟数据）
const standardsList = ref([
  {
    id: 1,
    name: '建筑工程施工质量验收统一标准',
    code: 'GB 50300-2013',
    industry: '建筑工程',
    chapters: 12,
    views: 1234,
    status: 'published',
    description: '规定了建筑工程施工质量验收的统一准则和基本方法',
    updateTime: '2024-03-01 10:23'
  },
  {
    id: 2,
    name: '财务会计准则第1号-存货',
    code: 'CAS 1',
    industry: '财务会计',
    chapters: 8,
    views: 2345,
    status: 'published',
    description: '规范企业存货的确认、计量和相关信息的披露',
    updateTime: '2024-02-28 14:56'
  },
  {
    id: 3,
    name: '人力资源管理体系认证标准',
    code: 'ISO 30414',
    industry: '人力资源',
    chapters: 15,
    views: 987,
    status: 'pending',
    description: '人力资源管理的国际标准和最佳实践',
    updateTime: '2024-02-25 09:12'
  },
  {
    id: 4,
    name: '安全生产标准化基本规范',
    code: 'GB/T 33000-2016',
    industry: '安全管理',
    chapters: 20,
    views: 1567,
    status: 'published',
    description: '规定了企业安全生产标准化建设的基本要求',
    updateTime: '2024-02-20 16:45'
  },
  {
    id: 5,
    name: '更多行业标准示例',
    code: 'GB/T 12345-2020',
    industry: '更多行业',
    chapters: 10,
    views: 678,
    status: 'draft',
    description: '这是一个示例标准，用于演示UI效果',
    updateTime: '2024-02-15 11:23'
  }
])

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(156)

// 对话框
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const editingItem = ref(null)

const formData = ref({
  name: '',
  code: '',
  industry: '',
  description: '',
  status: 'draft'
})

// 方法
const handleSearch = () => {
  ElMessage.success('搜索功能（演示）')
}

const handleReset = () => {
  searchForm.value = {
    industry: '',
    status: '',
    keyword: ''
  }
}

const handleView = (row) => {
  ElMessage.info(`查看准则：${row.name}（演示）`)
}

const handleEdit = (row) => {
  editingItem.value = row
  formData.value = { ...row }
  showCreateDialog.value = true
}

const handleDownload = (row) => {
  ElMessage.success(`下载：${row.name}（演示）`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除准则"${row.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('删除成功（演示）')
  })
}

const handleSubmit = () => {
  ElMessage.success(editingItem.value ? '编辑成功（演示）' : '创建成功（演示）')
  showCreateDialog.value = false
}

const handleBatchUpload = () => {
  ElMessage.success('批量导入成功（演示）')
  showUploadDialog.value = false
}

const getStatusType = (status) => {
  const types = {
    published: 'success',
    draft: 'info',
    pending: 'warning',
    archived: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    published: '已发布',
    draft: '草稿',
    pending: '待审核',
    archived: '已归档'
  }
  return texts[status] || status
}
</script>

<style scoped>
.standards-page {
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #666;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stat-trend {
  margin-top: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.standard-card {
  height: 280px;
  display: flex;
  flex-direction: column;
}

.standard-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.standard-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.standard-code {
  margin: 8px 0;
  font-size: 12px;
  color: #999;
}

.standard-desc {
  flex: 1;
  margin: 0;
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-footer-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.card-actions {
  display: flex;
  justify-content: space-around;
}

.standard-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.standard-name-cell .name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.standard-name-cell .code {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
