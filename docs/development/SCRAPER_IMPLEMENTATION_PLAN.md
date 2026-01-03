# 爬虫项目实施计划

> **创建时间:** 2025-12-18
> **最后更新:** 2025-12-22
> **状态:** ✅ 全部完成 - Python 爬虫生产就绪 + .NET 集成完成
> **目的:** 基于 JobSpy 和 SeekSpider 的研究，制定详细的爬虫实施步骤

---

## 📋 总体架构方案

基于前期调研（见 [SCRAPER_FUSION_ANALYSIS.md](SCRAPER_FUSION_ANALYSIS.md)），我们采用以下架构：

```
┌─────────────────────────────────────────────────────┐
│         Python FastAPI 爬虫服务                        │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐        ┌───────────────┐         │
│  │ Indeed       │        │ SEEK          │         │
│  │ Adapter      │        │ Adapter       │         │
│  │ (基于 JobSpy)│        │ (基于 SeekSpider)│      │
│  └──────────────┘        └───────────────┘         │
│         │                        │                   │
│         └────────┬───────────────┘                   │
│                  │                                    │
│         ┌────────▼────────┐                         │
│         │ 统一数据适配层   │                         │
│         │ (映射到 JobPosting)│                      │
│         └────────┬────────┘                         │
└──────────────────┼──────────────────────────────────┘
                   │ HTTP API
                   ▼
         ┌─────────────────┐
         │ .NET Backend    │
         │ Ingestion API   │
         └─────────────────┘
```

**核心理念:**
- ✅ 使用 JobSpy 库处理 Indeed（开箱即用）
- ✅ 提取 SeekSpider 核心逻辑处理 SEEK（去除 Scrapy/Selenium）
- ✅ FastAPI 提供统一的 REST API
- ✅ 数据转换层确保输出格式一致

---

## 🧪 开发方法：渐进式 TDD

### TDD 策略

**参考文档:** [TDD_DEVELOPMENT_GUIDE.md](TDD_DEVELOPMENT_GUIDE.md)

本项目采用**渐进式 TDD**（Incremental TDD）方法：

#### ✅ 使用 TDD 的部分（Red-Green-Refactor）

**1. 工具函数（完全 TDD）** - 优先级 P0
```
工具函数逻辑清晰，输入输出明确，最适合 TDD 练习：

🔴 RED    → 写失败的测试
🟢 GREEN  → 写最少代码让测试通过
🔵 REFACTOR → 重构优化

- parse_location()      # 地点解析
- parse_salary_range()  # 薪资解析
- extract_trade()       # Trade 提取
- clean_html()          # HTML 清理
- normalize_employment_type()  # 工作类型标准化
```

**2. 数据转换逻辑（推荐 TDD）** - 优先级 P1
```
- JobSpy → JobPostingDTO 转换
- SEEK → JobPostingDTO 转换
```

#### ⚠️ 可选 TDD 或后补测试的部分

**3. 适配器类（先实现，后补测试）** - 优先级 P1
```
原因：涉及外部 API 调用，Mock 复杂

- IndeedAdapter.scrape()
- SeekAdapter.scrape()

策略：
1. 先手动实现和测试
2. 验证可行后补充单元测试
```

**4. FastAPI 端点（集成测试）** - 优先级 P2
```
- POST /scrape/indeed
- POST /scrape/seek

策略：端到端集成测试即可
```

### TDD 实施顺序

```
Phase 2.1: 工具函数（TDD）           ⭐ 完全 TDD
  ├── test_location_parser.py
  ├── location_parser.py
  ├── test_salary_parser.py
  ├── salary_parser.py
  ├── test_trade_extractor.py
  └── trade_extractor.py

Phase 2.2: Indeed 适配器（混合）
  ├── indeed_adapter.py            (先实现)
  └── test_indeed_adapter.py       (后补测试)

Phase 2.3: SEEK 适配器（混合）
  ├── seek_adapter.py              (先实现)
  └── test_seek_adapter.py         (后补测试)

Phase 2.4: 集成测试
  └── test_integration.py          (端到端测试)
```

### 为什么选择渐进式 TDD？

