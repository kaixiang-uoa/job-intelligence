# Job Intelligence Platform - V1 MVP

> **最后更新:** 2025-12-26
> **当前阶段:** ✅ **数据质量修复完成 - 系统可部署**
> **开发策略:** V1 专注后端 API + 爬虫，V2 添加用户系统 + 前端
> **数据质量:** 95%+ (P0/P1 问题全部修复)

## 🎯 项目概述

Job Intelligence 是一个职位市场情报和分析平台，帮助蓝领技工（水管工、电工、瓦工等）聚合和分析来自 SEEK、Indeed 等平台的职位信息。

### 核心功能
- ✅ **多平台职位聚合** - 从 SEEK 和 Indeed 自动抓取职位数据
- ✅ **智能数据解析** - 自动提取地区、行业、薪资等关键信息
- ✅ **高质量数据** - 去重 100%，地点过滤 100%，Trade提取 95%+
- ✅ **定时任务** - 65个自动化任务，每6小时抓取一次
- 📊 **RESTful API** - 标准化 API 供前端调用

### 🎉 最新更新 (2025-12-26)

**数据质量修复完成！** 所有 P0 和 P1 问题已修复，系统达到生产部署标准。

- ✅ **P0 修复**: 重复数据问题 - 0个重复 (之前 20% 重复率)
- ✅ **P1 修复**: 地点过滤 - 100% 准确 (之前 50% 准确率)
- ✅ **P1 修复**: Trade 提取 - 95%+ 成功率 (SEEK 100%, Indeed 90%+)
- 📈 **整体提升**: 数据质量从 60-70% → 95%+

详见：[数据质量修复报告](docs/core/DATA_QUALITY_FIXES_2025-12-26.md)

### 技术架构
```
前端 (待开发)
    ↓
.NET 8 API (端口 5000)
    ├─ IngestController - 数据采集
    ├─ JobsController - 职位查询
    ├─ PostgreSQL 数据库
    └─ Hangfire 后台任务
    ↓
Python FastAPI (端口 8000)
    ├─ SEEK 适配器
    ├─ Indeed 适配器
    └─ 数据标准化
    ↓
外部数据源 (SEEK, Indeed)
```

## 📊 项目进度

### ✅ V1 MVP 已完成 (100%)

**Python 爬虫 API** (2025-12-26) - ⭐ 生产就绪
- ✅ FastAPI 服务 (端口 8000)
- ✅ SEEK 适配器 - **100% 数据质量** (地点过滤、去重已修复)
- ✅ Indeed 适配器 - **95%+ 数据质量**
- ✅ 位置解析引擎 - 支持复杂格式
- ✅ 薪资解析引擎 - 多币种、多格式
- ✅ 数据标准化和清洗
- ✅ **双层去重** - Python层 + 数据库层
- ✅ 103 个单元测试 - 100% 通过

**数据库** (2025-12-22)
- ✅ PostgreSQL 16 安装和配置
- ✅ EF Core Migrations
- ✅ 表结构：job_postings, ingest_runs
- ✅ 索引优化 (fingerprint, source_id, trade+state)

**.NET 后端集成** (2025-12-26) - ⭐ 生产就绪
- ✅ IngestController - 数据采集端点 + 调试功能
  - `GET /api/ingest/seek` - SEEK 数据
  - `GET /api/ingest/indeed` - Indeed 数据
  - `GET /api/ingest/all` - 并行获取所有平台
  - `saveToFile` 参数 - 保存原始数据到 /tmp 供调试
- ✅ ScrapeApiClient - Python API 客户端
- ✅ 数据模型完全对齐 (RawJobData ↔ JobPostingDTO)
- ✅ 端到端测试通过

**数据持久化** (2025-12-24) - ✅ 完成
- ✅ IngestionPipeline（数据标准化、去重）
- ✅ DeduplicationService（fingerprint + content_hash）
- ✅ Hangfire 后台任务
- ✅ Repository 层
- ✅ 数据更新策略（new/updated/duplicate）

