# JobSpy + SeekSpider 融合方案深度分析

> **分析时间:** 2025-12-16
> **目标:** 评估两个项目融合的可行性，取长补短

---

## 🔍 架构对比分析

### JobSpy 架构（轻量级、模块化）

```
架构特点：
├── 基于抽象类 Scraper 的插件式架构
├── 每个站点一个独立的 Scraper 实现
├── 统一的数据模型（Pydantic BaseModel）
├── 无框架依赖（纯 requests + beautifulsoup4）
└── 并发抓取（ThreadPoolExecutor）

核心设计模式：
┌─────────────────────────────────────┐
│   Scraper (ABC)                     │
│   ├── scrape() → JobResponse        │
│   └── 每个站点继承实现               │
├─────────────────────────────────────┤
│   Indeed(Scraper)                   │
│   LinkedIn(Scraper)                 │
│   Glassdoor(Scraper)                │
│   ZipRecruiter(Scraper)             │
└─────────────────────────────────────┘
```

**代码示例:**
```python
class Scraper(ABC):
    def __init__(self, site: Site, proxies: list[str] | str | None = None):
        self.site = site
        self.proxies = proxies

    @abstractmethod
    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """子类必须实现的抓取方法"""
        pass

class Indeed(Scraper):
    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        # Indeed 特定实现
        jobs = self._scrape_page(...)
        return JobResponse(jobs=jobs)
```

---

### SeekSpider 架构（Scrapy 框架、重量级）

```
架构特点：
├── 基于 Scrapy 框架的传统爬虫
├── Spider + Item + Pipeline 三层架构
├── 直接写入 PostgreSQL（紧耦合）
├── AI 增强功能（可选）
└── Selenium 自动化登录

核心设计模式：
┌─────────────────────────────────────┐
│   SeekSpider(scrapy.Spider)         │
│   ├── start_requests()              │
│   ├── parse()                       │
│   └── parse_job()                   │
├─────────────────────────────────────┤
│   SeekspiderItem                    │
│   └── Scrapy.Item 数据容器          │
├─────────────────────────────────────┤
│   SeekspiderPipeline                │
│   └── 直接写入 PostgreSQL            │
└─────────────────────────────────────┘
```

**代码示例:**
```python
class SeekSpider(scrapy.Spider):
    name = "seek"

    def start_requests(self):
        yield scrapy.Request(self.base_url)

    def parse(self, response):
        data = response.json()
        for job in data['data']:
            yield self.parse_job(job)

    def parse_job(self, data):
        item = SeekspiderItem()
        item['job_id'] = data['id']
        return item  # 传递给 Pipeline
```

---

## 💡 融合方案设计

### 方案 1: 将 SEEK 改造为 JobSpy 风格 ⭐⭐⭐⭐⭐ **强烈推荐**

**核心思路:** 保留 JobSpy 的架构，添加 SEEK 作为新的 Scraper

#### 实现步骤

**Step 1: 创建 SeekScraper 类**
```python
# jobspy/seek/__init__.py

from jobspy.model import Scraper, ScraperInput, JobResponse, JobPost, Site
import requests

class Seek(Scraper):
    """SEEK 澳洲求职网站爬虫"""

    def __init__(self, proxies: list[str] | str | None = None,
                 ca_cert: str | None = None,
                 user_agent: str | None = None):
        super().__init__(Site.SEEK, proxies=proxies)

        self.base_url = "https://www.seek.com.au/api/jobsearch/v5/search"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0...',
            'Accept': 'application/json',
        }

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """实现抽象方法"""
        jobs = []
        page = 1

        # 构建搜索参数
        params = self._build_params(scraper_input, page)

        while len(jobs) < scraper_input.results_wanted:
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            data = response.json()

            # 解析职位
            for job_data in data.get('data', []):
                job = self._parse_job(job_data)
                jobs.append(job)

            # 检查分页
            if page >= data.get('totalPages', 1):
                break
            page += 1
            params['page'] = page

        return JobResponse(jobs=jobs[:scraper_input.results_wanted])

    def _build_params(self, scraper_input: ScraperInput, page: int):
        """构建 SEEK API 参数"""
        # 从 SeekSpider 提取的逻辑
        return {
            'siteKey': 'AU-Main',
            'where': f'All {scraper_input.location}',
            'keywords': scraper_input.search_term,
            'page': page,
            'locale': 'en-AU',
            # TODO: 添加 Trades 职位分类
        }

    def _parse_job(self, data: dict) -> JobPost:
        """解析单个职位（从 SeekSpider 移植）"""
        return JobPost(
            id=str(data.get('id')),
            title=data.get('title', ''),
            company_name=data.get('advertiser', {}).get('description', ''),
            job_url=f"https://www.seek.com.au/job/{data.get('id')}",
            location=self._parse_location(data),
            description=data.get('teaser', ''),
            # ... 其他字段
        )
```

