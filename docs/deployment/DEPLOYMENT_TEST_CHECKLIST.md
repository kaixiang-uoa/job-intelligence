# 部署测试检查清单

**目的**: 确保每个服务部署后功能正常,数据流完整

**原则**: 先测试服务启动,再测试数据输入输出,最后测试端到端集成

---

## 📋 测试清单总览

```
第 1 阶段: PostgreSQL
  ├─ 服务启动检查
  ├─ 连接测试
  ├─ 数据库创建验证
  └─ 表结构检查

第 2 阶段: Python 爬虫 API
  ├─ 服务启动检查
  ├─ Health check 端点
  ├─ 单条数据爬取测试
  ├─ 数据格式验证
  └─ 写入数据库测试

第 3 阶段: .NET 后端 API
  ├─ 服务启动检查
  ├─ 数据库连接验证
  ├─ Health check 端点
  ├─ Swagger 文档访问
  ├─ 所有 API 端点测试
  └─ Hangfire Dashboard 访问

第 4 阶段: 端到端集成测试
  ├─ 完整数据流测试
  ├─ 定时任务验证
  ├─ 性能和资源监控
  └─ 错误处理测试
```

---

## 🔍 阶段 1: PostgreSQL 数据库

### 1.1 服务启动检查

```bash
# 启动 PostgreSQL
docker compose up -d postgres

# ✅ 检查点 1: 容器状态
docker compose ps postgres
# 期望: State = Up, 没有 "Restarting" 或 "Exit"

# ✅ 检查点 2: 查看启动日志
docker compose logs postgres | tail -20
# 期望: 看到 "database system is ready to accept connections"

# ✅ 检查点 3: 检查端口监听
docker compose exec postgres pg_isready -U admin
# 期望: "accepting connections"
```

**通过标准**:
- [ ] 容器状态为 `Up`
- [ ] 日志中有 "ready to accept connections"
- [ ] `pg_isready` 返回成功

---

### 1.2 连接测试

```bash
# ✅ 检查点 4: 使用 psql 连接
docker compose exec postgres psql -U admin -d jobintel
# 期望: 进入 psql 交互式界面

# 在 psql 中执行:
\l    # 列出所有数据库
\dt   # 列出所有表（应该为空,因为还没运行迁移）
\q    # 退出
```

**通过标准**:
- [ ] 能成功连接到数据库
- [ ] 看到 `jobintel` 数据库存在

---

### 1.3 数据库创建验证

```bash
# ✅ 检查点 5: 验证数据库配置
docker compose exec postgres psql -U admin -d jobintel -c "
SELECT
    current_database() as database,
    current_user as user,
    version() as postgres_version;
"

# 期望输出:
#  database | user  | postgres_version
# ----------+-------+------------------
#  jobintel | admin | PostgreSQL 16...
```

**通过标准**:
- [ ] 数据库名称为 `jobintel`
- [ ] 用户为 `admin`
- [ ] PostgreSQL 版本为 16.x

---

## 🐍 阶段 2: Python 爬虫 API

### 2.1 服务启动检查

```bash
# 启动 Python API
docker compose up -d python-api

# ✅ 检查点 6: 容器状态
docker compose ps python-api
# 期望: State = Up

# ✅ 检查点 7: 查看启动日志
docker compose logs python-api | tail -30
# 期望: 看到 "Uvicorn running on http://0.0.0.0:8000"
```

**通过标准**:
- [ ] 容器状态为 `Up`
- [ ] 日志显示 Uvicorn 启动成功

---

### 2.2 Health Check 端点测试

```bash
# ✅ 检查点 8: Health check
curl http://localhost:8000/health
# 期望: {"status":"healthy"}

# ✅ 检查点 9: API 文档访问
curl http://localhost:8000/docs
# 期望: 返回 HTML (FastAPI Swagger UI)
```

**通过标准**:
- [ ] `/health` 返回 `{"status":"healthy"}`
- [ ] `/docs` 可访问

---

### 2.3 单条数据爬取测试

