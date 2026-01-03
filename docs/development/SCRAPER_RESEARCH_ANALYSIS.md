# 爬虫开源项目深度分析报告

> **生成时间:** 2025-12-16
> **分析对象:** JobSpy + SeekSpider
> **目的:** 评估混合架构可行性

---

## 📁 项目概览

### 1. JobSpy（Indeed 等多平台爬虫）

**GitHub:** https://github.com/speedyapply/JobSpy
**Stars:** 2.5k | **最新版本:** v1.1.82 (2025-03-21)

#### 技术栈
```python
Python >= 3.10
requests = 2.31.0
beautifulsoup4 = 4.12.2
pandas = 2.1.0
pydantic = 2.3.0
tls-client = 1.0.1  # 绕过 TLS 指纹识别
markdownify = 1.1.0
```

#### 支持的求职网站
- ✅ Indeed（澳洲完美支持）
- ✅ LinkedIn
- ✅ Glassdoor（澳洲支持）
- ✅ Google Jobs
- ✅ ZipRecruiter
- ⚠️ **不支持 SEEK**

#### 代码结构
```
jobspy/
├── __init__.py              # 主入口，scrape_jobs() 函数
├── model.py                 # Pydantic 数据模型
├── util.py                  # 工具函数
├── indeed/
│   ├── __init__.py          # Indeed 爬虫类
│   ├── constant.py          # GraphQL 查询模板
│   └── util.py              # Indeed 工具函数
├── linkedin/
├── glassdoor/
└── ziprecruiter/
```

#### 核心实现分析

**1. 主函数签名:**
```python
def scrape_jobs(
    site_name: str | list[str] | Site | list[Site] | None = None,
    search_term: str | None = None,
    location: str | None = None,
    distance: int | None = 50,
    is_remote: bool = False,
    job_type: str | None = None,
    results_wanted: int = 15,
    country_indeed: str = "usa",  # 关键！支持 "Australia"
    proxies: list[str] | str | None = None,
    hours_old: int = None,
    **kwargs,
) -> pd.DataFrame
```

**2. Indeed 澳洲支持验证:**
```python
# 从代码看，country_indeed 参数支持以下值：
domain, api_country_code = scraper_input.country.indeed_domain_value

# 澳洲配置示例：
country_indeed='Australia'
# 会映射到: domain='au', base_url='https://au.indeed.com'
```

**3. 并发抓取机制:**
```python
# 使用 ThreadPoolExecutor 并发抓取多个站点
with ThreadPoolExecutor() as executor:
    future_to_site = {
        executor.submit(worker, site): site
        for site in scraper_input.site_type
    }
    for future in as_completed(future_to_site):
        site_value, scraped_data = future.result()
```

**4. Indeed API 调用方式:**
```python
# Indeed 使用 GraphQL API
self.api_url = "https://apis.indeed.com/graphql"

# 查询模板在 constant.py 中定义
job_search_query = """
query GetJobData {{
    jobSearch(
        {what}
        {location}
        {filters}
        limit: {limit}
        {cursor}
    ) {{
        results {{
            jobKey
            title
            company {{ name }}
            location {{ city, state }}
            ...
        }}
        pageInfo {{ nextCursor }}
    }}
}}
"""
```

**5. 数据输出格式:**
```python
# 返回 Pandas DataFrame，包含以下字段：
jobs_df.columns = [
    'site',           # 'indeed'
    'title',          # 职位标题
    'company',        # 公司名
    'location',       # 'Sydney, Australia'
    'job_type',       # 'fulltime, parttime'
    'date_posted',    # 发布日期
    'interval',       # 'yearly', 'hourly'
    'min_amount',     # 最低薪资
    'max_amount',     # 最高薪资
    'currency',       # 'AUD'
    'description',    # 职位描述（Markdown 格式）
    'job_url',        # 职位链接
    'emails',         # 联系邮箱
    ...
]
```

#### 优点分析
✅ **开箱即用** - pip install python-jobspy
✅ **活跃维护** - 2025年3月还在更新
✅ **澳洲 Indeed 原生支持** - 配置简单
✅ **并发抓取** - 性能好
✅ **无需 Scrapy** - 轻量级
✅ **返回 Pandas DataFrame** - 数据处理方便
✅ **TLS 客户端** - 绕过反爬虫
✅ **代理支持** - 可扩展性强