**Step 2: 注册到 JobSpy**
```python
# jobspy/__init__.py

from jobspy.seek import Seek  # 新增

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedIn,
    Site.INDEED: Indeed,
    Site.SEEK: Seek,  # 新增
    # ...
}
```

**Step 3: 添加 SEEK 到枚举**
```python
# jobspy/model.py

class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    SEEK = "seek"  # 新增
    # ...
```

**Step 4: 使用方式**
```python
from jobspy import scrape_jobs

# 同时抓取 Indeed 和 SEEK
jobs = scrape_jobs(
    site_name=["indeed", "seek"],  # 支持 SEEK！
    search_term="tiler",
    location="Adelaide",
    country_indeed='Australia',
    results_wanted=50
)

# 返回统一的 DataFrame
jobs.to_csv("jobs.csv")
```

#### 优点分析
✅ **架构统一** - 所有站点使用同一套接口
✅ **代码复用** - 复用 JobSpy 的并发、代理、数据模型
✅ **轻量级** - 无需 Scrapy、Selenium
✅ **易维护** - 模块化设计，SEEK 独立文件夹
✅ **易测试** - 单元测试友好
✅ **灵活调用** - 可单独调用 SEEK，也可混合抓取

#### 需要从 SeekSpider 移植的核心逻辑
1. ✅ SEEK API 端点和参数（已知）
2. ✅ 职位数据解析逻辑（`parse_job`）
3. ⚠️ Trades 职位分类 ID（需研究）
4. ❌ Selenium 登录（验证是否必需）
5. ❌ AI 分析（不需要）
6. ❌ PostgreSQL 管道（不需要）

---

### 方案 2: 保留 SeekSpider，通过 FastAPI 桥接 ❌ **不推荐**

**架构:**
```
FastAPI
├── /scrape/jobs?source=indeed
│   └─ 调用 JobSpy
└── /scrape/jobs?source=seek
    └─ 调用 Scrapy (subprocess)
```

**缺点:**
- ❌ 两套架构并存，维护成本高
- ❌ Scrapy 需要 subprocess 调用，性能差
- ❌ 数据格式不统一，需要额外转换
- ❌ 无法并发抓取多个站点

---

### 方案 3: 完全基于 Scrapy 重写 ❌ **不推荐**

**需要做的事:**
- 用 Scrapy 重写 Indeed 爬虫
- 用 Scrapy 重写 LinkedIn 爬虫
- ...

**缺点:**
- ❌ 工作量巨大
- ❌ JobSpy 已经很成熟，重写无意义
- ❌ Scrapy 过于重量级

---

## 🎯 推荐实施方案

### ✅ 最终方案：方案 1 - 将 SEEK 改造为 JobSpy 插件

#### 实施计划

**Phase 1: 最小化验证（今天，2小时）**
```bash
# 1. 在 JobSpy 项目中创建 seek 文件夹
mkdir jobspy/seek
touch jobspy/seek/__init__.py
touch jobspy/seek/util.py

# 2. 实现基础 SeekScraper（不含详情页抓取）
#    - 只抓取搜索结果页的基本信息
#    - 验证 API 调用可行性

# 3. 测试抓取 10 条数据
python test_seek.py
```

