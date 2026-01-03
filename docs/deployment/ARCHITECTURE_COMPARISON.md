# Azure 部署架构对比分析

## 概述

本文档对比两种部署架构方案，帮助你在**单 VM 部署**和**分布式部署**之间做出选择。

---

## 方案 A：单 VM 部署（Docker Compose）

### 架构图

```
Azure VM (B1s): 20.92.200.112
├── Docker Compose 编排
│   ├── PostgreSQL 16 (容器)
│   ├── Redis (容器)
│   ├── Python FastAPI (容器)
│   ├── .NET 8 API (容器)
│   └── Nginx (容器)
└── 资源: 1 vCPU, 1 GB RAM
```

### 优势

✅ **简单管理**
- 单一服务器，所有组件在一起
- 一个 `docker-compose.yml` 文件管理所有服务
- 日志和监控集中在一台机器

✅ **零额外成本**
- 只使用 1 台 B1s VM（免费 750 小时/月）
- 不消耗 PostgreSQL Flexible Server 配额
- 网络通信都在本地，无数据传输费用

✅ **快速部署**
- 从创建 VM 到服务运行：约 30 分钟
- 一次性部署，无需配置多台服务器
- 回滚简单：`docker-compose down && git pull && docker-compose up`

✅ **本地网络性能**
- 所有服务通过 Docker 内部网络通信（localhost）
- 延迟 < 1ms
- 无需配置 VNet 或防火墙规则

### 劣势

❌ **内存限制严重**
- 总内存只有 **1 GB**
- PostgreSQL + Redis + Python + .NET + Nginx 共享
- 预计分配：
  ```
  PostgreSQL:  256 MB
  Redis:        64 MB
  Python API:  256 MB
  .NET API:    256 MB
  Nginx:        32 MB
  系统保留:    136 MB
  ─────────────────
  总计:       1000 MB
  ```
- **风险**：内存不足可能导致服务崩溃或 OOM Killer 杀死进程

❌ **单点故障**
- VM 宕机 = 整个系统不可用
- 无法独立重启单个服务（除非用容器命令）

❌ **扩展性差**
- 无法单独扩展某个服务（如爬虫需要更多内存）
- 升级 VM 规格 = 所有服务都升级（成本增加）

❌ **调试困难**
- 某个服务占用过多资源，其他服务受影响
- 难以隔离性能问题

### 成本分析

| 资源 | 月成本 | 年成本 |
|------|--------|--------|
| B1s VM | **$0** (免费 750 小时) | **$0** (免费 12 个月) |
| 公网 IP | **$0** (免费 1,500 小时) | **$0** |
| 数据传输出 | **$0** (< 15 GB) | **$0** |
| **总计** | **$0/月** | **$0** |

---

## 方案 B：分布式部署（Azure 托管服务）

### 架构图

```
Azure PostgreSQL Flexible Server (B1MS)
├── 1 vCPU (Burstable)
├── 32 GB 存储
└── 免费 750 小时/月
         ↑
         │ VNet 内部通信
         │
    ┌────┴────┐
    │         │
VM 1 (B1s)   VM 2 (B1s)
Python API   .NET API
1GB RAM      1GB RAM
    │         │
    └────┬────┘
         │
    Nginx/Load Balancer
    (可选第三台 VM 或使用 Azure Load Balancer)
```

### 优势

✅ **资源隔离**
- PostgreSQL 独占 B1MS 实例（不受其他服务影响）
- Python API 独占 1 GB RAM
- .NET API 独占 1 GB RAM
- 每个服务有足够内存空间

✅ **托管数据库优势**
- **自动备份**：Azure 自动备份，保留 7-35 天
- **高可用性**：Azure 管理的故障转移（可选配置）
- **自动补丁**：PostgreSQL 安全更新自动应用
- **监控内置**：Azure Monitor 集成，无需自己配置
- **存储自动扩展**：32 GB 起，可按需增长

✅ **独立扩展**
- 爬虫负载高 → 单独升级 Python VM 到 B2s
- 数据库压力大 → 升级 PostgreSQL 到 B2MS
- API 访问量增加 → 只升级 .NET VM
- 不必为单个瓶颈升级整个系统

✅ **更好的安全性**
- PostgreSQL 不暴露公网端口（只在 VNet 内访问）
- 可为每个 VM 配置独立的网络安全组（NSG）
- 符合生产环境最佳实践

