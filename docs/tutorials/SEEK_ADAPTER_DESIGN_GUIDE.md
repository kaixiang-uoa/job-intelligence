# SEEK Adapter 设计与开发指南

> **教学文档** - Phase 3.2 SeekAdapter 实现
> **创建日期:** 2025-12-19
> **适用于:** Python 爬虫服务 - SEEK 适配器开发

---

## 1. 整体架构设计

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Endpoint                        │
│                   POST /scrape/seek                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SeekAdapter                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  scrape(keywords, location, results_wanted)          │  │
│  │  └─> List[JobPostingDTO]                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  私有方法（职责分离）:                                │  │
│  │  • _build_payload()        构建 API 请求体           │  │
│  │  • _call_seek_api()        调用 SEEK API            │  │
│  │  • _transform_job()        转换单个职位               │  │
│  │  • _extract_description()  提取职位描述               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SEEK Internal API                          │
│  https://chalice-experience-api.seek.com/graphql            │
│                                                             │
│  Request:                                                   │
│  • Headers: User-Agent, seek-request-brand, etc.           │
│  • Payload: GraphQL query with variables                   │
│                                                             │
│  Response:                                                  │
│  • data.jobs (array of job objects)                        │
│  • data.totalCount                                         │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              工具函数层（复用 5 个函数）                      │
│  • parse_location()           地点解析                      │
│  • extract_trade()            Trade 提取                    │
│  • normalize_employment_type() 工作类型标准化                │
│  • parse_salary_range()       薪资解析 ✅ NEW              │
│  • clean_html()               HTML 清理 ✅ NEW              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   JobPostingDTO                             │
│  统一的数据模型（所有平台返回相同格式）                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 设计原则

1. **继承复用**: 继承 `BaseJobAdapter`，复用公共接口
2. **职责分离**: 每个方法只做一件事，便于测试和维护
3. **工具函数复用**: 与 IndeedAdapter 共享 5 个工具函数
4. **数据统一**: 返回统一的 `JobPostingDTO`
5. **容错处理**: 三层错误处理，单个失败不影响整体

---

## 2. SEEK API 研究

### 2.1 API 端点

```
POST https://chalice-experience-api.seek.com/graphql
```

### 2.2 必需的 Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "seek-request-brand": "JobStreet",
    "seek-request-country": "AU",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

**关键点:**
- `seek-request-brand`: 可以是 "JobStreet" 或 "SEEK"
- `seek-request-country`: 必须是 "AU"（澳大利亚）
- User-Agent: 模拟浏览器请求

### 2.3 请求 Payload 结构

```python
payload = {
    "query": """
        query searchJobs($where: SearchJobsInput!) {
            jobs(where: $where) {
                id
                title
                advertiser { name }
                salary { label }
                location { label }
                workTypes
                teaser
                createdAt
                ... 更多字段
            }
            totalCount
        }
    """,
    "variables": {
        "where": {
            "keywords": ["plumber"],
            "page": 1,
            "pageSize": 50,
            "classifications": [
                {
                    "id": "6251",      # Trades & Services
                    "subClassifications": ["6315"]  # Plumbing
                }
            ],
            "seekSelectOnly": False,
            "salaryCurrency": "AUD",
            "workTypes": ["Full Time", "Part Time", "Contract"]
        }
    }
}
```

**关键字段说明:**
- `keywords`: 搜索关键词列表
- `classifications`: 职位分类（6251 = Trades & Services）
- `subClassifications`: 子分类（6315 = Plumbing 等）
- `pageSize`: 每页结果数量（最大 50）
- `workTypes`: 工作类型过滤

### 2.4 响应数据结构

```json
{
    "data": {
        "jobs": [
            {
                "id": "76485839",
                "title": "Experienced Plumber",
                "advertiser": {
                    "name": "ABC Plumbing"
                },
                "salary": {
                    "label": "$70,000 - $80,000 per year"
                },
                "location": {
                    "label": "Sydney NSW"
                },
                "workTypes": ["Full Time"],
                "teaser": "<p>We are looking for...</p>",
                "createdAt": "2025-12-15T00:00:00Z"
            }
        ],
        "totalCount": 245
    }
}
```

