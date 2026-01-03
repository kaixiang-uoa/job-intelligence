# 云平台部署方案对比

**文档目的**: 对比主流云平台部署 Python 爬虫 + .NET API 的方案
**更新日期**: 2025-12-26
**适用项目**: Job Intelligence Platform

---

## 📊 云平台总览

### 支持 Python 部署的主流云平台

| 平台 | Python 支持 | .NET 支持 | 免费额度 | 推荐度 |
|------|------------|-----------|---------|--------|
| **Azure** | ✅ 优秀 | ✅ 最佳 | 12个月 + $200 | ⭐⭐⭐⭐⭐ |
| **AWS** | ✅ 优秀 | ✅ 优秀 | 12个月 | ⭐⭐⭐⭐⭐ |
| **GCP** | ✅ 优秀 | ✅ 良好 | $300试用 | ⭐⭐⭐⭐ |
| **Aliyun** | ✅ 良好 | ✅ 良好 | 学生优惠 | ⭐⭐⭐⭐ |
| **DigitalOcean** | ✅ 良好 | ✅ 良好 | $200试用 | ⭐⭐⭐ |
| **Heroku** | ✅ 优秀 | ❌ 不支持 | 限制免费 | ⭐⭐ |

---

## 🔷 Azure 部署方案（推荐）⭐⭐⭐⭐⭐

### 为什么选择 Azure？

**优势：**
1. ✅ **微软官方平台** - 对 .NET 支持最好
2. ✅ **Python 原生支持** - Azure App Service 完美支持 Python
3. ✅ **丰富的服务** - Azure Functions, App Service, Container Instances
4. ✅ **学生优惠** - 12 个月免费 + $100 额度
5. ✅ **中文文档** - 完善的中文支持和社区
6. ✅ **全球节点** - 包括香港、新加坡等亚洲节点

**免费额度（12 个月）：**
- 750 小时/月 Azure App Service (B1)
- 750 小时/月 VM (B1s)
- 5 GB Blob 存储
- 250 GB SQL Database
- $200 初始额度

---

### Azure 部署方案 A：App Service（推荐）⭐⭐⭐⭐⭐

**架构：**
```
Internet
    ↓
Azure Front Door / Application Gateway (可选)
    ↓
┌─────────────────────────────────────────────┐
│  Azure App Service (Linux)                  │
│  ┌────────────────┐  ┌────────────────┐    │
│  │ Python API     │  │ .NET API       │    │
│  │ Port 8000      │  │ Port 5000      │    │
│  │ (FastAPI)      │  │ (ASP.NET Core) │    │
│  └────────────────┘  └────────────────┘    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Azure Database for PostgreSQL              │
│  (Flexible Server)                          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Azure Cache for Redis                      │
└─────────────────────────────────────────────┘
```

**优点：**
- ✅ 零配置部署（类似 Heroku）
- ✅ 自动扩展
- ✅ 内置 SSL 证书
- ✅ CI/CD 集成（GitHub Actions）
- ✅ 日志和监控
- ✅ 支持自定义域名

**缺点：**
- ❌ 成本相对较高（但有免费额度）
- ❌ 灵活性不如 VM

**成本估算：**
- Python App Service (B1): $13/月（免费 12 个月）
- .NET App Service (B1): $13/月（免费 12 个月）
- PostgreSQL Flexible Server (B1ms): $12/月
- Redis Basic (C0): $16/月
- **总计**: ~$54/月（前 12 个月免费或用 $200 额度）

**部署步骤：**

#### 1. 创建资源组
```bash
az group create --name job-intel-rg --location southeastasia
```

#### 2. 部署 Python API
```bash
# 创建 App Service Plan (Linux)
az appservice plan create \
  --name job-intel-plan \
  --resource-group job-intel-rg \
  --is-linux \
  --sku B1

# 创建 Python Web App
az webapp create \
  --resource-group job-intel-rg \
  --plan job-intel-plan \
  --name job-intel-python-api \
  --runtime "PYTHON:3.10"

# 配置启动命令
az webapp config set \
  --resource-group job-intel-rg \
  --name job-intel-python-api \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"

# 部署代码（从本地或 GitHub）
az webapp deploy \
  --resource-group job-intel-rg \
  --name job-intel-python-api \
  --src-path ./scrape-api \
  --type zip
```

#### 3. 部署 .NET API
```bash
# 创建 .NET Web App
az webapp create \
  --resource-group job-intel-rg \
  --plan job-intel-plan \
  --name job-intel-dotnet-api \
  --runtime "DOTNET:8.0"

# 发布 .NET 应用
cd src/JobIntel.Api
dotnet publish -c Release -o ./publish

# 部署
az webapp deploy \
  --resource-group job-intel-rg \
  --name job-intel-dotnet-api \
  --src-path ./publish \
  --type zip
```

