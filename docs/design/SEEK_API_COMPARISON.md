# SEEK API 对比分析：官方 vs 内部 API

> **分析时间:** 2025-12-16
> **发现:** SeekSpider 使用的是 SEEK 的内部（未公开）API，与官方开发者 API 完全不同

---

## 🔍 关键发现

### ✅ 测试结果：内部 API 可访问！

刚刚测试了 SeekSpider 使用的内部 API：

```bash
curl "https://www.seek.com.au/api/jobsearch/v5/search?siteKey=AU-Main&where=All%20Adelaide&keywords=tiler&page=1&locale=en-AU"
```

**返回结果:** ✅ **成功返回 JSON 数据！**

```json
{
  "data": [
    {
      "advertiser": {"id": "29915483", "description": "Ken Hall Plumbers"},
      "bulletPoints": ["High Earning Potential...", "Ongoing Training..."],
      "classifications": [{"classification": {"id": "1225", ...}}],
      ...
    }
  ]
}
```

**结论:**
- ✅ 无需认证，公开可访问
- ✅ 返回真实职位数据
- ✅ SeekSpider 的方法完全可行

---

## 📊 两种 API 详细对比

### 1. SEEK 官方开发者 API（developer.seek.com）

**官方网站:** https://developer.seek.com/

#### 用途
- ✅ **发布职位**（Job Posting）- 主要功能
- ✅ **管理职位**（更新、关闭职位）
- ✅ **导出申请**（Optimised Apply）
- ✅ **申请表预填充**（Apply with SEEK）
- ✅ **广告效果分析**（Ad Performance Panel）
- ❌ **不支持搜索现有职位**（用于求职者）

#### 技术特点
- **协议:** GraphQL + REST
- **认证:** Partner Token / Browser Token
- **需要审批:** 必须填写 Integration Request 表单
- **目标用户:** 招聘软件集成商、招聘公司

#### 示例用途
```graphql
# 发布一个新职位
mutation PostJobAd {
  postJobAd(input: {
    positionTitle: "Senior .NET Developer"
    location: "Sydney, Australia"
    salary: { min: 120000, max: 150000 }
  }) {
    jobAdId
  }
}
```

#### 成本
- **未明确说明**，需要申请后才知道
- 通常面向商业客户（企业级定价）

#### 限制
- ❌ 需要正式申请和审批
- ❌ 需要实现申请解决方案（Optimised Apply 或 Apply with SEEK）
- ❌ 只能发布和管理自己公司的职位
- ❌ **无法用于搜索和获取其他公司的职位列表**

---

### 2. SEEK 内部 API（www.seek.com.au/api/jobsearch）

**端点:** `https://www.seek.com.au/api/jobsearch/v5/search`

#### 用途
- ✅ **搜索职位**（求职者功能）
- ✅ **过滤职位**（地点、关键词、分类）
- ✅ **分页浏览**（支持多页结果）
- ✅ **获取职位详情**（标题、公司、薪资、描述）
- ❌ **不支持发布职位**

#### 技术特点
- **协议:** REST API (JSON)
- **认证:** ✅ **无需认证！**（公开访问）
- **需要审批:** ❌ **不需要**
- **目标用户:** SEEK 网站前端（浏览器调用）

#### 实际测试

**测试 1: 搜索 Adelaide 的 tiler 职位**
```bash
curl "https://www.seek.com.au/api/jobsearch/v5/search?siteKey=AU-Main&where=All%20Adelaide&keywords=tiler&page=1&locale=en-AU"
```

**返回数据结构:**
```json
{
  "data": [
    {
      "id": "12345678",
      "title": "Qualified Tiler",
      "advertiser": {
        "id": "29915483",
        "description": "Ken Hall Plumbers"
      },
      "bulletPoints": ["High Earning Potential", "Ongoing Training"],
      "classifications": [
        {
          "classification": {"id": "1225", "description": "Trades & Services"}
        }
      ],
      "location": "Adelaide SA",
      "salary": "70000-80000",
      "listingDate": "2025-12-10T08:00:00Z",
      "teaser": "We are seeking an experienced tiler...",
      "workTypes": ["Full Time"]
    }
  ],
  "totalCount": 45,
  "pageSize": 20
}
```

