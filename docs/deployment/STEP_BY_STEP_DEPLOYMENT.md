# 分阶段部署指南

**策略**: 渐进式部署，每个阶段独立测试验证
**目标**: 确保每个组件都稳定运行后再部署下一个
**更新日期**: 2026-01-03

---

## 💡 **重要提示：VM 规格选择**

根据你的 Azure 账户情况（剩余 A$298.71 额度），建议：

### **推荐方案（平衡测试与成本）**
1. **前 7 天测试期**：使用 **B2s** (2 vCPU, 4 GB RAM)
   - 成本：约 A$10-20
   - 优势：内存充足，部署顺畅，容易调试

2. **稳定后**：降级到 **B1s** (1 vCPU, 1 GB RAM)
   - 成本：$0/月（免费 12 个月）
   - 保留大部分额度用于未来

### **如何选择 VM 规格**
在下面的 Azure CLI 命令中，使用：
- **B2s 测试**: `--size Standard_B2s` (4GB 内存，推荐)
- **B1s 免费**: `--size Standard_B1s` (1GB 内存，挑战较大)

**本文档使用 B2s 作为示例**，你可以根据需要调整。

---

## 📋 部署路线图

```
阶段 1: PostgreSQL 数据库
   ↓ (测试数据库连接)
阶段 2: Python 爬虫 API
   ↓ (测试爬虫功能 + 数据写入)
阶段 3: .NET 后端 API
   ↓ (测试完整数据流)
阶段 4: Nginx 反向代理
   ↓ (测试生产环境访问)
```

---

## 🎯 阶段 1: 部署 PostgreSQL 数据库

### 目标
- 在 Azure VM 上运行 PostgreSQL 16
- 验证数据库连接正常
- 执行数据库迁移

### 步骤

#### 1.1 创建最小化 docker-compose.yml

```bash
# 在 Azure VM 上创建项目目录
mkdir -p ~/job-intelligence
cd ~/job-intelligence

# 创建第一阶段的 docker-compose
cat > docker-compose.stage1.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: jobintel-postgres
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=128MB"
      - "-c"
      - "max_connections=50"
      - "-c"
      - "work_mem=4MB"
    ports:
      - "5432:5432"  # 暴露端口用于测试
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
```

#### 1.2 创建环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
DB_PASSWORD=YourStrongPassword123!
EOF

chmod 600 .env
```

#### 1.3 启动 PostgreSQL

```bash
# 启动数据库
docker-compose -f docker-compose.stage1.yml up -d

# 查看日志
docker-compose -f docker-compose.stage1.yml logs -f postgres
```

#### 1.4 验证数据库（阶段 1 测试）

```bash
# 测试 1: 检查容器状态
docker ps | grep postgres

# 测试 2: 连接到数据库
docker exec -it jobintel-postgres psql -U admin -d jobintel

# 在 psql 中执行：
# \l              # 列出所有数据库
# \dt             # 列出所有表（应该是空的）
# SELECT version(); # 查看 PostgreSQL 版本
# \q              # 退出

# 测试 3: 从本地连接（如果需要）
psql -h <AZURE_VM_IP> -U admin -d jobintel
# 输入密码
```

### ✅ 阶段 1 完成标准

- [ ] PostgreSQL 容器运行正常（`docker ps` 显示 Up）
- [ ] 可以通过 psql 连接到数据库
- [ ] 数据库版本显示为 PostgreSQL 16.x
- [ ] 内存使用正常（`docker stats` < 200MB）

---

## 🐍 阶段 2: 部署 Python 爬虫 API

### 目标
- 部署 Python FastAPI 爬虫服务
- 测试爬虫功能
- 验证数据写入数据库

### 步骤

#### 2.1 准备 Python API 代码

```bash
# 在本地打包 Python API 代码
cd /Users/kxz/Desktop/Web-practice/job-intelligence

# 创建 Python API Dockerfile（如果还没有）
cat > scrape-api/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

#### 2.2 上传代码到 Azure VM

