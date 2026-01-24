# Job Intelligence Platform - 项目路线图

**创建日期**: 2026-01-19
**最后更新**: 2026-01-19
**状态**: ✅ 当前活跃
**文档类型**: 战略规划 / 实施指南

---

## 📋 文档说明

本文档整合了项目的完整发展路线,包括:
- ✅ **当前状态评估** - MVP V1 已完成并部署
- 📋 **短期计划** (1-2 周) - Bug 修复验证 + 监控优化
- 🎯 **中期计划** (2-4 周) - AI 功能 / 前端开发 / 用户系统
- 🚀 **长期愿景** (2-3 个月) - 完整 SaaS 产品

**与现有文档的关系**:
- 本文档是 **总规划**,整合了所有子文档的内容
- [V2_IMPLEMENTATION_PLAN.md](../development/V2_IMPLEMENTATION_PLAN.md) - 详细的技术实施步骤
- [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md) - 性能优化任务清单
- [LOGGING_MONITORING_PLAN.md](LOGGING_MONITORING_PLAN.md) - 监控方案设计
- [DAILY_PLAN.md](../development/DAILY_PLAN.md) - 日常工作记录

---

## 🎯 目录

- [当前项目状态](#当前项目状态-2026-01-19)
- [核心决策点](#核心决策点)
- [短期路线 (1-2 周)](#短期路线-1-2-周---稳定性验证)
- [中期路线 A: 快速路线](#中期路线-a-快速路线-1-2-周---面试优先)
- [中期路线 B: 深度路线](#中期路线-b-深度路线-2-4-周---ai-优先)
- [中期路线 C: 全栈路线](#中期路线-c-全栈路线-3-4-周---平衡发展)
- [长期愿景](#长期愿景-2-3-个月---完整产品)
- [技术栈演进](#技术栈演进)
- [成功指标](#成功指标)

---

## 当前项目状态 (2026-01-19)

### ✅ 已完成功能 (MVP V1)

#### 后端架构 (完成度: 95%)

**Python 爬虫 API** (scrape-api/):
```
✅ 核心功能:
  - SeekAdapter (SEEK 平台爬虫)
  - IndeedAdapter (Indeed 平台爬虫)
  - 职位数据标准化 (JobPostingDTO)
  - 地点解析增强 (支持复杂格式)
  - 自定义异常体系 (11 种异常类型)

✅ 测试覆盖:
  - 100 个单元测试 (100% 通过)
  - 测试覆盖率: 核心逻辑 90%+
  - TDD 开发流程完整

✅ API 端点:
  - POST /scrape/seek
  - POST /scrape/indeed
  - GET /health
```

**.NET 后端 API** (src/):
```
✅ 核心功能:
  - 数据摄取管道 (IngestionPipeline)
  - 去重服务 (fingerprint + source_id)
  - 数据标准化 (Normalizer)
  - Repository 模式 (JobRepository)
  - Hangfire 定时任务 (65 个任务)

✅ API 端点 (8 个):
  - GET /api/health
  - GET /api/jobs
  - GET /api/jobs/{id}
  - GET /api/analytics/summary
  - GET /api/analytics/by-trade
  - GET /api/analytics/by-state
  - GET /api/analytics/trends
  - POST /api/scrape/trigger

✅ 最近修复:
  - DateTime UTC 转换 (2026-01-19)
  - 去重逻辑优化 (两级检查)
  - GetBySourceIdAsync 方法补充
```

**数据库** (PostgreSQL 16):
```
✅ Azure PostgreSQL Flexible Server
  - B1MS 免费层 (750 hours/月)
  - 32 GB 存储
  - 自动备份启用
  - SSL 连接

✅ 数据库架构:
  - job_postings 表 (主表)
  - 唯一约束: (source, source_id)
  - 去重字段: fingerprint, content_hash
  - 状态: 已清空,等待新数据 (2026-01-19)
```

#### 部署架构 (生产环境运行)

```
当前架构 (2026-01-19):
┌─────────────────────────────────────────┐
│ Azure PostgreSQL Flexible Server       │
│ - 免费层 B1MS                           │
│ - PostgreSQL 16                         │
│ - 32 GB Storage                         │
│ - 数据已清空,重新开始                   │
└─────────────────────────────────────────┘
            ↑ SSL Connection
            │
┌─────────────────────────────────────────┐
│ Azure VM B1s (847 MB RAM)               │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Docker Compose                      │ │
│ │                                     │ │
│ │ ├─ Python API (43 MB)               │ │
│ │ │  - FastAPI                        │ │
│ │ │  - 爬虫适配器                     │ │
│ │ │  - DateTime 修复 ✅              │ │
│ │ │                                   │ │
│ │ └─ .NET API (140 MB)                │ │
│ │    - ASP.NET Core 8                 │ │
│ │    - Hangfire Dashboard             │ │
│ │    - 去重逻辑修复 ✅               │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 内存使用: 728 MB (86%) ⚠️ 需观察      │
│ 可用内存: 118 MB                        │
└─────────────────────────────────────────┘
            ↑
            │ GitHub Actions CI/CD
            │
┌─────────────────────────────────────────┐
│ GitHub Repository                       │
│ - 自动构建 Docker 镜像                  │
│ - 推送到 GHCR                           │
│ - 自动部署到 VM                         │
└─────────────────────────────────────────┘
```

**性能指标**:
- API 响应时间: < 100ms ✅
- 数据库连接: 稳定 ✅
- 内存使用率: 86% ⚠️ (目标 < 85%)
- 错误日志: 0 个 ✅ (2026-01-19 修复后)

**成本**: $0/月 (完全使用免费资源)

---

### ⚠️ 待验证事项 (24-48 小时)

**监控任务**:
1. ⏰ **内存使用趋势** - 每 6-12 小时检查
   - 目标: 保持 < 85%
   - 如果持续增长,需分析根因

2. ⏰ **Bug 修复验证** - 观察日志
   - DateTime Kind 错误: 预期 0 个
   - Duplicate Key 错误: 预期 0 个
   - Hangfire 任务执行: 预期正常

3. ⏰ **数据质量** - 新爬取数据验证
   - 去重逻辑正确工作
   - 数据字段完整
   - 无插入失败

**参考文档**: [BUG_FIXES_2026-01-19.md](BUG_FIXES_2026-01-19.md)

---

### ❌ 缺失功能

**用户端功能**:
- ❌ 前端 UI (无用户界面)
- ❌ 用户认证系统
- ❌ 保存职位功能
- ❌ Job Alerts 通知
- ❌ 个人 Dashboard

**AI 功能**:
- ❌ 职位描述智能解析
- ❌ 职位匹配推荐
- ❌ 简历优化建议
- ❌ 语义搜索

**运维功能**:
- ⚠️ Application Insights (计划中)
- ⚠️ Hangfire Dashboard (未开放访问)
- ⚠️ 自动化告警

---

## 核心决策点

在继续开发之前,需要明确以下核心问题:

### 1. 主要目标 (必答)

**选项**:
- **A. 面试准备** (1-2 周完成可演示项目)
- **B. 技术学习** (深入 AI/前端技术)
- **C. 创业准备** (打造可商业化产品)
- **D. 平衡发展** (兼顾以上目标)

**影响**: 决定了下一步的优先级和时间分配

---

### 2. 时间框架 (必答)

**选项**:
- **A. 1-2 周** (快速完成基础功能)
- **B. 2-4 周** (中等深度开发)
- **C. 1-3 个月** (完整产品打磨)

**影响**: 决定了功能范围和深度

---

### 3. 技术兴趣 (必答)

**选项**:
- **A. 前端开发** (React/Vue + TypeScript)
- **B. AI/LLM 集成** (OpenAI/LangChain)
- **C. 全栈架构** (系统设计 + DevOps)
- **D. 都想尝试** (需要更长时间)

**影响**: 决定了中期路线的选择

---

### 4. 当前短板 (选填,用于优化学习路径)

**可能的短板**:
- 缺少前端项目经验
- 没有 AI 应用经验
- 缺少完整的全栈项目
- 面试准备不足

---

## 短期路线 (1-2 周) - 稳定性验证

**时间**: 2026-01-19 ~ 2026-01-26
**目标**: 确保 Bug 修复有效,系统稳定运行
**状态**: ⏳ 进行中

### Week 1 (2026-01-19 ~ 2026-01-25)

#### Day 1-2: 持续监控 ⏰

**每日任务** (每 6-12 小时执行):
```bash
# 1. 检查系统健康
az vm run-command invoke \
  --resource-group job-intelligence-rg \
  --name jobintel-vm \
  --command-id RunShellScript \
  --scripts "curl -s http://localhost:5000/api/health"

# 2. 检查错误日志
docker logs jobintel-dotnet-api --tail 200 | grep -i "error\|exception"

# 3. 检查内存使用
docker stats --no-stream
```

**成功标准**:
- ✅ API 持续健康
- ✅ 无 DateTime/Duplicate Key 错误
- ✅ 内存使用率 < 85%
- ✅ Hangfire 任务正常执行

**失败处理**:
- 如果内存 > 90%: 分析根因,考虑优化
- 如果出现错误: 回滚或快速修复

---

#### Day 3-4: 监控优化 (可选) 📊

**选项 A: 开放 Hangfire Dashboard**
```bash
# 配置 SSH 隧道访问
ssh -L 5000:localhost:5000 azureuser@20.92.200.112

# 访问 http://localhost:5000/hangfire
```

**收益**:
- ✅ 可视化任务执行状态
- ✅ 查看失败任务和重试
- ✅ 手动触发任务

**选项 B: 配置 Application Insights** (1-2 天)

**步骤**: 参考 [LOGGING_MONITORING_PLAN.md](LOGGING_MONITORING_PLAN.md#中期方案-1-2-天)

**收益**:
- ✅ 自动收集性能指标
- ✅ 错误追踪和分析
- ✅ 告警规则配置

**决策点**: 如果系统稳定,可延后到中期路线

---

#### Day 5-7: 数据质量验证 ✅

**任务**:
1. 等待 Hangfire 定时任务执行
2. 验证新爬取的数据:
   - 检查数据库记录数
   - 抽查数据字段完整性
   - 验证去重逻辑有效

**验证脚本**:
```bash
# 检查数据库记录数
curl http://localhost:5000/api/health

# 查看最新职位
curl http://localhost:5000/api/jobs?limit=10

# 检查去重 (相同 source_id 应该只有一条)
# 通过 PostgreSQL 查询
```

**成功标准**:
- ✅ 数据成功插入
- ✅ 无重复记录 (相同 source + source_id)
- ✅ DateTime 字段格式正确
- ✅ 地点字段解析准确

---

### Week 2 (2026-01-26 ~ 2026-02-01): 决策和准备

#### Day 8-9: 路线决策 🤔

**任务**:
1. 回顾 Week 1 监控结果
2. 评估系统稳定性
3. 决定中期路线 (A/B/C)

**决策依据**:
- ✅ 系统稳定 → 可以开始新功能开发
- ⚠️ 仍有问题 → 继续优化和修复

---

#### Day 10-14: 技术准备 (根据选定路线)

**路线 A (快速路线) 准备**:
- [ ] 学习 React/Next.js 基础
- [ ] 学习 OpenAI API 使用
- [ ] 准备前端项目模板

**路线 B (深度路线) 准备**:
- [ ] 深入研究 LangChain
- [ ] 设计 AI 功能架构
- [ ] 准备测试数据集

**路线 C (全栈路线) 准备**:
- [ ] 设计用户数据库架构
- [ ] 研究 JWT 认证最佳实践
- [ ] 准备前后端集成方案

---

### 短期路线交付物

**Week 1 结束**:
- ✅ Bug 修复验证报告
- ✅ 系统稳定性确认
- ✅ 数据质量验证
- 📊 (可选) 监控系统配置

**Week 2 结束**:
- ✅ 中期路线决策
- ✅ 技术准备完成
- 📋 下一阶段详细计划

---

## 中期路线 A: 快速路线 (1-2 周) - 面试优先

**时间**: 2 周
**目标**: 最快速度完成可演示的全栈 + AI 项目
**适合**: 急需面试准备,时间紧迫

### Week 1: 基础前端 + AI 功能

#### Day 1-3: 前端基础框架 🎨

**技术选型**:
```
框架: Next.js 14 (App Router)
语言: TypeScript
样式: Tailwind CSS
UI 库: shadcn/ui (推荐) 或 Material-UI
状态: Zustand (轻量) 或 Context API
```

**快速启动**:
```bash
npx create-next-app@latest job-intelligence-frontend
# 选择: TypeScript, Tailwind CSS, App Router

cd job-intelligence-frontend
npm install axios zustand lucide-react
```

**核心页面** (最小化):
1. **首页** (`app/page.tsx`):
   - Logo + 搜索框
   - 简单的 Hero Section
   - "立即搜索" CTA

2. **职位列表页** (`app/jobs/page.tsx`):
   - 简单的卡片布局
   - 基础筛选 (trade, location)
   - 分页 (10 条/页)

3. **职位详情页** (`app/jobs/[id]/page.tsx`):
   - 职位信息展示
   - AI 解析结果 (后续添加)
   - "申请" 按钮 (跳转外部)

**实施重点**:
- ✅ 功能优先,不追求完美设计
- ✅ 使用现成 UI 组件,减少开发时间
- ✅ 响应式设计 (移动端基本可用)

**参考**: [V2_IMPLEMENTATION_PLAN.md - Phase 3](../development/V2_IMPLEMENTATION_PLAN.md#phase-3-前端框架和基础页面)

---

#### Day 4-5: AI 职位解析功能 🤖

**功能**: 使用 GPT-4 智能解析职位描述

**价值**:
- ✅ 提取关键信息 (技能、经验、薪资)
- ✅ 简化用户阅读
- ✅ 展示 AI 集成能力

**技术方案**:

**后端实现** (.NET API):
```csharp
// src/JobIntel.Api/Controllers/AIController.cs
[HttpPost("api/ai/analyze-job")]
public async Task<IActionResult> AnalyzeJob([FromBody] AnalyzeRequest request)
{
    var job = await _jobRepository.GetByIdAsync(request.JobId);

    var openAIClient = new OpenAIClient(Environment.GetEnvironmentVariable("OPENAI_API_KEY"));

    var prompt = $@"
分析以下职位描述,提取关键信息:

职位标题: {job.Title}
公司: {job.Company}
描述: {job.Description}

请用 JSON 格式返回:
{{
  ""skills"": [""技能1"", ""技能2""],
  ""experience"": ""经验要求"",
  ""salaryRange"": ""薪资范围 (如有)"",
  ""keyResponsibilities"": [""职责1"", ""职责2""],
  ""summary"": ""一句话总结""
}}
";

    var response = await openAIClient.GetCompletionAsync(prompt, temperature: 0.3);

    return Ok(new { analysis = response });
}
```

**前端集成**:
```typescript
// app/jobs/[id]/page.tsx
const [aiAnalysis, setAiAnalysis] = useState(null);

const analyzeJob = async () => {
  const res = await fetch('/api/ai/analyze-job', {
    method: 'POST',
    body: JSON.stringify({ jobId: id })
  });
  const data = await res.json();
  setAiAnalysis(data.analysis);
};

// 显示 AI 分析结果
{aiAnalysis && (
  <div className="ai-analysis">
    <h3>AI 智能解析</h3>
    <p><strong>总结:</strong> {aiAnalysis.summary}</p>
    <p><strong>技能要求:</strong> {aiAnalysis.skills.join(', ')}</p>
    <p><strong>经验要求:</strong> {aiAnalysis.experience}</p>
  </div>
)}
```

**成本控制**:
- 使用 GPT-3.5-turbo (更便宜)
- 缓存分析结果 (避免重复调用)
- 设置每日 API 调用上限

**预估成本**: $5-10/月 (开发阶段)

---

### Week 2: 完善和部署

#### Day 6-7: 前端优化 ✨

**任务**:
1. **UI/UX 优化**:
   - 改进卡片设计
   - 添加加载状态动画
   - 优化移动端体验

2. **错误处理**:
   - API 失败提示
   - 空状态设计
   - 404 页面

3. **性能优化**:
   - 图片优化 (Next.js Image)
   - 代码分割 (动态导入)
   - 缓存策略 (SWR)

---

#### Day 8-9: 前端部署 🚀

**部署选项**:

**推荐: Vercel** (零配置,免费)
```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 部署
cd job-intelligence-frontend
vercel

# 3. 配置环境变量
vercel env add NEXT_PUBLIC_API_URL
# 值: https://api.jobintel.com (或 VM IP)
```

**配置 CORS** (.NET API):
```csharp
// Program.cs
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins("https://your-app.vercel.app")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

app.UseCors("AllowFrontend");
```

**备选: 自建 Nginx**
- 部署到 VM 的 `/var/www/frontend`
- 配置 Nginx 静态托管

---

#### Day 10-12: 文档和演示 📚

**任务**:
1. **README 更新**:
   - 项目介绍
   - 技术栈
   - 功能演示 (GIF/视频)
   - 部署架构图

2. **演示准备**:
   - 录制 2-3 分钟演示视频
   - 准备演讲 PPT (如需要)
   - 整理面试问答

3. **Portfolio 更新**:
   - 添加到个人网站
   - 更新 LinkedIn
   - 准备项目介绍 (中英文)

---

### 快速路线交付物

**最终产出**:
- ✅ 全栈项目 (React + .NET + PostgreSQL)
- ✅ AI 功能 (GPT-4 职位解析)
- ✅ 生产环境部署 (Azure + Vercel)
- ✅ 完整文档和演示

**技术亮点**:
- OpenAI API 集成
- Next.js 14 App Router
- Azure 云部署
- CI/CD 自动化
- 100 个单元测试

**时间成本**: 12-14 天

**面试价值**: ⭐⭐⭐⭐⭐ (完整全栈 + AI 项目)

---

## 中期路线 B: 深度路线 (2-4 周) - AI 优先

**时间**: 3-4 周
**目标**: 打造 AI-Powered 求职平台,展示 LLM 应用深度
**适合**: 想深入学习 AI 技术,有充足时间

### Phase 1 (Week 1-2): AI 核心功能开发

#### Week 1: 职位描述智能解析

**目标**: 使用 GPT-4 + Structured Output 解析职位描述

**技术方案**:

**1. 结构化解析** (使用 Function Calling):
```python
# ai-service/app/services/job_analyzer.py
from openai import OpenAI

class JobAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze_job(self, job_title: str, job_description: str):
        """使用 GPT-4 结构化解析职位"""

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是职位描述分析专家..."},
                {"role": "user", "content": f"职位: {job_title}\n描述: {job_description}"}
            ],
            functions=[
                {
                    "name": "extract_job_info",
                    "description": "提取职位关键信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "required_skills": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "必需技能列表"
                            },
                            "preferred_skills": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "years_of_experience": {
                                "type": "string",
                                "description": "经验要求 (如: 3-5 年)"
                            },
                            "salary_range": {
                                "type": "object",
                                "properties": {
                                    "min": {"type": "number"},
                                    "max": {"type": "number"},
                                    "currency": {"type": "string"}
                                }
                            },
                            "key_responsibilities": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "work_type": {
                                "type": "string",
                                "enum": ["full-time", "part-time", "contract", "casual"]
                            },
                            "summary": {
                                "type": "string",
                                "description": "一句话总结"
                            }
                        },
                        "required": ["required_skills", "summary"]
                    }
                }
            ],
            function_call={"name": "extract_job_info"}
        )

        return response.choices[0].message.function_call.arguments
```

**2. 批量处理**:
```python
# 批量分析现有职位
@app.post("/ai/analyze-batch")
async def analyze_batch(limit: int = 100):
    """批量分析数据库中的职位"""

    jobs = await fetch_jobs_from_dotnet_api(limit)
    analyzer = JobAnalyzer(os.getenv("OPENAI_API_KEY"))

    results = []
    for job in jobs:
        analysis = analyzer.analyze_job(job.title, job.description)
        results.append({
            "job_id": job.id,
            "analysis": analysis
        })

        # 存储到数据库
        await save_analysis(job.id, analysis)

    return {"analyzed": len(results)}
```

**3. 数据库扩展**:
```sql
-- 新增表: 存储 AI 分析结果
CREATE TABLE job_analysis (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    required_skills JSONB,
    preferred_skills JSONB,
    years_of_experience VARCHAR(50),
    salary_range JSONB,
    key_responsibilities JSONB,
    work_type VARCHAR(20),
    summary TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id)
);

CREATE INDEX idx_job_analysis_job_id ON job_analysis(job_id);
```

**成功标准**:
- ✅ 成功解析 100+ 职位
- ✅ 提取准确率 > 85%
- ✅ API 响应时间 < 5s
- ✅ 成本控制在 $10/月

---

#### Week 2: 职位匹配推荐算法

**目标**: 基于用户技能和经验,推荐匹配职位

**技术方案**:

**1. 用户画像**:
```python
# 用户输入技能和经验
user_profile = {
    "skills": ["plumbing", "gasfitting", "drainage"],
    "years_of_experience": 5,
    "preferred_salary_min": 70000,
    "preferred_locations": ["NSW", "VIC"],
    "work_type": "full-time"
}
```

**2. 智能匹配** (使用 Embeddings):
```python
from openai import OpenAI

class JobMatcher:
    def __init__(self):
        self.client = OpenAI()

    def generate_embedding(self, text: str):
        """生成文本向量"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def calculate_match_score(self, user_profile, job_analysis):
        """计算匹配度"""

        # 1. 技能匹配 (向量相似度)
        user_skills_text = ", ".join(user_profile["skills"])
        job_skills_text = ", ".join(job_analysis["required_skills"])

        user_embedding = self.generate_embedding(user_skills_text)
        job_embedding = self.generate_embedding(job_skills_text)

        skill_similarity = cosine_similarity(user_embedding, job_embedding)

        # 2. 经验匹配 (规则)
        experience_match = self._match_experience(
            user_profile["years_of_experience"],
            job_analysis["years_of_experience"]
        )

        # 3. 薪资匹配
        salary_match = self._match_salary(
            user_profile["preferred_salary_min"],
            job_analysis.get("salary_range")
        )

        # 4. 地点匹配
        location_match = job.location_state in user_profile["preferred_locations"]

        # 综合评分
        match_score = (
            skill_similarity * 0.5 +
            experience_match * 0.2 +
            salary_match * 0.2 +
            (1.0 if location_match else 0) * 0.1
        )

        return match_score
```

**3. 推荐 API**:
```python
@app.post("/ai/recommend")
async def recommend_jobs(user_profile: UserProfile):
    """推荐匹配职位"""

    # 1. 获取所有职位和分析结果
    jobs_with_analysis = await fetch_jobs_with_analysis()

    matcher = JobMatcher()

    # 2. 计算匹配度
    recommendations = []
    for job, analysis in jobs_with_analysis:
        score = matcher.calculate_match_score(user_profile, analysis)

        if score > 0.6:  # 阈值: 60%
            recommendations.append({
                "job": job,
                "match_score": score,
                "reasons": matcher.get_match_reasons(user_profile, analysis)
            })

    # 3. 排序返回
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)

    return {"recommendations": recommendations[:20]}
```

**成功标准**:
- ✅ 推荐准确率 > 75% (人工评估)
- ✅ API 响应时间 < 3s
- ✅ 提供推荐理由 (可解释性)

---

### Phase 2 (Week 3): 简历优化助手

**目标**: 针对特定职位,提供简历优化建议

**技术方案**:

```python
@app.post("/ai/optimize-resume")
async def optimize_resume(request: ResumeOptimizeRequest):
    """简历优化建议"""

    # 1. 获取职位分析
    job_analysis = await get_job_analysis(request.job_id)

    # 2. 提取简历技能 (PDF 解析)
    resume_text = extract_text_from_pdf(request.resume_file)

    # 3. GPT-4 生成优化建议
    prompt = f"""
基于以下职位要求,分析简历并提供优化建议:

职位要求:
- 必需技能: {job_analysis.required_skills}
- 关键职责: {job_analysis.key_responsibilities}

简历内容:
{resume_text}

请提供:
1. 缺失的关键技能
2. 应该突出的经验
3. 简历措辞优化建议
4. 关键词建议 (ATS 优化)
"""

    response = await call_gpt4(prompt)

    return {"suggestions": response}
```

**成功标准**:
- ✅ PDF 简历解析准确
- ✅ 建议具体可行
- ✅ 支持中英文简历

---

### Phase 3 (Week 4): 简化前端 + 部署

**前端范围** (最小化):
- 职位列表 + AI 解析展示
- 职位推荐页面 (输入技能 → 显示推荐)
- 简历优化工具 (上传 PDF → 显示建议)

**部署**: 同快速路线

---

### 深度路线交付物

**最终产出**:
- ✅ AI-Powered 求职平台
- ✅ 3 个核心 AI 功能:
  - 职位描述智能解析
  - 职位匹配推荐
  - 简历优化助手
- ✅ LLM 应用最佳实践:
  - Function Calling
  - Embeddings 向量搜索
  - Prompt Engineering
- ✅ 完整文档和演示

**技术亮点**:
- GPT-4 Structured Output
- OpenAI Embeddings
- 向量相似度匹配
- PDF 解析 (PyPDF2)
- 推荐算法设计

**时间成本**: 21-28 天

**面试价值**: ⭐⭐⭐⭐⭐ (LLM 应用专家)

---

## 中期路线 C: 全栈路线 (3-4 周) - 平衡发展

**时间**: 3-4 周
**目标**: 完整的用户系统 + 前端 UI + 基础 AI
**适合**: 追求项目完整性,全栈技能平衡发展

### Phase 1 (Week 1): 用户系统后端

**参考**: [V2_IMPLEMENTATION_PLAN.md - Phase 2](../development/V2_IMPLEMENTATION_PLAN.md#phase-2-用户系统后端开发)

**核心功能**:
```
✅ 用户注册/登录 (JWT)
✅ Email 验证
✅ 密码重置
✅ 用户资料管理
```

**数据库设计**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES job_postings(id),
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

CREATE TABLE job_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    keywords VARCHAR(255),
    location VARCHAR(100),
    frequency VARCHAR(20),  -- 'daily', 'weekly'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API 端点** (新增):
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/saved-jobs
GET  /api/saved-jobs
DELETE /api/saved-jobs/{jobId}
POST /api/job-alerts
GET  /api/job-alerts
```

---

### Phase 2 (Week 2): 前端核心页面

**页面列表**:
1. 首页 (搜索 + Hero)
2. 职位列表 (筛选 + 分页)
3. 职位详情
4. 登录/注册页面
5. 用户中心 (保存的职位 + Job Alerts)

**技术栈**: Next.js 14 + TypeScript + Tailwind + shadcn/ui

**详细步骤**: 参考 [V2_IMPLEMENTATION_PLAN.md - Phase 3](../development/V2_IMPLEMENTATION_PLAN.md#phase-3-前端框架和基础页面)

---

### Phase 3 (Week 3): 用户功能集成

**保存职位**:
- 职位详情页添加 "保存" 按钮
- 用户中心显示已保存职位
- 取消保存功能

**Job Alerts**:
- 创建 Alert 表单
- Email 通知 (使用 Hangfire)
- Alert 管理 (编辑/删除/暂停)

**详细步骤**: 参考 [V2_IMPLEMENTATION_PLAN.md - Phase 4](../development/V2_IMPLEMENTATION_PLAN.md#phase-4-用户功能后端集成)

---

### Phase 4 (Week 4): AI 功能 + 部署

**简化 AI 功能** (选 1-2 个):
- 职位描述智能解析 (快速实现)
- 或 职位匹配推荐 (算法复杂)

**部署优化**:
- 前端部署到 Vercel
- 配置域名 (可选)
- 性能优化 (缓存、CDN)

**详细步骤**: 参考 [V2_IMPLEMENTATION_PLAN.md - Phase 5](../development/V2_IMPLEMENTATION_PLAN.md#phase-5-完整部署和优化)

---

### 全栈路线交付物

**最终产出**:
- ✅ 完整的 SaaS 产品
- ✅ 用户认证系统
- ✅ 个人 Dashboard
- ✅ 保存职位 + Job Alerts
- ✅ 基础 AI 功能
- ✅ 响应式前端
- ✅ 生产环境部署

**技术亮点**:
- JWT 认证
- Email 服务集成
- Hangfire 后台任务
- Next.js 14 App Router
- 全栈数据流

**时间成本**: 21-28 天

**面试价值**: ⭐⭐⭐⭐⭐ (完整 SaaS 产品)

---

## 长期愿景 (2-3 个月) - 完整产品

如果选择创业方向或长期打磨,可以考虑以下扩展:

### 扩展功能

**1. 多数据源集成**:
- LinkedIn Jobs
- Glassdoor
- Workforce Australia
- 目标: 5+ 平台

**2. 高级 AI 功能**:
- 语义搜索 (pgvector)
- 职业路径规划
- 薪资预测模型
- 面试问题生成

**3. 社区功能**:
- 用户评论和评分
- 职位分享
- 求职经验交流

**4. 商业化**:
- Premium 订阅 (Stripe 集成)
- 企业版 (批量 Job Alerts)
- 招聘方功能 (职位发布)

**5. 移动应用**:
- React Native App
- 推送通知
- 离线模式

---

## 技术栈演进

### 当前 (MVP V1)
```
后端: Python (FastAPI) + .NET 8 (ASP.NET Core)
数据库: PostgreSQL 16
部署: Azure VM + Docker Compose
CI/CD: GitHub Actions
```

### 短期增强 (中期路线)
```
前端: Next.js 14 + TypeScript + Tailwind
AI: OpenAI GPT-4 + Embeddings
认证: JWT
Email: SendGrid / AWS SES
```

### 长期扩展 (完整产品)
```
缓存: Redis
搜索: Elasticsearch / pgvector
监控: Application Insights / Prometheus
队列: RabbitMQ / Azure Service Bus
CDN: Cloudflare
支付: Stripe
移动: React Native
```

---

## 成功指标

### 技术指标

**短期** (1-2 周):
- ✅ Bug 修复验证通过
- ✅ 系统稳定运行 (内存 < 85%)
- ✅ 无关键错误

**中期** (2-4 周):
- ✅ 完成选定路线的核心功能
- ✅ 前端可访问 (如有)
- ✅ AI 功能可用 (如有)
- ✅ 文档完整

**长期** (2-3 个月):
- ✅ 完整 SaaS 产品
- ✅ 真实用户使用
- ✅ 用户反馈收集

---

### 学习指标

**短期**:
- ✅ 掌握系统稳定性监控
- ✅ 理解生产环境运维

**中期**:
- ✅ 掌握前端框架 (React/Next.js)
- ✅ 或 掌握 LLM 应用开发
- ✅ 或 掌握用户认证系统

**长期**:
- ✅ 全栈开发能力
- ✅ AI 集成经验
- ✅ SaaS 产品经验

---

### 面试指标

**基础**:
- ✅ 可演示的完整项目
- ✅ GitHub 代码质量
- ✅ 文档完整性

**进阶**:
- ✅ 技术难点解决能力
- ✅ 系统设计思维
- ✅ 问题诊断和修复能力

**高级**:
- ✅ 独特技术亮点 (AI/架构)
- ✅ 项目商业价值
- ✅ 持续改进和学习

---

## 相关文档

**规划类**:
- [V2_IMPLEMENTATION_PLAN.md](../development/V2_IMPLEMENTATION_PLAN.md) - 详细实施步骤
- [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md) - 优化任务清单
- [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) - 技术架构设计

**监控类**:
- [LOGGING_MONITORING_PLAN.md](LOGGING_MONITORING_PLAN.md) - 监控方案
- [BUG_FIXES_2026-01-19.md](BUG_FIXES_2026-01-19.md) - Bug 修复记录

**开发类**:
- [DAILY_PLAN.md](../development/DAILY_PLAN.md) - 日常工作记录
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - 开发指南

**部署类**:
- [CICD_DEPLOYMENT.md](../deployment/CICD_DEPLOYMENT.md) - CI/CD 配置
- [MIGRATION_COMPLETE_2026-01-10.md](../deployment/MIGRATION_COMPLETE_2026-01-10.md) - 迁移记录

---

**文档维护者**: 项目团队
**最后更新**: 2026-01-19
**下次审查**: 完成中期路线决策后
**状态**: ✅ 活跃使用中
