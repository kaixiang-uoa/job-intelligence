# 爬虫数据字段详细分析

> **分析时间:** 2025-12-16 晚上
> **目的:** 对比 JobSpy 和 SeekSpider 可抓取的数据字段，映射到我们的 JobPosting 实体

---

## 📊 数据源对比总览

### JobSpy (Indeed 等多平台)
- **数据源:** Indeed, LinkedIn, Glassdoor, Google Jobs, ZipRecruiter
- **数据模型:** `JobPost` (Pydantic BaseModel)
- **输出格式:** Pandas DataFrame
- **字段数量:** 20+ 个字段

### SeekSpider (SEEK 专用)
- **数据源:** SEEK Australia
- **数据模型:** `SeekspiderItem` (Scrapy Item)
- **输出格式:** Scrapy Item → PostgreSQL
- **字段数量:** 12 个字段

### 我们的数据模型 (.NET)
- **实体:** `JobPosting`
- **字段数量:** 18 个字段（不含 V2 预留）

---

## 🔍 JobSpy 数据字段详细分析

### 核心字段 (JobPost 类)

```python
class JobPost(BaseModel):
    # 基础信息 (必需)
    id: str | None                      # 职位 ID
    title: str                          # 职位标题 ✅ 必需
    company_name: str | None            # 公司名称
    job_url: str                        # 职位链接 ✅ 必需
    job_url_direct: str | None          # 直接申请链接

    # 地点信息
    location: Optional[Location]        # 地点对象
        ├── city: str                   # 城市
        ├── state: str                  # 州/省
        └── country: Country            # 国家枚举

    # 详细信息
    description: str | None             # 职位描述
    company_url: str | None             # 公司网站
    company_url_direct: str | None      # 公司直接链接

    # 职位属性
    job_type: list[JobType] | None      # 工作类型列表
        # JobType.FULL_TIME, PART_TIME, CONTRACT, etc.
    compensation: Compensation | None   # 薪资信息对象
        ├── interval: CompensationInterval  # yearly/monthly/hourly
        ├── min_amount: float           # 最低薪资
        ├── max_amount: float           # 最高薪资
        └── currency: str               # 货币 (USD/AUD)

    date_posted: date | None            # 发布日期
    emails: list[str] | None            # 联系邮箱列表
    is_remote: bool | None              # 是否远程
    listing_type: str | None            # 列表类型

    # LinkedIn 特有字段
    job_level: str | None               # 职位级别 (Entry, Mid, Senior)
    job_function: str | None            # 职位职能

    # LinkedIn 和 Indeed 共有
    company_industry: str | None        # 公司行业

    # Indeed 特有字段
    company_addresses: str | None       # 公司地址
    company_num_employees: str | None   # 员工数量
    company_revenue: str | None         # 公司收入
    company_description: str | None     # 公司描述
    company_logo: str | None            # 公司 Logo
    banner_photo_url: str | None        # 横幅图片

    # Naukri 特有字段
    skills: list[str] | None            # 技能列表
    experience_range: str | None        # 经验要求
    company_rating: float | None        # 公司评分
    company_reviews_count: int | None   # 评论数
    vacancy_count: int | None           # 空缺数量
    work_from_home_type: str | None     # 远程类型 (Hybrid/Remote)
```

### JobSpy 输出示例 (DataFrame)

```python
# scrape_jobs() 返回的 DataFrame 列名
columns = [
    'site',              # 数据源网站 (indeed, linkedin, etc.)
    'title',             # 职位标题
    'company',           # 公司名称
    'location',          # 地点字符串 "Adelaide, SA"
    'job_type',          # 工作类型字符串 "fulltime, parttime"
    'date_posted',       # 发布日期
    'interval',          # 薪资周期 (yearly/hourly)
    'min_amount',        # 最低薪资
    'max_amount',        # 最高薪资
    'currency',          # 货币 (AUD)
    'is_remote',         # 是否远程
    'job_url',           # 职位链接
    'job_url_direct',    # 直接申请链接
    'description',       # 职位描述 (Markdown 格式)
    'company_url',       # 公司网站
    'emails',            # 联系邮箱 (逗号分隔字符串)
    'job_level',         # 职位级别 (LinkedIn)
    'salary_source',     # 薪资来源 (direct_data/description)
    # ... 其他平台特有字段
]
```