**优点：**
- ✅ 在简单函数上体验完整 TDD 流程（学习价值高）
- ✅ 复杂部分避免卡在 Mock 上（保持开发效率）
- ✅ 最终代码有测试覆盖（质量保障）
- ✅ 符合实际工作场景（混合实践）

**时间成本：**
- 完全 TDD：+50% 时间
- 渐进式 TDD：+20% 时间（可接受）
- 后补测试：+10% 时间（但易遗漏）

---

## 🎯 实施阶段划分

### 阶段 1: Python 爬虫服务骨架（预计 2-3 小时）

**目标:** 创建 FastAPI 项目，实现基础结构

**任务清单:**
- [ ] 创建 Python 项目目录结构
- [ ] 安装依赖 (FastAPI, JobSpy, requests, pydantic)
- [ ] 实现基础 FastAPI 应用
- [ ] 定义统一的数据模型 (JobPostingDTO)
- [ ] 实现健康检查端点

**详细步骤:** 🔖 待实施时详细记录

---

### 阶段 2: Indeed 适配器（预计 4-5 小时，包含 TDD）

**目标:** 使用 JobSpy 库实现 Indeed 数据抓取

#### Phase 2.1: 工具函数（TDD）⭐ 预计 2 小时

**使用完全 TDD 流程：🔴 RED → 🟢 GREEN → 🔵 REFACTOR**

**任务清单:**
- [ ] **parse_location()** - 地点解析
  - [ ] 🔴 编写测试：test_parse_location_basic()
  - [ ] 🔴 编写测试：test_parse_location_with_comma()
  - [ ] 🔴 编写测试：test_parse_location_empty()
  - [ ] 🔴 编写测试：test_parse_location_invalid()
  - [ ] 🟢 实现最小功能
  - [ ] 🔵 重构优化

- [ ] **extract_trade()** - Trade 提取
  - [ ] 🔴 编写测试：test_extract_trade_tiler()
  - [ ] 🔴 编写测试：test_extract_trade_plumber()
  - [ ] 🔴 编写测试：test_extract_trade_not_found()
  - [ ] 🟢 实现关键词匹配
  - [ ] 🔵 重构优化

- [ ] **normalize_employment_type()** - 工作类型标准化
  - [ ] 🔴 编写测试
  - [ ] 🟢 实现功能
  - [ ] 🔵 重构

#### Phase 2.2: Indeed 适配器（混合方式）⭐ 预计 2 小时

**先实现，后补测试**

**任务清单:**
- [ ] 创建 IndeedAdapter 类
- [ ] 集成 JobSpy 的 scrape_jobs() 函数
- [ ] 实现数据转换逻辑（JobSpy → JobPostingDTO）
- [ ] 手动测试验证
- [ ] 补充单元测试（test_indeed_adapter.py）

#### Phase 2.3: 集成 Indeed 到 FastAPI（预计 30 分钟）

**任务清单:**
- [ ] 更新 POST /scrape/indeed 端点
- [ ] 连接 IndeedAdapter
- [ ] 手动测试完整流程
- [ ] 更新 API 文档示例

**参考代码位置:**
- JobSpy 库: `scrape-api-research/JobSpy/jobspy/__init__.py`
- 数据模型: `scrape-api-research/JobSpy/jobspy/model.py`
- 转换函数: [SCRAPER_DATA_FIELDS_ANALYSIS.md](SCRAPER_DATA_FIELDS_ANALYSIS.md) 第 4 节
- TDD 指南: [TDD_DEVELOPMENT_GUIDE.md](TDD_DEVELOPMENT_GUIDE.md)

**详细实施:** 🔖 待实施时详细记录

---

### 阶段 3: SEEK 适配器 ✅ 已完成（实际用时 ~3 小时）

**完成日期:** 2025-12-20

**目标:** 基于 SEEK REST API 实现 SEEK 数据抓取

**已完成任务:**
- ✅ 创建 SeekAdapter 类（~300 行）
- ✅ 实现 SEEK REST API 调用（GET 请求）
- ✅ 实现薪资解析 (parse_salary_range) - 17 测试用例 ✅
- ✅ 实现 HTML 清理 (clean_html) - 16 测试用例 ✅
- ✅ 实现数据转换逻辑（SEEK JSON → JobPostingDTO）
- ✅ 实现字段映射（locations, salaryLabel, workTypes 等）
- ✅ 手动测试通过（成功抓取 plumber 职位）
- ✅ FastAPI 集成完成（/scrape/seek 端点）
- ✅ 端到端测试通过（curl 测试成功）

