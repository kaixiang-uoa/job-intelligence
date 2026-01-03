# Job Intelligence Platform - 启动指南

> 完整的环境配置、服务启动、测试验证指南

## 目录

- [前置要求](#前置要求)
- [环境配置](#环境配置)
- [服务启动](#服务启动)
- [测试验证](#测试验证)
- [常见问题](#常见问题)

---

## 前置要求

### 必需软件

| 软件 | 版本要求 | 用途 | 安装检查 |
|------|---------|------|---------|
| **.NET SDK** | 8.0+ | 运行 .NET API | `dotnet --version` |
| **PostgreSQL** | 16+ | 数据库 | `psql --version` |
| **Python** | 3.10+ | 运行爬虫 API | `python3 --version` |
| **Anaconda** | 最新版 | Python 环境管理 | `conda --version` |

### 系统要求

- **操作系统:** macOS, Linux, 或 Windows (WSL2)
- **内存:** 至少 4GB RAM
- **磁盘空间:** 至少 2GB 可用空间
- **网络:** 需要访问 SEEK 和 Indeed 网站

---

## 环境配置

### 1. 安装 PostgreSQL 16

#### macOS (使用 Homebrew)

```bash
# 安装 PostgreSQL 16
brew install postgresql@16

# 启动 PostgreSQL 服务
brew services start postgresql@16

# 验证安装
psql --version
# 应该显示: psql (PostgreSQL) 16.x
```

#### Linux (Ubuntu/Debian)

```bash
# 添加 PostgreSQL 仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# 安装 PostgreSQL 16
sudo apt update
sudo apt install postgresql-16

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows

1. 下载 PostgreSQL 16 安装程序: https://www.postgresql.org/download/windows/
2. 运行安装程序，记住设置的密码
3. 添加 PostgreSQL bin 目录到 PATH

### 2. 配置数据库

```bash
# 创建数据库
createdb jobintel

# 创建用户（使用强密码）
psql jobintel -c "CREATE USER admin WITH PASSWORD 'dev123';"

# 授予权限
psql jobintel -c "GRANT ALL PRIVILEGES ON DATABASE jobintel TO admin;"
psql jobintel -c "GRANT ALL ON SCHEMA public TO admin;"

# 验证连接
psql -h localhost -U admin -d jobintel -c "SELECT version();"
```

**安全提示:** 生产环境请修改默认密码 `dev123`

### 3. 安装 .NET 8 SDK

#### macOS

```bash
brew install dotnet
```

#### Linux

```bash
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0
```

#### Windows

下载并安装: https://dotnet.microsoft.com/download/dotnet/8.0

### 4. 配置 Python 环境

```bash
# 克隆项目（如果还没有）
cd ~/Desktop/Web-practice
git clone <your-repo-url> job-intelligence
cd job-intelligence

# 进入 Python 项目目录
cd scrape-api

# 使用 Anaconda 创建虚拟环境（可选但推荐）
conda create -n jobintel python=3.10
conda activate jobintel

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python -m pytest tests/ -v
# 应该显示: 103 passed
```

### 5. 运行 EF Core Migrations

```bash
# 回到项目根目录
cd /Users/kxz/Desktop/Web-practice/job-intelligence

# 进入 .NET API 目录
cd src/JobIntel.Api

# 应用数据库迁移
dotnet ef database update

# 验证表创建
psql -h localhost -U admin -d jobintel -c "\dt"
# 应该看到: job_postings, ingest_runs, __EFMigrationsHistory
```

---

## 服务启动

### 启动顺序

1. PostgreSQL (第一个启动)
2. Python 爬虫 API (第二个启动)
3. .NET API (最后启动)

### 1. 启动 PostgreSQL

```bash
# macOS
brew services start postgresql@16

# Linux
sudo systemctl start postgresql

# 验证运行状态
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux
```

**端口:** 5432
**状态检查:**
```bash
psql -h localhost -U admin -d jobintel -c "SELECT 1;"
```

### 2. 启动 Python 爬虫 API

打开**新终端窗口**:

```bash
# 进入项目目录
cd /Users/kxz/Desktop/Web-practice/job-intelligence/scrape-api

# 激活 Anaconda 环境（如果使用）
conda activate jobintel

# 启动 FastAPI 服务
/Users/kxz/anaconda3/bin/python -m uvicorn app.main:app --reload --port 8000
```

**启动参数说明:**
- `--reload` - 开发模式，代码修改自动重启
- `--port 8000` - 指定端口 8000

**成功标志:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**端口:** 8000
**API 文档:** http://localhost:8000/docs
**健康检查:**
```bash
curl http://localhost:8000/
# 返回: {"message":"Job Intelligence Scrape API","version":"1.0.0"}
```

### 3. 启动 .NET API

打开**另一个新终端窗口**:

```bash
# 进入 .NET API 目录
cd /Users/kxz/Desktop/Web-practice/job-intelligence/src/JobIntel.Api

# 启动 .NET API
dotnet run --urls="http://localhost:5000"
```

**启动参数说明:**
- `--urls` - 指定监听端口 5000

**成功标志:**
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
```

**端口:** 5000
**Swagger UI:** http://localhost:5000/swagger
**Hangfire Dashboard:** http://localhost:5000/hangfire
**健康检查:**
```bash
curl http://localhost:5000/api/health
# 返回: {"status":"healthy","timestamp":"...","database":"connected","jobCount":0}
```

---

## 测试验证

### 1. 基础健康检查

```bash
# 测试 Python API
curl http://localhost:8000/

# 测试 .NET API
curl http://localhost:5000/api/health
```

**预期结果:**
- Python API: `{"message":"Job Intelligence Scrape API","version":"1.0.0"}`
- .NET API: `{"status":"healthy","database":"connected","jobCount":0}`

### 2. 测试 SEEK 数据采集

```bash
curl "http://localhost:5000/api/ingest/seek?keywords=plumber&location=Sydney&maxResults=5" \
  | python3 -m json.tool
```

**预期结果:**
```json
{
  "source": "seek",
  "count": 5,
  "jobs": [
    {
      "source": "seek",
      "source_id": "...",
      "title": "Plumber - Sydney",
      "company": "...",
      "location_state": "NSW",
      "location_suburb": "Sydney",
      "trade": "plumber",
      "employment_type": "Full Time",
      "pay_range_min": 70000,
      "pay_range_max": 90000,
      "description": "...",
      "posted_at": "2025-12-22T...",
      "scraped_at": "2025-12-22T..."
    }
  ],
  "scraped_at": "2025-12-22T..."
}
```

**数据质量检查:**
- ✅ `location_state` 应该是有效的澳大利亚州缩写 (NSW, VIC, QLD, SA, WA, TAS, NT, ACT)
- ✅ `location_suburb` 应该是具体的郊区名称
- ✅ `trade` 应该匹配搜索关键词
- ✅ `pay_range_min` 和 `pay_range_max` 应该是合理的数字（可能为 null）

### 3. 测试 Indeed 数据采集

```bash
curl "http://localhost:5000/api/ingest/indeed?keywords=electrician&maxResults=3" \
  | python3 -m json.tool
```

**预期结果:**
```json
{
  "source": "indeed",
  "count": 1-3,
  "jobs": [
    {
      "source": "indeed",
      "location_state": "NSW",
      "location_suburb": "Inverell",
      "trade": "electrician",
      "employment_type": "Full Time",
      "pay_range_min": null,
      "pay_range_max": null,
      "description": "非常详细的描述 (2000+ 字符)",
      ...
    }
  ]
}
```

**注意:** Indeed API 通常不返回薪资信息（`pay_range_min/max` 为 null），这是已知限制。

### 4. 测试并行采集（所有平台）

```bash
curl "http://localhost:5000/api/ingest/all?keywords=tiler&maxResults=3" \
  | python3 -m json.tool
```

**预期结果:**
- 返回混合数据（SEEK + Indeed）
- `source` 字段正确标识每个职位来源
- 数据自动合并

### 5. 测试 Python API 直接调用

```bash
# 测试 SEEK 端点
curl -X POST http://localhost:8000/scrape/seek \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "plumber",
    "location": "Melbourne",
    "max_results": 2
  }' | python3 -m json.tool

# 测试 Indeed 端点
curl -X POST http://localhost:8000/scrape/indeed \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "electrician",
    "max_results": 2
  }' | python3 -m json.tool
```

### 6. 运行 Python 单元测试

```bash
cd scrape-api
/Users/kxz/anaconda3/bin/python -m pytest tests/ -v
```

**预期结果:**
```
============================== test session starts ==============================
...
tests/test_indeed_adapter.py::TestIndeedAdapter::test_parse_location PASSED
tests/test_seek_adapter.py::TestSeekAdapter::test_parse_location PASSED
tests/test_salary_parser.py::TestSalaryParser::test_parse_salary_range PASSED
...
============================== 103 passed in 2.45s ==============================
```

---

## 常见问题

### 问题 1: PostgreSQL 连接被拒绝

**错误信息:**
```
Npgsql.NpgsqlException: Failed to connect to 127.0.0.1:5432
Connection refused
```

**解决方法:**
```bash
# 检查 PostgreSQL 是否运行
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# 启动 PostgreSQL
brew services start postgresql@16     # macOS
sudo systemctl start postgresql       # Linux
```

### 问题 2: Permission denied for schema public

**错误信息:**
```
42501: permission denied for schema public
```

**解决方法:**
```bash
psql jobintel -c "GRANT ALL ON SCHEMA public TO admin;"
psql jobintel -c "ALTER SCHEMA public OWNER TO admin;"
```

### 问题 3: Python API 404 Not Found

**错误信息:**
```
{"detail":"Not Found"}
```

**可能原因:**
- 使用了错误的端点 URL
- Python API 未启动

**解决方法:**
```bash
# 检查 Python API 是否运行
curl http://localhost:8000/

# 正确的端点格式
curl -X POST http://localhost:8000/scrape/seek  # ✅ 正确
curl -X POST http://localhost:8000/scrape/jobs  # ❌ 错误（旧端点）
```

### 问题 4: .NET API 无法调用 Python API

**错误信息:**
```
HttpRequestException: Connection refused
```

**解决方法:**
1. 确认 Python API 在端口 8000 运行
2. 检查 `appsettings.json` 配置:
```json
{
  "ScrapeApi": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

### 问题 5: EF Migrations 失败

**错误信息:**
```
Build failed. Unable to locate the .NET SDK.
```

**解决方法:**
```bash
# 从 JobIntel.Api 目录运行
cd src/JobIntel.Api
dotnet ef database update

# 如果仍然失败，指定启动项目
cd src/JobIntel.Infrastructure
dotnet ef database update --startup-project ../JobIntel.Api
```

### 问题 6: Port 5000 或 8000 已被占用

**错误信息:**
```
Address already in use
```

**解决方法:**
```bash
# 查找占用端口的进程
lsof -i :5000  # macOS/Linux
lsof -i :8000

# 杀死进程（替换 PID）
kill -9 <PID>

# 或使用不同端口
dotnet run --urls="http://localhost:5001"  # .NET
uvicorn app.main:app --port 8001           # Python
```

### 问题 7: Python 依赖安装失败

**错误信息:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方法:**
```bash
# 使用 Anaconda 创建干净的环境
conda create -n jobintel python=3.10
conda activate jobintel

# 更新 pip
pip install --upgrade pip

# 重新安装依赖
cd scrape-api
pip install -r requirements.txt
```

### 问题 8: 数据库表不存在

**错误信息:**
```
42P01: relation "job_postings" does not exist
```

**解决方法:**
```bash
# 运行 migrations
cd src/JobIntel.Api
dotnet ef database update

# 验证表创建
psql -h localhost -U admin -d jobintel -c "\dt"
```

---

## 快速命令参考

### 启动所有服务

```bash
# 终端 1: PostgreSQL
brew services start postgresql@16

# 终端 2: Python API
cd /Users/kxz/Desktop/Web-practice/job-intelligence/scrape-api
/Users/kxz/anaconda3/bin/python -m uvicorn app.main:app --reload --port 8000

# 终端 3: .NET API
cd /Users/kxz/Desktop/Web-practice/job-intelligence/src/JobIntel.Api
dotnet run --urls="http://localhost:5000"
```

### 停止所有服务

```bash
# 停止 Python 和 .NET API: 在各自终端按 Ctrl+C

# 停止 PostgreSQL
brew services stop postgresql@16  # macOS
sudo systemctl stop postgresql    # Linux
```

### 快速测试

```bash
# 健康检查
curl http://localhost:8000/
curl http://localhost:5000/api/health

# 获取 SEEK 数据
curl "http://localhost:5000/api/ingest/seek?keywords=plumber&location=Sydney&maxResults=3"

# 获取所有平台数据
curl "http://localhost:5000/api/ingest/all?keywords=electrician&maxResults=5"
```

### 数据库操作

```bash
# 连接数据库
psql -h localhost -U admin -d jobintel

# 查看所有表
\dt

# 查询职位数量
SELECT COUNT(*) FROM job_postings;

# 查看最近的采集记录
SELECT * FROM ingest_runs ORDER BY started_at DESC LIMIT 5;

# 退出
\q
```

---

## 下一步

- 阅读 [PostgreSQL 教程](docs/tutorials/PostgreSQL-Guide.md) 学习数据库基础
- 查看 [.NET 集成完成报告](docs/DOTNET_INTEGRATION_COMPLETE.md) 了解实现细节
- 浏览 Swagger UI (http://localhost:5000/swagger) 测试所有 API 端点
- 查看 Hangfire Dashboard (http://localhost:5000/hangfire) 监控后台任务
- 开始开发数据持久化功能（下一个优先级）

---

## 支持

遇到问题？

1. 检查 [常见问题](#常见问题) 部分
2. 查看日志输出（终端中的错误信息）
3. 查阅 [PostgreSQL 教程](docs/tutorials/PostgreSQL-Guide.md) 的故障排查部分
4. 参考项目文档 [docs/](docs/) 目录

**项目状态:** ✅ 基础集成完成，可以开始开发新功能