---

## 3. SeekAdapter 类设计

### 3.1 类继承关系

```python
class SeekAdapter(BaseJobAdapter):
    """
    SEEK 职位数据适配器

    继承自 BaseJobAdapter，实现 scrape() 方法
    使用 SEEK 内部 GraphQL API 获取职位数据
    """

    def __init__(self):
        super().__init__()
        self.api_url = "https://chalice-experience-api.seek.com/graphql"
        self.headers = {...}  # 固定的请求头
```

### 3.2 公共方法

#### 3.2.1 scrape() - 主入口

```python
def scrape(
    self,
    keywords: str,
    location: Optional[str] = None,
    results_wanted: int = 50
) -> List[JobPostingDTO]:
    """
    抓取 SEEK 职位数据

    Args:
        keywords: 搜索关键词（例如 "plumber"）
        location: 地点（可选，SEEK 会在 API 层面处理）
        results_wanted: 期望结果数量（默认 50，最大 50）

    Returns:
        List[JobPostingDTO]: 标准化的职位列表

    流程:
        1. 构建 GraphQL 请求体 (_build_payload)
        2. 调用 SEEK API (_call_seek_api)
        3. 转换每个职位 (_transform_job)
        4. 返回 JobPostingDTO 列表
    """
```

**为什么这样设计?**
- 符合 `BaseJobAdapter` 接口，与 `IndeedAdapter` 保持一致
- 参数简单，调用者不需要了解 SEEK API 细节
- 返回统一的 `JobPostingDTO`，便于后续处理

### 3.3 私有方法（职责分离）

#### 3.3.1 _build_payload() - 构建请求体

```python
def _build_payload(
    self,
    keywords: str,
    results_wanted: int
) -> dict:
    """
    构建 SEEK GraphQL API 请求体

    Returns:
        dict: 包含 query 和 variables 的请求体

    职责:
        • 将关键词转换为列表
        • 设置 Trades 分类 ID (6251, 6315)
        • 构建 GraphQL query 字符串
        • 组装 variables 对象
    """
```

**为什么需要单独的方法?**
- GraphQL payload 结构复杂，单独抽取便于测试
- 分类 ID 逻辑可能会扩展（支持更多 trade）
- 便于调试和修改 API 请求格式

#### 3.3.2 _call_seek_api() - 调用 API

```python
def _call_seek_api(self, payload: dict) -> dict:
    """
    调用 SEEK GraphQL API

    Args:
        payload: 请求体（包含 query 和 variables）

    Returns:
        dict: API 响应的 data 部分

    异常处理:
        • requests.RequestException: 网络错误
        • ValueError: 响应格式错误
        • KeyError: 缺少预期字段
    """
```

**为什么需要单独的方法?**
- HTTP 调用逻辑与业务逻辑分离
- 便于 mock 测试（不需要真实调用 API）
- 统一处理网络错误和响应验证

#### 3.3.3 _transform_job() - 转换单个职位

```python
def _transform_job(self, job_data: dict) -> Optional[JobPostingDTO]:
    """
    将 SEEK API 返回的单个职位转换为 JobPostingDTO

    Args:
        job_data: SEEK API 返回的职位对象

    Returns:
        JobPostingDTO or None（转换失败时返回 None）

    职责:
        • 提取基本字段（title, company, id）
        • 解析薪资范围（parse_salary_range）
        • 清理 HTML 描述（clean_html）
        • 解析地点（parse_location）
        • 提取 trade（extract_trade）
        • 标准化工作类型（normalize_employment_type）
    """
```

**为什么需要单独的方法?**
- 数据转换逻辑复杂，单独抽取便于测试
- 单个职位转换失败不应影响其他职位
- 调用了 5 个工具函数，逻辑清晰

#### 3.3.4 _extract_description() - 提取描述

```python
def _extract_description(self, job_data: dict) -> Optional[str]:
    """
    从 SEEK API 数据中提取职位描述

    优先级:
        1. job_data.get("teaser")     # HTML 片段
        2. job_data.get("content")    # 完整 HTML
        3. None

    处理:
        • 使用 clean_html() 清理 HTML
        • 限制长度（前 500 字符）
    """
```

