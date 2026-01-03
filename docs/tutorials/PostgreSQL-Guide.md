# PostgreSQL 完全指南 - 从零到实战

> **适合人群:** 完全没有数据库经验的小白
> **学习目标:** 掌握 PostgreSQL 基础操作，能够独立管理本项目的数据库
> **实战项目:** Job Intelligence Platform

---

## 📚 目录

1. [什么是 PostgreSQL？](#1-什么是-postgresql)
2. [为什么选择 PostgreSQL？](#2-为什么选择-postgresql)
3. [安装和配置](#3-安装和配置)
4. [基础概念](#4-基础概念)
5. [常用命令](#5-常用命令)
6. [SQL 基础](#6-sql-基础)
7. [实战：Job Intelligence 数据库](#7-实战job-intelligence-数据库)
8. [常见问题和解决方案](#8-常见问题和解决方案)
9. [进阶学习资源](#9-进阶学习资源)

---

## 1. 什么是 PostgreSQL？

### 简单理解

想象一下你有很多文件柜（数据库），每个柜子里有很多抽屉（表），每个抽屉里有很多文件夹（行），每个文件夹里有不同类型的信息（列）。

**PostgreSQL** 就是一个非常聪明的管理员，它可以：
- 🗄️ **存储数据** - 安全地保存你的数据
- 🔍 **快速查找** - 几毫秒内从百万条数据中找到你要的
- 🔒 **保护数据** - 确保数据不会丢失或损坏
- 📊 **分析数据** - 帮你统计、计算、分析

### 技术定义

PostgreSQL 是一个**开源的关系型数据库管理系统 (RDBMS)**，特点：
- ✅ 完全免费，开源
- ✅ 功能强大，支持复杂查询
- ✅ 可靠性高，数据安全
- ✅ 支持 JSON、数组等现代数据类型
- ✅ 社区活跃，文档丰富

---

## 2. 为什么选择 PostgreSQL？

### 与其他数据库对比

| 特性 | PostgreSQL | MySQL | SQLite |
|------|-----------|-------|--------|
| **开源** | ✅ 完全开源 | ⚠️ 部分开源 | ✅ 开源 |
| **JSON 支持** | ✅ 强大的 JSONB | ⚠️ 基础支持 | ❌ 无 |
| **复杂查询** | ✅ 优秀 | ⚠️ 一般 | ⚠️ 基础 |
| **全文搜索** | ✅ 内置强大功能 | ⚠️ 有限 | ❌ 无 |
| **适用场景** | 企业级应用 | Web 应用 | 嵌入式/小型应用 |

### 本项目为什么选 PostgreSQL？

1. **JSON 原生支持** - 我们的 `tags` 字段存储 JSON 数据
2. **全文搜索** - 搜索职位描述中的关键词
3. **高性能** - 处理大量职位数据
4. **已配置好** - 代码已经使用 PostgreSQL，无需修改

---

## 3. 安装和配置

### macOS 安装（使用 Homebrew）

```bash
# 1. 安装 PostgreSQL 16
brew install postgresql@16

# 2. 启动服务（开机自动启动）
brew services start postgresql@16

# 3. 验证安装
/opt/homebrew/opt/postgresql@16/bin/psql --version
# 应该显示：psql (PostgreSQL) 16.x
```

### Windows 安装

1. 下载官方安装包：https://www.postgresql.org/download/windows/
2. 运行安装程序，按照向导操作
3. 记住你设置的密码（默认用户名是 `postgres`）

### Linux (Ubuntu/Debian) 安装

```bash
# 1. 更新包列表
sudo apt update

# 2. 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 3. 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 验证安装成功

```bash
# 连接到 PostgreSQL（macOS/Linux）
psql postgres

# 你应该看到这样的提示符：
# postgres=#

# 输入 \q 退出
\q
```

---

## 4. 基础概念

### 4.1 数据库架构层次

```
PostgreSQL 服务器
    ├─ 数据库1 (jobintel)          ← 我们的项目数据库
    │   ├─ Schema (public)          ← 默认 schema
    │   │   ├─ 表1 (job_postings)   ← 职位数据表
    │   │   ├─ 表2 (ingest_runs)    ← 采集记录表
    │   │   └─ 索引、约束等
    │   └─ Schema (其他)
    ├─ 数据库2 (其他项目)
    └─ 数据库3
```

### 4.2 核心概念解释

#### 数据库 (Database)
- 一个独立的数据容器
- 就像一个完整的 Excel 文件
- 我们的项目有一个叫 `jobintel` 的数据库

#### 表 (Table)
- 存储具体数据的地方
- 就像 Excel 中的一个工作表
- 我们有 `job_postings`（职位）、`ingest_runs`（采集记录）等表

#### 行 (Row) / 记录 (Record)
- 表中的一条数据
- 就像 Excel 中的一行
- 例如：一个职位信息就是一行

#### 列 (Column) / 字段 (Field)
- 数据的一个属性
- 就像 Excel 中的一列
- 例如：`title`（职位标题）、`company`（公司名）

#### 主键 (Primary Key)
- 唯一标识一行数据的字段
- 通常是 `id`
- 就像身份证号，每个人都不同

#### 索引 (Index)
- 加快查询速度的机制
- 就像书的目录
- 我们在 `trade`（职业）、`location_state`（州）等字段上建了索引

---

## 5. 常用命令

### 5.1 连接数据库

```bash
# 连接到默认数据库（macOS）
psql postgres

# 连接到指定数据库
psql jobintel

# 以特定用户连接
psql -U admin -d jobintel

# 指定主机和端口
psql -h localhost -p 5432 -U admin -d jobintel
```

### 5.2 psql 工具命令（在 psql 提示符下）

```sql
-- 查看所有数据库
\l

-- 连接到指定数据库
\c jobintel

-- 查看当前数据库的所有表
\dt

-- 查看表结构
\d job_postings

-- 查看表的详细信息（包括索引）
\d+ job_postings

-- 查看所有用户
\du

-- 退出 psql
\q

-- 查看帮助
\?
```

### 5.3 服务管理命令

```bash
# macOS (使用 Homebrew)
brew services start postgresql@16    # 启动
brew services stop postgresql@16     # 停止
brew services restart postgresql@16  # 重启
brew services list                   # 查看状态

# Linux (使用 systemctl)
sudo systemctl start postgresql      # 启动
sudo systemctl stop postgresql       # 停止
sudo systemctl restart postgresql    # 重启
sudo systemctl status postgresql     # 查看状态
```

---

## 6. SQL 基础

### 6.1 创建数据库和用户

```sql
-- 创建数据库
CREATE DATABASE jobintel;

-- 创建用户
CREATE USER admin WITH PASSWORD 'dev123';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE jobintel TO admin;

-- 授予 schema 权限（PostgreSQL 特有）
GRANT ALL ON SCHEMA public TO admin;
```

### 6.2 创建表

```sql
-- 创建一个简单的表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,           -- 自增主键
    username VARCHAR(50) NOT NULL,    -- 字符串，最多50字符
    email VARCHAR(100) UNIQUE,        -- 唯一约束
    created_at TIMESTAMP DEFAULT NOW() -- 默认当前时间
);
```

### 6.3 插入数据 (INSERT)

```sql
-- 插入单条数据
INSERT INTO users (username, email)
VALUES ('john_doe', 'john@example.com');

-- 插入多条数据
INSERT INTO users (username, email)
VALUES
    ('jane_smith', 'jane@example.com'),
    ('bob_wilson', 'bob@example.com');
```

### 6.4 查询数据 (SELECT)

```sql
-- 查询所有数据
SELECT * FROM users;

-- 查询特定字段
SELECT username, email FROM users;

-- 条件查询
SELECT * FROM users WHERE username = 'john_doe';

-- 模糊查询
SELECT * FROM users WHERE email LIKE '%@example.com';

-- 排序
SELECT * FROM users ORDER BY created_at DESC;

-- 限制数量
SELECT * FROM users LIMIT 10;

-- 分页（跳过前10条，取10条）
SELECT * FROM users LIMIT 10 OFFSET 10;
```

### 6.5 更新数据 (UPDATE)

```sql
-- 更新单个字段
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- 更新多个字段
UPDATE users
SET username = 'new_username', email = 'new@example.com'
WHERE id = 1;

-- ⚠️ 注意：没有 WHERE 会更新所有行！
UPDATE users SET email = 'same@example.com';  -- 危险！
```

### 6.6 删除数据 (DELETE)

```sql
-- 删除特定行
DELETE FROM users WHERE id = 1;

-- 删除满足条件的所有行
DELETE FROM users WHERE created_at < '2024-01-01';

-- ⚠️ 注意：没有 WHERE 会删除所有数据！
DELETE FROM users;  -- 危险！会清空表！
```

### 6.7 聚合查询

```sql
-- 统计总数
SELECT COUNT(*) FROM users;

-- 分组统计
SELECT email_domain, COUNT(*)
FROM (
    SELECT SUBSTRING(email FROM POSITION('@' IN email) + 1) AS email_domain
    FROM users
) AS subquery
GROUP BY email_domain;

-- 计算平均值、最大值、最小值
SELECT
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary,
    MIN(salary) as min_salary
FROM job_postings;
```

---

## 7. 实战：Job Intelligence 数据库

### 7.1 我们的数据库结构

```sql
-- 查看我们的数据库
\c jobintel

-- 查看所有表
\dt

-- 应该看到：
-- public | job_postings        | table | admin
-- public | ingest_runs         | table | admin
-- public | __EFMigrationsHistory | table | admin
```

### 7.2 job_postings 表结构

```sql
-- 查看表结构
\d job_postings
```

**主要字段说明：**

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `id` | integer | 主键，自增 | 1, 2, 3... |
| `source` | varchar(50) | 数据来源 | "seek", "indeed" |
| `source_id` | varchar(255) | 平台原始ID | "89264918" |
| `title` | varchar(500) | 职位标题 | "Plumber - Sydney" |
| `company` | varchar(255) | 公司名称 | "ABC Plumbing" |
| `location_state` | varchar(50) | 州 | "NSW", "VIC" |
| `location_suburb` | varchar(100) | 郊区/城市 | "Sydney", "Melbourne" |
| `trade` | varchar(50) | 职业类型 | "plumber", "electrician" |
| `employment_type` | varchar(50) | 工作类型 | "Full Time", "Part Time" |
| `pay_range_min` | numeric(10,2) | 最低薪资 | 80000.00 |
| `pay_range_max` | numeric(10,2) | 最高薪资 | 100000.00 |
| `description` | text | 职位描述 | 长文本 |
| `tags` | text | 标签 (JSON) | `["visa_support"]` |
| `posted_at` | timestamp | 发布时间 | 2025-12-21 20:16:50 |
| `scraped_at` | timestamp | 爬取时间 | 2025-12-22 01:06:58 |
| `is_active` | boolean | 是否有效 | true/false |

### 7.3 常用查询示例

#### 查看所有职位

```sql
SELECT * FROM job_postings LIMIT 10;
```

#### 查找 Sydney 的 plumber 职位

```sql
SELECT title, company, location_suburb, pay_range_min, pay_range_max
FROM job_postings
WHERE trade = 'plumber'
  AND location_state = 'NSW'
  AND location_suburb LIKE '%Sydney%'
ORDER BY posted_at DESC;
```

#### 统计每个职业的职位数量

```sql
SELECT trade, COUNT(*) as job_count
FROM job_postings
WHERE is_active = true
GROUP BY trade
ORDER BY job_count DESC;
```

#### 查找薪资最高的10个职位

```sql
SELECT title, company, trade, pay_range_max
FROM job_postings
WHERE pay_range_max IS NOT NULL
ORDER BY pay_range_max DESC
LIMIT 10;
```

#### 统计每个州的平均薪资

```sql
SELECT
    location_state,
    COUNT(*) as job_count,
    AVG(pay_range_min) as avg_min_salary,
    AVG(pay_range_max) as avg_max_salary
FROM job_postings
WHERE pay_range_min IS NOT NULL
GROUP BY location_state
ORDER BY avg_max_salary DESC;
```

#### 查找最近7天发布的职位

```sql
SELECT title, company, posted_at
FROM job_postings
WHERE posted_at > NOW() - INTERVAL '7 days'
ORDER BY posted_at DESC;
```

#### 全文搜索（搜索描述中包含 "visa" 的职位）

```sql
SELECT title, company, location_state
FROM job_postings
WHERE description ILIKE '%visa%'  -- ILIKE 不区分大小写
   OR description ILIKE '%sponsorship%'
LIMIT 20;
```

### 7.4 数据统计查询

```sql
-- 整体统计
SELECT
    COUNT(*) as total_jobs,
    COUNT(DISTINCT source) as sources,
    COUNT(DISTINCT trade) as trades,
    COUNT(DISTINCT location_state) as states,
    AVG(pay_range_max) as avg_max_salary
FROM job_postings
WHERE is_active = true;
```

### 7.5 清空测试数据

```sql
-- ⚠️ 谨慎使用！这会删除所有职位数据
TRUNCATE TABLE job_postings RESTART IDENTITY CASCADE;

-- 删除特定来源的数据
DELETE FROM job_postings WHERE source = 'seek';
```

---

## 8. 常见问题和解决方案

### 问题 1: 连接被拒绝 (Connection refused)

**错误信息：**
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**解决方案：**
```bash
# 检查 PostgreSQL 是否运行
brew services list

# 启动 PostgreSQL
brew services start postgresql@16
```

### 问题 2: 权限错误 (Permission denied)

**错误信息：**
```
ERROR: permission denied for schema public
```

**解决方案：**
```sql
-- 授予用户权限
GRANT ALL ON SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
```

### 问题 3: 表不存在 (relation does not exist)

**错误信息：**
```
ERROR: relation "job_postings" does not exist
```

**解决方案：**
```bash
# 运行 EF Core migrations 创建表
cd src/JobIntel.Api
dotnet ef database update
```

### 问题 4: 忘记密码

**解决方案：**

1. 修改 `pg_hba.conf` 配置文件（临时允许无密码登录）
2. 重置密码
3. 恢复原配置

```bash
# 1. 找到配置文件
/opt/homebrew/opt/postgresql@16/bin/pg_config --sysconfdir

# 2. 编辑 pg_hba.conf，将 md5 改为 trust
# local   all   all   trust

# 3. 重启 PostgreSQL
brew services restart postgresql@16

# 4. 登录并重置密码
psql postgres
ALTER USER admin WITH PASSWORD 'newpassword';

# 5. 改回 md5，重启服务
```

### 问题 5: 端口被占用

**错误信息：**
```
could not bind IPv4 address "127.0.0.1": Address already in use
```

**解决方案：**
```bash
# 查找占用 5432 端口的进程
lsof -i :5432

# 停止进程
kill -9 <PID>

# 或者使用不同端口启动 PostgreSQL
```

---

## 9. 进阶学习资源

### 9.1 官方文档
- 📖 PostgreSQL 官方文档（英文）：https://www.postgresql.org/docs/
- 📖 PostgreSQL 中文文档：http://www.postgres.cn/docs/16/

### 9.2 推荐书籍
- 📚 《PostgreSQL 即学即用》- 适合初学者
- 📚 《PostgreSQL 实战》- 进阶实战
- 📚 《PostgreSQL 数据库内核分析》- 深入理解

### 9.3 在线教程
- 🎓 PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- 🎓 W3Schools SQL: https://www.w3schools.com/sql/

### 9.4 实用工具推荐

#### GUI 工具
- **pgAdmin** - 官方免费 GUI 工具
- **DBeaver** - 开源、跨平台、支持多种数据库
- **TablePlus** - 简洁美观（macOS）

#### 命令行增强
- **pgcli** - 更好用的 psql，有自动补全和语法高亮

```bash
# 安装 pgcli
brew install pgcli

# 使用
pgcli jobintel
```

### 9.5 本项目相关进阶主题

#### JSON 查询（我们的 tags 字段）

```sql
-- 查询包含特定 tag 的职位
SELECT * FROM job_postings
WHERE tags::jsonb @> '["visa_support"]';

-- 提取 JSON 字段
SELECT title, tags::jsonb->0 as first_tag
FROM job_postings
WHERE tags IS NOT NULL;
```

#### 全文搜索索引

```sql
-- 创建全文搜索索引（提升搜索性能）
CREATE INDEX idx_description_fts
ON job_postings
USING GIN(to_tsvector('english', description));

-- 使用全文搜索
SELECT title, company
FROM job_postings
WHERE to_tsvector('english', description) @@ to_tsquery('plumber & visa');
```

#### 性能优化

```sql
-- 查看查询执行计划
EXPLAIN ANALYZE
SELECT * FROM job_postings WHERE trade = 'plumber';

-- 查看索引使用情况
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'job_postings';
```

---

## 📝 总结

### 你已经学会了：

✅ PostgreSQL 是什么，为什么选择它
✅ 如何安装和启动 PostgreSQL
✅ 基本概念：数据库、表、行、列
✅ 常用 SQL 命令：SELECT, INSERT, UPDATE, DELETE
✅ 如何操作 Job Intelligence 项目的数据库
✅ 常见问题的解决方案

### 下一步学习：

1. **多练习** - 多写 SQL 查询，熟能生巧
2. **阅读文档** - PostgreSQL 官方文档是最好的学习资源
3. **实战项目** - 在我们的项目中实践所学知识
4. **进阶主题** - 学习索引优化、事务、备份恢复等

---

## 🔗 快速参考

### 常用命令速查

```bash
# 连接数据库
psql jobintel

# psql 内部命令
\l          # 列出所有数据库
\c dbname   # 切换数据库
\dt         # 列出所有表
\d table    # 查看表结构
\q          # 退出

# SQL 命令
SELECT * FROM table_name;           # 查询
INSERT INTO table_name VALUES (...);  # 插入
UPDATE table_name SET ...;          # 更新
DELETE FROM table_name WHERE ...;   # 删除
```

### 本项目数据库连接信息

```
主机: localhost
端口: 5432
数据库: jobintel
用户名: admin
密码: dev123
```

---

**祝学习愉快！有问题随时查阅本文档或搜索官方文档。** 🎓

**最后更新:** 2025-12-22
