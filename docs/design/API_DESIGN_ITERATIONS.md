# API Design Iterations - RESTful API 设计演进

> **文档说明:** 记录 API 设计的迭代过程,体现 Agile 开发中的设计演进。每次 API 设计变更都在此记录。

---

## 📋 迭代历史

### Iteration 1.0 - Initial Design (2024-12-14)
**来源:** Technical Design Document v1.0

**设计特点:**
- Snake_case 参数命名 (posted_after, pay_min, page_size, sort_by)
- 符合 PostgreSQL 数据库命名风格
- 与原始技术文档保持一致

**示例:**
```http
GET /api/jobs?trade=tiler&state=SA&posted_after=2024-12-01&page=1&page_size=20&sort_by=posted_at_desc
```

**响应格式:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 250,
    "total_pages": 13
  }
}
```

---

### Iteration 1.1 - API Naming Convention Refinement (2024-12-14)
**变更原因:**
- RESTful API 最佳实践通常使用 camelCase
- 提升前端集成体验 (JavaScript/TypeScript 友好)
- 与 .NET API 惯例保持一致
- 后端数据库仍使用 snake_case,仅 API 层使用 camelCase

**变更讨论:**
经过团队讨论,确定以下设计方案:

| 设计方面 | 选择的方案 | 理由 |
|---------|-----------|------|
| 分页参数 | `page` + `pageSize` | 直观易懂,符合直觉 |
| 排序参数 | `sortBy=posted_at_desc` | 清晰明确,自文档化 |
| 响应格式 | 扁平化 (data + pagination) | 简单直接,减少嵌套 |
| 过滤参数 | 简洁风格 (`trade=tiler`) | 符合 REST 习惯 |
| 日期参数 | `postedAfter` (camelCase) | 与其他参数命名统一 |

**最终设计:**

#### 参数命名对照表

| 原设计 (snake_case) | 新设计 (camelCase) | 说明 |
|-------------------|-------------------|------|
| `posted_after` | `postedAfter` | 发布时间筛选 |
| `pay_min` | `payMin` | 最低薪资 |
| `pay_max` | `payMax` | 最高薪资 |
| `employment_type` | `employmentType` | 雇佣类型 |
| `page_size` | `pageSize` | 每页数量 |
| `sort_by` | `sortBy` | 排序方式 |
| `total_items` | `totalItems` | 总记录数 |
| `total_pages` | `totalPages` | 总页数 |

**保持不变的参数:**
- `trade` - 单词,无需转换
- `state` - 单词,无需转换
- `suburb` - 单词,无需转换
- `page` - 单词,无需转换
- `tags` - 单词,无需转换

---

## 📖 当前 API 规范 (v1.1)

### Base URL
```
Development: http://localhost:5000/api
Production:  https://api.jobintel.com/api
```

---

### 1. Job Search & Retrieval

#### 1.1 Search Jobs

**Endpoint:**
```http
GET /api/jobs
```

**Query Parameters:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| `trade` | string | ❌ | - | 行业筛选: bricklayer, tiler, plasterer, carpenter, etc. |
| `state` | string | ❌ | - | 州筛选: NSW, VIC, QLD, SA, WA, TAS, NT, ACT |
| `suburb` | string | ❌ | - | 城市/郊区筛选 |
| `postedAfter` | datetime | ❌ | - | 发布时间筛选 (ISO 8601 格式) |
| `payMin` | decimal | ❌ | - | 最低时薪 (AUD) |
| `payMax` | decimal | ❌ | - | 最高时薪 (AUD) |
| `employmentType` | string | ❌ | - | 雇佣类型: full-time, part-time, casual, contract, apprenticeship |
| `tags` | string[] | ❌ | - | 标签筛选 (多选) |
| `page` | int | ❌ | 1 | 页码 (>= 1) |
| `pageSize` | int | ❌ | 20 | 每页数量 (1-100) |
| `sortBy` | string | ❌ | posted_at_desc | 排序方式 |

**排序选项 (sortBy):**
- `posted_at_asc` - 发布时间升序
- `posted_at_desc` - 发布时间降序 (默认)
- `pay_desc` - 薪资降序
- `pay_asc` - 薪资升序
- `title_asc` - 标题升序
- `title_desc` - 标题降序

**示例请求:**
```http
GET /api/jobs?trade=tiler&state=SA&postedAfter=2024-12-01&page=1&pageSize=20&sortBy=posted_at_desc
```

**成功响应 (200 OK):**
```json
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
      "employmentType": "full-time",
      "payRange": {
        "min": 35.00,
        "max": 45.00,
        "currency": "AUD",
        "unit": "hour"
      },
      "description": "We are seeking an experienced bricklayer...",
      "tags": ["visa_sponsor", "experienced"],
      "postedAt": "2024-12-10T08:00:00Z",
      "source": {
        "name": "seek",
        "url": "https://seek.com.au/job/12345"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 250,
    "totalPages": 13
  }
}
```

**错误响应:**

**400 Bad Request** - 参数验证失败
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid query parameters",
    "details": {
      "pageSize": "Must be between 1 and 100",
      "state": "Invalid state code"
    },
    "timestamp": "2024-12-14T10:30:00Z"
  }
}
```