**查询 API** (2025-12-24) - ✅ 完成
- ✅ JobsController - 完整实现
- ✅ `GET /api/jobs` - 搜索和筛选职位（分页、排序、多维过滤）
- ✅ `GET /api/jobs/{id}` - 获取职位详情
- ✅ 多维度过滤（trade, state, suburb, salary, employment_type, posted_after）
- ✅ 12 个 DTOs
- ✅ Swagger 文档

**定时任务** (2025-12-24) - ✅ 完成
- ✅ **65个自动化任务** (13 trades × 5 cities)
- ✅ 每6小时执行一次（0 */6 * * *）
- ✅ Hangfire Dashboard 可视化管理
- ✅ 自动去重和保存
- ✅ 完整的日志和监控

**数据质量修复** (2025-12-26) - ✅ 完成
- ✅ P0: 重复数据 - 0个重复 (100% 修复)
- ✅ P1: 地点过滤 - 100% 准确
- ✅ P1: Trade 提取 - 95%+ 成功率
- ✅ 整体数据质量：95%+

### 🔖 下一阶段规划

**V1.5 - 数据质量优化** (1-2周)
- [ ] Indeed 后处理过滤（丢弃 trade=null）
- [ ] 改进薪资数据解析
- [ ] 基于描述的 trade 二次提取
- [ ] AI 增强的职位分类

**V2 - 用户系统和前端** (2-3个月)
- [ ] 用户注册/登录
- [ ] React/Vue 前端
- [ ] 职位搜索界面
- [ ] 职位详情页面
- [ ] 保存的职位功能
- [ ] Job Alerts 订阅

详见：
- **[MVP V1 完成报告](docs/MVP_V1_COMPLETION.md)** 🎉 - V1 最终完成报告
- [V1 完成总结](docs/core/V1_COMPLETION_SUMMARY.md) - 功能清单和测试结果
- [数据质量修复报告](docs/core/DATA_QUALITY_FIXES_2025-12-26.md) - P0/P1 修复详情

---

## Implementation Summary

### Sprint 1.3 - Ingestion Pipeline ✅

Complete **Ingestion Pipeline** as specified in the Technical Design Document.

## What Has Been Implemented

### ✅ Core Entities
- **JobPosting** entity with all required fields ([JobPosting.cs](src/JobIntel.Core/Entities/JobPosting.cs))
- **IngestRun** entity for audit logging ([IngestRun.cs](src/JobIntel.Core/Entities/IngestRun.cs))

### ✅ Interfaces
- **IScrapeApiClient** - Interface for Python Scrape API communication
- **IIngestionPipeline** - Interface for processing raw job data
- **IDeduplicationService** - Interface for fingerprint and content hash generation
- **IJobRepository** - Repository interface for JobPosting CRUD operations
- **IIngestRunRepository** - Repository interface for IngestRun tracking

### ✅ Services

#### DeduplicationService ([DeduplicationService.cs](src/JobIntel.Ingest/Services/DeduplicationService.cs))
- Implements fingerprint generation: `SHA256(source:source_id:title:company:state:suburb)`
- Implements content hash generation for detecting job description changes
- String normalization for consistent hashing

#### ScrapeApiClient ([ScrapeApiClient.cs](src/JobIntel.Ingest/Services/ScrapeApiClient.cs))
- HTTP client for communicating with Python Scrape API
- POST `/scrape/jobs` endpoint integration
- Configurable via `appsettings.json`

#### IngestionPipeline ([IngestionPipeline.cs](src/JobIntel.Ingest/Services/IngestionPipeline.cs))
Complete pipeline with the following stages:

1. **Normalization**
   - Parse location into state and suburb
   - Extract trade category from job title
   - Normalize employment type
   - Parse salary range
   - Extract requirements from description
   - Generate tags (visa_sponsor, entry_level, experienced, remote)
   - Clean HTML and trim whitespace

