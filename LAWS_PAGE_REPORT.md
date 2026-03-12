# `/admin/laws` 法律文档管理页面 详细报告

> **报告生成时间**：2026-03-12  
> **页面 URL**：`https://admin.neikongai.com/admin/laws`  
> **涉及源文件**：
> - `frontend/src/views/admin/LawsList.vue`（841 行）
> - `frontend/src/views/admin/LawDetail.vue`（1165 行）
> - `frontend/src/api/laws.js`（107 行）
> - `backend/app/routers/admin_laws.py`（708 行）

---

## 目录

1. [功能概述](#1-功能概述)
2. [整体架构](#2-整体架构)
3. [路由配置](#3-路由配置)
4. [前端详情：`/admin/laws` 列表页](#4-前端详情adminlaws-列表页)
   - 4.1 [页面布局结构](#41-页面布局结构)
   - 4.2 [法律层级卡片](#42-法律层级卡片)
   - 4.3 [搜索与筛选栏](#43-搜索与筛选栏)
   - 4.4 [文档列表表格](#44-文档列表表格)
   - 4.5 [上传对话框](#45-上传对话框)
   - 4.6 [上传进度轮询](#46-上传进度轮询)
   - 4.7 [数据流与状态管理](#47-数据流与状态管理)
5. [前端详情：`/admin/laws/:id` 文档详情页](#5-前端详情adminlawsid-文档详情页)
   - 5.1 [页面布局结构](#51-页面布局结构)
   - 5.2 [文档元信息卡片](#52-文档元信息卡片)
   - 5.3 [分块列表表格](#53-分块列表表格)
   - 5.4 [查看分块对话框（弹窗）](#54-查看分块对话框弹窗)
   - 5.5 [编辑分块对话框](#55-编辑分块对话框)
   - 5.6 [数据流与状态管理](#56-数据流与状态管理)
6. [API 客户端封装（`laws.js`）](#6-api-客户端封装lawsjs)
7. [后端 API 详情（`admin_laws.py`）](#7-后端-api-详情admin_lawspy)
   - 7.1 [接口总表](#71-接口总表)
   - 7.2 [POST `/admin/laws/upload` — 上传文档](#72-post-adminlawsupload--上传文档)
   - 7.3 [GET `/admin/laws` — 获取文档列表](#73-get-adminlaws--获取文档列表)
   - 7.4 [GET `/admin/laws/{id}` — 获取文档详情](#74-get-adminlawsid--获取文档详情)
   - 7.5 [GET `/admin/laws/{id}/chunks` — 获取文档分块](#75-get-adminlawsidchunks--获取文档分块)
   - 7.6 [GET `/admin/laws/chunks/{chunk_id}` — 获取分块详情](#76-get-adminlawschunkschunk_id--获取分块详情)
   - 7.7 [DELETE `/admin/laws/{id}` — 删除文档](#77-delete-adminlawsid--删除文档)
   - 7.8 [GET `/admin/laws/{id}/logs` — 获取处理日志](#78-get-adminlawsidlogs--获取处理日志)
   - 7.9 [POST `/admin/laws/test-search` — 混合检索测试](#79-post-adminlawstest-search--混合检索测试)
   - 7.10 [PUT `/admin/laws/chunks/{chunk_id}` — 更新分块](#710-put-adminlawschunkschunk_id--更新分块)
   - 7.11 [POST `/admin/laws/{id}/reprocess` — 重新处理文档](#711-post-adminlawsidreprocess--重新处理文档)
   - 7.12 [DELETE `/admin/laws/chunks/{chunk_id}` — 删除分块](#712-delete-adminlawschunkschunk_id--删除分块)
8. [数据库设计](#8-数据库设计)
9. [已知问题与 Bug](#9-已知问题与-bug)
10. [安全风险](#10-安全风险)
11. [待开发功能（TODO）](#11-待开发功能todo)

---

## 1. 功能概述

`/admin/laws` 是 NeikongAI 平台的 **法律文档管理中心**，承担以下核心职责：

| 功能域 | 说明 |
|--------|------|
| 法律层级导航 | 用卡片展示宪法/法律/行政法规/部门规章/地方法规 5 个层级，点击即可筛选 |
| 文档列表 | 分页展示所有法律文档，含处理状态、分块数、生效日期等核心字段 |
| 文档搜索 | 支持按名称关键词搜索，支持按法律层级筛选 |
| 文档上传 | 支持 PDF/Word/TXT，提交后异步处理（分块 + 向量化） |
| 进度追踪 | 上传后自动轮询处理状态，实时进度条展示 |
| 文档删除 | 二次确认后删除文档及其全部分块 |
| 文档重处理 | 对失败文档可触发重新分块和向量化 |
| 文档详情 | 查看文档元信息及所有分块内容 |
| 分块查看 | 弹窗显示分块完整内容、关键词、条文详情 |
| 分块编辑 | UI 已实现，保存逻辑**未接入后端**（开发中） |
| 分块标记无效 | UI 已实现，后端逻辑**未实现** |

---

## 2. 整体架构

```
浏览器
  ├── /admin/laws                 → LawsList.vue（列表+上传）
  │     ↕ Axios HTTP              frontend/src/api/laws.js
  └── /admin/laws/:id             → LawDetail.vue（详情+分块管理）
        ↕ Axios HTTP              frontend/src/api/laws.js

                    ↕ REST API
                    
FastAPI 后端                      backend/app/routers/admin_laws.py
  ├── POST   /admin/laws/upload   上传+异步处理
  ├── GET    /admin/laws          分页列表
  ├── GET    /admin/laws/{id}     文档详情
  ├── GET    /admin/laws/{id}/chunks    分块列表
  ├── GET    /admin/laws/chunks/{id}    分块详情
  ├── DELETE /admin/laws/{id}     删除文档
  ├── GET    /admin/laws/{id}/logs      处理日志
  ├── POST   /admin/laws/test-search    混合检索测试
  ├── PUT    /admin/laws/chunks/{id}    更新分块+重新向量化
  ├── POST   /admin/laws/{id}/reprocess 重新处理
  └── DELETE /admin/laws/chunks/{id}   删除分块

                    ↕ psycopg2 直连
                    
PostgreSQL + pgvector
  ├── legal_documents   文档主表
  ├── legal_chunks      分块表（含 vector(1536) embedding）
  ├── ai_law_units      AI 合规单元分析结果
  └── document_processing_log  每步处理日志

                    ↕ DashScope API
                    
通义千问 / text-embedding-v1
  ├── text-embedding-v1  文本向量化（1536 维）
  └── qwen-turbo         关键词提取 / 合规单元分析
```

---

## 3. 路由配置

**文件**：`frontend/src/router/index.js`

```js
// 法律文档列表
{
  path: 'laws',
  name: 'AdminLaws',
  component: () => import('@/views/admin/LawsList.vue'),
  meta: { title: '法律分类管理 - 内控AI' }
}

// 文档详情（动态路由）
{
  path: 'laws/:id',
  name: 'AdminLawDetail',
  component: () => import('@/views/admin/LawDetail.vue'),
  meta: { title: '文档详情 - 内控AI' }
}
```

- 两个路由均属于 `/admin` 布局（`AdminLayout.vue`），位于侧边栏导航内
- **路由守卫**只设置页面标题，不做任何权限校验（`next()` 直接放行）

---

## 4. 前端详情：`/admin/laws` 列表页

**文件**：`frontend/src/views/admin/LawsList.vue`（841 行）

### 4.1 页面布局结构

```
┌─────────────────────────────────────────────────────────┐
│  页面标题卡片：法律文档管理                               │
└─────────────────────────────────────────────────────────┘
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ L5   │ │ L4   │ │ L3   │ │ L2   │ │ L1   │
│ 宪法 │ │ 法律 │ │行政  │ │部门  │ │地方  │
│      │ │      │ │法规  │ │规章  │ │法规  │  ← 法律层级卡片
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘
┌─────────────────────────────────────────────────────────┐
│  工具栏：当前层级提示 | 搜索框 | 层级下拉 | 搜索/重置    │
│                                     上传法律文档按钮 →   │
└─────────────────────────────────────────────────────────┘
（如有处理中文档，显示进度条 Alert）
┌─────────────────────────────────────────────────────────┐
│  文档列表表格                                             │
│  ID | 法律名称 | 层级 | 处理状态 | 生效日期 | 分块数 | 时间 | 操作 │
│  ...                                                      │
│  分页控件                                                │
└─────────────────────────────────────────────────────────┘
（点击"上传"弹出对话框）
```

### 4.2 法律层级卡片

**数据来源**：组件内硬编码（`levelCards` 数组）

| 层级值 | 标题 | 短标签 | 描述 |
|--------|------|--------|------|
| 5 | 宪法 | 最高层级 | 国家根本法，作为检索与合规判断的最终兜底 |
| 4 | 法律 | 国家法律 | 全国人大及其常委会制定，作为核心法源 |
| 3 | 行政法规 | 国务院 | 国务院制定，承接法律并细化执行要求 |
| 2 | 部门规章 | 部委规则 | 财政部、司法部等部门制定，贴近业务执行 |
| 1 | 地方法规 | 地方适用 | 各地区法规文件，适用于属地化合规管理 |

**交互逻辑**：
- 点击卡片 → `selectLevelCard(level)` → 更新 `selectedLevel` + 重置页码 + 调用 `fetchData()`
- 当前选中卡片高亮（`active` 样式：蓝色边框 + 阴影）
- 层级卡片标签由 `info` 型变为 `primary` 型

**响应式布局**：
```
xs: 24列（手机全宽）
sm: 12列（平板2列）
md/lg: 8列（桌面3列）
xl: 4列（大屏5列，每列约20%宽）
```

### 4.3 搜索与筛选栏

| 控件 | 绑定变量 | 触发事件 |
|------|----------|----------|
| 搜索框（文字搜索） | `searchQuery` | `@keyup.enter` → `handleSearch()` |
| 层级下拉 | `selectedLevel` | `@change` → `handleLevelChange()` |
| 搜索按钮 | — | `@click` → `handleSearch()` |
| 重置按钮 | — | `@click` → `resetFilters()` 清空搜索+层级+翻页 |
| 上传按钮 | — | `@click` → `openUploadDialog()` |

**当前层级提示**：选中层级后，工具栏左侧显示绿色 `el-alert` 提示"当前层级：XXX"

### 4.4 文档列表表格

**数据源**：`tableData`（由 `fetchData()` 异步填充）

| 列名 | 字段 | 宽度 | 说明 |
|------|------|------|------|
| ID | `id` | 80px | 数据库主键 |
| 法律名称 | `title` | min-width:260px | 文档标题 |
| 法律层级 | `legal_level_name` | 120px | 宪法/法律/行政法规/部门规章/地方法规 |
| 处理状态 | `processed_status` | 120px | Tag 颜色标注（见下表） |
| 生效日期 | `effective_date` | 140px | 原始字符串直接显示 |
| 分块数 | `chunks_count` | 100px | 向量化后的条文块总数 |
| 上传时间 | `uploaded_at` | 180px | `new Date(x).toLocaleString('zh-CN')` 格式化 |
| 操作 | — | 180px，fixed:right | 详情/删除/重新分块 |

**处理状态 Tag 颜色**：

| `processed_status` 值 | Tag 类型 | 显示文字 |
|----------------------|----------|----------|
| `completed` | success（绿色） | 已完成 |
| `processing` | warning（橙色） | 处理中 |
| `pending` | info（蓝色） | 等待中 |
| 其他/failed | danger（红色） | 失败 |

**操作列逻辑**：
- **详情**：`viewDetail(id)` → `router.push('/admin/laws/${id}')`
- **删除**：`handleDelete(row)` → `ElMessageBox.confirm` 二次确认 → `deleteLaw(row.id)` → 刷新列表
- **重新分块**（仅 `failed` 状态显示）：`handleReprocess(row)` → 确认 → `reprocessDocument(id)` → 刷新

**分页参数**：

| 参数 | 默认值 | 可选值 |
|------|--------|--------|
| `currentPage` | 1 | — |
| `pageSize` | 20 | 10 / 20 / 50 / 100 |
| `total` | 0 | 由后端返回 |

分页变化（`@current-change`、`@size-change`）均触发 `fetchData()`。

### 4.5 上传对话框

**触发**：点击工具栏"上传法律文档"按钮

**表单字段**：

| 字段 | 控件 | 必填 | 说明 |
|------|------|------|------|
| 法律名称 | el-input | ✅ | blur 触发校验 |
| 法律层级 | el-select | ✅ | change 触发校验 |
| 制定机关 | el-select | 仅层级=2（部门规章）时必填 | 固定选项：财政部/司法部/教育部/人社部/国家税务总局/国资委/其他 |
| 地区 | el-select（支持 filterable） | 仅层级=1（地方法规）时必填 | 全国 31 个省市自治区 |
| 生效日期 | el-date-picker | 否 | `YYYY-MM-DD` 格式 |
| 文件 | el-upload（拖拽+点击） | ✅（代码校验，非表单规则） | .pdf / .docx / .doc / .txt，单文件，50MB |

**动态校验规则**（`currentUploadRules` computed）：
```js
// 基础规则（始终有效）
title: [{ required: true }]
legal_level: [{ required: true }]

// 部门规章时追加
issuing_authority: [{ required: true }]  // legal_level === 2

// 地方法规时追加
region: [{ required: true }]  // legal_level === 1
```

**上传流程**：
```
点击"上传"
  → validate()（表单校验）
  → 检查 file 是否已选择
  → 构建 FormData（file + title + legal_level + 可选字段）
  → 关闭对话框
  → 追加处理中 Banner（uploadingDocs）
  → 调用 uploadLaw(formData)（POST multipart/form-data）
  → 拿到 document_id
  → 调用 startPolling(uploadId, document_id)
  → 刷新列表
```

**注意**：`issuing_authority` 和 `region` 字段通过 `formData.append()` 追加，但后端 `POST /admin/laws/upload` 接口**未声明这两个 Form 字段**，目前这两个值会被忽略（后端不读取）。

### 4.6 上传进度轮询

```
startPolling(uploadId, documentId)
  → 最多轮询 60 次，每次间隔 3 秒（最长等待 3 分钟）
  → 调用 getLawDetail(documentId) 获取 processed_status
  → 状态变化：
      completed  → progress=100, status=success, 3秒后从 Banner 移除
      failed     → progress=100, status=exception, 5秒后从 Banner 移除
      processing → progress 每次+5（上限90）
      pending    → progress 每次+3（上限70）
  → 超时（60次）→ status=exception，提示"处理超时"
```

**视觉效果**：进度条位于页面顶部 Alert 区域，颜色随状态变化（`warning`/`success`/`exception`）

### 4.7 数据流与状态管理

```
onMounted → fetchData()
              ↓
           getLawsList({ page, per_page, search, legal_level })
              ↓
           GET /api/admin/laws?page=...&per_page=...&search=...&legal_level=...
              ↓
           tableData.value = res.data
           total.value = res.total
```

**响应式变量清单**：

| 变量 | 类型 | 说明 |
|------|------|------|
| `searchQuery` | `ref('')` | 搜索关键词 |
| `selectedLevel` | `ref(null)` | 当前选中层级 |
| `loading` | `ref(false)` | 表格 loading 状态 |
| `tableData` | `ref([])` | 表格数据 |
| `currentPage` | `ref(1)` | 当前页 |
| `pageSize` | `ref(20)` | 每页数量 |
| `total` | `ref(0)` | 总记录数 |
| `dialogVisible` | `ref(false)` | 上传对话框显示 |
| `uploading` | `ref(false)` | 上传按钮 loading |
| `uploadingDocs` | `ref([])` | 处理中文档列表（进度条数组） |
| `uploadForm` | `ref({...})` | 上传表单数据 |
| `selectedLevelName` | `computed` | 当前选中层级的中文名 |
| `currentUploadRules` | `computed` | 动态表单校验规则 |

---

## 5. 前端详情：`/admin/laws/:id` 文档详情页

**文件**：`frontend/src/views/admin/LawDetail.vue`（1165 行）

### 5.1 页面布局结构

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回   法律文档详情                                    │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  文档标题                               [处理状态 Tag]   │
│──────────────────────────────────────────────────────── │
│  法律层级 | 文号 | 生效日期 | 上传时间 | 原始文件名 | 分块数│
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  文档分块（N 个）                                         │
│  序号 | 类型 | 章节 | 条款 | 内容（前100字） | 向量 | 操作│
│  ─── [查看] [编辑] [标记无效]                             │
│  ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 文档元信息卡片

使用 `el-descriptions` 二列展示：

| 字段 | 来源 |
|------|------|
| 法律层级 | `lawDetail.legal_level_name`（后端 CASE 转换） |
| 文号 | `lawDetail.doc_number`（无则显示 `-`） |
| 生效日期 | `lawDetail.effective_date` |
| 上传时间 | `lawDetail.uploaded_at`（格式化为本地时间） |
| 原始文件名 | `lawDetail.original_filename` |
| 分块数量 | `lawDetail.chunks_count` |

卡片 Header 显示文档标题 + 处理状态 Tag（与列表页颜色规则一致）。

### 5.3 分块列表表格

**数据源**：`chunks`（由 `getLawChunks(id)` 填充）

| 列名 | 字段 | 宽度 | 说明 |
|------|------|------|------|
| 序号 | `chunk_index` | 80px | 分块在文档中的顺序号 |
| 类型 | `chunk_type` | 120px | `single_article`→"单条"，其他→"条组" |
| 章节 | `chapter_number` | 100px | 例：第一章 |
| 条款 | `article_start`/`article_end` | 180px | 单条：第X条；条组：第X条 至 第Y条 |
| 内容 | `chunk_text` | min-width:300px | 仅显示前 100 字符+"..." |
| 向量 | — | 100px | `has_embedding !== false` → ✓（绿色），否则 -（灰色） |
| 关键词 | — | — | **隐藏**（`v-if="false"`，未来可启用） |
| 操作 | — | 240px，fixed:right | 查看 / 编辑 / 标记无效 |

### 5.4 查看分块对话框（弹窗）

点击"查看"按钮 → `viewChunk(chunk)` → 使用 `ElMessageBox.alert` 以 HTML 字符串渲染：

弹窗内容包含：
1. **元信息区**（灰底卡片）：类型、序号、章节、条款范围、字数、条文数量
2. **条组整体关键词**：蓝色标签（`#ecf5ff` 背景）
3. **完整内容**：`\n` 替换为 `<br/>`，带蓝色左边框
4. **每条详细关键词**（如有 `articles_detail`）：显示每条条文编号、内容摘要（前50字）、条文级关键词（绿色标签）

```js
ElMessageBox.alert(htmlContent, `查看分块内容 - ${chunk.article_start}`, {
  confirmButtonText: '关闭',
  dangerouslyUseHTMLString: true,     // ⚠️ XSS 风险
  customClass: 'chunk-view-dialog',
  showClose: true
})
```

> ⚠️ **安全风险**：使用 `dangerouslyUseHTMLString: true` 直接将数据库内容作为 HTML 渲染，若数据库中存在恶意内容可触发 XSS 攻击。

### 5.5 编辑分块对话框

点击"编辑"按钮 → 先弹出警告确认（`ElMessageBox.confirm`） → 确认后打开编辑表单对话框。

**表单字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| 章节 | el-input | 例：第一章 |
| 起始条款 | el-input | 例：第一条 |
| 结束条款 | el-input | 单条时留空 |
| 分块内容 | el-textarea（12行） | 最大 5000 字，显示字数统计 |

**保存逻辑**（`saveEdit`）：
```js
const saveEdit = async () => {
  // TODO: 调用后端 API 保存修改
  ElMessage.info('保存功能开发中...')
  // await updateChunk(currentChunk.value.id, editForm.value)  ← 已注释，未实装
}
```

> ⚠️ **当前保存功能不可用**，点击"保存修改"只弹出"保存功能开发中..."提示。

**模板重复 Bug**：
> `LawDetail.vue` 存在严重的 **模板代码重复** 问题：编辑分块对话框的 `<el-dialog>` 模板在 `<template>` 中被 **重复插入了 9 次**（分布在各个 `<template #default>` slot 内），导致文件从逻辑上约 200 行膨胀到 1165 行。这是典型的开发期调试残留，不影响实际渲染（Vue 最终只渲染顶层的 `v-model` 控制的弹窗）但会导致：
> - IDE 解析性能下降
> - 代码维护极其困难
> - 可能有隐藏的渲染行为问题

### 5.6 数据流与状态管理

```
onMounted → fetchData()
              ↓
           getLawDetail(id)  →  GET /api/admin/laws/{id}
              ↓
           lawDetail.value = detail
              ↓
           getLawChunks(id)  →  GET /api/admin/laws/{id}/chunks
              ↓
           chunks.value = chunksData.chunks
```

**响应式变量清单**：

| 变量 | 类型 | 说明 |
|------|------|------|
| `loading` | `ref(false)` | 文档详情卡片 loading |
| `lawDetail` | `ref({})` | 文档详情数据 |
| `chunks` | `ref([])` | 分块数据列表 |
| `editDialogVisible` | `ref(false)` | 编辑对话框显示 |
| `editForm` | `ref({})` | 编辑表单当前数据 |
| `currentChunk` | `ref(null)` | 当前正在编辑的分块 |

---

## 6. API 客户端封装（`laws.js`）

**文件**：`frontend/src/api/laws.js`

| 方法名 | HTTP 方法 | 路径 | Content-Type | 说明 |
|--------|-----------|------|--------------|------|
| `uploadLaw(formData)` | POST | `/admin/laws/upload` | multipart/form-data | 上传文档 |
| `getLawsList(params)` | GET | `/admin/laws` | — | 获取列表（query string） |
| `getLawDetail(id)` | GET | `/admin/laws/${id}` | — | 获取详情 |
| `getLawChunks(id)` | GET | `/admin/laws/${id}/chunks` | — | 获取分块列表 |
| `getChunkDetail(id)` | GET | `/admin/laws/chunks/${id}` | — | 获取分块详情（**未在前端使用**） |
| `deleteLaw(id)` | DELETE | `/admin/laws/${id}` | — | 删除文档 |
| `getLawLogs(id)` | GET | `/admin/laws/${id}/logs` | — | 获取处理日志（**未在前端使用**） |
| `testSearch(data)` | POST | `/admin/laws/test-search` | application/x-www-form-urlencoded | 混合检索测试（**未在前端使用**） |
| `updateChunk(id, data)` | PUT | `/admin/laws/chunks/${id}` | application/x-www-form-urlencoded | 更新分块（**已封装未调用**） |
| `deleteChunk(id)` | DELETE | `/admin/laws/chunks/${id}` | — | 删除分块（**已封装未调用**） |
| `reprocessDocument(id)` | POST | `/admin/laws/${id}/reprocess` | — | 重新处理 |

**Axios 实例配置**（`api/request.js`）：
- `baseURL: '/api'`（通过 Vite dev server 或 Nginx 代理到后端 8000 端口）
- `timeout: 600000`（10 分钟，适配文档处理等长任务）
- 请求拦截：自动注入 `Authorization: Bearer <token>`（来自 localStorage）
- 响应拦截：统一处理 401/403/404/500 错误

---

## 7. 后端 API 详情（`admin_laws.py`）

**文件**：`backend/app/routers/admin_laws.py`（708 行）  
**Router 前缀**：`/admin/laws`  
**认证状态**：⚠️ 所有端点的认证依赖均已注释（`# current_user: dict = Depends(require_admin)`），**无需任何身份验证**  
**文件上传目录**：`/var/www/neikongai/uploads/laws`（硬编码，启动时自动创建）

### 7.1 接口总表

| 方法 | 路径 | 认证 | 主要用途 |
|------|------|------|----------|
| POST | `/upload` | ❌无 | 上传并异步处理文档 |
| GET  | `` | ❌无 | 获取文档列表（分页+筛选） |
| GET  | `/{id}` | ❌无 | 获取文档详情 |
| GET  | `/{id}/chunks` | ❌无 | 获取文档分块列表 |
| GET  | `/chunks/{id}` | ❌无 | 获取单个分块详情 |
| DELETE | `/{id}` | ❌无 | 删除文档（级联） |
| GET  | `/{id}/logs` | ❌无 | 获取处理日志 |
| POST | `/test-search` | ❌无 | 混合检索测试 |
| PUT  | `/chunks/{id}` | ❌无 | 更新分块内容+重新向量化 |
| POST | `/{id}/reprocess` | ❌无 | 重新处理文档 |
| DELETE | `/chunks/{id}` | ❌无 | 删除单个分块 |

### 7.2 POST `/admin/laws/upload` — 上传文档

**参数**（Form）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | UploadFile | ✅ | .pdf/.docx/.doc/.txt |
| `title` | str | ✅ | 法律名称 |
| `legal_level` | int | ✅ | 1-5 |
| `doc_number` | str | 否 | 文号 |
| `effective_date` | str | 否 | 生效日期字符串 |

> ⚠️ 前端发送的 `issuing_authority`（制定机关）和 `region`（地区）字段 **后端未声明接收**，实际被忽略。

**处理流程**：
```
1. 校验扩展名（白名单：.pdf/.docx/.doc/.txt）
2. 生成时间戳文件名（防覆盖）: {timestamp}_{original_name}
3. 保存到 /var/www/neikongai/uploads/laws/
4. 计算 SHA-256 文件哈希
5. INSERT INTO legal_documents（status=pending, uploaded_by=1 硬编码）
6. background_tasks.add_task(process_document_task, document_id, file_path)
7. 立即返回 { success, document_id, message }
```

**异步任务 `process_document_task`**：
```
1. UPDATE processed_status = 'processing'
2. await doc_processor.process_document(document_id, file_path)
   （完整 5 步流水线：提取→结构→分块→向量化→入库）
```

**返回**：
```json
{ "success": true, "document_id": 123, "message": "文档上传成功，正在后台处理..." }
```

### 7.3 GET `/admin/laws` — 获取文档列表

**参数**（Query String）：
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `legal_level` | int | 无 | 按层级筛选 |
| `status` | str | 无 | 按 `status` 字段筛选（注意：非 `processed_status`） |
| `search` | str | 无 | `title ILIKE '%keyword%'` |
| `page` | int | 1 | 页码 |
| `per_page` | int | 20 | 每页数量 |

> ⚠️ **接口 Bug**：`status` 参数对应的是 `legal_documents.status`（active/inactive）字段，而前端实际上没有使用此参数，没有影响，但名字容易混淆（`processed_status` 才是处理进度状态）。

**SQL 查询逻辑**：
```sql
-- 支持动态 WHERE 条件
SELECT id, title, legal_level, doc_number, effective_date,
       status, processed_status, chunks_count, uploaded_at,
       CASE legal_level WHEN 5 THEN '宪法' ... END as legal_level_name
FROM legal_documents
WHERE [legal_level=?] [AND status=?] [AND title ILIKE ?]
ORDER BY uploaded_at DESC
LIMIT ? OFFSET ?
```

**返回**：
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### 7.4 GET `/admin/laws/{id}` — 获取文档详情

返回字段：`id, title, legal_level, doc_number, effective_date, status, original_filename, file_path, processed_status, chunks_count, uploaded_at, structure_json, legal_level_name`

> ⚠️ 返回了 `file_path`（服务器真实路径），客户端可看到服务器文件系统路径，存在信息泄露风险。

### 7.5 GET `/admin/laws/{id}/chunks` — 获取文档分块

返回字段：`id, chunk_index, chunk_text, chunk_type, chapter_number, chapter_title, section_number, section_title, article_start, article_end, articles_included, keywords, cited_count`

> 注意：不包含 `embedding`（向量）字段，避免传输大量数据。

### 7.6 GET `/admin/laws/chunks/{chunk_id}` — 获取分块详情

- JOIN `legal_documents` 获取 `document_title` 和 `legal_level_name`
- `embedding` 字段替换为描述字符串 `"[向量维度: 1536]"`

### 7.7 DELETE `/admin/laws/{id}` — 删除文档

```
1. SELECT file_path 查找文件路径
2. DELETE FROM legal_documents WHERE id=?（级联删除分块和处理日志）
3. os.remove(file_path) 删除物理文件
```

**返回**：`{ "success": true, "message": "删除成功" }`

### 7.8 GET `/admin/laws/{id}/logs` — 获取处理日志

字段：`id, step, status, details, processing_time_ms, error_message, created_at`  
按 `created_at` 正序排列（可复现整个处理过程）

**step 枚举值**（由文档处理器写入）：
- `extract_text` — 文本提取
- `parse_structure` — 结构识别
- `chunk` — 智能分块
- `vectorize` — 向量化
- `save_to_db` — 入库
- `processing` — 异常时的总错误日志

### 7.9 POST `/admin/laws/test-search` — 混合检索测试

**参数**（Form）：`query` (str)、`top_k` (int, 默认5)

**流程**：
1. `QueryUnderstandingService.understand_query(query)` → 提取关键词
2. `EmbeddingService.get_single_embedding(retrieval_query)` → 向量化
3. 执行联合查询：  
   关键词数组命中（`keywords && text[]`） **优先** + 向量相似度排序（`<=>` 算子）
4. 返回 `{ query, query_profile, results }`

> 该接口主要用于**开发调试**，前端没有调用入口（`laws.js` 中有封装但 UI 未接入）。

### 7.10 PUT `/admin/laws/chunks/{chunk_id}` — 更新分块

**参数**（Form）：`chunk_text`, `chapter_number`, `article_start`, `article_end`

**流程**：
1. 验证分块存在
2. `EmbeddingService.get_single_embedding(chunk_text)` → 生成新向量（1536维）
3. `UPDATE legal_chunks SET chunk_text, chapter_number, article_start, article_end, embedding WHERE id=?`

> 接口完整可用，但前端 `saveEdit()` 函数将其调用注释掉了（`// await updateChunk(...)`）。

### 7.11 POST `/admin/laws/{id}/reprocess` — 重新处理文档

**流程**：
1. 查找文档（含 `file_path`）
2. `DELETE FROM legal_chunks WHERE document_id=?`（清空旧分块）
3. `DELETE FROM document_processing_log WHERE document_id=?`（清空旧日志）
4. `UPDATE processed_status='pending', chunks_count=0, full_text='', structure_json=NULL`
5. `background_tasks.add_task(process_document_task, document_id, file_path)`

### 7.12 DELETE `/admin/laws/chunks/{chunk_id}` — 删除分块

```
1. 查找分块（获取 document_id）
2. DELETE FROM legal_chunks WHERE id=?
3. 更新 legal_documents.chunks_count（重新 COUNT）
```

> 前端 `laws.js` 有 `deleteChunk()` 封装，但 UI 中无调用入口。

---

## 8. 数据库设计

### `legal_documents` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | SERIAL PK | 主键 |
| `title` | VARCHAR | 法律名称 |
| `legal_level` | INTEGER | 1-5（地方法规到宪法） |
| `doc_number` | VARCHAR | 文号 |
| `effective_date` | VARCHAR/DATE | 生效日期 |
| `original_filename` | VARCHAR | 上传原始文件名 |
| `file_path` | VARCHAR | 服务器文件路径 |
| `file_hash` | VARCHAR(64) | SHA-256 哈希 |
| `full_text` | TEXT | 提取的全文 |
| `structure_json` | JSON | 章/节/条结构解析结果 |
| `status` | VARCHAR | `active` / `inactive` |
| `processed_status` | VARCHAR | `pending`/`processing`/`completed`/`failed` |
| `chunks_count` | INTEGER | 分块总数 |
| `uploaded_by` | INTEGER FK → users | 上传者（**当前硬编码为 1**） |
| `uploaded_at` | TIMESTAMP | 上传时间 |
| `updated_at` | TIMESTAMP | 最后更新时间 |

### `legal_chunks` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | SERIAL PK | 主键 |
| `document_id` | INTEGER FK | 所属文档 |
| `legal_level` | INTEGER | 冗余存储层级（加速检索） |
| `chunk_index` | INTEGER | 分块序号 |
| `chunk_text` | TEXT | 分块文本内容 |
| `chunk_hash` | VARCHAR(64) | SHA-256 哈希 |
| `chunk_type` | VARCHAR | `single_article` / `article_group` / `attachment` |
| `chapter_number` | VARCHAR | 章节编号 |
| `chapter_title` | VARCHAR | 章节标题 |
| `section_number` | VARCHAR | 节编号 |
| `section_title` | VARCHAR | 节标题 |
| `article_start` | VARCHAR | 起始条款（如"第三条"） |
| `article_end` | VARCHAR | 结束条款 |
| `articles_included` | TEXT[] | 包含的条款编号数组 |
| `has_references` | BOOLEAN | 是否含引用条款 |
| `reference_articles` | TEXT[] | 被引用条款数组 |
| `expanded_text` | TEXT | 展开引用后的文本 |
| `keywords` | TEXT[] | AI 提取的关键词 |
| `articles_detail` | JSON | 每条条文详细关键词 |
| `articles_count` | INTEGER | 条文数 |
| `embedding` | vector(1536) | pgvector 向量（1536维） |
| `cited_count` | INTEGER | 被其他分块引用次数 |

### `document_processing_log` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | SERIAL PK | 主键 |
| `document_id` | INTEGER FK | 所属文档 |
| `step` | VARCHAR | 处理步骤名 |
| `status` | VARCHAR | `processing` / `success` / `failed` |
| `details` | JSON | 步骤详情（字符数、分块数等） |
| `processing_time_ms` | INTEGER | 步骤耗时（毫秒） |
| `error_message` | TEXT | 错误信息 |
| `created_at` | TIMESTAMP | 记录时间 |

---

## 9. 已知问题与 Bug

### 🔴 高优先级

| 编号 | 位置 | 问题描述 |
|------|------|----------|
| B-1 | `LawDetail.vue` | 编辑分块对话框 `<el-dialog>` 模板在 `<template>` 中**重复嵌入 9 次**，是严重的代码冗余，需重构 |
| B-2 | `LawDetail.vue` `saveEdit()` | 保存分块功能**未实装**，调用 `updateChunk` 的代码被注释，点击只弹出"开发中"提示 |
| B-3 | `LawDetail.vue` `markInvalid()` | 标记无效功能**未实装**，仅弹出"开发中"提示，后端也无对应接口 |
| B-4 | `admin_laws.py` `upload_law` | `uploaded_by` **硬编码为 1**，无法追溯实际上传者 |
| B-5 | `admin_laws.py` `upload_law` | 前端发送的 `issuing_authority`（制定机关）和 `region`（地区）字段后端未接收，数据丢失 |

### 🟡 中优先级

| 编号 | 位置 | 问题描述 |
|------|------|----------|
| B-6 | `LawDetail.vue` `viewChunk()` | 使用 `dangerouslyUseHTMLString: true` 直接渲染数据库内容，存在 XSS 风险 |
| B-7 | `admin_laws.py` `get_law_detail` | 接口返回 `file_path`（服务器物理路径），存在信息泄露 |
| B-8 | `admin_laws.py` `get_laws` | `status` 参数说明不清晰（对应的是 `active/inactive`，非 `processed_status`） |
| B-9 | `LawsList.vue` `handleUpload` | 文件大小限制（50MB）仅在 UI 提示中说明，未做实际 JS 校验，后端也无大小限制 |
| B-10 | `LawDetail.vue` | `getLawLogs`（处理日志）接口已封装但页面未展示处理日志，用户无法直观看到失败原因 |

### 🟢 低优先级

| 编号 | 位置 | 问题描述 |
|------|------|----------|
| B-11 | `LawsList.vue` | `formatShortDate()` 直接返回原始字符串（`return dateStr`），未做格式化 |
| B-12 | `laws.js` | `getChunkDetail`, `getLawLogs`, `testSearch`, `deleteChunk` 已封装但无 UI 调用入口 |
| B-13 | `LawDetail.vue` | 关键词列（Keywords）列用 `v-if="false"` 隐藏，可通过改 `true` 快速启用 |

---

## 10. 安全风险

| 风险 | 等级 | 说明 |
|------|------|------|
| 全部 API 无认证 | 🔴 高 | 所有 `Depends(require_admin)` 均被注释，任何人可上传/删除/修改法律文档 |
| 前端路由无权限检查 | 🔴 高 | `router.beforeEach` 直接 `next()`，任何人可访问 `/admin/laws` |
| `dangerouslyUseHTMLString` | 🟡 中 | 数据库内容作为 HTML 渲染，若有恶意数据可触发 XSS |
| 返回服务器文件路径 | 🟡 中 | `GET /admin/laws/{id}` 返回 `file_path`，泄露服务器目录结构 |
| 文件上传无大小限制 | 🟡 中 | 后端未校验上传文件大小，可上传超大文件消耗服务器资源 |
| `uploaded_by` 硬编码为 1 | 🟡 中 | 无法审计谁上传了哪些文档 |
| 本地文件系统存储 | 🟡 中 | 文件存储在服务器本地（非 MinIO），无备份，单点故障 |

---

## 11. 待开发功能（TODO）

### 🔴 必须完成（页面核心功能缺失）

- [ ] **实装分块编辑保存**：`saveEdit()` 中调用 `updateChunk(currentChunk.value.id, editForm.value)`，去掉注释
- [ ] **实装标记无效**：后端新增 `PATCH /admin/laws/chunks/{id}/invalid`（软删除，设 `is_valid=false`），前端调用
- [ ] **处理日志展示**：在文档详情页新增"处理日志"展开区域，调用 `getLawLogs(id)` 展示每步耗时

### 🟡 应当完成

- [ ] **制定机关/地区字段入库**：后端 `upload_law` 新增 `issuing_authority` 和 `region` Form 参数，写入数据库
- [ ] **上传者归因**：`uploaded_by` 改为从 JWT Token 解析实际用户 ID
- [ ] **文件大小校验**：后端加 `if file.size > 50 * 1024 * 1024: raise HTTPException(400)`
- [ ] **去掉 `file_path` 返回**：`get_law_detail` 接口不返回服务器路径
- [ ] **修复重复模板**：重构 `LawDetail.vue`，将对话框代码移到 `<template>` 根层级，移除冗余副本

### 🟢 优化建议

- [ ] 启用关键词列（将 `v-if="false"` 改为可选显示）
- [ ] 在列表页增加"失败原因"快速查看（tooltip 或弹窗展示最近一条错误日志）
- [ ] 为 `test-search` 混合检索测试功能增加 UI 入口（目前仅限开发人员通过 Swagger 调试）
- [ ] `uploaded_at` 列增加排序功能（`el-table-column :sortable="'custom'"`）
- [ ] 支持批量删除（`el-table` selection + 批量操作工具栏）

---

*本报告基于代码静态分析生成，完整覆盖 `/admin/laws` 页面所涉及的前端、后端和数据库层。*