---

## 🔍 SeekSpider 数据字段详细分析

### 核心字段 (SeekspiderItem 类)

```python
class SeekspiderItem(scrapy.Item):
    job_id = scrapy.Field()            # SEEK 职位 ID
    job_title = scrapy.Field()         # 职位标题
    business_name = scrapy.Field()     # 公司名称
    work_type = scrapy.Field()         # 工作类型 (Full Time, Part Time, etc.)
    job_description = scrapy.Field()   # 职位描述 (HTML 格式)
    pay_range = scrapy.Field()         # 薪资范围字符串 (e.g., "70000-80000")
    suburb = scrapy.Field()            # 城市/郊区
    area = scrapy.Field()              # 地区/州
    url = scrapy.Field()               # 职位链接
    advertiser_id = scrapy.Field()     # 招聘方 ID
    job_type = scrapy.Field()          # 职位类型/分类
    posted_date = scrapy.Field()       # 发布日期
```

### SEEK API 原始数据示例

从我们之前测试的 SEEK API 返回：

```json
{
  "id": "12345678",
  "title": "Qualified Tiler",
  "advertiser": {
    "id": "29915483",
    "description": "Ken Hall Plumbers"
  },
  "bulletPoints": [
    "High Earning Potential",
    "Ongoing Training"
  ],
  "classifications": [
    {
      "classification": {
        "id": "1225",
        "description": "Trades & Services"
      }
    }
  ],
  "location": "Adelaide SA",
  "salary": "70000-80000",
  "salaryLabel": "$70,000 - $80,000 per year",
  "listingDate": "2025-12-10T08:00:00Z",
  "teaser": "We are seeking an experienced tiler...",
  "workTypes": ["Full Time"]
}
```

### SeekSpider 可抓取的扩展字段

根据 `seek.py` 中的 `_enrich_job_details` 方法：

```python
# 从职位详情页抓取的额外字段
location = soup.find("span", {"data-automation": "job-detail-location"})
work_type = soup.find("span", {"data-automation": "job-detail-work-type"})
job_type = soup.find("span", {"data-automation": "job-detail-classifications"})
salary = soup.find("span", {"data-automation": "job-detail-salary"})
job_details = soup.find("div", {"data-automation": "jobAdDetails"})
```

---

## 📋 字段对比表

### 核心字段对比

| 字段类别 | JobSpy (Indeed) | SeekSpider (SEEK) | 我们的 JobPosting | 数据来源 |
|---------|-----------------|-------------------|------------------|---------|
| **ID** | ✅ `id` (可选) | ✅ `job_id` (必需) | ✅ `SourceId` | 所有源 |
| **标题** | ✅ `title` (必需) | ✅ `job_title` | ✅ `Title` | 所有源 |
| **公司** | ✅ `company_name` | ✅ `business_name` | ✅ `Company` | 所有源 |
| **链接** | ✅ `job_url` | ✅ `url` | ❌ 缺失 | 所有源 |
| **描述** | ✅ `description` (Markdown) | ✅ `job_description` (HTML) | ✅ `Description` | 所有源 |
| **发布日期** | ✅ `date_posted` | ✅ `posted_date` | ✅ `PostedAt` | 所有源 |

### 地点字段对比

| 字段 | JobSpy | SeekSpider | JobPosting | 说明 |
|------|--------|-----------|-----------|------|
| **州/省** | ✅ `location.state` | ✅ `area` | ✅ `LocationState` | 需解析 |
| **城市** | ✅ `location.city` | ✅ `suburb` | ✅ `LocationSuburb` | 需解析 |
| **国家** | ✅ `location.country` | ❌ 固定澳洲 | ❌ 缺失 | 可推断 |
| **完整地点** | ✅ `location` (字符串) | ✅ `location` | ❌ 缺失 | 组合字段 |

### 薪资字段对比

| 字段 | JobSpy | SeekSpider | JobPosting | 说明 |
|------|--------|-----------|-----------|------|
| **最低薪资** | ✅ `compensation.min_amount` | ⚠️ `pay_range` (需解析) | ✅ `PayRangeMin` | 结构化 vs 字符串 |
| **最高薪资** | ✅ `compensation.max_amount` | ⚠️ `pay_range` (需解析) | ✅ `PayRangeMax` | 结构化 vs 字符串 |
| **薪资周期** | ✅ `compensation.interval` | ⚠️ 包含在 `pay_range` | ❌ 缺失 | yearly/hourly |
| **货币** | ✅ `compensation.currency` | ❌ 固定 AUD | ❌ 缺失 | USD/AUD |

