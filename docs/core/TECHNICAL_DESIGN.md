# Job Intelligence Platform - Technical Design Document

**Document Version:** 1.0  
**Last Updated:** December 14, 2024  
**Author:** Platform Engineering Team  
**Status:** Draft - Pending Review  
**Classification:** Internal

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-14 | Platform Team | Initial draft |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Background & Objectives](#2-project-background--objectives)
3. [System Architecture](#3-system-architecture)
4. [Technical Stack](#4-technical-stack)
5. [Data Model Design](#5-data-model-design)
6. [Component Design](#6-component-design)
7. [API Design](#7-api-design)
8. [Development Phases](#8-development-phases)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Security & Compliance](#10-security--compliance)
11. [Deployment Strategy](#11-deployment-strategy)
12. [Future Roadmap](#12-future-roadmap)

---

## 1. Executive Summary

### 1.1 Project Overview

**Job Intelligence Platform** is a data aggregation and analytics system designed to collect, normalize, and analyze job postings from multiple sources across the Australian construction trades sector. The platform provides real-time market intelligence through AI-powered analysis, enabling data-driven decision-making for job seekers and market researchers.

### 1.2 Business Value

- **Market Intelligence:** Real-time visibility into construction trade job market trends across Australian states
- **Time Efficiency:** Automated aggregation eliminates manual multi-platform searches
- **Data Quality:** Standardized, deduplicated job posting data with change tracking
- **AI-Powered Insights:** Natural language queries for complex market analysis
- **Extensibility:** Modular architecture supporting future commercial applications

### 1.3 Key Metrics (Target)

| Metric | Target (MVP) | Target (Phase 2) |
|--------|-------------|------------------|
| Data Sources | 2-3 platforms | 5+ platforms |
| Job Postings/Day | 100-500 | 1,000+ |
| Data Freshness | 24 hours | 6 hours |
| Query Response Time | < 500ms | < 200ms |
| AI Analysis Time | < 3s | < 1s |

---

## 2. Project Background & Objectives

### 2.1 Problem Statement

The Australian construction trades job market is fragmented across multiple platforms (SEEK, Indeed, Workforce Australia, Labour Hire agencies). Job seekers face several challenges:

1. **Data Fragmentation:** Manual searching across 5+ platforms
2. **Duplicate Listings:** Same job posted on multiple sites with different details
3. **Market Opacity:** Difficulty assessing regional demand, salary trends, or skill requirements
4. **Time Inefficiency:** 2-3 hours/day spent on manual job searches
5. **Lack of Analytics:** No tools for trend analysis or market intelligence

### 2.2 Target Users (Current Scope)

**Primary:** Individual job seekers in construction trades (bricklayers, tilers, plasterers, labourers)  
**Secondary (Future):** Recruitment agencies, market researchers, policy analysts

### 2.3 Project Objectives

#### Phase 1 (MVP - Weeks 1-2)
- Aggregate job postings from 2-3 sources
- Implement deduplication and data normalization
- Provide basic search/filter API
- Generate statistical insights (by state, trade, time)

#### Phase 2 (User Features - Weeks 3-4)
- User authentication system
- Saved searches and job bookmarking
- Email/notification alerts

#### Phase 3 (AI & Scale - Weeks 5-8)
- AI-powered semantic search (pgvector)
- Natural language query interface
- Trend prediction models
- Multi-source expansion (5+ platforms)

### 2.4 Success Criteria

**MVP Success:**
- [ ] Successfully scrape and normalize 100+ jobs/day
- [ ] < 5% duplicate rate after deduplication
- [ ] API response time < 500ms for filtered queries
- [ ] Basic analytics dashboard functional

**Production Readiness:**
- [ ] 99% uptime over 30 days
- [ ] Data freshness < 6 hours
- [ ] Support 100 concurrent API requests
- [ ] Zero data loss in scraping failures

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web UI     │  │  Mobile App  │  │  API Client  │          │
│  │  (Next.js)   │  │   (Future)   │  │   (Future)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    HTTPS/REST API
                             │
┌─────────────────────────────┼──────────────────────────────────┐
│                    Application Layer (.NET 8)                   │
│  ┌──────────────────────────┴──────────────────────────────┐   │
│  │              JobIntel.Api (Web API)                      │   │
│  │  ├─ Controllers (Jobs, Analytics, AI, Admin)            │   │
│  │  ├─ Middleware (Auth, Logging, Error Handling)          │   │
│  │  └─ Swagger/OpenAPI Documentation                       │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                       │
│  ┌──────────────────────┴───────────────────────────────────┐  │
│  │           JobIntel.Core (Domain Logic)                   │  │
│  │  ├─ Entities (JobPosting, IngestRun, User)              │  │
│  │  ├─ Interfaces (IJobRepository, IScrapeClient)          │  │
│  │  ├─ Services (DeduplicationService, AnalyticsService)   │  │
│  │  └─ DTOs (Request/Response Models)                      │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────┴───────────────────────────────────┐  │
│  │         JobIntel.Ingest (Background Jobs)                │  │
│  │  ├─ Hangfire Jobs (Scheduled Scraping)                  │  │
│  │  ├─ ScrapeApiClient (HTTP Client to Python API)         │  │
│  │  └─ IngestionPipeline (Normalize → Dedupe → Store)      │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────┴───────────────────────────────────┐  │
│  │      JobIntel.Infrastructure (Data Access)               │  │
│  │  ├─ DbContext (EF Core Configuration)                   │  │
│  │  ├─ Repositories (JobRepository, UserRepository)        │  │
│  │  ├─ Migrations (Database Schema Versioning)             │  │
│  │  └─ External Clients (AI APIs, Email Service)           │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL  │  │ Scrape API   │  │   AI APIs    │
│  + pgvector │  │  (Python)    │  │ (Claude/GPT) │
└─────────────┘  └──────────────┘  └──────────────┘
```

### 3.2 Component Interaction Flow

#### 3.2.1 Data Ingestion Flow
```
1. Hangfire Scheduler (Cron: every 6 hours)
   ↓
2. ScrapeJob.Execute()
   ↓
3. ScrapeApiClient.FetchJobsAsync(source, keywords, location)
   ├─→ HTTP POST to Python Scrape API
   └─→ Receives: List<RawJobData>
   ↓
4. IngestionPipeline.ProcessAsync(rawJobs)
   ├─→ Normalize: RawJobData → JobPosting entity
   ├─→ Deduplicate: Check fingerprint + content_hash
   ├─→ Generate embedding (if AI enabled)
   └─→ Persist: DbContext.SaveChangesAsync()
   ↓
5. Log results to IngestRun table
```

#### 3.2.2 Query Flow
```
1. Client → GET /api/jobs?trade=tiler&state=SA&posted_after=2024-12-01
   ↓
2. JobsController.SearchJobs(JobSearchRequest)
   ↓
3. JobRepository.SearchAsync(filters)
   ├─→ Build EF Core query with filters
   ├─→ Apply pagination (default: 20/page)
   └─→ Execute query (includes caching layer)
   ↓
4. Map entities → JobDto
   ↓
5. Return: PaginatedResponse<JobDto>
```

#### 3.2.3 AI Analysis Flow (Phase 3)
```
1. Client → POST /api/ai/analyze { query: "What are common requirements for Adelaide tilers?" }
   ↓
2. AIController.AnalyzeJobs(AIAnalysisRequest)
   ↓
3. Step 1: Filter jobs by structured criteria (SQL)
   ├─→ Location: Adelaide
   ├─→ Trade: tiler
   └─→ Date range: Last 30 days
   ↓
4. Step 2: Semantic search (pgvector)
   ├─→ Generate query embedding
   └─→ Cosine similarity search
   ↓
5. Step 3: Aggregate + Send to LLM
   ├─→ Context: Filtered job descriptions
   ├─→ Prompt: "Summarize common requirements..."
   └─→ LLM Response: Structured insights
   ↓
6. Return: AIAnalysisResponse
```

### 3.3 Architecture Principles

1. **Separation of Concerns:** Clean architecture with distinct layers (API, Core, Infrastructure)
2. **Dependency Inversion:** Depend on abstractions (interfaces), not concrete implementations
3. **Single Responsibility:** Each component has one clear purpose
4. **Open/Closed:** Open for extension (new data sources), closed for modification
5. **Fail-Safe:** Graceful degradation when external services fail

---

## 4. Technical Stack

### 4.1 Core Technologies

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Backend API** | ASP.NET Core Web API | 8.0 | Industry standard for enterprise .NET applications; excellent async/await support |
| **ORM** | Entity Framework Core | 8.0 | Type-safe database access; migration support; LINQ queries |
| **Database** | PostgreSQL | 16.x | ACID compliance; pgvector extension for AI features; robust indexing |
| **Vector Store** | pgvector | 0.5.x | Native PostgreSQL extension; eliminates separate vector DB overhead |
| **Job Scheduler** | Hangfire | 1.8.x | Persistent background jobs; built-in dashboard; retry logic |
| **Web Scraping** | Python FastAPI + Scrapy | 3.11/2.11 | Best-in-class scraping ecosystem; decoupled from main system |
| **HTML Parser** | AngleSharp | 1.1.x | C# native parser for simple scraping (fallback) |
| **API Docs** | Swagger/OpenAPI | 3.0 | Auto-generated documentation; interactive testing |
| **Logging** | Serilog | 3.x | Structured logging; multiple sinks (file, console, seq) |
| **Caching** | IMemoryCache / Redis | Built-in / 7.x | In-memory for MVP; Redis for production scale |
| **Testing** | xUnit + Moq | Latest | Standard .NET testing stack |

### 4.2 Development Tools

| Tool | Purpose |
|------|---------|
| **IDE** | Visual Studio 2022 / Rider |
| **Version Control** | Git + GitHub |
| **Database Client** | pgAdmin 4 / DBeaver |
| **API Testing** | Postman / Bruno |
| **Container** | Docker Desktop |
| **CI/CD** | GitHub Actions (future) |

### 4.3 External Services

| Service | Purpose | Phase |
|---------|---------|-------|
| **Scrape API** | Python-based web scraping service | MVP |
| **Claude API** | AI analysis and summarization | Phase 3 |
| **SendGrid** | Email notifications | Phase 2 |
| **Seq** | Centralized logging (optional) | Production |

### 4.4 Technology Decision Rationale

#### Why .NET over Node.js/Python?
- **Type Safety:** Compile-time error detection reduces runtime bugs
- **Performance:** Superior async I/O for high-concurrency API
- **Ecosystem:** Mature ORM (EF Core), background jobs (Hangfire), DI container
- **Career Alignment:** Australian .NET job market demand

#### Why PostgreSQL over MongoDB?
- **Structured Data:** Job postings have consistent schema
- **ACID Transactions:** Critical for deduplication logic
- **pgvector:** Native vector support without separate DB
- **SQL Expertise:** Strong querying and aggregation capabilities

#### Why Separate Python Scraping Service?
- **Best Tool for Job:** Scrapy ecosystem is unmatched for web scraping
- **Isolation:** Scraping failures don't crash main API
- **Flexibility:** Easy to swap scraping implementations
- **Resource Management:** Separate process boundaries

---

## 5. Data Model Design

### 5.1 Entity Relationship Diagram

```
┌─────────────────────────┐
│      job_postings       │
├─────────────────────────┤
│ id (PK)                 │
│ source                  │───┐
│ source_id               │   │
│ title                   │   │
│ company                 │   │
│ location_state          │   │
│ location_suburb         │   │
│ trade                   │   │
│ employment_type         │   │
│ pay_range_min           │   │
│ pay_range_max           │   │
│ description             │   │
│ requirements            │   │
│ tags (jsonb)            │   │
│ fingerprint (UNIQUE)    │   │
│ content_hash            │   │
│ embedding (vector)      │   │ Phase 3
│ posted_at               │   │
│ scraped_at              │   │
│ last_checked_at         │   │
│ is_active               │   │
│ created_at              │   │
│ updated_at              │   │
└─────────┬───────────────┘   │
          │                   │
          │ Many-to-One       │
          │                   │
          ▼                   │
┌─────────────────────────┐   │
│     ingest_runs         │   │
├─────────────────────────┤   │
│ id (PK)                 │◄──┘
│ source                  │
│ keywords                │
│ location                │
│ started_at              │
│ completed_at            │
│ status                  │ (pending/running/success/failed)
│ jobs_found              │
│ jobs_new                │
│ jobs_updated            │
│ jobs_deduped            │
│ error_message           │
│ error_stack_trace       │
│ metadata (jsonb)        │
└─────────────────────────┘

     Phase 2 Extensions:
     
┌─────────────────────────┐       ┌─────────────────────────┐
│        users            │       │    user_saved_jobs      │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │───┐   │ id (PK)                 │
│ email (UNIQUE)          │   │   │ user_id (FK)            │
│ password_hash           │   │   │ job_posting_id (FK)     │
│ created_at              │   │   │ saved_at                │
│ last_login_at           │   │   │ notes                   │
└─────────────────────────┘   │   └─────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────┐   │   ┌─────────────────────────┐
│     user_alerts         │   │   │    alert_executions     │
├─────────────────────────┤   │   ├─────────────────────────┤
│ id (PK)                 │◄──┘   │ id (PK)                 │
│ user_id (FK)            │───────│ alert_id (FK)           │
│ name                    │       │ executed_at             │
│ filters (jsonb)         │       │ jobs_matched            │
│ is_active               │       │ notification_sent       │
│ created_at              │       └─────────────────────────┘
└─────────────────────────┘
```

### 5.2 Core Tables

#### 5.2.1 `job_postings`

**Purpose:** Central repository for all scraped and normalized job postings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| `source` | VARCHAR(50) | NOT NULL, INDEX | Platform name (e.g., "seek", "indeed", "workforce_australia") |
| `source_id` | VARCHAR(255) | NOT NULL | External platform's job ID |
| `title` | VARCHAR(500) | NOT NULL, INDEX | Job title (e.g., "Bricklayer - Adelaide CBD") |
| `company` | VARCHAR(255) | NOT NULL, INDEX | Employer name |
| `location_state` | VARCHAR(50) | INDEX | Australian state code (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) |
| `location_suburb` | VARCHAR(100) | INDEX | City or suburb name |
| `trade` | VARCHAR(50) | INDEX | Normalized trade category (bricklayer, tiler, plasterer, labourer, etc.) |
| `employment_type` | VARCHAR(50) | | full-time, part-time, casual, contract, apprenticeship |
| `pay_range_min` | DECIMAL(10,2) | | Minimum hourly rate (AUD) |
| `pay_range_max` | DECIMAL(10,2) | | Maximum hourly rate (AUD) |
| `description` | TEXT | NOT NULL | Full job description (raw HTML stripped) |
| `requirements` | TEXT | | Skills/qualifications section (extracted if available) |
| `tags` | JSONB | | Array of tags (e.g., ["visa_sponsor", "entry_level"]) |
| `fingerprint` | VARCHAR(255) | UNIQUE, INDEX | Deduplication key: `SHA256(source:source_id:title:company:location)` |
| `content_hash` | VARCHAR(64) | INDEX | Hash of description+requirements to detect updates |
| `embedding` | VECTOR(1536) | | OpenAI/Claude embedding for semantic search (Phase 3) |
| `posted_at` | TIMESTAMP | INDEX | Original posting date from source platform |
| `scraped_at` | TIMESTAMP | NOT NULL | When this record was first created |
| `last_checked_at` | TIMESTAMP | | Last time we verified job is still active |
| `is_active` | BOOLEAN | DEFAULT TRUE, INDEX | Whether job is still available |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last modification timestamp |

**Indexes:**
```sql
CREATE INDEX idx_job_postings_source ON job_postings(source);
CREATE INDEX idx_job_postings_trade_state ON job_postings(trade, location_state);
CREATE INDEX idx_job_postings_posted_at ON job_postings(posted_at DESC);
CREATE INDEX idx_job_postings_active ON job_postings(is_active) WHERE is_active = true;
CREATE INDEX idx_job_postings_fingerprint_hash ON job_postings USING HASH(fingerprint);

-- Phase 3: Vector similarity search
CREATE INDEX idx_job_postings_embedding ON job_postings USING ivfflat (embedding vector_cosine_ops);
```

**Constraints:**
```sql
ALTER TABLE job_postings ADD CONSTRAINT uq_source_external_id UNIQUE (source, source_id);
ALTER TABLE job_postings ADD CONSTRAINT chk_pay_range CHECK (pay_range_min IS NULL OR pay_range_max IS NULL OR pay_range_min <= pay_range_max);
```

#### 5.2.2 `ingest_runs`

**Purpose:** Audit log for all scraping operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| `source` | VARCHAR(50) | NOT NULL | Data source (e.g., "seek", "indeed") |
| `keywords` | TEXT | | Comma-separated search keywords |
| `location` | VARCHAR(100) | | Location filter used |
| `started_at` | TIMESTAMP | NOT NULL | Job start time |
| `completed_at` | TIMESTAMP | | Job completion time (null if still running) |
| `status` | VARCHAR(20) | NOT NULL | pending, running, success, failed, partial_success |
| `jobs_found` | INTEGER | DEFAULT 0 | Total jobs returned by source |
| `jobs_new` | INTEGER | DEFAULT 0 | New jobs added to database |
| `jobs_updated` | INTEGER | DEFAULT 0 | Existing jobs with content changes |
| `jobs_deduped` | INTEGER | DEFAULT 0 | Duplicate jobs skipped |
| `error_message` | TEXT | | Error summary if failed |
| `error_stack_trace` | TEXT | | Full exception details |
| `metadata` | JSONB | | Additional context (API version, proxy used, etc.) |

**Indexes:**
```sql
CREATE INDEX idx_ingest_runs_source_started ON ingest_runs(source, started_at DESC);
CREATE INDEX idx_ingest_runs_status ON ingest_runs(status);
```

### 5.3 Deduplication Strategy

#### 5.3.1 Fingerprint Generation

**Purpose:** Identify the same job posted across multiple sources or re-posted over time.

**Algorithm:**
```csharp
public static string GenerateFingerprint(JobPosting job)
{
    var components = new[]
    {
        job.Source.ToLowerInvariant(),
        job.SourceId,
        NormalizeString(job.Title),
        NormalizeString(job.Company),
        job.LocationState?.ToUpperInvariant() ?? "",
        job.LocationSuburb?.ToLowerInvariant() ?? ""
    };
    
    var combined = string.Join(":", components);
    return ComputeSHA256Hash(combined);
}

private static string NormalizeString(string input)
{
    if (string.IsNullOrWhiteSpace(input)) return "";
    
    // Remove special characters, extra spaces, normalize case
    return Regex.Replace(input.ToLowerInvariant(), @"[^a-z0-9\s]", "")
                .Trim()
                .Replace("  ", " ");
}
```

**Edge Cases Handled:**
- Same job on multiple platforms (e.g., SEEK + Indeed) → Different fingerprints (by design, we track both)
- Re-posted job with changed description → Same fingerprint, updated `content_hash`
- Typos in company name → Normalized before hashing

#### 5.3.2 Content Change Detection

**Purpose:** Detect when job description is updated (e.g., salary change, new requirements).

**Algorithm:**
```csharp
public static string GenerateContentHash(string description, string requirements)
{
    var normalized = NormalizeString(description) + "|" + NormalizeString(requirements ?? "");
    return ComputeSHA256Hash(normalized);
}
```

**Workflow:**
```
1. New job arrives → Calculate fingerprint
2. Check if fingerprint exists in DB
   ├─ NO → Insert new record
   └─ YES → Calculate content_hash
       ├─ Hash matches → Skip (no changes)
       └─ Hash differs → Update record, increment `jobs_updated`
```

### 5.4 Data Retention Policy

| Data Type | Retention Period | Rationale |
|-----------|-----------------|-----------|
| Active job postings | Until marked inactive | Core data |
| Inactive job postings | 90 days | Trend analysis, training data |
| Ingest run logs | 30 days (success) / 90 days (failures) | Debugging, monitoring |
| User data | Until account deletion | Compliance |

---

## 6. Component Design

### 6.1 .NET Solution Structure

```
JobIntel/
│
├── JobIntel.sln
│
├── src/
│   ├── JobIntel.Api/                      # Web API Layer
│   │   ├── Controllers/
│   │   │   ├── JobsController.cs          # Job search, details, stats
│   │   │   ├── AnalyticsController.cs     # Trends, heatmaps
│   │   │   ├── AdminController.cs         # Scrape triggers, health
│   │   │   └── AIController.cs            # AI analysis (Phase 3)
│   │   ├── Middleware/
│   │   │   ├── ErrorHandlingMiddleware.cs
│   │   │   └── RequestLoggingMiddleware.cs
│   │   ├── Program.cs                     # Application startup
│   │   ├── appsettings.json
│   │   └── JobIntel.Api.csproj
│   │
│   ├── JobIntel.Core/                     # Domain Layer
│   │   ├── Entities/
│   │   │   ├── JobPosting.cs
│   │   │   ├── IngestRun.cs
│   │   │   ├── User.cs                    # Phase 2
│   │   │   └── UserAlert.cs               # Phase 2
│   │   ├── Interfaces/
│   │   │   ├── IJobRepository.cs
│   │   │   ├── IIngestRunRepository.cs
│   │   │   ├── IScrapeApiClient.cs
│   │   │   ├── IDeduplicationService.cs
│   │   │   └── IAnalyticsService.cs
│   │   ├── DTOs/
│   │   │   ├── Requests/
│   │   │   │   ├── JobSearchRequest.cs
│   │   │   │   └── ScrapeJobRequest.cs
│   │   │   └── Responses/
│   │   │       ├── JobDto.cs
│   │   │       ├── PaginatedResponse.cs
│   │   │       └── StatsDto.cs
│   │   ├── Enums/
│   │   │   ├── JobSource.cs
│   │   │   ├── AustralianState.cs
│   │   │   └── IngestRunStatus.cs
│   │   └── JobIntel.Core.csproj
│   │
│   ├── JobIntel.Ingest/                   # Background Jobs
│   │   ├── Jobs/
│   │   │   ├── ScrapeJob.cs               # Hangfire job
│   │   │   └── CleanupJob.cs              # Data retention
│   │   ├── Services/
│   │   │   ├── ScrapeApiClient.cs         # HTTP client for Python API
│   │   │   ├── IngestionPipeline.cs       # Normalize → Dedupe → Store
│   │   │   └── DeduplicationService.cs
│   │   └── JobIntel.Ingest.csproj
│   │
│   └── JobIntel.Infrastructure/           # Data Access Layer
│       ├── Data/
│       │   ├── JobIntelDbContext.cs
│       │   ├── Configurations/
│       │   │   ├── JobPostingConfiguration.cs
│       │   │   └── IngestRunConfiguration.cs
│       │   └── Migrations/
│       ├── Repositories/
│       │   ├── JobRepository.cs
│       │   └── IngestRunRepository.cs
│       ├── External/
│       │   ├── ClaudeApiClient.cs         # Phase 3
│       │   └── EmailService.cs            # Phase 2
│       └── JobIntel.Infrastructure.csproj
│
├── tests/
│   ├── JobIntel.Api.Tests/
│   ├── JobIntel.Core.Tests/
│   └── JobIntel.Ingest.Tests/
│
└── scrape-api/                            # Python Scraping Service
    ├── adapters/
    │   ├── base.py
    │   ├── seek_adapter.py
    │   └── workforce_australia_adapter.py
    ├── models/
    │   └── job_dto.py
    ├── main.py                            # FastAPI app
    ├── requirements.txt
    └── Dockerfile
```

### 6.2 Key Components

#### 6.2.1 JobsController (API Layer)

**Responsibilities:**
- Handle HTTP requests for job-related operations
- Input validation and authorization
- Map domain entities to DTOs
- Return standardized responses

**Key Endpoints:**
```csharp
[ApiController]
[Route("api/[controller]")]
public class JobsController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<PaginatedResponse<JobDto>>> SearchJobs(
        [FromQuery] JobSearchRequest request);
    
    [HttpGet("{id}")]
    public async Task<ActionResult<JobDto>> GetJobDetail(int id);
    
    [HttpGet("stats")]
    public async Task<ActionResult<StatsDto>> GetStatistics(
        [FromQuery] StatsRequest request);
}
```

#### 6.2.2 IJobRepository (Core Layer)

**Interface:**
```csharp
public interface IJobRepository
{
    Task<PaginatedResult<JobPosting>> SearchAsync(
        JobSearchCriteria criteria, 
        int page, 
        int pageSize);
    
    Task<JobPosting?> GetByIdAsync(int id);
    
    Task<JobPosting?> GetByFingerprintAsync(string fingerprint);
    
    Task<int> InsertAsync(JobPosting job);
    
    Task UpdateAsync(JobPosting job);
    
    Task<Dictionary<string, int>> GetCountByTradeAsync(DateTime? since = null);
    
    Task<Dictionary<string, int>> GetCountByStateAsync(DateTime? since = null);
}
```

#### 6.2.3 ScrapeJob (Ingest Layer)

**Purpose:** Hangfire background job that orchestrates scraping operations.

**Workflow:**
```csharp
public class ScrapeJob
{
    public async Task Execute(string source, string[] keywords, string? location)
    {
        var run = await CreateIngestRun(source, keywords, location);
        
        try
        {
            run.Status = IngestRunStatus.Running;
            await _runRepository.UpdateAsync(run);
            
            // Step 1: Call Python Scrape API
            var rawJobs = await _scrapeClient.FetchJobsAsync(source, keywords, location);
            run.JobsFound = rawJobs.Count;
            
            // Step 2: Process through pipeline
            var results = await _pipeline.ProcessAsync(rawJobs);
            run.JobsNew = results.NewCount;
            run.JobsUpdated = results.UpdatedCount;
            run.JobsDeduped = results.DedupedCount;
            
            run.Status = IngestRunStatus.Success;
        }
        catch (Exception ex)
        {
            run.Status = IngestRunStatus.Failed;
            run.ErrorMessage = ex.Message;
            run.ErrorStackTrace = ex.StackTrace;
        }
        finally
        {
            run.CompletedAt = DateTime.UtcNow;
            await _runRepository.UpdateAsync(run);
        }
    }
}
```

#### 6.2.4 IngestionPipeline (Ingest Layer)

**Stages:**
1. **Normalize:** Convert RawJobData → JobPosting entity
2. **Deduplicate:** Check fingerprint against DB
3. **Enrich:** Extract tags, normalize trade/location
4. **Persist:** Insert or update in database

```csharp
public class IngestionPipeline
{
    public async Task<IngestionResult> ProcessAsync(List<RawJobData> rawJobs)
    {
        var result = new IngestionResult();
        
        foreach (var raw in rawJobs)
        {
            // 1. Normalize
            var job = await _normalizer.NormalizeAsync(raw);
            
            // 2. Deduplicate
            var existing = await _jobRepo.GetByFingerprintAsync(job.Fingerprint);
            
            if (existing == null)
            {
                // New job
                await _jobRepo.InsertAsync(job);
                result.NewCount++;
            }
            else if (existing.ContentHash != job.ContentHash)
            {
                // Content updated
                existing.Description = job.Description;
                existing.ContentHash = job.ContentHash;
                existing.UpdatedAt = DateTime.UtcNow;
                await _jobRepo.UpdateAsync(existing);
                result.UpdatedCount++;
            }
            else
            {
                // Duplicate, skip
                result.DedupedCount++;
            }
        }
        
        return result;
    }
}
```

### 6.3 Python Scrape API

**Technology:** FastAPI + Scrapy  
**Deployment:** Standalone Docker container

**Endpoints:**
```python
POST /scrape/jobs
Request:
{
  "source": "seek" | "indeed" | "workforce_australia",
  "keywords": ["bricklayer", "tiler"],
  "location": "Adelaide",
  "max_results": 100
}

Response:
{
  "jobs": [
    {
      "source_id": "12345",
      "title": "Bricklayer - Adelaide CBD",
      "company": "ABC Construction",
      "location": "Adelaide, SA",
      "description": "...",
      "posted_at": "2024-12-10T08:00:00Z",
      "url": "https://seek.com.au/job/12345"
    }
  ],
  "total": 50,
  "scraped_at": "2024-12-14T10:30:00Z"
}
```

---

## 7. API Design

### 7.1 RESTful Endpoints

#### Base URL
```
Development: http://localhost:5000/api
Production:  https://api.jobintel.com/api
```

#### 7.1.1 Job Search & Retrieval

**Search Jobs**
```http
GET /jobs
Query Parameters:
  - trade: string (optional) - bricklayer, tiler, plasterer, etc.
  - state: string (optional) - NSW, VIC, QLD, SA, WA, TAS, NT, ACT
  - suburb: string (optional) - City or suburb name
  - posted_after: datetime (optional) - Filter by posting date
  - pay_min: decimal (optional) - Minimum hourly rate
  - pay_max: decimal (optional) - Maximum hourly rate
  - employment_type: string (optional) - full-time, part-time, casual, etc.
  - tags: string[] (optional) - visa_sponsor, entry_level, etc.
  - page: int (default: 1)
  - page_size: int (default: 20, max: 100)
  - sort_by: string (default: posted_at_desc) - posted_at_asc, posted_at_desc, pay_desc

Response 200:
{
  "data": [
    {
      "id": 12345,
      "title": "Bricklayer - Adelaide CBD",
      "company": "ABC Construction",
      "location": {
        "state": "SA",
        "suburb": "Adelaide"
      },
      "trade": "bricklayer",
      "employment_type": "full-time",
      "pay_range": {
        "min": 35.00,
        "max": 45.00,
        "currency": "AUD",
        "unit": "hour"
      },
      "description": "We are seeking...",
      "tags": ["visa_sponsor", "experienced"],
      "posted_at": "2024-12-10T08:00:00Z",
      "source": {
        "name": "seek",
        "url": "https://seek.com.au/job/12345"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 250,
    "total_pages": 13
  }
}
```

**Get Job Detail**
```http
GET /jobs/{id}

Response 200:
{
  "id": 12345,
  "title": "Bricklayer - Adelaide CBD",
  "company": "ABC Construction",
  ... (all fields from search, plus)
  "requirements": "- Certificate III in Bricklaying\n- 2+ years experience",
  "scraped_at": "2024-12-14T10:30:00Z",
  "last_checked_at": "2024-12-14T10:30:00Z",
  "is_active": true
}

Response 404: Job not found
```

#### 7.1.2 Analytics & Statistics

**Get Overall Statistics**
```http
GET /analytics/stats
Query Parameters:
  - since: datetime (optional) - Filter data from this date
  - trade: string (optional) - Filter by specific trade

Response 200:
{
  "total_jobs": 5432,
  "active_jobs": 4210,
  "jobs_added_today": 87,
  "by_trade": {
    "bricklayer": 1200,
    "tiler": 1850,
    "plasterer": 980,
    "labourer": 1402
  },
  "by_state": {
    "NSW": 1500,
    "VIC": 1200,
    "QLD": 1100,
    "SA": 650,
    "WA": 800,
    "TAS": 82,
    "NT": 50,
    "ACT": 50
  },
  "avg_pay_rate": {
    "min": 28.50,
    "max": 42.30,
    "median": 35.00
  }
}
```

**Get Trends**
```http
GET /analytics/trends
Query Parameters:
  - trade: string (required)
  - state: string (optional)
  - days: int (default: 30) - Number of days to analyze

Response 200:
{
  "trade": "tiler",
  "state": "SA",
  "period": {
    "start": "2024-11-14",
    "end": "2024-12-14"
  },
  "daily_counts": [
    { "date": "2024-11-14", "count": 12 },
    { "date": "2024-11-15", "count": 15 },
    ...
  ],
  "trend": "increasing", // increasing, decreasing, stable
  "change_percent": 25.5
}
```

#### 7.1.3 Admin Operations

**Trigger Manual Scrape**
```http
POST /admin/scrape
Authorization: Bearer {admin_token}
Request:
{
  "source": "seek",
  "keywords": ["bricklayer", "tiler"],
  "location": "Adelaide",
  "max_results": 100
}

Response 202: Accepted
{
  "run_id": 789,
  "status": "pending",
  "message": "Scraping job queued"
}
```

**Get Scrape History**
```http
GET /admin/runs
Query Parameters:
  - source: string (optional)
  - status: string (optional) - pending, running, success, failed
  - page: int
  - page_size: int

Response 200:
{
  "data": [
    {
      "id": 789,
      "source": "seek",
      "keywords": "bricklayer, tiler",
      "started_at": "2024-12-14T10:00:00Z",
      "completed_at": "2024-12-14T10:05:23Z",
      "status": "success",
      "stats": {
        "jobs_found": 120,
        "jobs_new": 15,
        "jobs_updated": 8,
        "jobs_deduped": 97
      }
    }
  ],
  ...
}
```

### 7.2 Error Response Format

**Standard Error Structure:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid state code: XYZ",
    "details": {
      "field": "state",
      "allowed_values": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
    },
    "timestamp": "2024-12-14T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**HTTP Status Codes:**
- 200: Success
- 201: Created (e.g., new scrape job)
- 202: Accepted (async operation queued)
- 400: Bad Request (validation error)
- 401: Unauthorized (Phase 2)
- 403: Forbidden (Phase 2)
- 404: Not Found
- 429: Too Many Requests (rate limiting)
- 500: Internal Server Error
- 503: Service Unavailable (scrape API down)

### 7.3 Rate Limiting (Production)

| Tier | Limit | Window |
|------|-------|--------|
| Anonymous | 100 requests | 15 minutes |
| Authenticated | 1000 requests | 15 minutes |
| Admin | Unlimited | - |

---

## 8. Development Phases

### 8.1 Phase 1: MVP - Data Foundation (Weeks 1-2)

**Goal:** Prove technical feasibility and core value proposition.

#### Sprint 1.1 (Week 1, Days 1-3): Infrastructure Setup ✅ 完成
- [x] Initialize .NET 8 solution structure
- [x] Set up PostgreSQL database (local Docker)
- [x] Configure EF Core with migrations
- [x] Implement `JobPosting` and `IngestRun` entities
- [x] Set up Hangfire dashboard
- [ ] Create Python FastAPI scaffold 🔖 待实施

**Deliverable:** Running .NET API with Swagger, empty database with schema. ✅

#### Sprint 1.2 (Week 1, Days 4-5): Scrape API (Python) 🔖 调研完成，待实施
- [x] 调研 JobSpy 开源项目（Indeed 等多平台）✅
- [x] 调研 SeekSpider 开源项目（SEEK 专用）✅
- [x] 设计融合方案（JobSpy 架构 + SEEK 插件）✅
- [x] SEEK API 分析（官方 vs 内部 API）✅
- [ ] Implement Indeed adapter (基于 JobSpy)
- [ ] Implement SEEK adapter (基于 SeekSpider 改造)
- [ ] Create `/scrape/jobs` endpoint
- [ ] Containerize with Docker

**Deliverable:** Python API that returns structured job data. 🔖

**参考文档:**
- [爬虫调研分析](docs/SCRAPER_RESEARCH_ANALYSIS.md)
- [融合方案设计](docs/SCRAPER_FUSION_ANALYSIS.md)
- [SEEK API 对比](docs/SEEK_API_COMPARISON.md)

#### Sprint 1.3 (Week 2, Days 1-3): Ingestion Pipeline ✅ 完成 (2025-12-14)
- [x] Implement `ScrapeApiClient` in .NET
- [x] Build `IngestionPipeline` (normalize → dedupe → store)
- [x] Implement deduplication logic
- [x] Create Hangfire `ScrapeJob`
- [x] Schedule daily scrapes (test with short interval)

**Deliverable:** Automated scraping that populates database. ✅

#### Sprint 1.4 (Week 2, Days 4-5): Query API ✅ 完成 (2025-12-16)
- [x] Implement `JobRepository` with search filters
- [x] Create `JobsController` endpoints (search, detail, stats)
- [x] Create `AnalyticsController` endpoints
- [x] Add basic analytics (count by trade/state)
- [x] V2 预留字段（SavedCount, ViewCount）
- [ ] Write unit tests for core logic 🔖 待实施

**Deliverable:** Functional REST API with basic analytics. ✅

**Phase 1 Success Criteria:**
- [ ] 100+ jobs in database from 2 sources 🔖 等待爬虫实施
- [ ] < 5% duplicate rate 🔖 等待爬虫实施
- [x] API responds in < 500ms ✅
- [ ] Manual testing confirms accuracy 🔖 等待爬虫实施

---

### 8.2 Phase 2: User Features (Weeks 3-4)

**Goal:** Enable personalized experience for job seekers.

#### Sprint 2.1 (Week 3, Days 1-2): Authentication
- [ ] Add `users` table and entity
- [ ] Implement JWT authentication
- [ ] Create registration/login endpoints
- [ ] Add `[Authorize]` attributes to protected endpoints

#### Sprint 2.2 (Week 3, Days 3-5): Saved Jobs
- [ ] Add `user_saved_jobs` table
- [ ] Implement save/unsave endpoints
- [ ] Create "My Saved Jobs" query
- [ ] Add notes field for saved jobs

#### Sprint 2.3 (Week 4, Days 1-3): Alerts System
- [ ] Add `user_alerts` and `alert_executions` tables
- [ ] Implement alert creation/management endpoints
- [ ] Create Hangfire job to check alerts
- [ ] Integrate email service (SendGrid)

#### Sprint 2.4 (Week 4, Days 4-5): Frontend (Optional)
- [ ] Basic Next.js dashboard
- [ ] Login/registration UI
- [ ] Job search interface
- [ ] Saved jobs page

**Phase 2 Success Criteria:**
- [ ] Users can register and log in
- [ ] Save/unsave jobs
- [ ] Create alerts and receive emails
- [ ] 99% email delivery rate

---

### 8.3 Phase 3: AI & Scale (Weeks 5-8)

**Goal:** Intelligent insights and production readiness.

#### Sprint 3.1 (Week 5): Vector Search
- [ ] Enable pgvector extension
- [ ] Generate embeddings for all jobs (Claude/OpenAI)
- [ ] Add embedding generation to ingestion pipeline
- [ ] Implement semantic search endpoint

#### Sprint 3.2 (Week 6): AI Analysis
- [ ] Create `AIController` with analysis endpoint
- [ ] Implement RAG pipeline (filter → retrieve → summarize)
- [ ] Add natural language query interface
- [ ] Create prompt templates for common queries

#### Sprint 3.3 (Week 7): Scale & Performance
- [ ] Add Redis caching layer
- [ ] Optimize database queries (EXPLAIN ANALYZE)
- [ ] Implement rate limiting
- [ ] Add comprehensive logging (Serilog → Seq)

#### Sprint 3.4 (Week 8): Production Deployment
- [ ] Set up Azure/AWS infrastructure
- [ ] Configure CI/CD pipeline (GitHub Actions)
- [ ] Deploy PostgreSQL (managed service)
- [ ] Deploy .NET API + Python Scrape API
- [ ] Set up monitoring (Application Insights)

**Phase 3 Success Criteria:**
- [ ] Semantic search returns relevant results
- [ ] AI analysis completes in < 3 seconds
- [ ] API handles 100 concurrent requests
- [ ] 99.9% uptime over 7 days

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Metric | Target (MVP) | Target (Production) |
|--------|-------------|---------------------|
| API Response Time (p95) | < 500ms | < 200ms |
| API Response Time (p99) | < 1s | < 500ms |
| Database Query Time | < 100ms | < 50ms |
| Scraping Throughput | 50 jobs/min | 200 jobs/min |
| Concurrent Users | 10 | 100 |
| Data Freshness | 24 hours | 6 hours |

### 9.2 Reliability

| Metric | Target |
|--------|--------|
| API Uptime | 99.5% (MVP), 99.9% (Production) |
| Scraping Success Rate | > 95% |
| Database Backup Frequency | Daily (automated) |
| Recovery Time Objective (RTO) | 4 hours |
| Recovery Point Objective (RPO) | 1 hour |

### 9.3 Scalability

**Vertical Scaling (MVP):**
- Single server with 2 CPU / 4GB RAM
- PostgreSQL on same server or managed service
- Handles ~1000 jobs/day, 100 API requests/hour

**Horizontal Scaling (Future):**
- Stateless API (multiple instances behind load balancer)
- Separate scraping workers (queue-based distribution)
- Read replicas for PostgreSQL
- Redis cluster for caching

### 9.4 Maintainability

- **Code Coverage:** > 80% for core business logic
- **Documentation:** All public APIs documented with XML comments
- **Logging:** Structured logs (JSON) with correlation IDs
- **Monitoring:** Health check endpoints for all services
- **Versioning:** API versioning from day 1 (e.g., `/api/v1/jobs`)

---

## 10. Security & Compliance

### 10.1 Security Measures

#### Authentication & Authorization (Phase 2)
- **JWT Tokens:** Short-lived (15 min) access tokens, long-lived (7 day) refresh tokens
- **Password Security:** BCrypt hashing with salt
- **HTTPS Only:** TLS 1.2+ enforced
- **CORS Policy:** Whitelist allowed origins

#### Data Protection
- **Encryption at Rest:** Database encryption (PostgreSQL TDE)
- **Encryption in Transit:** HTTPS/TLS for all API calls
- **Secrets Management:** Azure Key Vault / AWS Secrets Manager
- **API Keys:** Never logged or exposed in error messages

#### Input Validation
- **SQL Injection:** Parameterized queries (EF Core)
- **XSS Prevention:** Output encoding
- **CSRF Protection:** Anti-forgery tokens (future web UI)
- **Rate Limiting:** Per-IP and per-user limits

### 10.2 Compliance

#### Data Privacy
- **User Data:** Minimal collection (email, password hash only)
- **Job Data:** Public information only (no PII)
- **Right to Deletion:** User account deletion includes all related data
- **Data Retention:** See Section 5.4

#### Legal Considerations
- **Web Scraping:** Compliance with robots.txt and Terms of Service
- **Fair Use:** Data used for personal/research purposes (MVP)
- **Commercial Use:** Legal review required before monetization

---

## 11. Deployment Strategy

### 11.1 MVP Deployment (Local/Docker)

**Option 1: Local Development**
```bash
# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev -v pgdata:/var/lib/postgresql/data postgres:16

# .NET API
cd src/JobIntel.Api
dotnet run

# Python Scrape API
cd scrape-api
uvicorn main:app --reload
```

**Option 2: Docker Compose**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  scrape-api:
    build: ./scrape-api
    ports:
      - "8000:8000"
    depends_on:
      - postgres
  
  api:
    build: ./src/JobIntel.Api
    ports:
      - "5000:8080"
    environment:
      ConnectionStrings__Default: "Host=postgres;Database=jobintel;..."
      ScrapeApi__BaseUrl: "http://scrape-api:8000"
    depends_on:
      - postgres
      - scrape-api

volumes:
  pgdata:
```

### 11.2 Production Deployment (Azure)

**Architecture:**
```
Internet
   │
   ├─→ Azure Front Door (CDN + WAF)
   │      │
   │      ├─→ App Service (API) - Region 1
   │      └─→ App Service (API) - Region 2 (future)
   │
   ├─→ Container Instance (Scrape API)
   │
   └─→ Azure Database for PostgreSQL (Flexible Server)
        ├─ pgvector extension enabled
        └─ Automated backups
```

**Services:**
- **Compute:** Azure App Service (Linux, .NET 8)
- **Database:** Azure Database for PostgreSQL Flexible Server
- **Scraping:** Azure Container Instances (Python FastAPI)
- **Caching:** Azure Cache for Redis (Phase 3)
- **Secrets:** Azure Key Vault
- **Monitoring:** Application Insights
- **Logging:** Azure Log Analytics
- **CI/CD:** GitHub Actions

**Estimated Costs (USD/month):**
- App Service (B1): $13
- PostgreSQL (Burstable B1ms): $12
- Container Instances: $10
- Storage: $5
- **Total:** ~$40/month (MVP)

---

## 12. Future Roadmap

### 12.1 Phase 4: Advanced Analytics (Months 3-4)

- **Salary Prediction:** ML model to predict pay ranges based on job attributes
- **Skill Extraction:** NLP to identify required skills and certifications
- **Company Insights:** Aggregate data about employers (hiring frequency, average pay)
- **Market Reports:** Weekly/monthly reports on trade demand trends
- **Custom Dashboards:** User-defined widgets and charts

### 12.2 Phase 5: Collaboration Features (Months 5-6)

- **Shared Job Lists:** Users can share curated job collections
- **Community Reviews:** Employer ratings and reviews
- **Application Tracking:** Track where you've applied
- **Interview Prep:** AI-generated interview questions based on job description

### 12.3 Phase 6: Commercial Features (Months 7-12)

- **B2B API:** Paid API access for recruitment agencies
- **White-Label:** Customizable platform for labour hire companies
- **Premium Tier:** Advanced analytics, priority support
- **Mobile Apps:** iOS and Android native apps

### 12.4 Technical Debt & Improvements

- **Microservices:** Extract scraping, AI, and analytics into separate services
- **Event Sourcing:** Implement CQRS for better audit trails
- **Real-Time Updates:** WebSocket notifications for new jobs
- **Multi-Language:** Expand beyond Australian market
- **Advanced Deduplication:** ML-based fuzzy matching

---

## Appendices

### A. Glossary

| Term | Definition |
|------|------------|
| **Trade** | Specific construction occupation (e.g., bricklayer, tiler) |
| **Fingerprint** | Unique hash identifying a job posting |
| **Content Hash** | Hash of job description to detect changes |
| **Deduplication** | Process of identifying and removing duplicate jobs |
| **Ingestion** | Process of fetching, normalizing, and storing job data |
| **pgvector** | PostgreSQL extension for vector similarity search |
| **RAG** | Retrieval-Augmented Generation (AI technique) |
| **Semantic Search** | Search based on meaning, not just keywords |

### B. References

- [ASP.NET Core Documentation](https://docs.microsoft.com/en-us/aspnet/core/)
- [Entity Framework Core](https://docs.microsoft.com/en-us/ef/core/)
- [Hangfire Documentation](https://docs.hangfire.io/)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### C. Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2024-12-14 | 1.0 | Platform Team | Initial draft for review |

---

**Document Status:** Draft - Pending Technical Review  
**Next Review Date:** 2024-12-21  
**Approvers:** Engineering Lead, Product Manager, Security Team

---

*End of Document*
