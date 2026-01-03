# Azure 免费账户部署指南

**适用账户**: Azure 免费账户（非学生版）
**免费期限**: 12 个月 + $200 额度（30 天内使用）
**项目**: Job Intelligence Platform
**更新日期**: 2025-12-26

---

## 🎁 Azure 免费账户提供什么？

根据你的截图，Azure 免费账户包含：

### 💰 **1. $200 额度（前 30 天）**
- 可用于任何 Azure 服务
- 30 天内必须使用完，否则过期
- **策略**: 用于测试和初期部署

### 🆓 **2. 12 个月免费服务**

#### **计算服务**
- ✅ **750 小时/月 Linux VM (B1s)**
  - 1 vCPU, 1 GB RAM
  - 足够运行轻量级应用
  - 可以运行 Docker

- ✅ **750 小时/月 Windows VM (B1s)**
  - 如果需要 Windows 环境

#### **数据库**
- ✅ **250 GB SQL Database**
  - 或者可以用 PostgreSQL Flexible Server
  - 注意：PostgreSQL 可能需要付费

#### **存储**
- ✅ **5 GB Blob 存储**
  - 用于存储文件、日志

- ✅ **5 GB 文件存储**

#### **网络**
- ✅ **15 GB 出站流量**
  - 足够初期使用

### ♾️ **3. 永久免费服务**

- ✅ **Azure Functions** - 每月 100 万次执行免费
- ✅ **Azure App Service** - 10 个 Web/移动/API 应用
- ✅ **Azure DevOps** - 5 个用户免费

---

## 🎯 **推荐部署方案：单 VM + Docker**

### 为什么选择单 VM 方案？

**优点：**
1. ✅ **完全免费** - 12 个月内不花一分钱
2. ✅ **简单直接** - 所有服务在一台机器上
3. ✅ **易于管理** - 只需要维护一台服务器
4. ✅ **学习价值高** - 完整的 DevOps 实践

**限制：**
1. ⚠️ **性能有限** - B1s (1 vCPU, 1 GB RAM)
2. ⚠️ **不适合高流量** - 适合 MVP 和演示
3. ⚠️ **单点故障** - 一台机器挂了就全挂

**适用场景：**
- ✅ MVP 演示
- ✅ 个人项目
- ✅ 学习和实践
- ✅ 低流量应用（< 1000 PV/天）

---

## 🏗️ **架构设计**

```
Internet (HTTPS)
    ↓
Azure VM B1s (1 vCPU, 1 GB RAM, Ubuntu 22.04)
    ↓
┌────────────────────────────────────────────┐
│  Docker Compose                            │
│  ┌──────────────────────────────────────┐ │
│  │  Nginx (反向代理 + SSL)              │ │
│  │  Port 80, 443                        │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  .NET API                            │ │
│  │  Port 5000                           │ │
│  │  Memory: ~300 MB                     │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Python API                          │ │
│  │  Port 8000                           │ │
│  │  Memory: ~200 MB                     │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  PostgreSQL 16                       │ │
│  │  Port 5432                           │ │
│  │  Memory: ~200 MB                     │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │  Redis (可选)                        │ │
│  │  Port 6379                           │ │
│  │  Memory: ~50 MB                      │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘

总内存使用: ~750 MB / 1024 MB (73%)
```

---

## 📋 **部署步骤（完整指南）**

### Phase 1: 创建 Azure 账户和 VM

#### **Step 1: 注册 Azure 免费账户**（5 分钟）

1. 访问：https://azure.microsoft.com/free/
2. 点击 "Start free"
3. 登录 Microsoft 账户（或创建新账户）
4. 填写信息：
   - 国家/地区：选择你的国家
   - 手机号码：验证身份
   - 信用卡：**仅用于验证身份，不会扣款**
5. 完成注册

**注意：**
- ✅ 免费账户不会自动升级到付费
- ✅ $200 额度用完或 30 天后会提示你升级
- ✅ 12 个月免费服务会继续提供

#### **Step 2: 安装 Azure CLI**（2 分钟）

```bash
# macOS
brew install azure-cli

# 验证安装
az --version
```

#### **Step 3: 登录 Azure**（1 分钟）

```bash
# 登录
az login

# 会打开浏览器，登录你的 Azure 账户

# 查看订阅
az account show
```

#### **Step 4: 创建资源组**（1 分钟）

