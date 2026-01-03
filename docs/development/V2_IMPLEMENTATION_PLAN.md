# Job Intelligence Platform - V2 实施计划

**目标**: 开发完整的用户系统和前端界面，并部署到生产环境
**周期**: 2-3 个月
**开始日期**: 2025-12-26
**状态**: 🔖 计划中

---

## 📋 总体规划

### 阶段划分

```
Phase 1: 基础部署和环境准备 (Week 1-2)
         ↓
Phase 2: 用户系统后端开发 (Week 3-4)
         ↓
Phase 3: 前端框架和基础页面 (Week 5-8)
         ↓
Phase 4: 用户功能集成 (Week 9-10)
         ↓
Phase 5: 完整部署和优化 (Week 11-12)
```

---

## 🎯 Phase 1: 基础部署和环境准备

**时间**: Week 1-2 (2 周)
**目标**: 将 MVP V1 部署到生产环境，建立 CI/CD 流程

### Week 1: 服务器部署

#### Day 1-2: 云服务准备
- [ ] 选择云服务商（推荐 AWS/GCP/Aliyun）
  - [ ] 注册账号
  - [ ] 配置付款方式
  - [ ] 创建项目/资源组
- [ ] 服务器配置
  - [ ] 创建 VPS 实例（建议 2-4 vCPU, 4-8GB RAM）
  - [ ] 配置安全组（防火墙规则）
  - [ ] 生成 SSH 密钥对
  - [ ] 配置域名（可选，建议）

#### Day 3-4: 数据库和基础服务
- [ ] PostgreSQL 16 部署
  - [ ] 安装 PostgreSQL
  - [ ] 创建数据库和用户
  - [ ] 配置远程访问（如果需要）
  - [ ] 设置自动备份
- [ ] Redis 安装（为后续缓存做准备）
  - [ ] 安装 Redis
  - [ ] 配置持久化
  - [ ] 设置密码

#### Day 5-7: 应用部署
- [ ] Python API 部署
  - [ ] 安装 Python 3.10+ 和依赖
  - [ ] 配置 systemd 服务（或使用 Gunicorn + Supervisor）
  - [ ] 环境变量配置
  - [ ] 测试 API 可访问性
- [ ] .NET API 部署
  - [ ] 安装 .NET 8 SDK/Runtime
  - [ ] 发布应用（dotnet publish -c Release）
  - [ ] 配置 systemd 服务
  - [ ] 测试 API 可访问性
- [ ] Nginx 配置
  - [ ] 安装 Nginx
  - [ ] 配置反向代理（Python API → port 8000, .NET API → port 5000）
  - [ ] 配置 SSL 证书（Let's Encrypt）
  - [ ] 测试 HTTPS 访问

### Week 2: CI/CD 和监控

#### Day 8-10: 自动化部署
- [ ] GitHub Actions 配置
  - [ ] 创建 `.github/workflows/deploy.yml`
  - [ ] 配置自动化测试（pytest for Python, dotnet test for .NET）
  - [ ] 配置自动化部署（SSH 部署脚本）
  - [ ] 设置部署密钥和环境变量
- [ ] Docker 化（可选，推荐）
  - [ ] 编写 Dockerfile（Python API, .NET API）
  - [ ] 编写 docker-compose.yml
  - [ ] 测试容器化部署
  - [ ] 配置镜像仓库（Docker Hub/GitHub Container Registry）

#### Day 11-14: 监控和日志
- [ ] 应用监控
  - [ ] 配置日志系统（推荐 Serilog for .NET, Loguru for Python）
  - [ ] 集成错误追踪（可选：Sentry）
  - [ ] 配置性能监控（可选：Application Insights）
- [ ] 服务器监控
  - [ ] 安装 Node Exporter + Prometheus（可选）
  - [ ] 配置告警规则
  - [ ] 设置 Email/SMS 通知
- [ ] 数据库备份
  - [ ] 配置定时备份脚本
  - [ ] 测试备份恢复流程

**Phase 1 交付物:**
- ✅ MVP V1 在生产环境运行
- ✅ HTTPS 访问可用
- ✅ CI/CD 流程建立
- ✅ 监控和日志配置完成
- ✅ 数据开始积累

