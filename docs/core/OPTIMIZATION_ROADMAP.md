# 优化路线图 (Optimization Roadmap)

> **文档类型:** 开发计划 / 技术债跟踪
> **目标:** 记录 Job Intelligence 项目的待优化项，按优先级组织，便于后续评估和实施
> **最后更新:** 2025-12-20

---

## 📋 文档说明

本文档记录 **Python 爬虫服务（scrape-api/）** 和 **.NET 后端服务** 的优化任务。

**使用方式:**
- ✅ 核心功能完成后，回顾此文档评估是否需要优化
- ✅ 面试准备时，参考此文档讲述项目的改进空间
- ✅ 学习新技术时，从 P2-P3 任务中选择实践项目

**优先级定义:**
- **P1 (Important):** 影响系统稳定性和可维护性，建议尽快完成
- **P2 (Nice-to-Have):** 提升性能和用户体验，可根据需求评估
- **P3 (Future):** 功能扩展，可延后到 V2 版本

---

## 🎯 当前状态总览

### Python 爬虫服务

| 类别 | P1 | P2 | P3 |
|------|----|----|-----|
| 测试 | 2/2 ✅ | 0/0 | 0/0 |
| 错误处理 | 2/2 ✅ | 0/1 | 0/0 |
| 性能优化 | 0/0 | 0/3 | 0/0 |
| 日志监控 | 0/0 | 0/2 | 0/0 |
| 功能扩展 | 0/0 | 0/0 | 0/3 |

**总计:** 4/11 任务完成（36.4%）
**P1 任务完成率:** 100% (4/4) 🎉
**最后更新:** 2025-12-21

### .NET 后端服务

| 类别 | P1 | P2 | P3 |
|------|----|----|-----|
| 集成测试 | 0/1 | 0/0 | 0/0 |
| 性能优化 | 0/0 | 0/2 | 0/0 |
| 功能扩展 | 0/0 | 0/0 | 0/2 |

**总计:** 0/5 任务完成（0%）

---

## 🔧 Python 爬虫服务优化任务

### P1 - 质量保证 (Important)

#### 1.1 SeekAdapter 单元测试 ✅

**状态:** 已完成
**实际时间:** 1.5 小时
**完成时间:** 2025-12-21

**任务描述:**
- 当前 SeekAdapter 只有手动测试和端到端测试
- 缺少单元测试覆盖核心方法

**已完成任务:**
```python
# tests/test_seek_adapter.py (23 个新测试)
✅ test_build_params_basic()                    # URL 参数构建
✅ test_build_params_max_results()              # 最大结果数
✅ test_build_params_keywords_with_spaces()     # 带空格关键词
✅ test_extract_description_from_teaser()       # 从 teaser 提取
✅ test_extract_description_from_bullet_points() # 从 bulletPoints 提取
✅ test_extract_description_truncate_*()        # 长描述截断（2个）
✅ test_extract_description_empty*()            # 空描述处理（2个）
✅ test_transform_job_success()                 # 正常数据转换
✅ test_transform_job_missing_*()               # 缺少字段（2个）
✅ test_transform_job_no_*()                    # 可选字段缺失（3个）
✅ test_transform_job_invalid_*()               # 无效数据（2个）
✅ test_transform_job_*_company_field()         # 备选字段（2个）
✅ test_scrape_success()                        # 成功抓取（mock）
✅ test_scrape_empty_results()                  # 空结果
✅ test_scrape_partial_failures()               # 部分失败
✅ test_scrape_max_results_adjustment()         # 参数调整
```

**成功标准:**
- ✅ 新增 23 个单元测试（超出预期）
- ✅ 覆盖核心数据转换逻辑
- ✅ 所有测试通过（92/92 = 100%）

**发现的问题和修复:**
- ✅ **Bug 修复:** SeekAdapter 中 `parse_location()` 返回值赋值错误
  - 原代码：`city, state = parse_location(location_label)`
  - 修复后：`state, suburb = parse_location(location_label)`
  - 影响：DTO 中 `location_suburb` 和 `location_state` 字段值互换