✅ **故障隔离**
- Python 爬虫崩溃 → .NET API 和数据库不受影响
- 数据库维护 → 只影响写入，读取可从缓存提供（如果配置）

### 劣势

❌ **配置复杂**
- 需要创建 VNet（虚拟网络）
- 配置子网和网络安全组
- 设置 VM 之间的私有 IP 通信
- 配置 PostgreSQL 防火墙规则（允许 VNet 访问）
- 部署时间：约 **1.5-2 小时**（vs 单 VM 30 分钟）

❌ **管理开销**
- 需要 SSH 到 3 个不同的实例（DB + 2 VMs）
- 日志分散在多个地方
- 需要配置集中式日志收集（如 Azure Log Analytics）
- 监控需要跨多个资源

❌ **潜在数据传输费用**
- 如果配置不当，VNet 之间的流量可能收费
- **正确配置**：所有资源放在**同一区域同一 VNet** → 免费
- **错误配置**：跨区域或跨 VNet → 可能产生费用

❌ **调试复杂**
- 网络问题排查困难（防火墙、NSG、VNet 路由）
- 需要理解 Azure 网络概念

### 成本分析

| 资源 | 月成本 | 年成本 |
|------|--------|--------|
| PostgreSQL Flexible Server (B1MS) | **$0** (免费 750 小时) | **$0** (免费 12 个月) |
| VM 1 - Python API (B1s) | **$0** (免费 750 小时) | **$0** |
| VM 2 - .NET API (B1s) | **$0** (可能需要额外 VM 配额) | **$0** |
| 公网 IP x2 | **$0** (免费 1,500 小时) | **$0** |
| VNet 内部流量 | **$0** (同区域同 VNet) | **$0** |
| 数据传输出 | **$0** (< 15 GB) | **$0** |
| **总计** | **$0/月** | **$0** |

**注意**：
- Azure 免费账户**可能限制并发 VM 数量**（默认通常允许 2-4 台）
- 需要检查配额：`az vm list-usage --location australiaeast`

---

## 详细对比表

| 维度 | 方案 A：单 VM | 方案 B：分布式 |
|------|--------------|---------------|
| **部署时间** | 30 分钟 | 1.5-2 小时 |
| **内存总量** | 1 GB（共享） | 3 GB+（隔离） |
| **数据库内存** | 256 MB | 1 GB+（B1MS） |
| **故障隔离** | ❌ 单点故障 | ✅ 组件隔离 |
| **扩展性** | ❌ 全部升级 | ✅ 独立扩展 |
| **管理复杂度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **网络延迟** | < 1ms（本地） | 2-5ms（VNet） |
| **自动备份** | ❌ 需自己配置 | ✅ Azure 托管 |
| **监控** | 需自己配置 | ✅ Azure Monitor |
| **成本（测试期）** | $0/月 | $0/月 |
| **调试难度** | ⭐⭐ 中等 | ⭐⭐⭐⭐ 困难 |
| **生产就绪** | ❌ 不推荐 | ✅ 符合最佳实践 |

---

## 推荐决策流程

### 选择方案 A（单 VM），如果：

✅ 你的目标是**快速验证部署流程**
✅ 你希望**最小化配置复杂度**
✅ 你计划在**测试成功后迁移到生产环境**（那时再用分布式）
✅ 你对 **Azure 网络配置不熟悉**，想先从简单开始
✅ 你的数据量和访问量都很小（测试阶段）

### 选择方案 B（分布式），如果：

✅ 你希望**直接按照生产级最佳实践部署**
✅ 你愿意**投入额外时间学习 Azure VNet 配置**
✅ 你计划**长期运行这个系统**（不只是短期测试）
✅ 你需要**数据库自动备份和高可用性**
✅ 你可能会在测试期间**模拟高负载**（需要更多内存）

---

## 我的建议

基于你当前的情况（**测试部署阶段，A$298.71 剩余额度，想快速验证**），我建议：

### 🎯 **分阶段策略**

#### **第 1 阶段（本周）：方案 A - 单 VM 快速部署**