---

## 🎯 Phase 2: 用户系统后端开发

**时间**: Week 3-4 (2 周)
**目标**: 完整的用户注册/登录/认证系统

### Week 3: 核心用户功能

#### Day 15-17: 数据库设计
- [ ] 用户表设计
  ```sql
  CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      password_hash VARCHAR(255) NOT NULL,
      first_name VARCHAR(100),
      last_name VARCHAR(100),
      phone VARCHAR(20),
      is_email_verified BOOLEAN DEFAULT FALSE,
      email_verification_token VARCHAR(255),
      password_reset_token VARCHAR(255),
      password_reset_expires TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_login_at TIMESTAMP
  );
  ```
- [ ] 创建 EF Core Migration
- [ ] 应用到数据库

#### Day 18-21: 认证 API
- [ ] 安装 NuGet 包
  - [ ] Microsoft.AspNetCore.Identity.EntityFrameworkCore
  - [ ] System.IdentityModel.Tokens.Jwt
  - [ ] BCrypt.Net-Next（密码哈希）
- [ ] 实现 AuthController
  - [ ] `POST /api/auth/register` - 用户注册
  - [ ] `POST /api/auth/login` - 用户登录
  - [ ] `POST /api/auth/logout` - 登出
  - [ ] `POST /api/auth/refresh-token` - 刷新令牌
  - [ ] `GET /api/auth/me` - 获取当前用户信息
- [ ] JWT 配置
  - [ ] 配置 JWT 密钥和过期时间
  - [ ] 实现 TokenService（生成、验证 JWT）
  - [ ] 配置认证中间件
- [ ] 测试所有端点

### Week 4: 扩展功能

#### Day 22-24: Email 验证
- [ ] 集成 Email 服务
  - [ ] 选择服务商（SendGrid/AWS SES/SMTP）
  - [ ] 配置 Email 模板
  - [ ] 实现 EmailService
- [ ] Email 验证流程
  - [ ] `POST /api/auth/send-verification` - 发送验证邮件
  - [ ] `GET /api/auth/verify-email?token=xxx` - 验证邮箱
  - [ ] 更新用户 is_email_verified 状态

#### Day 25-28: 密码重置
- [ ] 密码重置流程
  - [ ] `POST /api/auth/forgot-password` - 请求重置
  - [ ] `POST /api/auth/reset-password` - 重置密码
  - [ ] 验证重置令牌
  - [ ] 更新密码哈希

**Phase 2 交付物:**
- ✅ 完整的用户认证 API
- ✅ JWT 认证中间件
- ✅ Email 验证功能
- ✅ 密码重置功能
- ✅ 所有端点测试通过

---

## 🎯 Phase 3: 前端框架和基础页面

**时间**: Week 5-8 (4 周)
**目标**: 建立前端框架，完成核心页面

### Week 5: 技术选型和项目初始化

#### Day 29-31: 前端技术栈
- [ ] 技术选型决策
  - **推荐**: Next.js 14 + TypeScript + Tailwind CSS
  - 备选: React + Vite, Vue 3 + Nuxt
- [ ] 项目初始化
  ```bash
  npx create-next-app@latest job-intelligence-frontend
  # 选择: TypeScript, Tailwind CSS, App Router
  ```
- [ ] 安装核心依赖
  - [ ] axios（HTTP 客户端）
  - [ ] react-query / swr（数据获取）
  - [ ] zustand / redux（状态管理）
  - [ ] react-hook-form（表单）
  - [ ] zod（表单验证）
  - [ ] lucide-react（图标）

#### Day 32-35: 基础架构
- [ ] 项目结构设计
  ```
  frontend/
  ├── src/
  │   ├── app/              # Next.js App Router 页面
  │   ├── components/       # React 组件
  │   │   ├── ui/          # UI 基础组件
  │   │   ├── layout/      # 布局组件
  │   │   └── features/    # 功能组件
  │   ├── lib/             # 工具函数
  │   ├── hooks/           # 自定义 Hooks
  │   ├── services/        # API 服务
  │   ├── store/           # 状态管理
  │   ├── types/           # TypeScript 类型
  │   └── styles/          # 全局样式
  ├── public/              # 静态资源
  └── tests/               # 测试文件
  ```