```bash
# 在本地执行
# 方法 1: 使用 scp
tar -czf scrape-api.tar.gz scrape-api/
scp scrape-api.tar.gz azureuser@<AZURE_VM_IP>:~/job-intelligence/

# SSH 到 Azure VM
ssh azureuser@<AZURE_VM_IP>
cd ~/job-intelligence
tar -xzf scrape-api.tar.gz

# 方法 2: 使用 Git（推荐）
# 先在本地提交代码到 GitHub，然后在 VM 上拉取
git clone https://github.com/your-username/job-intelligence.git
cd job-intelligence
```

#### 2.3 更新 docker-compose 添加 Python API

```bash
# 创建阶段 2 的 docker-compose
cat > docker-compose.stage2.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: jobintel-postgres
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=128MB"
      - "-c"
      - "max_connections=50"
      - "-c"
      - "work_mem=4MB"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  python-api:
    build:
      context: ./scrape-api
      dockerfile: Dockerfile
    container_name: jobintel-python-api
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/jobintel
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"  # 暴露端口用于测试
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
EOF
```

#### 2.4 启动 Python API

```bash
# 停止阶段 1 的容器
docker-compose -f docker-compose.stage1.yml down

# 启动阶段 2（数据库 + Python API）
docker-compose -f docker-compose.stage2.yml up -d --build

# 查看构建日志
docker-compose -f docker-compose.stage2.yml logs -f python-api
```

#### 2.5 验证 Python API（阶段 2 测试）

```bash
# 测试 1: 健康检查
curl http://localhost:8000/health
# 预期输出: {"status": "healthy"}

curl http://localhost:8000/
# 预期输出: API 基本信息

# 测试 2: 查看 API 文档
curl http://localhost:8000/docs
# 或在浏览器访问: http://<AZURE_VM_IP>:8000/docs

# 测试 3: 测试爬虫功能（抓取单个职位）
curl -X POST http://localhost:8000/api/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "source": "seek",
    "trade": "Plumber",
    "state": "VIC",
    "max_pages": 1
  }'

# 预期输出:
# {
#   "status": "success",
#   "jobs_scraped": 20-30,
#   "trade": "Plumber",
#   "state": "VIC"
# }

# 测试 4: 验证数据写入数据库
docker exec -it jobintel-postgres psql -U admin -d jobintel -c \
  "SELECT COUNT(*), trade, location_state FROM job_postings GROUP BY trade, location_state;"

# 应该看到刚才抓取的数据
```

### ✅ 阶段 2 完成标准

- [ ] Python API 容器运行正常
- [ ] `/health` 端点返回正常
- [ ] `/docs` 可以访问（Swagger UI）
- [ ] 可以成功抓取职位数据
- [ ] 数据正确写入 PostgreSQL
- [ ] 数据字段完整（trade、location_state、salary 等）
- [ ] 内存使用正常（总计 < 500MB）

### 🧪 阶段 2 完整测试清单

```bash
#!/bin/bash
# 保存为 test-stage2.sh

echo "=== 阶段 2 测试 ==="

echo "1. 测试健康检查..."
curl -f http://localhost:8000/health || exit 1

echo "2. 测试 Seek Plumber VIC..."
curl -X POST http://localhost:8000/api/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"source": "seek", "trade": "Plumber", "state": "VIC", "max_pages": 1}'

echo "3. 测试 Indeed Electrician NSW..."
curl -X POST http://localhost:8000/api/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"source": "indeed", "trade": "Electrician", "state": "NSW", "max_pages": 1}'

echo "4. 验证数据库..."
docker exec -it jobintel-postgres psql -U admin -d jobintel -c \
  "SELECT source, COUNT(*) FROM job_postings GROUP BY source;"

echo "5. 检查数据质量..."
docker exec -it jobintel-postgres psql -U admin -d jobintel -c \
  "SELECT
    COUNT(*) as total,
    COUNT(trade) as with_trade,
    COUNT(location_state) as with_state,
    COUNT(salary_min) as with_salary
  FROM job_postings;"

echo "=== 阶段 2 测试完成 ==="
```

---

## 🎯 阶段 3: 部署 .NET 后端 API

### 目标
- 部署 .NET 8 API
- 测试与 Python API 的集成
- 验证完整数据流

### 步骤

#### 3.1 准备 .NET API Dockerfile