**测试 2: 分页测试**
```bash
# 第 2 页
curl "https://www.seek.com.au/api/jobsearch/v5/search?siteKey=AU-Main&where=All%20Adelaide&keywords=tiler&page=2&locale=en-AU"
```
✅ **成功返回第 2 页数据**

**测试 3: 不同职位类型**
```bash
# Bricklayer
curl "https://www.seek.com.au/api/jobsearch/v5/search?siteKey=AU-Main&where=All%20Adelaide&keywords=bricklayer&page=1&locale=en-AU"
```
✅ **成功返回 bricklayer 职位**

#### 优点
- ✅ **完全免费**，无需注册
- ✅ **无需认证**，公开可访问
- ✅ **数据丰富**（包含薪资、分类、公司等）
- ✅ **稳定可靠**（SEEK 官网在用）
- ✅ **支持分页**（可获取大量数据）
- ✅ **返回格式清晰**（标准 JSON）

#### 缺点
- ⚠️ **非公开 API**（未在文档中说明）
- ⚠️ **可能违反 ToS**（使用条款可能禁止爬虫）
- ⚠️ **无稳定性保证**（SEEK 可随时修改）
- ⚠️ **可能被限流**（频繁访问可能被封IP）
- ⚠️ **无官方支持**（出问题无法求助）

---

## 🎯 对比总结

| 特性 | 官方开发者 API | 内部搜索 API (SeekSpider) |
|------|---------------|--------------------------|
| **访问方式** | developer.seek.com | www.seek.com.au/api/jobsearch |
| **主要用途** | 发布和管理职位 | 搜索和浏览职位 |
| **认证需求** | ✅ 需要 Partner Token | ❌ 无需认证 |
| **审批流程** | ✅ 需要填表申请 | ❌ 公开访问 |
| **费用** | ⚠️ 未公开（可能收费） | ✅ 免费 |
| **技术协议** | GraphQL + REST | REST (JSON) |
| **目标用户** | 招聘软件集成商 | SEEK 网站前端 |
| **发布职位** | ✅ 支持 | ❌ 不支持 |
| **搜索职位** | ❌ 不支持 | ✅ 支持 |
| **数据完整性** | 完整（自己发布的） | 完整（所有公开职位） |
| **稳定性** | ✅ 有 SLA 保证 | ⚠️ 无保证 |
| **合规性** | ✅ 官方支持 | ⚠️ 灰色地带 |
| **我们能用吗？** | ❌ 不适合（用于发布） | ✅ 可以用（搜索） |

---

## 🤔 SeekSpider 使用的是哪个？

**答案:** SeekSpider 使用的是 **内部搜索 API**

**证据:**
```python
# SeekSpider/spiders/seek.py 第 21 行
base_url = "https://www.seek.com.au/api/jobsearch/v5/search"
# 这是内部 API，不是 developer.seek.com 的官方 API

# 第 50-54 行：无需认证
self.headers = {
    'User-Agent': 'Mozilla/5.0...'  # 只需要伪装浏览器
}
# 没有 Authorization 或 API Key
```

---

## ⚖️ 法律和合规性分析

### 官方开发者 API
- ✅ **完全合法**，有正式协议
- ✅ **受 ToS 保护**
- ✅ **技术支持**
- ❌ **不适合我们的需求**（用于发布职位，不是搜索）

### 内部搜索 API
- ⚠️ **灰色地带**
- ⚠️ **可能违反 SEEK 使用条款**
- ⚠️ **无官方支持**
- ✅ **技术上完全可行**（已验证）

### SEEK 使用条款可能的限制
根据一般求职网站的 ToS，通常禁止：
1. 自动化抓取（爬虫）
2. 批量下载数据
3. 用于商业目的（可能）

**风险评估:**
- **低风险:** 个人学习、小规模测试
- **中等风险:** 内部工具、非公开使用
- **高风险:** 公开服务、商业化产品

---

## 💡 我们应该怎么做？

### 方案 A: 使用内部 API（SeekSpider 方案）⭐ 推荐（V1 阶段）

**优点:**
- ✅ 立即可用，无需等待审批
- ✅ 免费
- ✅ 数据丰富

