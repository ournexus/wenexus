# WeNexus 开发进度

## 当前状态

### 架构决策（已确认）

- **Frontend**: Next.js 15 全栈 — UI 渲染 + BFF + 简单 CRUD
- **Python Backend**: FastAPI + LangGraph — AI Agent 编排 + 内容生成
- **Java Backend**: 暂不启用，保留 scaffold
- **Database**: PostgreSQL（前后端共享）
- **Cache**: Redis（Python 后端用）

### Python 后端分层架构

```
backend/python/src/wenexus/
├── main.py                     # 入口：组装各层、启动应用
├── config/
│   └── __init__.py             # Settings（pydantic-settings）
├── facade/                     # API 网关层（HTTP 关注点）
│   ├── deps.py                 # 共享依赖：get_session_token, get_current_user, get_optional_user
│   ├── roundtable.py           # Roundtable 路由 (stub)
│   └── deliverable.py          # Deliverable 路由 (stub)
├── app/                        # 编排层（空，待实现）
├── service/
│   └── auth.py                 # authenticate(), revoke_session()
├── repository/
│   ├── db.py                   # engine, get_db, check_db_connection
│   └── auth.py                 # query_user_by_token(), delete_session()
└── util/
    └── schema.py               # UserInfo 跨层 DTO
```

**依赖规则**：facade → app → service → repository，单向向下，util/config 是基础设施层所有层均可导入。

### 已完成

- [x] Monorepo 基础设施（pnpm + Turborepo + pre-commit + CI/CD）
- [x] Web App 基座（ShipAny: auth, DB, i18n, 支付, RBAC, 主题）
- [x] 四域一核目录结构 scaffold（types, models, services stub, API routes stub, pages stub）
- [x] 数据库 Schema 定义（7 张领域表 + 18 张基座表 = 25 张表）
- [x] Discovery 域 services 实现（topic-service, feed-service）
- [x] Discovery 域 API routes + UI 组件（TopicCard, FeedView, CreateTopicForm）
- [x] Shared Kernel: Event Bus, LLM Gateway types
- [x] Roundtable 域 services 实现（expert, chat, orchestrator, autopilot, consensus）
- [x] 本地开发环境搭建（PostgreSQL + Redis + Python Backend + Frontend）
- [x] 前后端基础链路调通（Frontend → DB, Python → DB, Frontend ↔ Python health）
- [x] CI Pipeline 全部通过（frontend lint/typecheck/test, java build/test, python lint/typecheck/test, trivy security-scan）
- [x] Python 后端分层架构重构（config/facade/app/service/repository/util 六层）
- [x] Python 认证模块实现（共享 DB session 验证，拆分为 repository/service/facade 三层）
- [x] 单元测试 11 个全部通过（config 2 + facade 3 + service 4 + main 2）

### 认证系统状态

**设计文档**：

- `docs/technical/develop/202603/260308-auth-system-design.md` - 认证系统总体设计
- `docs/technical/develop/202603/260311-reverse-proxy-setup.md` - 反向代理实现（新）

| 模块 | 状态 | 说明 |
|------|------|------|
| Cookie 提取 (`facade/deps.py`) | ✅ 已实现 | `get_session_token` 从 `better-auth.session_token` 读取 |
| 必须认证 (`facade/deps.py`) | ✅ 已实现 | `get_current_user` — 无效 token 抛 401 |
| 可选认证 (`facade/deps.py`) | ✅ 已实现 | `get_optional_user` — 无效 token 返回 None |
| Session 查询 (`repository/auth.py`) | ✅ 已实现 | JOIN session + user 表，检查 expiresAt |
| 业务逻辑 (`service/auth.py`) | ✅ 已实现 | `authenticate()`, `revoke_session()` |
| 跨层 DTO (`util/schema.py`) | ✅ 已实现 | `UserInfo` dataclass |
| 反向代理 Cookie 传递 | ✅ 已实现 | Next.js rewrites `/api/py/v1/*` → `http://localhost:8000/api/v1/*` |
| 集成测试（真实 DB） | ✅ 已完成 | 13 passed; Cookie提取、依赖注入、异常流程验证 |
| 微信登录 | ⬜ 待实现 | Generic OAuth Plugin 方案已设计 |

> **注意**：设计文档 2.4 节中引用的文件路径 `common/auth.py` 和 `common/database.py` 已过时，实际代码已按分层架构重新组织。

### 未完成

- [ ] 前后端业务链路调通（Next.js BFF → Python API → LLM → DB → Frontend 展示）
- [ ] Roundtable 域 API routes + UI
- [ ] Deliverable 域全部
- [ ] Identity 域全部
- [ ] 微信登录集成
- [ ] 种子数据
- [ ] OpenRouter API Key 配置

---

## CI/CD Pipeline 状态

**全部 4 个 Job 稳定通过**

| Job | 内容 | 状态 |
|-----|------|------|
| test-frontend | pnpm lint + typecheck + test (Node 20, Turborepo) | ✅ |
| test-java-backend | mvn clean test + package | ✅ |
| test-python-backend | ruff lint + mypy + pytest unit (uv) | ✅ |
| security-scan | Trivy fs scan → SARIF → GitHub Security tab | ✅ |

---

## 本地环境

### 中间件

| 中间件 | 方案 | 启动方式 |
|--------|------|---------|
| PostgreSQL 16 | Homebrew | `brew services start postgresql@16` |
| Redis 8 | Homebrew | `brew services start redis` |
| AI Provider | OpenRouter | 需在 `.env.development` 配置 API Key |
| Frontend | pnpm + Turbopack | `pnpm dev --filter @wenexus/web` → localhost:3000 |
| Python Backend | uvicorn | `uv run uvicorn src.main:app --reload` → localhost:8000 |

### 数据库

- Host: localhost:5432 / Database: wenexus_dev
- User: wenexus / Password: wenexus_dev_pwd
- 25 张表已同步

### 快速启动

```bash
# 1. 中间件
brew services start postgresql@16 && brew services start redis

# 2. Python 后端
cd backend/python && uv run uvicorn wenexus.main:app --reload --port 8000

# 3. 前端（新终端）
cd frontend && pnpm dev --filter @wenexus/web
```

---

## 架构概览

```
Frontend (Next.js :3000)          Python Backend (FastAPI :8000)
  ├── UI 渲染                       ├── facade/ (HTTP 路由 + 认证依赖)
  ├── Auth (Better Auth)            ├── app/ (编排层, 待实现)
  ├── Discovery CRUD (直接 DB)      ├── service/ (认证业务逻辑)
  ├── Identity CRUD (直接 DB)       ├── repository/ (DB 连接 + 认证查询)
  └── BFF → Python (AI 相关)       └── util/ (UserInfo DTO)

                    PostgreSQL (Homebrew :5432)
                    Redis (Homebrew :6379)
```
