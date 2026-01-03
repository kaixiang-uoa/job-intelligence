# Project Files Overview

## Complete File Structure

```
job-intelligence/
│
├── JobIntel.sln                                    # Solution file
├── README.md                                       # Main documentation
├── QUICK_START.md                                  # Quick start guide
├── PROJECT_FILES.md                                # This file
│
├── files/                                          # Technical documentation
│   ├── JOB_INTELLIGENCE_TECHNICAL_DESIGN.md
│   └── JOB_INTELLIGENCE_DEVELOPMENT_GUIDE.md
│
└── src/
    │
    ├── JobIntel.Api/                              # ⭐ Web API Project
    │   ├── Program.cs                             # Application entry point (175 lines)
    │   ├── appsettings.json                       # Configuration
    │   └── JobIntel.Api.csproj                    # Project file
    │
    ├── JobIntel.Core/                             # ⭐ Domain Layer (Zero Dependencies)
    │   ├── Entities/
    │   │   ├── JobPosting.cs                      # Main job entity (47 lines)
    │   │   └── IngestRun.cs                       # Audit log entity (47 lines)
    │   │
    │   ├── DTOs/
    │   │   ├── RawJobData.cs                      # Python API response (24 lines)
    │   │   └── IngestionResult.cs                 # Pipeline result (15 lines)
    │   │
    │   ├── Interfaces/
    │   │   ├── IScrapeApiClient.cs                # Scrape API contract (23 lines)
    │   │   ├── IIngestionPipeline.cs              # Pipeline contract (20 lines)
    │   │   ├── IDeduplicationService.cs           # Deduplication contract (32 lines)
    │   │   ├── IJobRepository.cs                  # Job repository contract (21 lines)
    │   │   └── IIngestRunRepository.cs            # Ingest run repository contract (17 lines)
    │   │
    │   └── JobIntel.Core.csproj
    │
    ├── JobIntel.Infrastructure/                   # ⭐ Data Access Layer
    │   ├── Data/
    │   │   ├── JobIntelDbContext.cs               # EF Core context (20 lines)
    │   │   │
    │   │   └── Configurations/
    │   │       ├── JobPostingConfiguration.cs     # Job table config (128 lines)
    │   │       └── IngestRunConfiguration.cs      # Ingest run table config (70 lines)
    │   │
    │   ├── Repositories/
    │   │   ├── JobRepository.cs                   # Job CRUD operations (67 lines)
    │   │   └── IngestRunRepository.cs             # Ingest run operations (60 lines)
    │   │
    │   └── JobIntel.Infrastructure.csproj
    │       └── Dependencies:
    │           - Npgsql.EntityFrameworkCore.PostgreSQL 8.0.0
    │           - Microsoft.EntityFrameworkCore.Design 8.0.0
    │           - Hangfire.AspNetCore 1.8.0
    │           - Hangfire.PostgreSql 1.20.0
    │
    ├── JobIntel.Ingest/                           # ⭐ Background Jobs Layer
    │   ├── Jobs/
    │   │   └── ScrapeJob.cs                       # Hangfire job (108 lines)
    │   │
    │   ├── Services/
    │   │   ├── ScrapeApiClient.cs                 # HTTP client for Python API (107 lines)
    │   │   ├── IngestionPipeline.cs               # Main pipeline logic (316 lines)
    │   │   └── DeduplicationService.cs            # Fingerprint/hash generator (83 lines)
    │   │
    │   └── JobIntel.Ingest.csproj
    │
    └── JobIntel.Api/                              # ⭐ Sprint 1.4 新增 (2025-12-16)
        ├── Controllers/
        │   ├── BaseApiController.cs               # V2 认证就绪的基类
        │   ├── JobsController.cs                  # 2个端点：搜索、详情
        │   └── AnalyticsController.cs             # 3个端点：统计分析
        │
        └── (DTOs 添加到 JobIntel.Core)

## Sprint 1.4 新增文件详细清单 (2025-12-16)

### JobIntel.Core/DTOs/

#### Requests (请求 DTOs)
```
src/JobIntel.Core/DTOs/Requests/
└── JobSearchRequest.cs                            # 搜索请求（带验证）
```

#### Responses (响应 DTOs)
```
src/JobIntel.Core/DTOs/Responses/
├── JobDto.cs                                      # 职位详情 DTO
├── LocationDto.cs                                 # 地点嵌套 DTO
├── PayRangeDto.cs                                 # 薪资范围嵌套 DTO
├── JobSourceDto.cs                                # 数据源嵌套 DTO
├── PaginatedResponse.cs                           # 分页响应泛型
├── PaginationMeta.cs                              # 分页元数据
├── StatsDto.cs                                    # 统计数据 DTO
└── AvgPayRateDto.cs                               # 平均薪资嵌套 DTO
```

#### Internal (内部 DTOs)
```
src/JobIntel.Core/DTOs/Internal/
├── JobSearchCriteria.cs                           # 内部搜索条件
└── PaginatedResult.cs                             # 内部分页结果
```

### JobIntel.Core/Extensions/
```
src/JobIntel.Core/Extensions/
└── JobPostingExtensions.cs                        # Entity → DTO 映射扩展
```

### Repository 扩展
```
src/JobIntel.Core/Interfaces/
└── IJobRepository.cs                              # 新增 5 个方法签名
    - SearchAsync()
    - GetCountByTradeAsync()
    - GetCountByStateAsync()
    - GetTotalActiveJobsAsync()
    - GetJobsAddedTodayAsync()

