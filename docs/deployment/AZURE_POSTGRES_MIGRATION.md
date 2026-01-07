# Azure PostgreSQL 迁移计划

**创建日期**: 2026-01-07
**状态**: 准备执行
**目标**: 将数据库从 VM 本地 PostgreSQL 迁移到 Azure PostgreSQL Flexible Server (免费层)

---

## 📋 背景

### 问题分析
- **VM 内存不足**: B1s VM (847 MB total RAM) 在运行 26 小时后达到 97% 内存使用率 (819 MB) 并崩溃
- **内存增长**: 从初始 540 MB (64%) 增长到 819 MB (97%)，增加了 279 MB (51%)
- **资源限制**: 单个 VM 无法长期稳定运行所有服务（PostgreSQL + Python API + .NET API + Hangfire）

### 解决方案 (Option C)
采用混合部署架构：
- **Azure PostgreSQL Flexible Server** (B1MS, 免费 750 小时/月)
- **Python API + .NET API** 继续运行在单个 B1s VM 上

### 预期效果
- **内存使用**: 从 97% (819 MB) 降低到 27% (268 MB)
- **内存节省**: 551 MB (70% 减少)
- **成本**: $0/月 (完全使用免费层)
- **可靠性**: Azure 托管数据库，自动备份和高可用性

---

## ✅ 已完成步骤

### 1. 配置文件修改

#### docker-compose.yml
- ✅ 移除了 `postgres` 服务配置
- ✅ 移除了 `postgres_data` 卷定义
- ✅ 更新了 `dotnet-api` 的数据库连接字符串格式
- ✅ 移除了 `python-api` 对 postgres 的依赖
- ✅ 移除了 `dotnet-api` 对 postgres 健康检查的依赖
- ✅ 添加了 `SslMode=Require` 以支持 Azure PostgreSQL SSL 连接

#### .env.example
- ✅ 更新了数据库配置参数
- ✅ 添加了 `DB_HOST` 和 `DB_PORT` 参数
- ✅ 添加了 Azure PostgreSQL 示例格式注释
- ✅ 移除了本地 PostgreSQL 端口配置

---

## 🚀 待执行步骤

### 第一阶段: 数据备份 (如果 VM 可恢复)

如果能够恢复 VM 访问：

```bash
# 1. SSH 进入 VM
ssh azureuser@<vm-public-ip>

# 2. 检查 PostgreSQL 容器状态
docker ps -a | grep postgres

# 3. 导出数据库备份
docker exec jobintel-postgres pg_dump -U admin jobintel > /tmp/jobintel_backup.sql

# 4. 下载备份到本地
scp azureuser@<vm-public-ip>:/tmp/jobintel_backup.sql ~/Desktop/jobintel_backup.sql
```

**注意**: 如果 VM 无法恢复，数据库当前应该是空的（刚部署），可以跳过备份步骤。

---

### 第二阶段: 创建 Azure PostgreSQL Flexible Server

#### 2.1 登录 Azure
```bash
az login
```

#### 2.2 创建 PostgreSQL Flexible Server
```bash
# 设置变量
RESOURCE_GROUP="job-intelligence-rg"
LOCATION="australiaeast"
SERVER_NAME="jobintel-db-$(openssl rand -hex 4)"  # 生成唯一名称
ADMIN_USER="jobinteladmin"
ADMIN_PASSWORD="<生成一个强密码>"

# 创建 PostgreSQL Flexible Server (B1MS 免费层)
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --location $LOCATION \
  --admin-user $ADMIN_USER \
  --admin-password "$ADMIN_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 16 \
  --storage-size 32 \
  --public-access 0.0.0.0 \
  --yes

# 记录输出的服务器名称
echo "Server FQDN: $SERVER_NAME.postgres.database.azure.com"
```

#### 2.3 配置防火墙规则
```bash
# 获取 VM 的公网 IP
VM_PUBLIC_IP=$(az vm show -d -g $RESOURCE_GROUP -n jobintel-vm --query publicIps -o tsv)

# 添加 VM IP 到防火墙白名单
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --rule-name "Allow-VM" \
  --start-ip-address $VM_PUBLIC_IP \
  --end-ip-address $VM_PUBLIC_IP

# （可选）添加本地开发机器 IP
MY_IP=$(curl -s ifconfig.me)
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --rule-name "Allow-Dev-Machine" \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

#### 2.4 创建数据库
```bash
# 创建 jobintel 数据库
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $SERVER_NAME \
  --database-name jobintel
```

---

### 第三阶段: 数据迁移（如果有备份）

#### 3.1 测试连接
```bash
# 从本地测试连接
psql "host=$SERVER_NAME.postgres.database.azure.com port=5432 dbname=jobintel user=$ADMIN_USER password=$ADMIN_PASSWORD sslmode=require"
```

#### 3.2 导入数据（如果有备份）
```bash
# 从本地导入备份
psql "host=$SERVER_NAME.postgres.database.azure.com port=5432 dbname=jobintel user=$ADMIN_USER password=$ADMIN_PASSWORD sslmode=require" < ~/Desktop/jobintel_backup.sql
```

**如果没有备份**: 跳过此步骤，.NET API 的自动迁移功能会在启动时创建表结构。

---

### 第四阶段: 更新 VM 配置

#### 4.1 重启 VM（如果当前崩溃）
```bash
# 通过 Azure Portal 或 CLI 重启 VM
az vm restart --resource-group $RESOURCE_GROUP --name jobintel-vm
```

#### 4.2 SSH 进入 VM
```bash
ssh azureuser@<vm-public-ip>
```

#### 4.3 更新 .env 文件
```bash
cd ~/job-intelligence

# 备份当前 .env
cp .env .env.backup