### 职位属性对比

| 字段 | JobSpy | SeekSpider | JobPosting | 说明 |
|------|--------|-----------|-----------|------|
| **工作类型** | ✅ `job_type` (列表) | ✅ `work_type` (字符串) | ✅ `EmploymentType` | Full Time/Part Time |
| **行业/Trade** | ⚠️ 需从标题提取 | ✅ `job_type` (分类) | ✅ `Trade` | 我们需要的核心字段 |
| **是否远程** | ✅ `is_remote` | ❌ 缺失 | ❌ 缺失 | JobSpy 独有 |
| **职位级别** | ✅ `job_level` (LinkedIn) | ❌ 缺失 | ❌ 缺失 | Entry/Mid/Senior |
| **技能要求** | ✅ `skills` (Naukri) | ❌ 缺失 | ❌ 缺失 | 可从描述提取 |

### 公司信息对比

| 字段 | JobSpy | SeekSpider | JobPosting | 说明 |
|------|--------|-----------|-----------|------|
| **公司网站** | ✅ `company_url` | ❌ 缺失 | ❌ 缺失 | Indeed 提供 |
| **公司行业** | ✅ `company_industry` | ❌ 缺失 | ❌ 缺失 | LinkedIn/Indeed |
| **公司规模** | ✅ `company_num_employees` | ❌ 缺失 | ❌ 缺失 | Indeed 提供 |
| **公司 Logo** | ✅ `company_logo` | ❌ 缺失 | ❌ 缺失 | Indeed 提供 |
| **招聘方 ID** | ❌ 缺失 | ✅ `advertiser_id` | ❌ 缺失 | SEEK 独有 |

### 元数据字段对比

| 字段 | JobSpy | SeekSpider | JobPosting | 说明 |
|------|--------|-----------|-----------|------|
| **数据源** | ✅ `site` | ❌ 固定 "seek" | ✅ `Source` | indeed/seek/linkedin |
| **联系邮箱** | ✅ `emails` (列表) | ❌ 缺失 | ❌ 缺失 | 从描述提取 |
| **抓取时间** | ❌ 缺失 | ❌ 缺失 | ✅ `ScrapedAt` | 我们自己添加 |
| **Fingerprint** | ❌ 缺失 | ❌ 缺失 | ✅ `Fingerprint` | 去重用 |
| **ContentHash** | ❌ 缺失 | ❌ 缺失 | ✅ `ContentHash` | 去重用 |

---

## 🎯 数据字段映射方案

### JobSpy (Indeed) → JobPosting

```python
# Python 代码示例
def map_jobspy_to_jobposting(jobspy_row):
    return {
        "Source": jobspy_row['site'],                    # "indeed"
        "SourceId": jobspy_row.get('id') or generate_id(),  # 可能为空
        "Title": jobspy_row['title'],
        "Company": jobspy_row['company'],
        "LocationState": extract_state(jobspy_row['location']),  # 需解析 "Adelaide, SA"
        "LocationSuburb": extract_city(jobspy_row['location']),
        "Trade": extract_trade_from_title(jobspy_row['title']),  # 从标题提取
        "EmploymentType": parse_job_type(jobspy_row['job_type']),  # "fulltime, parttime" → "Full Time"
        "PayRangeMin": jobspy_row.get('min_amount'),
        "PayRangeMax": jobspy_row.get('max_amount'),
        "Description": jobspy_row['description'],         # 已是 Markdown
        "Requirements": extract_requirements(jobspy_row['description']),  # 需提取
        "Tags": generate_tags(jobspy_row),               # 基于 is_remote, job_level 等
        "PostedAt": jobspy_row['date_posted'],
        "ScrapedAt": datetime.utcnow(),
        # Fingerprint 和 ContentHash 由 DeduplicationService 生成
    }
```

### SeekSpider (SEEK) → JobPosting

