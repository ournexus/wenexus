---
project_name: 'wenexus'
user_name: 'xiaohui'
date: '2026-03-14'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 47
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Frontend (Monorepo: pnpm 9.0.0 + Turborepo 2.8.10)

- **Next.js** 15.5.7 (App Router, Turbopack, standalone output for non-Vercel)
- **React** 19.2.1 (Server Components 默认), TypeScript ^5 (strict mode)
- **TailwindCSS** 4.x + prettier-plugin-tailwindcss (class 自动排序)
- **Drizzle ORM** 0.44.2 (仅 PostgreSQL)
- **better-auth** 1.3.7 (Cookie-based session: `better-auth.session_token`)
- **next-intl** 4.3.4 (locale-based routing: /en/_, /zh/_)
- **react-hook-form** + Zod 4.1.5 (表单验证)
- **Radix UI** 20+ 原子组件 + Framer Motion 12.23.12
- **AI SDK**: @ai-sdk/react, LangChain, LangGraph
- **部署**: @opennextjs/cloudflare + wrangler (无 Node.js 原生模块)

### 前后端通信

- Next.js rewrites: `/api/py/v1/*` → Python 后端 (反向代理, 不直接调用后端地址)
- WebSocket: 独立连接管理, ConnectionManager 广播模式

### Backend Python (FastAPI)

- **FastAPI** 0.104.0+, **Pydantic** 2.5+, **SQLAlchemy** 2.0 (async)
- **asyncpg** 0.29.0, **structlog** (结构化日志)
- **LangChain/LangGraph** + OpenRouter API (LLM 集成)
- **代码质量**: ruff (lint+format), mypy (类型检查), pytest (asyncio_mode=auto)
- **测试标记**: @pytest.mark.unit, @pytest.mark.integration

### Backend Java (⚠️ 暂未启用, 模块已注释)

- Spring Boot 3.1.5, Java 17 — 不要修改或启动

### Infrastructure

- **数据库**: PostgreSQL 16 (唯一数据库), Redis 7 (缓存)
- **CI/CD**: GitHub Actions (Node 20, Java 17, Python 3.14)
- **E2E**: Playwright 1.52.0 (CI 中配合 PostgreSQL 服务容器)
- **安全**: Trivy 扫描, conventional commits 强制

### 关键约束

- Cloudflare Workers: 不支持 Node.js 原生模块 (shiki/prettier/yaml/acorn 已 stub)
- next.config 中间件栈顺序: withMDX → withNextIntl → withBundleAnalyzer (不可更改)
- pageExtensions 包含 md/mdx, 这些后缀的文件会被当作页面
- 禁止 mock 测试 — 优先集成测试和 E2E

## Critical Implementation Rules

### Language-Specific Rules

#### 前后端字段命名

- 数据库: snake_case, API/前端: camelCase
- ⚠️ 当前 Python 层是手动转换 (技术债), 新代码应使用 Pydantic alias_generator 自动化
- Drizzle schema: camelCase 字段 + `text('snake_case')` 自动映射

#### TypeScript

- `strict: true`, 不允许 `any`
- Server Components 默认, 交互组件加 `'use client'`
- Import 排序由 prettier-plugin 自动处理, 不需手动管理
- 路径别名: `@/*` → src/, `@wenexus/*` → packages

#### Python

- 全异步: `async def` + `AsyncSession`, 无同步 DB 操作
- `disallow_untyped_defs: true`: 每个函数必须有完整类型标注
- `str | None` 不用 `Optional`, `@dataclass` 做 DTO, `BaseModel` 做请求体
- 日志: `await logger.ainfo("event", key=value)`, 禁止 print
- SQL: 参数化 `text()` 查询, `asyncio.gather` 并发
- API 响应: `{"code": 0, "data": {...}}`

### Framework-Specific Rules

#### Next.js App Router

- 路由分组: `(auth)`, `(admin)`, `(chat)`, `(roundtable)` — 按功能域隔离布局
- 国际化: 所有页面在 `[locale]/` 下, next-intl 处理路由和翻译
- API Routes: `app/api/domains/{domain}/` 按领域组织, 作为 Python 后端的代理层
- 中间件 (`middleware.ts`): 检查 session 保护 admin/settings 等路由

#### React 组件

- Radix UI 原子组件 + compound 模式 (如 PromptInput + PromptInputButton)
- 状态管理: React Context (如 ChatContext), 无全局状态库
- 表单: react-hook-form + Zod schema 验证

#### FastAPI 后端分层 (严格执行, 禁止反向依赖)

