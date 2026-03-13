# NeikongAI

AI-Powered Compliance Management Website（AI 驱动的企业内控合规管理系统）

## 🚀 第一次运行？从这里开始

> **[📖 小白入门指南 → GETTING_STARTED.md](./GETTING_STARTED.md)**  
> 覆盖：数据库安装 → 建表 → 配置 API Key → 启动前后端 → 上传第一个文档 → AI 问答全流程

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