**为什么需要单独的方法?**
- SEEK 可能返回不同的描述字段
- 统一处理 HTML 清理逻辑
- 便于调整描述提取策略

---

## 4. 数据转换流程

### 4.1 SEEK API → JobPostingDTO 映射表

| JobPostingDTO 字段 | SEEK API 字段 | 处理方式 | 工具函数 |
|-------------------|--------------|---------|---------|
| **id** | `job_data["id"]` | 直接使用 SEEK 职位 ID | - |
| **title** | `job_data["title"]` | 直接使用 | - |
| **company** | `job_data["advertiser"]["name"]` | 安全提取（可能为空） | - |
| **location** | `job_data["location"]["label"]` | 例如 "Sydney NSW" | - |
| **city** | 从 location 解析 | "Sydney" | `parse_location()` |
| **state** | 从 location 解析 | "NSW" | `parse_location()` |
| **country** | 固定值 | "Australia" | - |
| **description** | `teaser` 或 `content` | HTML 清理 | `clean_html()` |
| **min_amount** | `salary.label` | 解析薪资范围 | `parse_salary_range()` |
| **max_amount** | `salary.label` | 解析薪资范围 | `parse_salary_range()` |
| **currency** | 固定值 | "AUD" | - |
| **interval** | 固定值 | "yearly" | - |
| **job_type** | `workTypes[0]` | "Full Time" → "fulltime" | `normalize_employment_type()` |
| **trade** | 从 title 提取 | "plumber" → "plumbing" | `extract_trade()` |
| **date_posted** | `createdAt` | ISO 8601 字符串 | - |
| **job_url** | 拼接 | `f"https://www.seek.com.au/job/{id}"` | - |

### 4.2 转换示例

**输入（SEEK API）:**
```json
{
    "id": "76485839",
    "title": "Experienced Plumber - Sydney",
    "advertiser": { "name": "ABC Plumbing" },
    "salary": { "label": "$70,000 - $80,000 per year" },
    "location": { "label": "Sydney NSW" },
    "workTypes": ["Full Time"],
    "teaser": "<p>We are looking for an <strong>experienced plumber</strong>...</p>",
    "createdAt": "2025-12-15T00:00:00Z"
}
```

**输出（JobPostingDTO）:**
```python
JobPostingDTO(
    id="76485839",
    title="Experienced Plumber - Sydney",
    company="ABC Plumbing",
    location="Sydney NSW",
    city="Sydney",
    state="NSW",
    country="Australia",
    description="We are looking for an experienced plumber...",  # HTML 已清理
    min_amount=70000.0,
    max_amount=80000.0,
    currency="AUD",
    interval="yearly",
    job_type="fulltime",
    trade="plumbing",  # 从 title 提取
    date_posted="2025-12-15T00:00:00Z",
    job_url="https://www.seek.com.au/job/76485839"
)
```

---

## 5. HTTP 请求处理

### 5.1 使用 requests 库

```python
import requests

response = requests.post(
    url=self.api_url,
    headers=self.headers,
    json=payload,
    timeout=30  # 30 秒超时
)

response.raise_for_status()  # 抛出 4xx/5xx 错误
data = response.json()
```

### 5.2 为什么选择 requests？

| 特性 | requests | httpx | aiohttp |
|------|---------|-------|---------|
| **同步支持** | ✅ 原生 | ✅ 原生 | ❌ 仅异步 |
| **API 简洁** | ✅ 非常简洁 | ✅ 简洁 | ⚠️ 复杂 |
| **依赖少** | ✅ 最少 | ⚠️ 中等 | ⚠️ 中等 |
| **成熟度** | ✅ 非常成熟 | ⚠️ 较新 | ✅ 成熟 |

**结论**: 当前阶段使用 `requests`，简单可靠

### 5.3 错误处理

```python
try:
    response = requests.post(...)
    response.raise_for_status()
    data = response.json()

    if "data" not in data:
        raise ValueError("API 响应缺少 'data' 字段")

    return data["data"]

except requests.Timeout:
    logger.error("SEEK API 超时")
    raise
except requests.RequestException as e:
    logger.error(f"SEEK API 请求失败: {e}")
    raise
except ValueError as e:
    logger.error(f"SEEK API 响应格式错误: {e}")
    raise
```