```bash
# 创建资源组（建议选择离你近的区域）
# 选项：
# - eastasia (香港)
# - southeastasia (新加坡)
# - japaneast (东京)

az group create \
  --name job-intel-rg \
  --location southeastasia

# 验证
az group list --output table
```

#### **Step 5: 创建虚拟机**（5 分钟）

```bash
# 创建 VM (B1s - 免费层)
az vm create \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --image Ubuntu2204 \
  --size Standard_B1s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --public-ip-address-allocation static

# 输出会包含：
# - publicIpAddress: 你的公网 IP
# - 保存这个 IP，后面会用到
```

**重要：保存输出信息**
```json
{
  "publicIpAddress": "xx.xx.xx.xx",  // 👈 保存这个 IP
  "privateIpAddress": "10.0.0.4",
  ...
}
```

#### **Step 6: 配置防火墙规则**（2 分钟）

```bash
# 打开 HTTP (80)
az vm open-port \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --port 80 \
  --priority 1001

# 打开 HTTPS (443)
az vm open-port \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --port 443 \
  --priority 1002

# 验证
az network nsg list \
  --resource-group job-intel-rg \
  --output table
```

---

### Phase 2: 服务器配置

#### **Step 7: SSH 到服务器**（1 分钟）

```bash
# 使用你的公网 IP
ssh azureuser@xx.xx.xx.xx

# 首次连接会提示确认，输入 yes
```

#### **Step 8: 安装 Docker**（5 分钟）

```bash
# 更新包管理器
sudo apt update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以应用组权限
exit
ssh azureuser@xx.xx.xx.xx

# 验证安装
docker --version
docker-compose --version
```

#### **Step 9: 安装 Git 和其他工具**（2 分钟）

```bash
# 安装 Git
sudo apt install -y git vim curl wget

# 配置 Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

### Phase 3: 部署应用

#### **Step 10: 克隆代码**（2 分钟）

```bash
# 克隆你的项目（如果已推送到 GitHub）
git clone https://github.com/your-username/job-intelligence.git
cd job-intelligence

# 或者从本地上传
# 在本地执行：
# scp -r /path/to/job-intelligence azureuser@xx.xx.xx.xx:~/
```

#### **Step 11: 创建优化的 docker-compose.yml**（10 分钟）

由于 B1s 只有 1 GB 内存，我们需要优化配置：

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL - 优化内存使用
  postgres:
    image: postgres:16-alpine  # 使用 alpine 版本节省内存
    container_name: jobintel-postgres
    environment:
      POSTGRES_DB: jobintel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      # 内存优化配置
      POSTGRES_INITDB_ARGS: "-c shared_buffers=128MB -c max_connections=50"
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

  # Redis - 轻量级配置
  redis:
    image: redis:7-alpine
    container_name: jobintel-redis
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 64mb
      --maxmemory-policy allkeys-lru
    restart: unless-stopped
    networks:
      - jobintel

  # Python API
  python-api:
    build:
      context: ./scrape-api
      dockerfile: Dockerfile
    container_name: jobintel-python-api
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/jobintel
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - jobintel

  # .NET API
  dotnet-api:
    build:
      context: ./src
      dockerfile: Dockerfile
    container_name: jobintel-dotnet-api
    environment:
      ConnectionStrings__DefaultConnection: Host=postgres;Database=jobintel;Username=admin;Password=${DB_PASSWORD}
      ScrapeApi__BaseUrl: http://python-api:8000
      ASPNETCORE_URLS: http://+:5000
    depends_on:
      - postgres
      - python-api
    restart: unless-stopped
    networks:
      - jobintel

  # Nginx - 反向代理
  nginx:
    image: nginx:alpine
    container_name: jobintel-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
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
```

#### **Step 12: 创建 Dockerfile**（5 分钟）

