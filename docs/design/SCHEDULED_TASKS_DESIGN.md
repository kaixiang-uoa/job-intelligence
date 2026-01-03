# 定时任务设计方案

> **创建时间:** 2025-12-23
> **状态:** 设计阶段
> **目的:** 规划系统的定时任务架构，支持从 V1 到 V2 的渐进式演进

---

## 📋 目录

1. [业务场景分析](#业务场景分析)
2. [两种模式对比](#两种模式对比)
3. [行业常见设计模式](#行业常见设计模式)
4. [分阶段实施方案](#分阶段实施方案)
5. [技术实现细节](#技术实现细节)
6. [数据库设计](#数据库设计)
7. [性能和成本考虑](#性能和成本考虑)

---

## 业务场景分析

### 核心问题

**定时任务的两种业务模式：**

1. **系统级定时抓取** - 系统后台自动维护数据池
2. **用户级定时抓取** - 用户个性化订阅和推送

### 关键差异

| 维度 | 系统级 | 用户级 |
|------|--------|--------|
| **数据归属** | 所有用户共享 | 每个用户独立 |
| **抓取策略** | 固定（热门组合） | 个性化（用户定义） |
| **资源消耗** | 低（集中抓取） | 高（分散抓取） |
| **适用场景** | Job board / 聚合平台 | 求职助手 / 订阅服务 |
| **用户体验** | 即时查询 | 主动推送 |
| **复杂度** | 简单 | 复杂（需用户系统） |

---

## 两种模式对比

### 模式 A：系统级定时抓取 ⭐ 推荐用于 V1

#### 业务场景
- 系统后台自动、定期从 SEEK/Indeed 抓取最新职位
- 所有用户共享同一份数据池
- 用户随时查询都能看到最新数据

#### 数据流程
```
系统定时任务（每小时/每天）
    ↓
抓取 SEEK/Indeed 最新职位
    ↓
保存到共享数据库（去重）
    ↓
所有用户都能查询到
```

#### 优点 ✅
- 简单高效，资源利用率高
- 数据集中管理，去重容易
- 用户无需等待，查询即时
- 适合大规模用户
- **无需用户系统即可运行**

#### 缺点 ❌
- 抓取策略固定（关键词、地区固定）
- 无法完全个性化（每个用户需求不同）
- 可能抓取用户不需要的数据

#### 典型应用
- Indeed、LinkedIn、SEEK 等 Job board
- 房产聚合平台（realestate.com.au）
- 新闻聚合平台

---

### 模式 B：用户级定时抓取 ⭐ 适合 V2

#### 业务场景
- 用户登录后设置个人搜索条件（如 "plumber in Sydney"）
- 系统为该用户定时抓取符合条件的职位
- 用户收到个性化推送/提醒

#### 数据流程
```
用户设置订阅：
  - 关键词：plumber
  - 地区：Sydney
  - 薪资范围：> $90k
  - 推送频率：每天早上 9 点

系统为该用户创建定时任务
    ↓
每天 9 点自动抓取符合条件的职位
    ↓
保存到用户的订阅结果中
    ↓
发送邮件/推送通知给用户
```

#### 优点 ✅
- 高度个性化
- 用户粘性强（订阅制）
- 可以精准推送
- 提高用户留存率

#### 缺点 ❌
- 复杂度高（需要用户系统、订阅管理）
- 资源消耗大（每个用户单独抓取）
- 可能重复抓取相同数据
- **需要完整的通知服务**

#### 典型应用
- Google Alerts
- 房产订阅提醒（Domain.com.au）
- LinkedIn Job Alerts

---

## 行业常见设计模式

### 1. LinkedIn / Indeed 模式（混合架构）⭐ 行业标准

**系统级抓取 + 用户订阅匹配**

```
第一层：系统每小时抓取热门职位（通用数据池）
    ↓
第二层：用户设置 Job Alert（基于现有数据池匹配）
    ↓
第三层：高级用户可触发即时搜索（API 调用）
```

**架构特点：**
- ✅ 基础数据由系统统一维护（降低成本）
- ✅ 用户订阅基于数据库查询，不触发实时抓取
- ✅ 只有 VIP/付费用户才能触发实时抓取
- ✅ 平衡了效率和个性化

**优势：**
- 资源可控
- 用户体验好
- 可扩展性强
- 适合大规模商业应用

**示例数据流：**
```sql
-- 系统抓取任务
每小时抓取 "software engineer" in Sydney → 数据库

-- 用户订阅
用户 A 订阅 "software engineer" in Sydney, $120k+
    ↓
每天早上 9 点，从数据库查询符合条件的新职位
    ↓
发送邮件给用户 A
```

---

### 2. Google Alerts 模式（纯用户订阅）

**每个用户创建自己的 Alert**

```
用户创建 Alert：
  - 关键词："machine learning engineer"
  - 频率：每天一次

系统定时（每天）：
    ↓
遍历所有用户的 Alert
    ↓
执行搜索/抓取
    ↓
发送结果给用户
```

**特点：**
- 完全个性化
- 需要强大的任务调度系统（Hangfire / Quartz）
- 适合中小规模用户（< 10,000 用户）

**资源考虑：**
- 10,000 用户 × 每天 1 次抓取 = 每天 10,000 次 API 调用
- 需要合理的频率限制和批处理

---

### 3. RSS Feed 模式（系统级固定抓取）

**系统维护固定的数据源**

```
系统每小时抓取固定来源
    ↓
用户订阅感兴趣的分类
    ↓
系统推送匹配的新内容
```

**特点：**
- 系统抓取策略固定
- 用户只能在现有分类中选择
- 资源消耗最低
- 适合新闻、博客聚合

---

## 分阶段实施方案

### 第一阶段：V1 - 系统级定时抓取 ⭐ 现在可做

**目标：** 保证数据库始终有最新职位

**实施策略：**
```
为 13 个 trade 类型创建定时任务
    ↓
每个 trade 抓取主要城市（Sydney, Melbourne, Brisbane, Adelaide, Perth）
    ↓
每 6 小时运行一次
    ↓
数据去重后入库
```

**任务矩阵：**
| Trade | 城市数 | 每次抓取量 | 每日总量 |
|-------|--------|-----------|---------|
| Plumber | 5 | 50 | 1000 |
| Electrician | 5 | 50 | 1000 |
| Carpenter | 5 | 50 | 1000 |
| ... | ... | ... | ... |
| **总计** | **65 任务** | **3250** | **13000** |

**预估成本：**
- 每 6 小时运行一次 = 每天 4 次
- 65 个任务 × 4 次/天 = **260 次抓取/天**
- 每次抓取 50 条 = **13,000 条数据/天**
- 去重后预计保留 30% = **约 4,000 条新职位/天**

**代码量：** 1-2 小时

**优点：**
- ✅ 简单，无需用户系统
- ✅ 数据持续更新
- ✅ 适合 MVP 验证
- ✅ 立即可用

**缺点：**
- ❌ 覆盖面有限（只抓热门组合）
- ❌ 不够个性化

---

### 第二阶段：V1.5 - 用户触发式搜索（可选）

**目标：** 允许用户即时搜索特定组合

**实施策略：**
```
用户访问网站 → 输入搜索条件
    ↓
前端调用 API: GET /api/ingest/seek?keywords=plumber&location=Sydney
    ↓
后端检查数据新鲜度（如果 < 24 小时，直接返回数据库结果）
    ↓
如果数据过期，触发即时抓取
    ↓
返回结果给用户
```

**特点：**
- 用户主动触发
- 按需抓取
- 无需定时任务
- 利用缓存减少 API 调用

**适合场景：**
- 用户量小（< 1,000）
- 查询频率低
- 快速验证市场需求

**缓存策略：**
```csharp
public async Task<List<JobDto>> SearchJobsAsync(string keywords, string location)
{
    var cacheKey = $"{keywords}_{location}";

    // 检查缓存
    var cachedResult = await _cache.GetAsync<List<JobDto>>(cacheKey);
    if (cachedResult != null && cachedResult.Age < TimeSpan.FromHours(24))
    {
        return cachedResult.Data;  // 返回缓存
    }

    // 缓存过期，触发抓取
    var freshData = await _scrapeApiClient.FetchJobsAsync(keywords, location);
    await _cache.SetAsync(cacheKey, freshData, TimeSpan.FromHours(24));

    return freshData;
}
```

---

### 第三阶段：V2 - 用户订阅 + Job Alerts 🚀 完整功能

**目标：** 提供个性化订阅和推送服务

**功能清单：**
1. ✅ 用户注册/登录
2. ✅ 创建个人 Job Alert
3. ✅ 设置推送频率（即时/每日/每周）
4. ✅ 多渠道通知（邮件/推送/短信）
5. ✅ Alert 管理（编辑/暂停/删除）
6. ✅ 查看推送历史

**实施策略：**
```
用户订阅基于数据库匹配（不重复抓取）
    ↓
系统定时扫描所有活跃 Alert
    ↓
从数据库查询匹配的新职位（last_run_at 之后的）
    ↓
如果有新职位 → 发送通知
    ↓
更新 last_run_at
```

**代码量：** 2-3 天

---

## 技术实现细节

### V1 实现：Hangfire 定时任务

#### 1. 基础配置

**Program.cs / Startup.cs:**
```csharp
// 添加 Hangfire 服务
builder.Services.AddHangfire(config => config
    .UsePostgreSqlStorage(connectionString)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings());

builder.Services.AddHangfireServer();

// 启用 Dashboard
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new MyAuthorizationFilter() }
});
```

#### 2. 创建定时任务服务

**IScheduledIngestService.cs:**
```csharp
public interface IScheduledIngestService
{
    Task FetchAndSaveAsync(string trade, string location, int maxResults);
}
```

**ScheduledIngestService.cs:**
```csharp
public class ScheduledIngestService : IScheduledIngestService
{
    private readonly IScrapeApiClient _scrapeApiClient;
    private readonly IIngestionPipeline _ingestionPipeline;
    private readonly ILogger<ScheduledIngestService> _logger;

    public async Task FetchAndSaveAsync(string trade, string location, int maxResults)
    {
        try
        {
            _logger.LogInformation(
                "Scheduled fetch started: trade={Trade}, location={Location}",
                trade, location);

            // 1. 从 SEEK 和 Indeed 抓取
            var seekTask = _scrapeApiClient.FetchJobsAsync(
                "seek", new[] { trade }, location, maxResults);
            var indeedTask = _scrapeApiClient.FetchJobsAsync(
                "indeed", new[] { trade }, location, maxResults);

            await Task.WhenAll(seekTask, indeedTask);

            var allJobs = seekTask.Result.Concat(indeedTask.Result).ToList();

            // 2. 处理和保存（去重）
            var result = await _ingestionPipeline.ProcessAsync(
                allJobs, "scheduled", CancellationToken.None);

            _logger.LogInformation(
                "Scheduled fetch completed: {Trade} in {Location}, " +
                "{New} new, {Updated} updated, {Duplicates} duplicates",
                trade, location, result.NewCount, result.UpdatedCount, result.DedupedCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Scheduled fetch failed: trade={Trade}, location={Location}",
                trade, location);
            throw;  // Hangfire 会自动重试
        }
    }
}
```

#### 3. 注册定时任务

**ScheduledJobsConfig.cs:**
```csharp
public static class ScheduledJobsConfig
{
    public static void ConfigureRecurringJobs()
    {
        var trades = new[]
        {
            "plumber", "electrician", "carpenter", "bricklayer",
            "tiler", "painter", "roofer", "plasterer",
            "glazier", "landscaper", "concreter", "drainer", "gasfitter"
        };

        var cities = new[]
        {
            "Sydney", "Melbourne", "Brisbane", "Adelaide", "Perth"
        };

        foreach (var trade in trades)
        {
            foreach (var city in cities)
            {
                var jobId = $"fetch-{trade}-{city}";

                RecurringJob.AddOrUpdate<IScheduledIngestService>(
                    jobId,
                    service => service.FetchAndSaveAsync(trade, city, 50),
                    Cron.Every(6).Hours(),  // 每 6 小时
                    new RecurringJobOptions
                    {
                        TimeZone = TimeZoneInfo.FindSystemTimeZoneById("AUS Eastern Standard Time")
                    });
            }
        }
    }
}
```

**在 Program.cs 中调用:**
```csharp
var app = builder.Build();

// 配置定时任务
ScheduledJobsConfig.ConfigureRecurringJobs();

app.Run();
```

#### 4. Hangfire Dashboard 访问

访问 `http://localhost:5000/hangfire` 查看：
- 所有定时任务列表
- 任务执行历史
- 成功/失败统计
- 手动触发任务
- 暂停/恢复任务

---

### V2 实现：用户订阅系统

#### 1. 数据库设计

**user_job_alerts 表:**
```sql
CREATE TABLE user_job_alerts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,  -- "Plumber jobs in Sydney"

    -- 搜索条件（JSONB）
    criteria JSONB NOT NULL,
    /* 示例：
    {
        "trade": "plumber",
        "locationState": "NSW",
        "locationSuburb": "Sydney",
        "payMin": 90000,
        "employmentType": "Full Time"
    }
    */

    -- 推送设置
    frequency VARCHAR(20) NOT NULL,  -- immediate, daily, weekly
    notification_channels JSONB,  -- ["email", "push"]

    -- 状态
    is_active BOOLEAN DEFAULT true,

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_run_at TIMESTAMP,

    -- 外键
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_alerts_user_id ON user_job_alerts(user_id);
CREATE INDEX idx_alerts_active ON user_job_alerts(is_active) WHERE is_active = true;
CREATE INDEX idx_alerts_frequency ON user_job_alerts(frequency);
```

**alert_notifications 表:**
```sql
CREATE TABLE alert_notifications (
    id SERIAL PRIMARY KEY,
    alert_id INT NOT NULL,
    job_id INT NOT NULL,

    -- 通知详情
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    channel VARCHAR(20) NOT NULL,  -- email, push, sms
    status VARCHAR(20) NOT NULL,  -- sent, failed, pending
    error_message TEXT,

    -- 外键
    CONSTRAINT fk_alert FOREIGN KEY (alert_id) REFERENCES user_job_alerts(id) ON DELETE CASCADE,
    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_alert_id ON alert_notifications(alert_id);
CREATE INDEX idx_notifications_sent_at ON alert_notifications(sent_at);
```

#### 2. Alert 处理服务

**IAlertProcessingService.cs:**
```csharp
public interface IAlertProcessingService
{
    Task ProcessAlertsAsync(string frequency);
}
```

**AlertProcessingService.cs:**
```csharp
public class AlertProcessingService : IAlertProcessingService
{
    private readonly IAlertRepository _alertRepository;
    private readonly IJobRepository _jobRepository;
    private readonly INotificationService _notificationService;
    private readonly ILogger<AlertProcessingService> _logger;

    public async Task ProcessAlertsAsync(string frequency)
    {
        // 1. 获取所有活跃的指定频率的 Alert
        var alerts = await _alertRepository.GetActiveAlertsAsync(frequency);

        _logger.LogInformation(
            "Processing {Count} {Frequency} alerts",
            alerts.Count, frequency);

        foreach (var alert in alerts)
        {
            try
            {
                // 2. 反序列化搜索条件
                var criteria = JsonSerializer.Deserialize<JobSearchCriteria>(alert.Criteria);

                // 3. 只查询自上次运行以来的新职位
                criteria.PostedAfter = alert.LastRunAt ?? DateTime.UtcNow.AddDays(-7);

                // 4. 从数据库查询匹配的职位（不触发新抓取）
                var result = await _jobRepository.SearchAsync(
                    criteria,
                    page: 1,
                    pageSize: 50,
                    sortBy: "posted_at_desc");

                if (result.Items.Count > 0)
                {
                    // 5. 发送通知
                    await _notificationService.SendAlertNotificationAsync(
                        alert.UserId,
                        alert.Name,
                        result.Items,
                        alert.NotificationChannels);

                    _logger.LogInformation(
                        "Sent {Count} jobs to user {UserId} for alert '{Name}'",
                        result.Items.Count, alert.UserId, alert.Name);
                }

                // 6. 更新最后运行时间
                alert.LastRunAt = DateTime.UtcNow;
                await _alertRepository.UpdateAsync(alert);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex,
                    "Failed to process alert {AlertId}", alert.Id);
            }
        }
    }
}
```

#### 3. 定时任务配置

**在 ScheduledJobsConfig.cs 中添加:**
```csharp
// 每天早上 9 点处理每日 Alert
RecurringJob.AddOrUpdate<IAlertProcessingService>(
    "process-daily-alerts",
    service => service.ProcessAlertsAsync("daily"),
    Cron.Daily(9),  // 每天 9:00 AM
    new RecurringJobOptions
    {
        TimeZone = TimeZoneInfo.FindSystemTimeZoneById("AUS Eastern Standard Time")
    });

// 每周一早上 9 点处理每周 Alert
RecurringJob.AddOrUpdate<IAlertProcessingService>(
    "process-weekly-alerts",
    service => service.ProcessAlertsAsync("weekly"),
    Cron.Weekly(DayOfWeek.Monday, 9),
    new RecurringJobOptions
    {
        TimeZone = TimeZoneInfo.FindSystemTimeZoneById("AUS Eastern Standard Time")
    });

// 即时 Alert 每 15 分钟检查一次
RecurringJob.AddOrUpdate<IAlertProcessingService>(
    "process-immediate-alerts",
    service => service.ProcessAlertsAsync("immediate"),
    Cron.Every(15).Minutes());
```

#### 4. API 端点

**AlertsController.cs:**
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]  // 需要登录
public class AlertsController : ControllerBase
{
    private readonly IAlertRepository _alertRepository;

    // POST /api/alerts - 创建 Alert
    [HttpPost]
    public async Task<ActionResult<AlertDto>> CreateAlert(CreateAlertRequest request)
    {
        var userId = GetCurrentUserId();  // 从 JWT token 获取

        var alert = new UserJobAlert
        {
            UserId = userId,
            Name = request.Name,
            Criteria = JsonSerializer.Serialize(request.Criteria),
            Frequency = request.Frequency,
            NotificationChannels = JsonSerializer.Serialize(request.NotificationChannels),
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        var alertId = await _alertRepository.CreateAsync(alert);

        return Ok(new { alertId, message = "Alert created successfully" });
    }

    // GET /api/alerts - 获取用户的所有 Alert
    [HttpGet]
    public async Task<ActionResult<List<AlertDto>>> GetMyAlerts()
    {
        var userId = GetCurrentUserId();
        var alerts = await _alertRepository.GetByUserIdAsync(userId);

        return Ok(alerts);
    }

    // PUT /api/alerts/{id} - 更新 Alert
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateAlert(int id, UpdateAlertRequest request)
    {
        var userId = GetCurrentUserId();
        var alert = await _alertRepository.GetByIdAsync(id);

        if (alert == null || alert.UserId != userId)
            return NotFound();

        alert.Name = request.Name;
        alert.Criteria = JsonSerializer.Serialize(request.Criteria);
        alert.Frequency = request.Frequency;

        await _alertRepository.UpdateAsync(alert);

        return Ok();
    }

    // DELETE /api/alerts/{id} - 删除 Alert
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteAlert(int id)
    {
        var userId = GetCurrentUserId();
        var alert = await _alertRepository.GetByIdAsync(id);

        if (alert == null || alert.UserId != userId)
            return NotFound();

        await _alertRepository.DeleteAsync(id);

        return NoContent();
    }

    // POST /api/alerts/{id}/toggle - 暂停/恢复 Alert
    [HttpPost("{id}/toggle")]
    public async Task<IActionResult> ToggleAlert(int id)
    {
        var userId = GetCurrentUserId();
        var alert = await _alertRepository.GetByIdAsync(id);

        if (alert == null || alert.UserId != userId)
            return NotFound();

        alert.IsActive = !alert.IsActive;
        await _alertRepository.UpdateAsync(alert);

        return Ok(new { isActive = alert.IsActive });
    }
}
```

---

## 数据库设计

### V1 额外表（可选）

**scheduled_ingest_runs 表:**
```sql
CREATE TABLE scheduled_ingest_runs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,  -- "fetch-plumber-sydney"
    trade VARCHAR(50),
    location VARCHAR(100),

    -- 执行结果
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- success, failed, running

    -- 统计
    jobs_fetched INT DEFAULT 0,
    jobs_new INT DEFAULT 0,
    jobs_updated INT DEFAULT 0,
    jobs_duplicated INT DEFAULT 0,

    -- 错误信息
    error_message TEXT,

    -- 元数据
    hangfire_job_id VARCHAR(100)
);

CREATE INDEX idx_ingest_runs_job_id ON scheduled_ingest_runs(job_id);
CREATE INDEX idx_ingest_runs_started_at ON scheduled_ingest_runs(started_at);
```

**用途：**
- 追踪每次定时任务的执行情况
- 统计抓取效率
- 监控和告警

---

### V2 完整表设计

已在上面 "技术实现细节 - V2 实现" 中详细说明：
- `user_job_alerts` - 用户订阅表
- `alert_notifications` - 推送历史表

---

## 性能和成本考虑

### V1 系统级抓取

**资源消耗估算：**

| 指标 | 数值 | 说明 |
|------|------|------|
| 定时任务数 | 65 | 13 trades × 5 cities |
| 执行频率 | 每 6 小时 | 每天 4 次 |
| 每日总抓取次数 | 260 | 65 × 4 |
| 每次抓取量 | 50 | SEEK + Indeed |
| 每日抓取总量 | 13,000 | 260 × 50 |
| 去重后保留率 | 30% | 预估 |
| 每日新增职位 | ~4,000 | 13,000 × 30% |

**API 成本（如果有限制）：**
- SEEK API: 260 次/天
- Indeed API: 260 次/天（通过 JobSpy 抓取，可能被限制）

**数据库存储：**
- 每条职位 ~2KB
- 每天新增 4,000 条 × 2KB = **8 MB/天**
- 一个月 = **240 MB**
- 一年 = **2.9 GB**

**优化策略：**
1. **智能调度** - 白天每 4 小时，晚上每 8 小时
2. **优先级抓取** - 热门组合优先
3. **失败重试** - Hangfire 自动重试机制
4. **数据清理** - 30 天后归档旧职位

---

### V2 用户订阅

**资源消耗估算（假设 1,000 用户）：**

| 场景 | 用户数 | 每日查询次数 | 总查询 | 说明 |
|------|--------|-------------|--------|------|
| 每日 Alert | 700 | 1 | 700 | 基于数据库查询 |
| 每周 Alert | 200 | 0.14 | 28 | 每周一次 |
| 即时 Alert | 100 | 96 | 9,600 | 每 15 分钟 |
| **总计** | 1,000 | - | **10,328** | 纯数据库查询 |

**关键优化：**
- ✅ **不触发新抓取** - 基于 V1 的数据池查询
- ✅ **批量处理** - 每次处理多个 Alert
- ✅ **索引优化** - criteria JSONB 字段使用 GIN 索引
- ✅ **缓存结果** - 相同条件共享结果

**通知成本：**
- 邮件：SendGrid 免费额度 100 emails/day
- 推送：Firebase 免费
- 短信：Twilio 按条计费（可选）

---

### 成本对比

| 方案 | API 调用 | 数据库查询 | 存储 | 通知 | 总成本 |
|------|---------|-----------|------|------|--------|
| V1 系统级 | 260/天 | 低 | 8 MB/天 | 无 | **低** |
| V2 用户级（纯抓取） | 10,000/天 | 低 | 20 MB/天 | 高 | **高** |
| V2 混合架构 | 260/天 | 10,000/天 | 8 MB/天 | 中 | **中** |

**结论：** V2 混合架构（系统抓取 + 用户订阅匹配）是最优方案 ✅

---

## 监控和告警

### V1 监控指标

**Hangfire Dashboard 自带：**
- ✅ 任务成功率
- ✅ 任务失败次数
- ✅ 平均执行时间
- ✅ 队列长度

**自定义监控（可选）：**
```csharp
public class IngestMonitoringService
{
    public async Task CheckIngestHealthAsync()
    {
        // 检查最近 1 小时内是否有成功的抓取
        var recentRuns = await _runRepository.GetRecentRunsAsync(TimeSpan.FromHours(1));

        if (!recentRuns.Any(r => r.Status == "success"))
        {
            // 发送告警邮件给管理员
            await _alertService.SendAdminAlertAsync(
                "Scheduled ingest not running",
                "No successful ingest in the last hour");
        }

        // 检查失败率
        var failureRate = recentRuns.Count(r => r.Status == "failed") / (double)recentRuns.Count;
        if (failureRate > 0.5)
        {
            await _alertService.SendAdminAlertAsync(
                "High ingest failure rate",
                $"Failure rate: {failureRate:P}");
        }
    }
}
```

### V2 监控指标

**Alert 系统健康度：**
- 处理的 Alert 数量
- 成功发送的通知数量
- 失败的通知数量
- 平均处理时间

**用户参与度：**
- 活跃 Alert 数量
- 用户打开邮件率
- 用户点击职位率

---

## 总结和建议

### 推荐实施路线

```
V1（现在）
    ↓
系统级定时抓取（1-2 小时实施）
    ↓
验证数据质量和系统稳定性
    ↓
V1.5（可选）
    ↓
用户触发式搜索（按需抓取）
    ↓
收集用户反馈
    ↓
V2（未来 1-2 个月）
    ↓
用户订阅 + Job Alerts
    ↓
完整的个性化服务
```

### 关键决策点

| 决策 | V1 | V2 |
|------|----|----|
| **抓取策略** | 系统级固定 | 基于数据池匹配 |
| **用户系统** | 不需要 | 需要 |
| **通知服务** | 不需要 | 需要 |
| **复杂度** | 低 | 中 |
| **开发时间** | 1-2 小时 | 2-3 天 |
| **适用场景** | MVP 验证 | 商业产品 |

### 下一步行动

1. ✅ **立即实施 V1 系统级定时抓取**
   - 简单高效
   - 无需用户系统
   - 验证技术可行性

2. ⏸️ **V1.5 可选（按需决定）**
   - 如果用户量小，可跳过
   - 直接进入 V2

3. 🚀 **V2 作为长期目标**
   - 在 V1 稳定后实施
   - 提供差异化竞争力

---

**文档创建时间:** 2025-12-23
**作者:** Claude Code & User
**状态:** 设计完成，待实施
**下一步:** 实施 V1 系统级定时抓取