src/JobIntel.Infrastructure/Repositories/
└── JobRepository.cs                               # 实现上述 5 个方法
```

## 爬虫调研文件夹 (2025-12-16)

```
scrape-api-research/
├── JobSpy/                                        # Indeed 等多平台爬虫
│   ├── jobspy/
│   │   ├── __init__.py                           # 主入口 scrape_jobs()
│   │   ├── model.py                              # Pydantic 数据模型
│   │   ├── indeed/                               # Indeed 爬虫实现
│   │   ├── linkedin/
│   │   ├── glassdoor/
│   │   └── ziprecruiter/
│   ├── pyproject.toml                            # Poetry 依赖
│   └── README.md
│
└── SeekSpider/                                    # SEEK 专用爬虫
    ├── SeekSpider/
    │   ├── spiders/
    │   │   └── seek.py                           # 主爬虫逻辑
    │   ├── items.py                              # 数据模型
    │   ├── pipelines.py                          # PostgreSQL 管道
    │   └── core/                                 # 核心组件
    ├── requirements.txt                          # Python 依赖
    └── README.md
```

## 文档结构 (2025-12-26 更新)

```
docs/
├── README.md                                      # 📚 文档索引
├── MVP_V1_COMPLETION.md                           # 🎉 V1 最终完成报告
├── DOCUMENTATION_CLEANUP_2025-12-26.md            # 文档整理报告
├── core/                                          # 核心文档
│   ├── TECHNICAL_DESIGN.md                        # 技术设计文档
│   ├── DEVELOPMENT_GUIDE.md                       # 开发指南
│   ├── V1_COMPLETION_SUMMARY.md                   # V1 完成总结
│   ├── DATA_QUALITY_FIXES_2025-12-26.md          # 数据质量修复
│   └── ... (6 个其他核心文档)
├── design/                                        # 设计文档（归档）
│   ├── SCRAPER_RESEARCH_ANALYSIS.md              # 爬虫调研分析
│   ├── SCRAPER_FUSION_ANALYSIS.md                # 融合方案
│   ├── SEEK_API_COMPARISON.md                    # API 对比
│   └── ... (其他设计文档)
├── development/                                   # 开发过程（归档）
└── tutorials/                                     # 教程
    ├── PostgreSQL-Guide.md
    ├── SEEK_ADAPTER_DESIGN_GUIDE.md
    └── OPTIMIZATION_PRIORITIES_GUIDE.md