**测试覆盖提升:**
- 总测试数：69 → 92 (+23)
- 执行时间：0.30 秒
- 通过率：100%

**收益:**
- ✅ 提前发现了数据字段赋值错误的 bug
- ✅ 覆盖了所有边缘情况（缺少字段、无效数据、备选字段）
- ✅ 为未来重构提供了安全网
- ✅ 面试时可以展示完整的 TDD 流程

---

#### 1.2 错误处理细化 ✅

**状态:** 已完成
**实际时间:** 1 小时
**完成时间:** 2025-12-21

**任务描述:**
- 当前所有异常都捕获为通用 Exception
- 无法区分网络错误、数据格式错误、业务逻辑错误

**已完成任务:**
```python
# app/exceptions.py - 创建完整的异常体系（280 行）
✅ ScraperException                    # 基础异常类
✅ ScraperNetworkError                 # 网络错误
✅ ScraperTimeoutError                 # 超时错误（继承自 NetworkError）
✅ RateLimitException                  # 速率限制（继承自 NetworkError）
✅ ScraperDataError                    # 数据格式错误
✅ ScraperValidationError              # 验证错误
✅ ScraperParsingError                 # 解析错误（继承自 DataError）
✅ PlatformException                   # 平台 API 错误
✅ ScraperAuthenticationError          # 认证错误（继承自 PlatformException）
✅ ScraperNotFoundError                # 资源不存在（继承自 PlatformException）
✅ ScraperConfigurationError           # 配置错误
✅ classify_http_error()               # HTTP 状态码分类函数

# app/adapters/seek_adapter.py - 更新错误处理
✅ _call_seek_api() 方法：
  - requests.Timeout → ScraperTimeoutError
  - requests.HTTPError → classify_http_error()
  - requests.ConnectionError → ScraperNetworkError
  - JSON 解析失败 → ScraperDataError
  - 响应格式错误 → ScraperDataError

✅ _transform_job() 方法：
  - 缺少必需字段 → ScraperValidationError（带字段名）
  - DTO 创建失败 → ScraperParsingError
  - 日期解析失败 → 记录警告并继续（不中断）

✅ scrape() 方法：
  - 捕获并分类三种错误：验证错误、解析错误、其他
  - 详细的日志记录（错误类型统计）
  - 致命错误向上传递，非致命错误跳过
```

**测试更新:**
```python
# tests/test_seek_adapter.py - 更新测试
✅ test_transform_job_missing_id()     # 验证 ScraperValidationError
✅ test_transform_job_missing_title()  # 验证 ScraperValidationError
```

**成功标准:**
- ✅ 定义 11 个自定义异常类（超出预期 3-5 个）
- ✅ 在 SeekAdapter 中全面使用
- ✅ 更新单元测试（2 个测试验证异常行为）
- ✅ 所有测试通过（92/92 = 100%）

**实现亮点:**
- 完整的异常层次结构（基类 + 继承）
- 每个异常类携带上下文信息（platform, field, status_code 等）
- `classify_http_error()` 辅助函数自动分类 HTTP 错误
- 错误日志包含统计信息（验证错误、解析错误、其他）

**收益:**
- ✅ 更精准的错误日志（区分 11 种错误类型）
- ✅ 更好的 API 响应（返回具体错误信息）
- ✅ 便于调试和问题排查
- ✅ 展示错误处理的深度理解和最佳实践

---

#### 1.3 地点解析增强 ✅

**状态:** 已完成
**实际时间:** 30 分钟
**完成时间:** 2025-12-21

**任务描述:**
- 当前 `parse_location()` 只支持简单格式（"Sydney, NSW"）
- 无法处理复杂格式（"Toowoomba & Darling Downs QLD"）

