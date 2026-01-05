# 文档索引

**最后更新**: 2026-01-05

---

## 📌 最新重要文档

### 部署相关（2026-01-05 更新）

| 文档 | 状态 | 用途 | 链接 |
|------|------|------|------|
| **Azure 部署完整总结** | ✅ 最新 | 部署过程回顾、技术细节、问题解决 | [DEPLOYMENT_SUMMARY_2026-01-05.md](deployment/DEPLOYMENT_SUMMARY_2026-01-05.md) |
| **学习总结** | ✅ 最新 | 深度学习笔记、面试准备、概念理解 | [LEARNING_SUMMARY_2026-01-05.md](LEARNING_SUMMARY_2026-01-05.md) |
| **CI/CD 部署指南** | ✅ 当前 | GitHub Actions 使用文档 | [deployment/CICD_DEPLOYMENT.md](deployment/CICD_DEPLOYMENT.md) |
| **架构对比文档** | ✅ 参考 | 单体 vs 分布式架构分析 | [deployment/ARCHITECTURE_COMPARISON.md](deployment/ARCHITECTURE_COMPARISON.md) |
| **部署测试清单** | ✅ 参考 | 32 个测试检查点 | [deployment/DEPLOYMENT_TEST_CHECKLIST.md](deployment/DEPLOYMENT_TEST_CHECKLIST.md) |

### 过时文档（仅供参考）

| 文档 | 状态 | 原因 | 链接 |
|------|------|------|------|
| 分阶段部署指南 | ⚠️ 已过时 | 基于 VM 本地构建（已被 CI/CD 替代） | [deployment/STEP_BY_STEP_DEPLOYMENT.md](deployment/STEP_BY_STEP_DEPLOYMENT.md) |
| Azure 免费部署指南 | ⚠️ 已过时 | 使用旧的部署方法 | [deployment/AZURE_FREE_DEPLOYMENT_GUIDE.md](deployment/AZURE_FREE_DEPLOYMENT_GUIDE.md) |

---

## 📚 核心文档

### 项目概览

| 文档 | 说明 |
|------|------|
| [MVP V1 完成总结](MVP_V1_COMPLETION.md) | MVP V1 功能清单和完成状态 |
| [V1 完成总结](core/V1_COMPLETION_SUMMARY.md) | V1 版本详细总结 |
| [.NET 集成完成](core/DOTNET_INTEGRATION_COMPLETE.md) | .NET 后端集成文档 |

### 技术设计

| 文档 | 说明 |
|------|------|
| [技术设计文档](core/TECHNICAL_DESIGN.md) | 整体技术架构设计 |
| [架构决策](core/ARCHITECTURE_DECISIONS.md) | 重要架构决策记录 |
| [数据库重新设计提案](design/DATABASE_REDESIGN_PROPOSAL.md) | 数据库优化方案 |
| [API 设计迭代](design/API_DESIGN_ITERATIONS.md) | API 设计演进过程 |

### 开发文档

| 文档 | 说明 |
|------|------|
| [开发指南](core/DEVELOPMENT_GUIDE.md) | 开发环境搭建和规范 |
| [TDD 开发指南](development/TDD_DEVELOPMENT_GUIDE.md) | 测试驱动开发实践 |
| [实现总结](core/IMPLEMENTATION_SUMMARY.md) | 各功能实现总结 |
| [每日计划](development/DAILY_PLAN.md) | 开发任务和进度 |

### 爬虫相关

| 文档 | 说明 |
|------|------|
| [爬虫研究分析](development/SCRAPER_RESEARCH_ANALYSIS.md) | 爬虫技术调研 |
| [爬虫融合分析](development/SCRAPER_FUSION_ANALYSIS.md) | 多爬虫框架对比 |
| [Seek API 对比](design/SEEK_API_COMPARISON.md) | Seek 平台 API 分析 |
| [爬虫数据字段分析](development/SCRAPER_DATA_FIELDS_ANALYSIS.md) | 数据字段映射 |
| [爬虫第一阶段完成](development/SCRAPER_PHASE1_COMPLETION.md) | 爬虫开发总结 |

### 定时任务

| 文档 | 说明 |
|------|------|
| [定时任务设计](design/SCHEDULED_TASKS_DESIGN.md) | Hangfire 任务设计 |
| [定时任务实现](design/SCHEDULED_TASKS_IMPLEMENTATION.md) | 实现细节 |

### 教程文档

| 文档 | 说明 |
|------|------|
| [PostgreSQL 指南](tutorials/PostgreSQL-Guide.md) | 数据库使用教程 |
| [数据检查指南](tutorials/DATA_CHECKING_GUIDE.md) | 数据质量验证 |
| [优化优先级指南](tutorials/OPTIMIZATION_PRIORITIES_GUIDE.md) | 性能优化建议 |
| [Seek Adapter 设计指南](tutorials/SEEK_ADAPTER_DESIGN_GUIDE.md) | 适配器模式应用 |

---

## 🔄 文档更新历史

### 2026-01-05
- ✅ 新增：[Azure 部署完整总结](deployment/DEPLOYMENT_SUMMARY_2026-01-05.md)
- ✅ 新增：[学习总结 2026-01-05](LEARNING_SUMMARY_2026-01-05.md)
- ✅ 新增：[CI/CD 部署指南](deployment/CICD_DEPLOYMENT.md)
- ⚠️ 标记过时：[分阶段部署指南](deployment/STEP_BY_STEP_DEPLOYMENT.md)
- ✅ 更新：[README.md](../README.md) - 添加部署状态和最新文档链接

### 2026-01-03
- 云平台对比分析
- Azure 免费部署指南
- 分阶段部署指南

### 2025-12-26
- 文档清理工作
- 数据质量修复记录

