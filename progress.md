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
│   ├── deps.py                 # 共享依赖：get_session_token, get_current_user, get_optional_user, raise_if_error
│   ├── roundtable.py           # Roundtable 路由（完整 CRUD + WebSocket）
│   └── deliverable.py          # Deliverable 路由 (501 stub)
├── app/                        # 编排层
│   ├── discovery.py            # Discovery 域用例
│   └── roundtable.py           # Roundtable 域用例
├── agent/                      # LangGraph AI Agent 模块（新）
│   ├── graph.py                # ReAct-style StateGraph（Roundtable Facilitator）
│   └── tools.py                # Agent 工具（日期、讨论格式化、专家推荐）
├── service/
│   ├── auth.py                 # authenticate(), revoke_session()
│   └── roundtable.py           # send_message (混合模式)
├── repository/
│   ├── db.py                   # engine, get_db, check_db_connection
│   ├── auth.py                 # query_user_by_token(), delete_session()
│   ├── discovery.py            # find_public_topics (含 expertCount)
│   └── roundtable.py           # session/message CRUD
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
- [x] **E2E 测试可靠性优化**（PR #38, #39）✨ DONE
  - [x] 增加测试超时到 120s（远程 DB 兼容）
  - [x] 提取魔法数字为命名常量（E2E_TEST_TIMEOUT）
  - [x] 优化 load strategy（networkidle → domcontentloaded）
  - [x] 改进 API 调用方式（page.request → browser-side fetch）
  - [x] 修复并发限流重试机制（6 次重试 + 随机延迟）
- [x] **CI/CD 架构优化**（PR #38, #39）✨ DONE
  - [x] 创建独立 test-e2e job（带 postgres 服务）
  - [x] Playwright webServer 自动启动 Next.js（仅 CI）
  - [x] 单元测试与 E2E 分离（减少 CI 时间）
  - [x] 部署 job 依赖正确配置
- [x] **OpenRouter API Key 配置** ✨ NEW
  - [x] 后端已通过 Pydantic Settings 读取
  - [x] 前端 .env.example 补充文档说明
- [x] **种子数据扩展** ✨ NEW
  - [x] 4 个内置专家 (求真者、经济学者、技术专家、伦理学者)
  - [x] 3 个示例话题
  - [x] 讨论会话自动创建
- [x] **Discovery ExpertCount 计算** ✨ NEW
  - [x] SQL 查询：统计每个 topic 的参与 experts
  - [x] 使用 jsonb_array_elements 提取 expert_ids
  - [x] 前端 TopicCard 已支持显示
- [x] **Roundtable 消息发送 UI**（已实现）
  - [x] message-input.tsx 完整表单
  - [x] 前端 API 路由集成
  - [x] WebSocket + 轮询实时更新
- [x] **部署架构完善** ✨ NEW
  - [x] Cloudflare Workers 部署（前端 Next.js via OpenNext）
  - [x] Cloudflare Tunnel 后端固定域名 `https://api.aispeeds.me`
  - [x] Supabase PostgreSQL 生产数据库
  - [x] CI/CD deploy-staging（develop 分支）和 deploy-production（main 分支）
  - [x] Wrangler secrets 注入（AUTH_SECRET, DATABASE_URL, PYTHON_BACKEND_URL）
  - [x] `dev.sh` 一键启动脚本（数据库 + 后端 + Tunnel + 前端 Workers 预览）
  - [x] CLAUDE.md 同步更新（部署架构、开发命令、环境变量文档）
- [x] **邮箱验证修复**（已合并到 main）
  - [x] Auth Secret 改为动态读取（兼容 Cloudflare Workers 运行时）
  - [x] Resend 邮件服务配置（RESEND_API_KEY + RESEND_SENDER_EMAIL）
- [x] **LangGraph Agent 集成到 Roundtable 流程** ✨ NEW
  - [x] `invoke_facilitator()` — 接受会话上下文，调用 LangGraph graph 生成 Facilitator 合成
  - [x] `send_message()` autopilot 模式：专家回复后自动追加 Facilitator 合成消息（role=host）
  - [x] WebSocket 广播 `facilitator_message` 事件
  - [x] 响应体新增 `facilitatorMessage` 字段