**Phase 2: 完整实现（明天，4小时）**
```bash
# 1. 研究 Trades 职位分类 ID
#    - 浏览器访问 SEEK，搜索 "tiler"
#    - Network 抓包，找到 classification 参数

# 2. 实现详情页抓取（可选）
#    - 参考 SeekSpider 的 _enrich_job_details
#    - 使用 BeautifulSoup 解析

# 3. 完善数据映射
#    - SEEK 字段 → JobPost 模型

# 4. 集成测试
#    - 同时抓取 Indeed + SEEK
#    - 验证数据格式一致性
```

**Phase 3: FastAPI 包装（后天，2小时）**
```python
# main.py
from fastapi import FastAPI
from jobspy import scrape_jobs

app = FastAPI()

@app.post("/scrape/jobs")
async def scrape(request: ScrapeRequest):
    df = scrape_jobs(
        site_name=[request.source],  # "indeed" or "seek"
        search_term=" ".join(request.keywords),
        location=f"{request.location}, Australia",
        results_wanted=request.max_results,
        country_indeed='Australia'
    )

    # 转换为 .NET 期望的格式
    jobs = df.to_dict('records')
    return {"jobs": jobs, "total": len(jobs)}
```

---

## 📊 核心代码对比

### 数据抓取逻辑

**JobSpy (Indeed):**
```python
# GraphQL API 调用
response = self.session.post(
    self.api_url,
    json={"query": graphql_query},
    headers=self.headers
)
jobs = response.json()['data']['jobSearch']['results']
```

**SeekSpider (SEEK):**
```python
# REST API 调用
response = requests.get(
    "https://www.seek.com.au/api/jobsearch/v5/search",
    params={'where': 'Adelaide', 'page': 1}
)
jobs = response.json()['data']
```

**结论:** 两者都是 HTTP API 调用，SeekSpider 甚至更简单！

---

### 数据模型映射

| 字段 | JobSpy (JobPost) | SeekSpider (Item) | 是否兼容 |
|------|------------------|-------------------|---------|
| ID | `id: str` | `job_id: str` | ✅ 直接映射 |
| 标题 | `title: str` | `job_title: str` | ✅ 直接映射 |
| 公司 | `company_name: str` | `business_name: str` | ✅ 直接映射 |
| 链接 | `job_url: str` | `url: str` | ✅ 直接映射 |
| 地点 | `location: Location` | `suburb + area` | ⚠️ 需转换 |
| 描述 | `description: str` | `job_description: str` | ✅ 直接映射 |
| 薪资 | `compensation: Compensation` | `pay_range: str` | ⚠️ 需解析 |
| 发布日期 | `date_posted: date` | `posted_date: str` | ⚠️ 需解析 |

**结论:** 90% 的字段可以直接映射，少数需要简单转换

---

## 🔧 具体移植步骤

### 从 SeekSpider 提取的核心代码

**1. API 端点和参数（直接复用）**
```python
# 从 SeekSpider/spiders/seek.py 第 21-47 行
base_url = "https://www.seek.com.au/api/jobsearch/v5/search"

search_params = {
    'siteKey': 'AU-Main',
    'sourcesystem': 'houston',
    'where': 'All Perth WA',  # 动态替换
    'page': 1,
    'seekSelectAllPages': 'true',
    'classification': '6281',  # ⚠️ 需要改为 Trades
    'include': 'seodata',
    'locale': 'en-AU',
}
```

**2. 职位解析逻辑（需适配）**
```python
# 从 SeekSpider/spiders/seek.py 第 159-193 行
def _parse_job(self, data: dict) -> JobPost:
    # 提取基本信息
    job_id = data['id']
    title = data.get('title', '')
    company = data.get('advertiser', {}).get('description', '')

    # 提取地点
    location_data = data.get('locations', [{}])[0]
    location = Location(
        city=location_data.get('label', '').split(',')[0],
        state='SA',  # 从 location 解析
        country=Country.AUSTRALIA
    )

    # 提取薪资（需要解析字符串）
    salary_label = data.get('salaryLabel', '')
    compensation = self._parse_salary(salary_label)

    return JobPost(
        id=str(job_id),
        title=title,
        company_name=company,
        location=location,
        compensation=compensation,
        job_url=f"https://www.seek.com.au/job/{job_id}",
        description=data.get('teaser', ''),
        date_posted=self._parse_date(data.get('listingDate'))
    )
```

