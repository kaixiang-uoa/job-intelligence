# Job Intelligence

> 澳洲职位数据采集与分析系统 | Australian Job Market Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![.NET 8](https://img.shields.io/badge/.NET-8.0-512BD4)](https://dotnet.microsoft.com/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB)](https://www.python.org/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791)](https://www.postgresql.org/)

## 📖 项目简介

Job Intelligence 是一个专注于澳洲 Trade 行业的职位数据采集与分析系统。通过自动爬取 Seek.com.au 等招聘网站的职位信息,为求职者和研究人员提供数据洞察。

**🎉 项目状态**: ✅ MVP V1 已完成并成功部署到 Azure
- **部署平台**: Azure VM (Australia East)
- **CI/CD**: GitHub Actions + GitHub Container Registry
- **在线访问**: http://20.92.200.112:5000/swagger

> 📚 **最新文档**:
> - [Azure 部署完整总结](docs/deployment/DEPLOYMENT_SUMMARY_2026-01-05.md) - 部署过程与技术细节
> - [学习总结 2026-01-05](docs/LEARNING_SUMMARY_2026-01-05.md) - 深度学习笔记与面试准备

### 核心功能

- 🔍 **智能爬虫**：自动抓取 Seek 平台的 Trade 职位数据
- 📊 **数据分析**：薪资趋势、职位分布、技能需求分析
- 🔄 **定时任务**：Hangfire 驱动的自动化数据更新
- 📡 **RESTful API**：提供标准化的数据查询接口
- 🐳 **容器化部署**：Docker Compose 一键部署

---

## 🏗️ 技术栈

| 组件 | 技术 |
|------|------|
| **后端 API** | ASP.NET Core 8.0 + Entity Framework Core |
| **爬虫服务** | Python 3.10 + FastAPI + BeautifulSoup4 |
| **数据库** | PostgreSQL 16 |
| **任务调度** | Hangfire |
| **反向代理** | Nginx |
| **容器化** | Docker + Docker Compose |

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/kaixiang-uoa/job-intelligence.git
cd job-intelligence

# 2. 配置环境变量
cp .env.example .env
nano .env  # 设置数据库密码等

# 3. 启动所有服务
docker compose up -d

# 4. 查看服务状态
docker compose ps
```

### 方式二：本地开发

详见 [README-DEV.md](README-DEV.md) 开发文档

---

## 📊 服务访问

| 服务 | URL | 说明 |
|------|-----|------|
| .NET API | http://localhost:5000 | 主 API 服务 |
| Swagger UI | http://localhost:5000/swagger | API 文档 |
| Hangfire Dashboard | http://localhost:5000/hangfire | 任务管理 |
| Python Scraper | http://localhost:8000 | 爬虫服务 |
| Python Docs | http://localhost:8000/docs | FastAPI 文档 |

---

## 📁 项目结构

```
job-intelligence/
├── backend/                  # .NET 后端 API
│   ├── src/
│   │   ├── JobIntel.Api/     # Web API 层
│   │   ├── JobIntel.Core/    # 领域层
│   │   └── JobIntel.Infrastructure/  # 数据访问层
│   └── JobIntel.sln
├── scraper/                  # Python 爬虫服务
│   ├── app/
│   │   ├── main.py
│   │   ├── scrapers/
│   │   └── models/
│   └── requirements.txt
├── docs/                     # 项目文档
│   ├── deployment/           # 部署指南
│   ├── development/          # 开发计划
│   └── tutorials/            # 教程
├── docker-compose.yml        # Docker Compose 配置
└── README.md                 # 本文档
```

---

## 💻 API 使用示例

### 获取职位列表

```bash
# 获取 Electrician 职位
curl "http://localhost:5000/api/jobs?trade=Electrician"

# 按州和薪资筛选
curl "http://localhost:5000/api/jobs?trade=Plumber&state=NSW&minSalary=70000"
```

### 手动触发爬虫

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "trade": "Electrician",
    "state": "NSW",
    "max_pages": 1
  }'
```

---

## 📚 文档导航

### 部署相关
- [分阶段部署指南](docs/deployment/ARCHITECTURE_COMPARISON.md) - 单 VM vs 分布式架构对比
- [Azure 免费部署](docs/deployment/AZURE_FREE_DEPLOYMENT_GUIDE.md) - 使用 Azure 免费资源
- [分步部署教程](docs/deployment/STEP_BY_STEP_DEPLOYMENT.md) - 阶段式部署流程

### 开发相关
- [README-DEV.md](README-DEV.md) - 完整开发文档
- [V2 实施计划](docs/development/V2_IMPLEMENTATION_PLAN.md) - 未来功能路线图
- [技术设计](docs/core/TECHNICAL_DESIGN.md) - 系统架构详解

### 教程
- [PostgreSQL 教程](docs/tutorials/PostgreSQL-Guide.md) - 数据库入门
- [数据检查指南](docs/tutorials/DATA_CHECKING_GUIDE.md) - 7 种数据验证方法

---

## 🔧 环境变量配置

创建 `.env` 文件并配置以下变量:

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=jobintel
DB_USER=admin
DB_PASSWORD=your_secure_password_here

# .NET API
ASPNETCORE_ENVIRONMENT=Production
DOTNET_API_PORT=5000

# Python API
PYTHON_API_PORT=8000

# Hangfire
HANGFIRE_USERNAME=admin
HANGFIRE_PASSWORD=your_hangfire_password_here
```

---

## 🧪 测试

```bash
# Python 爬虫测试
cd scraper
pytest

# .NET API 测试
cd backend
dotnet test
```

---

## 📈 项目状态

### ✅ V1 MVP 已完成 (100%)
- [x] Seek 爬虫基础功能
- [x] PostgreSQL 数据存储
- [x] .NET Web API
- [x] Hangfire 定时任务
- [x] Docker 容器化部署
- [x] 数据质量优化（95%+ 准确率）

### 🔄 V2 规划中
- [ ] 用户系统（注册/登录）
- [ ] React 前端界面
- [ ] 数据可视化仪表板
- [ ] 多数据源支持（Indeed, LinkedIn）
- [ ] AI 薪资预测

详见 [V2_IMPLEMENTATION_PLAN.md](docs/development/V2_IMPLEMENTATION_PLAN.md)

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。使用本工具抓取数据时,请遵守网站的 robots.txt 和服务条款。

---

## 📧 联系方式

- **GitHub**: [@kaixiang-uoa](https://github.com/kaixiang-uoa)
- **项目地址**: [job-intelligence](https://github.com/kaixiang-uoa/job-intelligence)

---

<div align="center">

**如果这个项目对你有帮助,请给个 ⭐ Star！**

Made with ❤️ by Kaixiang

</div>
