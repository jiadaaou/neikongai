<template>
  <div class="knowledge-dashboard">
    <el-page-header title="法律知识库" content="知识库仪表盘" />
    
    <!-- ============================================= -->
    <!-- 第一部分：总览统计卡片 -->
    <!-- ============================================= -->
    <div style="margin: 20px 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.lawsTotal }}</div>
              <div class="stat-label">法律文档总数</div>
              <div class="stat-trend">
                本月新增 {{ stats.lawsThisMonth }} 部
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.standardsTotal }}</div>
              <div class="stat-label">行业准则总数</div>
              <div class="stat-trend">
                本月新增 {{ stats.standardsThisMonth }} 个
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.vectorsTotal.toLocaleString() }}</div>
              <div class="stat-label">向量总数</div>
              <div class="stat-trend">
                向量化率 {{ stats.vectorizationRate }}%
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value" :class="{ 'good': stats.healthScore >= 80 }">
                {{ stats.healthScore }}
              </div>
              <div class="stat-label">知识库健康度</div>
              <div class="stat-trend" :class="{ 'good': stats.healthScore >= 80 }">
                {{ stats.healthScore >= 80 ? '✅ 健康' : '⚠️ 待优化' }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- ============================================= -->
    <!-- 第二部分：基础法律库详情（按层级） -->
    <!-- ============================================= -->
    <el-card style="margin: 20px 0">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">
            ⚖️ 基础法律库（5 层，对应检索第 4-8 层）
          </span>
          <el-button type="primary" size="small" @click="goToLaws">
            管理法律 →
          </el-button>
        </div>
      </template>
      
      <el-table :data="lawLevels" border stripe>
        <el-table-column label="检索层级" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary" size="large">第 {{ row.searchLevel }} 层</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="层级名称" width="180">
          <template #default="{ row }">
            <span style="font-size: 16px;">{{ row.icon }}</span>
            <span style="margin-left: 8px; font-weight: bold;">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="法律层级" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">legal_level={{ row.legalLevel }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="文档数量" width="120" align="center">
          <template #default="{ row }">
            <span style="font-size: 18px; font-weight: bold; color: #409EFF;">
              {{ row.count }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="分块数量" width="120" align="center">
          <template #default="{ row }">
            <span style="font-size: 16px;">{{ row.chunks }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="向量数量" width="120" align="center">
          <template #default="{ row }">
            <span style="font-size: 16px;">{{ row.vectors }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="完成度" width="200">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.completionRate" 
              :status="row.completionRate === 100 ? 'success' : 'warning'"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" fixed="right" width="150" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLevel(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="uploadToLevel(row)">
              上传
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 缺失提示 -->
      <el-alert 
        v-if="missingLevels.length > 0"
        type="warning" 
        :closable="false"
        style="margin-top: 20px"
        title="⚠️ 知识库完整性提示"
      >
        <ul style="margin: 10px 0; padding-left: 20px;">
          <li v-for="level in missingLevels" :key="level.searchLevel" style="margin: 5px 0;">
            <strong>{{ level.name }}</strong>（检索第 {{ level.searchLevel }} 层）为空，
            建议上传相关文档以提高检索覆盖率
          </li>
        </ul>
        <p style="margin-top: 10px;">
          <strong>当前覆盖率：{{ coverageRate }}%</strong>
        </p>
      </el-alert>
    </el-card>
    
    <!-- ============================================= -->
    <!-- 第三部分：行业准则库详情（按行业） -->
    <!-- ============================================= -->
    <el-card style="margin: 20px 0">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">
            📋 行业准则库
          </span>
          <el-button type="primary" size="small" @click="goToStandards">
            管理准则 →
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20" v-if="industries.length > 0">
        <el-col :span="8" v-for="industry in industries" :key="industry.id">
          <el-card shadow="hover" class="industry-card" @click="viewIndustry(industry)">
            <div class="industry-header">
              <span class="industry-icon">{{ industry.icon }}</span>
              <span class="industry-name">{{ industry.name }}</span>
            </div>
            <div class="industry-stats">
              <div class="industry-stat">
                <span class="stat-value">{{ industry.count }}</span>
                <span class="stat-label">准则数量</span>
              </div>
              <div class="industry-stat">
                <span class="stat-value">{{ industry.vectors }}</span>
                <span class="stat-label">向量数量</span>
              </div>
            </div>
            <el-button 
              link 
              type="primary" 
              style="margin-top: 15px"
            >
              查看详情 →
            </el-button>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty 
        v-else
        description="暂无行业准则，请先创建行业分类"
      >
        <el-button type="primary" @click="createIndustry">
          创建行业分类
        </el-button>
      </el-empty>
    </el-card>
    
    <!-- ============================================= -->
    <!-- 第四部分：向量化实时监控 -->
    <!-- ============================================= -->
    <el-card style="margin: 20px 0">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">
            📈 向量化监控
          </span>
          <el-button type="primary" size="small" @click="goToMonitor">
            详细监控 →
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="monitor-section">
            <h4>当前处理队列</h4>
            <div v-if="processingQueue.length > 0">
              <el-alert 
                type="info" 
                :closable="false"
                style="margin-bottom: 15px"
              >
                正在处理 {{ processingQueue.length }} 个文档
              </el-alert>
              
              <div v-for="item in processingQueue" :key="item.id" class="processing-item">
                <div style="flex: 1;">
                  <div style="font-weight: bold;">{{ item.title }}</div>
                  <div style="font-size: 12px; color: #909399; margin-top: 5px;">
                    {{ item.type === 'law' ? '法律文档' : '行业准则' }}
                  </div>
                </div>
                <div style="width: 200px; margin-left: 20px;">
                  <el-progress :percentage="item.progress" :status="item.status" />
                </div>
              </div>
            </div>
            <el-empty v-else description="当前无处理任务" />
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="monitor-section">
            <h4>今日向量化统计</h4>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-stat-value">{{ todayStats.processed }}</div>
                  <div class="mini-stat-label">已处理</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-stat-value error">{{ todayStats.failed }}</div>
                  <div class="mini-stat-label">失败</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-stat-value">{{ todayStats.speed }}</div>
                  <div class="mini-stat-label">个/分钟</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-col>
      </el-row>
      
      <!-- API 调用状态 -->
      <el-divider />
      <div class="api-status">
        <span style="font-weight: bold; margin-right: 10px;">OpenAI API 状态：</span>
        <el-tag :type="apiStatus === 'online' ? 'success' : 'danger'" size="large">
          {{ apiStatus === 'online' ? '✅ 正常' : '❌ 异常' }}
        </el-tag>
        <span style="margin-left: 30px;">今日调用次数：<strong>{{ apiCalls }}</strong></span>
        <span style="margin-left: 30px;">成功率：<strong>{{ apiSuccessRate }}%</strong></span>
      </div>
    </el-card>
    
    <!-- ============================================= -->
    <!-- 第五部分：快速操作 -->
    <!-- ============================================= -->
    <el-card style="margin: 20px 0">
      <template #header>
        <span style="font-weight: bold; font-size: 16px;">
          🚀 快速操作
        </span>
      </template>
      
      <el-space wrap :size="15">
        <el-button type="primary" @click="uploadLaw" :icon="Upload">
          上传法律文档
        </el-button>
        <el-button type="primary" @click="uploadStandard" :icon="Upload">
          上传行业准则
        </el-button>
        <el-button @click="testSearch" :icon="Search">
          测试检索
        </el-button>
        <el-button @click="exportReport" :icon="Download">
          导出报告
        </el-button>
        <el-button @click="healthCheck" :icon="Monitor">
          知识库体检
        </el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, Search, Download, Monitor } from '@element-plus/icons-vue'

const router = useRouter()

// 总览统计（模拟数据）
const stats = ref({
  lawsTotal: 58,
  lawsThisMonth: 3,
  standardsTotal: 0,
  standardsThisMonth: 0,
  vectorsTotal: 12345,
  vectorizationRate: 98.5,
  healthScore: 85
})

// 法律层级数据（模拟数据）
const lawLevels = ref([
  { 
    searchLevel: 8, 
    name: '宪法', 
    icon: '🏛️',
    legalLevel: 5, 
    count: 1, 
    chunks: 45, 
    vectors: 45, 
    completionRate: 100 
  },
  { 
    searchLevel: 7, 
    name: '法律', 
    icon: '⚖️',
    legalLevel: 4, 
    count: 52, 
    chunks: 1234, 
    vectors: 1234, 
    completionRate: 100 
  },
  { 
    searchLevel: 6, 
    name: '行政法规', 
    icon: '📋',
    legalLevel: 3, 
    count: 3, 
    chunks: 156, 
    vectors: 156, 
    completionRate: 100 
  },
  { 
    searchLevel: 5, 
    name: '部门规章', 
    icon: '📑',
    legalLevel: 2, 
    count: 2, 
    chunks: 89, 
    vectors: 89, 
    completionRate: 100 
  },
  { 
    searchLevel: 4, 
    name: '地方法规', 
    icon: '📄',
    legalLevel: 1, 
    count: 0, 
    chunks: 0, 
    vectors: 0, 
    completionRate: 0 
  }
])

// 缺失层级
const missingLevels = computed(() => {
  return lawLevels.value.filter(level => level.count === 0)
})

// 覆盖率
const coverageRate = computed(() => {
  const total = lawLevels.value.length
  const filled = lawLevels.value.filter(level => level.count > 0).length
  return Math.round((filled / total) * 100)
})

// 行业准则（模拟数据 - 空数据用于演示）
const industries = ref([
  // { id: 1, name: '建筑工程', icon: '🏗️', count: 12, vectors: 456 },
  // { id: 2, name: '财务会计', icon: '💰', count: 8, vectors: 234 },
  // { id: 3, name: '人力资源', icon: '👥', count: 15, vectors: 567 }
])

// 处理队列（模拟数据）
const processingQueue = ref([
  { id: 1, title: '中华人民共和国环境保护法', type: 'law', progress: 75, status: '' },
  { id: 2, title: '建筑工程施工规范', type: 'standard', progress: 45, status: '' }
])

// 今日统计
const todayStats = ref({
  processed: 123,
  failed: 2,
  speed: 15
})

// API 状态
const apiStatus = ref('online')
const apiCalls = ref(1234)
const apiSuccessRate = ref(99.8)

// 页面跳转
const goToLaws = () => {
  router.push('/admin/laws')
}

const goToStandards = () => {
  ElMessage.info('行业准则管理页面开发中...')
  router.push('/admin/standards')
}

const goToMonitor = () => {
  ElMessage.info('向量监控页面开发中...')
  // router.push('/admin/knowledge/monitor')
}

const viewLevel = (row) => {
  ElMessage.success(`查看 ${row.name} 层级`)
  router.push(`/admin/laws?level=${row.legalLevel}`)
}

const uploadToLevel = (row) => {
  ElMessage.success(`上传到 ${row.name} 层级`)
}

const viewIndustry = (industry) => {
  ElMessage.success(`查看 ${industry.name} 详情`)
}

const createIndustry = () => {
  ElMessage.info('创建行业分类功能开发中...')
}

const uploadLaw = () => {
  router.push('/admin/laws')
  ElMessage.info('请在法律管理页面上传')
}

const uploadStandard = () => {
  ElMessage.info('行业准则上传功能开发中...')
}

const testSearch = () => {
  ElMessage.info('检索测试功能开发中...')
}

const exportReport = () => {
  ElMessage.info('报告导出功能开发中...')
}

const healthCheck = () => {
  ElMessage.info('知识库体检功能开发中...')
}
</script>

<style scoped>
.knowledge-dashboard {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.stat-card {
  transition: all 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-value.good {
  color: #67c23a;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.stat-trend.good {
  color: #67c23a;
}

.industry-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.industry-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.industry-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.industry-icon {
  font-size: 40px;
  margin-right: 15px;
}

.industry-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.industry-stats {
  display: flex;
  justify-content: space-around;
}

.industry-stat {
  text-align: center;
}

.industry-stat .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  display: block;
  margin-bottom: 5px;
}

.industry-stat .stat-label {
  font-size: 12px;
  color: #909399;
}

.monitor-section {
  padding: 15px;
  background: #f9fafc;
  border-radius: 4px;
}

.monitor-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
}

.processing-item {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.mini-stat {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.mini-stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.mini-stat-value.error {
  color: #f56c6c;
}

.mini-stat-label {
  font-size: 12px;
  color: #909399;
}

.api-status {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f9fafc;
  border-radius: 4px;
}
</style>