**Python API Dockerfile:**
```dockerfile
# scrape-api/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.NET API Dockerfile:**
```dockerfile
# src/Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 5000

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["JobIntel.Api/JobIntel.Api.csproj", "JobIntel.Api/"]
COPY ["JobIntel.Core/JobIntel.Core.csproj", "JobIntel.Core/"]
COPY ["JobIntel.Infrastructure/JobIntel.Infrastructure.csproj", "JobIntel.Infrastructure/"]
COPY ["JobIntel.Ingest/JobIntel.Ingest.csproj", "JobIntel.Ingest/"]
RUN dotnet restore "JobIntel.Api/JobIntel.Api.csproj"
COPY . .
WORKDIR "/src/JobIntel.Api"
RUN dotnet build "JobIntel.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "JobIntel.Api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "JobIntel.Api.dll"]
```

#### **Step 13: 创建 Nginx 配置**（5 分钟）

```bash
# 创建目录
mkdir -p nginx
```

**nginx/nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    # 上传限制
    client_max_body_size 10M;

    # 上游服务器
    upstream python_api {
        server python-api:8000;
    }

    upstream dotnet_api {
        server dotnet-api:5000;
    }

    # HTTP 重定向到 HTTPS（暂时注释，先用 HTTP）
    # server {
    #     listen 80;
    #     server_name _;
    #     return 301 https://$host$request_uri;
    # }

    # HTTP 服务器（开发/测试用）
    server {
        listen 80;
        server_name _;

        # Python API
        location /api/scrape {
            proxy_pass http://python_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # .NET API
        location /api {
            proxy_pass http://dotnet_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Hangfire Dashboard
        location /hangfire {
            proxy_pass http://dotnet_api/hangfire;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 健康检查
        location /health {
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }
}
```

#### **Step 14: 创建环境变量文件**（2 分钟）

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# 数据库密码（请修改为强密码）
DB_PASSWORD=your_strong_password_here

# Redis 密码（请修改为强密码）
REDIS_PASSWORD=your_redis_password_here
EOF

# 设置权限
chmod 600 .env
```

#### **Step 15: 启动服务**（5 分钟）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

#### **Step 16: 验证部署**（2 分钟）

```bash
# 检查容器状态
docker-compose ps

# 应该看到所有服务都是 Up 状态

# 测试 API
curl http://localhost/api/health
curl http://localhost/api/scrape/health

# 从外部测试（在你本地电脑）
curl http://xx.xx.xx.xx/api/health
```

---

### Phase 4: 配置 SSL（可选）

#### **Step 17: 安装 Certbot**（5 分钟）

```bash
# 如果你有域名，可以配置免费 SSL 证书

# 安装 Certbot
sudo apt install -y certbot

# 获取证书（替换为你的域名）
sudo certbot certonly --standalone -d yourdomain.com