```

## File Statistics (Updated 2025-12-16)

### Sprint 1.3 完成 (Day 1 - 2025-12-14)

| Project | Files | Lines |
|---------|-------|-------|
| **JobIntel.Core** | 9 | ~250 |
| **JobIntel.Infrastructure** | 5 | ~345 |
| **JobIntel.Ingest** | 4 | ~614 |
| **JobIntel.Api** | 2 | ~175 |
| **Total (Sprint 1.3)** | **20** | **~1,384** |

### Sprint 1.4 新增 (Day 2 - 2025-12-16)

| 类型 | Files | Lines |
|------|-------|-------|
| **Controllers** | 3 | ~200 |
| **DTOs** | 12 | ~350 |
| **Extensions** | 1 | ~50 |
| **Total (Sprint 1.4)** | **16** | **~600** |

### 爬虫调研 (Day 2 - 2025-12-16)

| 类型 | Files |
|------|-------|
| **开源项目** | 2 (JobSpy, SeekSpider) |
| **调研文档** | 3 |

### 总计

| 阶段 | Files | Lines |
|------|-------|-------|
| **C# 代码** | 36 | ~1,984 |
| **文档** | 14 | - |
| **克隆项目** | 2 | - |

## Key Files Explained

### Domain Layer (JobIntel.Core)

#### Entities
- **[JobPosting.cs](src/JobIntel.Core/Entities/JobPosting.cs)** - Central job posting entity with 25+ properties including deduplication fields (fingerprint, content_hash)
- **[IngestRun.cs](src/JobIntel.Core/Entities/IngestRun.cs)** - Audit trail for scraping operations with statistics and error tracking

#### DTOs
- **[RawJobData.cs](src/JobIntel.Core/DTOs/RawJobData.cs)** - Raw data received from Python Scrape API
- **[IngestionResult.cs](src/JobIntel.Core/DTOs/IngestionResult.cs)** - Result of pipeline processing with counts

#### Interfaces
All service contracts with zero implementation dependencies

### Infrastructure Layer (JobIntel.Infrastructure)

#### Database
- **[JobIntelDbContext.cs](src/JobIntel.Infrastructure/Data/JobIntelDbContext.cs)** - EF Core context with auto-discovery of configurations

#### Configurations
- **[JobPostingConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/JobPostingConfiguration.cs)**
  - Complete table schema: job_postings
  - 7 indexes (source, trade+state, posted_at, active, fingerprint, content_hash)
  - Unique constraint on source + source_id
  - All column names in snake_case

- **[IngestRunConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/IngestRunConfiguration.cs)**
  - Audit table schema: ingest_runs
  - 2 indexes (source+started_at, status)
  - Enum to string conversion

#### Repositories
- **[JobRepository.cs](src/JobIntel.Infrastructure/Repositories/JobRepository.cs)**
  - GetByIdAsync, GetByFingerprintAsync, InsertAsync, UpdateAsync, GetCountAsync
  - Uses AsNoTracking() for read operations

- **[IngestRunRepository.cs](src/JobIntel.Infrastructure/Repositories/IngestRunRepository.cs)**
  - CreateAsync, UpdateAsync, GetByIdAsync, GetRecentAsync
  - Tracks all scrape operations

### Ingest Layer (JobIntel.Ingest)

#### Background Jobs
- **[ScrapeJob.cs](src/JobIntel.Ingest/Jobs/ScrapeJob.cs)**
  - Hangfire job following Development Guide pattern
  - Workflow: CreateRun → Fetch → Process → UpdateRun
  - Full error handling with stack trace capture

#### Services
- **[ScrapeApiClient.cs](src/JobIntel.Ingest/Services/ScrapeApiClient.cs)**
  - HTTP client for Python Scrape API
  - POST /scrape/jobs with retry logic
  - JSON serialization with snake_case

- **[IngestionPipeline.cs](src/JobIntel.Ingest/Services/IngestionPipeline.cs)** ⭐ **LARGEST FILE**
  - 13 helper methods for data normalization:
    - Location parsing (Adelaide, SA → state=SA, suburb=Adelaide)
    - Trade extraction (8 trade categories with keywords)
    - Employment type normalization
    - Salary range parsing with regex
    - Requirements extraction
    - Tag generation (4 tag types)
    - HTML cleaning
  - Three-stage pipeline: Normalize → Deduplicate → Store
  - Handles new, updated, and duplicate jobs differently

- **[DeduplicationService.cs](src/JobIntel.Ingest/Services/DeduplicationService.cs)**
  - Fingerprint: SHA256(source:source_id:normalized_title:normalized_company:state:suburb)
  - Content Hash: SHA256(normalized_description|normalized_requirements)
  - String normalization: lowercase, remove special chars, collapse spaces

### API Layer (JobIntel.Api)

- **[Program.cs](src/JobIntel.Api/Program.cs)**
  - Complete application configuration
  - Database setup (EF Core + PostgreSQL)
  - Hangfire setup (PostgreSQL storage)
  - Dependency injection (6 scoped services)
  - HTTP client configuration
  - 3 endpoints: health, admin/scrape, hangfire dashboard

- **[appsettings.json](src/JobIntel.Api/appsettings.json)**
  - Connection string
  - Scrape API URL
  - Logging configuration

## Dependencies Graph

```
JobIntel.Api
  ├─→ JobIntel.Core
  ├─→ JobIntel.Infrastructure
  └─→ JobIntel.Ingest

