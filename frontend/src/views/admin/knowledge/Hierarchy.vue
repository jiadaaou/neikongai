<template>
  <div class="hierarchy-page">
    <!-- 页面标题 -->
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>法律层级管理</h2>
          <p class="subtitle">管理各法律层级的文档和统计数据</p>
        </div>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          新建分类
        </el-button>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-top: 24px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="法律层级总数" :value="statistics.totalLevels">
            <template #prefix>
              <el-icon color="#1890ff"><FolderOpened /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">本月新增 3</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="文档总数" :value="statistics.totalDocs">
            <template #prefix>
              <el-icon color="#52c41a"><Document /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="info" size="small">较上月 +156</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="向量总数" :value="formatNumber(statistics.totalVectors)">
            <template #prefix>
              <el-icon color="#faad14"><DataLine /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="warning" size="small">+8.5%</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="最近更新" value="2天前">
            <template #prefix>
              <el-icon color="#722ed1"><Clock /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">正常</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <el-card style="margin-top: 24px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="法律层级">
          <el-select v-model="searchForm.level" placeholder="全部层级" clearable style="width: 180px;" @change="handleLevelChange">
            <el-option label="全部层级（汇总）" value="" />
            <el-option label="宪法" value="宪法" />
            <el-option label="法律" value="法律" />
            <el-option label="行政法规" value="行政法规" />
            <el-option label="地方性法规" value="地方性法规" />
            <el-option label="司法解释" value="司法解释" />
          </el-select>
        </el-form-item>
        <el-form-item label="文档状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 150px;">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索文档名称"
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

    <!-- 法律层级列表（卡片视图）-->
    <el-card style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>{{ currentLevelTitle }}（共 {{ filteredDocs.length }} 个文档）</span>
          <div>
            <el-button :icon="Upload" size="small" @click="showUploadDialog = true">上传文档</el-button>
            <el-button-group style="margin-left: 12px;">
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
        <el-col v-for="item in paginatedDocs" :key="item.id" :span="8" style="margin-bottom: 16px;">
          <el-card shadow="hover" class="doc-card">
            <div class="card-header-info">
              <el-tag :type="getLevelTagType(item.level)" size="small">
                {{ item.level }}
              </el-tag>
              <el-tag size="small" effect="plain">{{ item.category }}</el-tag>
            </div>
            <h3 class="doc-title">{{ item.name }}</h3>
            <p class="doc-code">编号：{{ item.code }}</p>
            <el-divider style="margin: 12px 0;" />
            <div class="card-footer-info">
              <div class="info-item">
                <el-icon><Document /></el-icon>
                <span>{{ item.chunks }} 分块</span>
              </div>
              <div class="info-item">
                <el-icon><DataLine /></el-icon>
                <span>{{ item.vectors }} 向量</span>
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
      <el-table v-else :data="paginatedDocs" style="width: 100%;">
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="文档名称" min-width="300">
          <template #default="{ row }">
            <div class="doc-name-cell">
              <el-icon color="#1890ff"><Document /></el-icon>
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="code">{{ row.code }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="法律层级" width="120">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="150">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chunks" label="分块数" width="100" align="center" />
        <el-table-column prop="vectors" label="向量数" width="100" align="center" />
        <el-table-column prop="size" label="文件大小" width="120" />
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
        :total="filteredDocs.length"
        :page-sizes="[12, 24, 48, 96]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 创建分类对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建法律分类"
      width="600px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="法律层级" required>
          <el-select v-model="formData.level" placeholder="请选择法律层级" style="width: 100%;">
            <el-option label="宪法" value="宪法" />
            <el-option label="法律" value="法律" />
            <el-option label="行政法规" value="行政法规" />
            <el-option label="地方性法规" value="地方性法规" />
            <el-option label="司法解释" value="司法解释" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类名称" required>
          <el-input v-model="formData.name" placeholder="如：刑法、民法等" />
        </el-form-item>
        <el-form-item label="分类编码">
          <el-input v-model="formData.code" placeholder="请输入分类编码" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传法律文档" width="600px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="法律层级" required>
          <el-select v-model="uploadForm.level" placeholder="请选择法律层级" style="width: 100%;">
            <el-option label="宪法" value="宪法" />
            <el-option label="法律" value="法律" />
            <el-option label="行政法规" value="行政法规" />
            <el-option label="地方性法规" value="地方性法规" />
            <el-option label="司法解释" value="司法解释" />
          </el-select>
        </el-form-item>
        <el-form-item label="文档分类">
          <el-input v-model="uploadForm.category" placeholder="如：刑法、民法等" />
        </el-form-item>
        <el-form-item label="文档上传">
          <el-upload
            drag
            multiple
            :auto-upload="false"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、TXT 格式，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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
  FolderOpened,
  DataLine,
  Clock,
  UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 统计数据
const statistics = ref({
  totalLevels: 5,
  totalDocs: 2569,
  totalVectors: 123456,
  lastUpdate: '2天前'
})

// 搜索表单
const searchForm = ref({
  level: '',
  status: '',
  keyword: ''
})

// 视图模式
const viewMode = ref('card')

// 所有文档数据（模拟数据）
const allDocs = ref([
  // 宪法
  { id: 1, name: '中华人民共和国宪法', code: 'XIANFA-2018', level: '宪法', category: '宪法正文', chunks: 45, vectors: 1234, size: '2.3 MB', updateTime: '2024-03-01 10:23', status: 'published' },
  { id: 2, name: '宪法修正案（2018）', code: 'XIANFA-XZ-2018', level: '宪法', category: '宪法修正案', chunks: 10, vectors: 234, size: '456 KB', updateTime: '2024-02-28 14:56', status: 'published' },
  { id: 3, name: '全国人民代表大会组织法', code: 'XIANFA-ZZF-001', level: '宪法', category: '宪法相关法', chunks: 20, vectors: 544, size: '1.1 MB', updateTime: '2024-02-25 09:12', status: 'published' },
  
  // 法律
  { id: 11, name: '中华人民共和国刑法（2020修正）', code: 'FL-XF-2020', level: '法律', category: '刑法', chunks: 156, vectors: 5678, size: '5.6 MB', updateTime: '2024-03-02 11:34', status: 'published' },
  { id: 12, name: '中华人民共和国民法典', code: 'FL-MFD-2020', level: '法律', category: '民法', chunks: 567, vectors: 23456, size: '12.3 MB', updateTime: '2024-03-01 15:45', status: 'published' },
  { id: 13, name: '中华人民共和国行政诉讼法', code: 'FL-XZSSF-2017', level: '法律', category: '行政法', chunks: 89, vectors: 3456, size: '2.1 MB', updateTime: '2024-02-29 09:23', status: 'published' },
  { id: 14, name: '中华人民共和国劳动合同法', code: 'FL-LDHTF-2012', level: '法律', category: '社会法', chunks: 123, vectors: 4567, size: '2.8 MB', updateTime: '2024-02-28 16:12', status: 'published' },
  { id: 15, name: '中华人民共和国公司法', code: 'FL-GSF-2018', level: '法律', category: '经济法', chunks: 178, vectors: 6789, size: '3.5 MB', updateTime: '2024-02-27 10:56', status: 'published' },
  
  // 行政法规
  { id: 21, name: '国务院关于环境保护的若干规定', code: 'XZFG-HJBH-001', level: '行政法规', category: '环境保护', chunks: 67, vectors: 2345, size: '1.5 MB', updateTime: '2024-03-03 14:23', status: 'published' },
  { id: 22, name: '建设工程质量管理条例', code: 'XZFG-JSGC-001', level: '行政法规', category: '工程建设', chunks: 89, vectors: 3456, size: '1.9 MB', updateTime: '2024-03-02 09:45', status: 'published' },
  { id: 23, name: '安全生产许可证条例', code: 'XZFG-AQSC-001', level: '行政法规', category: '安全生产', chunks: 45, vectors: 1789, size: '890 KB', updateTime: '2024-03-01 11:12', status: 'published' },
  
  // 地方性法规
  { id: 31, name: '北京市物业管理条例', code: 'DFXFG-BJ-WY-001', level: '地方性法规', category: '北京市', chunks: 78, vectors: 2890, size: '1.6 MB', updateTime: '2024-03-04 08:34', status: 'published' },
  { id: 32, name: '上海市环境保护条例', code: 'DFXFG-SH-HJBH-001', level: '地方性法规', category: '上海市', chunks: 92, vectors: 3234, size: '2.0 MB', updateTime: '2024-03-03 15:23', status: 'published' },
  { id: 33, name: '广东省安全生产条例', code: 'DFXFG-GD-AQSC-001', level: '地方性法规', category: '广东省', chunks: 67, vectors: 2567, size: '1.4 MB', updateTime: '2024-03-02 10:45', status: 'published' },
  
  // 司法解释
  { id: 41, name: '最高人民法院关于审理劳动争议案件适用法律问题的解释', code: 'SFJS-ZGF-LD-001', level: '司法解释', category: '劳动争议', chunks: 56, vectors: 2123, size: '1.1 MB', updateTime: '2024-03-04 09:12', status: 'published' },
  { id: 42, name: '最高人民法院关于审理买卖合同纠纷案件适用法律问题的解释', code: 'SFJS-ZGF-MM-001', level: '司法解释', category: '合同纠纷', chunks: 78, vectors: 2890, size: '1.5 MB', updateTime: '2024-03-03 11:34', status: 'published' },
  { id: 43, name: '最高人民检察院关于渎职侵权犯罪案件立案标准的规定', code: 'SFJS-ZGJ-DZ-001', level: '司法解释', category: '刑事案件', chunks: 34, vectors: 1456, size: '780 KB', updateTime: '2024-03-02 14:56', status: 'published' }
])

// 过滤后的文档
const filteredDocs = computed(() => {
  let docs = allDocs.value
  
  // 按层级筛选
  if (searchForm.value.level) {
    docs = docs.filter(doc => doc.level === searchForm.value.level)
  }
  
  // 按状态筛选
  if (searchForm.value.status) {
    docs = docs.filter(doc => doc.status === searchForm.value.status)
  }
  
  // 按关键词筛选
  if (searchForm.value.keyword) {
    docs = docs.filter(doc => 
      doc.name.includes(searchForm.value.keyword) ||
      doc.code.includes(searchForm.value.keyword)
    )
  }
  
  return docs
})

// 当前显示的标题
const currentLevelTitle = computed(() => {
  return searchForm.value.level ? `${searchForm.value.level}层级文档` : '全部法律文档'
})

// 分页
const currentPage = ref(1)
const pageSize = ref(12)

const paginatedDocs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDocs.value.slice(start, end)
})