- [ ] 配置文件
  - [ ] API 基础 URL 配置
  - [ ] 环境变量（.env.local）
  - [ ] TypeScript 配置优化
  - [ ] ESLint + Prettier 配置
- [ ] UI 组件库集成
  - [ ] 选择: shadcn/ui（推荐）或 Ant Design / Material-UI
  - [ ] 配置主题和颜色
  - [ ] 创建通用组件（Button, Input, Card, Modal 等）

### Week 6: 核心页面开发（无认证）

#### Day 36-38: 首页和搜索
- [ ] 首页设计
  - [ ] Header（Logo, 导航, 搜索栏）
  - [ ] Hero Section（主标题、搜索表单）
  - [ ] 热门职位分类
  - [ ] Footer
- [ ] 搜索功能
  - [ ] 搜索表单组件
  - [ ] 多维度筛选（trade, location, salary）
  - [ ] 搜索建议（可选）
  - [ ] 集成 `/api/jobs` 端点

#### Day 39-42: 职位列表和详情
- [ ] 职位列表页
  - [ ] JobCard 组件（显示单个职位）
  - [ ] 分页组件
  - [ ] 排序选择（最新、薪资高低）
  - [ ] 筛选侧边栏（trade, state, salary range）
  - [ ] 加载状态和错误处理
- [ ] 职位详情页
  - [ ] 职位信息展示（完整描述）
  - [ ] 公司信息
  - [ ] 申请按钮（跳转到原站）
  - [ ] 相关职位推荐
  - [ ] 保存职位按钮（需登录）

### Week 7-8: 用户相关页面

#### Day 43-45: 登录注册页面
- [ ] 登录页面
  - [ ] 登录表单（email, password）
  - [ ] 表单验证（zod + react-hook-form）
  - [ ] 错误提示
  - [ ] "忘记密码" 链接
  - [ ] "注册" 链接
- [ ] 注册页面
  - [ ] 注册表单（email, password, confirm password, first name, last name）
  - [ ] 表单验证
  - [ ] 密码强度提示
  - [ ] "已有账号" 链接
- [ ] 集成后端 API
  - [ ] `/api/auth/login`
  - [ ] `/api/auth/register`
  - [ ] JWT 存储（localStorage/cookie）
  - [ ] 自动跳转逻辑

#### Day 46-49: 用户中心页面
- [ ] 个人中心布局
  - [ ] 侧边栏导航（个人信息、保存的职位、Job Alerts）
  - [ ] 主内容区域
- [ ] 个人信息页
  - [ ] 显示用户信息
  - [ ] 编辑个人信息表单
  - [ ] 修改密码功能
  - [ ] 头像上传（可选）

#### Day 50-56: 保存的职位和 Job Alerts
- [ ] 保存的职位页面
  - [ ] 显示已保存职位列表
  - [ ] 取消保存功能
  - [ ] 空状态提示
- [ ] Job Alerts 页面
  - [ ] 创建 Alert 表单（keywords, location, frequency）
  - [ ] Alert 列表
  - [ ] 编辑/删除 Alert
  - [ ] 暂停/激活 Alert

**Phase 3 交付物:**
- ✅ 完整的前端项目框架
- ✅ 7 个核心页面（首页、搜索、列表、详情、登录、注册、用户中心）
- ✅ 响应式设计（支持移动端）
- ✅ 与后端 API 完整集成
- ✅ 用户体验优化（加载状态、错误处理）

---

## 🎯 Phase 4: 用户功能后端集成

**时间**: Week 9-10 (2 周)
**目标**: 实现保存职位和 Job Alerts 后端功能

### Week 9: 保存的职位

#### Day 57-59: 数据库和 API
- [ ] 数据库表设计
  ```sql
  CREATE TABLE saved_jobs (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      job_id INTEGER NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
      saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      notes TEXT,
      UNIQUE(user_id, job_id)
  );
  CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);
  ```
