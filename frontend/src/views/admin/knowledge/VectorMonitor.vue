<template>
  <div class="monitor-page">
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>向量监控</h2>
          <p class="subtitle">实时监控向量数据库的运行状态和性能指标</p>
        </div>
        <div class="header-actions">
          <el-tag :type="systemStatus.type" size="large">
            <el-icon><component :is="systemStatus.icon" /></el-icon>
            {{ systemStatus.text }}
          </el-tag>
          <el-button :icon="Refresh" @click="handleRefresh">刷新数据</el-button>
        </div>
      </div>
    </el-card>

    <!-- 实时指标卡片 -->
    <el-row :gutter="16" style="margin-top: 24px;">
      <el-col :span="6">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-header">
            <el-icon :size="32" color="#1890ff"><Coin /></el-icon>
            <div class="metric-info">
              <div class="metric-label">向量总数</div>
              <div class="metric-value">{{ formatNumber(metrics.totalVectors) }}</div>
            </div>
          </div>
          <div class="metric-footer">
            <el-progress :percentage="75" :show-text="false" />
            <span class="metric-trend">
              <el-icon color="#52c41a"><CaretTop /></el-icon>
              +2.5% 较昨日
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-header">
            <el-icon :size="32" color="#52c41a"><Timer /></el-icon>
            <div class="metric-info">
              <div class="metric-label">平均查询时间</div>
              <div class="metric-value">{{ metrics.avgQueryTime }} ms</div>
            </div>
          </div>
          <div class="metric-footer">
            <el-progress :percentage="60" status="success" :show-text="false" />
            <span class="metric-trend success">
              <el-icon color="#52c41a"><CaretBottom /></el-icon>
              -8.3% 较昨日
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-header">
            <el-icon :size="32" color="#faad14"><TrendCharts /></el-icon>
            <div class="metric-info">
              <div class="metric-label">今日查询次数</div>
              <div class="metric-value">{{ formatNumber(metrics.todayQueries) }}</div>
            </div>
          </div>
          <div class="metric-footer">
            <el-progress :percentage="85" status="warning" :show-text="false" />
            <span class="metric-trend">
              <el-icon color="#52c41a"><CaretTop /></el-icon>
              +12.8% 较昨日
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-header">
            <el-icon :size="32" color="#722ed1"><DataLine /></el-icon>
            <div class="metric-info">
              <div class="metric-label">相似度准确率</div>
              <div class="metric-value">{{ metrics.accuracy }}%</div>
            </div>
          </div>
          <div class="metric-footer">
            <el-progress :percentage="metrics.accuracy" color="#722ed1" :show-text="false" />
            <span class="metric-trend">
              <el-icon color="#52c41a"><CaretTop /></el-icon>
              +0.8% 较昨日
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" style="margin-top: 24px;">
      <!-- 查询趋势图 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>查询趋势（最近7天）</span>
              <el-radio-group v-model="chartTimeRange" size="small">
                <el-radio-button label="7d">7天</el-radio-button>
                <el-radio-button label="30d">30天</el-radio-button>
                <el-radio-button label="90d">90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="queryTrendChart"></div>
        </el-card>
      </el-col>

      <!-- 响应时间分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>响应时间分布</span>
          </template>
          <div class="chart-container" ref="responseTimeChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 24px;">
      <!-- 向量分布统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>向量分布统计</span>
          </template>
          <div class="chart-container" ref="vectorDistChart"></div>
        </el-card>
      </el-col>

      <!-- 相似度得分分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>相似度得分分布</span>
          </template>
          <div class="chart-container" ref="similarityChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- API 调用统计 -->
    <el-card style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>OpenAI API 调用统计</span>
          <el-button :icon="Download" size="small">导出报告</el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="6">
          <div class="api-stat-item">
            <div class="stat-label">今日调用次数</div>
            <div class="stat-value">{{ formatNumber(apiStats.todayCalls) }}</div>
            <div class="stat-detail">成功率: {{ apiStats.successRate }}%</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="api-stat-item">
            <div class="stat-label">消耗 Token</div>
            <div class="stat-value">{{ formatNumber(apiStats.tokensUsed) }}</div>
            <div class="stat-detail">约 ${{ apiStats.cost }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="api-stat-item">
            <div class="stat-label">平均延迟</div>
            <div class="stat-value">{{ apiStats.avgLatency }} ms</div>
            <div class="stat-detail">P95: {{ apiStats.p95Latency }} ms</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="api-stat-item">
            <div class="stat-label">错误率</div>
            <div class="stat-value">{{ apiStats.errorRate }}%</div>
            <div class="stat-detail">最近1小时</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 实时日志 -->
    <el-card style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>实时查询日志</span>
          <div>
            <el-select v-model="logLevel" size="small" style="width: 120px; margin-right: 12px;">
              <el-option label="全部" value="all" />
              <el-option label="成功" value="success" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
            </el-select>
            <el-button :icon="Refresh" size="small" @click="refreshLogs">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="logs" style="width: 100%;" max-height="400">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getLogType(row.level)" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="query" label="查询内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="similarity" label="相似度" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getSimilarityType(row.similarity)" size="small">
              {{ row.similarity }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="耗时" width="100" align="center">
          <template #default="{ row }">
            {{ row.responseTime }} ms
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :icon="View" @click="viewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="logPage"
        v-model:page-size="logPageSize"
        :total="logTotal"
        layout="prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 向量检索测试 -->
    <el-card style="margin-top: 24px;">
      <template #header>
        <span>向量检索测试</span>
      </template>

      <el-form :inline="true">
        <el-form-item label="测试查询">
          <el-input
            v-model="testQuery"
            placeholder="输入测试查询文本"
            style="width: 400px;"
          />
        </el-form-item>
        <el-form-item label="返回数量">
          <el-input-number v-model="testTopK" :min="1" :max="20" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleTest" :loading="testing">
            执行测试
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="testResults.length > 0" class="test-results">
        <h4>检索结果：</h4>
        <el-table :data="testResults" style="margin-top: 12px;">
          <el-table-column type="index" label="排名" width="80" />
          <el-table-column prop="content" label="匹配内容" min-width="400" show-overflow-tooltip />
          <el-table-column prop="similarity" label="相似度" width="120" align="center">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.round(row.similarity * 100)"
                :color="getProgressColor(row.similarity)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="200" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Coin,
  Timer,
  TrendCharts,
  DataLine,
  Download,
  View,
  Search,
  CaretTop,
  CaretBottom,
  SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 系统状态
const systemStatus = ref({
  type: 'success',
  icon: 'SuccessFilled',
  text: '运行正常'
})

// 实时指标
const metrics = ref({
  totalVectors: 1234567,
  avgQueryTime: 45,
  todayQueries: 8932,
  accuracy: 94.5
})

// API 统计
const apiStats = ref({
  todayCalls: 8932,
  successRate: 98.7,
  tokensUsed: 456789,
  cost: 12.34,
  avgLatency: 234,
  p95Latency: 567,
  errorRate: 1.3
})

// 图表时间范围
const chartTimeRange = ref('7d')

// 日志
const logLevel = ref('all')
const logPage = ref(1)
const logPageSize = ref(10)
const logTotal = ref(100)

const logs = ref([
  {
    time: '2024-03-04 15:23:45',
    type: '语义搜索',
    level: 'success',
    query: '劳动合同法关于试用期的规定',
    similarity: 92,
    responseTime: 45,
    status: 'success'
  },
  {
    time: '2024-03-04 15:23:12',
    type: '文档检索',
    level: 'success',
    query: '建筑工程质量验收标准',
    similarity: 88,
    responseTime: 67,
    status: 'success'
  },
  {
    time: '2024-03-04 15:22:56',
    type: '相似推荐',
    level: 'warning',
    query: '企业合规管理制度',
    similarity: 65,
    responseTime: 123,
    status: 'success'
  },
  {
    time: '2024-03-04 15:22:34',
    type: '语义搜索',
    level: 'error',
    query: '无效查询测试',
    similarity: 0,
    responseTime: 234,
    status: 'error'
  },
  {
    time: '2024-03-04 15:22:01',
    type: '文档检索',
    level: 'success',
    query: '财务会计准则解读',
    similarity: 95,
    responseTime: 34,
    status: 'success'
  }
])

// 测试
const testQuery = ref('')
const testTopK = ref(5)
const testing = ref(false)
const testResults = ref([])

// 图表实例
const queryTrendChart = ref(null)
const responseTimeChart = ref(null)
const vectorDistChart = ref(null)
const similarityChart = ref(null)

let chartInstances = []

// 方法
const formatNumber = (num) => {
  return num.toLocaleString()
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新（演示）')
}

const refreshLogs = () => {
  ElMessage.success('日志已刷新（演示）')
}

const viewDetail = (row) => {
  ElMessage.info(`查看详情：${row.query}（演示）`)
}

const handleTest = () => {
  if (!testQuery.value) {
    ElMessage.warning('请输入测试查询')
    return
  }
  
  testing.value = true
  setTimeout(() => {
    testResults.value = [
      {
        content: '《劳动合同法》第十九条规定，试用期最长不得超过六个月...',
        similarity: 0.95,
        source: '劳动合同法'
      },
      {
        content: '试用期包含在劳动合同期限内，劳动合同仅约定试用期的...',
        similarity: 0.88,
        source: '劳动合同法实施条例'
      },
      {
        content: '用人单位与劳动者约定的试用期不符合本法规定的...',
        similarity: 0.82,
        source: '劳动争议案例汇编'
      }
    ]
    testing.value = false
    ElMessage.success('检索完成')
  }, 1000)
}

const getLogType = (level) => {
  const types = {
    success: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return types[level] || 'info'
}

const getSimilarityType = (similarity) => {
  if (similarity >= 90) return 'success'
  if (similarity >= 70) return 'warning'
  return 'danger'
}

const getProgressColor = (similarity) => {
  if (similarity >= 0.9) return '#52c41a'
  if (similarity >= 0.7) return '#faad14'
  return '#ff4d4f'
}

// 初始化图表
const initCharts = () => {
  // 查询趋势图
  const chart1 = echarts.init(queryTrendChart.value)
  chart1.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['02-27', '02-28', '02-29', '03-01', '03-02', '03-03', '03-04']
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '查询次数',
        data: [6543, 7234, 7891, 8123, 8456, 8789, 8932],
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 }
      }
    ]
  })

  // 响应时间分布
  const chart2 = echarts.init(responseTimeChart.value)
  chart2.setOption({
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 7234, name: '< 50ms' },
          { value: 1234, name: '50-100ms' },
          { value: 345, name: '100-200ms' },
          { value: 119, name: '> 200ms' }
        ]
      }
    ]
  })

  // 向量分布统计
  const chart3 = echarts.init(vectorDistChart.value)
  chart3.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['宪法', '法律', '行政法规', '地方法规', '司法解释', '行业准则']
    },
    yAxis: { type: 'value' },
    series: [
      {
        data: [1234, 45678, 23456, 34567, 9876, 12345],
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#1890ff' },
            { offset: 1, color: '#36cfc9' }
          ])
        }
      }
    ]
  })

  // 相似度得分分布
  const chart4 = echarts.init(similarityChart.value)
  chart4.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['0-20', '20-40', '40-60', '60-80', '80-90', '90-100']
    },
    yAxis: { type: 'value' },
    series: [
      {
        data: [45, 123, 456, 1234, 3456, 4578],
        type: 'bar',
        itemStyle: { color: '#52c41a' }
      }
    ]
  })

  chartInstances = [chart1, chart2, chart3, chart4]
}

onMounted(() => {
  initCharts()
  
  // 自动调整图表大小
  window.addEventListener('resize', () => {
    chartInstances.forEach(chart => chart.resize())
  })
})

onUnmounted(() => {
  chartInstances.forEach(chart => chart.dispose())
})
</script>

<style scoped>
.monitor-page {
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
  align-items: center;
  gap: 12px;
}

.metric-card ::v-deep(.el-card__body) {
  padding: 20px;
}

.metric-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.metric-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.metric-trend.success {
  color: #52c41a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.api-stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.stat-detail {
  font-size: 12px;
  color: #999;
}

.test-results {
  margin-top: 24px;
}

.test-results h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}
</style>