# 编辑 .env 文件
nano .env
```

更新以下内容：
```env
# Database Configuration (Azure PostgreSQL Flexible Server)
DB_HOST=<your-server-name>.postgres.database.azure.com
DB_PORT=5432
DB_NAME=jobintel
DB_USER=jobinteladmin
DB_PASSWORD=<your-admin-password>

# Hangfire Configuration
HANGFIRE_USERNAME=admin
HANGFIRE_PASSWORD=<your-hangfire-password>
```

#### 4.4 拉取最新配置
```bash
# 拉取更新后的 docker-compose.yml
git pull origin main

# 或者手动下载
curl -o docker-compose.yml https://raw.githubusercontent.com/<your-repo>/main/docker-compose.yml
```

---

### 第五阶段: 启动服务

#### 5.1 停止旧服务
```bash
cd ~/job-intelligence
docker compose down
```

#### 5.2 清理旧的 PostgreSQL 数据（可选）
```bash
# 删除本地 PostgreSQL 数据卷（如果不需要）
docker volume rm job-intelligence_postgres_data
```

#### 5.3 启动新服务
```bash
# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

---

### 第六阶段: 验证和测试

#### 6.1 检查容器状态
```bash
docker ps
docker compose ps
```

预期输出：
```
NAME                    STATUS          PORTS
jobintel-python-api     Up X seconds    0.0.0.0:8000->8000/tcp
jobintel-dotnet-api     Up X seconds    0.0.0.0:5000->5000/tcp
```

注意：**不应该**再有 `jobintel-postgres` 容器。

#### 6.2 测试 API 健康状态
```bash
# 测试 Python API
curl http://localhost:8000/health

# 测试 .NET API
curl http://localhost:5000/api/health
```

#### 6.3 验证数据库连接
检查 .NET API 日志，应该看到：
```
info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      Applying database migrations...
info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      Database migrations applied successfully
```

#### 6.4 检查 Hangfire Dashboard
访问 `http://<vm-public-ip>:5000/hangfire`，验证：
- Dashboard 可以访问
- 定时任务已配置
- 无错误日志

#### 6.5 监控内存使用
```bash
# 持续监控内存使用
watch -n 5 'free -h && echo "---" && docker stats --no-stream'
```

预期结果：
- 总内存使用应该在 **200-300 MB (25-35%)**
- 显著低于之前的 819 MB (97%)

---

## 📊 成功指标

### 性能指标
- ✅ 内存使用率 < 40%
- ✅ Python API 响应时间 < 500ms
- ✅ .NET API 响应时间 < 1s
- ✅ 数据库连接成功率 100%

### 功能指标
- ✅ 所有 API 端点正常响应
- ✅ Hangfire 定时任务正常执行
- ✅ 数据库读写操作正常
- ✅ 自动迁移功能正常工作

### 稳定性指标
- ✅ 服务运行 24 小时无崩溃
- ✅ 内存增长率 < 5% per day
- ✅ 无 OOM (Out of Memory) 错误

---

## 🔧 故障排查

### 问题 1: 无法连接到 Azure PostgreSQL

**可能原因**:
- 防火墙规则未正确配置
- VM IP 地址变化

**解决方案**:
```bash
# 检查当前 VM IP
curl ifconfig.me

# 更新防火墙规则
az postgres flexible-server firewall-rule update \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --rule-name "Allow-VM" \
  --start-ip-address <new-vm-ip> \
  --end-ip-address <new-vm-ip>
```

### 问题 2: SSL 连接错误

**错误信息**: `SSL connection required`

**解决方案**:
确保连接字符串包含 `SslMode=Require`：
```
Host=xxx.postgres.database.azure.com;Port=5432;Database=jobintel;Username=admin;Password=xxx;SslMode=Require
```

### 问题 3: .NET API 启动失败

**检查步骤**:
```bash
# 查看详细日志
docker logs jobintel-dotnet-api

# 检查环境变量
docker exec jobintel-dotnet-api env | grep DB_
```

### 问题 4: 自动迁移失败

**可能原因**:
- 数据库权限不足
- 网络连接问题

**解决方案**:
```bash
# 手动执行迁移
docker exec -it jobintel-dotnet-api dotnet ef database update
```

---

## 📝 回滚计划

如果迁移失败，可以回滚到本地 PostgreSQL：

### 1. 恢复旧的 docker-compose.yml
```bash
git checkout HEAD~1 docker-compose.yml
```

### 2. 恢复旧的 .env
```bash
cp .env.backup .env
```

### 3. 重启服务
```bash
docker compose down
docker compose up -d
```

---

## 🎯 下一步优化（未来）

完成迁移后，可以考虑的进一步优化：

1. **数据库性能调优**
   - 配置连接池大小
   - 添加索引
   - 启用查询性能分析

2. **监控和告警**
   - 配置 Azure Monitor
   - 设置内存使用告警
   - 配置数据库性能监控

3. **高可用性**
   - 配置数据库副本
   - 启用自动备份保留
   - 配置灾难恢复计划

4. **安全加固**
   - 使用 Azure Key Vault 存储密码
   - 启用 Azure AD 认证
   - 配置 VNet 集成

---

## 📚 相关文档

- [Azure PostgreSQL 定价](https://azure.microsoft.com/pricing/details/postgresql/flexible-server/)
- [Azure 免费层限制](../deployment/Azure-free.md)
- [部署总结 2026-01-05](DEPLOYMENT_SUMMARY_2026-01-05.md)
- [学习总结 2026-01-05](../LEARNING_SUMMARY_2026-01-05.md)

---

**准备者**: Claude Code
**审核状态**: 待用户确认
**预计执行时间**: 30-60 分钟
**风险等级**: 低（可完全回滚）