```bash
# 在本地创建 .NET Dockerfile
cat > src/Dockerfile << 'EOF'
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# 复制项目文件
COPY ["JobIntel.Api/JobIntel.Api.csproj", "JobIntel.Api/"]
COPY ["JobIntel.Core/JobIntel.Core.csproj", "JobIntel.Core/"]
COPY ["JobIntel.Infrastructure/JobIntel.Infrastructure.csproj", "JobIntel.Infrastructure/"]
COPY ["JobIntel.Ingest/JobIntel.Ingest.csproj", "JobIntel.Ingest/"]

# 恢复依赖
RUN dotnet restore "JobIntel.Api/JobIntel.Api.csproj"

# 复制所有代码
COPY . .

# 构建
WORKDIR "/src/JobIntel.Api"
RUN dotnet build "JobIntel.Api.csproj" -c Release -o /app/build

# Publish stage
FROM build AS publish
RUN dotnet publish "JobIntel.Api.csproj" -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
EXPOSE 5000

# 复制发布文件
COPY --from=publish /app/publish .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["dotnet", "JobIntel.Api.dll"]
EOF
```

#### 3.2 上传 .NET 代码到 Azure VM

```bash
# 在本地打包（如果使用 scp）
tar -czf dotnet-api.tar.gz src/
scp dotnet-api.tar.gz azureuser@<AZURE_VM_IP>:~/job-intelligence/

# 或者使用 Git（推荐）
git add .
git commit -m "Add deployment configs"
git push

# 在 VM 上拉取
ssh azureuser@<AZURE_VM_IP>
cd ~/job-intelligence
git pull
```

#### 3.3 创建阶段 3 docker-compose

```bash
cat > docker-compose.stage3.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: jobintel-postgres
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=128MB"
      - "-c"
      - "max_connections=50"
      - "-c"
      - "work_mem=4MB"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  python-api:
    build:
      context: ./scrape-api
      dockerfile: Dockerfile
    container_name: jobintel-python-api
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/jobintel
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: unless-stopped

  dotnet-api:
    build:
      context: ./src
      dockerfile: Dockerfile
    container_name: jobintel-dotnet-api
    environment:
      ConnectionStrings__DefaultConnection: Host=postgres;Database=jobintel;Username=admin;Password=${DB_PASSWORD}
      ScrapeApi__BaseUrl: http://python-api:8000
      ASPNETCORE_URLS: http://+:5000
      ASPNETCORE_ENVIRONMENT: Production
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - python-api
    restart: unless-stopped

volumes:
  postgres_data:
EOF
```

#### 3.4 启动完整后端

```bash
# 停止阶段 2
docker-compose -f docker-compose.stage2.yml down

# 启动阶段 3（完整后端）
docker-compose -f docker-compose.stage3.yml up -d --build

# 查看构建日志（.NET 构建可能需要 5-10 分钟）
docker-compose -f docker-compose.stage3.yml logs -f dotnet-api
```

#### 3.5 运行数据库迁移

```bash
# 等待 .NET API 启动后，执行迁移
docker exec -it jobintel-dotnet-api dotnet ef database update

# 或者在容器内部
docker exec -it jobintel-dotnet-api bash
cd /app
dotnet JobIntel.Api.dll --migrate
exit
```

#### 3.6 验证 .NET API（阶段 3 测试）

```bash
# 测试 1: 健康检查
curl http://localhost:5000/health
# 预期输出: {"status": "Healthy"}

# 测试 2: 访问 Swagger
curl http://localhost:5000/swagger/index.html
# 或浏览器: http://<AZURE_VM_IP>:5000/swagger

# 测试 3: 查询职位（通过 .NET API）
curl http://localhost:5000/api/jobs?state=VIC&trade=Plumber&page=1&pageSize=10

# 预期输出:
# {
#   "items": [...],
#   "totalCount": 123,
#   "page": 1,
#   "pageSize": 10
# }

# 测试 4: 触发爬虫任务（.NET 调用 Python）
curl -X POST http://localhost:5000/api/scrape/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "trade": "Carpenter",
    "state": "QLD",
    "sources": ["seek", "indeed"]
  }'

# 测试 5: 访问 Hangfire Dashboard
curl http://localhost:5000/hangfire
# 或浏览器: http://<AZURE_VM_IP>:5000/hangfire

# 测试 6: 验证数据统计
curl http://localhost:5000/api/stats/summary
```