**已完成任务:**
```python
# app/utils/location_parser.py - 增强地点解析（从 54 行 → 136 行）
✅ 支持 & 连接的多地点：
   - "Toowoomba & Darling Downs QLD" → ("QLD", "Toowoomba")
   - "Brisbane & Gold Coast, QLD" → ("QLD", "Brisbane")

✅ 支持 Greater 前缀：
   - "Greater Sydney, NSW" → ("NSW", "Sydney")
   - "Greater Sydney Area" → (None, "Sydney")

✅ 支持 Remote 特殊情况：
   - "Remote - Australia" → ("", "Remote")
   - "Remote, NSW" → ("NSW", "Remote")

✅ 支持 All Australia：
   - "All Australia" → ("", "All Australia")

✅ 支持末尾州缩写格式（无逗号）：
   - "Toowoomba & Darling Downs QLD" → 自动提取 "QLD"
   - 使用 AUSTRALIAN_STATES 常量验证州缩写

✅ 新增工具函数：
   - _remove_greater_prefix() - 移除 "Greater " 前缀
```

**测试覆盖:**
```python
# tests/test_location_parser.py - 新增 8 个测试
✅ test_parse_location_with_ampersand()         # & 连接 + 末尾州缩写
✅ test_parse_location_with_ampersand_comma()   # & 连接 + 逗号分隔
✅ test_parse_location_greater_prefix()          # Greater 前缀（无州）
✅ test_parse_location_greater_with_state()      # Greater 前缀 + 州
✅ test_parse_location_remote()                  # Remote - Australia
✅ test_parse_location_remote_with_state()       # Remote, NSW
✅ test_parse_location_all_australia()           # All Australia
✅ test_parse_location_multiple_regions()        # 多地区
```

**成功标准:**
- ✅ 支持 "&" 连接的多地点（取第一个）
- ✅ 支持 "Greater" 前缀自动移除
- ✅ 支持 "Remote" 和 "All Australia" 特殊情况
- ✅ 新增 8 个单元测试
- ✅ 所有测试通过（100/100 = 100%）

**测试覆盖提升:**
- 总测试数：92 → 100 (+8)
- location_parser 测试：6 → 14 (+8)
- 执行时间：0.40 秒
- 通过率：100%

**实现亮点:**
- 渐进式解析：逗号分隔 → 末尾州缩写 → 特殊格式
- 灵活的格式支持（有无逗号均可）
- 澳大利亚州/领地缩写验证（8 个州）
- 保持向后兼容（原有 6 个测试全部通过）

**收益:**
- ✅ 提升数据质量（地点字段更准确，覆盖复杂格式）
- ✅ 减少数据清洗工作
- ✅ 较小改动，收益显著

---

### P2 - 性能优化 (Nice-to-Have)

#### 2.1 缓存机制 🔖

**状态:** 待评估
**预计时间:** 2-3 小时
**优先级:** 中（根据实际使用情况评估）

**任务描述:**
- 当前每次搜索都调用外部 API（SEEK/Indeed）
- 相同搜索条件重复调用浪费资源，可能被限流

**方案设计:**

**选项 A: 简单内存缓存（推荐用于学习/测试）**
```python
# app/services/cache_service.py
class SimpleCache:
    """内存缓存，适合单机部署"""

    def __init__(self, ttl_minutes=30):
        self._cache = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[List[JobPostingDTO]]:
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return data
        return None

    def set(self, key: str, value: List[JobPostingDTO]):
        self._cache[key] = (value, datetime.now())

# 使用方式
cache = SimpleCache(ttl_minutes=30)

@app.post("/scrape/seek")
def scrape_seek(request: ScrapeRequest):
    cache_key = generate_cache_key(request.keywords, request.location)
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"缓存命中: {cache_key}")
        return {"jobs": cached, "from_cache": True}

    jobs = adapter.scrape(request)
    cache.set(cache_key, jobs)
    return {"jobs": jobs, "from_cache": False}
```

