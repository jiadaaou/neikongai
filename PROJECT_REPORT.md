# NeikongAI 项目详情报告

> **报告生成时间**：2026-03-12  
> **当前分支**：`copilot/review-project-content`  
> **项目状态**：开发阶段（管理 API 认证已恢复，需要管理员 JWT token）

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [系统架构](#3-系统架构)
4. [目录结构](#4-目录结构)
5. [后端模块详情](#5-后端模块详情)
   - 5.1 [API 路由一览](#51-api-路由一览)
   - 5.2 [文档处理流水线](#52-文档处理流水线)
   - 5.3 [AI 服务层](#53-ai-服务层)
   - 5.4 [数据库 Schema](#54-数据库-schema)
6. [前端模块详情](#6-前端模块详情)
   - 6.1 [页面路由一览](#61-页面路由一览)
   - 6.2 [状态管理](#62-状态管理)
   - 6.3 [API 封装](#63-api-封装)
7. [环境配置](#7-环境配置)
8. [安全现状与风险](#8-安全现状与风险)
9. [代码质量评估](#9-代码质量评估)
10. [已知问题与 TODO](#10-已知问题与-todo)
11. [快速启动](#11-快速启动)

---

## 1. 项目概述

**NeikongAI**（内控 AI）是一套 **AI 驱动的企业合规管理平台**，核心功能为：

| 功能域 | 说明 |
|--------|------|
| 法律知识库 | 支持上传 PDF/Word/TXT 法律文件，自动解析条文结构、分块、向量化入库 |
| 合规问答 | 基于"分层法律向量检索 + 关键词召回 + 重排序"的证据驱动 RAG 架构，调用通义千问生成回答 |
| 行业准则管理 | 与法律文件类似的行业准则知识库，独立存储和检索 |
| 管理后台 | 超级管理员可管理法律文档、标准文档、企业账号、用户账号 |
| 企业用户端 | 企业用户通过 AI 对话方式咨询合规问题，查看历史记录 |

**当前阶段**：MVP 基础功能基本就绪，正处于联调和功能打磨阶段。

---

## 2. 技术栈

### 后端
| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 主语言 |
| FastAPI | 0.104.1 | Web 框架 / REST API |
| Uvicorn | 0.24.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.23 | ORM（部分使用，旧模型层） |
| psycopg2-binary | 2.9.9 | PostgreSQL 直连驱动（主要使用） |
| PostgreSQL + pgvector | — | 关系型数据库 + 向量扩展 |
| python-jose | 3.3.0 | JWT 签名与验证 |
| passlib[bcrypt] | 1.7.4 | 密码哈希 |
| dashscope | — | 通义千问大模型 API（文本生成 + Embedding） |
| PyPDF2 / pdfplumber | — | PDF 文本提取 |
| python-docx | 1.1.0 | Word 文本提取 |
| Redis | 5.0.1 | （已引入依赖，暂未使用） |
| MinIO | 7.2.0 | 对象存储（已引入依赖，暂未集成） |
| ChromaDB | 0.4.18 | 向量数据库（已引入依赖，实际向量存储在 PostgreSQL pgvector） |
| Alembic | 1.12.1 | 数据库迁移（已引入依赖，暂未使用迁移文件） |
| python-dotenv | 1.0.0 | 环境变量加载 |

### 前端
| 组件 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5.25 | 前端框架（Composition API） |
| Vite | 8.0.0-beta.13 | 构建工具 |
| Vue Router | 5.0.3 | 路由管理 |
| Pinia | 3.0.4 | 全局状态管理 |
| Element Plus | 2.13.3 | UI 组件库 |
| ECharts | 6.0.0 | 图表（向量监控页面使用） |
| Axios | 1.13.6 | HTTP 客户端 |

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                 │
│  ┌───────────────────────┐   ┌──────────────────────────────┐   │
│  │  管理后台 (Vue 3)      │   │  企业用户端 (Vue 3)           │   │
│  │  /admin/*             │   │  /company/*                  │   │
│  └──────────┬────────────┘   └──────────────┬───────────────┘   │
└─────────────┼──────────────────────────────┼───────────────────┘
              │  HTTP REST API (Axios)        │
              ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI 后端 (Python 3.11)                      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ /auth    │  │ /admin/  │  │ /ai/ask  │  │ /conversations │  │
│  │ 登录注册  │  │ laws /   │  │ 合规问答  │  │ 对话管理        │  │
│  │          │  │standards │  │          │  │                │  │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └───────────────┘  │
│                     │             │                              │
│  ┌──────────────────▼─────────────▼──────────────────────────┐  │
│  │                    服务层 (Services)                        │  │
│  │  TextExtractor → StructureParser → ChunkingService        │  │
│  │  → EmbeddingService → DocumentProcessor → LawAIAnalyzer   │  │
│  │  → EvidenceAnswerService ← QueryUnderstandingService       │  │
│  └─────────────────────┬──────────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────────┐
          ▼              ▼                  ▼
   ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐
   │ PostgreSQL  │ │  DashScope   │ │  本地文件系统    │
   │ + pgvector  │ │  通义千问 API │ │ /var/www/       │
   │ (主数据库)  │ │  (qwen-turbo │ │ neikongai/      │
   │             │ │   qwen-max   │ │ uploads/        │
   │ legal_docs  │ │   text-emb)  │ └─────────────────┘
   │ legal_chunks│ └──────────────┘
   │ ai_law_units│
   │ users       │
   └─────────────┘
```

**核心数据流（RAG 合规问答）**：
```
用户提问
  → QueryUnderstandingService（qwen-turbo）：提取关键词、检索意图、业务领域
  → EmbeddingService（text-embedding-v1）：将检索查询向量化（1536 维）
  → PostgreSQL pgvector：① 关键词召回（ILIKE） ② 分层向量召回（5层各取 Top-5）
  → 合并去重 + 二次重排（关键词命中 / 义务句 / 法律层级权重）
  → 取 Top-3 证据片段
  → AIService（qwen-turbo）：根据证据生成回答
  → 返回给用户
```

---

## 4. 目录结构

```
neikongai/
├── .gitignore                  # 根目录 gitignore（新增）
├── README.md                   # 项目说明
├── PROJECT_REPORT.md           # 本报告
├── index.html                  # 主页静态入口
├── test-login.html             # 登录测试页面
│
├── backend/                    # FastAPI 后端
│   ├── .gitignore              # 后端 gitignore（新增）
│   ├── .env.example            # 环境变量示例（包含所有必需变量）
│   ├── requirements.txt        # Python 依赖
│   ├── test_vector_retrieval.py # 向量检索调试脚本
│   └── app/
│       ├── main.py             # 应用入口，注册所有路由
│       ├── ai_service.py       # 通义千问对话服务
│       ├── schemas.py          # Pydantic 请求/响应 Schema
│       ├── api/                # （空模块，预留）
│       ├── core/
│       │   ├── database.py     # SQLAlchemy 引擎 + psycopg2 连接工厂
│       │   └── init_db.py      # 创建表结构脚本
│       ├── models/
│       │   └── models.py       # SQLAlchemy ORM 模型
│       ├── routers/            # API 路由层
│       │   ├── auth.py         # 认证：注册/登录/me
│       │   ├── chat.py         # 对话：conversations + messages
│       │   ├── files.py        # 文件：上传/列表（stub）
│       │   ├── users.py        # 用户：获取 profile
│       │   ├── ai_test.py      # AI 连通性测试
│       │   ├── ai_ask.py       # AI 合规问答（主入口）
│       │   ├── query_understanding.py  # 问题理解接口
│       │   ├── admin_laws.py   # 法律文档管理（全 CRUD + 检索）
│       │   └── admin_standards.py  # 行业准则管理（全 CRUD）
│       ├── services/           # 业务服务层
│       │   ├── text_extractor.py           # PDF/Word/TXT 文本提取
│       │   ├── text_extractor_with_table.py # 含表格的 PDF 提取（扩展版）
│       │   ├── structure_parser.py         # 法律条文结构解析（章/节/条）
│       │   ├── ai_structure_analyzer.py    # AI 识别附件并转自然语言
│       │   ├── chunking_service.py         # 法律文档分块（一条一块）
│       │   ├── chunking_service_standards.py # 标准文档分块
│       │   ├── embedding_service.py        # DashScope text-embedding-v1 向量化
│       │   ├── document_processor.py       # 法律文档处理协调器
│       │   ├── document_processor_standards.py # 标准文档处理协调器
│       │   ├── law_ai_analyzer.py          # AI 法律条文合规单元分析
│       │   ├── query_understanding_service.py  # 用户问题理解（qwen-turbo）
│       │   └── evidence_answer_service.py  # 证据驱动 RAG 回答
│       └── utils/              # （空模块，预留）
│
├── frontend/                   # Vue 3 前端源码
│   ├── .gitignore
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js     # 路由配置
│       ├── stores/user.js      # Pinia 用户状态
│       ├── api/
│       │   ├── request.js      # Axios 实例（含 token 注入）
│       │   ├── laws.js         # 法律文档 API 封装
│       │   └── standards.js    # 标准文档 API 封装
│       ├── layouts/
│       │   ├── AdminLayout.vue     # 管理后台布局
│       │   └── CompanyLayout.vue   # 企业用户端布局
│       └── views/
│           ├── auth/
│           │   ├── LoginPage.vue
│           │   └── RegisterPage.vue
│           ├── admin/
│           │   ├── knowledge/
│           │   │   ├── Dashboard.vue       # 知识库仪表盘
│           │   │   ├── Hierarchy.vue       # 法律层级管理汇总
│           │   │   ├── HierarchyDetail.vue # 具体层级详情
│           │   │   ├── IndustryStandards.vue # 行业准则管理
│           │   │   └── VectorMonitor.vue   # 向量数据库监控
│           │   ├── LawsList.vue        # 法律文档列表
│           │   ├── LawDetail.vue       # 法律文档详情+分块管理
│           │   ├── StandardsList.vue   # 标准文档列表
│           │   ├── StandardDetail.vue  # 标准文档详情+分块管理
│           │   ├── CompaniesPage.vue   # 企业管理
│           │   └── UsersPage.vue       # 用户管理
│           ├── company/
│           │   ├── ChatPage.vue        # AI 对话问答
│           │   └── HistoryPage.vue     # 查询历史
│           └── public/
│               └── HomePage.vue        # 公开首页
│
├── frontend-dist/              # 前端构建产物（生产部署用）
├── homepage/                   # 独立首页静态文件
├── homepage-src/               # 首页 Vue 源码
├── css/                        # 全局 CSS
└── js/                         # 全局 JS
```

---

## 5. 后端模块详情

### 5.1 API 路由一览

#### 认证模块（`/` 前缀由路由器内部定义）
> **路由文件**：`backend/app/routers/auth.py`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/register` | 用户注册（用户名+邮箱+密码） | 无 |
| POST | `/login` | 登录，返回 JWT Bearer token | 无 |
| GET  | `/me` | 获取当前登录用户信息 | 需要 JWT |

**说明**：
- 密码使用 `bcrypt` 哈希存储
- JWT 有效期：30 分钟（`ACCESS_TOKEN_EXPIRE_MINUTES=30`，与 `.env` 中的 1440 分钟不一致，**存在配置冲突**）
- Token payload 包含 `sub`（用户名）、`user_id`、`role`

---

#### AI 合规问答（`/ai` 前缀）
> **路由文件**：`backend/app/routers/ai_ask.py`、`backend/app/routers/query_understanding.py`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/ai/ask` | 合规问答主接口（完整 RAG 流程） | ❌ 无 |
| POST | `/ai/query-understand` | 单独测试问题理解层 | ❌ 无 |
| GET  | `/ai/test` | 测试通义千问 API 连通性 | ❌ 无 |

**`/ai/ask` 返回结构**：
```json
{
  "success": true,
  "data": {
    "question": "...",
    "answer": "（AI 生成的合规回答）",
    "evidence": [
      {
        "chunk_id": 42,
        "law_title": "中华人民共和国劳动法",
        "article_start": "第三条",
        "chunk_text": "...",
        "rerank_score": 1.24,
        "legal_level": 4
      }
    ],
    "layer_results": { "5": [], "4": [...], "3": [], "2": [], "1": [] },
    "query_profile": {
      "question_type": "合规咨询",
      "business_domain": "用工",
      "keywords": ["劳动合同", "..."],
      "objects": [...],
      "behavior": "..."
    }
  }
}
```

---

#### 对话模块（`/conversations`、`/messages`）
> **路由文件**：`backend/app/routers/chat.py`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/conversations` | 创建新对话 | ✅ JWT |
| GET  | `/conversations` | 获取当前用户所有对话 | ✅ JWT |
| POST | `/messages` | 发送消息（通义千问回复） | ✅ JWT |
| GET  | `/conversations/{id}/messages` | 获取对话消息历史 | ✅ JWT |

---

#### 法律文档管理（`/admin/laws` 前缀）
> **路由文件**：`backend/app/routers/admin_laws.py`（708 行）  
> ✅ **所有端点已启用认证**，需要携带管理员 JWT token（`super_admin` 或 `company_admin` 角色）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/admin/laws/upload` | 上传法律文档，异步处理 | ✅ 管理员 JWT |
| GET  | `/admin/laws` | 分页列表（支持筛选：层级/状态/搜索） | ✅ 管理员 JWT |
| GET  | `/admin/laws/{id}` | 文档详情 | ✅ 管理员 JWT |
| GET  | `/admin/laws/{id}/chunks` | 文档分块列表 | ✅ 管理员 JWT |
| GET  | `/admin/laws/chunks/{chunk_id}` | 单个分块详情（含向量维度信息） | ✅ 管理员 JWT |
| DELETE | `/admin/laws/{id}` | 删除文档（级联删除分块+日志+文件） | ✅ 管理员 JWT |
| GET  | `/admin/laws/{id}/logs` | 文档处理日志 | ✅ 管理员 JWT |
| POST | `/admin/laws/test-search` | 混合检索测试 | ✅ 管理员 JWT |
| PUT  | `/admin/laws/chunks/{chunk_id}` | 更新分块文本并重新向量化 | ✅ 管理员 JWT |
| POST | `/admin/laws/{id}/reprocess` | 重新处理文档 | ✅ 管理员 JWT |
| DELETE | `/admin/laws/chunks/{chunk_id}` | 删除单个分块 | ✅ 管理员 JWT |

**法律层级定义**：
| 层级值 | 名称 |
|--------|------|
| 5 | 宪法 |
| 4 | 法律 |
| 3 | 行政法规 |
| 2 | 部门规章 |
| 1 | 地方法规 |

---

#### 行业准则管理（`/admin/standards` 前缀）
> **路由文件**：`backend/app/routers/admin_standards.py`（701 行）  
> ✅ **所有端点已启用认证**，需要管理员 JWT token

与法律文档管理接口结构完全对称，路径前缀为 `/admin/standards`，认证要求相同（`super_admin` 或 `company_admin`）。

---

#### 用户与文件模块
> **路由文件**：`users.py`、`files.py`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET  | `/profile` | 获取用户资料 | ✅ JWT |
| POST | `/upload` | 文件上传（**Stub，未实现**） | ✅ JWT |
| GET  | `/` | 文件列表（**Stub，未实现**） | ✅ JWT |

---

### 5.2 文档处理流水线

上传文件后，后台异步任务（`BackgroundTasks`）执行以下 5 步：

```
步骤 1：文本提取
  └── TextExtractor.extract(file_path)
      支持：.pdf（PyPDF2 + pdfplumber）、.docx（python-docx）、.txt（chardet 检测编码）
      输出：{ text: "全文", pages: [...], metadata: { total_pages, format, file_size } }

步骤 2：结构识别
  └── StructureParser.parse_structure(full_text, use_ai=False)
      规则提取：章（第X章）、节（第X节）、条（第X条）
      识别引用关系（依照/参照/按照/根据 本法第X条）
      识别附件/附则/附表
      输出：{ chapters, sections, articles, references, attachments }

步骤 2.5（可选）：AI 转换附加内容
  └── AIStructureAnalyzer.convert_attachment_to_natural_language()
      使用 qwen-max 将表格/附件转换为自然语言描述

步骤 3：智能分块
  ├── 策略1：有章节结构 → 一条一块（含章节元数据）
  ├── 策略2：无章节结构 → 一条一块
  └── 策略3：无结构文档 → 按字数分块（200~1000字）
  去重 + AI 关键词提取（qwen-turbo / qwen-max）

步骤 4：向量化
  └── EmbeddingService.get_embeddings(chunk_texts)
      调用 DashScope text-embedding-v1（1536 维）
      批量处理（每批最多 25 条）
      超长文本截断到 1800 字符

步骤 5：存入数据库
  ├── 写入 legal_chunks 表（含 pgvector embedding）
  └── 调用 LawAIAnalyzer.analyze_chunk()（qwen-turbo）
      提取：主体、行为、义务、禁止项、风险类型/等级、合规动作
      写入 ai_law_units 表
```

**每步记录处理日志**到 `document_processing_log` 表，包含耗时（毫秒）和错误信息。

---

### 5.3 AI 服务层

| 服务 | 模型 | 用途 |
|------|------|------|
| `AIService` | qwen-turbo | 通用对话，历史消息最多保留 10 轮 |
| `EmbeddingService` | text-embedding-v1 | 文本向量化，1536 维 |
| `QueryUnderstandingService` | qwen-turbo | 将用户问题解构为结构化检索 profile |
| `AIStructureAnalyzer` | qwen-max | 法律文档附件识别 + 自然语言转换 + 关键词提取 |
| `LawAIAnalyzer` | qwen-turbo | 法律条文合规单元分析 |
| `EvidenceAnswerService` | — | RAG 编排层（综合使用以上服务） |

**QueryUnderstandingService 输出示例**：
```json
{
  "question_type": "合规咨询",
  "business_stage": "事前",
  "business_domain": "财务",
  "objects": ["发票", "增值税"],
  "behavior": "开具",
  "retrieval_query": "企业开具增值税发票的合规要求",
  "keywords": ["发票", "增值税", "开具", "合规"]
}
```

---

### 5.4 数据库 Schema

#### 主要数据表（psycopg2 直连使用，不通过 ORM）

```sql
-- 法律文档表
legal_documents (
  id, title, legal_level, doc_number, effective_date,
  original_filename, file_path, file_hash, full_text,
  structure_json,           -- JSON: 章/节/条结构
  processed_status,         -- pending / processing / completed / failed
  chunks_count,             -- 分块总数
  status,                   -- active / inactive
  uploaded_by, uploaded_at, updated_at
)

-- 法律分块表（含向量）
legal_chunks (
  id, document_id, legal_level, chunk_index,
  chunk_text, chunk_hash, chunk_type,
  chapter_number, chapter_title,
  section_number, section_title,
  article_start, article_end, articles_included,
  has_references, reference_articles, expanded_text,
  keywords,                 -- text[]
  articles_detail,          -- JSON
  articles_count,
  embedding,                -- vector(1536)  ← pgvector
  cited_count
)

-- AI 合规单元表
ai_law_units (
  id, chunk_id, document_id,
  source_article, subject, behavior,
  obligation, prohibition,
  risk_type, risk_level, compliance_action,
  keywords,
  analysis_model, analysis_status, raw_ai_output,
  created_at, updated_at
)

-- 文档处理日志
document_processing_log (
  id, document_id, step, status,
  details,              -- JSON
  processing_time_ms, error_message,
  created_at
)

-- 标准文档（结构相同，表名为 standard_documents / standard_chunks）

-- 用户表（通过 ORM 也定义了，psycopg2 也直接操作）
users (
  id, username, email, hashed_password,
  full_name, phone, avatar_url,
  role,                 -- SUPER_ADMIN / COMPANY_ADMIN / COMPANY_USER
  company_id, is_active, is_verified, last_login,
  created_at, updated_at
)

-- ORM 定义的表（未迁移状态）
companies (id, name, code, contact_*, minio_*, chroma_*, is_active, storage_quota, ...)
documents  (id, title, filename, file_url, content, knowledge_base_type, company_id, ...)
```

**注意**：ORM 模型（`models.py`）与实际 SQL 直连使用的表名存在**不一致**：ORM 定义了 `documents`，而实际使用的是 `legal_documents` / `standard_documents`（直接通过 psycopg2 操作，无 ORM 映射）。

---

## 6. 前端模块详情

### 6.1 页面路由一览

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| `/` | — | 重定向到 `/admin/knowledge/dashboard` | 无 |
| `/login` | `LoginPage.vue` | 登录 | 公开 |
| `/register` | `RegisterPage.vue` | 注册 | 公开 |
| `/admin/knowledge/dashboard` | `Dashboard.vue` | 知识库仪表盘 | ⚠️ 无验证 |
| `/admin/knowledge/hierarchy` | `Hierarchy.vue` | 法律层级管理汇总 | ⚠️ 无验证 |
| `/admin/knowledge/hierarchy/:level` | `HierarchyDetail.vue` | 层级详情 | ⚠️ 无验证 |
| `/admin/knowledge/standards` | `IndustryStandards.vue` | 行业准则管理 | ⚠️ 无验证 |
| `/admin/knowledge/monitor` | `VectorMonitor.vue` | 向量数据库监控 | ⚠️ 无验证 |
| `/admin/laws` | `LawsList.vue` | 法律文档列表+上传 | ⚠️ 无验证 |
| `/admin/laws/:id` | `LawDetail.vue` | 文档详情、分块管理 | ⚠️ 无验证 |
| `/admin/standards` | `StandardsList.vue` | 标准文档列表+上传 | ⚠️ 无验证 |
| `/admin/standards/:id` | `StandardDetail.vue` | 标准文档详情 | ⚠️ 无验证 |
| `/admin/companies` | `CompaniesPage.vue` | 企业管理 | ⚠️ 无验证 |
| `/admin/users` | `UsersPage.vue` | 用户管理 | ⚠️ 无验证 |
| `/company/chat` | `ChatPage.vue` | AI 法律对话 | ⚠️ 无验证 |
| `/company/history` | `HistoryPage.vue` | 查询历史 | ⚠️ 无验证 |

**路由守卫现状**：`router/index.js` 中的守卫仅设置页面标题，直接调用 `next()` 放行所有请求，**不进行任何权限检查**。

---

### 6.2 状态管理

`stores/user.js`（Pinia）存储 token（localStorage），提供：

| 状态/方法 | 说明 |
|-----------|------|
| `token` | JWT 原始字符串 |
| `isLoggedIn` | 是否已登录（token 非空） |
| `currentUser` | 从 JWT 解码的用户信息 `{userId, username, role}` |
| `isSuperAdmin` | 角色是否为 `SUPER_ADMIN` |
| `isCompanyAdmin` | 角色是否为 `COMPANY_ADMIN` |
| `isCompanyUser` | 角色是否为 `COMPANY_USER` 或 `COMPANY_ADMIN` |
| `login(tokenStr)` | 保存 token |
| `logout()` | 清除 token |

---

### 6.3 API 封装

**`api/request.js`**（Axios 实例）：
- `baseURL: '/api'`（通过 Vite 或 Nginx 代理到后端 8000 端口）
- `timeout: 600000`（10 分钟，适配文档处理等长耗时请求）
- 请求拦截器：自动注入 `Authorization: Bearer <token>`
- 响应拦截器：统一错误处理（401/403/404/500）

**`api/laws.js`** 封装了所有 `/admin/laws/*` 接口调用。  
**`api/standards.js`** 封装了所有 `/admin/standards/*` 接口调用。

---

## 7. 环境配置

复制 `backend/.env.example` 为 `backend/.env` 并填写：

```bash
# 必须修改的配置
SECRET_KEY=<随机生成，至少32字符>
JWT_SECRET_KEY=<随机生成，至少32字符>
DB_PASSWORD=<数据库密码>
DASHSCOPE_API_KEY=<通义千问 API Key，从 DashScope 控制台获取>

# 数据库（默认本机 PostgreSQL）
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neikongai
DB_USER=neikongai_user

# CORS（生产环境）
ALLOWED_ORIGINS=https://neikongai.com,https://www.neikongai.com
```

> ⚠️ 务必在 `.env.example` 中查看完整变量列表。

---

## 8. 安全现状与风险

### 🔴 已修复
| 问题 | 状态 |
|------|------|
| `backend/.env`（含真实数据库密码和 DashScope API Key）被提交到 Git | ✅ 已从 git 追踪中移除，`.gitignore` 已覆盖 |

> ⚠️ **敏感凭据已泄露到 Git 历史记录中，必须立即轮换**：
> - `DASHSCOPE_API_KEY`（`sk-a6d6564a22f74098bd7abbaa8bd0786a`）
> - `DB_PASSWORD`（`Neikongai2026!@#`）
> - `JWT_SECRET_KEY` / `SECRET_KEY`

### 🔴 待修复（高优先级）
| 问题 | 风险等级 | 说明 |
|------|----------|------|
| 全部管理 API 无认证 | ✅ **已修复** | `admin_laws.py`、`admin_standards.py` 所有端点已恢复 `require_admin` 认证 |
| `/ai/ask` 无认证 | 🔴 高 | 任何人可免费调用通义千问 API，产生费用 |
| 前端路由守卫无权限验证 | 🔴 高 | 任何人可访问管理后台所有页面 |
| JWT 有效期配置不一致 | 🟡 中 | 代码中写死 30 分钟，`.env` 配置 1440 分钟，实际生效为 30 分钟 |
| Token 存储在 localStorage | 🟡 中 | 存在 XSS 攻击风险，建议改为 HttpOnly Cookie |
| CORS 允许通配符 `*`（开发默认值） | 🟡 中 | 生产环境需要设置 `ALLOWED_ORIGINS` |
| 文件上传路径写死为 `/var/www/neikongai/` | 🟡 中 | 需配置为环境变量，本地开发路径可能不存在 |
| 上传文件无大小限制验证 | 🟡 中 | `admin_laws.py` 未检查文件大小 |
| 删除文档接口无权限验证 | ✅ **已修复** | 删除接口已恢复 `require_admin` 认证保护 |

### 🟢 已正确实现的安全措施
- 密码使用 bcrypt 哈希存储
- JWT 签名采用 HS256
- SQL 参数化查询（无 SQL 注入风险）
- 文件扩展名白名单校验
- 管理 API 已启用基于角色的认证（`super_admin` / `company_admin`）

---

## 9. 代码质量评估

### 优点
- 服务层分层清晰（TextExtractor → StructureParser → Chunking → Embedding → DB）
- 文档处理每步有详细日志记录
- 分块策略根据文档结构自适应（有章节/无章节/无结构）
- RAG 检索采用多路召回（向量 + 关键词）+ 分层权重 + 二次重排，设计合理
- `LawAIAnalyzer` 对每个分块生成结构化合规单元（主体/行为/义务/禁止/风险等级）

### 待改进
| 问题 | 说明 |
|------|------|
| `admin_laws.py` 与 `admin_standards.py` 代码高度重复 | 两个文件各 700+ 行，逻辑几乎相同，建议抽象公共基类 |
| `text_extractor.py` 与 `text_extractor_with_table.py` 并存 | 需要合并或明确使用规则 |
| ORM 模型与实际数据库表不一致 | `models.py` 中的 `documents` 表未实际使用，实际使用 `legal_documents` |
| `get_db_connection()` 每次创建新连接 | 无连接池，高并发下存在性能问题 |
| 错误处理不统一 | 部分服务直接 `raise Exception`，部分返回空结果 |
| `@app.on_event("startup/shutdown")` 已废弃 | FastAPI 0.93+ 建议改用 `lifespan` 上下文管理器 |
| main.py 日志显示"开发模式：已禁用认证" | 需在生产前改为正确状态 |
| `requirements.txt` 中 Redis/MinIO/ChromaDB 已引入但未使用 | 未来集成用，但增加部署复杂度 |

---

## 10. 已知问题与 TODO

### 🔴 阻塞性问题（上线前必须解决）
- [x] **启用认证中间件**：已在 `auth.py` 新增 `require_admin` 函数，并恢复 `admin_laws.py`、`admin_standards.py` 中 22 处认证保护（`ai_ask.py` 为 AI 问答，普通用户也需使用，不加 admin 限制）
- [ ] **前端路由守卫**：在 `router/index.js` 中加入基于 `userStore.isLoggedIn` 和 `role` 的权限检查
- [ ] **轮换所有已泄露的凭据**（见第8节）
- [ ] **修复 JWT 有效期**：统一为 `ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))`
- [ ] **上传目录改为环境变量**：`UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/var/www/neikongai/uploads/laws")`

### 🟡 功能完善
- [ ] 实现 `files.py` 中的文件上传/列表功能（当前为 stub）
- [ ] 实现 `CompaniesPage.vue` 和 `UsersPage.vue` 的实际 CRUD API（当前前端页面已有，后端 API 未实现）
- [ ] 数据库迁移：使用 Alembic 管理数据库 schema 版本
- [ ] Redis 集成：缓存高频查询结果、分布式限流
- [ ] MinIO 集成：文件存储改为对象存储（当前是本地文件系统）
- [ ] 合规问答增加用户历史记录功能（当前 `/ai/ask` 不关联用户会话）
- [ ] `text_extractor_with_table.py` 整合到主流程

### 🟢 优化建议
- [ ] `admin_laws.py` 和 `admin_standards.py` 抽象公共基类或通用函数
- [ ] `get_db_connection()` 改为使用连接池（psycopg2 的 `pool.SimpleConnectionPool`）
- [ ] 将 `@app.on_event` 改为 `lifespan` context manager
- [ ] 前端 `utils/request.js` 与 `api/request.js` 重复，建议合并
- [ ] 添加单元测试（目前只有 `test_vector_retrieval.py` 调试脚本）
- [ ] API 速率限制（防止 AI 接口滥用）

---

## 11. 快速启动

### 前提条件
- Python 3.11+
- PostgreSQL（需安装 `pgvector` 扩展）
- Node.js 18+
- DashScope API Key（通义千问）

### 后端启动
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写：DB_PASSWORD, DASHSCOPE_API_KEY, SECRET_KEY, JWT_SECRET_KEY

# 初始化数据库（确保 PostgreSQL 已启动并创建了数据库）
# psql -U postgres -c "CREATE DATABASE neikongai;"
# psql -U postgres -c "CREATE USER neikongai_user WITH PASSWORD '...'; GRANT ALL ON DATABASE neikongai TO neikongai_user;"
# psql -U neikongai_user -d neikongai -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 启动服务
uvicorn app.main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

### 前端启动
```bash
cd frontend
npm install
npm run dev  # 默认 http://localhost:5173
```

**Vite 代理配置**（`vite.config.js` 中确认已配置 `/api` → `http://localhost:8000`）

### 部署
- 前端构建：`cd frontend && npm run build`（产物在 `frontend-dist/`）
- 后端：`uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Nginx 反向代理：`/api/*` → 后端 8000，其余静态文件由 `frontend-dist/` 提供

---

*本报告基于代码静态分析生成，反映当前（2026-03-12）代码库的真实状态。*
