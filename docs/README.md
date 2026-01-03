# 📚 文档索引

**Job Intelligence Platform V1 MVP** - 完整文档导航

---

## 🚀 快速开始

新用户请从这里开始：

- **[项目主页](../README.md)** - 项目概述和功能介绍
- **[快速启动指南](../GETTING_STARTED.md)** - 环境配置和启动步骤
- **[PostgreSQL 教程](tutorials/PostgreSQL-Guide.md)** - 零基础数据库学习

---

## 📋 核心文档

V1 MVP 生产就绪文档（最重要）

### 项目总结

- **[MVP V1 完成报告](MVP_V1_COMPLETION.md)** 🎉 **V1 最终报告**
  - 项目完成总结和数据质量修复
  - 文档整理结果
  - 生产就绪清单
  - V1/V1.5/V2 对比

- **[V1 完成总结](core/V1_COMPLETION_SUMMARY.md)** ⭐ 推荐阅读
  - 项目概览和功能清单
  - 技术栈和架构
  - 测试结果和质量指标
  - 部署指南

- **[数据质量修复报告](core/DATA_QUALITY_FIXES_2025-12-26.md)** ⭐ 最新
  - P0/P1 问题修复详情
  - 测试结果和对比
  - 已知限制和优化建议
  - 代码注释位置

### 技术设计

- **[技术设计文档](core/TECHNICAL_DESIGN.md)** ⭐ 核心设计
  - 系统架构和技术栈
  - 数据模型设计
  - API 端点规范
  - 去重和数据流策略

- **[开发指南](core/DEVELOPMENT_GUIDE.md)** ⭐ 开发规范
  - 开发环境配置
  - 编码规范和最佳实践
  - 测试指南
  - 部署流程

### 技术实现

- **[.NET 集成完成报告](core/DOTNET_INTEGRATION_COMPLETE.md)**
  - Python 爬虫 + .NET 后端集成
  - 端到端测试结果
  - API 使用示例

- **[查询 API 测试报告](core/QUERY_API_TEST_RESULTS.md)**
  - 搜索和过滤功能测试
  - 分页和排序验证
  - 性能指标

- **[实现总结](core/IMPLEMENTATION_SUMMARY.md)**
  - 代码统计和文件清单
  - 技术决策和合规性
  - 架构模式说明

### 架构和优化

- **[架构决策记录](core/ARCHITECTURE_DECISIONS.md)**
  - 关键技术选型
  - 设计模式和最佳实践

- **[优化路线图](core/OPTIMIZATION_ROADMAP.md)**
  - 性能优化建议
  - 未来增强计划

- **[项目文件参考](core/PROJECT_FILES.md)**
  - 代码库结构详解
  - 文件职责说明

---

## 🎨 设计文档

系统设计和规划文档（归档）

### API 设计

- **[API 设计迭代](design/API_DESIGN_ITERATIONS.md)**
  - RESTful API 演进过程
  - 端点设计决策

- **[SEEK API 对比分析](design/SEEK_API_COMPARISON.md)**
  - SEEK GraphQL vs REST API
  - 技术选型理由

### 数据库设计

- **[数据库重新设计方案](design/DATABASE_REDESIGN_PROPOSAL.md)**
  - JSONB 字段优化
  - 索引策略
  - 迁移计划

### 定时任务

- **[定时任务设计](design/SCHEDULED_TASKS_DESIGN.md)**
  - 65 个任务矩阵 (13 trades × 5 cities)
  - Hangfire 配置
  - 时区和调度策略

- **[定时任务实施报告](design/SCHEDULED_TASKS_IMPLEMENTATION.md)**
  - 实现细节
  - 测试结果
  - 运行监控

---

## 🛠️ 开发过程文档

开发历程记录（归档，供参考）

### 爬虫开发

- **[爬虫研究分析](development/SCRAPER_RESEARCH_ANALYSIS.md)**
  - 技术方案调研
  - SEEK 和 Indeed API 分析

- **[爬虫数据字段分析](development/SCRAPER_DATA_FIELDS_ANALYSIS.md)**
  - API 返回字段解析
  - 数据映射方案

- **[爬虫融合分析](development/SCRAPER_FUSION_ANALYSIS.md)**
  - 多平台数据统一
  - 标准化策略

- **[爬虫实施计划](development/SCRAPER_IMPLEMENTATION_PLAN.md)**
  - 开发里程碑
  - 任务拆分

