# WeNexus 开发进度

## 当前状态

### 架构决策（已确认）

- **Frontend**: Next.js 15 全栈 — UI 渲染 + BFF + 简单 CRUD
- **Python Backend**: FastAPI + LangGraph — AI Agent 编排 + 内容生成
- **Java Backend**: 暂不启用，保留 scaffold
- **Database**: PostgreSQL（前后端共享）
- **Cache**: Redis（Python 后端用）

### 已完成的代码

- [x] Monorepo 基础设施（pnpm + Turborepo + pre-commit + CI/CD）
- [x] Web App 基座（ShipAny: auth, DB, i18n, 支付, RBAC, 主题）
- [x] 四域一核目录结构 scaffold（types, models, services stub, API routes stub, pages stub）
- [x] 数据库 Schema 定义（7 张领域表 + 18 张基座表 = 25 张表）
- [x] Discovery 域 services 实现（topic-service, feed-service）
- [x] Discovery 域 API routes 实现
- [x] Discovery 域 UI 组件（TopicCard, FeedView, CreateTopicForm）
- [x] Shared Kernel: Event Bus, LLM Gateway types
- [x] Roundtable 域 services 实现（expert, chat, orchestrator, autopilot, consensus）
- [x] 本地开发环境搭建（PostgreSQL + Redis + Python Backend + Frontend）
- [x] Python 后端骨架代码（FastAPI + 健康检查 + API 路由 stub + DB 连接）
- [x] 数据库 Schema 同步到 PostgreSQL（25 张表）
- [x] 前后端基础链路调通（Frontend → DB, Python → DB, Frontend ↔ Python health）
- [x] CI Pipeline 全部通过（frontend lint/typecheck/test, java build/test, python lint/typecheck/test, trivy security-scan + SARIF upload）/

### 未完成

- [ ] 前后端业务链路调通（Next.js BFF → Python API → LLM → DB → Frontend 展示）
- [ ] Roundtable 域 API routes + UI
- [ ] Deliverable 域全部
- [ ] Identity 域全部
- [ ] 种子数据
- [ ] OpenRouter API Key 配置

---

## CI/CD Pipeline 状态

**全部 4 个 Job 稳定通过**（PR #20 + #21）

| Job | 内容 | 状态 |
|-----|------|------|
| test-frontend | pnpm lint + typecheck + test (Node 20, Turborepo) | ✅ |
| test-java-backend | mvn clean test + package | ✅ |
| test-python-backend | ruff lint + mypy + pytest unit (uv) | ✅ |
| security-scan | Trivy fs scan → SARIF → GitHub Security tab | ✅ |

### 已修复的 CI 问题

- Python `db.py` 懒加载 SQLAlchemy engine（CI 无 DATABASE_URL 不报错）
- Admin app 空 scaffold 跳过 build/lint/typecheck
- Node 升级到 20（fumadocs-mdx 需要 File API）
- Turbo `test.dependsOn` 改为 `["^build"]`（仅构建依赖包，不构建 web app）
- CI build step 暂跳过（需要 DATABASE_URL 等环境变量）
- Trivy 改用 apt 仓库直装（避免 composite action 内部 `actions/checkout` 污染 git 状态）

---

## 本地环境启动方式

### 中间件

| 中间件 | 方案 | 启动方式 |
|--------|------|---------|
| PostgreSQL 16 | Homebrew | `brew services start postgresql@16` |
| Redis 8 | Homebrew | `brew services start redis` |
| AI Provider | OpenRouter | 需在 `.env.development` 配置 API Key |
| Frontend | pnpm + Turbopack | `pnpm dev --filter @wenexus/web` → localhost:3000 |
| Python Backend | uvicorn | `PYTHONPATH=src uvicorn wenexus.main:app --reload` → localhost:8000 |

### 数据库信息

- Host: localhost:5432
- Database: wenexus_dev
- User: wenexus / Password: wenexus_dev_pwd
- 25 张表已同步

### 环境配置策略

一套接口，多环境适配：

- `.env.development` — 本地开发（Homebrew PG/Redis + OpenRouter）
- `.env.staging` — 预发布（云服务 PG/Redis + OpenRouter）
- `.env.production` — 生产（云服务全套）

### 快速启动命令

```bash
# 1. 启动中间件
brew services start postgresql@16
brew services start redis

# 2. 启动 Python 后端
cd backend/python
PYTHONPATH=src python3 -m uvicorn wenexus.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 启动前端（新终端）
cd frontend
pnpm dev --filter @wenexus/web
```

### 调通验证标准

1. ~~PostgreSQL + Redis 启动~~ ✅
2. ~~Frontend 启动，首页可访问 (HTTP 200)~~ ✅
3. ~~Python Backend 启动，`/health` 返回 200~~ ✅
4. ~~Python Backend 连接 PostgreSQL 成功~~ ✅
5. 创建话题 → 数据写入 PostgreSQL → 前端可读取（待实现）
6. 发起讨论 → Next.js BFF → Python API → LLM 调用 → 消息写入 DB → 前端展示（待实现）

---

## 架构概览

```
Frontend (Next.js :3000)          Python Backend (FastAPI :8000)
  ├── UI 渲染                       ├── Roundtable 讨论引擎 (LangGraph)
  ├── Auth (Better Auth)            ├── Deliverable 内容生成
  ├── Discovery CRUD (直接 DB)      ├── LLM Gateway (OpenRouter)
  ├── Identity CRUD (直接 DB)       ├── Search/Grounding Gateway
  └── BFF → Python (AI 相关)       └── 共享 PostgreSQL + Redis

                    PostgreSQL (Homebrew :5432)
                    Redis (Homebrew :6379)
```