#### 缺点分析
❌ **不支持 SEEK** - 需要额外实现
⚠️ **依赖 tls-client** - 可能需要编译
⚠️ **GraphQL API 依赖** - Indeed 改 API 会失效

---

### 2. SeekSpider（SEEK 专用爬虫）

**GitHub:** https://github.com/qinscode/SeekSpider
**Stars:** 30 | **最后更新:** 2024-04

#### 技术栈
```python
Python >= 3.9
Scrapy = 2.8.0
Selenium = 4.27.1           # 用于登录
beautifulsoup4 = 4.12.3
psycopg2-binary = 2.9.9    # PostgreSQL 直连
scrapy_fake_useragent = 1.4.4
webdriver_manager = 4.0.2
```

#### 代码结构
```
SeekSpider/
├── main.py                      # CLI 入口
├── scrapy.cfg
├── SeekSpider/
│   ├── spiders/
│   │   └── seek.py              # 主爬虫
│   ├── items.py                 # 数据模型
│   ├── pipelines.py             # PostgreSQL 管道
│   ├── middlewares.py
│   ├── settings.py
│   ├── core/
│   │   ├── config.py            # 环境配置
│   │   ├── database.py          # 数据库管理
│   │   ├── ai_client.py         # AI 集成（可选）
│   │   └── logger.py
│   └── utils/
│       ├── salary_normalizer.py
│       └── tech_stack_analyzer.py
```

#### 核心实现分析

**1. SEEK API 发现:**
```python
# SEEK 使用内部 API（非公开）
base_url = "https://www.seek.com.au/api/jobsearch/v5/search"

# 查询参数
search_params = {
    'siteKey': 'AU-Main',
    'sourcesystem': 'houston',
    'where': 'All Perth WA',          # 地点
    'page': 1,
    'seekSelectAllPages': 'true',
    'classification': '6281',          # IT 大类
    'subclassification': '6287',       # 具体职位类型
    'include': 'seodata',
    'locale': 'en-AU',
}
```

**2. 职位分类映射:**
```python
job_categories = {
    '6282': 'Architects',
    '6283': 'Business/Systems Analysts',
    '6287': 'Developers/Programmers',
    '6291': 'Help Desk & IT Support',
    # ... 共 22 个 IT 相关分类
}

# ⚠️ 重要发现：当前代码只支持 IT 类职位！
# 需要修改为 Trades 职位分类
```

**3. 数据抓取流程:**
```python
def parse(self, response):
    """解析搜索结果页"""
    raw_data = response.json()

    # 分页信息
    total_count = raw_data.get('totalCount', 0)
    items_per_page = raw_data.get('solMetadata', {}).get('pageSize', 20)

    # 遍历职位
    for data in raw_data['data']:
        yield self.parse_job(data)

    # 自动翻页
    if self.search_params['page'] < total_pages:
        self.search_params['page'] += 1
        yield self.make_requests_from_url(self.base_url)
```

**4. 数据模型:**
```python
class SeekspiderItem(scrapy.Item):
    job_id = scrapy.Field()           # SEEK 职位 ID
    job_title = scrapy.Field()
    business_name = scrapy.Field()    # 公司名
    work_type = scrapy.Field()        # Full Time / Part Time
    job_description = scrapy.Field()
    pay_range = scrapy.Field()
    suburb = scrapy.Field()           # 城市
    area = scrapy.Field()             # 地区
    url = scrapy.Field()
    advertiser_id = scrapy.Field()
    job_type = scrapy.Field()
    posted_date = scrapy.Field()
```

**5. PostgreSQL 管道（去重逻辑）:**
```python
class SeekspiderPipeline:
    def open_spider(self, spider):
        # 加载所有已存在的 job_id 到内存
        self.cursor.execute('SELECT "Id" FROM "Jobs"')
        self.existing_job_ids = set(str(row[0]) for row in self.cursor.fetchall())

    def process_item(self, item, spider):
        job_id = str(item.get('job_id'))

        # 内存去重
        if job_id in self.existing_job_ids:
            # UPDATE 现有记录
            update_sql = """
                UPDATE "Jobs" SET
                    "JobTitle" = %s,
                    "UpdatedAt" = now(),
                    "IsActive" = TRUE
                WHERE "Id" = %s
            """
            self.cursor.execute(update_sql, params)
        else:
            # INSERT 新记录
            insert_sql = """INSERT INTO "Jobs" (...)"""
            self.cursor.execute(insert_sql, params)
            self.existing_job_ids.add(job_id)
```