```bash
# ✅ 检查点 10: 测试 Seek 爬虫（获取 5 条数据）
curl -X POST "http://localhost:8000/api/scrape/seek" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "Electrician",
    "location": "Sydney NSW",
    "max_results": 5
  }' | jq '.'

# 期望输出结构:
# {
#   "jobs": [
#     {
#       "source": "seek",
#       "source_id": "...",
#       "title": "...",
#       "company": "...",
#       "location": "...",
#       "state": "NSW",
#       "suburb": "Sydney",
#       "salary_min": ...,
#       "salary_max": ...,
#       "employment_type": "...",
#       "description": "...",
#       "url": "..."
#     }
#   ],
#   "count": 5,
#   "source": "seek"
# }
```

**通过标准**:
- [ ] 返回状态码 200
- [ ] `jobs` 数组不为空
- [ ] `count` 等于实际返回的职位数量
- [ ] 每个 job 对象包含必需字段 (见下方)

---

### 2.4 数据格式验证

**必需字段检查**:

```bash
# ✅ 检查点 11: 验证必需字段
# 保存上一步的 JSON 到文件
curl -X POST "http://localhost:8000/api/scrape/seek" \
  -H "Content-Type: application/json" \
  -d '{"keywords":"Electrician","location":"Sydney NSW","max_results":1}' \
  > /tmp/scrape_result.json

# 检查必需字段
cat /tmp/scrape_result.json | jq '.jobs[0] | {
  has_source: (.source != null),
  has_source_id: (.source_id != null),
  has_title: (.title != null),
  has_company: (.company != null),
  has_location: (.location != null),
  has_url: (.url != null)
}'

# 期望: 所有字段都为 true
```

**数据质量检查**:

| 字段 | 验证规则 | 检查命令 |
|------|---------|---------|
| `source` | = "seek" | `jq '.jobs[0].source'` |
| `source_id` | 非空字符串 | `jq '.jobs[0].source_id \| length'` |
| `state` | NSW/VIC/QLD/SA/WA/TAS/NT/ACT 之一 | `jq '.jobs[0].state'` |
| `salary_min` | ≥ 0 或 null | `jq '.jobs[0].salary_min'` |
| `employment_type` | Full-Time/Part-Time/Contract/Casual | `jq '.jobs[0].employment_type'` |

**通过标准**:
- [ ] 所有必需字段都存在
- [ ] `state` 是有效的澳洲州名
- [ ] `salary_min` ≤ `salary_max`（如果都不为 null）
- [ ] `employment_type` 是有效值

---

### 2.5 写入数据库测试（暂不执行，等 .NET API 部署后测试）

此步骤在阶段 3 完成后进行。

---

## 🔧 阶段 3: .NET 后端 API

### 3.1 服务启动检查

```bash
# 启动 .NET API
docker compose up -d dotnet-api

# ✅ 检查点 12: 容器状态
docker compose ps dotnet-api
# 期望: State = Up

# ✅ 检查点 13: 查看启动日志
docker compose logs dotnet-api | tail -50
# 期望: 看到 "Now listening on: http://[::]:5000"
```

**通过标准**:
- [ ] 容器状态为 `Up`
- [ ] 日志显示 "Now listening on"
- [ ] 没有错误日志（Exception, Error）

---

### 3.2 数据库连接验证

```bash
# ✅ 检查点 14: 检查数据库迁移是否执行
docker compose exec postgres psql -U admin -d jobintel -c "\dt"

# 期望: 看到以下表
# - job_postings
# - ingest_runs
# - hangfire 相关表
```

**通过标准**:
- [ ] `job_postings` 表存在
- [ ] `ingest_runs` 表存在
- [ ] Hangfire 表已创建

---

### 3.3 Health Check 端点测试

```bash
# ✅ 检查点 15: Health check
curl http://localhost:5000/api/health
# 期望: {"status":"Healthy","database":"Connected"}

# ✅ 检查点 16: Swagger UI 访问
curl -I http://localhost:5000/swagger
# 期望: HTTP/1.1 200 OK
```

**通过标准**:
- [ ] `/api/health` 返回 Healthy
- [ ] `/swagger` 可访问