### ✅ 阶段 3 完成标准

- [ ] .NET API 容器运行正常
- [ ] 数据库迁移成功执行
- [ ] `/health` 端点返回正常
- [ ] Swagger UI 可访问
- [ ] 可以查询职位数据
- [ ] .NET 可以成功调用 Python API
- [ ] Hangfire Dashboard 可访问
- [ ] 定时任务正常运行
- [ ] 内存使用正常（总计 < 750MB）

### 🧪 阶段 3 完整测试清单

```bash
#!/bin/bash
# 保存为 test-stage3.sh

echo "=== 阶段 3 测试 ==="

echo "1. 测试 .NET 健康检查..."
curl -f http://localhost:5000/health || exit 1

echo "2. 测试查询职位..."
curl -f "http://localhost:5000/api/jobs?page=1&pageSize=5"

echo "3. 测试按州筛选..."
curl -f "http://localhost:5000/api/jobs?state=VIC&page=1&pageSize=5"

echo "4. 测试按行业筛选..."
curl -f "http://localhost:5000/api/jobs?trade=Plumber&page=1&pageSize=5"

echo "5. 测试统计 API..."
curl -f "http://localhost:5000/api/stats/summary"

echo "6. 测试触发爬虫..."
curl -X POST http://localhost:5000/api/scrape/trigger \
  -H "Content-Type: application/json" \
  -d '{"trade": "Electrician", "state": "NSW", "sources": ["seek"]}'

echo "7. 验证完整数据流..."
docker exec -it jobintel-postgres psql -U admin -d jobintel -c \
  "SELECT
    COUNT(*) as total_jobs,
    COUNT(DISTINCT trade) as unique_trades,
    COUNT(DISTINCT location_state) as unique_states,
    MAX(created_at) as latest_job
  FROM job_postings;"

echo "=== 阶段 3 测试完成 ==="
```

---

## 🌐 阶段 4: 部署 Nginx 反向代理（可选）

### 目标
- 添加 Nginx 反向代理
- 统一访问入口
- 准备生产环境

### 步骤

#### 4.1 创建 Nginx 配置

```bash
mkdir -p nginx

cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    client_max_body_size 10M;

    upstream python_api {
        server python-api:8000;
    }

    upstream dotnet_api {
        server dotnet-api:5000;
    }

    server {
        listen 80;
        server_name _;

        # Python API
        location /api/scrape {
            proxy_pass http://python_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # .NET API
        location /api {
            proxy_pass http://dotnet_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Swagger
        location /swagger {
            proxy_pass http://dotnet_api/swagger;
            proxy_set_header Host $host;
        }

        # Hangfire
        location /hangfire {
            proxy_pass http://dotnet_api/hangfire;
            proxy_set_header Host $host;
        }

        # Health check
        location /health {
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }
}
EOF
```

#### 4.2 最终 docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: jobintel-postgres
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=128MB"
      - "-c"
      - "max_connections=50"
      - "-c"
      - "work_mem=4MB"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - jobintel

  python-api:
    build:
      context: ./scrape-api
      dockerfile: Dockerfile
    container_name: jobintel-python-api
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/jobintel
      LOG_LEVEL: INFO
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - jobintel

  dotnet-api:
    build:
      context: ./src
      dockerfile: Dockerfile
    container_name: jobintel-dotnet-api
    environment:
      ConnectionStrings__DefaultConnection: Host=postgres;Database=jobintel;Username=admin;Password=${DB_PASSWORD}
      ScrapeApi__BaseUrl: http://python-api:8000
      ASPNETCORE_URLS: http://+:5000
      ASPNETCORE_ENVIRONMENT: Production
    depends_on:
      - postgres
      - python-api
    restart: unless-stopped
    networks:
      - jobintel

  nginx:
    image: nginx:alpine
    container_name: jobintel-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
    depends_on:
      - python-api
      - dotnet-api
    restart: unless-stopped
    networks:
      - jobintel