- **[爬虫 Phase 1 完成报告](development/SCRAPER_PHASE1_COMPLETION.md)**
  - 初步实现成果
  - 测试结果

### 开发方法

- **[TDD 开发指南](development/TDD_DEVELOPMENT_GUIDE.md)**
  - 测试驱动开发实践
  - 单元测试模式

- **[TDD 实施清单](development/TDD_IMPLEMENTATION_CHECKLIST.md)**
  - 测试覆盖检查
  - 质量保证流程

### 开发计划

- **[每日开发计划](development/DAILY_PLAN.md)** ⭐ 当前状态
  - MVP V1 完成总结
  - V2 方向确定
  - 开发进度跟踪

- **[V2 实施计划](development/V2_IMPLEMENTATION_PLAN.md)** 🆕 ⭐ 下一阶段
  - 完整产品开发路线（2-3 个月）
  - 5 个阶段详细规划
  - 部署 + 用户系统 + 前端
  - 技术栈和里程碑

---

## 📖 教程

- **[数据检查完全指南](tutorials/DATA_CHECKING_GUIDE.md)** 🆕 ⭐ 推荐
  - 7 种数据检查方式详解
  - 实用脚本使用说明
  - 常见问题排查
  - 最佳实践和推荐组合

- **[PostgreSQL 零基础教程](tutorials/PostgreSQL-Guide.md)**
  - 基础概念讲解
  - 命令行操作
  - 常用查询示例

- **[SEEK 适配器设计指南](tutorials/SEEK_ADAPTER_DESIGN_GUIDE.md)**
  - SEEK API 使用详解
  - 适配器模式实现
  - 数据解析技巧

- **[优化优先级指南](tutorials/OPTIMIZATION_PRIORITIES_GUIDE.md)**
  - 性能优化建议
  - 代码质量提升
  - 最佳实践

---

## 📁 文档结构

```
docs/                          # 唯一文档目录
├── README.md                  # 本文档 (索引)
├── DOCUMENTATION_CLEANUP_2025-12-26.md  # 文档整理报告
├── core/                      # 核心文档 (V1 MVP)
│   ├── TECHNICAL_DESIGN.md           # ⭐ 技术设计文档
│   ├── DEVELOPMENT_GUIDE.md          # ⭐ 开发指南
│   ├── V1_COMPLETION_SUMMARY.md      # V1 完成总结
│   ├── DATA_QUALITY_FIXES_2025-12-26.md  # 数据质量修复
│   ├── DOTNET_INTEGRATION_COMPLETE.md
│   ├── QUERY_API_TEST_RESULTS.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── ARCHITECTURE_DECISIONS.md
│   ├── OPTIMIZATION_ROADMAP.md
│   └── PROJECT_FILES.md
├── design/                    # 设计文档 (归档)
│   ├── API_DESIGN_ITERATIONS.md
│   ├── DATABASE_REDESIGN_PROPOSAL.md
│   ├── SCHEDULED_TASKS_DESIGN.md
│   ├── SCHEDULED_TASKS_IMPLEMENTATION.md
│   └── SEEK_API_COMPARISON.md
├── development/               # 开发过程 (归档)
│   ├── SCRAPER_*.md          # 爬虫开发过程 (6个文档)
│   ├── TDD_*.md              # TDD 实践 (2个文档)
│   └── DAILY_PLAN.md         # 每日计划
└── tutorials/                 # 教程和指南
    ├── PostgreSQL-Guide.md
    ├── SEEK_ADAPTER_DESIGN_GUIDE.md
    └── OPTIMIZATION_PRIORITIES_GUIDE.md
```

---

## 🔗 外部资源

### 技术文档

- [.NET 8 文档](https://learn.microsoft.com/en-us/dotnet/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Hangfire 文档](https://docs.hangfire.io/)

### 数据源

- [SEEK API](https://www.seek.com.au/)
- [Indeed API](https://au.indeed.com/)
- [JobSpy 库](https://github.com/Bunsly/JobSpy)

---

## 📝 文档维护

### 更新频率

- **核心文档**: 重大版本发布时更新 (V1 → V2)
- **设计文档**: 归档，不再更新
- **开发文档**: 归档，供参考
- **教程**: 根据反馈持续更新

### 文档规范

- 所有文档使用 Markdown 格式
- 包含创建日期和最后更新日期
- 使用中文撰写（代码注释除外）
- 保持简洁清晰，避免冗余

---

**文档索引创建时间**: 2025-12-26
**最后更新**: 2025-12-26
**文档版本**: V1.0
**状态**: ✅ 完成