# 证书会保存在 /etc/letsencrypt/live/yourdomain.com/
```

#### **Step 18: 更新 Nginx 配置启用 HTTPS**

如果你已经有域名并获取了 SSL 证书，更新 nginx 配置：

```nginx
# nginx/nginx.conf (HTTPS 版本)
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

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$host$request_uri;
    }

    # HTTPS 服务器
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL 证书配置
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL 安全配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;

        # Python API
        location /api/scrape {
            proxy_pass http://python_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        # .NET API
        location /api {
            proxy_pass http://dotnet_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        # Hangfire Dashboard
        location /hangfire {
            proxy_pass http://dotnet_api/hangfire;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 健康检查
        location /health {
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }
}
```

**复制 SSL 证书到 nginx 目录：**
```bash
# 创建 SSL 目录
mkdir -p nginx/ssl

# 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# 设置权限
sudo chown -R $USER:$USER nginx/ssl
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem

# 重启 Nginx
docker-compose restart nginx
```

---

## 💰 **成本估算**

### 免费期内（12 个月）

| 服务 | 规格 | 成本 |
|------|------|------|
| VM B1s | 1 vCPU, 1 GB RAM | **免费** (750 小时/月) |
| 公网 IP | 静态 IP | **免费** (前 12 个月) |
| 存储 | 30 GB SSD | **免费** |
| 出站流量 | < 15 GB/月 | **免费** |
| **总计** | | **$0/月** |

### 免费期后（第 13 个月起）

| 服务 | 成本 |
|------|------|
| VM B1s | ~$10/月 |
| 公网 IP | ~$3/月 |
| 存储 | ~$1/月 |
| **总计** | **~$14/月** |

---

## 📊 **性能优化建议**

### 内存优化

由于只有 1 GB 内存，需要注意：

1. **PostgreSQL 配置**
   ```bash
   # 已在 docker-compose.yml 中配置
   shared_buffers=128MB
   max_connections=50
   work_mem=4MB
   ```

2. **Redis 配置**
   ```bash
   # 限制最大内存 64MB
   maxmemory 64mb
   maxmemory-policy allkeys-lru
   ```

3. **监控内存使用**
   ```bash
   # 查看内存使用
   free -h

   # 查看各容器内存使用
   docker stats
   ```

4. **如果内存不够，可以：**
   - ❌ 暂时不启动 Redis（缓存功能暂时禁用）
   - ✅ 升级到 B2s (2 vCPU, 4 GB) - 需要付费约 $30/月

---

## 🔧 **常用管理命令**

```bash
# 查看所有容器
docker-compose ps

# 查看日志
docker-compose logs -f [service-name]

# 重启服务
docker-compose restart [service-name]

# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 进入容器
docker-compose exec [service-name] bash

# 查看资源使用
docker stats
```

---

## 🔍 **常见问题和故障排查**

### 问题 1: 容器无法启动

**症状：**
```bash
docker-compose ps
# 显示某个服务状态为 Exit 或 Restarting
```

**排查步骤：**
```bash
# 1. 查看详细日志
docker-compose logs [service-name]

# 2. 检查内存使用
free -h
docker stats

# 3. 如果是内存不足，尝试：
# - 减少 PostgreSQL 内存配置
# - 暂时禁用 Redis
# - 升级到 B2s VM
```

---

### 问题 2: API 无法从外部访问

**症状：**
```bash
# 从本地电脑测试
curl http://xx.xx.xx.xx/api/health
# 连接超时或拒绝
```

**排查步骤：**
```bash
# 1. 检查容器内部访问
ssh azureuser@xx.xx.xx.xx
curl http://localhost/api/health
# 如果内部可以访问，说明是防火墙问题

# 2. 检查 Azure 防火墙规则
az network nsg rule list \
  --resource-group job-intel-rg \
  --nsg-name job-intel-vmNSG \
  --output table

# 3. 确保 80 和 443 端口已开放
az vm open-port \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --port 80 \
  --priority 1001

# 4. 检查 Ubuntu 防火墙（ufw）
sudo ufw status
# 如果启用了，需要允许端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

### 问题 3: 数据库连接失败

**症状：**
```
Error: could not connect to server: Connection refused
```

**排查步骤：**
```bash
# 1. 检查 PostgreSQL 容器状态
docker-compose ps postgres

# 2. 查看 PostgreSQL 日志
docker-compose logs postgres

# 3. 检查环境变量
cat .env
# 确保 DB_PASSWORD 已设置

# 4. 手动测试连接
docker-compose exec postgres psql -U admin -d jobintel
```

---

### 问题 4: 内存不足 (Out of Memory)

**症状：**
```
docker stats
# 显示内存使用接近 100%
```

**解决方案：**

**方案 1: 优化配置（不花钱）**
```yaml
# 修改 docker-compose.yml

# PostgreSQL - 进一步降低内存
postgres:
  command:
    - "shared_buffers=64MB"  # 从 128MB 降到 64MB
    - "max_connections=20"    # 从 50 降到 20

# 暂时禁用 Redis
# redis:
#   ...
```

**方案 2: 启用交换空间（Swap）**
```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证
free -h
```

**方案 3: 升级 VM（需要付费）**
```bash
# 升级到 B2s (2 vCPU, 4 GB RAM) - 约 $30/月
az vm resize \
  --resource-group job-intel-rg \
  --name job-intel-vm \
  --size Standard_B2s
```

---

### 问题 5: Docker 构建失败

**症状：**
```
ERROR: failed to solve: process "/bin/sh -c ..." did not complete successfully
```

**排查步骤：**
```bash
# 1. 检查磁盘空间
df -h

# 2. 清理 Docker 缓存
docker system prune -a

# 3. 逐个构建查看详细错误
docker-compose build python-api
docker-compose build dotnet-api

# 4. 如果是网络问题（下载超时）
# 修改 Dockerfile 添加镜像源（针对中国用户）
```

---

### 问题 6: SSL 证书无法获取

**症状：**
```
Certbot failed to authenticate some domains
```

**解决方案：**
```bash
# 1. 确保域名已正确解析到 VM IP
dig yourdomain.com
nslookup yourdomain.com

# 2. 确保 80 端口未被占用
sudo lsof -i :80

# 3. 停止 Nginx 容器后再申请证书
docker-compose stop nginx
sudo certbot certonly --standalone -d yourdomain.com

# 4. 证书申请成功后，重启 Nginx
docker-compose start nginx
```

---

### 问题 7: 定时任务不执行

**症状：**
- Hangfire Dashboard 显示任务为 "Enqueued" 但从不执行

**排查步骤：**
```bash
# 1. 查看 .NET API 日志
docker-compose logs dotnet-api

# 2. 检查数据库连接
docker-compose exec postgres psql -U admin -d jobintel -c "\dt"

# 3. 检查 Hangfire 表
docker-compose exec postgres psql -U admin -d jobintel -c "SELECT * FROM hangfire.job LIMIT 5;"

# 4. 手动触发任务测试
# 访问 http://xx.xx.xx.xx/hangfire
# 找到任务 → 点击 "Trigger now"
```

---

### 问题 8: 爬虫抓取失败

**症状：**
```
HTTP 403 Forbidden 或 429 Too Many Requests
```

**解决方案：**
```bash
# 1. 检查 Python API 日志
docker-compose logs python-api

# 2. 降低抓取频率
# 修改 .NET API 的定时任务配置

# 3. 添加请求头和延迟
# 在 Python 爬虫代码中：
# - 添加 User-Agent
# - 增加请求间隔
# - 使用代理（如果需要）
```

---

### 问题 9: VM 性能慢

**症状：**
- API 响应时间 > 5 秒
- 页面加载缓慢

**优化建议：**

1. **启用 Redis 缓存**（如果内存足够）
2. **优化数据库查询**
   ```sql
   -- 添加索引
   CREATE INDEX idx_trade ON job_postings(trade);
   CREATE INDEX idx_state ON job_postings(location_state);
   CREATE INDEX idx_posted_at ON job_postings(posted_at);
   ```
3. **启用 Nginx Gzip 压缩**
   ```nginx
   gzip on;
   gzip_types text/plain application/json;
   ```
4. **考虑升级 VM**

---

### 问题 10: SSH 连接断开

**症状：**
```
packet_write_wait: Connection to xx.xx.xx.xx port 22: Broken pipe
```

**解决方案：**
```bash
# 在本地 ~/.ssh/config 添加：
Host azure-vm
    HostName xx.xx.xx.xx
    User azureuser
    ServerAliveInterval 60
    ServerAliveCountMax 3

# 然后使用：
ssh azure-vm
```

---

## 📱 **监控和维护**

### 设置基本监控

```bash
# 创建监控脚本
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Status ==="
echo "Time: $(date)"
echo ""
echo "Memory:"
free -h
echo ""
echo "Disk:"
df -h
echo ""
echo "Docker Containers:"
docker-compose ps
echo ""
echo "Docker Stats:"
docker stats --no-stream
EOF

chmod +x ~/monitor.sh

# 添加到 crontab（每小时检查一次）
(crontab -l 2>/dev/null; echo "0 * * * * ~/monitor.sh >> ~/monitor.log") | crontab -
```

### 设置自动备份

```bash
# 创建备份脚本
cat > ~/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U admin jobintel > $BACKUP_DIR/db_$DATE.sql

# 压缩
gzip $BACKUP_DIR/db_$DATE.sql

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF

chmod +x ~/backup.sh

# 每天凌晨 3 点自动备份
(crontab -l 2>/dev/null; echo "0 3 * * * ~/backup.sh") | crontab -
```

### 设置日志轮转

```bash
# 创建 logrotate 配置
sudo bash -c 'cat > /etc/logrotate.d/docker-compose << EOF
/home/azureuser/job-intelligence/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF'
```

---

## 🎯 **下一步**

部署完成后：

1. ✅ 测试所有 API 端点
2. ✅ 配置域名（可选）
3. ✅ 启用 HTTPS（可选）
4. ✅ 配置 GitHub Actions 自动部署
5. ✅ 设置监控和告警
6. ✅ 开始开发 V2 功能

---

## 📋 **检查清单**

部署前：
- [ ] Azure 账户已注册
- [ ] Azure CLI 已安装
- [ ] 本地代码已提交到 Git

部署中：
- [ ] VM 已创建
- [ ] 防火墙规则已配置
- [ ] Docker 已安装
- [ ] 代码已上传
- [ ] 环境变量已配置
- [ ] 服务已启动

部署后：
- [ ] 所有容器运行正常
- [ ] API 端点可访问
- [ ] 数据库连接正常
- [ ] Hangfire Dashboard 可访问

---

## 📝 **快速参考卡**

### 核心命令速查

```bash
# === 服务管理 ===
docker-compose up -d              # 启动所有服务
docker-compose down               # 停止所有服务
docker-compose restart            # 重启所有服务
docker-compose ps                 # 查看服务状态
docker-compose logs -f            # 查看实时日志

# === 监控 ===
docker stats                      # 查看资源使用
free -h                           # 查看内存
df -h                             # 查看磁盘

# === 数据库 ===
docker-compose exec postgres psql -U admin -d jobintel

# === 备份 ===
~/backup.sh                       # 手动备份数据库

# === SSH ===
ssh azureuser@xx.xx.xx.xx         # 连接到 VM
```

### 重要 URL

| 服务 | URL |
|------|-----|
| API 健康检查 | `http://your-ip/api/health` |
| Swagger UI | `http://your-ip/swagger` |
| Hangfire Dashboard | `http://your-ip/hangfire` |
| Python API 健康检查 | `http://your-ip/api/scrape/health` |

### 成本汇总

| 阶段 | 成本 |
|------|------|
| 前 12 个月 | **$0/月** |
| 第 13 个月起 | **~$14/月** (B1s VM) |
| 升级到 B2s | **~$30/月** (2 vCPU, 4 GB) |

---

## 🎓 **学习收获**

通过完成这个部署，你将学会：

✅ Azure 云服务基础知识
✅ Docker 和 Docker Compose 实战
✅ Nginx 反向代理配置
✅ PostgreSQL 数据库管理
✅ SSL/HTTPS 证书配置
✅ Linux 服务器运维
✅ 监控和日志管理
✅ 内存优化和性能调优

---

## 📚 **相关文档**

- [V2 实施计划](../development/V2_IMPLEMENTATION_PLAN.md) - 下一阶段开发计划
- [云平台对比](CLOUD_PLATFORM_COMPARISON.md) - Azure vs AWS vs GCP
- [数据检查指南](../tutorials/DATA_CHECKING_GUIDE.md) - 7 种数据验证方法
- [技术设计文档](../core/TECHNICAL_DESIGN.md) - 系统架构

---

## 💡 **最佳实践提示**

1. **定期备份** - 设置自动备份脚本，每天备份数据库
2. **监控资源** - 定期查看内存和磁盘使用，避免突然崩溃
3. **日志管理** - 使用 logrotate 防止日志文件占满磁盘
4. **安全更新** - 定期更新系统和 Docker 镜像
   ```bash
   sudo apt update && sudo apt upgrade
   docker-compose pull
   docker-compose up -d
   ```
5. **域名使用** - 建议绑定域名并配置 HTTPS，提升专业度
6. **成本控制** - 定期查看 Azure 账单，确保在免费额度内
   ```bash
   az consumption usage list --output table
   ```
7. **性能测试** - 部署后进行压力测试，确保系统稳定性

---

## ⚠️ **重要注意事项**

1. ⚠️ **免费账户限制**
   - B1s VM 性能有限，不适合高流量生产环境
   - 12 个月后需要付费或迁移
   - $200 额度只有 30 天有效期

2. ⚠️ **内存管理**
   - 1 GB RAM 非常紧张，需要精心优化
   - 建议启用 swap 作为缓冲
   - 生产环境建议升级到 B2s 或更高

3. ⚠️ **数据安全**
   - 定期备份数据库（自动脚本已提供）
   - .env 文件包含敏感信息，不要提交到 Git
   - 使用强密码

4. ⚠️ **成本意识**
   - 监控资源使用，避免超出免费额度
   - 不用时可以停止 VM（停止后不计费）
   ```bash
   az vm stop --resource-group job-intel-rg --name job-intel-vm
   az vm start --resource-group job-intel-rg --name job-intel-vm
   ```

---

## 🚀 **下一步行动**

完成部署后，建议按以下顺序进行：

1. **第 1 天**: 完成基础部署，确保所有服务运行正常
2. **第 2-3 天**: 配置监控、备份、日志管理
3. **第 4-5 天**: 性能测试和优化
4. **第 6-7 天**: （可选）配置域名和 HTTPS
5. **第 2 周起**: 开始 V2 功能开发（用户系统 + 前端）

---

**文档创建**: 2025-12-26
**文档版本**: 1.0
**适用账户**: Azure 免费账户（非学生版）
**预计部署时间**: 1-2 小时
**难度**: ⭐⭐⭐（中等）
**维护**: 需要基本的 Linux 和 Docker 知识