---

#### 1.2 Get Job Details

**Endpoint:**
```http
GET /api/jobs/{id}
```

**Path Parameters:**
- `id` (int, required) - Job posting ID

**示例请求:**
```http
GET /api/jobs/12345
```

**成功响应 (200 OK):**
```json
{
  "id": 12345,
  "title": "Bricklayer - Adelaide CBD",
  "company": "ABC Construction",
  "location": {
    "state": "SA",
    "suburb": "Adelaide"
  },
  "trade": "bricklayer",
  "employmentType": "full-time",
  "payRange": {
    "min": 35.00,
    "max": 45.00,
    "currency": "AUD",
    "unit": "hour"
  },
  "description": "We are seeking an experienced bricklayer...",
  "requirements": "- Certificate III in Bricklaying\n- 2+ years experience\n- White Card",
  "tags": ["visa_sponsor", "experienced"],
  "postedAt": "2024-12-10T08:00:00Z",
  "scrapedAt": "2024-12-14T10:30:00Z",
  "lastCheckedAt": "2024-12-14T10:30:00Z",
  "isActive": true,
  "source": {
    "name": "seek",
    "url": "https://seek.com.au/job/12345"
  }
}
```

**错误响应:**

**404 Not Found**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Job posting with ID 12345 not found",
    "timestamp": "2024-12-14T10:30:00Z"
  }
}
```

---

### 2. Analytics & Statistics

#### 2.1 Get Overall Statistics

**Endpoint:**
```http
GET /api/analytics/stats
```

**Query Parameters:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| `since` | datetime | ❌ | - | 统计起始时间 (ISO 8601) |
| `trade` | string | ❌ | - | 按行业筛选统计 |

**示例请求:**
```http
GET /api/analytics/stats?since=2024-12-01&trade=tiler
```

**成功响应 (200 OK):**
```json
{
  "totalJobs": 5432,
  "activeJobs": 4210,
  "jobsAddedToday": 87,
  "byTrade": {
    "bricklayer": 1200,
    "tiler": 1850,
    "plasterer": 980,
    "carpenter": 1402
  },
  "byState": {
    "NSW": 1500,
    "VIC": 1200,
    "QLD": 1100,
    "SA": 650,
    "WA": 800,
    "TAS": 82,
    "NT": 50,
    "ACT": 50
  },
  "avgPayRate": {
    "min": 28.50,
    "max": 42.30,
    "median": 35.00
  }
}
```

---

#### 2.2 Get Trends (Optional - Phase 3)

**Endpoint:**
```http
GET /api/analytics/trends
```

**Query Parameters:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| `trade` | string | ✅ | - | 行业 |
| `state` | string | ❌ | - | 州 |
| `days` | int | ❌ | 30 | 分析天数 (1-90) |

**示例请求:**
```http
GET /api/analytics/trends?trade=tiler&state=SA&days=30
```

**成功响应 (200 OK):**
```json
{
  "trade": "tiler",
  "state": "SA",
  "period": {
    "start": "2024-11-14",
    "end": "2024-12-14"
  },
  "dailyCounts": [
    { "date": "2024-11-14", "count": 12 },
    { "date": "2024-11-15", "count": 15 },
    { "date": "2024-11-16", "count": 18 }
  ],
  "trend": "increasing",
  "changePercent": 25.5
}
```

---

### 3. Admin Operations

#### 3.1 Trigger Manual Scrape

**Endpoint:**
```http
POST /api/admin/scrape
```

**Request Body:**
```json
{
  "source": "seek",
  "keywords": ["tiler", "bricklayer"],
  "location": "Adelaide",
  "maxResults": 100
}
```

**成功响应 (202 Accepted):**
```json
{
  "jobId": "abc123",
  "status": "queued",
  "message": "Scraping job has been queued"
}
```

---

## 🔄 命名约定总结

### API 层 (对外接口)
- **参数命名:** camelCase
- **JSON 字段:** camelCase
- **HTTP 方法:** 标准 RESTful (GET, POST, PUT, DELETE)
- **路径:** kebab-case (如需要)

**示例:**
```json
{
  "pageSize": 20,
  "totalItems": 100,
  "employmentType": "full-time",
  "postedAt": "2024-12-14T10:30:00Z"
}
```

### 数据库层 (内部存储)
- **表名:** snake_case
- **列名:** snake_case
- **索引名:** snake_case

**示例:**
```sql
SELECT
  employment_type,
  posted_at,
  pay_range_min
