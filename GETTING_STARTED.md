# 小白入门指南：从零启动 NeikongAI

> **适合人群**：第一次运行这个项目、不熟悉 Python / Vue 的开发者  
> **目标**：让你在本地把前后端全部跑起来，并成功上传第一个法律文档、发出第一条 AI 问答

---

## 目录

1. [你需要准备什么（前提条件）](#1-你需要准备什么前提条件)
2. [第一步：安装 PostgreSQL 数据库](#2-第一步安装-postgresql-数据库)
3. [第二步：创建数据库和表结构](#3-第二步创建数据库和表结构)
4. [第三步：获取通义千问 API Key](#4-第三步获取通义千问-api-key)
5. [第四步：配置后端环境变量](#5-第四步配置后端环境变量)
6. [第五步：启动后端服务](#6-第五步启动后端服务)
7. [第六步：启动前端](#7-第六步启动前端)
8. [第七步：登录管理后台](#8-第七步登录管理后台)
9. [第八步：上传第一个法律文档](#9-第八步上传第一个法律文档)
10. [第九步：测试 AI 问答](#10-第九步测试-ai-问答)
11. [常见错误和解决方法](#11-常见错误和解决方法)

---

## 1. 你需要准备什么（前提条件）

在开始之前，请确认你的电脑上已经安装了以下软件：

| 软件 | 最低版本 | 检查命令 | 下载地址 |
|------|---------|---------|---------|
| Python | 3.10+ | `python3 --version` | https://www.python.org/downloads/ |
| Node.js | 18+ | `node --version` | https://nodejs.org/ |
| PostgreSQL | 14+ | `psql --version` | https://www.postgresql.org/download/ |
| Git | 任意 | `git --version` | https://git-scm.com/ |

> ⚠️ **Windows 用户注意**：建议使用 WSL2（Windows Linux 子系统）或 Git Bash 来运行命令，避免路径问题。

---

## 2. 第一步：安装 PostgreSQL 数据库

### 2.1 安装 pgvector 扩展

NeikongAI 使用 PostgreSQL 的 **pgvector** 扩展来存储 AI 向量。必须安装。

**Ubuntu / Debian：**
```bash
sudo apt-get install postgresql-server-dev-all
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make && sudo make install
```

**macOS（Homebrew）：**
```bash
brew install pgvector
```

**Windows：** 参考 https://github.com/pgvector/pgvector#windows

### 2.2 创建数据库和用户

打开终端，用 PostgreSQL 超级用户登录：

```bash
# Linux / macOS
sudo -u postgres psql

# Windows（在 pgAdmin 的 Query Tool 里执行也可以）
psql -U postgres
```

在 `psql` 提示符里，依次执行以下 SQL：

```sql
-- 创建数据库用户（把 your_password_here 改成你自己的密码）
CREATE USER neikongai_user WITH PASSWORD 'your_password_here';

-- 创建数据库
CREATE DATABASE neikongai OWNER neikongai_user;

-- 给用户完整权限
GRANT ALL PRIVILEGES ON DATABASE neikongai TO neikongai_user;

-- 退出 psql
\q
```

---

## 3. 第二步：创建数据库和表结构

项目使用了 8 张数据库表。我们已经准备好了一键初始化脚本。

```bash
# 进入后端目录
cd /path/to/neikongai/backend

# 执行初始化脚本（把 your_password_here 改成你上一步设置的密码）
psql -U neikongai_user -d neikongai -h localhost -f init_db.sql
```

执行成功后，你会看到类似输出：
```
CREATE EXTENSION
CREATE TABLE
CREATE TABLE
CREATE TABLE
...
INSERT 0 1          ← 初始管理员账号创建成功
```

**这一步创建了什么：**
- `users` 表：用户账号
- `legal_documents` 表：上传的法律 / 行业准则文档
- `legal_chunks` 表：文档分块（含 1536 维向量字段）
- `ai_law_units` 表：AI 合规分析结果
- `document_processing_log` 表：文档处理日志
- `conversations` / `messages` 表：AI 对话历史

同时创建了初始管理员账号：
- **用户名**：`admin`
- **初始密码**：`Admin@123456`
- **⚠️ 安全提示**：上线前请立即修改密码！

---

## 4. 第三步：获取通义千问 API Key

NeikongAI 使用阿里云通义千问（DashScope）提供：
- **文本嵌入**（把文字变成向量）
- **大模型生成**（回答用户的合规问题）
- **AI 文档结构识别**（识别法条结构）

**获取步骤：**

1. 打开 https://dashscope.console.aliyun.com/
2. 注册 / 登录阿里云账号
3. 点击左侧菜单 → **API-KEY 管理**
4. 点击 **创建新的 API-KEY**
5. 复制生成的 Key（格式类似 `sk-xxxxxxxxxxxxxxxx`）

> 💡 **费用**：通义千问提供免费额度（每月数百万 Token），学习/测试期间通常不需要付费。

---

## 5. 第四步：配置后端环境变量

```bash
# 进入后端目录
cd /path/to/neikongai/backend

# 复制配置模板
cp .env.example .env
```

用文本编辑器打开 `.env` 文件，**必须修改**以下几项：

```ini
# ① 数据库密码（改成第2步你设置的密码）
DATABASE_URL=postgresql://neikongai_user:your_password_here@localhost:5432/neikongai
DB_PASSWORD=your_password_here

# ② 通义千问 API Key（改成第3步复制的 Key）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# ③ JWT 安全密钥（改成任意一串随机字符，用于加密登录 token）
SECRET_KEY=random-string-at-least-32-chars
JWT_SECRET_KEY=another-random-string-at-least-32-chars
```

> ❌ **永远不要把 `.env` 文件上传到 GitHub！**（已在 `.gitignore` 中排除）

---

## 6. 第五步：启动后端服务

```bash
# 进入后端目录
cd /path/to/neikongai/backend

# 创建 Python 虚拟环境（只需要第一次）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows

# 安装依赖（只需要第一次，可能需要几分钟）
pip install -r requirements.txt
pip install dashscope pdfplumber  # 额外依赖

# 创建上传目录
mkdir -p /var/www/neikongai/uploads/laws

# 启动后端（开发模式，代码改动自动重启）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后，你会看到：
```
🚀 NeikongAI API 启动成功！
📖 API 文档地址: http://localhost:8000/docs
```

**验证是否成功：** 打开浏览器访问 http://localhost:8000/docs，如果看到 Swagger API 文档页面，说明后端已正常运行。

---

## 7. 第六步：启动前端

**新开一个终端窗口**（不要关闭后端），然后：

```bash
# 进入前端目录
cd /path/to/neikongai/frontend

# 安装依赖（只需要第一次，可能需要几分钟）
npm install

# 启动前端开发服务器
npm run dev
```

启动成功后，你会看到：
```
  VITE vx.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

打开浏览器访问 **http://localhost:3000**，应该能看到跳转到登录页面。

---

## 8. 第七步：登录管理后台

在浏览器打开 http://localhost:3000，使用初始管理员账号登录：

- **用户名**：`admin`
- **密码**：`Admin@123456`

登录成功后会进入**知识库仪表盘**，这就是管理后台首页。

左侧菜单包含：
- 📊 **知识库仪表盘** — 统计总览
- 📋 **法律层级管理** — 按层级查看法律文档
- 📚 **行业准则管理** — 行业准则文档
- 📈 **向量监控** — 向量数据库状态
- ⚖️ **法律文档管理** — 上传和管理法律文件
- 🏢 **企业管理** — 管理企业账号
- 👥 **用户管理** — 管理用户账号

---

## 9. 第八步：上传第一个法律文档

1. 点击左侧菜单 **法律文档管理**
2. 点击页面右上角 **上传法律文档** 按钮
3. 填写表单：
   - **法律名称**：例如 `中华人民共和国公司法`
   - **法律层级**：选择 `法律（4）`
   - **选择文件**：上传一个 PDF 或 Word 文件（.pdf / .docx）
4. 点击 **确认上传**

上传后，后端会自动在后台进行：
1. 📖 **文本提取**（从 PDF/Word 读取文字）
2. 🔍 **结构识别**（识别章节、条文）
3. ✂️ **智能分块**（每条条款独立一块）
4. 🧬 **向量化**（调用通义千问 Embedding API）
5. 🤖 **AI 合规分析**（识别义务、风险等）

> ⏱️ 处理时间取决于文档大小和网络速度，一般需要 30 秒到 5 分钟。

点击文档列表里的文档名称，可以查看**处理日志**和**分块详情**。

---

## 10. 第九步：测试 AI 问答

AI 问答功能需要**企业用户账号**（非管理员账号）。

### 创建一个企业用户

打开 http://localhost:3000/register，注册一个新账号（普通用户）。

### 使用 AI 问答

用新注册的账号登录后，页面会跳转到企业用户界面：

1. 点击 **AI 法律问答**
2. 在输入框里输入问题，例如：
   - `公司法关于股东会的召开有什么规定？`
   - `违反安全生产法需要承担哪些责任？`
3. 点击发送，等待 AI 回答

AI 会根据你上传的法律文档进行检索，给出有法律依据的回答。

---

## 11. 常见错误和解决方法

### ❌ `could not connect to server` / 数据库连接失败

**原因**：PostgreSQL 未启动，或 `.env` 中密码错误。

**解决**：
```bash
# 检查 PostgreSQL 是否运行
sudo systemctl status postgresql   # Linux
brew services list                  # macOS

# 启动 PostgreSQL
sudo systemctl start postgresql    # Linux
brew services start postgresql     # macOS
```

检查 `.env` 中 `DB_PASSWORD` 是否和创建用户时的密码一致。

---

### ❌ `relation "legal_documents" does not exist`

**原因**：第三步的 `init_db.sql` 没有执行成功。

**解决**：重新执行初始化脚本：
```bash
psql -U neikongai_user -d neikongai -h localhost -f backend/init_db.sql
```

---

### ❌ `DASHSCOPE_API_KEY 未设置` / 向量化失败

**原因**：`.env` 文件里没有填写 API Key，或填写了占位符 `your-dashscope-api-key-here`。

**解决**：在 `.env` 中把 `DASHSCOPE_API_KEY` 改为你的真实 Key（`sk-...`）。

---

### ❌ `No module named 'dashscope'`

**解决**：
```bash
source venv/bin/activate
pip install dashscope
```

---

### ❌ 前端页面空白 / API 请求失败（Network Error）

**原因**：后端没有启动，或端口不对。

**解决**：
1. 确认后端在 `http://localhost:8000` 运行（打开该地址应返回 JSON）
2. 确认前端代理配置正确（`frontend/vite.config.js` 里 proxy 指向 `http://localhost:8000`）

---

### ❌ 登录后显示"权限不足"

**原因**：`users` 表里该账号的 `role` 字段不是 `super_admin` 或 `company_admin`。

**解决**：直接在数据库修改：
```sql
UPDATE users SET role = 'super_admin' WHERE username = 'admin';
```

---

## 下一步

恭喜！如果你完成了以上所有步骤，你的 NeikongAI 已经在本地完整运行起来了。接下来你可以：

- 📄 阅读 `README.md` 了解项目整体架构
- 🚀 阅读 `DEPLOYMENT_GUIDE.md` 了解如何把代码部署到服务器
- 🔍 阅读 `PROJECT_REPORT.md` 深入了解每个模块的技术细节
- 💻 打开 http://localhost:8000/docs 探索所有 API 接口