---

### 3.4 所有 API 端点测试

#### 3.4.1 Ingest 端点测试

```bash
# ✅ 检查点 17: 通过 .NET API 触发 Seek 爬虫
curl "http://localhost:5000/api/ingest/seek?keywords=Plumber&location=Melbourne&maxResults=3"

# 期望输出:
# {
#   "jobs_found": 3,
#   "jobs_new": 3,
#   "jobs_updated": 0,
#   "jobs_deduped": 0,
#   "source": "seek",
#   "success": true
# }

# ✅ 检查点 18: 验证数据已写入数据库
docker compose exec postgres psql -U admin -d jobintel -c "
SELECT COUNT(*) as total_jobs FROM job_postings;
"
# 期望: total_jobs = 3

# ✅ 检查点 19: 查看写入的数据样例
docker compose exec postgres psql -U admin -d jobintel -c "
SELECT
    source,
    title,
    company,
    location_state,
    location_suburb,
    salary_min,
    salary_max,
    employment_type
FROM job_postings
LIMIT 3;
"
```

**通过标准**:
- [ ] API 返回 `success: true`
- [ ] `jobs_found` > 0
- [ ] 数据库中能查到对应数量的职位
- [ ] 数据字段完整

---

#### 3.4.2 Jobs 查询端点测试

```bash
# ✅ 检查点 20: 查询所有职位（分页）
curl "http://localhost:5000/api/jobs?page=1&pageSize=10" | jq '.'

# 期望输出:
# {
#   "items": [...],
#   "total": 3,
#   "page": 1,
#   "pageSize": 10,
#   "totalPages": 1
# }

# ✅ 检查点 21: 按 trade 筛选
curl "http://localhost:5000/api/jobs?trade=Plumber" | jq '.total'
# 期望: 返回筛选后的数量

# ✅ 检查点 22: 按 state 筛选
curl "http://localhost:5000/api/jobs?state=VIC" | jq '.total'

# ✅ 检查点 23: 获取单个职位详情
JOB_ID=$(curl -s "http://localhost:5000/api/jobs?pageSize=1" | jq -r '.items[0].id')
curl "http://localhost:5000/api/jobs/$JOB_ID" | jq '.'
# 期望: 返回完整的职位详情
```

**通过标准**:
- [ ] `/api/jobs` 返回分页数据
- [ ] `total` 字段正确
- [ ] 筛选功能正常工作
- [ ] `/api/jobs/{id}` 返回单个职位详情

---

### 3.5 Hangfire Dashboard 访问

```bash
# ✅ 检查点 24: Hangfire Dashboard 访问
curl -I http://localhost:5000/hangfire
# 期望: HTTP/1.1 200 OK (可能需要认证)

# 在浏览器中访问: http://VM_IP:5000/hangfire
# 用户名: admin
# 密码: (你在 .env 中设置的 HANGFIRE_PASSWORD)
```

**通过标准**:
- [ ] Hangfire Dashboard 可访问
- [ ] 能看到 Jobs, Recurring Jobs, Servers 等页面

---

## 🔄 阶段 4: 端到端集成测试

### 4.1 完整数据流测试

```bash
# ✅ 检查点 25: 完整流程测试 (Seek → .NET → DB → Query)

# 1. 触发爬取（获取 10 条 Electrician 职位）
curl "http://localhost:5000/api/ingest/seek?keywords=Electrician&location=Sydney&maxResults=10"

# 2. 等待 5 秒让数据写入
sleep 5

# 3. 查询数据库确认
docker compose exec postgres psql -U admin -d jobintel -c "
SELECT
    source,
    COUNT(*) as count,
    MIN(created_at) as first_job,
    MAX(created_at) as last_job
FROM job_postings
GROUP BY source;
"

# 4. 通过 API 查询
curl "http://localhost:5000/api/jobs?trade=Electrician&state=NSW" | jq '{
  total: .total,
  sample_titles: [.items[0:3][].title]
}'
```

**通过标准**:
- [ ] 数据能成功从 Seek 爬取
- [ ] 数据能正确存入数据库
- [ ] 能通过 API 查询到刚才爬取的数据
- [ ] 数据字段完整无缺失