JobIntel.Ingest
  ├─→ JobIntel.Core
  └─→ JobIntel.Infrastructure

JobIntel.Infrastructure
  └─→ JobIntel.Core

JobIntel.Core
  └─→ (no dependencies)
```

## NuGet Packages

### JobIntel.Api
- Swashbuckle.AspNetCore 6.5.0
- Hangfire.AspNetCore 1.8.0
- Hangfire.PostgreSql 1.20.0

### JobIntel.Infrastructure
- Npgsql.EntityFrameworkCore.PostgreSQL 8.0.0
- Microsoft.EntityFrameworkCore.Design 8.0.0
- Hangfire.AspNetCore 1.8.0
- Hangfire.PostgreSql 1.20.0

### JobIntel.Ingest
- (inherits from Infrastructure and Core)

### JobIntel.Core
- (zero external dependencies)

## Database Schema

### job_postings (25 columns)
- Primary: id, source, source_id, title, company
- Location: location_state, location_suburb
- Classification: trade, employment_type
- Compensation: pay_range_min, pay_range_max
- Content: description, requirements, tags
- Deduplication: fingerprint (UNIQUE), content_hash
- Metadata: posted_at, scraped_at, last_checked_at, is_active
- Audit: created_at, updated_at

### ingest_runs (13 columns)
- Primary: id, source
- Search params: keywords, location
- Execution: started_at, completed_at, status
- Statistics: jobs_found, jobs_new, jobs_updated, jobs_deduped
- Errors: error_message, error_stack_trace
- Metadata: metadata (JSON)

### Hangfire tables
- hangfire.job
- hangfire.state
- hangfire.counter
- hangfire.server
- ... (9 tables total, auto-created)

## Compliance with Technical Design Document

| Section | Specification | Implementation |
|---------|--------------|----------------|
| **5.2.1** | job_postings table schema | ✅ [JobPostingConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/JobPostingConfiguration.cs) |
| **5.2.2** | ingest_runs table schema | ✅ [IngestRunConfiguration.cs](src/JobIntel.Infrastructure/Data/Configurations/IngestRunConfiguration.cs) |
| **5.3.1** | Fingerprint algorithm | ✅ [DeduplicationService.cs:23](src/JobIntel.Ingest/Services/DeduplicationService.cs#L23) |
| **5.3.2** | Content hash algorithm | ✅ [DeduplicationService.cs:38](src/JobIntel.Ingest/Services/DeduplicationService.cs#L38) |
| **6.2.3** | ScrapeJob workflow | ✅ [ScrapeJob.cs:31](src/JobIntel.Ingest/Jobs/ScrapeJob.cs#L31) |
| **6.2.4** | IngestionPipeline stages | ✅ [IngestionPipeline.cs:29](src/JobIntel.Ingest/Services/IngestionPipeline.cs#L29) |
| **Dev Guide 4.4** | Hangfire job pattern | ✅ [ScrapeJob.cs](src/JobIntel.Ingest/Jobs/ScrapeJob.cs) |

All naming conventions, database column names (snake_case), and architectural patterns match the specification exactly.

---

## Python 爬虫服务文件清单

> **添加时间:** 2025-12-18 (阶段 1 骨架)
> **最后更新:** 2025-12-19 (阶段 2 Indeed 适配器)

### scrape-api/ (31 files)

```
scrape-api/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI 应用入口 ✅
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py              # 可扩展适配器基类 ⭐
│   │   ├── indeed_adapter.py            # Indeed 适配器 ✅
│   │   └── seek_adapter.py              # SEEK 适配器 ✅ NEW (Day 5)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                  # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_posting_dto.py           # 统一数据模型
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── location_parser.py           # 地点解析工具 ✅
│       ├── trade_extractor.py           # Trade 提取工具 ✅
│       ├── employment_type.py           # 工作类型标准化 ✅
│       ├── salary_parser.py             # 薪资解析工具 ✅ NEW (Day 5)
│       └── html_cleaner.py              # HTML 清理工具 ✅ NEW (Day 5)
├── tests/
│   ├── test_location_parser.py          # 地点解析测试（6 用例）✅
│   ├── test_trade_extractor.py          # Trade 提取测试（16 用例）✅
│   ├── test_employment_type.py          # 工作类型测试（14 用例）✅
│   ├── test_salary_parser.py            # 薪资解析测试（17 用例）✅ NEW (Day 5)
│   └── test_html_cleaner.py             # HTML 清理测试（16 用例）✅ NEW (Day 5)
├── requirements.txt                      # Python 依赖
├── .env                                  # 环境变量
├── .env.example                          # 环境变量示例
├── .gitignore
├── run.sh                                # 启动脚本
├── verify_setup.py                       # 设置验证脚本
├── test_indeed_manual.py                 # Indeed 手动测试脚本 ✅
├── test_seek_manual.py                   # SEEK 手动测试脚本 ✅ NEW (Day 5)
├── debug_seek_response.py                # SEEK API 调试脚本 ✅ NEW (Day 5)
└── README.md                             # 项目说明
```

### 核心文件说明

#### app/adapters/base_adapter.py (120 行)
**用途:** 可扩展的适配器基类

**核心类:**
- `BaseJobAdapter` - 抽象基类，所有平台适配器继承此类
  - `scrape()` - 抓取方法（子类必须实现）
  - `platform_name` - 平台名称（子类必须实现）
  - `validate_request()` - 请求验证
  - `_generate_id()` - ID 生成工具
- `ScraperException` - 爬虫异常基类
- `RateLimitException` - 速率限制异常
- `PlatformException` - 平台错误异常

**可扩展性:**
```python
# 添加新平台只需 3 步：
class LinkedInAdapter(BaseJobAdapter):
    @property
    def platform_name(self) -> str:
        return "linkedin"

    def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        # 实现逻辑
        pass