#### 优点分析
✅ **SEEK 原生支持** - 专门为 SEEK 设计
✅ **PostgreSQL 直连** - 与我们的技术栈一致
✅ **智能去重** - 基于 job_id 的 upsert
✅ **分页自动化** - 自动遍历所有页
✅ **Scrapy 架构** - 成熟的爬虫框架
✅ **代码清晰** - 模块化设计

#### 缺点分析
❌ **只支持 IT 职位** - 需要修改为 Trades
❌ **Selenium 依赖** - 资源消耗大（登录用）
❌ **AI 功能耦合** - 需要去除（我们不需要）
❌ **直接写数据库** - 不符合我们的架构（应该返回 JSON）
⚠️ **更新不频繁** - 2024年4月后无更新

---

## 🔧 混合架构设计方案

### 方案：JobSpy (Indeed) + 改造 SeekSpider (SEEK)

#### 架构图
```
┌─────────────────────────────────────────────────────┐
│          FastAPI Scrape Service (Python)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  POST /scrape/jobs                                  │
│    ├─ if source == "indeed":                        │
│    │    └─ JobSpy.scrape_jobs() ✅ 开箱即用         │
│    │                                                │
│    └─ if source == "seek":                          │
│         └─ SeekAdapter (改造 SeekSpider) ⚠️ 需修改  │
│                                                     │
└─────────────────────────────────────────────────────┘
            │
            │ HTTP JSON Response
            ▼
┌─────────────────────────────────────────────────────┐
│     .NET ScrapeApiClient (已实现)                   │
│     └─ IngestionPipeline → PostgreSQL              │
└─────────────────────────────────────────────────────┘
```

#### 实现步骤

**Step 1: 创建 FastAPI 项目骨架**
```bash
mkdir scrape-api
cd scrape-api

# 依赖清单
cat > requirements.txt <<EOF
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.10.0
python-jobspy==1.1.82    # JobSpy 库
scrapy==2.8.0            # SeekSpider 依赖
beautifulsoup4==4.12.3
requests==2.32.3
EOF

pip install -r requirements.txt
```

**Step 2: 定义数据模型**
```python
# models.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScrapeRequest(BaseModel):
    source: str                    # "indeed" | "seek"
    keywords: List[str]            # ["tiler", "bricklayer"]
    location: str                  # "Adelaide"
    max_results: int = 100

class JobData(BaseModel):
    source_id: str
    title: str
    company: str
    location: str
    description: Optional[str]
    posted_at: Optional[datetime]
    url: str
    # 与 .NET RawJobData 匹配

class ScrapeResponse(BaseModel):
    jobs: List[JobData]
    total: int
    scraped_at: datetime
```

**Step 3: Indeed 适配器（直接使用 JobSpy）**
```python
# adapters/indeed_adapter.py
from jobspy import scrape_jobs
from models import JobData
from datetime import datetime

class IndeedAdapter:
    async def scrape(self, request: ScrapeRequest) -> List[JobData]:
        # 使用 JobSpy 库抓取
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=" ".join(request.keywords),
            location=f"{request.location}, Australia",
            results_wanted=request.max_results,
            country_indeed='Australia',
            hours_old=168,  # 7天内
        )

        # 转换为我们的格式
        jobs = []
        for _, row in df.iterrows():
            jobs.append(JobData(
                source_id=str(row.get('job_key', '')),
                title=row.get('title', ''),
                company=row.get('company', ''),
                location=row.get('location', ''),
                description=row.get('description', ''),
                posted_at=row.get('date_posted'),
                url=row.get('job_url', '')
            ))

        return jobs
```

**Step 4: SEEK 适配器（改造 SeekSpider）**

需要做的修改：
1. ❌ 去除 Selenium 登录逻辑（测试是否必需）
2. ❌ 去除 AI 分析组件
3. ❌ 去除 PostgreSQL 管道
4. ✅ 修改职位分类为 Trades（不是 IT）
5. ✅ 改为返回 JSON 而非写数据库

