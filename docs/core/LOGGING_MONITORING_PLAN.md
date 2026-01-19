# 日志监控计划

**创建日期**: 2026-01-19
**状态**: 📋 规划中
**优先级**: P1 - 重要 (支持 Bug 修复验证)

---

## 📋 目录

- [背景与目标](#背景与目标)
- [短期方案 (立即可用)](#短期方案-立即可用)
- [中期方案 (1-2 天)](#中期方案-1-2-天)
- [长期方案 (可选)](#长期方案-可选)
- [实施计划](#实施计划)

---

## 背景与目标

### 当前问题

**2026-01-19 Bug 修复背景**:
- 修复了两个关键 Bug (DateTime + Duplicate Key)
- 需要验证修复效果
- 需要监控内存使用趋势
- 需要追踪 Hangfire 任务执行情况

### 监控目标

**核心指标**:
1. ✅ **Bug 修复验证**
   - DateTime Kind 错误数量 = 0
   - Duplicate Key 错误数量 = 0

2. ✅ **系统健康**
   - 内存使用率 < 85%
   - API 响应时间 < 200ms
   - 数据库连接稳定

3. ✅ **任务执行**
   - Hangfire 任务成功率 > 95%
   - 爬取任务完成率 > 90%
   - 数据插入成功率 > 98%

### 关键需求

**必须追踪的错误**:
```
1. DateTime Kind=Unspecified 错误
   - 错误信息: "Cannot write DateTime with Kind=Unspecified"
   - 期望: 0 次

2. Duplicate Key Violation 错误
   - 错误信息: "duplicate key value violates unique constraint \"uq_source_external_id\""
   - 期望: 0 次

3. 其他数据库错误
   - DbUpdateException
   - 连接超时
```

---

## 短期方案 (立即可用)

### 方案 A: Docker Logs ✅ **当前使用**

**优点**:
- ✅ 无需配置,立即可用
- ✅ 直接访问容器日志
- ✅ 可以实时跟踪

**缺点**:
- ❌ 容器重启后日志丢失
- ❌ 没有持久化存储
- ❌ 查询功能有限

#### 使用方法

**1. 查看最近日志**
```bash
# 查看最近 100 行
docker logs jobintel-dotnet-api --tail 100

# 查看最近 200 行并搜索错误
docker logs jobintel-dotnet-api --tail 200 | grep -i "error\|exception"
```

**2. 实时跟踪日志**
```bash
# 实时查看新日志
docker logs -f jobintel-dotnet-api

# 实时查看并高亮错误
docker logs -f jobintel-dotnet-api | grep --color -E "error|exception|fail|$"
```

**3. 搜索特定错误**
```bash
# 检查 DateTime 错误
docker logs jobintel-dotnet-api --tail 500 | grep -i "kind=unspecified"

# 检查 Duplicate Key 错误
docker logs jobintel-dotnet-api --tail 500 | grep -i "uq_source_external_id"

# 统计错误数量
docker logs jobintel-dotnet-api --tail 1000 | grep -c "Error"
```

**4. 通过 Azure Run Command 远程查看**
```bash
az vm run-command invoke \
  --resource-group job-intelligence-rg \
  --name jobintel-vm \
  --command-id RunShellScript \
  --scripts "docker logs jobintel-dotnet-api --tail 100 | grep -E 'Error|Exception'"
```

#### 监控脚本

创建本地监控脚本以便快速检查:

**文件**: `scripts/check-logs.sh`
```bash
#!/bin/bash

echo "=== Bug 修复验证 ==="
echo "DateTime Kind 错误数:"
az vm run-command invoke \
  --resource-group job-intelligence-rg \
  --name jobintel-vm \
  --command-id RunShellScript \
  --scripts "docker logs jobintel-dotnet-api --tail 500 | grep -c 'kind=unspecified' || echo 0" \
  --query "value[0].message" -o tsv | tail -1

echo "Duplicate Key 错误数:"
az vm run-command invoke \
  --resource-group job-intelligence-rg \
  --name jobintel-vm \
  --command-id RunShellScript \
  --scripts "docker logs jobintel-dotnet-api --tail 500 | grep -c 'uq_source_external_id' || echo 0" \
  --query "value[0].message" -o tsv | tail -1

echo ""
echo "=== 系统健康检查 ==="
az vm run-command invoke \
  --resource-group job-intelligence-rg \
  --name jobintel-vm \
  --command-id RunShellScript \
  --scripts "curl -s http://localhost:5000/api/health && echo && free -h && docker stats --no-stream" \
  --query "value[0].message" -o tsv
```

**使用**:
```bash
chmod +x scripts/check-logs.sh
./scripts/check-logs.sh
```

---

### 方案 B: Hangfire Dashboard ✅ **推荐开启**

**优点**:
- ✅ 已经集成,无需额外开发
- ✅ 可视化任务执行状态
- ✅ 查看失败原因和重试次数
- ✅ 手动触发任务

**缺点**:
- ⚠️ 需要开放端口 (安全考虑)
- ⚠️ 没有认证 (默认配置)

#### 配置步骤

**1. 开放 NSG 端口** (可选 - 如需外部访问)

```bash
# 允许本机 IP 访问 Hangfire Dashboard
az network nsg rule create \
  --resource-group job-intelligence-rg \
  --nsg-name jobintel-nsg \
  --name AllowHangfireDashboard \
  --priority 120 \
  --source-address-prefixes $(curl -s ifconfig.me) \
  --destination-port-ranges 5000 \
  --access Allow \
  --protocol Tcp \
  --description "Allow Hangfire Dashboard access from my IP"
```

**2. 访问 Dashboard**

```
http://20.92.200.112:5000/hangfire
```

**3. 监控内容**

- **Jobs** 页面: 查看所有后台任务
- **Recurring Jobs**: 查看定时任务配置
- **Failed Jobs**: 查看失败任务和错误信息
- **Retries**: 查看重试队列
- **Servers**: 查看 Hangfire 服务器状态

#### 安全建议

**选项 1: 仅内网访问** (推荐)
- 不开放外部端口
- 通过 SSH 隧道访问:
  ```bash
  ssh -L 5000:localhost:5000 azureuser@20.92.200.112
  # 然后访问 http://localhost:5000/hangfire
  ```

**选项 2: IP 白名单**
- 只允许特定 IP 访问
- 使用上面的 NSG 规则

**选项 3: 添加认证** (未来)
- 配置 Hangfire 认证
- 需要修改代码和重新部署

---

## 中期方案 (1-2 天)

### 方案 C: Azure Application Insights ⭐ **推荐**

**优点**:
- ✅ Azure 原生集成
- ✅ 自动收集日志、性能、异常
- ✅ 强大的查询语言 (Kusto/KQL)
- ✅ 可视化 Dashboard
- ✅ 告警功能
- ✅ 免费额度 (5 GB/月)

**缺点**:
- ⏰ 需要配置 (30 分钟)
- 📦 需要添加 NuGet 包
- 🚀 需要重新部署

#### 配置步骤

**1. 创建 Application Insights 资源**

```bash
# 创建 Application Insights
az monitor app-insights component create \
  --app jobintel-insights \
  --location australiaeast \
  --resource-group job-intelligence-rg \
  --application-type web \
  --kind web

# 获取 Instrumentation Key
az monitor app-insights component show \
  --app jobintel-insights \
  --resource-group job-intelligence-rg \
  --query "instrumentationKey" -o tsv
```

**2. 添加 NuGet 包**

**文件**: `src/JobIntel.Api/JobIntel.Api.csproj`
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.ApplicationInsights.AspNetCore" Version="2.22.0" />
</ItemGroup>
```

**3. 配置 Application Insights**

**文件**: `src/JobIntel.Api/appsettings.json`
```json
{
  "ApplicationInsights": {
    "InstrumentationKey": "${APPLICATIONINSIGHTS_INSTRUMENTATION_KEY}",
    "EnableAdaptiveSampling": true,
    "EnablePerformanceCounterCollectionModule": true
  }
}
```

**文件**: `src/JobIntel.Api/Program.cs`
```csharp
// 添加 Application Insights
builder.Services.AddApplicationInsightsTelemetry(builder.Configuration);
```

**4. 添加环境变量**

**文件**: `.env` (on VM)
```env
APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=<从 Azure 获取的 key>
```

**文件**: `docker-compose.yml`
```yaml
services:
  dotnet-api:
    environment:
      - APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=${APPLICATIONINSIGHTS_INSTRUMENTATION_KEY}
```

**5. 重新部署**

```bash
# 推送到 GitHub 触发 CI/CD
git add .
git commit -m "feat: Add Application Insights monitoring"
git push origin main
```

#### 使用 Application Insights

**1. 访问 Portal**
```
https://portal.azure.com
→ Application Insights
→ jobintel-insights
```

**2. 查看实时指标**
- Live Metrics Stream: 实时请求、异常、性能
- Performance: 响应时间趋势
- Failures: 失败请求和异常

**3. 使用 Kusto 查询**

**查找 DateTime Kind 错误**:
```kusto
exceptions
| where timestamp > ago(24h)
| where outerMessage contains "Kind=Unspecified"
| summarize count() by bin(timestamp, 1h)
| render timechart
```

**查找 Duplicate Key 错误**:
```kusto
exceptions
| where timestamp > ago(24h)
| where outerMessage contains "uq_source_external_id"
| summarize count() by bin(timestamp, 1h)
| render timechart
```

**API 性能分析**:
```kusto
requests
| where timestamp > ago(24h)
| summarize avg(duration), percentiles(duration, 50, 95, 99) by name
| order by avg_duration desc
```

**内存使用趋势**:
```kusto
performanceCounters
| where timestamp > ago(24h)
| where name == "% Processor Time" or name == "Available Bytes"
| summarize avg(value) by name, bin(timestamp, 1h)
| render timechart
```

#### 配置告警

**告警 1: DateTime 错误告警**
```bash
az monitor metrics alert create \
  --name "DateTime-Kind-Error-Alert" \
  --resource-group job-intelligence-rg \
  --scopes "/subscriptions/{sub}/resourceGroups/job-intelligence-rg/providers/Microsoft.Insights/components/jobintel-insights" \
  --condition "count exceptions | where outerMessage contains 'Kind=Unspecified' > 0" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "Alert when DateTime Kind error occurs"
```

**告警 2: 内存使用过高**
```bash
az monitor metrics alert create \
  --name "High-Memory-Usage-Alert" \
  --resource-group job-intelligence-rg \
  --scopes "/subscriptions/{sub}/resourceGroups/job-intelligence-rg/providers/Microsoft.Compute/virtualMachines/jobintel-vm" \
  --condition "avg Percentage CPU > 85" \
  --window-size 15m \
  --evaluation-frequency 5m \
  --severity 2 \
  --description "Alert when memory usage > 85% for 15 minutes"
```

---

## 长期方案 (可选)

### 方案 D: Serilog 文件日志

**适用场景**:
- 需要本地调试
- Application Insights 不够详细
- 需要离线分析日志

#### 配置步骤

**1. 添加 NuGet 包**
```xml
<PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
<PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />
```

**2. 配置 Serilog**

**文件**: `src/JobIntel.Api/appsettings.json`
```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "Console"
      },
      {
        "Name": "File",
        "Args": {
          "path": "/var/log/jobintel/api-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 7,
          "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}"
        }
      }
    ]
  }
}
```

**3. 挂载日志目录**

**文件**: `docker-compose.yml`
```yaml
services:
  dotnet-api:
    volumes:
      - ./logs:/var/log/jobintel
```

**4. 配置 logrotate** (可选)
```bash
# 在 VM 上配置日志轮转
cat > /etc/logrotate.d/jobintel <<EOF
/home/azureuser/job-intelligence/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

## 实施计划

### 第一阶段: 立即执行 (今天)

**目标**: 验证 Bug 修复效果

**任务**:
1. ✅ 使用 Docker Logs 监控
   - 每 6 小时检查一次
   - 搜索 DateTime 和 Duplicate Key 错误
   - 记录内存使用趋势

2. ⏳ 考虑开放 Hangfire Dashboard
   - 评估安全风险
   - 如需要,开放 IP 白名单
   - 或使用 SSH 隧道访问

**监控频率**: 每 6 小时
**持续时间**: 24-48 小时
**工具**: Docker Logs + Azure Run Command

---

### 第二阶段: 1-2 天后

**目标**: 建立长期监控

**任务**:
1. 配置 Application Insights
   - 创建 Azure 资源
   - 添加 SDK 到代码
   - 配置环境变量
   - 重新部署

2. 设置告警规则
   - DateTime 错误告警
   - Duplicate Key 错误告警
   - 内存使用过高告警
   - API 响应时间告警

3. 创建监控 Dashboard
   - 关键指标可视化
   - 错误趋势图
   - 性能指标

**预计时间**: 2-3 小时
**优先级**: P1 (重要)

---

### 第三阶段: 后续优化 (可选)

**目标**: 完善监控体系

**任务**:
1. 添加文件日志 (Serilog)
2. 配置 Hangfire 认证
3. 集成 Azure Monitor Alerts
4. 设置日志归档策略

**优先级**: P2 (次要)

---

## 监控检查清单

### 日常检查 (每 6-12 小时)

- [ ] 检查 API 健康状态
- [ ] 查看 Docker Logs 错误数量
- [ ] 检查内存使用率
- [ ] 验证 Hangfire 任务执行

### 每周检查

- [ ] 回顾 Application Insights 趋势
- [ ] 分析异常日志
- [ ] 评估性能指标
- [ ] 更新告警阈值 (如需要)

### 每月检查

- [ ] 审查监控成本
- [ ] 优化日志保留策略
- [ ] 更新监控文档
- [ ] 评估监控有效性

---

## 成本估算

### Application Insights

**免费额度**:
- 数据摄入: 5 GB/月
- 数据保留: 90 天

**预估使用**:
- 日志数据: ~50 MB/天
- 月度用量: ~1.5 GB/月
- **成本**: $0 (在免费额度内)

### Docker Logs

**存储**:
- 容器日志: ~20 MB/天
- 最多保留 7 天
- **成本**: $0 (使用 VM 磁盘)

### Hangfire Dashboard

**资源**:
- 已集成,无额外成本
- **成本**: $0

**总计**: $0/月 ✅

---

## 相关文档

- [Bug 修复记录 2026-01-19](BUG_FIXES_2026-01-19.md) - 需要监控的 Bug
- [Azure 部署总结](../deployment/DEPLOYMENT_SUMMARY_2026-01-05.md)
- [CI/CD 部署指南](../deployment/CICD_DEPLOYMENT.md)

---

**文档维护者**: 项目团队
**最后更新**: 2026-01-19
**下次审查**: 实施 Application Insights 后