**选项 B: Redis 缓存（推荐用于生产环境）**
```python
# app/services/redis_cache.py
import redis
import json

class RedisCache:
    """Redis 缓存，适合分布式部署"""

    def __init__(self, redis_url: str, ttl_seconds=1800):
        self.client = redis.from_url(redis_url)
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[List[JobPostingDTO]]:
        data = self.client.get(key)
        if data:
            return [JobPostingDTO(**job) for job in json.loads(data)]
        return None

    def set(self, key: str, value: List[JobPostingDTO]):
        serialized = json.dumps([job.dict() for job in value])
        self.client.setex(key, self.ttl, serialized)

# 配置（添加到 .env）
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=1800  # 30 分钟
```

**实施步骤:**
1. [ ] 实现 SimpleCache 类（先简单实现）
2. [ ] 添加缓存 key 生成逻辑（MD5 hash）
3. [ ] 在 FastAPI 端点中集成
4. [ ] 测试缓存命中率
5. [ ] （可选）升级为 Redis 缓存

**成功标准:**
- [ ] 相同搜索条件返回缓存数据
- [ ] TTL 过期后自动刷新
- [ ] 添加缓存统计（命中率、缓存大小）

**收益:**
- 减少 50-80% 的外部 API 调用（假设有重复搜索）
- 降低被限流风险
- 提升响应速度（缓存响应 < 50ms vs API 响应 1-3s）

**权衡分析:**
- **何时实施?** 如果同一搜索条件频繁重复（如演示、测试），立即实施
- **何时延后?** 如果每次搜索条件都不同，缓存收益低，可延后

---

#### 2.2 并发抓取 🔖

**状态:** 待评估
**预计时间:** 2-3 小时
**优先级:** 低（当前单次抓取够快）

**任务描述:**
- 当前抓取是串行的（一个接一个）
- 如果需要同时抓取多个数据源，性能较慢

**方案设计:**
```python
# app/services/concurrent_scraper.py
import asyncio
from typing import List

class ConcurrentScraper:
    """并发抓取多个数据源"""

    async def scrape_all(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        tasks = [
            self._scrape_indeed(request),
            self._scrape_seek(request),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        jobs = []
        for result in results:
            if isinstance(result, list):
                jobs.extend(result)
            else:
                logger.error(f"抓取失败: {result}")

        return jobs

    async def _scrape_indeed(self, request: ScrapeRequest):
        adapter = IndeedAdapter()
        return await asyncio.to_thread(adapter.scrape, request)

    async def _scrape_seek(self, request: ScrapeRequest):
        adapter = SeekAdapter()
        return await asyncio.to_thread(adapter.scrape, request)

# FastAPI 端点
@app.post("/scrape/all")
async def scrape_all_sources(request: ScrapeRequest):
    scraper = ConcurrentScraper()
    jobs = await scraper.scrape_all(request)
    return {"jobs": jobs, "count": len(jobs)}
```

**实施步骤:**
1. [ ] 创建 ConcurrentScraper 类
2. [ ] 使用 asyncio.gather 并发调用
3. [ ] 处理部分失败情况（一个源失败不影响其他）
4. [ ] 性能测试（对比串行 vs 并发）

**成功标准:**
- [ ] 同时抓取 2 个源比串行快 40-60%
- [ ] 单个源失败不影响其他源
- [ ] 日志记录每个源的耗时

**收益:**
- 提升多源抓取性能（2 个源 3s → 1.5s）
- 更好的用户体验

**权衡分析:**
- **何时实施?** 如果需要同时抓取 3+ 个数据源
- **何时延后?** 如果只使用单一数据源，收益不大

---

#### 2.3 批量抓取优化 🔖

**状态:** 待评估
**预计时间:** 2 小时
**优先级:** 低

**任务描述:**
- 当前 API 只支持单次抓取（max_results=50）
- 如果需要抓取 200 个结果，需要调用 4 次 API