2. **Deduplication**
   - Generate fingerprint for each job
   - Check existing jobs by fingerprint
   - Compare content hash to detect changes

3. **Storage**
   - Insert new jobs
   - Update changed jobs
   - Skip duplicates
   - Update last_checked_at timestamp

### ✅ Infrastructure

#### Database Context ([JobIntelDbContext.cs](src/JobIntel.Infrastructure/Data/JobIntelDbContext.cs))
- EF Core DbContext with JobPostings and IngestRuns DbSets

#### Entity Configurations
- **JobPostingConfiguration** - Complete table schema with indexes ([JobPostingConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/JobPostingConfiguration.cs))
  - Indexes: source, trade+state, posted_at, is_active, fingerprint (unique), content_hash
  - Unique constraint on source + source_id
- **IngestRunConfiguration** - Audit table schema ([IngestRunConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/IngestRunConfiguration.cs))
  - Indexes: source+started_at, status

#### Repositories
- **JobRepository** - CRUD operations for JobPosting ([JobRepository.cs](src/JobIntel.Infrastructure/Repositories/JobRepository.cs))
- **IngestRunRepository** - CRUD operations for IngestRun ([IngestRunRepository.cs](src/JobIntel.Infrastructure/Repositories/IngestRunRepository.cs))

### ✅ Background Jobs

#### ScrapeJob ([ScrapeJob.cs](src/JobIntel.Ingest/Jobs/ScrapeJob.cs))
Hangfire background job following Development Guide Section 4.4:

1. Create IngestRun record (status: Running)
2. Call ScrapeApiClient to fetch jobs
3. Process jobs through IngestionPipeline
4. Update IngestRun with results (new, updated, deduped counts)
5. Handle errors and update status

### ✅ API Configuration

#### Program.cs ([Program.cs](src/JobIntel.Api/Program.cs))
- Database connection with PostgreSQL + EF Core
- Hangfire setup with PostgreSQL storage
- Dependency injection for all services
- Swagger/OpenAPI documentation
- CORS configuration for development

#### Endpoints
- **GET /api/health** - Health check endpoint with database status
- **POST /api/admin/scrape** - Trigger manual scrape job
- **GET /hangfire** - Hangfire dashboard for monitoring background jobs

## Project Structure

```
JobIntel/
├── JobIntel.sln
├── src/
│   ├── JobIntel.Api/              # Web API Layer
│   │   ├── Program.cs             # Application startup and DI
│   │   └── appsettings.json       # Configuration
│   │
│   ├── JobIntel.Core/             # Domain Layer (no dependencies)
│   │   ├── Entities/              # JobPosting, IngestRun
│   │   ├── DTOs/                  # RawJobData, IngestionResult
│   │   └── Interfaces/            # Service contracts
│   │
│   ├── JobIntel.Infrastructure/   # Data Access Layer
│   │   ├── Data/
│   │   │   ├── JobIntelDbContext.cs
│   │   │   └── Configurations/    # Entity configurations
│   │   └── Repositories/          # Repository implementations
│   │
│   └── JobIntel.Ingest/           # Background Jobs Layer
│       ├── Jobs/
│       │   └── ScrapeJob.cs       # Hangfire job
│       └── Services/
│           ├── ScrapeApiClient.cs
│           ├── IngestionPipeline.cs
│           └── DeduplicationService.cs
```

## 快速开始

详细的启动指南请查看 [GETTING_STARTED.md](GETTING_STARTED.md)

### 一键启动（快速版）

```bash
# 1. 启动 PostgreSQL
brew services start postgresql@16

# 2. 启动 Python 爬虫 API（新终端）
cd scrape-api
/Users/kxz/anaconda3/bin/python -m uvicorn app.main:app --reload --port 8000

# 3. 启动 .NET API（新终端）
cd src/JobIntel.Api
dotnet run --urls="http://localhost:5000"

# 4. 测试集成
curl http://localhost:5000/api/health
curl "http://localhost:5000/api/ingest/seek?keywords=plumber&location=Sydney&maxResults=5"
```