- [ ] 创建 EF Core Migration
- [ ] 实现 SavedJobsController
  - [ ] `POST /api/saved-jobs` - 保存职位（需认证）
  - [ ] `GET /api/saved-jobs` - 获取已保存职位（需认证）
  - [ ] `DELETE /api/saved-jobs/{jobId}` - 取消保存（需认证）

#### Day 60-63: 前端集成
- [ ] SavedJobsService（API 调用）
- [ ] 保存按钮组件
- [ ] 更新职位详情页（显示保存状态）
- [ ] 更新职位列表页（显示保存状态）
- [ ] 保存的职位页面数据加载
- [ ] 测试完整流程

### Week 10: Job Alerts

#### Day 64-66: 数据库和 API
- [ ] 数据库表设计
  ```sql
  CREATE TABLE job_alerts (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      keywords VARCHAR(255) NOT NULL,
      location VARCHAR(100),
      trade VARCHAR(50),
      min_salary DECIMAL(10,2),
      employment_type VARCHAR(50),
      frequency VARCHAR(20) NOT NULL, -- 'daily', 'weekly'
      is_active BOOLEAN DEFAULT TRUE,
      last_sent_at TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX idx_job_alerts_user_id ON job_alerts(user_id);
  CREATE INDEX idx_job_alerts_active ON job_alerts(is_active) WHERE is_active = TRUE;
  ```
- [ ] 创建 EF Core Migration
- [ ] 实现 JobAlertsController
  - [ ] `POST /api/job-alerts` - 创建 Alert（需认证）
  - [ ] `GET /api/job-alerts` - 获取 Alerts（需认证）
  - [ ] `PUT /api/job-alerts/{id}` - 更新 Alert（需认证）
  - [ ] `DELETE /api/job-alerts/{id}` - 删除 Alert（需认证）

#### Day 67-70: Email 通知和前端集成
- [ ] 后台任务（Hangfire）
  - [ ] 创建 JobAlertService
  - [ ] 实现查询匹配职位逻辑
  - [ ] 生成 Email 内容
  - [ ] 发送 Email
  - [ ] 配置定时任务（每天早上 8:00）
- [ ] 前端集成
  - [ ] JobAlertsService
  - [ ] Job Alerts 管理页面完整实现
  - [ ] 测试完整流程

**Phase 4 交付物:**
- ✅ 保存的职位功能完整
- ✅ Job Alerts 功能完整
- ✅ Email 通知系统
- ✅ Hangfire 定时任务配置
- ✅ 前后端完全集成

---

## 🎯 Phase 5: 完整部署和优化

**时间**: Week 11-12 (2 周)
**目标**: 部署完整系统，优化性能和用户体验

### Week 11: 前端部署和优化

#### Day 71-73: 前端部署
- [ ] 生产构建
  ```bash
  npm run build
  ```
- [ ] 部署选择
  - 选项 A: Vercel（推荐，零配置）
  - 选项 B: 自建服务器（Nginx 静态托管）
  - 选项 C: Cloudflare Pages
- [ ] 域名配置
  - [ ] 配置主域名（如 jobintel.com）
  - [ ] API 子域名（如 api.jobintel.com）
- [ ] CORS 配置
  - [ ] 更新 .NET API CORS 策略
  - [ ] 允许前端域名访问

#### Day 74-77: 性能优化
- [ ] 前端优化
  - [ ] 图片优化（Next.js Image 组件）
  - [ ] 代码分割（动态导入）
  - [ ] 缓存策略（浏览器缓存、SWR）
  - [ ] SEO 优化（meta tags, sitemap）
- [ ] 后端优化
  - [ ] 添加 Redis 缓存（热门职位、统计数据）
  - [ ] 数据库查询优化（EXPLAIN ANALYZE）
  - [ ] API 响应压缩（gzip）
  - [ ] 限流（rate limiting）

### Week 12: 测试和上线

#### Day 78-80: 完整测试
- [ ] 功能测试
  - [ ] 用户注册流程
  - [ ] 登录和认证
  - [ ] 职位搜索和筛选
  - [ ] 保存职位
  - [ ] Job Alerts 创建和通知
  - [ ] 所有用户交互