FROM job_postings
```

### C# 代码层 (应用逻辑)
- **类名:** PascalCase
- **属性名:** PascalCase
- **方法名:** PascalCase
- **参数名:** camelCase

**示例:**
```csharp
public class JobPosting
{
    public string EmploymentType { get; set; }
    public DateTime PostedAt { get; set; }
    public decimal? PayRangeMin { get; set; }
}
```

---

## 📊 DTO 映射策略

### Entity → DTO 映射
使用扩展方法实现清晰的映射逻辑:

```csharp
public static class JobPostingExtensions
{
    public static JobDto ToDto(this JobPosting entity)
    {
        return new JobDto
        {
            Id = entity.Id,
            Title = entity.Title,
            Company = entity.Company,
            Location = new LocationDto
            {
                State = entity.LocationState,
                Suburb = entity.LocationSuburb
            },
            Trade = entity.Trade,
            EmploymentType = entity.EmploymentType,
            PayRange = entity.PayRangeMin.HasValue || entity.PayRangeMax.HasValue
                ? new PayRangeDto
                {
                    Min = entity.PayRangeMin,
                    Max = entity.PayRangeMax,
                    Currency = "AUD",
                    Unit = "hour"
                }
                : null,
            Description = entity.Description,
            Tags = ParseTags(entity.Tags),
            PostedAt = entity.PostedAt,
            Source = new JobSourceDto
            {
                Name = entity.Source,
                Url = $"https://{entity.Source}.com.au/job/{entity.SourceId}"
            }
        };
    }

    private static List<string> ParseTags(string? tagsJson)
    {
        if (string.IsNullOrEmpty(tagsJson))
            return new List<string>();

        return JsonSerializer.Deserialize<List<string>>(tagsJson)
               ?? new List<string>();
    }
}
```

---

## 🎯 设计原则

1. **一致性优先:**
   - API 层统一使用 camelCase
   - 数据库层统一使用 snake_case
   - C# 代码层统一使用 PascalCase

2. **用户友好:**
   - 参数命名直观易懂
   - 错误信息清晰明确
   - 响应格式简单扁平

3. **前端友好:**
   - JavaScript/TypeScript 原生支持 camelCase
   - 减少字段转换工作
   - JSON 序列化配置自动处理

4. **可扩展性:**
   - 预留未来功能的参数空间
   - 响应格式支持版本演进
   - 向后兼容考虑

5. **性能优化:**
   - 合理的分页限制 (max 100)
   - 利用数据库索引
   - 支持灵活的排序选项

---

## 📝 实施清单

### Phase 1, Sprint 1.4 实施要点:

- [ ] 配置 JSON 序列化为 camelCase
  ```csharp
  builder.Services.AddControllers()
      .AddJsonOptions(options =>
      {
          options.JsonSerializerOptions.PropertyNamingPolicy =
              JsonNamingPolicy.CamelCase;
      });
  ```

- [ ] 所有 DTO 类使用 PascalCase 属性名
- [ ] Controller 参数绑定使用 [FromQuery] 自动映射
- [ ] Swagger 文档生成正确的 camelCase 示例
- [ ] 错误响应使用统一格式

---

## 🔮 未来迭代规划

### Iteration 1.2 (计划 - Phase 2)
**可能的增强:**
- 添加 HATEOAS links (自描述 API)
- 支持 GraphQL (灵活查询)
- API 版本控制 (v1, v2)
- 响应压缩 (gzip)
- ETag 支持 (缓存优化)

### Iteration 1.3 (计划 - Phase 3)
**可能的增强:**
- 批量操作端点
- Webhook 通知
- WebSocket 实时更新
- 高级过滤语法 (类似 OData)

---

**最后更新:** 2024-12-14 21:00
**下次迭代:** Sprint 1.4 完成后评审
**文档所有者:** Development Team