1. 在现有 VM (20.92.200.112) 上用 Docker Compose 部署全栈
2. 验证以下功能：
   - ✅ PostgreSQL 能正常运行并存储数据
   - ✅ Python 爬虫能抓取数据并写入数据库
   - ✅ .NET API 能查询数据库并返回 JSON
   - ✅ Nginx 能正确路由请求
3. **目标**：确认所有代码在 Azure 环境下能正常运行
4. **时间投入**：半天到 1 天

#### **第 2 阶段（下周）：方案 B - 迁移到分布式**

如果第 1 阶段成功，且你确认需要长期运行：

1. 创建 Azure PostgreSQL Flexible Server
2. 迁移数据：`pg_dump` 从 Docker 导出 → `pg_restore` 到托管数据库
3. 创建第二台 B1s VM 用于 Python API
4. 配置 VNet 和网络安全组
5. 在现有 VM 上部署 .NET API
6. 配置 Nginx 作为反向代理

**优势**：
- 你已经验证了代码能运行（降低风险）
- 学习了 Docker 部署流程
- 有清晰的数据迁移路径
- 可以对比两种架构的性能差异

---

## 快速决策参考

### 如果你现在想立刻开始部署：

**选择 A**，执行以下命令：

```bash
# 继续我之前准备的 Docker 安装脚本
ssh -i ~/.ssh/jobintel-vm_key.pem azureuser@20.92.200.112
```

**预计时间**：今天就能完成基础部署

---

### 如果你想做长期规划：

**选择 B**，我会创建新的部署指南：

1. `DISTRIBUTED_DEPLOYMENT.md` - 分布式架构完整指南
2. VNet 配置脚本
3. PostgreSQL Flexible Server 创建步骤
4. 多 VM 编排指南

**预计时间**：需要 1-2 天完成完整部署

---

## 问题检查清单

在做决定前，回答以下问题：

1. **你的 Azure 账户能创建多少台 VM？**
   运行：`az vm list-usage --location australiaeast --output table`
   查看 "Total Cores" 和 "Virtual Machines" 配额

2. **你是否熟悉 VNet 和子网配置？**
   - 是 → 方案 B 更容易
   - 否 → 方案 A 学习曲线更平缓

3. **你计划运行多久？**
   - < 1 个月（测试） → 方案 A
   - > 3 个月（长期） → 方案 B

4. **数据库数据有多重要？**
   - 可以丢失（测试数据） → 方案 A
   - 需要备份保护 → 方案 B

---

## 下一步行动

### 如果选择方案 A：

我将执行：
1. SSH 到 VM 20.92.200.112
2. 安装 Docker 和 Docker Compose
3. 克隆代码仓库
4. 创建 `.env` 文件
5. 启动 `docker-compose up -d`
6. 测试每个服务的健康检查

### 如果选择方案 B：

我将创建：
1. `DISTRIBUTED_DEPLOYMENT.md` 完整指南
2. Azure CLI 脚本自动化创建资源
3. VNet 配置模板
4. 数据库迁移脚本

---

## ✅ **最终决策：方案 C - 分阶段策略**

**决策日期**: 2026-01-03
**执行人**: User + Claude
**目标**: 先快速验证部署流程，再升级到生产级架构

---

## 📋 **执行时间表**

### **第 1 阶段：单 VM 快速部署（本周，预计 1 天）**

**目标**: 在现有 VM (20.92.200.112) 上验证所有组件能正常运行

**任务清单**:
- [x] 创建 Azure B1s VM
- [x] 配置 SSH 密钥和连接
- [ ] 安装 Docker 和 Docker Compose
- [ ] 克隆代码仓库到 VM
- [ ] 配置环境变量 (.env)
- [ ] 部署阶段 1: PostgreSQL 数据库
- [ ] 测试数据库连接和基本操作
- [ ] 部署阶段 2: Python 爬虫 API
- [ ] 测试爬虫抓取功能
- [ ] 部署阶段 3: .NET 后端 API
- [ ] 测试 API 端点和数据查询
- [ ] 部署阶段 4: Nginx 反向代理
- [ ] 端到端测试完整流程

**验收标准**:
1. ✅ 所有 Docker 容器正常运行
2. ✅ PostgreSQL 能存储和查询数据
3. ✅ Python API 能抓取 Seek 数据并写入数据库
4. ✅ .NET API 能返回职位数据 JSON
5. ✅ Hangfire 定时任务能自动触发爬虫
6. ✅ Nginx 能正确路由所有请求