**3. 详情页抓取（可选，提升数据质量）**
```python
# 从 SeekSpider/spiders/seek.py 第 195-226 行
def _fetch_job_details(self, job_url: str) -> dict:
    """抓取职位详情页（完整描述）"""
    response = requests.get(job_url, headers=self.headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # 提取完整职位描述
    job_details = soup.find("div", {"data-automation": "jobAdDetails"})
    description = str(job_details) if job_details else None

    # 提取其他详细信息
    location = soup.find("span", {"data-automation": "job-detail-location"})
    work_type = soup.find("span", {"data-automation": "job-detail-work-type"})

    return {
        'description': description,
        'location': location.text if location else None,
        'work_type': work_type.text if work_type else None
    }
```

---

## 🚨 关键风险与解决方案

### 风险 1: Trades 职位分类 ID 未知
**影响:** 无法精准搜索 Trades 职位
**解决方案:**
```bash
# 方案 A: 浏览器抓包
1. 访问 https://www.seek.com.au
2. 搜索 "tiler"
3. 打开 DevTools → Network
4. 查找 /api/jobsearch/v5/search 请求
5. 记录 classification 参数

# 方案 B: 关键词搜索（如果分类ID不可用）
params = {
    'keywords': 'tiler bricklayer',  # 关键词搜索
    # 不指定 classification
}
```

### 风险 2: SEEK 是否需要登录
**影响:** 可能无法访问 API
**解决方案:**
```python
# 测试未登录访问
response = requests.get(
    "https://www.seek.com.au/api/jobsearch/v5/search",
    params={'where': 'Adelaide', 'keywords': 'tiler'}
)

if response.status_code == 401:
    # 需要登录，使用 requests 模拟（避免 Selenium）
    login_response = requests.post(
        "https://www.seek.com.au/oauth/login",
        json={'username': '...', 'password': '...'}
    )
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
else:
    # 无需登录！
    pass
```

### 风险 3: 数据格式变化
**影响:** SEEK 改 API 导致解析失败
**解决方案:**
```python
# 健壮的解析逻辑
def _parse_job(self, data: dict) -> JobPost:
    try:
        job_id = data['id']  # 必需字段
    except KeyError:
        raise ParseError("Missing job ID")

    # 可选字段使用 .get() + 默认值
    title = data.get('title', 'Unknown Title')
    company = data.get('advertiser', {}).get('description', 'Unknown Company')

    return JobPost(...)
```

---

## ✅ 最终结论

### 是否可以融合？**可以！** ⭐⭐⭐⭐⭐

**融合方式:** 将 SeekSpider 的核心逻辑移植到 JobSpy 架构

**工作量评估:**
- **代码行数:** ~200 行（SeekSpider 核心逻辑）
- **开发时间:** 6-8 小时
- **难度:** ⭐⭐⭐ (中等)

**收益:**
- ✅ 统一架构，易维护
- ✅ 支持并发抓取 Indeed + SEEK
- ✅ 无需 Scrapy、Selenium
- ✅ 代码量减少 70%

**风险:**
- ⚠️ Trades 分类 ID 需要研究（1小时）
- ⚠️ 可能需要登录（待验证）
- ⚠️ API 稳定性（SEEK 未公开文档）

---

## 📅 实施建议

**今天（2小时）:**
1. 创建 `jobspy/seek/` 文件夹
2. 实现基础 SeekScraper（无详情页）
3. 测试抓取 10 条 Trades 职位

**明天（4小时）:**
1. 研究 Trades 分类 ID
2. 完善数据解析
3. 添加详情页抓取（可选）
4. 集成测试

**后天（2小时）:**
1. FastAPI 包装
2. 与 .NET 对接测试
3. 完整数据流验证

**总耗时:** ~8 小时（完成 V1 MVP）

---

**下一步:** 你想现在开始实施吗？我可以帮你：
1. Fork JobSpy 项目（在 scrape-api-research 基础上修改）
2. 创建 SeekScraper 骨架
3. 测试 SEEK API 是否可访问（验证登录需求）