// 对话框
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)

const formData = ref({
  level: '',
  name: '',
  code: '',
  sort: 0,
  description: ''
})

const uploadForm = ref({
  level: '',
  category: ''
})

// 方法
const formatNumber = (num) => {
  return num.toLocaleString()
}

const handleLevelChange = () => {
  currentPage.value = 1
}

const handleSearch = () => {
  currentPage.value = 1
  ElMessage.success('搜索完成')
}

const handleReset = () => {
  searchForm.value = {
    level: '',
    status: '',
    keyword: ''
  }
  currentPage.value = 1
}

const handleView = (row) => {
  ElMessage.info(`查看文档：${row.name}（演示）`)
}

const handleEdit = (row) => {
  ElMessage.info(`编辑文档：${row.name}（演示）`)
}

const handleDownload = (row) => {
  ElMessage.success(`下载：${row.name}（演示）`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除文档"${row.name}"吗？`,
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
  ElMessage.success('创建成功（演示）')
  showCreateDialog.value = false
}

const handleUpload = () => {
  ElMessage.success('上传成功（演示）')
  showUploadDialog.value = false
}

const getLevelTagType = (level) => {
  const types = {
    '宪法': 'danger',
    '法律': 'warning',
    '行政法规': 'success',
    '地方性法规': 'info',
    '司法解释': 'primary'
  }
  return types[level] || 'info'
}
</script>

<style scoped>
.hierarchy-page {
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

.stat-trend {
  margin-top: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-card {
  height: 260px;
  display: flex;
  flex-direction: column;
}

.doc-card ::v-deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.doc-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 44px;
}

.doc-code {
  margin: 8px 0;
  font-size: 12px;
  color: #999;
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
  margin-top: auto;
}

.doc-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-name-cell .name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.doc-name-cell .code {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