### 访问端点

- **Swagger UI:** http://localhost:5000/swagger
- **Health Check:** http://localhost:5000/api/health
- **Hangfire Dashboard:** http://localhost:5000/hangfire
- **Python API Docs:** http://localhost:8000/docs

### 前置要求
- .NET 8 SDK
- PostgreSQL 16
- Python 3.10+ (Anaconda)
- macOS/Linux（Windows 需调整命令）

## Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=jobintel;Username=admin;Password=dev123"
  },
  "ScrapeApi": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

## Key Features Implemented

### 1. Deduplication Logic
- **Fingerprint:** Unique identifier based on source, source_id, title, company, and location
- **Content Hash:** Detects changes in job description and requirements
- **Normalization:** Consistent string formatting for reliable hashing

### 2. Data Normalization
- Location parsing (e.g., "Adelaide, SA" → state=SA, suburb=Adelaide)
- Trade extraction from job titles
- Employment type normalization
- Salary range parsing
- Requirements extraction
- Tag generation (visa_sponsor, entry_level, etc.)
- HTML cleaning

### 3. Pipeline Processing
- Sequential processing: Normalize → Deduplicate → Store
- Three outcomes: New job, Updated job, Duplicate job
- Error handling with partial success support
- Detailed logging at each stage

### 4. Audit Trail
- Every scrape operation logged in `ingest_runs` table
- Statistics: jobs_found, jobs_new, jobs_updated, jobs_deduped
- Error tracking with stack traces
- Execution time tracking

### 5. Hangfire Integration
- Background job execution
- Retry logic on failures
- Web dashboard for monitoring
- Job scheduling capabilities (ready for recurring jobs)

## 📚 文档

### 新手指南
- **[启动指南](GETTING_STARTED.md)** - 完整的环境配置和启动步骤
- **[PostgreSQL 教程](docs/tutorials/PostgreSQL-Guide.md)** - 零基础 PostgreSQL 学习指南

### 核心文档
- **[V1 完成总结](docs/core/V1_COMPLETION_SUMMARY.md)** ⭐ - 项目概览和功能清单
- **[数据质量修复报告](docs/core/DATA_QUALITY_FIXES_2025-12-26.md)** 🆕 - P0/P1 问题修复详情
- **[.NET 集成完成报告](docs/core/DOTNET_INTEGRATION_COMPLETE.md)** - Python + .NET 集成测试
- **[查询 API 测试报告](docs/core/QUERY_API_TEST_RESULTS.md)** - 搜索功能验证

### 完整文档索引
- **[文档导航](docs/README.md)** - 所有文档的分类索引

## Next Steps (Not Implemented Yet)

The following are from the Technical Design Document but not part of Sprint 1.3:

- **Sprint 1.4:** Query API (JobsController, search filters, analytics)
- **Phase 2:** User authentication and saved jobs
- **Phase 3:** AI-powered semantic search with pgvector

## Technical Decisions

1. **Clean Architecture:** Dependencies flow inward (API → Infrastructure/Ingest → Core)
2. **Repository Pattern:** Abstraction over data access for testability
3. **Dependency Injection:** All services registered in Program.cs
4. **Entity Framework Core:** Type-safe database access with migrations
5. **Hangfire:** Reliable background job processing with PostgreSQL storage
6. **Snake_case Database:** Follows PostgreSQL conventions in column names

## Compliance with Technical Design Document

This implementation strictly follows:

- **Section 5.2:** Data model design for job_postings and ingest_runs tables
- **Section 5.3:** Deduplication strategy with fingerprint and content_hash
- **Section 6.2.3:** ScrapeJob workflow and error handling
- **Section 6.2.4:** IngestionPipeline stages (normalize → dedupe → store)
- **Development Guide Section 4.4:** Hangfire job pattern

All naming conventions, database schemas, and architectural patterns match the technical specifications.