| 层 | 能做 | 不能做 |
|---|---|---|
| **facade** | HTTP 解析、参数校验、调用 app/service | 写 SQL、业务判断 |
| **app** | 编排多个 service 调用 | 直接操作 DB |
| **service** | 业务逻辑、调用 repository | 接触 Request/Response 对象 |
| **repository** | SQL 查询、数据持久化 | 业务逻辑判断 |

- **util/**: 跨层共享 (schema、websocket 等), 不含业务逻辑
- **DI**: `Depends(get_db)`, `Depends(get_current_user)` 用于 DB 和认证
- **WebSocket**: `ws_manager` 是全局单例, 直接 import 使用, 不通过 `Depends()` 注入
- **启动**: `@asynccontextmanager lifespan` 管理生命周期, 启动时验证 DB 连接

### Testing Rules

- **禁止 mock 测试**: 不用 `unittest.mock`、`jest.mock`, 优先真实集成测试
- **前端 E2E**: Playwright, 测试放在独立包 `frontend/packages/e2e/`, 不与应用代码混合
- **Python 测试标记**: `@pytest.mark.unit` (无外部依赖) / `@pytest.mark.integration` (需 DB/Redis)
- **Python asyncio**: `asyncio_mode=auto`, 测试函数自动 async, 不需 `@pytest.mark.asyncio`
- **CI 环境**: E2E 配合 PostgreSQL 16 服务容器, 超时: 导航 30s, 操作 15s
- **测试策略分层**: 关键路径用 Playwright 代码测试, 探索性测试用自然语言用例 (`e2e/cases/*.yaml`)

### Code Quality & Style Rules

- **函数长度**: 单个函数不超过 30 行
- **命名自解释**: 函数名、变量名要自解释, 减少注释需求
- **拒绝硬编码**: 使用常量、枚举或配置文件
- **拒绝过度设计**: 只解决当前问题, 不预设未来需求
- **前端格式化**: Prettier (semi, singleQuote, tabWidth=2, printWidth=80)
- **Python 格式化**: `ruff format .` (line-length=88) + `ruff check --fix .`
- **Pre-commit hooks**: trailing whitespace, YAML/JSON/TOML 验证, markdownlint, conventional commits
- **模块文档**: 新模块必须有顶部 JSDoc (TS) 或 docstring (Python), 声明用途和依赖关系

### Development Workflow Rules

- **Conventional Commits**: feat/fix/docs/style/refactor/perf/test/ci/chore/build/revert (pre-commit 强制)
- **技术文档**: 每个有意义的 commit 对应一份 `docs/technical/YYMMDD-描述.md`
- **文档权限**: `docs/theory/`, `docs/prd/`, `docs/design/` 对 AI 只读, `docs/technical/` 受控写入
- **分支**: feature 分支开发, PR 合并到 main
- **部署**: main → 生产 (Cloudflare Workers), develop → staging
- **代码提交前检查**: pre-commit hooks 自动运行 (格式化、lint、commit message 校验)

### Critical Don't-Miss Rules

#### 代理必须避免的反模式

- 不要在前端硬编码 Python 后端地址, 必须通过 `/api/py/v1/*` 反向代理
- 不要在 `app/` 目录下创建 `.md`/`.mdx` 文件, 会被当作页面路由
- 不要修改 Java 后端代码, 模块已注释未启用
- 不要在 service 层 import FastAPI 的 Request/Response
- 不要在 repository 层写业务判断逻辑
- 不要通过 `Depends()` 注入 `ws_manager`, 直接 import
- 前端数据库操作必须用 `db()`, 不要直接调 `getPostgresDb()`

#### 认证模式

- `get_current_user`: 强制认证, 无有效 session 抛 401
- `get_optional_user`: 可选认证, 无 token 返回 None (token 无效仍抛 401)
- middleware.ts 只检查 cookie 是否存在, 不验证有效性, 真正权限校验在页面/API 层

#### 部署与环境

- Cloudflare 构建必须设置 `CF_BUILD=true`, 否则 bundle 过大部署失败
- better-auth 无 `DATABASE_URL` 时静默失败, 不报错
- 配置缓存 1 小时 (`unstable_cache`), 改配置后需 `revalidateTag` 或重启

#### 安全原则

- 只修复可被直接利用的重大漏洞 (SQL 注入、RCE)
- 不主动添加预防性安全加固, 开发阶段功能优先

#### AI 代理工作要求

- 写完代码必须自行启动验证, 不依赖用户做基本测试
- 修改代码前必须先读取文件
- 不确定时提问, 不基于假设实现

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-03-14
