# Job Intelligence Scraper API

> Python FastAPI 爬虫服务 - 为 .NET 后端提供职位数据抓取

## 📋 概述

此项目是 Job Intelligence Platform 的爬虫服务组件，负责从多个求职平台抓取职位数据：

- ✅ **Indeed** - 使用 JobSpy 库
- ✅ **SEEK** - 使用 SEEK 内部 API
- 🔖 **未来可扩展** - LinkedIn, Glassdoor, Google Jobs 等

## 🏗️ 架构设计

### 可扩展设计

```
BaseJobAdapter (抽象基类)
    ├── IndeedAdapter (基于 JobSpy)
    ├── SeekAdapter (基于 SEEK API)
    └── 🔖 未来: LinkedInAdapter, GlassdoorAdapter...
```

所有适配器：
- 继承 `BaseJobAdapter`
- 实现 `scrape()` 方法
- 返回统一的 `JobPostingDTO` 格式

### 数据流

```
求职平台 → 平台适配器 → 数据转换 → 统一 DTO → FastAPI → .NET Backend
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件（可选，默认配置已可用）
nano .env
```

### 3. 运行服务

```bash
# 开发模式（自动重载）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 📁 项目结构

```
scrape-api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 应用入口
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_posting_dto.py       # 数据模型
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py          # 抽象基类 ⭐
│   │   ├── indeed_adapter.py        # 🔖 待实现
│   │   └── seek_adapter.py          # 🔖 待实现
│   ├── services/
│   │   ├── __init__.py
│   │   └── data_transformer.py      # 🔖 待实现
│   └── utils/
│       ├── __init__.py
│       ├── location_parser.py       # 🔖 待实现
│       ├── salary_parser.py         # 🔖 待实现
│       ├── trade_extractor.py       # 🔖 待实现
│       └── html_cleaner.py          # 🔖 待实现
├── tests/
│   └── (单元测试)                    # 🔖 待实现
├── requirements.txt                 # Python 依赖
├── .env.example                     # 环境变量示例
├── .gitignore
└── README.md
```

## 🔌 API 端点

### 系统端点

#### `GET /health`
健康检查

**响应示例:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-12-18T12:00:00Z",
  "platforms": ["indeed", "seek"]
}
```

### 爬虫端点

#### `POST /scrape/indeed`
抓取 Indeed 职位

**请求体:**
```json
{
  "keywords": "tiler",
  "location": "Adelaide",
  "max_results": 50
}
```

**响应:**
```json
{
  "platform": "indeed",
  "jobs": [
    {
      "source": "indeed",
      "source_id": "abc123",
      "title": "Experienced Tiler",
      "company": "Premier Tiling",
      "location_state": "SA",
      "location_suburb": "Adelaide",
      "trade": "tiler",
      "employment_type": "Full Time",
      "pay_range_min": 70000.0,
      "pay_range_max": 85000.0,
      "description": "We are seeking...",
      "posted_at": "2025-12-15T08:00:00Z"
    }
  ],
  "count": 1,
  "scraped_at": "2025-12-18T12:00:00Z"
}
```

#### `POST /scrape/seek`
抓取 SEEK 职位

**请求体:**
```json
{
  "keywords": "plumber",
  "location": "Adelaide",
  "max_results": 50,
  "classification": "1225"  // Trades & Services
}
```

## 🛠️ 开发状态

### ✅ 已完成（阶段 1）

- [x] 项目目录结构
- [x] 依赖配置 (requirements.txt)
- [x] 环境变量管理 (.env)
- [x] 可扩展的适配器基类设计
- [x] 统一数据模型 (JobPostingDTO)
- [x] FastAPI 应用骨架
- [x] 健康检查端点
- [x] API 文档 (Swagger/ReDoc)

### 🔖 待实施

- [ ] **阶段 2**: Indeed 适配器实现
- [ ] **阶段 3**: SEEK 适配器实现
- [ ] **阶段 4**: 数据转换工具函数
- [ ] **阶段 5**: 单元测试
- [ ] **阶段 6**: .NET 集成测试
- [ ] **阶段 7**: 错误处理和优化

## 🔧 核心设计特点

### 1. 可扩展性

通过抽象基类 `BaseJobAdapter`，轻松添加新平台：

```python
class LinkedInAdapter(BaseJobAdapter):
    @property
    def platform_name(self) -> str:
        return "linkedin"

    def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        # 实现 LinkedIn 爬取逻辑
        pass
```

### 2. 统一数据格式

所有平台返回相同的 `JobPostingDTO`，确保与 .NET 后端兼容。

### 3. 配置化

所有平台特定配置通过环境变量管理，便于部署。

### 4. 日志和监控

使用 Loguru 提供结构化日志，便于调试和监控。

## 📚 相关文档

- [爬虫实施计划](../docs/development/SCRAPER_IMPLEMENTATION_PLAN.md)
- [数据字段分析](../docs/development/SCRAPER_DATA_FIELDS_ANALYSIS.md)
- [SEEK API 对比](../docs/design/SEEK_API_COMPARISON.md)
- [融合方案设计](../docs/development/SCRAPER_FUSION_ANALYSIS.md)
- [完整文档索引](../docs/README.md)

## ⚠️ 注意事项

### SEEK API 合规性

- SEEK 内部 API 为非公开 API
- V1 阶段：内部测试使用，风险可控
- 生产环境：需要评估合规风险

### 速率限制

- 默认请求延迟：2 秒
- 建议使用 User-Agent 轮换
- 监控 429 错误码

## 📝 下一步

1. 实现 Indeed 适配器（最简单，验证流程）
2. 实现 SEEK 适配器
3. 添加单元测试
4. 与 .NET 后端集成测试

---

**版本:** 1.0.0
**最后更新:** 2025-12-18
**状态:** 🔖 阶段 1 完成，准备实施阶段 2
