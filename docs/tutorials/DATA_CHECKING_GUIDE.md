# MVP 数据检查完全指南

**目标受众**: 开发者、测试人员、产品经理
**适用阶段**: MVP V1
**最后更新**: 2025-12-26

---

## 📋 目录

1. [快速开始](#快速开始)
2. [七种检查方式](#七种检查方式)
3. [实用脚本](#实用脚本)
4. [常见问题排查](#常见问题排查)
5. [最佳实践](#最佳实践)

---

## 快速开始

### 最简单的检查方式

```bash
# 1. 检查 API 健康状态
curl http://localhost:5000/api/health | jq

# 2. 查看数据库中的职位总数
psql -h localhost -p 5432 -U admin -d jobintel -c "SELECT COUNT(*) FROM job_postings;"

# 3. 运行完整数据质量检查
./scripts/check_data_quality.sh
```

---

## 七种检查方式

### 方式一：直接数据库查询 ⭐ 最推荐

**适用场景**: 验证数据准确性、深度分析

#### 连接数据库
```bash
psql -h localhost -p 5432 -U admin -d jobintel
```

#### 常用 SQL 查询

**1. 基础统计**
```sql
-- 总职位数
SELECT COUNT(*) FROM job_postings;

-- 活跃职位数
SELECT COUNT(*) FROM job_postings WHERE is_active = true;

-- 最新职位时间
SELECT MAX(posted_at) FROM job_postings;
```

**2. 按维度分组**
```sql
-- 按 trade 分组
SELECT trade, COUNT(*) as count
FROM job_postings
GROUP BY trade
ORDER BY count DESC;

-- 按州分组
SELECT location_state, COUNT(*) as count
FROM job_postings
GROUP BY location_state
ORDER BY count DESC;

-- 按来源分组
SELECT source, COUNT(*) as count
FROM job_postings
GROUP BY source;
```

**3. 数据质量检查**
```sql
-- 检查重复（相同 source_id）
SELECT source_id, COUNT(*) as count
FROM job_postings
GROUP BY source_id
HAVING COUNT(*) > 1;

-- Trade 提取成功率
SELECT
    COUNT(*) as total,
    COUNT(trade) as with_trade,
    ROUND(100.0 * COUNT(trade) / COUNT(*), 2) as percentage
FROM job_postings;

-- 地点提取成功率
SELECT
    COUNT(*) as total,
    COUNT(location_state) as with_location,
    ROUND(100.0 * COUNT(location_state) / COUNT(*), 2) as percentage
FROM job_postings;

-- 薪资数据完整性
SELECT
    COUNT(*) as total,
    COUNT(pay_range_min) as with_salary,
    ROUND(100.0 * COUNT(pay_range_min) / COUNT(*), 2) as percentage
FROM job_postings;
```

**4. 详细查看职位**
```sql
-- 最新 10 条职位
SELECT
    id,
    title,
    company,
    location_state,
    trade,
    employment_type,
    pay_range_min,
    posted_at
FROM job_postings
ORDER BY posted_at DESC
LIMIT 10;

-- 查看某个 trade 的职位
SELECT * FROM job_postings WHERE trade = 'carpenter' LIMIT 5;

-- 查看某个州的职位
SELECT * FROM job_postings WHERE location_state = 'NSW' LIMIT 5;
```

---

### 方式二：Postman API 测试 ⭐ 推荐用于功能测试

**适用场景**: 测试 API 端点、模拟前端调用

#### 设置步骤

1. 打开 Postman
2. 导入集合: `Job_Intelligence_API.postman_collection.json`
3. 设置环境变量:
   - `baseUrl` = `http://localhost:5000`
   - `sevenDaysAgo` = (计算 7 天前的日期，ISO 8601 格式)
   - `thirtyDaysAgo` = (计算 30 天前的日期，ISO 8601 格式)

#### 可用端点

**健康检查**
```
GET /api/health
```

**职位查询**
```
GET /api/jobs                              # 所有职位（分页）
GET /api/jobs?trade=tiler                  # 按 trade 筛选
GET /api/jobs?state=SA                     # 按州筛选
GET /api/jobs?trade=tiler&state=SA         # 组合筛选
GET /api/jobs?payMin=25&payMax=50          # 薪资范围
GET /api/jobs?employmentType=Full-time     # 工作类型
GET /api/jobs/{id}                         # 单个职位详情
```

**分析统计**
```
GET /api/analytics/stats                   # 整体统计
GET /api/analytics/by-trade                # 按 trade 统计
GET /api/analytics/by-state                # 按州统计
```

---

### 方式三：curl 命令行 ⭐ 快速测试

**适用场景**: 快速验证、脚本自动化

#### 常用命令

```bash
# 健康检查
curl http://localhost:5000/api/health | jq

# 获取所有职位（分页）
curl "http://localhost:5000/api/jobs?page=1&pageSize=10" | jq

# 按 trade 筛选
curl "http://localhost:5000/api/jobs?trade=carpenter" | jq '.jobs[] | {title, company, trade}'

# 按州筛选
curl "http://localhost:5000/api/jobs?state=NSW" | jq '.jobs[] | {title, location_state}'

# 组合筛选
curl "http://localhost:5000/api/jobs?trade=tiler&state=SA" | jq

# 获取统计数据
curl http://localhost:5000/api/analytics/stats | jq

# 按 trade 分组统计
curl http://localhost:5000/api/analytics/by-trade | jq

# 保存到文件
curl "http://localhost:5000/api/jobs?trade=carpenter" > /tmp/carpenter_jobs.json
```

---

### 方式四：Swagger UI

**适用场景**: 查看 API 文档、演示

#### 访问方式
1. 启动 .NET API
2. 浏览器访问: `http://localhost:5000/swagger`
3. 选择端点 → 填写参数 → 点击 "Execute"

---

### 方式五：Hangfire Dashboard

**适用场景**: 监控定时任务

#### 访问方式
1. 启动 .NET API
2. 浏览器访问: `http://localhost:5000/hangfire`
3. 查看:
   - **Jobs** - 所有任务
   - **Recurring Jobs** - 定时任务（65 个）
   - **Succeeded** - 成功的任务
   - **Failed** - 失败的任务

#### 可以做什么
- 查看任务执行历史
- 手动触发任务
- 查看失败原因
- 监控任务性能

---

### 方式六：Python 分析脚本 ⭐ 推荐用于报告

**适用场景**: 生成报告、数据分析

#### 使用方式

```bash
# 安装依赖（如果还没安装）
pip3 install psycopg2-binary

# 运行分析脚本（生成文本报告）
python3 scripts/analyze_data.py

# 导出为 JSON
python3 scripts/analyze_data.py --export json

# 导出为 CSV
python3 scripts/analyze_data.py --export csv

# 同时导出 JSON 和 CSV
python3 scripts/analyze_data.py --export both
```

#### 输出示例
```
==========================================
📊 Job Intelligence MVP - 数据分析报告
==========================================
生成时间: 2025-12-26 10:30:45

1️⃣ 基础统计
------------------------------------------
总职位数: 1250
活跃职位数: 1180

2️⃣ 数据来源分布
------------------------------------------
seek      :  980 (78.40%)
indeed    :  270 (21.60%)

3️⃣ Trade 分布（Top 10）
------------------------------------------
 1. carpenter         : 250
 2. electrician       : 220
 3. plumber          : 180
...

5️⃣ 数据质量评估
------------------------------------------
重复数据: 0 个
Trade 提取成功率: 96.5%
地点提取成功率: 100.0%
薪资数据完整性: 65.2%

整体质量评分: 98.83/100
✅ 优秀！数据质量达到生产标准
```

---

### 方式七：Shell 脚本完整检查 ⭐ 推荐用于定期检查

**适用场景**: 每日数据质量检查

#### 使用方式

```bash
# 运行完整检查
./scripts/check_data_quality.sh
```

#### 检查内容
1. ✅ 服务状态（数据库、API）
2. 📊 数据库基础统计
3. 📈 数据来源分布
4. 🏷️ Trade 分布
5. 🌏 地点分布
6. ✔️ 数据质量检查（去重、提取成功率）
7. 📋 采集任务统计
8. 👀 最近职位预览
9. 💯 数据质量评分

---

## 实用脚本

### 脚本 1: 数据质量检查脚本

**位置**: `scripts/check_data_quality.sh`

**功能**:
- 自动检查数据库连接
- 生成完整的数据质量报告
- 计算数据质量评分（0-100）

**使用**:
```bash
./scripts/check_data_quality.sh
```

---

### 脚本 2: Python 数据分析脚本

**位置**: `scripts/analyze_data.py`

**功能**:
- 统计分析
- 数据质量评估
- 导出 JSON/CSV

**使用**:
```bash
# 查看报告
python3 scripts/analyze_data.py

# 导出数据
python3 scripts/analyze_data.py --export both
```

---

## 常见问题排查

### 问题 1: 数据库连接失败

**症状**:
```
psql: error: connection to server at "localhost" (::1), port 5432 failed
```

**检查**:
```bash
# 检查 PostgreSQL 是否运行
brew services list | grep postgresql

# 启动 PostgreSQL
brew services start postgresql@16

# 测试连接
psql -h localhost -p 5432 -U admin -d jobintel -c "SELECT 1"
```

---

### 问题 2: API 无响应

**症状**:
```
curl: (7) Failed to connect to localhost port 5000
```

**检查**:
```bash
# 检查端口是否被占用
lsof -i :5000

# 启动 .NET API
cd src/JobIntel.Api
dotnet run
```

---

### 问题 3: 没有数据

**症状**:
```sql
SELECT COUNT(*) FROM job_postings;
-- 返回 0
```

**解决**:
```bash
# 1. 检查定时任务是否运行
# 访问 http://localhost:5000/hangfire

# 2. 手动触发一次抓取（使用 Postman 或 curl）
curl -X POST "http://localhost:5000/api/admin/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "seek",
    "keywords": ["carpenter"],
    "location": "Adelaide",
    "maxResults": 50
  }'
```

---

### 问题 4: 数据质量评分低

**症状**:
```
整体质量评分: 65.5 / 100
```

**排查**:
```sql
-- 检查重复数据
SELECT source_id, COUNT(*) FROM job_postings
GROUP BY source_id HAVING COUNT(*) > 1;

-- 检查 trade 提取
SELECT COUNT(*), COUNT(trade) FROM job_postings;

-- 检查地点提取
SELECT COUNT(*), COUNT(location_state) FROM job_postings;
```

**参考**: [数据质量修复报告](../core/DATA_QUALITY_FIXES_2025-12-26.md)

---

## 最佳实践

### 1. 每日检查清单

```bash
# 上午检查
./scripts/check_data_quality.sh

# 查看 Hangfire 任务
open http://localhost:5000/hangfire

# 检查 API 健康
curl http://localhost:5000/api/health | jq
```

---

### 2. 数据验证流程

**新抓取数据后**:
1. 检查数据量: `SELECT COUNT(*) FROM job_postings`
2. 检查去重: `SELECT source_id, COUNT(*) ... HAVING COUNT(*) > 1`
3. 检查地点: `SELECT location_state, COUNT(*) ... GROUP BY location_state`
4. 检查 trade: `SELECT trade, COUNT(*) ... GROUP BY trade`
5. 抽查几条数据: `SELECT * FROM job_postings ORDER BY posted_at DESC LIMIT 5`

---

### 3. 性能监控

```sql
-- 查看采集任务统计
SELECT
    source,
    COUNT(*) as runs,
    AVG(jobs_fetched) as avg_fetched,
    AVG(jobs_saved) as avg_saved,
    MAX(started_at) as last_run
FROM ingest_runs
GROUP BY source;

-- 查看数据增长趋势
SELECT
    DATE(created_at) as date,
    COUNT(*) as jobs_added
FROM job_postings
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 7;
```

---

### 4. 推荐检查组合

**场景 1: 开发调试**
- ✅ Postman（测试 API）
- ✅ psql（验证数据）
- ✅ curl（快速测试）

**场景 2: 数据质量验证**
- ✅ `check_data_quality.sh`（完整检查）
- ✅ psql（深度分析）
- ✅ `analyze_data.py`（生成报告）

**场景 3: 演示给用户**
- ✅ Swagger UI（API 文档）
- ✅ Postman（实时测试）
- ✅ Hangfire Dashboard（任务监控）

**场景 4: 定期监控**
- ✅ `check_data_quality.sh`（每日）
- ✅ Hangfire Dashboard（实时）
- ✅ `analyze_data.py --export json`（每周报告）

---

## 相关文档

- [数据质量修复报告](../core/DATA_QUALITY_FIXES_2025-12-26.md) - P0/P1 修复详情
- [PostgreSQL 教程](PostgreSQL-Guide.md) - 数据库使用指南
- [技术设计文档](../core/TECHNICAL_DESIGN.md) - 系统架构
- [开发指南](../core/DEVELOPMENT_GUIDE.md) - 开发规范

---

## 总结

MVP 阶段提供了 **7 种数据检查方式**，满足不同场景需求：

| 方式 | 难度 | 推荐度 | 适用场景 |
|------|------|--------|----------|
| 1. 数据库查询 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 数据验证、深度分析 |
| 2. Postman | ⭐⭐ | ⭐⭐⭐⭐⭐ | API 测试、功能验证 |
| 3. curl | ⭐⭐ | ⭐⭐⭐⭐ | 快速测试、脚本自动化 |
| 4. Swagger UI | ⭐ | ⭐⭐⭐ | 查看文档、演示 |
| 5. Hangfire | ⭐ | ⭐⭐⭐⭐ | 任务监控 |
| 6. Python 脚本 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 报告生成、数据导出 |
| 7. Shell 脚本 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 定期检查、完整验证 |

**推荐组合**: 数据库查询 + Postman + Shell 脚本

---

**文档创建**: 2025-12-26
**文档版本**: 1.0
**适用版本**: MVP V1