---

### 4.2 去重功能验证

```bash
# ✅ 检查点 26: 测试去重功能

# 1. 记录当前职位总数
BEFORE=$(curl -s "http://localhost:5000/api/jobs" | jq '.total')
echo "Before: $BEFORE jobs"

# 2. 重复爬取相同的职位
curl "http://localhost:5000/api/ingest/seek?keywords=Electrician&location=Sydney&maxResults=5"

# 3. 检查职位总数是否增加
AFTER=$(curl -s "http://localhost:5000/api/jobs" | jq '.total')
echo "After: $AFTER jobs"

# 4. 验证去重统计
# 期望: jobs_new = 0, jobs_deduped > 0
```

**通过标准**:
- [ ] 重复爬取不会增加职位数量
- [ ] API 返回 `jobs_deduped > 0`

---

### 4.3 定时任务验证

```bash
# ✅ 检查点 27: 检查 Hangfire 定时任务

# 1. 在浏览器访问 Hangfire Dashboard
# http://VM_IP:5000/hangfire

# 2. 导航到 "Recurring Jobs" 页面

# 3. 验证任务列表
# 期望: 看到 65 个定时任务（13 trades × 5 states）
# 格式: "seek_[trade]_[state]_scrape" 例如 "seek_electrician_nsw_scrape"

# 4. 手动触发一个任务测试
# 点击任意任务的 "Trigger now" 按钮

# 5. 导航到 "Jobs" 页面查看执行结果
# 期望: 任务状态为 "Succeeded"
```

**通过标准**:
- [ ] 看到 65 个定时任务
- [ ] 任务名称格式正确
- [ ] 手动触发任务能成功执行
- [ ] 执行结果显示 "Succeeded"

---

### 4.4 性能和资源监控

```bash
# ✅ 检查点 28: 检查内存使用
docker stats --no-stream

# 期望输出类似:
# CONTAINER      MEM USAGE / LIMIT     MEM %
# postgres       120MB / 1GB          12%
# python-api     80MB / 1GB           8%
# dotnet-api     150MB / 1GB          15%
# nginx          10MB / 1GB           1%

# ✅ 检查点 29: 总内存使用
free -h

# 期望:
# - Used < 800MB (留有余地)
# - Available > 200MB
```

**通过标准**:
- [ ] 总内存使用 < 800MB
- [ ] 没有容器频繁重启
- [ ] `docker stats` 显示正常

---

### 4.5 错误处理测试

```bash
# ✅ 检查点 30: 测试无效参数
curl "http://localhost:5000/api/ingest/seek?keywords=&location=&maxResults=0"
# 期望: 返回 400 Bad Request 或适当的错误消息

# ✅ 检查点 31: 测试无效 trade
curl "http://localhost:5000/api/jobs?trade=InvalidTrade"
# 期望: 返回空结果或 400 错误

# ✅ 检查点 32: 测试数据库断连恢复
# 停止数据库
docker compose stop postgres
sleep 2

# 尝试查询（应该失败）
curl "http://localhost:5000/api/health"
# 期望: {"status":"Unhealthy","database":"Disconnected"}

# 重启数据库
docker compose start postgres
sleep 5

# 再次查询（应该恢复）
curl "http://localhost:5000/api/health"
# 期望: {"status":"Healthy","database":"Connected"}
```

**通过标准**:
- [ ] 无效参数返回适当错误
- [ ] 数据库断连后能检测到
- [ ] 数据库恢复后能自动重连

---

## 📊 最终验收标准

### ✅ 所有服务健康

```bash
# 一键检查所有服务状态
docker compose ps

# 期望: 所有服务状态都是 "Up"
```

| 服务 | 状态 | 端口 | Health Check |
|------|------|------|--------------|
| postgres | Up | 5432 | `pg_isready` ✅ |
| python-api | Up | 8000 | `/health` ✅ |
| dotnet-api | Up | 5000 | `/api/health` ✅ |
| nginx | Up | 80 | `/health` ✅ |

