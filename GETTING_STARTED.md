# 小白入门指南：从零启动 NeikongAI

---

## ❓ 先看这里：你属于哪种情况？

| 情况 | 描述 | 跳转 |
|------|------|------|
| **情况 A（推荐先看）** | 我已经有一台服务器，上面装好了 PostgreSQL、Python、Node.js 等，现在想把 GitHub 上的代码部署上去 | 👉 [情况 A：服务器已就绪，直接部署](#情况-a服务器已就绪直接把代码部署上去) |
| **情况 B** | 我在自己的电脑上从零开始，什么都还没装 | 👉 [情况 B：从零开始在本地运行](#情况-b从零开始在本地电脑上运行) |

---

## 💡 先理解一个核心概念：GitHub 和服务器是两回事

很多人刚开始会有一个困惑：**GitHub 上的代码怎么才能跑起来？要在 GitHub 上安装东西吗？**

**不是的。** 用一张图来解释：

```
  GitHub（代码仓库）              你的服务器（真正运行的地方）
  ─────────────────              ──────────────────────────
  存放代码文件                    实际运行 Python、Node.js
  你可以在这里修改代码              连接数据库、存文件
  .py / .vue / .js 等等           处理用户请求

         │   git clone / git pull   │
         └─────────────────────────┘
              你用这个命令把代码
              从 GitHub 复制到服务器
```

**关键点：**
- GitHub 只是**存代码**的地方，不运行任何程序
- 所有服务（Python、PostgreSQL、Redis 等）都运行在**你的服务器上**
- 你只需要在**服务器上**执行 `git clone 仓库地址`，把代码拉下来，然后启动就行了
- `.env` 配置文件（含数据库密码、API Key）**只放在服务器上**，永远不上传 GitHub

---

## 情况 A：服务器已就绪，直接把代码部署上去

> **适合你的情况**：服务器上已有 PostgreSQL、Python 3.10+、Node.js 18+、Nginx、Git

### A-0. 通过 SSH 连上你的服务器

```bash
ssh 你的用户名@你的服务器IP
```

### A-1. 把代码从 GitHub 拉到服务器

```bash
# 进入你想放代码的目录（推荐 /var/www/）
cd /var/www

# 克隆代码（第一次）
git clone https://github.com/jiadaaou/neikongai.git
cd neikongai
```

> 如果你以后改了代码并推送到 GitHub，在服务器上只需要运行 `git pull` 就能更新。

### A-2. 检查 pgvector 扩展是否已安装

NeikongAI 用 PostgreSQL 的 pgvector 扩展来存储 AI 向量。先检查是否已装：

```bash
sudo -u postgres psql -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

- 如果有返回一行记录，说明已安装，跳过安装步骤
- 如果无输出，需要安装：

```bash
# Ubuntu/Debian
sudo apt-get install -y postgresql-server-dev-$(pg_config --version | grep -oP '\d+' | head -1)
git clone https://github.com/pgvector/pgvector.git /tmp/pgvector
cd /tmp/pgvector && make && sudo make install
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### A-3. 创建数据库用户和数据库

```bash
sudo -u postgres psql
```

在 psql 里执行：

```sql
-- 创建专用用户（把 your_password_here 换成你自己的强密码）
CREATE USER neikongai_user WITH PASSWORD 'your_password_here';
CREATE DATABASE neikongai OWNER neikongai_user;
GRANT ALL PRIVILEGES ON DATABASE neikongai TO neikongai_user;
\q
```

### A-4. 初始化数据库表结构

```bash
cd /var/www/neikongai
psql -U neikongai_user -d neikongai -h localhost -f backend/init_db.sql
```

执行成功后会看到一堆 `CREATE TABLE`，最后一行 `INSERT 0 1` 表示初始管理员账号创建成功。

### A-5. 配置后端环境变量

```bash
cd /var/www/neikongai/backend
cp .env.example .env
nano .env   # 或者用 vim .env
```

**必须修改的项目：**

```ini
# 数据库连接（改成你 A-3 步骤中设置的密码）
DATABASE_URL=postgresql://neikongai_user:your_password_here@localhost:5432/neikongai
DB_PASSWORD=your_password_here

# 通义千问 API Key（在 https://dashscope.console.aliyun.com/ 获取）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 安全密钥（随便填一串32位以上的随机字符）
SECRET_KEY=填入随机字符串至少32位
JWT_SECRET_KEY=填入另一个随机字符串至少32位

# 你的域名（前端部署后的访问地址）
ALLOWED_ORIGINS=https://你的域名.com,http://你的服务器IP
```

### A-6. 安装后端 Python 依赖

```bash
cd /var/www/neikongai/backend

# 创建虚拟环境（隔离 Python 包，不污染系统）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install dashscope pdfplumber   # 这两个包未在 requirements.txt 中但必须安装

# 创建文件上传目录
mkdir -p /var/www/neikongai/uploads/laws
mkdir -p /var/www/neikongai/uploads/standards
mkdir -p /var/www/neikongai/storage/chromadb
```

### A-7. 启动后端服务

**临时测试方式（验证能跑起来）：**

```bash
cd /var/www/neikongai/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

看到 `🚀 NeikongAI API 启动成功！` 就说明后端正常。

**正式部署方式（用 systemd 让服务自动运行）：**

```bash
sudo nano /etc/systemd/system/neikongai-backend.service
```

粘贴以下内容（根据你的实际路径修改）：

```ini
[Unit]
Description=NeikongAI Backend
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/neikongai/backend
ExecStart=/var/www/neikongai/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/var/www/neikongai/backend/venv/bin

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable neikongai-backend
sudo systemctl start neikongai-backend
sudo systemctl status neikongai-backend   # 查看是否正常运行
```

### A-8. 构建并部署前端

```bash
cd /var/www/neikongai/frontend

# 安装依赖（只需要第一次）
npm install

# 构建生产版本
npm run build
# 构建完成后，dist/ 目录就是前端静态文件
```

### A-9. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/neikongai
```

粘贴以下配置（把 `你的域名.com` 改成你的实际域名或服务器 IP）：

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 前端静态文件
    root /var/www/neikongai/frontend/dist;
    index index.html;

    # 前端路由（Vue Router history 模式需要）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # 上传大文件支持
        client_max_body_size 100M;
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/neikongai /etc/nginx/sites-enabled/
sudo nginx -t      # 检查配置是否正确
sudo systemctl reload nginx
```

### A-10. 验证部署成功

打开浏览器，访问你的域名或服务器 IP：

- 看到登录页面 → ✅ 前端正常
- 用户名 `admin`，密码 `Admin@123456` 能登录 → ✅ 后端 + 数据库正常
- 后台能上传文档并看到"处理中" → ✅ 文件系统正常
- 上传后能向量化成功 → ✅ DashScope API Key 正常

---

## 情况 B：从零开始在本地电脑上运行

> **适合情况**：在自己的开发电脑（Windows / macOS / Linux）上从零开始，什么都还没装

### B-1. 安装必要软件

在开始之前，请先安装以下软件：

| 软件 | 最低版本 | 下载地址 |
|------|---------|---------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| PostgreSQL | 14+ | https://www.postgresql.org/download/ |
| Git | 任意 | https://git-scm.com/ |

> ⚠️ **Windows 用户注意**：建议使用 WSL2（Windows Linux 子系统）或 Git Bash 来运行命令。

### B-2. 安装 pgvector 扩展

NeikongAI 使用 PostgreSQL 的 **pgvector** 扩展来存储 AI 向量。

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

### B-3. 创建数据库

```bash
sudo -u postgres psql
```

```sql
CREATE USER neikongai_user WITH PASSWORD 'your_password_here';
CREATE DATABASE neikongai OWNER neikongai_user;
GRANT ALL PRIVILEGES ON DATABASE neikongai TO neikongai_user;
\q
```

### B-4. 克隆项目代码

```bash
git clone https://github.com/jiadaaou/neikongai.git
cd neikongai
```

### B-5. 初始化数据库表结构

```bash
psql -U neikongai_user -d neikongai -h localhost -f backend/init_db.sql
```

### B-6. 获取通义千问 API Key

1. 打开 https://dashscope.console.aliyun.com/
2. 登录阿里云 → **API-KEY 管理** → **创建新的 API-KEY**
3. 复制 Key（格式：`sk-xxxxxxxxxxxxxxxx`）

### B-7. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入数据库密码和 DASHSCOPE_API_KEY
```

### B-8. 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install dashscope pdfplumber
mkdir -p /var/www/neikongai/uploads/laws
mkdir -p /var/www/neikongai/uploads/standards
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### B-9. 启动前端

新开一个终端窗口：

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000，使用 `admin` / `Admin@123456` 登录。

---

## 两种情况都适用：上传第一个文档 & 测试 AI 问答

### 上传第一个法律文档

登录管理后台后：

1. 点击左侧菜单 **法律文档管理**
2. 点击 **上传法律文档** 按钮
3. 填写表单（法律名称、法律层级），选择 PDF 或 Word 文件
4. 点击确认

上传后后端自动处理：📖 提取文本 → 🔍 识别结构 → ✂️ 智能分块 → 🧬 向量化 → 🤖 AI 合规分析  
处理需要 30 秒到 5 分钟，视文档大小而定。

### 测试 AI 问答

注册一个**普通用户账号**（或用 `admin` 账号的企业用户界面），输入问题如：
- `公司法关于股东会的召开有什么规定？`
- `违反安全生产法需要承担哪些责任？`

---

## 常见错误和解决方法

### ❌ 数据库连接失败 / `could not connect to server`

检查 PostgreSQL 是否运行，以及 `.env` 里的密码是否正确：

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql   # 如未运行则启动
```

---

### ❌ `relation "legal_documents" does not exist`

`init_db.sql` 没有执行成功。重新执行：

```bash
psql -U neikongai_user -d neikongai -h localhost -f /var/www/neikongai/backend/init_db.sql
```

---

### ❌ `DASHSCOPE_API_KEY 未设置` / 向量化失败

在 `.env` 中把 `DASHSCOPE_API_KEY` 改为你的真实 Key（`sk-...`）。

---

### ❌ `No module named 'dashscope'`

```bash
source /var/www/neikongai/backend/venv/bin/activate
pip install dashscope pdfplumber
```

---

### ❌ 前端页面空白 / API 请求 404

检查 Nginx 配置里的 `proxy_pass` 是否指向 `http://127.0.0.1:8000`，以及后端服务是否在运行：

```bash
sudo systemctl status neikongai-backend
curl http://127.0.0.1:8000/   # 应返回 {"message":"欢迎使用 NeikongAI API",...}
```

---

### ❌ 登录后"权限不足"

在数据库里确认 admin 账号的 role：

```bash
psql -U neikongai_user -d neikongai -h localhost -c "SELECT username, role FROM users;"
# 如果 admin 的 role 不是 super_admin，执行：
psql -U neikongai_user -d neikongai -h localhost -c "UPDATE users SET role = 'super_admin' WHERE username = 'admin';"
```

---

## 下一步

恭喜！你的 NeikongAI 已经运行起来了。接下来：

- 📄 阅读 `README.md` 了解项目整体架构
- 🔑 阅读 `DEPLOYMENT_GUIDE.md` 了解密钥管理和代码更新流程
- 🔍 阅读 `PROJECT_REPORT.md` 深入了解每个模块的技术细节
- 💻 访问 `http://你的域名/api/docs` 探索所有 API 接口