**方案设计:**
```python
# 支持分页抓取
@app.post("/scrape/seek/batch")
def scrape_seek_batch(request: ScrapeRequest):
    """
    批量抓取，支持分页

    request.max_results = 200 → 自动分 4 次调用（每次 50）
    """
    adapter = SeekAdapter()
    total_wanted = request.max_results or 50
    batch_size = 50  # SEEK API 每页最多 50

    all_jobs = []
    for page in range(1, (total_wanted // batch_size) + 1):
        batch_request = ScrapeRequest(
            keywords=request.keywords,
            location=request.location,
            max_results=batch_size
        )
        jobs = adapter.scrape(batch_request)
        all_jobs.extend(jobs)

        if len(jobs) < batch_size:
            break  # 没有更多结果

    return {"jobs": all_jobs[:total_wanted], "count": len(all_jobs)}
```

**成功标准:**
- [ ] 支持抓取超过 50 个结果
- [ ] 自动分页调用
- [ ] 添加进度反馈（如 WebSocket）

**收益:**
- 支持大规模数据采集
- 适合后台任务（Hangfire ScrapeJob）

---

#### 2.4 结构化日志 🔖

**状态:** 待评估
**预计时间:** 1 小时
**优先级:** 低（当前日志够用）

**任务描述:**
- 当前使用 Python logging（文本格式）
- 难以聚合和分析（如统计成功率、平均耗时）

**方案设计:**
```python
# 使用 structlog 实现结构化日志
import structlog

logger = structlog.get_logger()

# 记录抓取事件
logger.info(
    "scrape_completed",
    platform="seek",
    keywords="plumber",
    results_count=5,
    duration_ms=1234,
    cache_hit=False
)

# 输出格式（JSON）
{
  "event": "scrape_completed",
  "platform": "seek",
  "keywords": "plumber",
  "results_count": 5,
  "duration_ms": 1234,
  "cache_hit": false,
  "timestamp": "2025-12-20T10:30:00Z"
}
```

**集成 Elasticsearch（可选）:**
```python
# 将日志发送到 Elasticsearch
# 可以使用 Kibana 可视化分析
# - 按平台统计成功率
# - 按关键词统计热门搜索
# - 监控 API 响应时间
```

**成功标准:**
- [ ] 所有日志使用结构化格式
- [ ] 可以按字段过滤和聚合
- [ ] （可选）集成 Elasticsearch/Datadog

**收益:**
- 更好的可观测性（Observability）
- 快速排查问题
- 数据驱动决策（如识别热门搜索）

---

#### 2.5 监控和告警 🔖

**状态:** 待评估
**预计时间:** 2 小时
**优先级:** 低（适合生产环境）

**任务描述:**
- 当前没有监控系统
- 无法知道 API 成功率、响应时间等指标

**方案设计:**
```python
# 使用 Prometheus + Grafana

# 1. 添加 metrics 端点
from prometheus_client import Counter, Histogram, generate_latest

scrape_requests_total = Counter(
    "scrape_requests_total",
    "Total scrape requests",
    ["platform", "status"]
)

scrape_duration_seconds = Histogram(
    "scrape_duration_seconds",
    "Scrape duration",
    ["platform"]
)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# 2. 在适配器中记录指标
def scrape(self, request: ScrapeRequest):
    start_time = time.time()
    try:
        jobs = self._do_scrape(request)
        scrape_requests_total.labels(platform="seek", status="success").inc()
        return jobs
    except Exception as e:
        scrape_requests_total.labels(platform="seek", status="error").inc()
        raise
    finally:
        duration = time.time() - start_time
        scrape_duration_seconds.labels(platform="seek").observe(duration)
```

**Grafana 仪表板:**
- 总请求数（按平台）
- 成功率（成功/总数）
- 平均响应时间
- 缓存命中率

**成功标准:**
- [ ] Prometheus 正确收集指标
- [ ] Grafana 仪表板可视化
- [ ] 设置告警规则（如成功率 < 90%）

**收益:**
- 实时监控系统健康度
- 快速发现异常（如 API 限流）
- 展示 SRE/DevOps 能力