**关键技术实现:**
- SEEK API: `https://www.seek.com.au/api/jobsearch/v5/search`
- 请求方式: HTTP GET + URL 参数
- Headers: User-Agent, Accept
- 参数: siteKey=AU-Main, where, keywords, page, pageSize, locale
- 无需认证 ✅

**实现的代码文件:**
1. `app/adapters/seek_adapter.py` - SEEK 适配器主类
2. `app/utils/salary_parser.py` - 薪资解析工具（支持 8+ 格式）
3. `app/utils/html_cleaner.py` - HTML 清理工具（BeautifulSoup）
4. `tests/test_salary_parser.py` - 17 个单元测试
5. `tests/test_html_cleaner.py` - 16 个单元测试
6. `test_seek_manual.py` - 手动测试脚本
7. `debug_seek_response.py` - API 调试脚本

**教学文档:**
- ✅ `files/tutorials/SEEK_ADAPTER_DESIGN_GUIDE.md` - 完整的设计教学文档

**测试结果:**
- ✅ 单元测试: 33/33 通过（17 + 16）
- ✅ 总单元测试: 69/69 通过（36 Indeed + 33 SEEK）
- ✅ 手动测试: 成功抓取 5 个职位
- ✅ API 测试: curl 测试返回正确 JSON

**数据字段验证:**
- ✅ 薪资解析正确（$40-$50/小时，时薪转年薪）
- ✅ 地点解析（Adelaide SA, Toowoomba QLD）
- ✅ 工作类型（Full Time）
- ✅ Trade 识别（plumber）
- ✅ 公司名称、描述、URL 等

---

### 阶段 4: 统一数据适配层（预计 2-3 小时）

**目标:** 确保两个爬虫输出格式完全一致

**任务清单:**
- [ ] 实现 JobPostingDTO (Pydantic 模型)
- [ ] 实现数据标准化函数
  - [ ] normalize_employment_type()
  - [ ] extract_requirements()
  - [ ] generate_tags()
- [ ] 实现数据验证
- [ ] 单元测试所有转换函数

**数据模型定义:** 🔖 待实施时详细记录

---

### 阶段 5: FastAPI 端点实现（预计 1-2 小时）

**目标:** 提供 HTTP API 供 .NET 后端调用

**任务清单:**
- [ ] 实现 POST /scrape/indeed 端点
- [ ] 实现 POST /scrape/seek 端点
- [ ] 实现 GET /health 健康检查
- [ ] 添加请求参数验证
- [ ] 添加错误处理
- [ ] 添加日志记录

**API 规范:** 🔖 待实施时详细记录

---

### 阶段 6: .NET 集成测试（预计 1-2 小时）

**目标:** 验证 Python 爬虫服务与 .NET 后端的集成

**任务清单:**
- [ ] 启动 Python FastAPI 服务
- [ ] 更新 .NET ScrapeApiClient 配置
- [ ] 触发 Hangfire 爬虫任务
- [ ] 验证数据流: 爬虫 → Python API → .NET API → PostgreSQL
- [ ] 验证去重逻辑
- [ ] 验证数据标准化

**详细测试步骤:** 🔖 待实施时详细记录

---

### 阶段 7: 错误处理和优化（预计 2-3 小时）

**目标:** 提高爬虫稳定性和性能

**任务清单:**
- [ ] 实现速率限制（避免被封 IP）
- [ ] 实现重试机制（网络错误处理）
- [ ] 实现 User-Agent 轮换
- [ ] 添加详细日志
- [ ] 性能优化（并发抓取）
- [ ] 错误监控和告警

**详细实施:** 🔖 待实施时详细记录

---

## 📁 项目目录结构（计划）

