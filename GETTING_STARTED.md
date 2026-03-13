# NeikongAI 部署指南（服务器版）

> **适合你的情况**：服务器上已装好 PostgreSQL、Redis、MinIO、Python、Node.js、Nginx，现在要把 GitHub 上的项目代码部署到服务器并启动。

---

## 💡 一句话说清楚：GitHub 和服务器的关系

**GitHub 只是存代码的地方，不运行任何程序。**

```
  GitHub（存代码）                      你的服务器（真正运行的地方）
  ─────────────────────                 ──────────────────────────────
  存放 .py / .vue / .js 等代码文件       运行 Python / Node.js
  你在这里看代码、修改代码                 连接 PostgreSQL / Redis / MinIO
  不运行任何程序                          处理用户请求、响应浏览器

                  │  git clone / git pull  │
                  └────────────────────────┘
                    用这个命令把代码拉到服务器
```

**所以：不需要在 GitHub 上安装任何东西。你只需要在服务器上执行几条命令，把代码拉下来，然后启动服务。**

`.env` 配置文件（含数据库密码、API Key）**只放在服务器上**，永远不上传 GitHub。

---

## 步骤一：SSH 连上服务器

```bash
ssh 你的用户名@你的服务器IP
```

---

## 步骤二：把代码从 GitHub 拉到服务器

```bash
# 进入部署目录
cd /var/www

# 第一次：克隆代码
git clone https://github.com/jiadaaou/neikongai.git
cd neikongai
```

> **以后更新代码**：在 GitHub 上修改代码并推送后，在服务器上执行 `cd /var/www/neikongai && git pull` 即可同步最新代码。

---

## 步骤三：检查 pgvector 扩展

NeikongAI 用 PostgreSQL 的 pgvector 扩展存储 AI 向量。先检查是否已安装：

```bash
sudo -u postgres psql -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

- 返回一行 `vector` → ✅ 已安装，跳过本步骤
- 无输出 → 需要安装：

```bash
# Ubuntu / Debian
sudo apt-get install -y postgresql-server-dev-$(psql --version | grep -oP '\d+' | head -1)
git clone https://github.com/pgvector/pgvector.git /tmp/pgvector
cd /tmp/pgvector && make && sudo make install
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
cd /var/www/neikongai   # 回到项目目录
```

---

## 步骤四：创建数据库用户和数据库

```bash
sudo -u postgres psql
```

在 psql 里执行（把 `your_password_here` 换成你自己的强密码）：

```sql
CREATE USER neikongai_user WITH PASSWORD 'your_password_here';
CREATE DATABASE neikongai OWNER neikongai_user;
GRANT ALL PRIVILEGES ON DATABASE neikongai TO neikongai_user;
\q
```

---

## 步骤五：初始化数据库表结构

项目所有的表（用户、文档、AI 分析结果等）都在这一步创建：

```bash
cd /var/www/neikongai
psql -U neikongai_user -d neikongai -h localhost -f backend/init_db.sql
```

执行成功输出中会有一堆 `CREATE TABLE`，最后一行 `INSERT 0 1` 表示初始管理员账号已创建：
- **用户名**：`admin`
- **密码**：`Admin@123456`（上线后请立即修改！）

---

## 步骤六：配置 .env 环境变量

```bash
cd /var/www/neikongai/backend
cp .env.example .env
nano .env    # 或 vim .env
```

**必须填写以下几项**（其余保持默认即可）：

```ini
# ① 数据库连接（用步骤四设置的密码）
DATABASE_URL=postgresql://neikongai_user:your_password_here@localhost:5432/neikongai
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neikongai
DB_USER=neikongai_user
DB_PASSWORD=your_password_here

# ② 通义千问 API Key
#    获取地址：https://dashscope.console.aliyun.com/ → API-KEY 管理 → 创建
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# ③ 安全密钥（随机字符串，32位以上，可用命令生成：openssl rand -hex 32）
SECRET_KEY=粘贴随机字符串
JWT_SECRET_KEY=粘贴另一个随机字符串

# ④ 允许的前端域名
ALLOWED_ORIGINS=https://你的域名.com,http://你的服务器IP
```

> ❌ **永远不要把 `.env` 文件推送到 GitHub！**（`.gitignore` 已排除它）

---

## 步骤七：安装 Python 依赖并创建目录

```bash
cd /var/www/neikongai/backend

# 创建 Python 虚拟环境（隔离依赖，不污染系统 Python）
python3 -m venv venv
source venv/bin/activate

# 安装依赖（首次需要几分钟）
pip install -r requirements.txt
pip install dashscope pdfplumber   # 必须额外安装的两个包

# 创建文件存储目录
mkdir -p /var/www/neikongai/uploads/laws
mkdir -p /var/www/neikongai/uploads/standards
mkdir -p /var/www/neikongai/storage/chromadb
```

---

## 步骤八：启动后端服务

### 先测试能否启动（临时方式）

```bash
cd /var/www/neikongai/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