---

### P3 - 功能扩展 (Future)

#### 3.1 新数据源 - LinkedIn 🔖

**状态:** 待调研
**预计时间:** 4-6 小时
**优先级:** V2 功能

**任务描述:**
- 接入 LinkedIn Jobs API 或爬虫
- 扩展职位数据覆盖范围

**调研任务:**
1. [ ] LinkedIn 是否有公开 API？
2. [ ] 是否需要使用爬虫？（法律风险评估）
3. [ ] 数据格式和字段映射

**实施步骤:**
1. [ ] 创建 LinkedInAdapter 类
2. [ ] 实现 scrape() 方法
3. [ ] 数据转换为 JobPostingDTO
4. [ ] 添加单元测试
5. [ ] FastAPI 端点集成

**收益:**
- 更多职位数据
- 展示架构扩展性（adapter 模式的优势）

---

#### 3.2 新数据源 - Glassdoor 🔖

**状态:** 待调研
**预计时间:** 4-6 小时
**优先级:** V2 功能

**任务描述:**
- 接入 Glassdoor Jobs API 或爬虫
- 特色数据：公司评分、薪资透明度

**调研任务:**
同 LinkedIn

---

#### 3.3 AI 语义搜索 🔖

**状态:** 待调研
**预计时间:** 8-12 小时
**优先级:** V2 功能（需要数据库支持）

**任务描述:**
- 当前搜索是关键词匹配（"plumber" 只匹配 "plumber"）
- AI 语义搜索可以匹配相似职位（"plumber" → "pipefitter", "gasfitter"）

**方案设计:**
```python
# 1. 使用 pgvector 存储职位嵌入
# PostgreSQL 扩展，支持向量搜索

# 2. 生成职位嵌入
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(job.title + " " + job.description)

# 3. 存储到数据库
# jobs 表添加 embedding 列（vector 类型）

# 4. 语义搜索
query_embedding = model.encode("plumber jobs")
similar_jobs = db.query(
    "SELECT * FROM jobs ORDER BY embedding <-> %s LIMIT 10",
    query_embedding
)
```

**实施步骤:**
1. [ ] 调研 pgvector 或 Elasticsearch
2. [ ] 选择嵌入模型（SentenceTransformer）
3. [ ] 生成所有职位的嵌入
4. [ ] 实现语义搜索 API
5. [ ] 性能测试（向量搜索 vs 关键词搜索）

**收益:**
- 更智能的搜索体验
- 展示 AI/ML 能力
- 学习向量数据库

**前置条件:**
- 需要 .NET 后端支持（pgvector 扩展）
- 需要一定量的职位数据（至少 1000+）

---

## 🏗️ .NET 后端服务优化任务

### P1 - 集成测试 (Important)

#### 1.1 Python ↔ .NET 集成测试 ⏳

**状态:** 待开始
**预计时间:** 2-3 小时
**优先级:** 高（核心功能验证）

**任务描述:**
- 验证 Python FastAPI 和 .NET Backend 的数据流
- 确保去重逻辑和标准化正确工作

**测试场景:**
```csharp
// 场景 1: 正常抓取和存储
[Test]
public async Task TestIngestionPipeline_Success()
{
    // 1. 调用 Python API 抓取职位
    var jobs = await _scrapeApiClient.ScrapeSeekAsync("plumber", maxResults: 5);

    // 2. 验证返回数据
    Assert.That(jobs.Count, Is.GreaterThan(0));

    // 3. 通过 IngestionPipeline 处理
    await _ingestionPipeline.IngestJobsAsync(jobs);

    // 4. 验证数据库存储
    var dbJobs = await _jobRepository.GetRecentJobsAsync(limit: 10);
    Assert.That(dbJobs.Count, Is.GreaterThan(0));
}

// 场景 2: 去重逻辑
[Test]
public async Task TestDeduplication_SameJob()
{
    // 1. 第一次摄取
    await _ingestionPipeline.IngestJobsAsync(jobs);
    var count1 = await _jobRepository.CountAsync();

    // 2. 第二次摄取相同数据
    await _ingestionPipeline.IngestJobsAsync(jobs);
    var count2 = await _jobRepository.CountAsync();

    // 3. 验证没有重复存储
    Assert.That(count1, Is.EqualTo(count2));
}

// 场景 3: 数据标准化
[Test]
public async Task TestNormalization_LocationState()
{
    // 验证地点字段正确分离（Suburb vs State）
    var job = await _jobRepository.GetByIdAsync(jobId);
    Assert.That(job.LocationState, Is.EqualTo("NSW"));
    Assert.That(job.LocationSuburb, Is.EqualTo("Sydney"));
}
```

