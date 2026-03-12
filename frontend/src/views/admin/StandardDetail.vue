<template>
  <div class="standard-detail">
    <el-page-header @back="goBack" title="返回" content="标准文档详情" />
    
    <el-card v-loading="loading" class="detail-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>{{ standardDetail.title }}</h3>
          <el-tag v-if="standardDetail.processed_status === 'completed'" type="success">已完成</el-tag>
          <el-tag v-else-if="standardDetail.processed_status === 'processing'" type="warning">处理中</el-tag>
          <el-tag v-else-if="standardDetail.processed_status === 'pending'" type="info">等待处理</el-tag>
          <el-tag v-else type="danger">处理失败</el-tag>
        </div>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="标准层级">
          {{ standardDetail.legal_level_name }}
        </el-descriptions-item>
        <el-descriptions-item label="文号">
          {{ standardDetail.doc_number || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="生效日期">
          {{ standardDetail.effective_date || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="上传时间">
          {{ formatDate(standardDetail.uploaded_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="原始文件名">
          {{ standardDetail.original_filename }}
        </el-descriptions-item>
        <el-descriptions-item label="分块数量">
          {{ standardDetail.chunks_count || 0 }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <el-card class="chunks-card" shadow="never">
      <template #header>
        <h3>文档分块（{{ chunks.length }}个）</h3>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
      </template>
      
      <el-table :data="chunks" stripe>
        <el-table-column prop="chunk_index" label="序号" width="80" />
        <el-table-column prop="chunk_type" label="类型" width="120">
          <template #default="{ row }">
            {{ row.chunk_type === 'single_article' ? '单条' : '条组' }}

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
        <el-table-column prop="chapter_number" label="章节" width="100" />
        
        <!-- 修改：条款范围显示 -->
        <el-table-column label="条款" width="180">
          <template #default="{ row }">
            <span v-if="row.article_end && row.article_start !== row.article_end">
              {{ row.article_start }} 至 {{ row.article_end }}
            </span>
            <span v-else>
              {{ row.article_start || '-' }}
            </span>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
        
        <el-table-column prop="chunk_text" label="内容" min-width="300">
          <template #default="{ row }">
            {{ row.chunk_text.substring(0, 100) }}...

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
        
        <!-- 修改：关键词显示（处理空值）- 暂时隐藏 -->
        <el-table-column v-if="false" label="关键词" width="200">
          <template #default="{ row }">
            <span v-if="!row.keywords || row.keywords.length === 0" style="color: #ccc;">
              -
            </span>
            <el-tag
              v-for="keyword in row.keywords"
              :key="keyword"
              size="small"
              style="margin-right: 5px"
            >
              {{ keyword }}
            </el-tag>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
        
        <!-- 新增：向量状态列 -->
        <el-table-column label="向量" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_embedding !== false" type="success" size="small">✓</el-tag>
            <el-tag v-else type="info" size="small">-</el-tag>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
        
        <!-- 新增：操作列 -->
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="viewChunk(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button size="small" type="primary" @click="editChunk(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="markInvalid(row)">
                <el-icon><CircleClose /></el-icon>
                标记无效
              </el-button>
            </el-button-group>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

    <!-- 编辑分块对话框 - 优化版 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分块内容"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-alert
        title="⚠️ 编辑后将自动重新向量化，请确保标准条文的准确性！"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="90px" label-position="right">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input 
                v-model="editForm.chapter_number" 
                placeholder="例如：第一章"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-tag>条组</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始条款">
              <el-input 
                v-model="editForm.article_start" 
                placeholder="例如：第一条"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束条款">
              <el-input 
                v-model="editForm.article_end" 
                placeholder="例如：第八条（单条留空）"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分块内容">
          <el-input
            v-model="editForm.chunk_text"
            type="textarea"
            :rows="12"
            placeholder="请输入标准条文内容"
            show-word-limit
            :maxlength="5000"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px;">
            当前字数：{{ editForm.chunk_text?.length || 0 }} 字
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-text type="info" size="small">
            💡 保存后将自动重新生成向量
          </el-text>
          <div>
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveEdit">
              💾 保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStandardDetail, getStandardChunks } from '@/api/standards'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const standardDetail = ref({})
const chunks = ref([])
const editDialogVisible = ref(false)
const editForm = ref({})
const currentChunk = ref(null)

const goBack = () => {
  router.back()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 查看完整内容
const viewChunk = (chunk) => {
  // 构建关键词HTML
  let keywordsHtml = '<div style="color: #999; margin-top: 5px;">无关键词</div>';
  
  if (chunk.keywords && chunk.keywords.length > 0) {
    keywordsHtml = '<div style="margin-top: 5px;">' + 
      chunk.keywords.map(kw => 
        `<span style="display: inline-block; padding: 2px 8px; margin: 2px; background: #ecf5ff; color: #409eff; border-radius: 3px; font-size: 12px;">${kw}</span>`
      ).join('') + 
      '</div>';
  }
  
  // 构建每条详细关键词HTML
  let articlesDetailHtml = '';
  
  if (chunk.articles_detail && chunk.articles_detail.length > 0) {
    articlesDetailHtml = `
      <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
        <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">📝 每条详细关键词：</h4>
        ${chunk.articles_detail.map((article, idx) => `
          <div style="margin-bottom: 10px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
            <div style="font-weight: bold; color: #606266; margin-bottom: 5px;">
              ${idx + 1}. ${article.article_number || '未知条号'}
            </div>
            <div style="font-size: 12px; color: #909399; margin-bottom: 5px;">
              ${article.article_text ? (article.article_text.substring(0, 50) + '...') : '无内容'}
            </div>
            <div>
              ${article.keywords && article.keywords.length > 0 
                ? article.keywords.map(kw => 
                    `<span style="display: inline-block; padding: 2px 6px; margin: 2px; background: #e1f3d8; color: #67c23a; border-radius: 3px; font-size: 11px;">${kw}</span>`
                  ).join('')
                : '<span style="color: #999; font-size: 12px;">无关键词</span>'
              }
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  const h = ElMessageBox
  h.alert(
    `<div class="chunk-view-content" style="max-height: 600px; overflow-y: auto;">
      <div class="chunk-meta" style="background: #f5f7fa; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
        <div style="margin-bottom: 8px;">
          <span><strong>类型：</strong>${chunk.chunk_type === 'single_article' ? '单条' : chunk.chunk_type === 'attachment' ? '附件' : '条组'}</span>
          <span style="margin-left: 20px;"><strong>序号：</strong>${chunk.chunk_index}</span>
        </div>
        <div style="margin-bottom: 8px;">
          <span><strong>章节：</strong>${chunk.chapter_number || "-"}</span>
          <span style="margin-left: 20px;"><strong>条款：</strong>${chunk.article_start}${chunk.article_end && chunk.article_end !== chunk.article_start ? " 至 " + chunk.article_end : ""}</span>
        </div>
        <div>
          <span><strong>字数：</strong>${chunk.chunk_text.length} 字</span>
          <span style="margin-left: 20px;"><strong>条文数量：</strong>${chunk.articles_count || 1} 条</span>
        </div>
      </div>
      
      <div style="margin-bottom: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">🔑 条组整体关键词：</h4>
        ${keywordsHtml}
      </div>
      
      <div style="margin-bottom: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">📄 完整内容：</h4>
        <div class="chunk-text-content" style="line-height: 1.8; color: #606266; background: white; padding: 12px; border-radius: 4px; border: 1px solid #eee;">
          ${chunk.chunk_text.replace(/\n/g, "<br/>")}
        </div>
      </div>
      
      ${articlesDetailHtml}
    </div>`,
    `查看分块内容 - ${chunk.article_start}`,
    {
      confirmButtonText: "关闭",
      dangerouslyUseHTMLString: true,
      customClass: "chunk-view-dialog",
      showClose: true,
      center: false
    }
  )
}

// 编辑分块（带锁定确认）
const editChunk = (chunk) => {
  ElMessageBox.confirm(
    '编辑分块内容后将自动重新向量化。<br/><strong style="color: red;">请谨慎修改，确保标准条文的准确性！</strong>',
    '⚠️ 编辑警告',
    {
      confirmButtonText: '确认编辑',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(() => {
    currentChunk.value = chunk
    editForm.value = {
      chunk_text: chunk.chunk_text,
      chapter_number: chunk.chapter_number,
      article_start: chunk.article_start,
      article_end: chunk.article_end
    }
    editDialogVisible.value = true
  }).catch(() => {
    // 用户取消
  })
}

// 保存编辑
const saveEdit = async () => {
  try {
    // TODO: 调用后端 API 保存修改
    ElMessage.info('保存功能开发中...')
    // await updateChunk(currentChunk.value.id, editForm.value)
    // ElMessage.success('保存成功，正在重新向量化...')
    // editDialogVisible.value = false
    // fetchData()
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

// 标记无效（软删除）
const markInvalid = (chunk) => {
  ElMessageBox.confirm(
    `确定要标记分块 "${chunk.article_start}" 为无效吗？<br/>标记后该分块将不参与检索，但仍保留在数据库中。`,
    '确认操作',
    {
      confirmButtonText: '确认标记',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(() => {
    ElMessage.info('标记功能开发中...')
    // TODO: 调用后端 API 标记为无效
  }).catch(() => {
    // 用户取消
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const id = route.params.id
    
    // 获取详情
    const detail = await getStandardDetail(id)
    standardDetail.value = detail
    
    // 获取分块
    const chunksData = await getStandardChunks(id)
    chunks.value = chunksData.chunks || []
  } catch (error) {
    console.error('获取详情失败：', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.standard-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-header h3 {
  margin: 0;
  flex: 1;
}

.detail-card,
.chunks-card {
  margin-top: 20px;
}

:deep(.chunk-view-dialog) {
  max-width: 800px;
}

:deep(.chunk-view-dialog .el-message-box__message) {
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.8;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>

<style>
/* 查看对话框样式 */
:deep(.chunk-view-dialog) {
  max-width: 900px;
  width: 90%;
}

:deep(.chunk-view-dialog .el-message-box__message) {
  max-height: 600px;
  overflow-y: auto;
  padding: 0;
}

:deep(.chunk-view-content) {
  padding: 15px;
}

:deep(.chunk-meta) {
  background-color: #f5f7fa;
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}

:deep(.chunk-text-content) {
  line-height: 2;
  font-size: 15px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  text-align: justify;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

/* 滚动条样式 */
:deep(.el-message-box__message::-webkit-scrollbar) {
  width: 8px;
}

:deep(.el-message-box__message::-webkit-scrollbar-thumb) {
  background-color: #dcdfe6;
  border-radius: 4px;
}

:deep(.el-message-box__message::-webkit-scrollbar-thumb:hover) {
  background-color: #c0c4cc;
}
</style>
