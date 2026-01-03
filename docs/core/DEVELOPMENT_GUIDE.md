# Job Intelligence Platform - Development Guide

**Document Version:** 1.0  
**Last Updated:** December 14, 2024  
**Audience:** Development Team  
**Prerequisite:** Read Technical Design Document first

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Project Structure Deep Dive](#3-project-structure-deep-dive)
4. [Core Implementation Patterns](#4-core-implementation-patterns)
5. [Database Operations](#5-database-operations)
6. [API Development Guidelines](#6-api-development-guidelines)
7. [Testing Strategy](#7-testing-strategy)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Quick Start

### 1.1 Prerequisites Checklist

- [ ] .NET 8 SDK installed (`dotnet --version` should show 8.0.x)
- [ ] Docker Desktop running
- [ ] PostgreSQL 16 accessible (via Docker or local)
- [ ] Python 3.11+ (for scrape API)
- [ ] Git configured
- [ ] IDE: Visual Studio 2022 / Rider / VS Code

### 1.2 Initial Setup (15 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-org/job-intelligence.git
cd job-intelligence

# 2. Start PostgreSQL (Docker)
docker run -d \
  --name jobintel-postgres \
  -e POSTGRES_DB=jobintel \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=dev123 \
  -p 5432:5432 \
  postgres:16

# 3. Restore .NET dependencies
cd src/JobIntel.Api
dotnet restore

# 4. Run database migrations
dotnet ef database update --project ../JobIntel.Infrastructure

# 5. Start API
dotnet run
# Navigate to: http://localhost:5000/swagger

# 6. (Optional) Start Python Scrape API
cd ../../scrape-api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 1.3 Verify Installation

```bash
# Test .NET API health
curl http://localhost:5000/api/health

# Test database connection
dotnet ef dbcontext info --project src/JobIntel.Infrastructure

# Test Swagger UI
open http://localhost:5000/swagger
```

---

## 2. Development Environment Setup

### 2.1 IDE Configuration

#### Visual Studio 2022 / Rider

**Recommended Extensions:**
- CodeMaid (code cleanup)
- SonarLint (code quality)
- GitLens (git integration)
- Thunder Client (API testing)

**Settings:**
```json
{
  "editor.formatOnSave": true,
  "csharp.format.enable": true,
  "omnisharp.enableRoslynAnalyzers": true,
  "dotnet-test-explorer.testProjectPath": "**/*Tests.csproj"
}
```

**Recommended .editorconfig** (already in repo):
```ini
root = true

[*.cs]
indent_style = space
indent_size = 4
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# Naming conventions
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.severity = warning
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.symbols = interface
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.style = begins_with_i
```

#### VS Code

**Required Extensions:**
- C# Dev Kit
- C# Extensions
- REST Client
- GitLens

### 2.2 Database Tools

**Recommended:**
- **pgAdmin 4** (GUI): https://www.pgadmin.org/download/
- **DBeaver** (cross-platform): https://dbeaver.io/download/
- **Azure Data Studio** (Microsoft): https://aka.ms/azuredatastudio

**Connection Details (local development):**
```
Host: localhost
Port: 5432
Database: jobintel
Username: admin
Password: dev123
```

### 2.3 API Testing Tools

**Postman Collection:**
Import `postman/JobIntel.postman_collection.json` (included in repo)

**Alternative: REST Client (VS Code)**
See `api-tests/requests.http` for examples:
```http
### Get all jobs
GET http://localhost:5000/api/jobs
Content-Type: application/json

### Search with filters
GET http://localhost:5000/api/jobs?trade=tiler&state=SA
```

### 2.4 Git Workflow

**Branch Naming Convention:**
```
feature/JIRA-123-add-user-alerts
bugfix/JIRA-456-fix-deduplication
hotfix/critical-scraping-failure
```

**Commit Message Format:**
```
[JIRA-123] Add user alerts functionality

- Implement UserAlert entity
- Create alert management endpoints
- Add Hangfire job for alert checking
```

**Pull Request Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex logic
- [ ] Unit tests added/updated
- [ ] API documentation updated
- [ ] No new warnings
```

---

## 3. Project Structure Deep Dive

### 3.1 Solution Organization

```
JobIntel/
├── JobIntel.sln                          # Main solution file
├── .editorconfig                         # Code style rules
├── .gitignore
├── README.md
├── docker-compose.yml                    # Local development stack
│
├── src/                                  # Source code
│   ├── JobIntel.Api/                     # ⭐ Main API project
│   ├── JobIntel.Core/                    # ⭐ Domain logic
│   ├── JobIntel.Ingest/                  # ⭐ Background jobs
│   └── JobIntel.Infrastructure/          # ⭐ Data access
│
├── tests/                                # Test projects
│   ├── JobIntel.Api.Tests/
│   ├── JobIntel.Core.Tests/
│   └── JobIntel.Ingest.Tests/
│
├── scrape-api/                           # Python scraping service
│   ├── adapters/
│   ├── models/
│   ├── main.py
│   └── requirements.txt
│
└── docs/                                 # Documentation
    ├── api/                              # API specs
    ├── architecture/                     # Diagrams
    └── deployment/                       # Deployment guides
```

### 3.2 Dependency Graph

```
JobIntel.Api
    ├─→ JobIntel.Core (domain)
    ├─→ JobIntel.Ingest (background jobs)
    └─→ JobIntel.Infrastructure (data access)

JobIntel.Ingest
    ├─→ JobIntel.Core
    └─→ JobIntel.Infrastructure

JobIntel.Infrastructure
    └─→ JobIntel.Core

JobIntel.Core
    └─→ (no dependencies - pure domain logic)
```

**Key Principle:** Dependencies flow inward. Core has no external dependencies.

### 3.3 Key Files Explained

| File | Purpose | When to Modify |
|------|---------|----------------|
| `Program.cs` | Application startup, DI configuration | Adding new services, middleware |
| `appsettings.json` | Configuration (connection strings, API keys) | Environment-specific settings |
| `JobIntelDbContext.cs` | EF Core database context | Adding new entities |
| `*Configuration.cs` | Entity configurations (fluent API) | Changing table schemas |
| `*Controller.cs` | HTTP request handlers | Adding new API endpoints |
| `*Repository.cs` | Database access layer | Adding new queries |
| `*Service.cs` | Business logic | Adding new features |

---

## 4. Core Implementation Patterns

### 4.1 Entity Creation Pattern

**Step-by-Step:**

1. **Define Entity** (`JobIntel.Core/Entities/`)
```csharp
namespace JobIntel.Core.Entities;

public class JobPosting
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
    // ... other properties
    
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
```

2. **Create Configuration** (`JobIntel.Infrastructure/Data/Configurations/`)
```csharp
public class JobPostingConfiguration : IEntityTypeConfiguration<JobPosting>
{
    public void Configure(EntityTypeBuilder<JobPosting> builder)
    {
        builder.ToTable("job_postings");
        
        builder.HasKey(x => x.Id);
        
        builder.Property(x => x.Title)
            .HasMaxLength(500)
            .IsRequired();
        
        builder.HasIndex(x => x.Fingerprint)
            .IsUnique();
        
        builder.HasIndex(x => new { x.Trade, x.LocationState });
    }
}
```

3. **Add to DbContext** (`JobIntel.Infrastructure/Data/JobIntelDbContext.cs`)
```csharp
public class JobIntelDbContext : DbContext
{
    public DbSet<JobPosting> JobPostings => Set<JobPosting>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfiguration(new JobPostingConfiguration());
    }
}
```

4. **Generate Migration**
```bash
cd src/JobIntel.Infrastructure
dotnet ef migrations add AddJobPostings --startup-project ../JobIntel.Api
dotnet ef database update --startup-project ../JobIntel.Api
```

### 4.2 Repository Pattern

**Interface** (`JobIntel.Core/Interfaces/IJobRepository.cs`)
```csharp
public interface IJobRepository
{
    Task<JobPosting?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<JobPosting?> GetByFingerprintAsync(string fingerprint, CancellationToken ct = default);
    Task<PaginatedResult<JobPosting>> SearchAsync(JobSearchCriteria criteria, int page, int pageSize, CancellationToken ct = default);
    Task<int> InsertAsync(JobPosting job, CancellationToken ct = default);
    Task UpdateAsync(JobPosting job, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}
```

**Implementation** (`JobIntel.Infrastructure/Repositories/JobRepository.cs`)
```csharp
public class JobRepository : IJobRepository
{
    private readonly JobIntelDbContext _context;
    private readonly ILogger<JobRepository> _logger;
    
    public JobRepository(JobIntelDbContext context, ILogger<JobRepository> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    public async Task<JobPosting?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        return await _context.JobPostings
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id, ct);
    }
    
    public async Task<PaginatedResult<JobPosting>> SearchAsync(
        JobSearchCriteria criteria, 
        int page, 
        int pageSize, 
        CancellationToken ct = default)
    {
        var query = _context.JobPostings.AsNoTracking();
        
        // Apply filters
        if (!string.IsNullOrEmpty(criteria.Trade))
            query = query.Where(x => x.Trade == criteria.Trade);
        
        if (!string.IsNullOrEmpty(criteria.State))
            query = query.Where(x => x.LocationState == criteria.State);
        
        if (criteria.PostedAfter.HasValue)
            query = query.Where(x => x.PostedAt >= criteria.PostedAfter.Value);
        
        if (criteria.PayMin.HasValue)
            query = query.Where(x => x.PayRangeMin >= criteria.PayMin.Value);
        
        // Count total
        var total = await query.CountAsync(ct);
        
        // Apply pagination and sorting
        var items = await query
            .OrderByDescending(x => x.PostedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(ct);
        
        return new PaginatedResult<JobPosting>
        {
            Items = items,
            TotalCount = total,
            Page = page,
            PageSize = pageSize
        };
    }
    
    // ... other methods
}
```

**Registration** (`Program.cs`)
```csharp
builder.Services.AddScoped<IJobRepository, JobRepository>();
```

### 4.3 Controller Pattern

```csharp
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class JobsController : ControllerBase
{
    private readonly IJobRepository _jobRepo;
    private readonly IMapper _mapper;
    private readonly ILogger<JobsController> _logger;
    
    public JobsController(
        IJobRepository jobRepo, 
        IMapper mapper, 
        ILogger<JobsController> logger)
    {
        _jobRepo = jobRepo;
        _mapper = mapper;
        _logger = logger;
    }
    
    /// <summary>
    /// Search job postings with filters
    /// </summary>
    /// <param name="request">Search criteria</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>Paginated list of jobs</returns>
    [HttpGet]
    [ProducesResponseType(typeof(PaginatedResponse<JobDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> SearchJobs(
        [FromQuery] JobSearchRequest request, 
        CancellationToken ct)
    {
        // Validate
        if (request.Page < 1)
            return BadRequest(new ErrorResponse("Page must be >= 1"));
        
        if (request.PageSize > 100)
            return BadRequest(new ErrorResponse("PageSize cannot exceed 100"));
        
        // Map to criteria
        var criteria = _mapper.Map<JobSearchCriteria>(request);
        
        // Query
        var result = await _jobRepo.SearchAsync(
            criteria, 
            request.Page, 
            request.PageSize, 
            ct);
        
        // Map to DTO
        var response = new PaginatedResponse<JobDto>
        {
            Data = _mapper.Map<List<JobDto>>(result.Items),
            Pagination = new PaginationMeta
            {
                Page = result.Page,
                PageSize = result.PageSize,
                TotalItems = result.TotalCount,
                TotalPages = (int)Math.Ceiling((double)result.TotalCount / result.PageSize)
            }
        };
        
        return Ok(response);
    }
}
```

### 4.4 Hangfire Job Pattern

**Job Definition** (`JobIntel.Ingest/Jobs/ScrapeJob.cs`)
```csharp
public class ScrapeJob
{
    private readonly IScrapeApiClient _scrapeClient;
    private readonly IIngestionPipeline _pipeline;
    private readonly IIngestRunRepository _runRepo;
    private readonly ILogger<ScrapeJob> _logger;
    
    public ScrapeJob(
        IScrapeApiClient scrapeClient,
        IIngestionPipeline pipeline,
        IIngestRunRepository runRepo,
        ILogger<ScrapeJob> logger)
    {
        _scrapeClient = scrapeClient;
        _pipeline = pipeline;
        _runRepo = runRepo;
        _logger = logger;
    }
    
    public async Task ExecuteAsync(string source, string[] keywords, string? location)
    {
        var runId = await _runRepo.CreateAsync(new IngestRun
        {
            Source = source,
            Keywords = string.Join(", ", keywords),
            Location = location,
            StartedAt = DateTime.UtcNow,
            Status = IngestRunStatus.Running
        });
        
        try
        {
            _logger.LogInformation("Starting scrape job {RunId} for {Source}", runId, source);
            
            // Step 1: Fetch from Python API
            var rawJobs = await _scrapeClient.FetchJobsAsync(source, keywords, location);
            _logger.LogInformation("Fetched {Count} jobs from {Source}", rawJobs.Count, source);
            
            // Step 2: Process through pipeline
            var result = await _pipeline.ProcessAsync(rawJobs);
            
            // Step 3: Update run status
            await _runRepo.UpdateAsync(runId, new IngestRun
            {
                CompletedAt = DateTime.UtcNow,
                Status = IngestRunStatus.Success,
                JobsFound = rawJobs.Count,
                JobsNew = result.NewCount,
                JobsUpdated = result.UpdatedCount,
                JobsDeduped = result.DedupedCount
            });
            
            _logger.LogInformation(
                "Scrape job {RunId} completed: {New} new, {Updated} updated, {Deduped} duplicates", 
                runId, result.NewCount, result.UpdatedCount, result.DedupedCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Scrape job {RunId} failed", runId);
            
            await _runRepo.UpdateAsync(runId, new IngestRun
            {
                CompletedAt = DateTime.UtcNow,
                Status = IngestRunStatus.Failed,
                ErrorMessage = ex.Message,
                ErrorStackTrace = ex.StackTrace
            });
            
            throw; // Hangfire will retry
        }
    }
}
```

**Schedule Job** (`Program.cs`)
```csharp
// After app.Run()
using (var scope = app.Services.CreateScope())
{
    var recurringJobs = scope.ServiceProvider.GetRequiredService<IRecurringJobManager>();
    
    // Daily scrape at 2 AM UTC
    recurringJobs.AddOrUpdate<ScrapeJob>(
        "scrape-seek-tilers-adelaide",
        job => job.ExecuteAsync("seek", new[] { "tiler" }, "Adelaide"),
        Cron.Daily(2));
}
```

---

## 5. Database Operations

### 5.1 Migrations Workflow

**Create Migration:**
```bash
# From JobIntel.Infrastructure directory
dotnet ef migrations add <MigrationName> --startup-project ../JobIntel.Api

# Example:
dotnet ef migrations add AddUserAlertsTable --startup-project ../JobIntel.Api
```

**Apply Migration (local):**
```bash
dotnet ef database update --startup-project ../JobIntel.Api
```

**Rollback Migration:**
```bash
# Rollback to previous migration
dotnet ef database update <PreviousMigrationName> --startup-project ../JobIntel.Api

# Remove last migration (if not yet applied)
dotnet ef migrations remove --startup-project ../JobIntel.Api
```

**Generate SQL Script (for production):**
```bash
dotnet ef migrations script --startup-project ../JobIntel.Api --output migrations.sql
```

### 5.2 Seeding Data

**Create Seed Method** (`JobIntelDbContext.cs`)
```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    base.OnModelCreating(modelBuilder);
    
    // Seed test data (dev environment only)
    if (Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Development")
    {
        modelBuilder.Entity<JobPosting>().HasData(
            new JobPosting
            {
                Id = 1,
                Source = "test",
                SourceId = "test-001",
                Title = "Bricklayer - Adelaide CBD",
                Company = "Test Construction Pty Ltd",
                LocationState = "SA",
                LocationSuburb = "Adelaide",
                Trade = "bricklayer",
                Description = "Test job posting for development",
                Fingerprint = "test-fingerprint-001",
                PostedAt = DateTime.UtcNow.AddDays(-7),
                ScrapedAt = DateTime.UtcNow,
                IsActive = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            }
        );
    }
}
```

### 5.3 Raw SQL Queries (when needed)

```csharp
// Execute raw SQL (use sparingly!)
var stateStats = await _context.Database
    .SqlQuery<StateJobCount>(@"
        SELECT 
            location_state AS State,
            COUNT(*) AS JobCount
        FROM job_postings
        WHERE is_active = true
        GROUP BY location_state
        ORDER BY JobCount DESC
    ")
    .ToListAsync();

public record StateJobCount(string State, int JobCount);
```

### 5.4 Performance Optimization

**Use AsNoTracking for read-only queries:**
```csharp
// ✅ Good - no change tracking overhead
var jobs = await _context.JobPostings
    .AsNoTracking()
    .Where(x => x.Trade == "tiler")
    .ToListAsync();

// ❌ Bad - unnecessary tracking
var jobs = await _context.JobPostings
    .Where(x => x.Trade == "tiler")
    .ToListAsync();
```

**Avoid N+1 queries:**
```csharp
// ❌ Bad - N+1 problem
var jobs = await _context.JobPostings.ToListAsync();
foreach (var job in jobs)
{
    var company = await _context.Companies.FindAsync(job.CompanyId); // Separate query!
}

// ✅ Good - eager loading
var jobs = await _context.JobPostings
    .Include(x => x.Company)
    .ToListAsync();
```

**Use pagination:**
```csharp
// Always paginate large result sets
var page = 1;
var pageSize = 20;
var jobs = await _context.JobPostings
    .OrderByDescending(x => x.PostedAt)
    .Skip((page - 1) * pageSize)
    .Take(pageSize)
    .ToListAsync();
```

---

## 6. API Development Guidelines

### 6.1 Request/Response DTOs

**Request DTO** (`JobIntel.Core/DTOs/Requests/`)
```csharp
public class JobSearchRequest
{
    [FromQuery(Name = "trade")]
    public string? Trade { get; set; }
    
    [FromQuery(Name = "state")]
    [RegularExpression("^(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)$")]
    public string? State { get; set; }
    
    [FromQuery(Name = "posted_after")]
    public DateTime? PostedAfter { get; set; }
    
    [FromQuery(Name = "pay_min")]
    [Range(0, 200)]
    public decimal? PayMin { get; set; }
    
    [FromQuery(Name = "page")]
    [Range(1, int.MaxValue)]
    public int Page { get; set; } = 1;
    
    [FromQuery(Name = "page_size")]
    [Range(1, 100)]
    public int PageSize { get; set; } = 20;
}
```

**Response DTO** (`JobIntel.Core/DTOs/Responses/`)
```csharp
public class JobDto
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Company { get; set; } = string.Empty;
    public LocationDto Location { get; set; } = new();
    public string? Trade { get; set; }
    public string? EmploymentType { get; set; }
    public PayRangeDto? PayRange { get; set; }
    public string Description { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = new();
    public DateTime? PostedAt { get; set; }
    public JobSourceDto Source { get; set; } = new();
}

public class LocationDto
{
    public string State { get; set; } = string.Empty;
    public string? Suburb { get; set; }
}

public class PayRangeDto
{
    public decimal? Min { get; set; }
    public decimal? Max { get; set; }
    public string Currency { get; set; } = "AUD";
    public string Unit { get; set; } = "hour";
}

public class JobSourceDto
{
    public string Name { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
}
```

### 6.2 Error Handling

**Global Error Handler** (`Middleware/ErrorHandlingMiddleware.cs`)
```csharp
public class ErrorHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ErrorHandlingMiddleware> _logger;
    
    public ErrorHandlingMiddleware(RequestDelegate next, ILogger<ErrorHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }
    
    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            await HandleExceptionAsync(context, ex);
        }
    }
    
    private static Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var code = HttpStatusCode.InternalServerError;
        var result = JsonSerializer.Serialize(new ErrorResponse
        {
            Code = "INTERNAL_ERROR",
            Message = "An unexpected error occurred. Please try again later.",
            Timestamp = DateTime.UtcNow,
            RequestId = context.TraceIdentifier
        });
        
        context.Response.ContentType = "application/json";
        context.Response.StatusCode = (int)code;
        
        return context.Response.WriteAsync(result);
    }
}
```

**Custom Exceptions:**
```csharp
public class NotFoundException : Exception
{
    public NotFoundException(string message) : base(message) { }
}

public class ValidationException : Exception
{
    public Dictionary<string, string[]> Errors { get; }
    
    public ValidationException(Dictionary<string, string[]> errors) : base("Validation failed")
    {
        Errors = errors;
    }
}
```

### 6.3 Logging Best Practices

```csharp
public class JobsController : ControllerBase
{
    private readonly ILogger<JobsController> _logger;
    
    [HttpGet("{id}")]
    public async Task<IActionResult> GetJob(int id)
    {
        // ✅ Structured logging with parameters
        _logger.LogInformation("Fetching job {JobId}", id);
        
        var job = await _jobRepo.GetByIdAsync(id);
        
        if (job == null)
        {
            // ✅ Log with context
            _logger.LogWarning("Job {JobId} not found", id);
            return NotFound(new ErrorResponse($"Job {id} not found"));
        }
        
        // ✅ Log sensitive operations
        _logger.LogDebug("Successfully retrieved job {JobId} - {JobTitle}", id, job.Title);
        
        return Ok(_mapper.Map<JobDto>(job));
    }
}
```

**Log Levels:**
- `Trace`: Very detailed (disabled in production)
- `Debug`: Diagnostic information
- `Information`: General flow (e.g., "User logged in", "Job created")
- `Warning`: Unexpected but recoverable (e.g., "Job not found")
- `Error`: Failures requiring attention
- `Critical`: System-wide failures

---

## 7. Testing Strategy

### 7.1 Unit Tests (xUnit)

**Test Structure:**
```csharp
public class DeduplicationServiceTests
{
    [Fact]
    public void GenerateFingerprint_SameJob_ReturnsSameHash()
    {
        // Arrange
        var job1 = new JobPosting
        {
            Source = "seek",
            SourceId = "123",
            Title = "Bricklayer - Adelaide",
            Company = "ABC Construction",
            LocationState = "SA"
        };
        
        var job2 = new JobPosting
        {
            Source = "seek",
            SourceId = "123",
            Title = "Bricklayer - Adelaide",
            Company = "ABC Construction",
            LocationState = "SA"
        };
        
        var service = new DeduplicationService();
        
        // Act
        var hash1 = service.GenerateFingerprint(job1);
        var hash2 = service.GenerateFingerprint(job2);
        
        // Assert
        Assert.Equal(hash1, hash2);
    }
    
    [Theory]
    [InlineData("Bricklayer", "bricklayer")]
    [InlineData("Brick Layer", "bricklayer")]
    [InlineData("brick-layer!", "bricklayer")]
    public void NormalizeString_VariousInputs_ReturnsNormalized(string input, string expected)
    {
        // Arrange
        var service = new DeduplicationService();
        
        // Act
        var result = service.NormalizeString(input);
        
        // Assert
        Assert.Equal(expected, result);
    }
}
```

### 7.2 Integration Tests

**Setup:**
```csharp
public class JobsControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly JobIntelDbContext _context;
    
    public JobsControllerTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
        
        // Use in-memory database
        var scope = factory.Services.CreateScope();
        _context = scope.ServiceProvider.GetRequiredService<JobIntelDbContext>();
        _context.Database.EnsureCreated();
    }
    
    [Fact]
    public async Task SearchJobs_WithValidFilters_ReturnsOk()
    {
        // Arrange
        await SeedTestData();
        
        // Act
        var response = await _client.GetAsync("/api/jobs?trade=tiler&state=SA");
        
        // Assert
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<PaginatedResponse<JobDto>>(content);
        
        Assert.NotNull(result);
        Assert.True(result.Data.Count > 0);
        Assert.All(result.Data, job => Assert.Equal("tiler", job.Trade));
    }
    
    private async Task SeedTestData()
    {
        _context.JobPostings.AddRange(
            new JobPosting { /* ... */ },
            new JobPosting { /* ... */ }
        );
        await _context.SaveChangesAsync();
    }
}
```

### 7.3 Test Coverage Goals

| Layer | Target Coverage |
|-------|----------------|
| Core (business logic) | > 90% |
| Repositories | > 80% |
| Controllers | > 70% |
| Services | > 85% |
| Overall | > 80% |

**Run tests:**
```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# Run specific test class
dotnet test --filter "FullyQualifiedName~DeduplicationServiceTests"
```

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue: Migration fails with "relation already exists"**
```bash
# Solution: Drop database and recreate
dotnet ef database drop --force --startup-project ../JobIntel.Api
dotnet ef database update --startup-project ../JobIntel.Api
```

**Issue: Hangfire dashboard not accessible**
```csharp
// Ensure authorization is disabled for development
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new AllowAllAuthorizationFilter() } // DEV ONLY!
});
```

**Issue: CORS errors in frontend**
```csharp
// Program.cs
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

app.UseCors("AllowAll");
```

### 8.2 Debugging Tips

**Enable detailed EF Core logging:**
```csharp
// appsettings.Development.json
{
  "Logging": {
    "LogLevel": {
      "Microsoft.EntityFrameworkCore.Database.Command": "Information"
    }
  }
}
```

**Inspect generated SQL:**
```csharp
var query = _context.JobPostings.Where(x => x.Trade == "tiler");
Console.WriteLine(query.ToQueryString()); // Prints SQL
```

**Use Hangfire dashboard for job debugging:**
- Navigate to `http://localhost:5000/hangfire`
- View failed jobs, retry manually
- Check job arguments and stack traces

### 8.3 Performance Profiling

**Use MiniProfiler (optional):**
```bash
dotnet add package MiniProfiler.AspNetCore.Mvc
```

```csharp
// Program.cs
builder.Services.AddMiniProfiler(options =>
{
    options.RouteBasePath = "/profiler";
}).AddEntityFramework();

app.UseMiniProfiler();

// Access: http://localhost:5000/profiler/results-index
```

---

## Appendices

### A. Useful Commands Reference

```bash
# .NET CLI
dotnet build                              # Build solution
dotnet run                                # Run project
dotnet test                               # Run tests
dotnet format                             # Format code
dotnet watch run                          # Run with hot reload

# EF Core
dotnet ef migrations add <Name>           # Create migration
dotnet ef database update                 # Apply migrations
dotnet ef database drop                   # Drop database
dotnet ef dbcontext info                  # Show DbContext info

# Docker
docker ps                                 # List running containers
docker logs <container>                   # View logs
docker exec -it <container> psql -U admin # Connect to PostgreSQL

# Git
git checkout -b feature/my-feature        # Create branch
git add .                                 # Stage changes
git commit -m "Message"                   # Commit
git push origin feature/my-feature        # Push to remote
```

### B. Code Snippets (for IDE)

**Entity snippet:**
```xml
<CodeSnippet>
  <Header>
    <Title>Entity</Title>
    <Shortcut>entity</Shortcut>
  </Header>
  <Code Language="csharp">
    <![CDATA[
    public class $Name$
    {
        public int Id { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
        $end$
    }
    ]]>
  </Code>
</CodeSnippet>
```

---

**End of Development Guide**

For architecture decisions, refer to [Technical Design Document](./JOB_INTELLIGENCE_TECHNICAL_DESIGN.md).  
For deployment instructions, see [Deployment Guide](./DEPLOYMENT_GUIDE.md) (coming soon).