**成功标准:**
- [ ] 至少 5 个集成测试覆盖核心流程
- [ ] 所有测试通过
- [ ] 验证去重逻辑正确

**收益:**
- 确保系统端到端可用
- 发现潜在的数据转换问题
- 面试时可以展示完整的测试策略

---

### P2 - 性能优化 (Nice-to-Have)

#### 2.1 .NET 后端缓存 🔖

**状态:** 待评估
**预计时间:** 2-3 小时
**优先级:** 低（Python 层缓存已足够）

**任务描述:**
- 在 .NET 后端添加 Redis 缓存
- 缓存查询 API 的响应（如热门搜索）

**方案设计:**
```csharp
// 使用 IDistributedCache
public class JobsController : ControllerBase
{
    private readonly IDistributedCache _cache;

    [HttpGet]
    public async Task<IActionResult> SearchJobs([FromQuery] JobSearchRequest request)
    {
        var cacheKey = $"search:{request.Trade}:{request.Location}";

        // 尝试从缓存获取
        var cachedData = await _cache.GetStringAsync(cacheKey);
        if (cachedData != null)
        {
            var cachedJobs = JsonSerializer.Deserialize<List<JobDto>>(cachedData);
            return Ok(new { jobs = cachedJobs, fromCache = true });
        }

        // 从数据库查询
        var jobs = await _jobRepository.SearchJobsAsync(request);

        // 缓存结果（5 分钟）
        var options = new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5)
        };
        await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(jobs), options);

        return Ok(new { jobs, fromCache = false });
    }
}
```

**成功标准:**
- [ ] 配置 Redis
- [ ] 热门查询响应时间 < 50ms
- [ ] 添加缓存统计端点

**收益:**
- 减轻数据库压力
- 提升查询 API 性能

**权衡:**
- 如果查询不频繁，收益有限
- 建议先完成 Python 层缓存

---

#### 2.2 数据库索引优化 🔖

**状态:** 待评估
**预计时间:** 1 小时
**优先级:** 低（数据量小时不明显）

**任务描述:**
- 为常用查询字段添加索引
- 提升搜索性能

**方案设计:**
```csharp
// 在 EF Core 配置中添加索引
modelBuilder.Entity<JobPosting>()
    .HasIndex(j => j.Trade);

modelBuilder.Entity<JobPosting>()
    .HasIndex(j => j.LocationState);

modelBuilder.Entity<JobPosting>()
    .HasIndex(j => new { j.Trade, j.LocationState });  // 复合索引

modelBuilder.Entity<JobPosting>()
    .HasIndex(j => j.CreatedAt);
```

**性能测试:**
```sql
-- 测试查询性能
EXPLAIN ANALYZE
SELECT * FROM JobPostings
WHERE Trade = 'Plumber' AND LocationState = 'NSW'
ORDER BY CreatedAt DESC
LIMIT 20;

-- 对比有无索引的执行时间
```

**成功标准:**
- [ ] 添加 3-5 个索引
- [ ] 查询性能提升 50%+
- [ ] 验证索引有效（EXPLAIN ANALYZE）

**收益:**
- 数据量增长后保持性能
- 学习数据库优化