- [x] **Roundtable 域补充 API routes** ✨ NEW
  - [x] PATCH `/sessions/{id}` — 更新会话设置（mode, is_private）
  - [x] POST `/sessions/{id}/end` — 结束讨论会话（status → completed）
  - [x] DELETE `/sessions/{id}/messages/{mid}` — 软删除消息（仅作者或会话所有者）
  - [x] Repository: `update_session_fields`, `find_message_by_id`, `soft_delete_message`
  - [x] App: 权限检查 + 状态冲突检测（409 已完成/已删除）
- [x] **Agent 代码质量优化** ✨ NEW
- [x] 解决 LangGraph/langchain mypy 类型检查不兼容（添加 `type: ignore`）
- [x] 修复 deps.py E402 导入顺序错误（PEP8 compliance）
- [x] **生产部署配置** ✨ NEW
- [x] Cloudflare Workers 生产域名配置更新
- [x] `.langgraph_api/` 目录加入 gitignore

### 当前分支与未提交变更

**分支**：`main`

**未提交的本地变更**（1 个文件）：

| 文件 | 变更内容 |
|------|---------|
| `frontend/apps/web/wrangler.toml` | Staging 环境的 worker domain 调整为 yihuimbin 子域 |

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
| 微信登录 | 📝 方案已完成 | 技术方案文档 `260329-wechat-login-integration.md` 已写，待实现 |

> **注意**：设计文档 2.4 节中引用的文件路径 `common/auth.py` 和 `common/database.py` 已过时，实际代码已按分层架构重新组织。

### 未完成

- [ ] WebSocket 实时消息推送优化（目前已有 WebSocket + 轮询降级）
- [ ] Deliverable 域全部（当前 facade stub 返回 501）
- [ ] Identity 域全部
- [ ] 微信登录集成（技术方案文档已完成：`260329-wechat-login-integration.md`）

---

## CI/CD Pipeline 状态

**全部 5 个 Job 稳定通过**

| Job | 内容 | 状态 |
|-----|------|------|
| test-frontend | pnpm lint + typecheck + test (Node 20, Turborepo) | ✅ |
| test-e2e | Playwright E2E tests with auto-started Next.js | ✅ |
| test-java-backend | mvn clean test + package | ✅ |
| test-python-backend | ruff lint + mypy + pytest unit (uv) | ✅ |
| security-scan | Trivy fs scan → SARIF → GitHub Security tab | ✅ |

---

## 本地环境

### 中间件

| 中间件 | 方案 | 启动方式 |
|--------|------|---------|
| PostgreSQL 16 | Supabase（生产）/ Homebrew（本地） | 生产云托管；本地 `brew services start postgresql@16` |
| Redis | Upstash（生产）/ Homebrew（本地） | 生产云托管；本地 `brew services start redis` |
| AI Provider | OpenRouter | `.env.development` 配置 API Key |
| Frontend | Cloudflare Workers / pnpm | 生产 Workers；本地 `pnpm cf:preview` → localhost:8787 |
| Python Backend | FastAPI + Cloudflare Tunnel | 生产 `https://api.aispeeds.me`；本地 `:8000` |

### 数据库

- Host: localhost:5432 / Database: wenexus_dev
- User: wenexus / Password: wenexus_dev_pwd
- 25 张表已同步

### 快速启动

```bash
# 推荐：一键启动
./scripts/dev.sh           # 全栈：数据库 + 后端(--reload) + Tunnel + 前端 Workers 预览
./scripts/dev.sh frontend  # 仅前端 Workers 预览（http://localhost:8787）
./scripts/dev.sh stop      # 停止所有

# 或手动启动
# 1. 中间件
brew services start postgresql@16 && brew services start redis

# 2. Python 后端
cd backend/python && uv run uvicorn src.wenexus.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 前端（新终端）
cd frontend/apps/web && pnpm cf:preview
```

---

## 架构概览

```
用户 → Cloudflare Workers（Next.js via OpenNext :8787 本地/:443 生产）
           │  PYTHON_BACKEND_URL
           ▼
     Cloudflare Tunnel → FastAPI :8000
          ├── facade/           HTTP 路由 + raise_if_error
          ├── app/              编排层（Discovery, Roundtable）
          ├── agent/            LangGraph AI Agent（Facilitator）
          ├── service/          业务逻辑（auth, roundtable）
          ├── repository/       DB 查询（auth, discovery, roundtable）
          └── config/           Pydantic Settings

          Supabase PostgreSQL（生产）/ localhost:5432（开发）
          Upstash Redis（生产）/ localhost:6379（开发）
```
