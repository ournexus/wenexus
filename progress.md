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
- [x] Discovery 域 Python API 实现（facade: 2 endpoint, service: get_public_topics）
- [x] Discovery 域集成测试 14 个全部通过（API 端点、分页、数据格式、完整性检查）
- [x] 业务流程集成文档完成（260312-business-flow-integration.md）
- [x] 前后端业务流程调通（Python API → DB 完整链路，Discovery 域端到端验证）
- [x] **Roundtable 消息发送功能**（混合模式）
  - [x] Repository 层：save_message, get_session_context, get_session_experts, update_session_status
  - [x] Service 层：send_message (混合模式),_generate_and_save_expert_response
  - [x] Util 层：LLM 集成 (OpenRouter API)
  - [x] Facade 层：POST /sessions/{id}/messages 端点
  - [x] 集成测试 2 个全部通过
  - [x] 技术文档已完成
- [x] **Python 后端分层架构深度优化**（PR #31）✨ NEW
  - [x] SQL 查询全部移至 repository 层（之前混在 service 中）
  - [x] App 编排层实现（分页、认证检查、session 创建）
  - [x] Facade 层规范化（直接调用 app，不穿过 service）
  - [x] 去重认证检查（consolidate 到 app 层）
  - [x] 移除死代码（get_session_for_user）
- [x] **Cloudflare Workers 部署方案**（PR #31）
  - [x] 环境变量 Proxy 延迟加载（解决 Workers 无法在静态初始化时读取 secrets）
  - [x] 移除 next/font/google（不兼容 Workers 运行时）
  - [x] 修复 esbuild keepNames 错误（`__name is not defined`）
- [x] **BMAD 规划文档**（PR #31）
  - [x] 产品需求文档 (PRD) 完整版（用户旅程、领域模型、NFR）
  - [x] 技术架构设计（分层决策、关键组件）
  - [x] 用户故事与 Epics（完整的工作分解）
  - [x] UX 设计规范（交互流、界面原型）
  - [x] 实现就绪报告（220326 版本）
- [x] **初始数据库 Schema**（PR #31）
  - [x] Drizzle 迁移完整实现（0000_rapid_the_watchers）
  - [x] 核心领域表（topics, roundtable_sessions, experts, messages, observation_cards, deliverables）
  - [x] 认证表（better-auth 兼容）
  - [x] Migration 元数据与 journal
- [x] **E2E 测试基础设施**（PR #31）
  - [x] Playwright signup 完整流程测试
  - [x] 测试环境配置（.env.test）
  - [x] PR 意见处理 Claude 命令
- [x] **安全加固**（PR #31）
  - [x] .wrangler 和 .dev.vars 加入 .gitignore

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

- [ ] 前端集成 Roundtable 消息发送 UI（调用 POST /sessions/{id}/messages）
- [ ] WebSocket 实时消息推送（替代轮询）
- [ ] Roundtable 域其他 API routes（edit session, delete message, etc.）
- [ ] Deliverable 域全部
- [ ] Identity 域全部
- [ ] 微信登录集成
- [ ] 种子数据
- [ ] OpenRouter API Key 配置（从环境变量读取）
- [ ] Discovery ExpertCount 计算与 Roundtable 域集成

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