```

#### app/models/job_posting_dto.py (250 行)
**用途:** 统一的数据模型

**核心类:**
- `PlatformEnum` - 平台枚举（可扩展）
  - `INDEED = "indeed"`
  - `SEEK = "seek"`
  - 🔖 未来: LINKEDIN, GLASSDOOR, GOOGLE_JOBS
- `JobPostingDTO` - 标准化职位数据（18 字段）
  - 对应 .NET JobPosting 实体
  - Pydantic 数据验证
- `ScrapeRequest` - 爬取请求参数
- `ScrapeResponse` - 爬取响应格式
- `HealthResponse` - 健康检查响应

#### app/config/settings.py (70 行)
**用途:** 配置管理

**配置项:**
- FastAPI 配置（host, port, debug）
- Indeed 配置（国家、结果数、延迟）
- SEEK 配置（API URL、站点密钥、延迟）
- User-Agent 配置
- 日志配置

**技术:** pydantic-settings，自动从 .env 加载

#### app/main.py (230 行)
**用途:** FastAPI 应用入口

**端点:**
- `GET /` - API 根路径
- `GET /health` - 健康检查 ✅
- `POST /scrape/indeed` - Indeed 爬虫 ✅ (已实现)
- `POST /scrape/seek` - SEEK 爬虫 🔖

**功能:**
- CORS 中间件
- 全局异常处理
- 结构化日志（Loguru）
- 应用生命周期事件

#### app/adapters/indeed_adapter.py (170 行) ✅ NEW
**用途:** Indeed 平台适配器

**核心类:**
- `IndeedAdapter` - 继承 BaseJobAdapter
  - `scrape()` - 调用 JobSpy 抓取数据
  - `_transform_job()` - DataFrame → JobPostingDTO

**数据转换:**
- 使用 `parse_location()` 解析地点
- 使用 `extract_trade()` 提取 trade
- 使用 `normalize_employment_type()` 标准化类型
- 处理薪资、时间戳、URL 等字段

**错误处理:**
- `ScraperException` 异常
- Loguru 日志记录
- 转换失败降级处理

#### app/utils/location_parser.py (54 行) ✅ NEW
**用途:** 地点解析工具

**函数:**
- `parse_location(location_str)` → `(state, suburb)`
  - 解析 "Adelaide, SA" → ("SA", "Adelaide")
  - 处理边界情况（空值、无效格式）
  - 6 个单元测试

#### app/utils/trade_extractor.py (70 行) ✅ NEW
**用途:** Trade 类型提取

**函数:**
- `extract_trade(title)` → `trade_name`
  - 从职位标题识别 trade 类型
  - 支持 13 种 trade（tiler, plumber, electrician 等）
  - 关键词匹配 + 变体识别
  - 16 个单元测试

**Trade 类型:**
- tiler, plumber, electrician, bricklayer, carpenter
- painter, roofer, welder, glazier, plasterer
- concreter, stonemason, scaffolder

#### app/utils/employment_type.py (80 行) ✅ NEW
**用途:** 工作类型标准化

**函数:**
- `normalize_employment_type(employment_type)` → `标准格式`
  - "fulltime" → "Full Time"
  - "part-time" → "Part Time"
  - 支持多种变体（ft, pt, full-time 等）
  - 14 个单元测试

#### tests/test_location_parser.py ✅ NEW
**测试覆盖:**
- 6 个测试用例
- 基本解析、带空格、空输入、无效格式、None、多逗号

#### tests/test_trade_extractor.py ✅ NEW
**测试覆盖:**
- 16 个测试用例
- 13 种 trade 识别、变体匹配、边界情况

#### tests/test_employment_type.py ✅ NEW
**测试覆盖:**
- 14 个测试用例
- 标准化映射、大小写处理、空值处理

#### test_indeed_manual.py ✅ NEW
**用途:** 手动测试脚本

**功能:**
- 测试 IndeedAdapter 直接调用
- 测试 FastAPI 健康检查
- 输出详细的测试结果和样例数据

#### requirements.txt (22 dependencies)
**核心依赖:**
- `fastapi==0.115.5`
- `uvicorn==0.32.1`
- `pydantic==2.10.3`
- `python-jobspy==1.1.82` - Indeed 等多平台爬虫
- `requests==2.32.3`
- `beautifulsoup4==4.12.3`
- `loguru==0.7.3`
- `pytest==8.3.4` - 测试框架

### TDD 相关文档（3 个）

#### TDD_DEVELOPMENT_GUIDE.md (700+ 行)
**用途:** TDD 方法论完整指南

**内容:**
- TDD 核心概念（Red-Green-Refactor）
- 完整示例（薪资解析、计算器）
- 跨语言对比（Python, C#, JavaScript, Go）
- 实战技巧和常见误区
- pytest 工具使用

#### TDD_IMPLEMENTATION_CHECKLIST.md (350+ 行)
**用途:** 阶段 2 开发的逐步检查清单

**内容:**
- Phase 2.1: 工具函数（TDD）
  - parse_location() 步骤
  - extract_trade() 步骤
  - normalize_employment_type() 步骤
- Phase 2.2: Indeed 适配器
- Phase 2.3: FastAPI 集成
- 完成标准检查

#### SCRAPER_IMPLEMENTATION_PLAN.md (更新)
**新增内容:**
- 渐进式 TDD 策略章节
- TDD 实施顺序
- 为什么选择渐进式 TDD

### 爬虫研究文档（4 个）

#### SCRAPER_RESEARCH_ANALYSIS.md
**内容:** JobSpy 和 SeekSpider 深度分析

#### SCRAPER_FUSION_ANALYSIS.md
**内容:** 融合方案设计

#### SEEK_API_COMPARISON.md
**内容:** SEEK 官方 vs 内部 API 对比

#### SCRAPER_DATA_FIELDS_ANALYSIS.md
**内容:** 数据字段映射方案

---

## 文档清理记录

> **清理时间:** 2025-12-18

### 删除的文档（2 个）
- ❌ `DOCUMENTATION_AUDIT.md` - 过时的临时审查报告
- ❌ `DOCUMENTATION_UPDATE_SUMMARY.md` - 过时的临时总结

### 更新的文档（3 个）
- ✅ `NEXT_STEPS.md` - 更新当前进度（Day 3 完成）
- ✅ `DAILY_PLAN.md` - 添加 Day 3 总结，Day 4 计划
- ✅ `PROJECT_FILES.md` - 添加 scrape-api/ 文件清单（本节）

### 当前文档总数
- **根目录:** 2 个
- **docs/ 文件夹:** 17 个
- **总计:** 19 个文档

---

## Phase 2 新增文件总结 (Day 4)

> **新增时间:** 2025-12-19

### 新增代码文件（7 个）
1. ✅ `app/adapters/indeed_adapter.py` - Indeed 适配器（170 行）
2. ✅ `app/utils/location_parser.py` - 地点解析（54 行）
3. ✅ `app/utils/trade_extractor.py` - Trade 提取（70 行）
4. ✅ `app/utils/employment_type.py` - 工作类型标准化（80 行）
5. ✅ `tests/test_location_parser.py` - 地点解析测试（6 用例）
6. ✅ `tests/test_trade_extractor.py` - Trade 提取测试（16 用例）
7. ✅ `tests/test_employment_type.py` - 工作类型测试（14 用例）

### 新增测试脚本（1 个）
8. ✅ `test_indeed_manual.py` - 手动测试脚本

### 更新文件（1 个）
9. ✅ `app/main.py` - 更新 /scrape/indeed 端点

### 测试统计
- **单元测试:** 36 个（6 + 16 + 14）
- **通过率:** 100% ✅
- **测试覆盖:** 工具函数完整覆盖

---

## Phase 3 新增文件总结 (Day 5)

> **新增时间:** 2025-12-20

### 新增代码文件（5 个）
1. ✅ `app/adapters/seek_adapter.py` - SEEK 适配器（~300 行）
   - 继承 BaseJobAdapter
   - SEEK REST API 集成
   - 4 个私有方法：_build_params, _call_seek_api, _extract_description, _transform_job

2. ✅ `app/utils/salary_parser.py` - 薪资解析（~140 行）
   - 支持 8+ 种格式（基本范围、K 后缀、单值、时薪、特殊格式）
   - 时薪转年薪（38小时/周 × 52周）
   - 完整类型注解和文档字符串

3. ✅ `app/utils/html_cleaner.py` - HTML 清理（~72 行）
   - BeautifulSoup 解析 HTML
   - 移除 script/style 标签
   - 处理 HTML 实体（&nbsp;, &lt;, &gt;, &quot;）
   - 规范化空白字符

4. ✅ `tests/test_salary_parser.py` - 薪资解析测试（17 用例）
   - 基本范围、K 后缀、单值、时薪
   - 特殊格式（Up to, From）
   - 边界情况（空值、None、无效格式）

5. ✅ `tests/test_html_cleaner.py` - HTML 清理测试（16 用例）
   - 基本标签移除、HTML 实体
   - script/style 标签处理
   - 复杂 HTML、列表、嵌套标签
   - 边界情况

### 新增测试脚本（2 个）
6. ✅ `test_seek_manual.py` - SEEK 手动测试脚本
7. ✅ `debug_seek_response.py` - SEEK API 响应调试脚本

### 新增教学文档（1 个）
8. ✅ `files/tutorials/SEEK_ADAPTER_DESIGN_GUIDE.md` - SEEK 适配器设计教学
   - 完整架构设计（架构图、设计原则）
   - SEEK API 研究（端点、Headers、Payload、响应结构）
   - SeekAdapter 类设计（方法职责、数据转换流程）
   - HTTP 请求处理、错误处理策略
   - 完整字段映射表和示例
   - 开发步骤建议、学习要点、思考题

### 更新文件（1 个）
9. ✅ `app/main.py` - 更新 /scrape/seek 端点（使用 SeekAdapter）

### 测试统计
- **新增单元测试:** 33 个（17 + 16）
- **总单元测试:** 69 个（36 + 33）
- **通过率:** 100% ✅
- **测试覆盖:** 所有工具函数完整覆盖

### 核心能力
- ✅ 两个数据源适配器（Indeed + SEEK）
- ✅ 5 个工具函数（地点、trade、类型、薪资、HTML）
- ✅ 3 个 API 端点（health, indeed, seek）
- ✅ 统一数据模型（JobPostingDTO）
- ✅ 可扩展架构（BaseJobAdapter 模式）

---

**最后更新:** 2025-12-20