#### 4. 配置数据库
```bash
# 创建 PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group job-intel-rg \
  --name job-intel-postgres \
  --location southeastasia \
  --admin-user adminuser \
  --admin-password <your-password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 16 \
  --storage-size 32

# 创建数据库
az postgres flexible-server db create \
  --resource-group job-intel-rg \
  --server-name job-intel-postgres \
  --database-name jobintel
```

#### 5. 配置 Redis
```bash
az redis create \
  --resource-group job-intel-rg \
  --name job-intel-redis \
  --location southeastasia \
  --sku Basic \
  --vm-size c0
```

#### 6. 配置环境变量
```bash
# Python API
az webapp config appsettings set \
  --resource-group job-intel-rg \
  --name job-intel-python-api \
  --settings \
    DATABASE_URL="postgresql://..." \
    REDIS_URL="redis://..."

# .NET API
az webapp config appsettings set \
  --resource-group job-intel-rg \
  --name job-intel-dotnet-api \
  --settings \
    ConnectionStrings__DefaultConnection="Host=...;Database=jobintel;..." \
    ScrapeApi__BaseUrl="https://job-intel-python-api.azurewebsites.net"
```

---

### Azure 部署方案 B：Container Instances + VM（灵活）⭐⭐⭐⭐

**架构：**
```
Internet
    ↓
Azure Load Balancer
    ↓
┌─────────────────────────────────────────────┐
│  Azure VM (Ubuntu 22.04)                    │
│  ┌────────────────────────────────────┐    │
│  │  Docker Compose                    │    │
│  │  ├─ Python API (Container)         │    │
│  │  ├─ .NET API (Container)           │    │
│  │  ├─ PostgreSQL (Container)         │    │
│  │  ├─ Redis (Container)              │    │
│  │  └─ Nginx (Container)              │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**优点：**
- ✅ 完全控制
- ✅ 成本较低
- ✅ 容器化部署
- ✅ 易于迁移

**缺点：**
- ❌ 需要自己管理
- ❌ 需要配置安全组、备份等

**成本估算：**
- VM B2s (2 vCPU, 4 GB): $30/月（免费 12 个月）
- **总计**: ~$30/月

**部署步骤：**

#### 1. 创建 VM
```bash
az vm create \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard
```

#### 2. 安装 Docker
```bash
# SSH 到 VM
ssh azureuser@<VM-IP>

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"

  python-api:
    build: ./scrape-api
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/jobintel
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  dotnet-api:
    build: ./src
    environment:
      ConnectionStrings__DefaultConnection: Host=postgres;Database=jobintel;Username=admin;Password=${DB_PASSWORD}
      ScrapeApi__BaseUrl: http://python-api:8000
    depends_on:
      - postgres
      - python-api
    ports:
      - "5000:5000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - python-api
      - dotnet-api

volumes:
  postgres_data:
```

#### 4. 部署
```bash
# 克隆代码
git clone <your-repo>
cd job-intelligence

# 启动服务
docker-compose up -d
```

---

### Azure 部署方案 C：Azure Functions（Serverless）⭐⭐⭐

**适用场景**: 如果你的爬虫是定时任务（每 6 小时运行一次）

**优点：**
- ✅ 按使用付费（非常便宜）
- ✅ 自动扩展
- ✅ 无需管理服务器

**缺点：**
- ❌ 冷启动问题
- ❌ 不适合长时间运行任务

**成本估算：**
- 每月 100 万次执行免费
- 每 6 小时运行一次 = 120 次/月
- **总计**: $0/月（免费额度内）

---

## 🟠 AWS 部署方案 ⭐⭐⭐⭐⭐

### AWS 部署方案 A：Elastic Beanstalk（推荐）

**架构：**
```
Internet → ALB → EC2 Instances → RDS PostgreSQL + ElastiCache Redis
```

**优点：**
- ✅ 类似 App Service，零配置部署
- ✅ 支持 Python 和 .NET
- ✅ 自动扩展
- ✅ 免费 12 个月

**部署步骤：**

```bash
# 安装 EB CLI
pip install awsebcli

# 初始化 Python API
cd scrape-api
eb init -p python-3.10 job-intel-python-api --region ap-southeast-1
eb create job-intel-python-env