- [ ] 性能测试
  - [ ] 负载测试（Artillery/K6）
  - [ ] 并发用户测试
  - [ ] API 响应时间验证
- [ ] 兼容性测试
  - [ ] 浏览器测试（Chrome, Safari, Firefox）
  - [ ] 移动端测试（iOS, Android）

#### Day 81-84: 上线准备和发布
- [ ] 准备工作
  - [ ] 生产环境最终检查
  - [ ] 数据库备份
  - [ ] 监控和日志确认
  - [ ] 准备回滚计划
- [ ] 软发布（Beta）
  - [ ] 邀请少量用户测试
  - [ ] 收集反馈
  - [ ] 修复 bug
- [ ] 正式上线
  - [ ] 更新 DNS
  - [ ] 发布公告
  - [ ] 监控系统状态
  - [ ] 准备用户支持

**Phase 5 交付物:**
- ✅ 完整系统部署到生产环境
- ✅ 性能优化完成
- ✅ 所有功能测试通过
- ✅ 正式上线运营

---

## 📊 技术栈总结

### 后端
- **语言**: C# (.NET 8), Python 3.10
- **框架**: ASP.NET Core, FastAPI
- **数据库**: PostgreSQL 16
- **认证**: JWT
- **后台任务**: Hangfire
- **缓存**: Redis
- **Email**: SendGrid / AWS SES

### 前端
- **框架**: Next.js 14（推荐）或 React + Vite
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **UI 库**: shadcn/ui（推荐）或 Ant Design
- **状态管理**: Zustand 或 Redux Toolkit
- **表单**: React Hook Form + Zod
- **数据获取**: SWR 或 React Query

### DevOps
- **CI/CD**: GitHub Actions
- **容器**: Docker + docker-compose
- **Web 服务器**: Nginx
- **SSL**: Let's Encrypt
- **监控**: Prometheus + Grafana（可选）
- **日志**: Serilog + ELK Stack（可选）

---

## 🎯 关键里程碑

| 里程碑 | 时间 | 状态 |
|--------|------|------|
| MVP V1 完成 | Week 0 | ✅ 已完成 |
| 基础部署完成 | Week 2 | ⏳ 计划中 |
| 用户系统完成 | Week 4 | ⏳ 计划中 |
| 前端核心页面完成 | Week 8 | ⏳ 计划中 |
| 用户功能集成完成 | Week 10 | ⏳ 计划中 |
| 正式上线 | Week 12 | ⏳ 计划中 |

---

## 📋 每周检查清单

### 每周一
- [ ] 回顾上周进度
- [ ] 更新本周计划
- [ ] 识别风险和阻塞
- [ ] 更新 DAILY_PLAN.md

### 每周五
- [ ] 完成度评估
- [ ] Demo 准备（如果有）
- [ ] 文档更新
- [ ] 下周计划调整

---

## 💡 成功要素

### 技术
1. **渐进式开发** - 先部署 MVP，再迭代功能
2. **自动化测试** - 保证质量，减少回归
3. **监控先行** - 提前发现问题
4. **文档同步** - 代码和文档一起更新

### 流程
1. **每日提交** - 保持代码仓库活跃
2. **功能分支** - 使用 Git Flow 工作流
3. **Code Review** - 自我审查或让 AI 审查
4. **持续部署** - 小步快跑，快速迭代

### 学习
1. **技术博客** - 记录关键技术决策
2. **面试准备** - 整理技术难点和解决方案
3. **Portfolio** - 同步更新 GitHub 和简历

---

## 🔗 相关文档

- [MVP V1 完成报告](../MVP_V1_COMPLETION.md)
- [技术设计文档](../core/TECHNICAL_DESIGN.md)
- [开发指南](../core/DEVELOPMENT_GUIDE.md)
- [DAILY_PLAN](DAILY_PLAN.md)

---

**文档创建**: 2025-12-26
**文档版本**: 1.0
**状态**: 🔖 等待启动
**预计完成**: 2025-03-26（3 个月后）