### 2025-12-23
- V1 完成总结
- .NET 集成完成文档

---

## 📖 阅读建议

### 新手入门路径

1. **了解项目**
   - [README.md](../README.md)
   - [MVP V1 完成总结](MVP_V1_COMPLETION.md)

2. **本地开发**
   - [开发指南](core/DEVELOPMENT_GUIDE.md)
   - [README-DEV.md](../README-DEV.md)

3. **理解架构**
   - [技术设计文档](core/TECHNICAL_DESIGN.md)
   - [架构决策](core/ARCHITECTURE_DECISIONS.md)

4. **部署到云端**
   - [学习总结 2026-01-05](LEARNING_SUMMARY_2026-01-05.md)（强烈推荐先读）
   - [CI/CD 部署指南](deployment/CICD_DEPLOYMENT.md)
   - [Azure 部署完整总结](deployment/DEPLOYMENT_SUMMARY_2026-01-05.md)

### 面试准备路径

1. **技术深度**
   - [学习总结 2026-01-05](LEARNING_SUMMARY_2026-01-05.md) - 核心概念和面试问答
   - [Azure 部署完整总结](deployment/DEPLOYMENT_SUMMARY_2026-01-05.md) - 实战案例

2. **问题解决能力**
   - 阅读部署失败和解决过程
   - 理解从优化到架构转变的思路

3. **技术栈掌握**
   - .NET 8 + EF Core
   - Docker + Docker Compose
   - GitHub Actions + CI/CD
   - PostgreSQL 优化

4. **项目经验总结**
   - 准备 STAR 故事（参考学习总结中的面试问答）
   - 量化成果和技术关键词

### 技术深入路径

1. **CI/CD 实践**
   - [CI/CD 部署指南](deployment/CICD_DEPLOYMENT.md)
   - GitHub Actions Workflow 分析
   - 容器镜像构建优化

2. **数据库优化**
   - [数据库重新设计提案](design/DATABASE_REDESIGN_PROPOSAL.md)
   - PostgreSQL 索引策略
   - 查询性能优化

3. **微服务架构**
   - [架构对比文档](deployment/ARCHITECTURE_COMPARISON.md)
   - 单体到分布式迁移路径
   - 服务拆分策略

---

## 🎯 文档维护指南

### 添加新文档

1. **创建文档**
   - 选择合适的目录（core/design/development/deployment/tutorials）
   - 使用清晰的文件名（大写字母+下划线）
   - 添加日期后缀（如有必要）

2. **文档模板**
   ```markdown
   # 文档标题

   **创建日期**: YYYY-MM-DD
   **最后更新**: YYYY-MM-DD
   **状态**: [进行中/已完成/已过时]

   ## 目录
   ...

   ## 正文
   ...

   ## 相关文档
   - [文档名](链接)
   ```

3. **更新索引**
   - 在本文件中添加新文档条目
   - 更新相关文档的交叉引用
   - 记录更新历史

### 标记过时文档

1. **在文档开头添加警告**
   ```markdown
   # ⚠️ [已过时] 原标题

   > **重要提示**: 说明为什么过时
   > **请改用**: [新文档链接]
   > **保留原因**: 历史参考/学习案例
   ```

2. **不要删除**
   - 过时的文档仍有价值
   - 展示了思维演进过程
   - 可作为学习案例

3. **更新索引**
   - 移到"过时文档"区域
   - 添加状态标记
   - 说明过时原因

---

## 📝 待办事项

### 需要创建的文档

- [ ] API 使用示例集
- [ ] 监控和告警配置指南
- [ ] 数据备份和恢复流程
- [ ] 安全最佳实践
- [ ] 性能调优指南

### 需要更新的文档

- [ ] 开发指南 - 添加 CI/CD 本地测试
- [ ] 技术设计 - 更新部署架构图
- [ ] README-DEV.md - 添加 GitHub Actions 调试技巧

### 需要清理的文档

- [ ] 合并重复的部署文档
- [ ] 整理 tutorials 目录
- [ ] 统一文档格式

---

## 🔍 快速查找

### 按主题查找

**部署相关**:
- 如何部署到 Azure? → [CI/CD 部署指南](deployment/CICD_DEPLOYMENT.md)
- 为什么之前的部署失败了? → [部署总结](deployment/DEPLOYMENT_SUMMARY_2026-01-05.md)
- 如何更新应用? → [CI/CD 部署指南](deployment/CICD_DEPLOYMENT.md#更新应用)

**开发相关**:
- 如何搭建开发环境? → [开发指南](core/DEVELOPMENT_GUIDE.md)
- 如何添加新的爬虫? → [爬虫实现计划](development/SCRAPER_IMPLEMENTATION_PLAN.md)
- 如何编写测试? → [TDD 开发指南](development/TDD_DEVELOPMENT_GUIDE.md)

**学习相关**:
- 面试准备资料? → [学习总结 2026-01-05](LEARNING_SUMMARY_2026-01-05.md)
- CI/CD 核心概念? → [学习总结](LEARNING_SUMMARY_2026-01-05.md#核心概念理解)
- 技术难点解析? → [学习总结](LEARNING_SUMMARY_2026-01-05.md#技术难点突破)

### 按文档类型查找

**总结类**:
- MVP V1 完成总结
- V1 完成总结
- 部署总结
- 学习总结

**指南类**:
- 开发指南
- 部署指南
- TDD 指南
- PostgreSQL 指南

**设计类**:
- 技术设计
- API 设计迭代
- 数据库设计
- 定时任务设计

**分析类**:
- 爬虫研究分析
- 架构对比分析
- Seek API 对比

---

**文档维护者**: 项目团队
**最后审查**: 2026-01-05
**下次审查**: 2026-02-05（每月审查一次）