```
scrape-api/                          # Python 爬虫服务根目录
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 应用入口
│   ├── config.py                    # 配置文件
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_posting_dto.py      # 统一数据模型
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py         # 抽象基类
│   │   ├── indeed_adapter.py       # Indeed 适配器
│   │   └── seek_adapter.py         # SEEK 适配器
│   ├── services/
│   │   ├── __init__.py
│   │   └── data_transformer.py     # 数据转换服务
│   └── utils/
│       ├── __init__.py
│       ├── location_parser.py      # 地点解析
│       ├── salary_parser.py        # 薪资解析
│       ├── trade_extractor.py      # Trade 提取
│       └── html_cleaner.py         # HTML 清理
├── tests/
│   ├── test_indeed_adapter.py
│   ├── test_seek_adapter.py
│   └── test_data_transformer.py
├── requirements.txt                 # Python 依赖
├── .env.example                     # 环境变量示例
└── README.md                        # 项目说明
```

---

## 🔧 关键技术实现点

### 1. Indeed 适配器核心代码（示例）

```python
# 🔖 待实施，以下为参考代码
from jobspy import scrape_jobs
from app.models.job_posting_dto import JobPostingDTO
from app.utils.location_parser import parse_location
from app.utils.trade_extractor import extract_trade

class IndeedAdapter:
    def scrape(self, keywords: str, location: str, max_results: int = 50):
        # 使用 JobSpy 库
        df = scrape_jobs(
            site_name=['indeed'],
            search_term=keywords,
            location=location,
            results_wanted=max_results,
            country_indeed='Australia'
        )

        # 转换为统一格式
        jobs = []
        for _, row in df.iterrows():
            state, suburb = parse_location(row['location'])
            trade = extract_trade(row['title'])

            job = JobPostingDTO(
                source='indeed',
                source_id=row.get('id') or self._generate_id(row),
                title=row['title'],
                company=row['company'],
                location_state=state,
                location_suburb=suburb,
                trade=trade,
                employment_type=self._normalize_job_type(row['job_type']),
                pay_range_min=row.get('min_amount'),
                pay_range_max=row.get('max_amount'),
                description=row['description'],
                posted_at=row['date_posted']
            )
            jobs.append(job)

        return jobs
```

### 2. SEEK 适配器核心代码（示例）

```python
# 🔖 待实施，以下为参考代码
import requests
from app.models.job_posting_dto import JobPostingDTO
from app.utils.salary_parser import parse_salary_range
from app.utils.html_cleaner import clean_html

class SeekAdapter:
    BASE_URL = "https://www.seek.com.au/api/jobsearch/v5/search"

    def scrape(self, keywords: str, location: str, classification: str = None):
        jobs = []
        page = 1

        while True:
            params = {
                'siteKey': 'AU-Main',
                'where': location,
                'keywords': keywords,
                'page': page,
                'locale': 'en-AU'
            }

            if classification:
                params['classification'] = classification

            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            for item in data['data']:
                job = self._parse_job(item)
                jobs.append(job)

            # 处理分页
            if page >= self._get_total_pages(data):
                break
            page += 1

        return jobs

    def _parse_job(self, data):
        min_salary, max_salary = parse_salary_range(data.get('salaryLabel', ''))

        return JobPostingDTO(
            source='seek',
            source_id=data['id'],
            title=data.get('title'),
            company=data.get('advertiser', {}).get('description'),
            location_state=data.get('locations', [{}])[0].get('label'),
            location_suburb=self._extract_suburb(data),
            trade=self._extract_classification(data),
            employment_type=data.get('workTypes', [None])[0],
            pay_range_min=min_salary,
            pay_range_max=max_salary,
            description=clean_html(data.get('teaser')),
            posted_at=data.get('listingDate')
        )
```

### 3. FastAPI 端点（示例）