**预计资源使用**:
```
总内存: 1 GB
├── PostgreSQL: ~256 MB
├── Python API:  ~256 MB
├── .NET API:    ~256 MB
├── Nginx:       ~32 MB
└── 系统保留:    ~200 MB
```

**风险提示**:
- ⚠️ 内存可能不足，需要监控 `docker stats`
- ⚠️ 如果 OOM，暂时禁用 Redis 或降低 PostgreSQL 配置
- ⚠️ 这是测试环境，不适合生产流量

---

### **第 2 阶段：升级到分布式架构（下周，预计 1-2 天）**

**前置条件**: 第 1 阶段所有测试通过

**目标**: 迁移到生产级架构，享受托管数据库和资源隔离的好处

**任务清单**:
- [ ] **Day 1 - 数据库迁移**
  - [ ] 创建 Azure PostgreSQL Flexible Server (B1MS)
  - [ ] 配置防火墙规则（允许 VNet 访问）
  - [ ] 从 Docker PostgreSQL 导出数据: `pg_dump`
  - [ ] 导入到 Azure PostgreSQL: `pg_restore`
  - [ ] 验证数据完整性
  - [ ] 配置自动备份（7 天保留）

- [ ] **Day 2 - 网络配置**
  - [ ] 创建 VNet 和子网
  - [ ] 配置网络安全组 (NSG)
  - [ ] 创建第二台 B1s VM 用于 Python API
  - [ ] 配置 VM 之间的私有 IP 通信

- [ ] **Day 3 - 服务迁移**
  - [ ] 在 VM 1 上部署 .NET API（连接到 Azure PostgreSQL）
  - [ ] 在 VM 2 上部署 Python API（连接到 Azure PostgreSQL）
  - [ ] 配置 Nginx 反向代理（可选：使用 Azure Load Balancer）
  - [ ] 更新环境变量（数据库连接字符串）

- [ ] **Day 4 - 测试和验证**
  - [ ] 端到端功能测试
  - [ ] 性能对比测试（vs 单 VM）
  - [ ] 故障隔离测试（重启单个服务）
  - [ ] 配置 Azure Monitor 监控

**新架构资源分配**:
```
Azure PostgreSQL (B1MS)
├── 1 vCPU (Burstable)
├── 1 GB+ RAM
└── 32 GB 存储

VM 1 - .NET API (B1s)
├── 1 vCPU
├── 1 GB RAM
└── .NET 8 API + Hangfire + Nginx

VM 2 - Python API (B1s)
├── 1 vCPU
├── 1 GB RAM
└── FastAPI + 爬虫引擎

总内存: 3 GB+ (vs 1 GB)
```

**优势对比**:
| 指标 | 第 1 阶段（单 VM） | 第 2 阶段（分布式） | 提升 |
|------|-------------------|-------------------|------|
| 总内存 | 1 GB | 3 GB+ | **3x** |
| 数据库内存 | 256 MB | 1 GB+ | **4x** |
| 故障隔离 | ❌ 单点故障 | ✅ 组件隔离 | **高可用** |
| 自动备份 | ❌ 需手动配置 | ✅ Azure 托管 | **生产就绪** |
| 扩展性 | ❌ 全部升级 | ✅ 独立扩展 | **灵活** |

---

## 🎯 **立即开始：第 1 阶段执行步骤**

### **Step 1: 安装 Docker**

```bash
# SSH 到 VM
ssh -i ~/.ssh/jobintel-vm_key.pem azureuser@20.92.200.112

# 更新包管理器
sudo apt update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install -y docker-compose-plugin

# 重新登录以应用组权限
exit
ssh -i ~/.ssh/jobintel-vm_key.pem azureuser@20.92.200.112

# 验证安装
docker --version
docker compose version
```

### **Step 2: 克隆代码仓库**

```bash
# 安装 Git（如果没有）
sudo apt install -y git

# 克隆仓库（需要替换为你的仓库地址）
# 选项 1: HTTPS（需要输入密码或 token）
git clone https://github.com/yourusername/job-intelligence.git

# 选项 2: SSH（需要配置 GitHub SSH key）
# git clone git@github.com:yourusername/job-intelligence.git

# 进入项目目录
cd job-intelligence
```