**权衡:**
- 数据量 < 10,000 时收益不大
- 索引过多会影响写入性能

---

### P3 - 功能扩展 (Future)

#### 3.1 用户系统（V2 功能）🔖

**状态:** V2 规划
**预计时间:** 8-12 小时
**优先级:** V2

**任务列表:**
- [ ] 用户注册/登录（JWT 认证）
- [ ] 保存的工作（SavedJobs 表）
- [ ] 工作提醒（JobAlerts 表）
- [ ] 用户权限管理

**详细规划:** 等 V1 完成后制定

---

#### 3.2 前端应用（V2 功能）🔖

**状态:** V2 规划
**预计时间:** 20-30 小时
**优先级:** V2

**技术栈:**
- React + TypeScript
- Material-UI / Ant Design
- React Query（数据获取）

**详细规划:** 等 V1 完成后制定

---

## 📊 实施建议

### 当前阶段（2025-12-20）

**已完成:**
✅ Python 爬虫核心功能（69 个测试通过）
✅ .NET 后端 API（8 个端点）
✅ 数据库架构

**下一步（推荐顺序）:**

**阶段 1: 验证集成（P1，必做）**
1. ⏳ .NET 集成测试（2-3 小时）
   - 验证 Python → .NET → PostgreSQL 数据流
   - 确保去重和标准化正确
2. ⏳ SeekAdapter 单元测试（1-2 小时）
   - 补充缺失的测试覆盖

**阶段 2: 质量提升（P1，建议做）**
3. ⏳ 错误处理细化（1 小时）
   - 定义自定义异常类
4. ⏳ 地点解析增强（30 分钟）
   - 处理复杂格式

**阶段 3: 性能优化（P2，可选）**
5. 🔖 缓存机制（2-3 小时）
   - 如果有重复搜索需求，实施 SimpleCache
6. 🔖 结构化日志（1 小时）
   - 如果需要分析使用数据

**阶段 4: 功能扩展（P3，V2 计划）**
7. 🔖 新数据源（LinkedIn/Glassdoor）
8. 🔖 AI 语义搜索
9. 🔖 用户系统 + 前端

---

### 时间成本总览

| 优先级 | 总任务数 | 预计总时间 | 建议实施时机 |
|--------|----------|------------|--------------|
| P1 | 4 | 5-7 小时 | 立即（集成前） |
| P2 | 7 | 12-16 小时 | V1 稳定后 |
| P3 | 5 | 40-60 小时 | V2 版本 |

---

### 面试准备建议

**展示项目时，按优先级讲述:**

1. **P0（核心功能）:** "我实现了完整的职位爬虫系统，支持 Indeed 和 SEEK 两个数据源..."
2. **P1（质量保证）:** "我非常注重代码质量，编写了 69 个单元测试，覆盖所有工具函数..."
3. **P2（改进空间）:** "如果有更多时间，我会添加缓存机制来优化性能..."
4. **P3（未来愿景）:** "未来可以扩展到 LinkedIn，甚至实现 AI 语义搜索..."

**回答"如果重新做"问题:**

> "如果重新做，我会优先完成 P1 的 SeekAdapter 单元测试和错误处理细化，因为这直接影响系统的稳定性和可维护性。P2 的缓存机制可以根据实际使用情况评估，如果搜索条件重复度高，就值得投入时间实现。"

---

## 🔗 相关文档

- [OPTIMIZATION_PRIORITIES_GUIDE.md](../tutorials/OPTIMIZATION_PRIORITIES_GUIDE.md) - 优先级概念学习
- [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) - 技术选型和权衡分析
- [NEXT_STEPS.md](./NEXT_STEPS.md) - 总体开发路线图
- [TDD_DEVELOPMENT_GUIDE.md](../tutorials/TDD_DEVELOPMENT_GUIDE.md) - 测试驱动开发方法

---

**最后更新:** 2025-12-20
**维护者:** Claude Code
**状态:** 持续更新（每个阶段完成后更新进度）