---

## 6. 错误处理策略

### 6.1 三层错误保护

```
第 1 层: 参数验证（scrape 方法入口）
    ↓
    • keywords 不能为空
    • results_wanted 范围检查 (1-50)
    ↓
第 2 层: API 调用错误（_call_seek_api）
    ↓
    • 网络超时（Timeout）
    • HTTP 错误（4xx/5xx）
    • 响应格式错误（缺少字段）
    ↓
第 3 层: 数据转换错误（_transform_job）
    ↓
    • 单个职位转换失败 → 记录日志，返回 None
    • 过滤掉 None，不影响其他职位
```

### 6.2 容错原则

**部分失败容忍:**
- API 返回 50 个职位，其中 3 个转换失败
- 结果: 返回 47 个成功的 JobPostingDTO
- 日志: WARNING - 3 个职位转换失败

**完全失败快速返回:**
- API 调用失败 → 立即抛出异常
- 参数无效 → 立即抛出 ValueError

### 6.3 日志记录

```python
import logging

logger = logging.getLogger(__name__)

# 信息日志
logger.info(f"开始抓取 SEEK 职位: {keywords}, 期望数量: {results_wanted}")

# 警告日志
logger.warning(f"职位 {job_id} 转换失败: {e}")

# 错误日志
logger.error(f"SEEK API 调用失败: {e}")
```

---

## 7. 配置管理

### 7.1 环境变量（可选）

```python
# .env
SEEK_API_URL=https://chalice-experience-api.seek.com/graphql
SEEK_REQUEST_BRAND=JobStreet
SEEK_REQUEST_COUNTRY=AU
SEEK_TIMEOUT=30
```

### 7.2 Pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    seek_api_url: str = "https://chalice-experience-api.seek.com/graphql"
    seek_request_brand: str = "JobStreet"
    seek_request_country: str = "AU"
    seek_timeout: int = 30

    class Config:
        env_file = ".env"
```

**当前阶段**: 硬编码在适配器中（简单）
**未来优化**: 使用 Settings 管理（灵活）

---

## 8. 与 IndeedAdapter 对比

| 维度 | IndeedAdapter | SeekAdapter |
|------|--------------|-------------|
| **数据源** | JobSpy 库（封装 Indeed API） | SEEK GraphQL API（直接调用） |
| **API 类型** | 第三方库抽象 | 直接 HTTP 调用 |
| **复杂度** | 简单（库已封装） | 中等（需要手动构建请求） |
| **数据格式** | pandas DataFrame | JSON（GraphQL 响应） |
| **转换方式** | 迭代 DataFrame 行 | 迭代 JSON 数组 |
| **工具函数** | 共用 5 个 | 共用 5 个 |
| **代码量** | ~80 行 | ~130-150 行 |
| **错误处理** | 简单（库已处理） | 复杂（手动处理 HTTP） |

**关键差异:**
- IndeedAdapter: 依赖第三方库，简单但依赖外部维护
- SeekAdapter: 直接调用 API，复杂但完全可控

---

## 9. 代码结构预览

```python
# app/adapters/seek_adapter.py (~130-150 行)

class SeekAdapter(BaseJobAdapter):

    def __init__(self):
        # 初始化 API URL 和 Headers
        pass

    def scrape(self, keywords, location, results_wanted) -> List[JobPostingDTO]:
        # 1. 参数验证
        # 2. 构建 payload
        # 3. 调用 API
        # 4. 转换数据
        # 5. 返回结果
        pass

    def _build_payload(self, keywords, results_wanted) -> dict:
        # 构建 GraphQL 请求体
        pass

    def _call_seek_api(self, payload) -> dict:
        # HTTP POST 请求
        # 错误处理
        # 返回 data 部分
        pass

    def _transform_job(self, job_data) -> Optional[JobPostingDTO]:
        # 提取字段
        # 调用 5 个工具函数
        # 返回 JobPostingDTO
        pass

    def _extract_description(self, job_data) -> Optional[str]:
        # 提取 teaser 或 content
        # 调用 clean_html()
        pass