### **Step 3: 配置环境变量**

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=jobintel
DB_USER=admin
DB_PASSWORD=your_secure_password_here

# Python API
PYTHON_API_PORT=8000

# .NET API
ASPNETCORE_ENVIRONMENT=Production
DOTNET_API_PORT=5000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Hangfire
HANGFIRE_USERNAME=admin
HANGFIRE_PASSWORD=your_hangfire_password_here
EOF

# 设置文件权限（保护敏感信息）
chmod 600 .env

# 生成强密码（可选）
echo "建议的数据库密码: $(openssl rand -base64 32)"
echo "建议的 Hangfire 密码: $(openssl rand -base64 32)"
```

### **Step 4: 启动服务（按阶段）**

按照 [STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md) 中的 4 个阶段依次部署。

**快速参考**:
```bash
# 阶段 1: PostgreSQL
docker compose up -d postgres
docker compose logs -f postgres
docker compose exec postgres psql -U admin -d jobintel

# 阶段 2: Python API
docker compose up -d python-api
curl http://localhost:8000/health

# 阶段 3: .NET API
docker compose up -d dotnet-api
curl http://localhost:5000/api/health

# 阶段 4: Nginx
docker compose up -d nginx
curl http://localhost/api/health
```

---

## 📊 **成功指标**

### **第 1 阶段成功标准**:
- [ ] 所有容器状态为 "Up"
- [ ] 数据库能接受连接并查询
- [ ] Python API 能成功抓取至少 1 个职位
- [ ] .NET API 能返回职位列表
- [ ] Hangfire Dashboard 可访问
- [ ] Nginx 能正确路由请求
- [ ] 内存使用 < 900 MB

### **第 2 阶段成功标准**:
- [ ] Azure PostgreSQL 连接成功
- [ ] 数据迁移无丢失
- [ ] 所有 VM 通过 VNet 通信
- [ ] 每个服务独立重启不影响其他服务
- [ ] Azure Monitor 显示健康状态
- [ ] 数据库自动备份正常运行

---

## 🚧 **回滚计划**

如果第 2 阶段出现问题，可以快速回滚到第 1 阶段：

```bash
# 1. 保留 Docker PostgreSQL 的备份
docker compose exec postgres pg_dump -U admin jobintel > backup_before_migration.sql

# 2. 如果 Azure PostgreSQL 有问题，修改 .env 回到本地数据库
# DB_HOST=postgres  # 改回 Docker 容器名

# 3. 重启服务
docker compose restart dotnet-api python-api

# 4. 恢复数据（如果需要）
docker compose exec -T postgres psql -U admin jobintel < backup_before_migration.sql
```

---

## 💰 **总成本**

| 阶段 | 资源 | 月成本 | 年成本 |
|------|------|--------|--------|
| **第 1 阶段** | 1x B1s VM | **$0** | **$0** (12 月免费) |
| **第 2 阶段** | 1x PostgreSQL B1MS<br>2x B1s VM | **$0** | **$0** (12 月免费) |
| **第 13 个月起** | 同上 | **~$50** | **~$600** |

**注意**:
- 所有资源必须在**同一区域** (australiaeast) 以避免数据传输费用
- 免费期结束后可以选择停止或降级资源

---

## 📚 **相关文档**

- **执行指南**: [STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md) - 第 1 阶段详细步骤
- **Azure 完整指南**: [AZURE_FREE_DEPLOYMENT_GUIDE.md](AZURE_FREE_DEPLOYMENT_GUIDE.md) - 所有 Azure 配置
- **免费资源清单**: [Azure-free.md](Azure-free.md) - 可用的免费服务
- **下一步开发**: [V2_IMPLEMENTATION_PLAN.md](../development/V2_IMPLEMENTATION_PLAN.md) - 用户系统和前端计划

---

## ✅ **决策确认**

- ✅ **方案选择**: 方案 C - 分阶段策略
- ✅ **第 1 阶段**: 单 VM Docker Compose 部署（本周）
- ✅ **第 2 阶段**: 分布式架构迁移（下周）
- ✅ **当前 VM**: 20.92.200.112 (B1s, 1 vCPU, 1 GB RAM)
- ✅ **下一步行动**: 安装 Docker 并开始第 1 阶段部署

**准备开始第 1 阶段部署！** 🚀
