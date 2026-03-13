# 部署工作流程与密钥管理指南（小白版）

> **适用人群**：对 Git / Linux 服务器操作不熟悉的开发者  
> **目标**：彻底搞清楚"在哪改代码"、"在哪改密钥"、"两者有什么区别"

---

## 目录

1. [最重要的一个概念：GitHub 存什么，服务器存什么](#1-最重要的一个概念github-存什么服务器存什么)
2. [你的两个想法分别适用于什么场景](#2-你的两个想法分别适用于什么场景)
3. [密钥（API Key / 数据库密码）怎么改——完整步骤](#3-密钥api-key--数据库密码怎么改完整步骤)
4. [代码改动怎么从 GitHub 同步到服务器](#4-代码改动怎么从-github-同步到服务器)
5. [常见问题 FAQ](#5-常见问题-faq)
6. [「上传→修改→下载→删除GitHub」这个方法可行吗？](#6-上传修改下载删除github这个方法可行吗)
7. [改完代码要怎么生效？密钥不在GitHub上AI怎么改代码？](#7-改完代码要怎么生效密钥不在github上ai怎么改代码)

---

## 1. 最重要的一个概念：GitHub 存什么，服务器存什么

### 核心原则：密钥永远不放 GitHub

用一张表格来解释两者的分工：

| 内容类型 | 放 GitHub？ | 放服务器？ | 原因 |
|----------|------------|------------|------|
| Python 代码（`.py`） | ✅ 是 | ✅ 是（从 GitHub 拉取） | 代码可以公开，没有安全风险 |
| Vue 代码（`.vue`）  | ✅ 是 | ✅ 是（从 GitHub 拉取） | 同上 |
| `.env.example`（模板） | ✅ 是 | ✅ 是 | 只是模板，里面的是占位符，没有真实密钥 |
| `.env`（真实密钥文件） | ❌ **绝对不行** | ✅ 是（手动创建，永不上传） | 包含真实密码，一旦上传到 GitHub（即使私有仓库）就有泄露风险 |
| `DASHSCOPE_API_KEY` 真实值 | ❌ **绝对不行** | ✅ 写在 `.env` 里 | 同上 |
| `DB_PASSWORD` 真实值 | ❌ **绝对不行** | ✅ 写在 `.env` 里 | 同上 |

### 用图来理解

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub 仓库（代码仓库）                                          │
│  ─────────────────────────────────────────────────────────────  │
│  ✅  backend/app/main.py           （代码，可以在这里改）         │
│  ✅  backend/.env.example          （模板，占位符，安全）          │
│  ❌  backend/.env                  （.gitignore 里已排除）        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    git pull（拉取代码）
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  服务器（/var/www/neikongai/）                                   │
│  ─────────────────────────────────────────────────────────────  │
│  ✅  backend/app/main.py           （从 GitHub 拉来的代码）       │
│  ✅  backend/.env.example          （从 GitHub 拉来的模板）        │
│  ✅  backend/.env                  （服务器上手动创建/编辑，        │
│                                      里面写真实密钥，只在服务器上） │
└─────────────────────────────────────────────────────────────────┘
```

**关键点**：
- `.env` 文件**只存在于服务器**，从来不上传 GitHub
- 改密钥 = 只改服务器上的 `.env` 文件，GitHub 什么都不用改
- 改代码 = 在 GitHub 改（或本地改后推送），然后在服务器 `git pull`

---

## 2. 你的两个想法分别适用于什么场景

### 想法 A：在服务器上改代码，然后推回 GitHub

**流程**：
```
服务器 → 修改文件 → git add → git commit → git push → GitHub 更新
```

**适合的场景**：
- 紧急修复（服务正在运行，不能等）
- 服务器已有完整开发环境

**缺点**：
- 容易忘记推回 GitHub，导致代码不同步
- 服务器直接承担开发工作，有误操作风险
- **不推荐作为主要工作流**

---

### 想法 B：在 GitHub 上改代码，然后同步到服务器

**流程**：
```
GitHub 改代码 → 服务器 git pull → 重启服务
```

**适合的场景**：
- ✅ 日常的所有代码改动（推荐！）
- ✅ 修复 Bug
- ✅ 新增功能

**注意**：`git pull` 只会更新**代码文件**，不会动 `.env` 文件（因为 `.env` 不在 GitHub 里）

---

### 想法 C（推荐）：代码在 GitHub 改，密钥在服务器的 .env 文件里改

这是正确的工作方式：

```
┌──────────────────────────┐     ┌──────────────────────────────┐
│    修改代码                │     │    修改密钥/配置               │
│    ──────────────────     │     │    ──────────────────────     │
│  1. 在 GitHub 网页上修改   │     │  1. SSH 登录服务器              │
│  2. 服务器执行 git pull    │     │  2. 编辑 backend/.env          │
│  3. 重启服务              │     │  3. 重启服务                   │
│                          │     │  （完全不需要动 GitHub）         │
└──────────────────────────┘     └──────────────────────────────┘
```

---

## 3. 密钥（API Key / 数据库密码）怎么改——完整步骤

### 背景说明

你的项目中有以下密钥需要轮换（之前被意外提交到了 Git 历史里）：
- `DASHSCOPE_API_KEY`（通义千问 API 密钥）
- `DB_PASSWORD`（数据库密码）
- `SECRET_KEY` / `JWT_SECRET_KEY`（应用密钥）

**轮换密钥的含义**：让旧密钥作废，换一个新的密钥，这样即使旧密钥被人看到，也无法使用。

---

### 步骤一：轮换 DASHSCOPE_API_KEY（通义千问）

**在哪里操作**：浏览器，不需要接触服务器或 GitHub

1. 打开 [DashScope 控制台](https://dashscope.console.aliyun.com/)（阿里云）
2. 登录你的账号
3. 点击左侧菜单「API-KEY 管理」
4. 找到旧的 API Key（`sk-a6d6564a22f74098bd7abbaa8bd0786a`），点击**删除**
5. 点击「创建新的 API-KEY」
6. **复制新的 API Key**（只会显示一次，请立即保存到安全的地方）

---

### 步骤二：轮换数据库密码

**在哪里操作**：SSH 登录到服务器，在 PostgreSQL 里执行命令

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 连接 PostgreSQL（以下命令在服务器上执行）
sudo -u postgres psql

# 在 PostgreSQL 里，修改用户密码（把 新密码 换成你要设置的密码）
ALTER USER neikongai_user WITH PASSWORD '新密码';

# 退出 PostgreSQL
\q
```

> **新密码建议格式**：至少16位，包含大写字母+小写字母+数字+特殊字符  
> 例如：`Nkgai2026!Xp9#mQ`（这只是举例，请自己想一个）

---

### 步骤三：把新密钥写入服务器的 .env 文件

**在哪里操作**：SSH 登录服务器

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 进入项目目录（根据你的实际部署路径修改）
cd /var/www/neikongai/backend

# 用 nano 编辑器打开 .env 文件
nano .env
```

在 nano 编辑器里，找到以下几行并修改（上下键移动，直接编辑）：

```ini
# 把这行改成新的 API Key
DASHSCOPE_API_KEY=sk-你的新API_KEY粘贴在这里

# 把这行改成新的数据库密码
DB_PASSWORD=你在步骤二设置的新密码

# 同时更新 DATABASE_URL 里的密码（找到这行也改掉）
DATABASE_URL=postgresql://neikongai_user:你的新密码@localhost:5432/neikongai

# 同时为 SECRET_KEY 和 JWT_SECRET_KEY 生成新的随机值
SECRET_KEY=（见下方生成方法）
JWT_SECRET_KEY=（见下方生成方法）
```

**如何生成随机密钥**（在服务器命令行执行）：
```bash
# 每次执行都会生成一个不同的随机字符串，复制结果填进 .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**nano 保存方法**：
- `Ctrl + O`  → 保存文件
- `Enter`     → 确认文件名
- `Ctrl + X`  → 退出编辑器

---

### 步骤四：重启后端服务

密钥改完之后，需要重启服务让 Python 程序重新读取 `.env` 文件：

```bash
# 如果使用 systemd 管理服务（常见方式）
sudo systemctl restart neikongai-backend

# 如果是用 supervisor 管理
sudo supervisorctl restart neikongai

# 如果是手动启动的，先找到进程 PID
ps aux | grep uvicorn
# 然后 kill 掉旧进程，再重新启动
kill <PID>
cd /var/www/neikongai/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
```

---

### 步骤五：验证新密钥生效

```bash
# 测试 API 是否正常响应
curl https://admin.neikongai.com/api/health

# 查看后端日志，确认没有错误
# 如果用 systemd：
journalctl -u neikongai-backend -n 50 --no-pager

# 如果是文件日志：
tail -50 /var/www/neikongai/logs/app.log
```

---

## 4. 代码改动怎么从 GitHub 同步到服务器

### 日常代码更新流程（推荐）

**第一步**：在 GitHub 网页修改代码（或本地修改后 push 到 GitHub）

**第二步**：SSH 登录服务器，拉取代码

```bash
# SSH 登录
ssh root@你的服务器IP

# 进入项目目录
cd /var/www/neikongai

# 拉取最新代码
git pull origin main

# （如果你的默认分支叫 master，则改成）
# git pull origin master
```

**第三步**：根据改动类型，决定需要做什么

| 改动的文件 | 需要额外操作 |
|----------|------------|
| 只改了后端 Python 代码 | 重启后端服务（见上方步骤四） |
| 只改了前端 Vue 代码 | 需要重新构建前端（见下方） |
| 改了 `requirements.txt` | 需要重新安装依赖（见下方） |
| 只改了 `.env.example`（模板） | 什么都不需要做（模板不影响运行） |

### 前端代码更新

```bash
# 进入前端目录
cd /var/www/neikongai/frontend

# 安装新依赖（如果 package.json 有变化）
npm install

# 重新构建
npm run build

# 构建产物会自动输出到 frontend-dist/，nginx 已指向这个目录
```

### 安装新的 Python 依赖

```bash
cd /var/www/neikongai/backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. 常见问题 FAQ

### Q1：我在 GitHub 上改了 .env.example，服务器上 git pull 之后，.env 里的密钥会变吗？

**不会**。

`.env.example` 是模板文件，`.env` 是真正运行用的配置文件。它们是两个不同的文件：
- `.env.example`：GitHub 上有，服务器上也有，内容是占位符（`your_password_here`）
- `.env`：**只在服务器上**，包含真实密钥，即使 `git pull` 也不会被覆盖（因为它不在 Git 里）

---

### Q2：我不小心把 .env 文件 git add 了，怎么办？

**立刻执行以下步骤**，不要 `git push`：

```bash
# 把 .env 从 git 暂存区移除（不删除文件本身）
git rm --cached backend/.env

# 确认 .gitignore 里有 .env 这一行
cat .gitignore | grep ".env"

# 重新提交
git commit -m "remove .env from tracking"
```

如果已经 push 到 GitHub 了：立刻轮换所有密钥（按照第3节操作），因为文件已经上传，即使删除历史也可能被人缓存了。

---

### Q3：改了密钥之后，代码需要修改吗？

**不需要**。

代码里读取密钥的方式是：
```python
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
```

`os.getenv()` 会去读取 `.env` 文件里的值。你只需要修改 `.env` 文件，代码本身完全不需要动。

---

### Q4：想法 A（服务器直接改代码）有什么风险？

主要有两个风险：

1. **代码不同步**：你在服务器上改了代码，但忘记 push 到 GitHub，下次 `git pull` 会把你的改动覆盖掉
2. **冲突问题**：如果 GitHub 上也有改动，服务器上也有改动，`git pull` 时会产生冲突，需要手动解决

所以建议：**代码改动统一走 GitHub → 服务器**，服务器上只用来：
- 编辑 `.env` 文件（密钥配置）
- 执行 `git pull`（拉取最新代码）
- 重启服务

---

### Q5：我应该用什么顺序来修复安全问题？

按照以下优先级操作：

**第一优先（今天就做）：轮换泄露的密钥**
- [ ] 在 DashScope 控制台删除旧 API Key，创建新 Key
- [ ] 修改 PostgreSQL 数据库密码
- [ ] 更新服务器上的 `.env` 文件
- [ ] 重启后端服务

**第二优先（本周内）：恢复 API 认证**
- [ ] 在 `admin_laws.py` 中恢复所有端点的认证（取消注释 `Depends(require_admin)`）
- [ ] 在前端路由守卫中加入登录检查

**第三优先（下个版本）：代码质量问题**
- [ ] 修复 `LawDetail.vue` 中重复的 `<el-dialog>` 模板
- [ ] 实装分块编辑保存功能

---

### Q6：.env 文件的格式是什么？

```ini
# 井号开头的是注释，不会被读取
# 格式是：变量名=值（等号两边不要有空格）

DASHSCOPE_API_KEY=sk-你的APIKey
DB_PASSWORD=你的数据库密码

# 如果值包含特殊字符或空格，用双引号括起来
SECRET_KEY="abc123!@#$%"
```

---

### Q7：服务器上怎么查看 .env 文件现在的内容？

```bash
# 方法1：直接打印（会显示明文密钥，注意周围没有人）
cat /var/www/neikongai/backend/.env

# 方法2：只列出变量名，不显示值（更安全）
cat /var/www/neikongai/backend/.env | cut -d= -f1
```

---

---

## 6. 「上传→修改→下载→删除GitHub」这个方法可行吗？

### 你描述的工作流程

你的想法是：
1. 把服务器代码传到 GitHub
2. 让 AI 在 GitHub 上帮你改代码
3. 改完后把代码下载回服务器
4. 把 GitHub 上的文件全删掉
5. 在服务器上运行网站

**这个流程可以用，但有几个严重的坑，必须提前了解清楚。**

---

### ⚠️ 坑 1：.env 文件（密钥）绝对不能上传到 GitHub

这是最重要的一点。你上传代码时，**必须把 `.env` 文件排除在外**。

`.env` 文件里有你的数据库密码和 API Key。一旦上传到 GitHub（即使是私有仓库），这些密钥就处于风险中。你的项目已经发生过这个问题（旧的密钥已经泄露），所以务必先轮换密钥，再重新上传。

**检查方法**：上传之前，在服务器上运行：
```bash
# 确认 .env 没有被 Git 跟踪
cd /var/www/neikongai
git status
# 如果看到 backend/.env 出现在列表里，立刻执行：
git rm --cached backend/.env
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "remove .env from git tracking"
```

---

### ⚠️ 坑 2：从 GitHub 下载代码到服务器，方法要选对

"下载回服务器"有两种方式，选错了会覆盖掉你服务器上已有的 `.env` 文件或数据库：

#### 方式 A（推荐）：用 `git pull`

```bash
# 在服务器上执行
cd /var/www/neikongai
git pull origin main
```

**优点**：只更新有变化的代码文件，`.env` 文件完全不受影响（因为它不在 Git 里）。

---

#### 方式 B（危险）：直接解压覆盖

```bash
# ❌ 危险操作，可能覆盖 .env、数据库文件、上传的图片等
cp -r ~/下载/neikongai/* /var/www/neikongai/
```

**风险**：如果你直接把 GitHub 下载的 zip 解压覆盖到服务器目录，可能会：
- 覆盖服务器上的 `.env` 文件（导致密钥丢失，服务无法启动）
- 覆盖用户上传的文件（`uploads/` 目录）
- 覆盖数据库迁移状态

---

### ⚠️ 坑 3：删掉 GitHub 上的文件，以后没法用了

"改完就删 GitHub"的想法，相当于每次修改都要重新上传，非常麻烦。

**更好的做法**：GitHub 仓库保持私有（`Private`），只有你能看到。你把代码放在那里是安全的（只要不上传 `.env`）。下次需要修改，可以直接在 GitHub 上的代码基础上继续改，不需要重新上传。

如果你担心安全，把仓库设为 **Private（私有）** 就够了：
- GitHub → 仓库页面 → Settings → 拉到最底部 → Danger Zone → "Change repository visibility" → Private

---

### ✅ 你的方法改良版（推荐这样做）

```
第 1 步：确保 .env 不在 GitHub 里（只做一次）
         服务器上 → git rm --cached backend/.env → 推送到 GitHub

第 2 步：让 AI 在 GitHub 上帮你改代码
         GitHub 网页 → AI 修改代码 → 代码 commit 到 GitHub

第 3 步：把 GitHub 上改好的代码同步到服务器
         服务器上 → git pull origin main
                  （.env 文件完全不受影响）

第 4 步：重启服务
         服务器上 → sudo systemctl restart neikongai-backend

第 5 步：（可选）把 GitHub 仓库设为 Private
         不需要删除，Private 仓库只有你能看到，和不存在一样安全
```

---

### 总结：你的问题的直接回答

| 你的问题 | 答案 |
|----------|------|
| "传回服务器后能不能执行？" | **可以**，`git pull` 之后服务器代码就更新了，重启服务即可运行 |
| "改完要把 GitHub 上的文件全删掉吗？" | **不需要**，把仓库设为 Private 就安全了，删了反而麻烦 |
| "`.env` 里的密钥怎么办？" | `.env` 不在 GitHub 里，`git pull` 不会动它，安全 |
| "我不会 git pull 怎么办？" | 在服务器 SSH 终端输入 `cd /var/www/neikongai && git pull` 就好了 |

---

---

## 7. 改完代码要怎么生效？密钥不在GitHub上AI怎么改代码？

### 问题 1：你改完代码以后，我需要在服务器上更新才能看到效果吗？

**是的，必须在服务器上更新代码，然后访问域名才能看到新效果。**

原因很简单：你访问域名，其实是在访问你**服务器上运行的那份代码**，不是访问 GitHub 上的代码。GitHub 只是存代码的地方，服务器才是真正运行代码的地方。

整个流程是这样的：

```
AI 在 GitHub 上改代码
        ↓
  GitHub 上有了新代码
        ↓
  【这步你必须做】服务器上执行 git pull
        ↓
  服务器上的代码更新了
        ↓
  重启服务（让新代码生效）
        ↓
  访问你的域名，看到新效果 ✅
```

**缺少中间这步，域名访问到的永远是旧代码。**

#### 具体怎么操作（服务器 SSH 终端里输入）

```bash
# 第 1 步：进入项目目录
cd /var/www/neikongai

# 第 2 步：拉取 GitHub 上的最新代码
git pull origin main

# 第 3 步：重启后端服务（让新代码生效）
sudo systemctl restart neikongai-backend

# 第 4 步：如果改了前端，还需要重新构建前端
cd frontend
npm run build
```

---

### 问题 2：密钥不在 GitHub 上，AI 改代码的时候怎么处理需要密钥的地方？

**AI 改的是"使用密钥的代码逻辑"，不是密钥本身的值。**

这两件事是完全不同的：

| 改的内容 | 放在哪里 | 举例 |
|----------|----------|------|
| 密钥的**值**（真实的Key） | 只在服务器的 `.env` 文件里 | `DASHSCOPE_API_KEY=sk-abc123xyz` |
| **读取**密钥的代码逻辑 | 在 GitHub 代码里 | `api_key = os.getenv("DASHSCOPE_API_KEY")` |

AI 只会修改第二列（代码逻辑），不会动第一列（真实密钥值）。

#### 用一个例子来说明

假设 AI 帮你修改了调用 AI 接口的代码，改动前后是这样的：

```python
# 改动前（旧代码）
response = client.chat(model="old-model", messages=messages)

# 改动后（AI 帮你改成了新版本）
response = client.chat(model="qwen-max", messages=messages, temperature=0.8)
```

你注意到没有？**代码里根本没有密钥**。密钥是通过 `os.getenv("DASHSCOPE_API_KEY")` 从服务器的 `.env` 文件里读取的，代码本身不包含密钥。

所以 AI 改代码时：
- ✅ 可以修改模型名称、参数、业务逻辑
- ✅ 可以增加新功能、修改接口返回格式
- ✅ 完全不需要知道真实的密钥值
- 🔒 密钥值安全地留在你服务器的 `.env` 文件里

#### 什么情况下你需要手动操作？

只有以下情况才需要你亲自在服务器上修改 `.env`：

1. **换了新的 API Key**（在 DashScope 网站重新生成了密钥）
2. **修改了数据库密码**
3. **新增了一个新的配置项**（AI 会告诉你"请在 `.env` 里添加 XXX=你的值"）

---

### 两个问题的总结

| 你的问题 | 答案 |
|----------|------|
| "改完代码需要在服务器更新才能看到效果吗？" | **是的**，`git pull` + 重启服务后，访问域名才能看到新效果 |
| "密钥不在 GitHub 上，AI 怎么改需要密钥的代码？" | **AI 只改代码逻辑，不改密钥值**。代码用 `os.getenv()` 读取密钥，真实密钥值始终在服务器的 `.env` 里 |

---

## 总结：一句话记住核心原则

> **代码** 放 GitHub，用 `git pull` 更新到服务器。  
> **密钥** 只放服务器的 `.env` 文件，永远不碰 GitHub。  
> **轮换密钥** = 改 DashScope 控制台 + 改 PostgreSQL + 改服务器 `.env` + 重启服务。  
> **整个过程完全不需要改 GitHub 上的任何代码。**

---

*如有疑问，可直接描述你遇到的具体问题，将逐步指导你操作。*