看到 `🚀 NeikongAI API 启动成功！` 说明后端正常。按 Ctrl+C 停止，继续下面的步骤。

### 用 systemd 让后端开机自启（正式方式）

```bash
sudo nano /etc/systemd/system/neikongai-backend.service
```

粘贴以下内容：

```ini
[Unit]
Description=NeikongAI Backend API
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/neikongai/backend
ExecStart=/var/www/neikongai/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/var/www/neikongai/backend/.env
Environment=PATH=/var/www/neikongai/backend/venv/bin

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable neikongai-backend    # 开机自启
sudo systemctl start neikongai-backend
sudo systemctl status neikongai-backend    # 确认运行中
```

---

## 步骤九：构建前端静态文件

```bash
cd /var/www/neikongai/frontend

# 安装前端依赖（首次需要几分钟）
npm install

# 构建生产版本（输出到 frontend/dist/ 目录）
npm run build
```

---

## 步骤十：配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/neikongai
```

粘贴以下配置，把 `你的域名.com` 替换成你的实际域名或服务器 IP：

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 前端静态文件目录
    root /var/www/neikongai/frontend/dist;
    index index.html;

    # Vue Router history 模式：所有路由都走 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 100M;
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/neikongai /etc/nginx/sites-enabled/
sudo nginx -t          # 检查配置语法
sudo systemctl reload nginx
```

---

## 验证部署成功

打开浏览器访问你的域名或 IP，逐项检查：

| 检查项 | 预期结果 | 说明 |
|--------|---------|------|
| 访问域名 | 出现登录页面 | 前端 + Nginx 正常 |
| 用 `admin` / `Admin@123456` 登录 | 进入管理后台 | 后端 + 数据库正常 |
| 上传一个法律文档 | 显示"处理中" | 文件系统正常 |
| 等待向量化完成 | 状态变为"完成" | DashScope API Key 正常 |

---

## 以后更新代码

在 GitHub 上修改代码并推送后，在服务器上执行：

```bash
cd /var/www/neikongai
git pull                                    # 拉取最新代码

# 如果修改了后端代码：
sudo systemctl restart neikongai-backend

# 如果修改了前端代码：
cd frontend && npm run build               # 重新构建
sudo systemctl reload nginx
```

---

## 常见错误和解决方法

### ❌ 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql
# 检查密码是否和 .env 里的 DB_PASSWORD 一致
sudo -u postgres psql -c "\du"
```

---

### ❌ `relation "legal_documents" does not exist`

`init_db.sql` 没有执行或执行失败，重新执行步骤五：

```bash
psql -U neikongai_user -d neikongai -h localhost -f /var/www/neikongai/backend/init_db.sql
```

---

### ❌ `DASHSCOPE_API_KEY 未设置` / 向量化一直失败

在 `.env` 里确认 `DASHSCOPE_API_KEY` 已填入真实的 Key（`sk-...`），不是占位符。修改后重启后端：

```bash
sudo systemctl restart neikongai-backend
```

---

### ❌ `No module named 'dashscope'` 或 `No module named 'pdfplumber'`

```bash
source /var/www/neikongai/backend/venv/bin/activate
pip install dashscope pdfplumber
sudo systemctl restart neikongai-backend
```

---

### ❌ 前端页面空白 / API 请求返回 502

后端服务未运行，或端口不对：

```bash
sudo systemctl status neikongai-backend
# 如果未运行：
sudo systemctl start neikongai-backend
sudo journalctl -u neikongai-backend -n 50   # 查看错误日志
```

---

### ❌ 登录后提示"权限不足"

管理员账号的角色不对，修复：

```bash
psql -U neikongai_user -d neikongai -h localhost \
  -c "UPDATE users SET role = 'super_admin' WHERE username = 'admin';"
```

---

## 下一步

- 🔑 阅读 `DEPLOYMENT_GUIDE.md` — 了解密钥管理、代码更新的完整工作流
- 📄 阅读 `README.md` — 了解项目整体架构
- 💻 访问 `http://你的域名/api/docs` — 探索全部 API 接口

---

## 附录：本地开发（在自己电脑上从零开始）

> 以下内容**不适用于已有服务器的情况**，仅供在本地开发电脑（Windows/macOS/Linux）上搭建测试环境参考。

1. 安装 Python 3.10+、Node.js 18+、PostgreSQL 14+、Git
2. 安装 pgvector：Ubuntu 用 `apt-get`，macOS 用 `brew install pgvector`
3. 创建数据库用户和数据库（同步骤四）
4. 克隆代码：`git clone https://github.com/jiadaaou/neikongai.git`
5. 初始化表结构（同步骤五）
6. 配置 `.env`（同步骤六，`ALLOWED_ORIGINS` 改为 `http://localhost:3000`）
7. 安装 Python 依赖（同步骤七）
8. 启动后端（开发模式）：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
9. 启动前端（开发模式）：`cd frontend && npm install && npm run dev`
10. 浏览器访问 http://localhost:3000，使用 `admin` / `Admin@123456` 登录