```python
# 🔖 待实施，以下为参考代码
from fastapi import FastAPI, HTTPException
from app.adapters.indeed_adapter import IndeedAdapter
from app.adapters.seek_adapter import SeekAdapter

app = FastAPI(title="Job Intelligence Scraper API")

@app.post("/scrape/indeed")
async def scrape_indeed(keywords: str, location: str, max_results: int = 50):
    try:
        adapter = IndeedAdapter()
        jobs = adapter.scrape(keywords, location, max_results)
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/seek")
async def scrape_seek(keywords: str, location: str, classification: str = None):
    try:
        adapter = SeekAdapter()
        jobs = adapter.scrape(keywords, location, classification)
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## ⚠️ 风险和注意事项

### 1. SEEK API 合规性
- ⚠️ 使用 SEEK 内部 API 可能违反使用条款
- ✅ V1 阶段：内部测试，风险可控
- ⚠️ V2 Production：需要评估商业化风险
- 📋 参考: [SEEK_API_COMPARISON.md](SEEK_API_COMPARISON.md) 第 7-8 节

### 2. 速率限制
- ✅ 实现请求延迟（每次请求间隔 1-2 秒）
- ✅ User-Agent 轮换
- ✅ 错误码 429 检测和退避

### 3. 数据质量
- ⚠️ JobSpy 可能返回空的 ID
- ⚠️ SEEK 薪资字符串格式不统一
- ⚠️ Trade 提取可能不准确（需要关键词列表）

### 4. 依赖管理
- ✅ JobSpy 库版本: v1.1.82（2025-03-21）
- ⚠️ 需要定期更新检查库的兼容性

---

## 📊 实际工作量统计

| 阶段 | 预计时间 | 实际时间 | 状态 |
|------|---------|---------|------|
| 阶段 1: FastAPI 骨架 | 2-3 小时 | 1 小时 | ✅ 完成 |
| 阶段 2: Indeed 适配器（含 TDD） | 2-3 小时 | 2.5 小时 | ✅ 完成 |
| 阶段 3: SEEK 适配器（含 TDD） | 4-5 小时 | 3 小时 | ✅ 完成 |
| 阶段 4: P1 优化（测试+错误处理+位置） | - | 3 小时 | ✅ 完成 |
| 阶段 5: .NET 集成 | 1-2 小时 | 3 小时 | ✅ 完成 |
| 阶段 6: 数据库配置 | - | 1 小时 | ✅ 完成 |
| 阶段 7: 文档创建 | - | 2 小时 | ✅ 完成 |
| **总计** | **14-21 小时** | **15.5 小时** | ✅ **全部完成** |

**实际用时:** 约 2 天（2025-12-18 至 2025-12-22）

---

## ✅ 最终完成状态

### Python 爬虫 API（端口 8000）
- ✅ FastAPI 框架完整
- ✅ SEEK 适配器生产就绪
- ✅ Indeed 适配器生产就绪
- ✅ 5 个工具函数（位置、薪资、Trade、工作类型、HTML）
- ✅ 103 个单元测试，100% 通过
- ✅ 端到端测试成功

### .NET 后端集成（端口 5000）
- ✅ IngestController 创建（3 个端点）
- ✅ ScrapeApiClient 更新
- ✅ 数据模型完全对齐
- ✅ PostgreSQL 数据库配置
- ✅ 端到端测试通过

### 数据质量验证
- ✅ SEEK：位置 100%，Trade 100%，薪资 80%
- ✅ Indeed：位置 100%，Trade 100%，描述质量优秀

### 文档体系
- ✅ PostgreSQL 教程
- ✅ 启动指南
- ✅ 集成完成报告
- ✅ 所有项目文档更新

---

## 🎯 下一步行动

**当前状态：** ✅ Python 爬虫 + .NET 集成全部完成

**下一步：**
1. **数据持久化**（优先级 P1）
   - 修改 IngestController 保存数据到数据库
   - 完善去重逻辑
   - 测试完整数据流

2. **查询 API 实现**（优先级 P2）
   - 完善 JobsController
   - 测试搜索和过滤功能

3. **定时任务**（优先级 P3）
   - Hangfire 定期数据采集

---

## 📚 相关文档

- [爬虫调研分析](SCRAPER_RESEARCH_ANALYSIS.md) - JobSpy 和 SeekSpider 详细调研
- [融合方案设计](SCRAPER_FUSION_ANALYSIS.md) - 架构设计和技术选型
- [SEEK API 对比](SEEK_API_COMPARISON.md) - SEEK 官方 vs 内部 API
- [数据字段分析](SCRAPER_DATA_FIELDS_ANALYSIS.md) - 完整的数据映射方案
- [下一步计划](NEXT_STEPS.md) - 总体开发路线图

---

**说明:** 本文档为实施计划，所有代码示例仅供参考。实际实施时将根据具体情况调整，并详细记录每个步骤的实施细节和遇到的问题。