```python
# adapters/seek_adapter.py
import requests
from typing import List
from models import JobData

class SeekAdapter:
    base_url = "https://www.seek.com.au/api/jobsearch/v5/search"

    # ⚠️ 需要研究 Trades 职位的 classification ID
    TRADES_CATEGORIES = {
        'tiler': '????',          # 需要查找
        'bricklayer': '????',
        'carpenter': '????',
        # TODO: 需要通过浏览器抓包获取正确的分类 ID
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 ...',
            'Accept': 'application/json',
        }

    async def scrape(self, request: ScrapeRequest) -> List[JobData]:
        jobs = []

        for keyword in request.keywords:
            classification_id = self.TRADES_CATEGORIES.get(keyword.lower())
            if not classification_id:
                continue

            params = {
                'siteKey': 'AU-Main',
                'where': f'All {request.location}',
                'classification': classification_id,
                'page': 1,
                'locale': 'en-AU',
            }

            # 分页抓取
            while len(jobs) < request.max_results:
                response = requests.get(self.base_url, params=params, headers=self.headers)
                data = response.json()

                for job_data in data.get('data', []):
                    jobs.append(self._parse_job(job_data))

                # 检查是否还有下一页
                if params['page'] >= data.get('totalPages', 1):
                    break
                params['page'] += 1

        return jobs[:request.max_results]

    def _parse_job(self, raw_data: dict) -> JobData:
        return JobData(
            source_id=str(raw_data.get('id', '')),
            title=raw_data.get('title', ''),
            company=raw_data.get('advertiser', {}).get('name', ''),
            location=raw_data.get('location', ''),
            description=raw_data.get('teaser', ''),  # 简短描述
            posted_at=raw_data.get('listedAt', {}).get('shortLabel'),
            url=f"https://www.seek.com.au/job/{raw_data.get('id')}"
        )
```

**Step 5: FastAPI 主应用**
```python
# main.py
from fastapi import FastAPI, HTTPException
from models import ScrapeRequest, ScrapeResponse, JobData
from adapters.indeed_adapter import IndeedAdapter
from adapters.seek_adapter import SeekAdapter
from datetime import datetime

app = FastAPI(title="Job Scrape API", version="1.0")

@app.post("/scrape/jobs", response_model=ScrapeResponse)
async def scrape_jobs(request: ScrapeRequest):
    if request.source == "indeed":
        adapter = IndeedAdapter()
    elif request.source == "seek":
        adapter = SeekAdapter()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source: {request.source}")

    jobs = await adapter.scrape(request)

    return ScrapeResponse(
        jobs=jobs,
        total=len(jobs),
        scraped_at=datetime.utcnow()
    )

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## 🚧 待解决的问题

### 1. SEEK Trades 职位分类 ID
**问题:** SeekSpider 当前只支持 IT 职位（classification=6281）
**解决方案:**
- 访问 SEEK 网站搜索 "tiler"
- 打开浏览器开发者工具 → Network
- 查看 API 请求中的 `classification` 参数
- 记录所有 Trades 相关的分类 ID

### 2. SEEK 是否需要登录
**问题:** SeekSpider 使用 Selenium 登录
**验证:**
- 测试未登录状态下能否访问 API
- 如果可以，去除 Selenium 依赖
- 如果不行，考虑使用 requests 模拟登录

### 3. 数据映射
**问题:** JobSpy 和 SeekSpider 返回的字段不完全一致
**解决:** 创建统一的 `JobData` 模型，做字段映射

---

## ✅ 推荐实施计划

### V1 MVP（本周完成）
1. ✅ 只实现 Indeed 适配器（使用 JobSpy）
2. ⏭️ SEEK 暂时跳过（V1.1 实现）
3. ✅ 验证完整数据流：Python → .NET → PostgreSQL

### V1.1（下周）
1. 研究 SEEK Trades 职位分类
2. 改造 SeekSpider 核心逻辑
3. 去除 AI 和 Selenium 依赖
4. 集成到 FastAPI

---

## 📊 最终评估

### JobSpy
- **可用性:** ⭐⭐⭐⭐⭐ (5/5) - 开箱即用
- **维护性:** ⭐⭐⭐⭐⭐ (5/5) - 活跃维护
- **适配成本:** ⭐⭐⭐⭐⭐ (5/5) - 几乎零成本

### SeekSpider
- **可用性:** ⭐⭐⭐ (3/5) - 需要大量改造
- **维护性:** ⭐⭐ (2/5) - 无人维护
- **适配成本:** ⭐⭐ (2/5) - 需要1-2天开发

### 混合架构总评
✅ **推荐使用**
理由：
1. Indeed 部分零成本（JobSpy）
2. SEEK 有参考代码（SeekSpider）
3. 快速验证 MVP 可行性
4. 后续可独立优化每个适配器

---

**下一步行动:** 开始实现 FastAPI + JobSpy 的 Indeed 适配器