# 初始化 .NET API
cd ../src/JobIntel.Api
eb init -p dotnet-core job-intel-dotnet-api --region ap-southeast-1
eb create job-intel-dotnet-env
```

**成本估算：**
- EC2 t2.micro × 2: 免费 12 个月
- RDS db.t3.micro: 免费 12 个月
- ElastiCache t2.micro: $12/月
- **总计**: ~$12/月（前 12 个月）

---

### AWS 部署方案 B：EC2 + Docker（灵活）

**架构：** 与 Azure VM 方案类似

**优点：**
- ✅ 完全控制
- ✅ 成本低

**成本估算：**
- EC2 t2.medium (2 vCPU, 4 GB): 免费 12 个月
- **总计**: $0/月（前 12 个月）

---

## 🔵 Google Cloud Platform（GCP）⭐⭐⭐⭐

### GCP 部署方案：Cloud Run + Cloud SQL

**架构：**
```
Internet → Cloud Load Balancer → Cloud Run (Containers) → Cloud SQL
```

**优点：**
- ✅ 容器化部署
- ✅ 按使用付费
- ✅ $300 试用额度

**部署步骤：**

```bash
# 构建容器镜像
gcloud builds submit --tag gcr.io/PROJECT_ID/python-api ./scrape-api
gcloud builds submit --tag gcr.io/PROJECT_ID/dotnet-api ./src

# 部署到 Cloud Run
gcloud run deploy python-api --image gcr.io/PROJECT_ID/python-api
gcloud run deploy dotnet-api --image gcr.io/PROJECT_ID/dotnet-api
```

**成本估算：**
- Cloud Run: 按请求计费（前 200 万次免费）
- Cloud SQL (db-f1-micro): $7/月
- **总计**: ~$7/月

---

## 🟡 阿里云（Aliyun）⭐⭐⭐⭐

### Aliyun 部署方案：ECS + RDS

**优点：**
- ✅ 国内访问快
- ✅ 学生优惠（9.9元/月）
- ✅ 中文支持

**缺点：**
- ❌ 需要备案（如果使用域名）
- ❌ 海外访问慢

**成本估算：**
- ECS 学生机: ¥9.9/月
- RDS MySQL: ¥40/月
- **总计**: ~¥50/月（约 $7）

---

## 🎯 **推荐方案对比**

### 方案 1：Azure App Service（最简单）⭐⭐⭐⭐⭐

**适合人群**: 想快速部署，不想管理服务器
**成本**: $54/月（前 12 个月免费）
**难度**: ⭐（非常简单）

**优点：**
- 零配置，5 分钟部署
- 自动 SSL
- 内置监控

**缺点：**
- 成本较高（免费期后）

---

### 方案 2：Azure VM + Docker（推荐）⭐⭐⭐⭐⭐

**适合人群**: 想完全控制，学习 DevOps
**成本**: $30/月（前 12 个月免费）
**难度**: ⭐⭐⭐（中等）

**优点：**
- 完全控制
- 成本低
- 易于迁移

**缺点：**
- 需要自己配置和维护

---

### 方案 3：AWS Elastic Beanstalk（备选）⭐⭐⭐⭐

**适合人群**: 熟悉 AWS 生态
**成本**: $12/月（前 12 个月）
**难度**: ⭐⭐（简单）

---

### 方案 4：GCP Cloud Run（省钱）⭐⭐⭐⭐

**适合人群**: 想省钱，流量不大
**成本**: $7/月
**难度**: ⭐⭐⭐（中等）

---

## 🎯 **最终推荐**

### 🥇 第一推荐：Azure VM + Docker

**理由：**
1. ✅ **学习价值高** - 学习完整的 DevOps 流程
2. ✅ **成本低** - 12 个月免费，之后 $30/月
3. ✅ **灵活性强** - 完全控制，易于调试
4. ✅ **真实环境** - 模拟生产环境
5. ✅ **.NET 最佳平台** - 微软官方支持

### 🥈 第二推荐：Azure App Service

**理由：**
1. ✅ **部署最快** - 5 分钟上线
2. ✅ **维护简单** - 无需管理服务器
3. ✅ **适合演示** - 快速展示项目

### 🥉 第三推荐：AWS Elastic Beanstalk

**理由：**
1. ✅ **AWS 生态** - 适合想学 AWS 的人
2. ✅ **成本低** - 12 个月基本免费
3. ✅ **自动扩展** - 适合流量增长

---

## 📋 下一步行动

### 如果选择 Azure VM + Docker:

```bash
# 1. 注册 Azure 学生账号
https://azure.microsoft.com/en-us/free/students/

# 2. 安装 Azure CLI
brew install azure-cli

# 3. 登录
az login

# 4. 创建资源
# 参考上面的部署步骤
```

### 如果选择 Azure App Service:

```bash
# 1. 在 Azure Portal 创建 Web App
https://portal.azure.com

# 2. 配置 GitHub Actions
# 自动部署到 App Service
```

---

## 🔗 相关资源

### Azure
- [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
- [Azure App Service 文档](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Python 部署指南](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)

### AWS
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Elastic Beanstalk 文档](https://docs.aws.amazon.com/elasticbeanstalk/)

### GCP
- [GCP Free Tier](https://cloud.google.com/free)
- [Cloud Run 文档](https://cloud.google.com/run/docs)

---

**文档创建**: 2025-12-26
**推荐方案**: Azure VM + Docker
**预计部署时间**: 1-2 天