```

---

## 10. 开发步骤建议

### Step 1: 创建文件骨架（5 分钟）
```bash
touch scrape-api/app/adapters/seek_adapter.py
```

### Step 2: 实现 `__init__` 和硬编码配置（10 分钟）
- API URL
- Headers
- GraphQL query 模板

### Step 3: 实现 `_build_payload`（15 分钟）
- 参数转换
- 构建 variables

### Step 4: 实现 `_call_seek_api`（20 分钟）
- HTTP POST 请求
- 错误处理
- 响应验证

### Step 5: 实现 `_extract_description`（10 分钟）
- 提取逻辑
- 调用 clean_html()

### Step 6: 实现 `_transform_job`（30 分钟）
- 字段映射
- 调用 5 个工具函数
- 错误处理

### Step 7: 实现 `scrape` 主方法（20 分钟）
- 参数验证
- 调用私有方法
- 组装结果

### Step 8: 手动测试（20 分钟）
```python
# test_seek_manual.py
adapter = SeekAdapter()
jobs = adapter.scrape("plumber", results_wanted=5)
print(f"抓取到 {len(jobs)} 个职位")
for job in jobs:
    print(job.title, job.company, job.min_amount)
```

**总计**: ~2-3 小时（含调试）

---

## 11. 关键学习点

### 11.1 设计模式
1. **适配器模式**: 将不同 API 转换为统一接口
2. **模板方法**: BaseJobAdapter 定义骨架，子类实现细节
3. **单一职责**: 每个方法只做一件事

### 11.2 Python 技术
1. **类型注解**: `List[JobPostingDTO]`, `Optional[str]`
2. **字典安全访问**: `job_data.get("advertiser", {}).get("name")`
3. **列表推导式**: `[self._transform_job(j) for j in jobs]`
4. **过滤 None**: `[j for j in jobs if j is not None]`

### 11.3 HTTP 编程
1. **GraphQL 请求**: query + variables 结构
2. **Headers 伪装**: User-Agent, seek-request-brand
3. **错误处理**: Timeout, RequestException, HTTP 状态码

### 11.4 数据处理
1. **工具函数组合**: 5 个小函数组合成复杂转换
2. **容错处理**: 部分失败不影响整体
3. **数据清洗**: HTML 清理、薪资解析

---

## 12. 思考题

**问题 1**: 为什么要将 `_build_payload` 单独抽取成方法，而不是直接写在 `scrape` 里？

**问题 2**: 如果 SEEK API 返回 50 个职位，但其中 10 个 `advertiser.name` 为空，应该如何处理？

**问题 3**: 如果未来要支持更多 trade（electrician, carpenter），`_build_payload` 需要如何修改？

**问题 4**: 为什么 `_transform_job` 返回 `Optional[JobPostingDTO]` 而不是直接抛出异常？

**问题 5**: 如果 SEEK API 突然改变响应格式，哪个方法最容易受影响？如何提高健壮性？

---

## 附录: SEEK GraphQL Query 完整示例

```graphql
query searchJobs($where: SearchJobsInput!) {
    jobs(where: $where) {
        id
        title
        advertiser {
            name
        }
        salary {
            label
        }
        location {
            label
        }
        workTypes
        teaser
        content
        createdAt
        classification {
            label
        }
        subClassification {
            label
        }
    }
    totalCount
}
```

**Variables:**
```json
{
    "where": {
        "keywords": ["plumber"],
        "page": 1,
        "pageSize": 50,
        "classifications": [
            {
                "id": "6251",
                "subClassifications": ["6315"]
            }
        ],
        "seekSelectOnly": false,
        "salaryCurrency": "AUD",
        "workTypes": ["Full Time", "Part Time", "Contract", "Casual"]
    }
}
```

---

**文档版本**: 1.0
**下一步**: 理解设计思路后，开始实现 SeekAdapter
**参考文档**: [SEEK_API_COMPARISON.md](../docs/SEEK_API_COMPARISON.md), [SCRAPER_IMPLEMENTATION_PLAN.md](../docs/SCRAPER_IMPLEMENTATION_PLAN.md)
