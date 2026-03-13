# NeikongAI

AI-Powered Compliance Management Website（AI 驱动的企业内控合规管理系统）

## 🚀 部署到服务器？从这里开始

> **[📖 服务器部署指南 → GETTING_STARTED.md](./GETTING_STARTED.md)**  
> 适用于服务器上已装好 PostgreSQL / Redis / MinIO / Python / Node.js / Nginx 的情况  
> 步骤一~步骤十：git clone → 建库 → 配置 .env → pip install → systemd → npm build → Nginx  
> 💡 文档开头解释了"GitHub 只存代码、服务器才是运行的地方"这个核心概念

---

## 项目简介

NeikongAI 是一个多租户法律知识库 + 企业内控系统，集成了通义千问大模型，支持：
- 法律法规文档上传与向量化检索
- AI 合规问答（基于证据驱动的分层法律检索）
- 企业内控管理

## 技术栈

- **后端**：Python / FastAPI + PostgreSQL + ChromaDB + DashScope（通义千问）
- **前端**：Vue 3 + Vite + Element Plus
- **向量数据库**：PostgreSQL pgvector 扩展

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入真实的数据库密码和 DASHSCOPE_API_KEY

uvicorn app.main:app --reload
```

API 文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 环境变量

复制 `backend/.env.example` 为 `backend/.env` 并填写以下关键配置：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接 URL |
| `DB_PASSWORD` | 数据库密码 |
| `DASHSCOPE_API_KEY` | 通义千问 API Key（在 [DashScope 控制台](https://dashscope.console.aliyun.com/) 获取） |
| `JWT_SECRET_KEY` | JWT 签名密钥（生产环境请使用随机强密钥） |
| `SECRET_KEY` | 应用密钥（生产环境请使用随机强密钥） |

> ⚠️ **安全提示**：请勿将 `.env` 文件提交到版本控制系统。`.env` 已被 `.gitignore` 排除。

## 目录结构

```
neikongai/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务服务（文档处理、向量化、问答）
│   │   ├── core/           # 数据库配置
│   │   └── main.py         # 应用入口
│   ├── .env.example        # 环境变量示例
│   └── requirements.txt
├── frontend/               # Vue 3 前端（源码）
├── frontend-dist/          # 前端构建产物（部署用）
├── homepage/               # 首页静态文件
└── homepage-src/           # 首页源码
```

---

## ✂️ 拆分规则代码在哪里？

文档上传后，后端会自动把文本拆分成多个向量块（chunk），用于向量检索。拆分规则集中在以下两个文件：

| 文档类型 | 拆分规则文件 | 被哪里调用 |
|---------|------------|----------|
| **法律文档**（法律、法规）| `backend/app/services/chunking_service.py` | `document_processor.py` |
| **行业准则**（标准、准则）| `backend/app/services/chunking_service_standards.py` | `document_processor_standards.py` |

### 当前拆分规则（一句话）

> **一条法条 / 一条条款 = 一个向量块**，不合并、不拆分。章节信息（章号、节号）作为元数据保留在块里。

### 三种策略（两个文件共用同一框架）

| 策略 | 触发条件 | 对应方法 |
|------|---------|---------|
| 策略1 | 文档有章节 + 有条文 | `chunk_with_chapters()` |
| 策略2 | 文档无章节，只有条文 | `chunk_without_chapters()` |
| 策略3 | 无结构文档（通知/公告）| `chunk_unstructured()`，按段落大小切分 |

### 想修改拆分规则？

- **改变"每条 = 一块"的规则** → 找 `_chunk_articles_group()`（准则版）或 `chunk_with_chapters()` 中的 for 循环逻辑
- **改变块的大小限制** → 修改 `__init__` 中的 `max_chunk_size`（默认 1000 字）
- **改变块的内容结构** → 修改 `_create_chunk()` 方法

> 💡 两个文件顶部的注释块里有完整的**行号速查表**，打开文件直接看即可。