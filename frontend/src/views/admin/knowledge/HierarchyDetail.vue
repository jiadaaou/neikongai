<template>
  <div class="hierarchy-detail-page">
    <!-- 页面标题 -->
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>{{ levelTitle }}</h2>
          <p class="subtitle">{{ levelDescription }}</p>
        </div>
        <el-button type="primary" :icon="Upload" @click="showUploadDialog = true">
          上传文档
        </el-button>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-top: 24px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="`${levelTitle}文档总数`" :value="statistics.totalDocs">
            <template #prefix>
              <el-icon color="#1890ff"><Document /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">本月新增 {{ statistics.newDocs }}</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="分块总数" :value="statistics.totalChunks">
            <template #prefix>
              <el-icon color="#52c41a"><Grid /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="info" size="small">平均 {{ statistics.avgChunks }} 块/文档</el-tag>
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
            <el-tag type="warning" size="small">+{{ statistics.vectorGrowth }}%</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="查询次数（本月）" :value="formatNumber(statistics.queryCount)">
            <template #prefix>
              <el-icon color="#722ed1"><Search /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-trend">
            <el-tag type="success" size="small">+{{ statistics.queryGrowth }}%</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和筛选 -->
    <el-card style="margin-top: 24px;">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="keyword"
            placeholder="搜索文档名称、编号"
            :prefix-icon="Search"
            clearable
            style="width: 300px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search">搜索</el-button>
          <el-button :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文档列表 -->
    <el-card style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>文档列表（共 {{ documents.length }} 个）</span>
        </div>
      </template>

      <el-table :data="documents" style="width: 100%;">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="文档名称" min-width="350">
          <template #default="{ row }">
            <div class="doc-name-cell">
              <el-icon color="#1890ff" :size="20"><Document /></el-icon>
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="code">编号：{{ row.code }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="150">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chunks" label="分块数" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.chunks }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vectors" label="向量数" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.vectors }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="文件大小" width="120" />
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link :icon="Download" @click="handleDownload(row)">下载</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传法律文档" width="600px">
      <el-form :model="uploadForm" label-width="100px">
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
import { useRoute } from 'vue-router'
import {
  Upload,
  Document,
  Grid,
  DataLine,
  Search,
  Refresh,
  View,
  Download,
  Delete,
  UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()

// 层级配置
const levelConfig = {
  xianfa: {
    title: '宪法',
    description: '国家的根本法，具有最高的法律效力',
    docs: [
      { id: 1, name: '中华人民共和国宪法', code: 'XIANFA-2018', category: '宪法正文', chunks: 45, vectors: 1234, size: '2.3 MB', updateTime: '2024-03-01 10:23' },
      { id: 2, name: '宪法修正案（2018）', code: 'XIANFA-XZ-2018', category: '宪法修正案', chunks: 10, vectors: 234, size: '456 KB', updateTime: '2024-02-28 14:56' },
      { id: 3, name: '全国人民代表大会组织法', code: 'XIANFA-ZZF-001', category: '宪法相关法', chunks: 20, vectors: 544, size: '1.1 MB', updateTime: '2024-02-25 09:12' }
    ]
  },
  falv: {
    title: '法律',
    description: '由全国人民代表大会及其常务委员会制定的规范性文件',
    docs: [
      { id: 11, name: '中华人民共和国刑法（2020修正）', code: 'FL-XF-2020', category: '刑法', chunks: 156, vectors: 5678, size: '5.6 MB', updateTime: '2024-03-02 11:34' },
      { id: 12, name: '中华人民共和国民法典', code: 'FL-MFD-2020', category: '民法', chunks: 567, vectors: 23456, size: '12.3 MB', updateTime: '2024-03-01 15:45' },
      { id: 13, name: '中华人民共和国行政诉讼法', code: 'FL-XZSSF-2017', category: '行政法', chunks: 89, vectors: 3456, size: '2.1 MB', updateTime: '2024-02-29 09:23' },
      { id: 14, name: '中华人民共和国劳动合同法', code: 'FL-LDHTF-2012', category: '社会法', chunks: 123, vectors: 4567, size: '2.8 MB', updateTime: '2024-02-28 16:12' },
      { id: 15, name: '中华人民共和国公司法', code: 'FL-GSF-2018', category: '经济法', chunks: 178, vectors: 6789, size: '3.5 MB', updateTime: '2024-02-27 10:56' }
    ]
  },
  xingzhengfagui: {
    title: '行政法规',
    description: '由国务院制定的规范性文件',
    docs: [
      { id: 21, name: '国务院关于环境保护的若干规定', code: 'XZFG-HJBH-001', category: '环境保护', chunks: 67, vectors: 2345, size: '1.5 MB', updateTime: '2024-03-03 14:23' },
      { id: 22, name: '建设工程质量管理条例', code: 'XZFG-JSGC-001', category: '工程建设', chunks: 89, vectors: 3456, size: '1.9 MB', updateTime: '2024-03-02 09:45' },
      { id: 23, name: '安全生产许可证条例', code: 'XZFG-AQSC-001', category: '安全生产', chunks: 45, vectors: 1789, size: '890 KB', updateTime: '2024-03-01 11:12' }
    ]
  },
  difangxingfagui: {
    title: '地方性法规',
    description: '由地方人民代表大会及其常务委员会制定的规范性文件',
    docs: [
      { id: 31, name: '北京市物业管理条例', code: 'DFXFG-BJ-WY-001', category: '北京市', chunks: 78, vectors: 2890, size: '1.6 MB', updateTime: '2024-03-04 08:34' },
      { id: 32, name: '上海市环境保护条例', code: 'DFXFG-SH-HJBH-001', category: '上海市', chunks: 92, vectors: 3234, size: '2.0 MB', updateTime: '2024-03-03 15:23' },
      { id: 33, name: '广东省安全生产条例', code: 'DFXFG-GD-AQSC-001', category: '广东省', chunks: 67, vectors: 2567, size: '1.4 MB', updateTime: '2024-03-02 10:45' }
    ]
  },
  sifajieshi: {
    title: '司法解释',
    description: '由最高人民法院、最高人民检察院作出的具体应用法律的解释',
    docs: [
      { id: 41, name: '最高人民法院关于审理劳动争议案件适用法律问题的解释', code: 'SFJS-ZGF-LD-001', category: '劳动争议', chunks: 56, vectors: 2123, size: '1.1 MB', updateTime: '2024-03-04 09:12' },
      { id: 42, name: '最高人民法院关于审理买卖合同纠纷案件适用法律问题的解释', code: 'SFJS-ZGF-MM-001', category: '合同纠纷', chunks: 78, vectors: 2890, size: '1.5 MB', updateTime: '2024-03-03 11:34' },
      { id: 43, name: '最高人民检察院关于渎职侵权犯罪案件立案标准的规定', code: 'SFJS-ZGJ-DZ-001', category: '刑事案件', chunks: 34, vectors: 1456, size: '780 KB', updateTime: '2024-03-02 14:56' }
    ]
  }
}

const currentLevel = computed(() => route.params.level || 'xianfa')
const config = computed(() => levelConfig[currentLevel.value] || levelConfig.xianfa)

const levelTitle = computed(() => config.value.title)
const levelDescription = computed(() => config.value.description)
const documents = computed(() => config.value.docs)

// 统计数据
const statistics = computed(() => {
  const docs = documents.value
  const totalDocs = docs.length
  const totalChunks = docs.reduce((sum, doc) => sum + doc.chunks, 0)
  const totalVectors = docs.reduce((sum, doc) => sum + doc.vectors, 0)
  const avgChunks = Math.round(totalChunks / totalDocs)
  
  return {
    totalDocs,
    newDocs: Math.floor(totalDocs * 0.1),
    totalChunks,
    avgChunks,
    totalVectors,
    vectorGrowth: 8.5,
    queryCount: Math.floor(totalVectors * 0.05),
    queryGrowth: 12.3
  }
})

const keyword = ref('')
const showUploadDialog = ref(false)
const uploadForm = ref({
  category: ''
})

const formatNumber = (num) => {
  return num.toLocaleString()
}

const handleView = (row) => {
  ElMessage.info(`查看文档：${row.name}（演示）`)
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

const handleUpload = () => {
  ElMessage.success('上传成功（演示）')
  showUploadDialog.value = false
}
</script>

<style scoped>
.hierarchy-detail-page {
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