networks:
  jobintel:
    driver: bridge

volumes:
  postgres_data:
EOF
```

#### 4.3 启动完整系统

```bash
# 停止阶段 3
docker-compose -f docker-compose.stage3.yml down

# 启动完整系统
docker-compose up -d

# 查看所有容器
docker-compose ps
```

#### 4.4 验证 Nginx（阶段 4 测试）

```bash
# 测试 1: Nginx 健康检查
curl http://localhost/health

# 测试 2: 通过 Nginx 访问 .NET API
curl http://localhost/api/jobs?page=1&pageSize=5

# 测试 3: 通过 Nginx 访问 Python API
curl -X POST http://localhost/api/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"source": "seek", "trade": "Plumber", "state": "VIC", "max_pages": 1}'

# 测试 4: 访问 Swagger
curl http://localhost/swagger/index.html

# 测试 5: 访问 Hangfire
curl http://localhost/hangfire
```

### ✅ 阶段 4 完成标准

- [ ] Nginx 容器运行正常
- [ ] 所有 API 可通过 Nginx 访问
- [ ] 路由配置正确
- [ ] 从外部可以访问（`http://<AZURE_VM_IP>/health`）

---

## 📊 监控和维护

### 查看系统状态

```bash
# 查看所有容器
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f dotnet-api
```

### 常用操作

```bash
# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart dotnet-api

# 停止所有服务
docker-compose down

# 完全清理（删除数据卷）
docker-compose down -v
```

---

## 📋 完整测试脚本

创建一个完整的端到端测试脚本：

```bash
cat > test-complete-system.sh << 'EOF'
#!/bin/bash

echo "========================================="
echo "    Job Intelligence 完整系统测试"
echo "========================================="

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

function test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}

    echo -n "测试 $name... "

    if [ "$method" == "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d '{}')
    fi

    if [ "$response" == "200" ] || [ "$response" == "201" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response)"
        return 1
    fi
}

echo ""
echo "1. 基础健康检查"
echo "-------------------"
test_endpoint "Nginx 健康检查" "http://localhost/health"
test_endpoint ".NET API 健康" "http://localhost/api/health"
test_endpoint "Python API 健康" "http://localhost/api/scrape/health"

echo ""
echo "2. 数据查询测试"
echo "-------------------"
test_endpoint "查询所有职位" "http://localhost/api/jobs?page=1&pageSize=5"
test_endpoint "按州筛选 (VIC)" "http://localhost/api/jobs?state=VIC&page=1"
test_endpoint "按行业筛选 (Plumber)" "http://localhost/api/jobs?trade=Plumber&page=1"
test_endpoint "统计数据" "http://localhost/api/stats/summary"

echo ""
echo "3. 数据库测试"
echo "-------------------"
echo -n "数据库职位总数... "
count=$(docker exec jobintel-postgres psql -U admin -d jobintel -t -A -c "SELECT COUNT(*) FROM job_postings;")
echo -e "${GREEN}$count 条记录${NC}"

echo ""
echo "4. 容器状态"
echo "-------------------"
docker-compose ps

echo ""
echo "5. 资源使用"
echo "-------------------"
docker stats --no-stream

echo ""
echo "========================================="
echo "           测试完成！"
echo "========================================="
EOF

chmod +x test-complete-system.sh
```

---

## 🎯 总结

### 部署顺序
1. **阶段 1**: PostgreSQL → 测试数据库连接
2. **阶段 2**: Python API → 测试爬虫功能
3. **阶段 3**: .NET API → 测试完整后端
4. **阶段 4**: Nginx → 测试生产环境

### 每个阶段必须验证
- ✅ 容器状态正常
- ✅ 健康检查通过
- ✅ API 功能正常
- ✅ 数据流正确
- ✅ 内存使用合理

### 下一步
完成所有 4 个阶段后，你将拥有一个完整运行的系统，可以：
- 开始开发 V2 功能（用户系统 + 前端）
- 配置域名和 HTTPS
- 设置 CI/CD 自动部署

---

**文档创建**: 2026-01-03
**策略**: 渐进式部署
**预计总时间**: 2-3 小时
**难度**: ⭐⭐⭐（中等）