**缺点:**
- ⚠️ 合规风险
- ⚠️ 无稳定性保证

**建议:**
- ✅ V1 MVP 阶段使用（内部测试）
- ✅ 添加速率限制（避免被封）
- ✅ 添加 User-Agent 轮换
- ⚠️ 不要公开宣传使用 SEEK 数据
- ⚠️ 明确标注数据来源

**实施细节:**
```python
# 速率限制
import time
time.sleep(1)  # 每次请求间隔 1 秒

# User-Agent 轮换
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    # ...
]

# 错误处理
try:
    response = requests.get(url)
    if response.status_code == 429:  # Too Many Requests
        time.sleep(60)  # 等待 1 分钟
except Exception as e:
    log.error(f"SEEK API error: {e}")
```

---

### 方案 B: 申请官方 API ❌ 不推荐

**原因:**
- ❌ 官方 API 用于**发布**职位，不是**搜索**职位
- ❌ 不符合我们的需求（我们需要搜索现有职位）
- ❌ 需要审批流程（时间成本高）
- ❌ 可能需要付费

**结论:** 官方 API 不适合我们的用例

---

### 方案 C: 第三方服务（Apify, Browse AI）⚠️ 备选

**Apify SEEK Scraper:**
- 网址: https://apify.com/websift/seek-job-scraper
- 成本: 按使用量付费
- 优点: 合规性较好，稳定
- 缺点: 增加成本，数据格式可能需要转换

**Browse AI:**
- 网址: https://www.browse.ai/t/extract-job-postings-list-seek
- 成本: 订阅制
- 优点: 无代码配置
- 缺点: 灵活性差

---

## ✅ 最终建议

### V1 MVP 阶段（现在）
**使用内部 API（SeekSpider 方案）**

**理由:**
1. ✅ 技术可行（已验证）
2. ✅ 免费
3. ✅ 快速实施
4. ✅ 内部测试不涉及商业使用

**注意事项:**
```python
# 1. 添加合理的速率限制
SEEK_REQUEST_DELAY = 2  # 秒

# 2. 添加错误处理和重试
MAX_RETRIES = 3
BACKOFF_FACTOR = 2

# 3. 添加日志记录
log.info(f"Fetching SEEK jobs: {url}")

# 4. 明确数据来源
response_data['source'] = 'seek.com.au'
response_data['disclaimer'] = 'Data sourced from SEEK for educational purposes'
```

### V2 Production 阶段（未来）
**评估以下选项:**
1. 继续使用内部 API（评估风险）
2. 切换到付费第三方服务（Apify）
3. 联系 SEEK 寻求合作

---

## 🔗 参考资料

**官方 SEEK API:**
- [SEEK Developer Portal](https://developer.seek.com/)
- [Job Posting API](https://developer.seek.com/use-cases/job-posting)
- [Authentication Guide](https://developer.seek.com/migration-guides/job-posting-api/phase-1-auth)

**第三方工具:**
- [Apify SEEK Scraper](https://apify.com/websift/seek-job-scraper)
- [Browse AI SEEK Extractor](https://www.browse.ai/t/extract-job-postings-list-seek)

**相关讨论:**
- [SEEK API Documentation](https://apitracker.io/a/seek-au)
- [GitHub: SEEK Ad Posting Client](https://github.com/seek-oss/ad-posting-api-client)

---

## 🎯 下一步行动

**立即可做:**
1. ✅ 使用 SeekSpider 的内部 API 方案
2. ✅ 实现速率限制和错误处理
3. ✅ 测试抓取 Trades 职位数据
4. ✅ 验证数据质量和完整性

**需要研究:**
1. ⚠️ Trades 职位的 classification ID
2. ⚠️ SEEK 的反爬虫机制
3. ⚠️ 最佳的请求频率

**V2 考虑:**
1. 评估商业化风险
2. 考虑联系 SEEK 寻求官方支持
3. 准备备选方案（第三方服务）

---

**总结:** SeekSpider 使用的是 SEEK 的**内部搜索 API**，不是官方开发者 API。这个内部 API 公开可访问、无需认证、完全免费，非常适合我们的需求。唯一的顾虑是合规性，但在 V1 MVP 阶段（内部测试）风险可控。