```python
# Python 代码示例
def map_seekspider_to_jobposting(seek_item):
    return {
        "Source": "seek",
        "SourceId": seek_item['job_id'],
        "Title": seek_item['job_title'],
        "Company": seek_item['business_name'],
        "LocationState": seek_item['area'],              # 直接使用
        "LocationSuburb": seek_item['suburb'],
        "Trade": seek_item['job_type'],                  # SEEK 提供分类
        "EmploymentType": seek_item['work_type'],        # "Full Time"
        "PayRangeMin": parse_salary_min(seek_item['pay_range']),  # "70000-80000" → 70000
        "PayRangeMax": parse_salary_max(seek_item['pay_range']),  # "70000-80000" → 80000
        "Description": clean_html(seek_item['job_description']),  # HTML → 纯文本
        "Requirements": extract_requirements(seek_item['job_description']),
        "Tags": generate_tags_from_description(seek_item['job_description']),
        "PostedAt": parse_date(seek_item['posted_date']),
        "ScrapedAt": datetime.utcnow(),
    }
```

---

## ⚠️ 数据质量对比

### JobSpy (Indeed) 优势

| 优势 | 说明 |
|------|------|
| ✅ **结构化薪资** | `compensation` 对象已解析，直接可用 |
| ✅ **Markdown 描述** | 已转换，无需清理 HTML |
| ✅ **多平台支持** | Indeed, LinkedIn, Glassdoor 数据格式统一 |
| ✅ **丰富的公司信息** | 公司网站、行业、规模等 |
| ✅ **是否远程** | `is_remote` 字段明确 |
| ✅ **联系邮箱** | 自动提取 |

### JobSpy (Indeed) 劣势

| 劣势 | 说明 |
|------|------|
| ❌ **缺少 Trade** | 需要从标题或描述提取（额外处理） |
| ❌ **ID 可能为空** | Indeed 不总是返回 ID |
| ⚠️ **地点格式不统一** | "Adelaide, SA" vs "Sydney NSW" |

### SeekSpider (SEEK) 优势

| 优势 | 说明 |
|------|------|
| ✅ **Trade 分类明确** | SEEK API 直接提供职位分类 |
| ✅ **ID 总是存在** | SEEK 职位 ID 可靠 |
| ✅ **地点结构化** | `suburb` 和 `area` 分开 |
| ✅ **澳洲本地化** | 专门针对澳洲市场 |

### SeekSpider (SEEK) 劣势

| 劣势 | 说明 |
|------|------|
| ❌ **薪资是字符串** | 需要解析 "70000-80000 per year" |
| ❌ **描述是 HTML** | 需要清理 HTML 标签 |
| ❌ **缺少公司信息** | 没有公司网站、行业等 |
| ❌ **缺少远程标识** | 无法直接判断是否远程 |

---

## 🔧 需要实现的数据转换逻辑

### 1. 地点解析（JobSpy）

```python
def parse_location(location_str: str) -> tuple[str, str]:
    """
    解析地点字符串
    输入: "Adelaide, SA" 或 "Sydney NSW"
    输出: (state, suburb)
    """
    # 示例实现
    parts = location_str.split(',')
    if len(parts) == 2:
        suburb = parts[0].strip()
        state = parts[1].strip()
    else:
        # "Sydney NSW" 格式
        words = location_str.split()
        state = words[-1]  # 最后一个词
        suburb = ' '.join(words[:-1])

    return state, suburb
```

### 2. 薪资解析（SeekSpider）

```python
def parse_salary_range(pay_range: str) -> tuple[float, float]:
    """
    解析薪资字符串
    输入: "$70,000 - $80,000 per year" 或 "70000-80000"
    输出: (70000.0, 80000.0)
    """
    import re

    # 移除 $, 逗号
    cleaned = pay_range.replace('$', '').replace(',', '')

    # 提取数字
    numbers = re.findall(r'\d+', cleaned)

    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    elif len(numbers) == 1:
        amount = float(numbers[0])
        return amount, amount  # 单一薪资
    else:
        return None, None
```

### 3. Trade 提取（JobSpy）