---

### ✅ 数据质量检查

```bash
# 检查数据质量
docker compose exec postgres psql -U admin -d jobintel -c "
SELECT
    -- 总职位数
    (SELECT COUNT(*) FROM job_postings) as total_jobs,

    -- 有薪资信息的职位占比
    (SELECT COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM job_postings), 0)
     FROM job_postings WHERE salary_min IS NOT NULL) as pct_with_salary,

    -- 有 trade 的职位占比
    (SELECT COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM job_postings), 0)
     FROM job_postings WHERE trade IS NOT NULL) as pct_with_trade,

    -- 重复职位数（应该为 0）
    (SELECT COUNT(*) - COUNT(DISTINCT fingerprint) FROM job_postings) as duplicates;
"
```

**期望结果**:
- [ ] `total_jobs` > 0
- [ ] `duplicates` = 0（没有重复）
- [ ] `pct_with_trade` > 90%
- [ ] `pct_with_salary` > 50%

---

### ✅ API 响应时间

```bash
# 测试 API 响应时间
time curl -s "http://localhost:5000/api/jobs?pageSize=100" > /dev/null

# 期望: real < 2s
```

**通过标准**:
- [ ] 查询 API 响应时间 < 2 秒
- [ ] Health check < 100ms

---

## 🎯 完整测试脚本

将上述所有检查点整合成一个自动化脚本:

```bash
#!/bin/bash
# 保存为: test_deployment.sh

echo "=== Job Intelligence Deployment Test Suite ==="
echo ""

PASSED=0
FAILED=0

function test_check() {
    local name="$1"
    local command="$2"

    echo -n "Testing: $name ... "
    if eval "$command" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((PASSED++))
    else
        echo "❌ FAIL"
        ((FAILED++))
    fi
}

# PostgreSQL Tests
echo "=== PostgreSQL Tests ==="
test_check "PostgreSQL container running" "docker compose ps postgres | grep -q 'Up'"
test_check "PostgreSQL accepting connections" "docker compose exec -T postgres pg_isready -U admin | grep -q 'accepting'"
test_check "Database 'jobintel' exists" "docker compose exec -T postgres psql -U admin -lqt | cut -d \\| -f 1 | grep -qw jobintel"

# Python API Tests
echo "=== Python API Tests ==="
test_check "Python API container running" "docker compose ps python-api | grep -q 'Up'"
test_check "Python API health check" "curl -sf http://localhost:8000/health | grep -q 'healthy'"

# .NET API Tests
echo "=== .NET API Tests ==="
test_check ".NET API container running" "docker compose ps dotnet-api | grep -q 'Up'"
test_check ".NET API health check" "curl -sf http://localhost:5000/api/health | grep -q 'Healthy'"

echo ""
echo "=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Please check the logs."
    exit 1
fi
```

---

## 📝 测试报告模板

测试完成后,填写此报告:

```markdown
# 部署测试报告

**测试日期**: YYYY-MM-DD
**测试人员**: Your Name
**VM IP**: 20.92.200.112

## 测试结果汇总

| 阶段 | 通过检查点 | 总检查点 | 状态 |
|------|-----------|---------|------|
| PostgreSQL | __/5 | 5 | ✅/❌ |
| Python API | __/11 | 11 | ✅/❌ |
| .NET API | __/13 | 13 | ✅/❌ |
| 集成测试 | __/8 | 8 | ✅/❌ |

## 数据质量

- 总职位数: __
- 重复职位数: __ (应为 0)
- Trade 提取率: __%
- 薪资提取率: __%

## 性能指标

- API 平均响应时间: __ ms
- 总内存使用: __ MB / 1024 MB
- PostgreSQL 内存: __ MB
- Python API 内存: __ MB
- .NET API 内存: __ MB

## 发现的问题

1.
2.
3.

## 结论

[ ] 部署成功,所有测试通过
[ ] 部署成功,存在小问题但不影响使用
[ ] 部署失败,需要修复后重新测试
```

---

**准备好开始部署了吗？我们将严格按照这个测试清单逐步验证每个服务！**