```python
TRADE_KEYWORDS = {
    'tiler': ['tiler', 'tiling', 'tile'],
    'bricklayer': ['bricklayer', 'brick', 'masonry'],
    'carpenter': ['carpenter', 'carpentry', 'joiner'],
    'plumber': ['plumber', 'plumbing'],
    'electrician': ['electrician', 'electrical', 'sparky'],
    'painter': ['painter', 'painting'],
    'plasterer': ['plasterer', 'plastering'],
    'labourer': ['labourer', 'laborer', 'general labour'],
}

def extract_trade(title: str) -> str:
    """
    从职位标题提取 Trade
    输入: "Experienced Tiler - Adelaide"
    输出: "tiler"
    """
    title_lower = title.lower()

    for trade, keywords in TRADE_KEYWORDS.items():
        if any(keyword in title_lower for keyword in keywords):
            return trade

    return None  # 无法识别
```

### 4. HTML 清理（SeekSpider）

```python
from bs4 import BeautifulSoup

def clean_html(html_str: str) -> str:
    """
    清理 HTML 标签
    输入: "<p>We are seeking...</p>"
    输出: "We are seeking..."
    """
    if not html_str:
        return ""

    soup = BeautifulSoup(html_str, 'html.parser')

    # 移除 script 和 style 标签
    for tag in soup(['script', 'style']):
        tag.decompose()

    # 获取纯文本
    text = soup.get_text()

    # 清理空白
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)

    return text
```

### 5. 工作类型标准化

```python
EMPLOYMENT_TYPE_MAPPING = {
    # JobSpy 格式
    'fulltime': 'Full Time',
    'parttime': 'Part Time',
    'contract': 'Contract',
    'temporary': 'Temporary',
    'internship': 'Internship',

    # SeekSpider 格式（已标准化）
    'Full Time': 'Full Time',
    'Part Time': 'Part Time',
    'Contract/Temp': 'Contract',
    'Casual/Vacation': 'Casual',
}

def normalize_employment_type(raw_type: str) -> str:
    """
    标准化工作类型
    """
    if not raw_type:
        return None

    # JobSpy 可能返回 "fulltime, parttime"
    types = [t.strip() for t in raw_type.split(',')]
    normalized = [EMPLOYMENT_TYPE_MAPPING.get(t, t) for t in types]

    return normalized[0]  # 取第一个
```

---

## 📊 最终数据覆盖率

### 我们的 JobPosting 字段覆盖率

| JobPosting 字段 | JobSpy 支持 | SeekSpider 支持 | 备注 |
|----------------|-------------|-----------------|------|
| Source | ✅ 直接 | ✅ 固定 | - |
| SourceId | ⚠️ 可能空 | ✅ 必有 | JobSpy 需回退方案 |
| Title | ✅ | ✅ | - |
| Company | ✅ | ✅ | - |
| LocationState | ✅ 需解析 | ✅ 直接 | - |
| LocationSuburb | ✅ 需解析 | ✅ 直接 | - |
| Trade | ⚠️ 需提取 | ✅ 直接 | SEEK 优势 |
| EmploymentType | ✅ 需标准化 | ✅ 直接 | - |
| PayRangeMin | ✅ 直接 | ⚠️ 需解析 | JobSpy 优势 |
| PayRangeMax | ✅ 直接 | ⚠️ 需解析 | JobSpy 优势 |
| Description | ✅ Markdown | ⚠️ 需清理 | JobSpy 优势 |
| Requirements | ⚠️ 需提取 | ⚠️ 需提取 | 两者都需要 |
| Tags | ⚠️ 需生成 | ⚠️ 需生成 | 两者都需要 |
| PostedAt | ✅ 直接 | ✅ 直接 | - |
| **覆盖率** | **85%** | **75%** | - |

---

## 🎯 实施建议

### 优先级 1: 必须实现的转换

1. **地点解析** (JobSpy)
2. **薪资解析** (SeekSpider)
3. **HTML 清理** (SeekSpider)
4. **Trade 提取** (JobSpy)

### 优先级 2: 建议实现的转换

5. **工作类型标准化** (两者)
6. **Requirements 提取** (两者)
7. **Tags 生成** (两者)

### 优先级 3: 可选增强

8. **联系邮箱提取** (JobSpy 已提供)
9. **公司信息保存** (扩展 JobPosting 实体)
10. **远程标识** (扩展 JobPosting 实体)

---

## 🚀 下一步

1. 确认数据映射方案
2. 实现数据转换函数
3. 创建统一的数据适配器
4. 测试数据转换准确性

**你想先看哪个部分的详细实现？**
