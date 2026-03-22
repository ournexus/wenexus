---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - docs/bmad/planning-artifacts/prd.md
  - docs/bmad/planning-artifacts/product-brief-wenexus-2026-03-14.md
  - docs/bmad/planning-artifacts/ux-design-specification.md
  - docs/bmad/project-context.md
  - docs/bmad/planning-artifacts/implementation-readiness-report-2026-03-15.md
  - docs/prd/domain-architecture.md
  - docs/prd/aigc-architecture-vision.md
  - docs/prd/user-story-v4.md
  - docs/design/personas/user-personas.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-03-21'
project_name: 'wenexus'
user_name: 'xiaohui'
date: '2026-03-20'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**功能需求（48 条 FR）按架构影响域分类：**

| 能力域 | FR 编号 | 架构影响 |
|--------|---------|----------|
| 话题与内容生产 | FR1-FR7 | 话题数据模型、内容生命周期状态机、批量/增量双模式生产管线、话题关联图谱 |
| 圆桌讨论引擎 | FR8-FR15 | **核心引擎**——Autopilot/Interactive 双模式统一架构、求真者事实打底、多专家线程辩论编排、发言排队与打断机制、实时流式渲染、会话持久化与恢复 |
| 观点卡片消费 | FR16-FR23 | AIGC JSX 渲染（提示词 + 预定义组件约束）、移动端优先信息流、SSR/SEO、分享水印、生命阶段分类浏览 |
| 内容搜索与发现 | FR24-FR27 | 自然语言搜索引擎、多轮对话式搜索状态管理、搜索→圆桌无缝跳转、首页推荐 |
| 产出物生成 | FR28-FR29 | 多格式产出物模板、圆桌讨论→产出物的内容蒸馏管线 |
| 外部分发与导流 | FR30-FR35 | **独立分发子系统**——任务调度引擎、多平台适配层（Plugin 架构）、监控面板、异常告警、分发策略配置 |
| 用户管理与付费 | FR36-FR41 | 认证系统（better-auth）、免费/付费权限分层、积分制经济模型 |
| 质量保障与运维 | FR42-FR48 | Verify Agent 自动验证管线、异常通知与人工介入工作流、LLM 供应商抽象层（含容错）、行为数据采集 |

**FR 优先级与架构决策的关系（⚠️ PRD 中 FR 未按 P0-P3 标注）：**

根据 PRD 的 MVP Scope 描述，FR 的隐含优先级为：

- **P0 圆桌引擎**（FR8-FR15）：需要最健壮的架构支持，是核心竞争力
- **P1 观点卡片**（FR16-FR23）：用户触达层，SSR 性能和移动端体验是关键
- **P2 外部分发**（FR30-FR35）：独立子系统，可渐进实现
- **P3 付费系统**（FR36-FR41）：基础功能，初期架构可轻量

架构决策应优先保障 P0/P1 的技术方案完整性。

**非功能需求（17 条 NFR）架构驱动分析：**

| NFR 分类 | 关键指标 | 架构影响 |
|----------|----------|----------|
| 性能（NFR1-6） | 首屏 < 2s、首 token < 2s、60fps 滚动 | SSR + 边缘部署、OpenRouter 流式调用、虚拟列表 + 图片懒加载 |
| 可靠性（NFR7-10） | 可用性 > 99.5%、断点续传、自动重连 | 内容管线幂等设计、WebSocket 重连 + polling 降级、分发任务失败重试 |
| 可扩展性（NFR11-14） | 100 话题/天、50→10000+ 无退化、热切换 LLM | 批量管线并行化、数据库索引 + 分页策略、LLM Provider 注册表模式 |
| 集成（NFR15-17） | OpenRouter 降级、平台适配、支付安全 | LLM 容错链（fallback chain + circuit breaker + rate limit）、分发平台 Plugin 架构、HTTPS + 支付令牌化 |

**UX 设计规范对架构的影响：**

| UX 规范要求 | 架构影响 |
|-------------|----------|
| 双层卡片形态（钩子卡片 + 展开卡片） | AIGC 生成需通过提示词和预定义组件来区分两种形态，非模板系统 |
| 圆桌讨论线程式 UI + 挂机/主持模式切换 | 需要前端状态机管理模式切换 + 后端会话状态持久化 |
| 多 AI 专家同时发言的时序编排 | 需要后端发言排队机制 + 打断协议，防止认知过载 |
| 对话式搜索 UI（多轮追问） | 搜索状态管理需支持对话上下文链 |
| Mobile-first + 4 个断点 | 移动端 WebSocket 连接更不稳定，需更积极的重连策略和 polling 降级 |
| WCAG AA 无障碍 | 组件库需支持 aria 属性、键盘导航、屏幕阅读器 |
| 实时流式文本渲染 | SSE + OpenRouter streaming 的前端渐进式渲染组件 |

### Scale & Complexity Assessment

**复杂度等级：中高（Medium-High）**

| 维度 | 评估 | 说明 |
|------|------|------|
| 实时特性 | 高 | WebSocket（圆桌通信）+ SSE（AI 流式）+ OpenRouter streaming，三通道协调 |
| 多 Agent 编排 | 高 | Autopilot/Interactive 双模式引擎、求真者 + 多专家辩论、Verify Agent 验证管线 |
| 内容生产管线 | 中高 | 批量 Autopilot → Verify → 发布，断点续传，双模式数据一致性 |
| AIGC 渲染 | 中高 | AI 生成 JSX 的安全渲染（提示词约束 + 预定义组件 + 沙箱），成功率 > 95% |
| 外部集成 | 中 | OpenRouter LLM 供应商、小红书等外部平台分发、支付系统 |
| 用户交互 | 中高 | 信息流滑动、圆桌讨论多模式、对话式搜索、产出物生成 |
| 数据复杂度 | 中 | 话题关联图谱、多版本内容、用户行为埋点、讨论历史 |
| 多租户 | 低 | 单平台，无多租户需求 |
| 合规要求 | 低 | 短期不设内容安全红线，无强合规 |

**主要技术领域**：全栈 Web 应用（Next.js + FastAPI），AI 密集型

**预估架构组件数**：~25-30 个（4 域 + 共享内核 + 基础设施层）

### Technical Constraints & Dependencies

**Brownfield 资产（已有系统）：**

| 资产 | 状态 | 架构影响 |
|------|------|----------|
| Next.js 15 App Router + React 19 | 生产就绪 | Server Components 默认，路由分组按功能域隔离 |
| FastAPI 分层架构（facade→app→service→repository） | 生产就绪 | 严格分层，禁止反向依赖，全异步 |
| better-auth Cookie-based session | 已集成 | 认证模式已确定（强制/可选两种） |
| WebSocket ConnectionManager + auto-reconnect | 已实现 | 圆桌实时通信基础已有，需扩展发言排队 |
| SSE AI SDK streamText() + useChat() | 已实现 | AI 流式输出基础已有，待补 OpenRouter streaming |
| next-intl 4.3.4 locale routing | 已集成 | MVP 仅中文，但架构面向全球 |
| Drizzle ORM + PostgreSQL 16 | 已集成 | 数据模型扩展基础已有 |
| LLM 抽象层 util/llm.py | 基础可用 | 需扩展：容错链（fallback + circuit breaker）、模块级模型配置 |
| 前端路由分组 (auth)(admin)(chat)(roundtable) | 已定义 | 需与 4 域边界对齐 |

**关键技术约束：**

| 约束 | 说明 |
|------|------|
| next.config 中间件栈顺序 | withMDX → withNextIntl → withBundleAnalyzer，不可更改 |
| FastAPI 分层规则 | facade→app→service→repository，严格单向依赖 |
| 前后端通信 | Next.js rewrites `/api/py/v1/*` → Python 后端，禁止前端硬编码后端地址 |
| TypeScript strict mode | 不允许 `any`，Server Components 默认 |
| Python 全异步 | `async def` + `AsyncSession`，无同步 DB 操作 |
| 禁止 mock 测试 | 优先集成测试和 E2E 测试 |

### Cross-Cutting Concerns

| 关注点 | 涉及域 | 架构策略 |
|--------|--------|----------|
| **LLM 供应商抽象** | 全域 | 共享内核 LLM Gateway，OpenRouter 统一接口 + 容错链（fallback chain + circuit breaker + rate limit handling），支持模块级模型配置和热切换 |
| **实时通信** | 圆桌域、发现域 | 三通道协调：WebSocket（圆桌双向通信）+ SSE（AI 流式输出）+ OpenRouter streaming；移动端需更积极的重连策略 |
| **内容生命周期** | 圆桌域、交付域、发现域 | 状态机：生成中 → 验证中 → 通过 → 异常 → 重新生成；贯穿内容生产管线 |
| **认证与权限** | 全域 | better-auth cookie session + 免费/付费分层权限 |
| **国际化** | 全域 | next-intl locale routing，MVP 中文，架构面向全球 |
| **行为数据采集** | 全域 | 统一埋点事件模型（浏览、点击、停留、分享、转化） |
| **SEO** | 发现域 | SSR/SSG + JSON-LD 结构化数据，Server Components 天然支持 |

### Key Data Flow Paths

**路径 1：内容生产流（Autopilot → 用户消费）**

```
话题种子 → 圆桌引擎(Autopilot模式) → 多专家结构化讨论产出
    → Verify Agent 自动质量验证
        → [通过] → 内容蒸馏 → 观点卡片(钩子+展开) → Discovery 信息流 + 分发队列
        → [异常] → 通知管理员 → 人工介入(重新生成/编辑/放弃)
```

**路径 2：用户交互流（Interactive → 产出物）**

```
用户浏览卡片(Discovery) → 进入圆桌(Roundtable)
    → 挂机围观(被动观看AI讨论，含发言排队编排)
    → 接管主持(输入问题引导讨论方向)
    → 生成产出物(Deliverable) → 下载/分享
```

**路径 3：分发回流（外部平台 → WeNexus）**

```
通过验证的观点卡片 → 分发调度引擎(定时触发)
    → 平台适配层(小红书等) → 自动发布(图片+文案+导流链接)
    → 用户点击导流链接 → WeNexus 着陆页
    → 监控面板(发布状态/曝光量/导流量/异常)
```

### Core Architecture Challenges

**挑战 1：圆桌引擎 Autopilot/Interactive 双模式统一架构**

同一个引擎的两种运行模式：Autopilot 模式（无用户输入，自动产出结构化多视角内容）和 Interactive 模式（用户可挂机围观或接管主持）。需要统一的对话编排层、专家调度策略和状态机设计，同时支持模式间的无缝切换（FR13）。多位 AI 专家同时发言时需要发言排队机制和打断协议（UX 驱动约束），防止用户认知过载。

**挑战 2：AIGC JSX 渲染安全与质量**

AI 生成 JSX 直接渲染为用户可见的观点卡片（FR18），需要同时解决安全性（XSS 防护、沙箱隔离）和质量问题（渲染成功率 > 95%，NFR4）。两种卡片形态（钩子卡片 vs 展开卡片）需要通过精心设计的提示词和预定义组件库来约束 AI 输出，充分发挥 AI 的生成能力而非限制在固定模板内。跨现代浏览器兼容也需要在组件层面保障。

**挑战 3：实时三通道协调（WebSocket + SSE + OpenRouter streaming）**

圆桌讨论涉及三种实时通道的协调：WebSocket 用于圆桌双向通信（已有 ConnectionManager），SSE 用于 AI 流式输出（已有 streamText），OpenRouter streaming 用于 LLM 调用的流式响应（待实现）。需要统一的连接管理、错误恢复和降级策略（NFR10）。移动端场景下网络更不稳定，需要更积极的自动重连和 polling 降级策略。

**挑战 4：内容生产管线与双模式数据一致性**

Autopilot 批量生产（异步管线：Content Agent → Verify Agent → 发布队列）和 Interactive 实时交互（同步管线：用户输入 → AI 响应 → 持久化）两条数据路径最终都写入同一个话题库。需要设计一致性策略确保：批量生产不覆盖用户交互数据、并发写入不产生冲突、内容版本可追溯。管线还需支持断点续传（NFR8），单个话题失败不阻塞批量任务。

**挑战 5：域边界与 Next.js 路由对齐**

4 个业务域（发现、圆桌、交付、身份）+ 共享内核的边界需要同时映射到：Next.js App Router 路由分组（已有 (auth)(admin)(chat)(roundtable)）、FastAPI 分层结构（facade→app→service→repository）、前端组件组织。域间通过领域事件和防腐层接口通信，需确保前后端的域边界一致。

**挑战 6：分发子系统的可扩展性**

外部分发（FR30-35）不是简单的"发布到平台"，而是一个包含任务调度引擎、多平台适配层、监控面板、异常告警和策略配置的独立子系统。需要 Plugin 架构支持未来新增平台（NFR14），任务失败自动重试（NFR9），平台 API 变更后快速适配（NFR16）。

**挑战 7：LLM 供应商抽象层容错设计**

FR46-47 要求多 LLM 供应商切换和模块级模型配置，NFR13 要求热切换，NFR15 要求超时和限流降级。现有 `util/llm.py` 提供基础抽象，需扩展为完整的容错链：fallback chain（主→备模型自动切换）、circuit breaker（故障隔离）、rate limit handling（限流感知与排队）。

## Starter Template Evaluation

### Primary Technology Domain

全栈 Web 应用（Next.js + FastAPI），AI 密集型内容平台。

### Starter Assessment: Brownfield — 不适用

WeNexus 是 Brownfield 项目，技术栈已完整确定并投入使用，无需评估 Starter Template。以下记录已确定的技术决策作为架构基线。

### Established Technology Stack

**Language & Runtime:**

- 前端：TypeScript ^5（strict mode），React 19 Server Components 默认
- 后端：Python 3.11+（全异步，`async def` + `AsyncSession`），类型标注强制（`disallow_untyped_defs: true`）
- 数据库字段命名：DB snake_case，API/前端 camelCase

**Frontend Architecture:**

- Next.js 15 App Router + Turbopack（standalone output for non-Vercel）
- TailwindCSS 4.x + **shadcn/ui**（Radix UI + Tailwind 预组装，统一组件样式系统）+ Framer Motion 12.23.12
- react-hook-form + Zod 4.1.5（表单验证）
- next-intl 4.3.4（locale-based routing: /en/\*, /zh/\*）
- better-auth 1.3.7（Cookie-based session）
- Drizzle ORM 0.44.2（PostgreSQL 16）— 前端职责：用户认证和已有页面数据访问
- @ai-sdk/react（AI 流式交互渲染）
- 虚拟列表方案（@tanstack/virtual 或 react-virtuoso）— 信息流 10000+ 话题性能保障

**Backend Architecture:**

- FastAPI 0.104.0+（严格四层：facade → app → service → repository）
- Pydantic 2.5+（请求体验证），SQLAlchemy 2.0 async + asyncpg 0.29.0
- LangChain/LangGraph + OpenRouter API（LLM 集成 + **多 Agent 编排**）
- SQLAlchemy 为后端数据访问唯一 ORM — 后端职责：Agent 相关持久化、内容生产管线、圆桌讨论数据
- structlog（结构化日志），ruff（lint + format），mypy（类型检查）

**Infrastructure:**

- 部署：@opennextjs/cloudflare + wrangler（优先利用平台优势）
- 数据库：PostgreSQL 16 + Redis 7
- CI/CD：GitHub Actions（Node 20, Java 17, Python 3.11）
- E2E：Playwright 1.52.0
- 安全：Trivy 扫描，conventional commits 强制
- Monorepo：pnpm 9.0.0 + Turborepo 2.8.10

**Monorepo Apps 状态：**

| App | MVP 状态 | 说明 |
|-----|----------|------|
| apps/web | ✅ 核心 | 主 Web 应用，用户端内容消费和圆桌讨论 |
| apps/admin | ✅ 必需 | 管理后台，内容生产调度 + 分发链路管理 |
| apps/mobile | 📦 预留 | React Native，MVP 阶段空壳 |

### Architectural Decisions Record (Starter Phase)

**ADR-S1: 圆桌多 Agent 编排在后端**

- 决策：圆桌讨论的多 Agent 编排（专家调度、发言排队、Autopilot/Interactive 模式切换）全部在后端 FastAPI + LangGraph 完成，前端只负责渲染和用户输入
- 理由：后端编排可控制发言顺序、执行 Verify Agent 验证、管理长上下文，前端无需感知 Agent 内部状态

**ADR-S2: LangGraph 统一编排在线 + 离线链路**

- 决策：LangGraph 同时驱动在线链路（Interactive 圆桌讨论）和离线链路（Autopilot 内容生产）；Verify Agent 是离线链路中的一个验证节点
- 理由：同一个引擎的两种模式，统一编排避免代码分裂

**ADR-S3: shadcn/ui 作为统一组件样式系统**

- 决策：采用 shadcn/ui（Radix UI + Tailwind 预组装）作为前端统一组件样式规范
- 理由：统一视觉规范、减少手动样式维护、提供 AIGC JSX 生成的组件白名单基础

**ADR-S4: shadcn/ui 组件清单作为 AIGC JSX 预定义组件约束**

- 决策：AI 生成 JSX 卡片时，提示词中约束只使用已注册的 shadcn/ui 组件（如 Card, Badge, Separator 等），配合预定义样式约束
- 理由：既是安全白名单（防止注入未知组件），也是视觉一致性保障（AI 输出天然适配设计系统）

**ADR-S5: 前后端数据库访问职责分离**

- 决策：前端 Drizzle ORM 负责用户认证和已有页面数据访问；后端 SQLAlchemy 负责所有 Agent 相关持久化（圆桌讨论、内容生产、分发管线）
- 理由：已有前端数据访问代码保留，Agent 相关的复杂数据操作统一在后端管理

**ADR-S6: React Context 为主，圆桌域预留复杂状态方案**

- 决策：全局状态管理使用 React Context；圆桌域如遇深嵌套 + 频繁更新性能问题，可局部引入 Zustand 或 useReducer + Context 组合
- 理由：轻量优先，按需升级

**ADR-S7: LLM Gateway 预留直连供应商通道**

- 决策：P0 阶段统一走 OpenRouter；LLM Gateway 抽象层设计时预留直连供应商的接口路径
- 理由：OpenRouter 是单点依赖，容错设计需要 Plan B

### Open Research Items

| 编号 | 待研究项 | 说明 | 优先级 |
|------|----------|------|--------|
| RI-1 | 三条通信链路部署路径 | REST（Next.js rewrite）、WebSocket、SSE 在 Cloudflare Workers / Vercel / Docker 部署下的实际路径和限制 | 🔴 高 — 影响实时通信架构方案 |

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- 前后端数据库职责分离与 Migration 策略
- 圆桌讨论通信协议（WebSocket 消息类型枚举 + LangGraph SDK 流式）
- 圆桌讨论页面双通道 vs 统一通道方案
- AIGC JSX 渲染策略（流式优先，无安全隔离）
- 通信协议 PoC/spike 作为实现第 0 步

**Important Decisions (Shape Architecture):**

- 权限模型（RBAC 三角色）
- 组件组织方式（域 > 功能分层）
- 任务调度架构（任务表驱动 + LLM rate limit 级别并发控制）
- 缓存分层策略
- 错误响应格式兼容策略

**Deferred Decisions (Post-MVP):**

- 图数据库引入（当前 PostgreSQL 关系表 + JSON 够用）
- APM 监控（按需引入）
- 自动化调度触发（短期手动）

### Data Architecture

| 决策 | 选择 | 理由 |
|------|------|------|
| Schema Migration | 各自管理：Drizzle Kit 管用户表，Alembic 管 Agent 表 | 前后端职责清晰，互不干扰 |
| 表命名防撞规则 | 前端表前缀 `auth_*` / `user_*`，后端表前缀 `agent_*` / `content_*` / `task_*` / `dist_*` | 共享同一 PostgreSQL，命名前缀约定防止 migration 冲突 |
| 缓存策略 | Next.js unstable_cache（页面级，1h TTL）+ Redis（热数据） | 分层缓存，已有基础设施 |
| 话题关联图谱 | PostgreSQL 关系表 + JSON 字段 | 不引入新依赖，MVP 阶段足够 |
| 前端数据访问 | Drizzle ORM — 用户认证和已有页面数据 | 保留已有代码 |
| 后端数据访问 | SQLAlchemy 2 async — Agent / 内容 / 讨论 / 分发 | 复杂数据操作统一后端 |

### Authentication & Security

| 决策 | 选择 | 理由 |
|------|------|------|
| 权限模型 | RBAC 三角色：free_user / premium_user / admin | better-auth session 扩展角色字段，简洁够用 |
| API 鉴权 | Session cookie 透传（Next.js rewrite 自动携带） | 最简方案，后端已有 get_current_user / get_optional_user |
| AIGC JSX 渲染 | 不做安全隔离，以最佳流式渲染效果为目标 | 通过提示词 + shadcn/ui 预定义组件约束质量，不牺牲渲染体验 |

### API & Communication Patterns

| 决策 | 选择 | 理由 |
|------|------|------|
| API 风格 | RESTful（沿用 `/api/py/v1/*` rewrite） | 已有基础，简单直接 |
| 错误处理 | 成功响应保持 `{"code": 0, "data": {...}}`；错误响应迁移到 RFC 9457 Problem Details `{"type", "title", "status", "detail"}` | 兼容已有成功格式，错误格式对齐业界标准 |
| 圆桌通信协议 | WebSocket JSON + 消息类型枚举（ExpertSpeak / ModeSwitch / ConsensusUpdate / UserInput / SystemNotice 等） | 结构化消息，前后端共享类型契约 |
| AI 流式输出 | 后端 LangGraph SDK 原生输出 → 前端 LangGraph 客户端 SDK 接收 | 跟随 SDK 标准，不自定义协议 |
| 圆桌讨论通道策略 | **待 PoC 确认**：优先方案 A（统一 WebSocket，LangGraph 流式输出通过后端转发为 WebSocket 消息）；备选方案 B（双通道：WebSocket 管状态，LangGraph SDK 管流式内容）| 需要 RI-1 研究结果 + LangGraph 前端 SDK 成熟度评估后最终确定 |

### Frontend Architecture

| 决策 | 选择 | 理由 |
|------|------|------|
| 路由分组 | 保持现有 `(auth)(admin)(chat)(roundtable)`，按需扩展 | 已有结构，不做大规模重组 |
| 组件组织 | 大层面按域（`domains/`），域内按 shadcn/ui 既有习惯 | 域边界清晰，组件存放符合社区惯例 |
| 组件扩展约定 | shadcn/ui 基础组件统一放 `components/ui/`；域特有的业务组件放 `domains/*/components/`；如需扩展 shadcn/ui 组件样式，在域内创建 wrapper 组件引用基础组件 | 基础组件不分裂，域扩展通过 wrapper |
| SC/CC 边界 | React 19 默认 — Server Components 优先，仅必要时 `'use client'` | 官方最佳实践 |

### Infrastructure & Deployment

| 决策 | 选择 | 理由 |
|------|------|------|
| 环境策略 | 双环境：main→production, develop→staging | 已有，足够 |
| 监控与日志 | structlog 结构化日志优先，APM 按需引入 | 1 人团队运维成本最小化 |
| 任务调度 | 任务表驱动（状态 + 并发数控制），短期手动触发，调用已有任务接口 | 轻量，不引入 Celery 等重依赖 |
| 任务调度并发控制 | 任务级并发控制 + LLM 调用级 rate limit awareness（联动 LLM Gateway 容错设计 ADR-S7） | 离线批量生产（>100 话题/天）需要感知 OpenRouter rate limit，避免被限流 |

### Decision Impact Analysis

**Implementation Sequence:**
0. **通信协议 PoC/spike** — 验证 WebSocket / SSE / LangGraph SDK 在目标部署环境下的可行性（⚠️ 阻塞后续圆桌引擎开发）

1. 数据架构（Migration 策略 + 表结构 + 命名前缀约定）→ 基础设施就绪
2. 认证 + 权限（RBAC 扩展）→ 用户分层可用
3. API + 通信协议（WebSocket 消息类型 + LangGraph SDK）→ 圆桌引擎可开发
4. 前端组件架构（域分组 + shadcn/ui）→ UI 开发可并行
5. 任务调度（任务表 + LLM rate limit 联动）→ 内容生产管线可运行

**Cross-Component Dependencies:**

- LangGraph SDK 选择同时影响 API 通信和 AI 流式输出
- RBAC 权限影响免费/付费功能门控
- WebSocket 消息类型枚举是圆桌域前后端的共享契约
- 任务表设计影响内容生产管线和分发子系统
- LLM rate limit awareness 联动 LLM Gateway 容错（ADR-S7）和任务调度并发控制

### Decision Change Triggers

| 触发条件 | 影响决策 | 备选方案 |
|----------|----------|----------|
| LangGraph 前端 JS/TS SDK 不成熟或流式支持不足 | AI 流式输出协议 | 退回 SSE 方案：后端 LangGraph → SSE → 前端 @ai-sdk/react |
| CF Workers 不支持 WebSocket 长连接或有严格限制 | 部署方案 + 通信协议 | 切换部署方案（Vercel / Docker 自部署） |
| OpenRouter rate limit 导致批量生产吞吐量不足 | LLM Gateway 策略 | 激活直连供应商通道（ADR-S7），多供应商并行调用 |
| 前后端 migration 出现冲突 | 数据库管理策略 | 切换为 PostgreSQL schema 隔离（public + backend） |
| React Context 在圆桌域出现性能瓶颈 | 状态管理方案 | 圆桌域局部引入 Zustand（ADR-S6） |

### Updated Open Research Items

| 编号 | 待研究项 | 说明 | 优先级 |
|------|----------|------|--------|
| RI-1 | 通信链路部署路径 + LangGraph 前端 SDK 评估 | REST / WebSocket / SSE / LangGraph SDK 在 CF Workers / Vercel / Docker 下的可行性；LangGraph JS/TS 客户端 SDK 的流式支持成熟度；圆桌讨论单通道 vs 双通道最终方案 | 🔴 高 — 实现第 0 步，阻塞圆桌引擎开发 |

## Implementation Patterns & Consistency Rules

> **文档优先级**：本架构文档的 patterns 覆盖 project-context.md 中的同名规则。两者冲突时，以本架构文档为准。project-context.md 中未被本文档覆盖的规则仍然有效。

### Pattern Categories Defined

**已有规则（project-context.md 已覆盖，不重复）：**

- TypeScript strict mode / Python 全异步 / 字段命名（DB snake_case, API camelCase）
- FastAPI 四层分层规则 / 组件模式 / 日志格式
- 代码风格（函数 ≤30 行、命名自解释、拒绝硬编码）
- 测试策略（禁止 mock、Playwright E2E）

**以下为新增的一致性规则，覆盖 project-context 未涉及的架构决策：**

### Naming Patterns

**Database Naming:**

| 规则 | 约定 | 示例 |
|------|------|------|
| 表名 | 复数、snake_case + 前缀约定 | `auth_users`, `agent_sessions`, `content_topics` |
| 前端管理的表 | 前缀 `auth_*`, `user_*` | `auth_users`, `auth_sessions`, `user_preferences` |
| 后端管理的表 | 前缀 `agent_*`, `content_*`, `task_*`, `dist_*` | `agent_experts`, `content_cards`, `task_jobs`, `dist_records` |
| 列名 | snake_case | `created_at`, `topic_id`, `is_premium` |
| 外键 | `{referenced_table_singular}_id` | `topic_id`, `user_id`, `session_id` |
| 索引 | `idx_{table}_{columns}` | `idx_content_topics_status`, `idx_auth_users_email` |
| JSON 字段 | snake_case 键名 | `{"topic_tags": [...], "meta_data": {...}}` |

**API Naming:**

| 规则 | 约定 | 示例 |
|------|------|------|
| REST 端点 | 复数名词、kebab-case | `/api/py/v1/topics`, `/api/py/v1/roundtable-sessions` |
| 路由参数 | camelCase | `/api/py/v1/topics/:topicId` |
| 查询参数 | camelCase | `?pageSize=20&sortBy=createdAt` |
| 版本化 | URL 路径前缀 | `/api/py/v1/`, `/api/py/v2/` |

**WebSocket Message Types:**

| 规则 | 约定 | 示例 |
|------|------|------|
| 消息类型枚举 | SCREAMING_SNAKE_CASE | `EXPERT_SPEAK`, `MODE_SWITCH`, `CONSENSUS_UPDATE` |
| 消息结构 | `{type, payload, timestamp, sessionId}` | `{"type": "EXPERT_SPEAK", "payload": {...}, "timestamp": "...", "sessionId": "..."}` |
| 前后端类型共享 | 前端 TypeScript type + 后端 Pydantic model，编译期对齐 | `WebSocketMessage` type ↔ `WebSocketMessage` Pydantic model |

**Code Naming（补充 project-context 未覆盖的）：**

| 规则 | 约定 | 示例 |
|------|------|------|
| 域目录 | kebab-case | `domains/discovery/`, `domains/roundtable/` |
| 组件文件 | PascalCase | `TopicCard.tsx`, `RoundtableSession.tsx` |
| Hook 文件 | camelCase with `use` 前缀 | `useRoundtable.ts`, `useTopicFeed.ts` |
| Service 文件 | camelCase with `Service` 后缀 | `topicService.ts`, `roundtableService.ts` |
| 类型文件 | 域内 `types.ts`，跨域 `shared/types.ts` | `domains/roundtable/types.ts` |
| 常量文件 | 域内 `constants.ts` | `domains/discovery/constants.ts` |
| Python 模块 | snake_case | `roundtable_service.py`, `content_pipeline.py` |

### Structure Patterns

**Frontend Component Organization:**

```
domains/
├── discovery/
│   ├── components/          # 业务组件
│   │   ├── TopicCard.tsx
│   │   ├── TopicCard.test.tsx   # co-located 测试
│   │   ├── FeedView.tsx
│   │   └── TopicFilter.tsx
│   ├── hooks/               # 域内 hooks
│   │   └── useTopicFeed.ts
│   ├── services/            # 域内服务
│   ├── types.ts             # 域内类型
│   ├── constants.ts         # 域内常量
│   └── index.ts             # 公开 API：只导出组件和类型
│
├── roundtable/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types.ts
│   └── index.ts
│
├── deliverable/
│   └── ...
│
└── identity/
    └── ...

components/
└── ui/                      # shadcn/ui 基础组件（全局共享）
    ├── button.tsx
    ├── card.tsx
    └── ...

shared/
├── api/
│   └── client.ts            # 统一 HTTP 客户端
├── events/
│   └── event-bus.ts         # 领域事件发布/订阅抽象层
├── types.ts                 # 跨域共享类型
└── ...
```

**域 index.ts 导出规则：**

- ✅ 导出：组件、类型定义
- ❌ 不直接导出：service、hook
- 跨域需要调用 service 时：通过防腐层接口（`shared/` 中定义的接口）暴露，不直接 import 域内 service

**统一 HTTP 客户端（`shared/api/client.ts`）：**

- 提供 `apiClient.get()`, `apiClient.post()`, `apiClient.put()`, `apiClient.delete()`
- 自动处理：cookie 透传、RFC 9457 错误解析、响应类型推断
- 所有前端 API 调用必须通过此客户端，禁止直接 fetch

**Backend Module Organization（补充 project-context）：**

```
backend/python/src/
├── facade/
│   ├── roundtable_facade.py     # 按域组织 facade
│   ├── content_facade.py
│   └── distribution_facade.py
├── app/
│   ├── roundtable_app.py
│   └── content_pipeline_app.py
├── service/
│   ├── roundtable/              # 复杂域可用子目录
│   │   ├── discussion_service.py
│   │   ├── autopilot_service.py
│   │   └── verify_service.py
│   ├── content_service.py
│   └── distribution_service.py
├── graph/                       # LangGraph 编排（见下方 LangGraph Patterns）
│   ├── roundtable_graph.py
│   ├── autopilot_graph.py
│   ├── verify_graph.py
│   ├── nodes/
│   │   ├── fact_checker_node.py
│   │   ├── expert_speak_node.py
│   │   ├── verify_quality_node.py
│   │   └── distill_content_node.py
│   └── state/
│       ├── roundtable_state.py
│       └── pipeline_state.py
├── repository/
│   ├── session_repository.py
│   ├── topic_repository.py
│   └── task_repository.py
└── model/
    ├── roundtable_models.py
    ├── content_models.py
    └── task_models.py

tests/                           # 后端测试：独立目录，镜像 src/ 结构
├── service/
│   ├── roundtable/
│   │   └── test_discussion_service.py
│   └── test_content_service.py
├── graph/
│   ├── test_roundtable_graph.py
│   └── nodes/
│       └── test_fact_checker_node.py
├── repository/
│   └── test_topic_repository.py
└── conftest.py
```

**测试文件位置：**

- 前端：co-located — `TopicCard.tsx` 旁边放 `TopicCard.test.tsx`
- 后端：独立 `tests/` 目录，镜像 `src/` 结构 — 各自生态惯例

### LangGraph Orchestration Patterns

**Graph 文件组织：**

| 规则 | 约定 | 示例 |
|------|------|------|
| Graph 定义 | `src/graph/{name}_graph.py` | `roundtable_graph.py`, `autopilot_graph.py` |
| Node 函数 | `src/graph/nodes/{name}_node.py`，函数名 `{verb}_{entity}` | `check_facts()`, `generate_expert_response()` |
| State 类型 | `src/graph/state/{name}_state.py`，TypedDict 定义 | `RoundtableState`, `PipelineState` |
| Graph 入口 | 每个 graph 文件导出 `create_{name}_graph()` 工厂函数 | `create_roundtable_graph()` |

**Node 函数规范：**

```python
# 每个 node 是纯函数：接收 state，返回 state 更新
async def check_facts(state: RoundtableState) -> dict:
    """求真者事实打底节点"""
    # 通过 LLM Gateway 调用，不直接调用 OpenRouter
    # 返回 state 的部分更新
    return {"facts": facts, "citations": citations}
```

**Graph 与 Service 的关系：**

- Graph 定义编排流程（谁先谁后、条件分支）
- Node 调用 service 层执行具体业务逻辑
- Graph 不直接访问 repository，通过 service 间接访问
- 依赖方向：`graph → service → repository`

### Domain Event Patterns

**Event Bus 抽象层（`shared/events/event-bus.ts`）：**

```typescript
interface EventBus {
  publish<T>(event: DomainEvent<T>): void;
  subscribe<T>(type: string, handler: (event: DomainEvent<T>) => void): void;
  unsubscribe(type: string, handler: Function): void;
}
```

- 生产环境：基于 React Context 或 EventEmitter 实现
- 测试环境：in-memory EventBus，可直接断言事件的发布和处理
- 事件命名：`SCREAMING_SNAKE_CASE`，`{ENTITY}_{ACTION}`
- 事件结构：`{type, payload, timestamp, sourceModule, correlationId?}`

### Format Patterns

**API Response Formats:**

```typescript
// 成功响应（保持已有格式）
{ "code": 0, "data": { ... } }

// 错误响应（RFC 9457 Problem Details）
{
  "type": "https://wenexus.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Topic with id 'abc123' does not exist"
}
```

**Date/Time Formats:**

- API 传输：ISO 8601 字符串 `"2026-03-20T14:30:00Z"`
- 数据库存储：`TIMESTAMP WITH TIME ZONE`
- 前端展示：通过 next-intl 格式化为本地化显示

**分页格式：**

```typescript
{
  "code": 0,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 156,
      "hasMore": true
    }
  }
}
```

### Communication Patterns

**State Management Patterns（React Context）：**

- 状态更新：不可变更新（spread operator / immer）
- Action 命名：`{verb}{Entity}`，如 `setTopics`, `updateConsensus`, `toggleAutopilot`
- Context 组织：每个域一个 Context Provider，不混用
- 性能：大对象拆分为多个小 Context，避免无关重渲染

### Process Patterns

**Error Handling:**

| 层级 | 策略 |
|------|------|
| 前端组件 | React Error Boundary 包裹域级组件，fallback UI |
| 前端 API 调用 | 统一通过 `shared/api/client.ts`，自动解析 RFC 9457 错误 |
| 后端 facade | 捕获异常，转换为 RFC 9457 格式返回 |
| 后端 service | 抛出领域异常（自定义 Exception 类），不处理 HTTP |
| 后端 repository | 抛出数据异常，不处理业务逻辑 |
| LLM 调用 | LLM Gateway 统一处理超时/限流/降级，service 层不直接 try-catch LLM 错误 |
| LangGraph Node | Node 内异常由 Graph 的 error handler 捕获，不向外泄露 |

**Loading State Patterns:**

- 命名：`is{Action}Loading`，如 `isDiscussionLoading`, `isCardGenerating`
- 流式加载：`isStreaming` + `streamProgress`（用于 AI 流式输出进度）
- 骨架屏：信息流和卡片使用 Skeleton 组件，圆桌讨论使用 typing indicator

**Retry Patterns:**

- API 调用：不自动重试，由用户触发
- LLM 调用：LLM Gateway 层处理（fallback chain），service 层不重试
- 任务调度：任务表记录重试次数，最大重试 3 次，指数退避
- 分发任务：失败自动重试（NFR9），记录失败原因

### Enforcement Guidelines

**All AI Agents MUST:**

1. 实现代码前阅读 `project-context.md` + 本架构文档的 Implementation Patterns 节；冲突时以本架构文档为准
2. 域内组件/类型通过 `index.ts` 暴露，service/hook 不直接 export，跨域调用通过防腐层接口
3. 新建数据库表时使用约定的前缀（前端 `auth_*`/`user_*`，后端 `agent_*`/`content_*`/`task_*`/`dist_*`）
4. WebSocket 消息必须包含 `type`, `payload`, `timestamp`, `sessionId` 四个字段，类型前后端通过 TS type + Pydantic model 对齐
5. 错误响应使用 RFC 9457 格式，成功响应使用 `{"code": 0, "data": {...}}`
6. LLM 调用统一通过 LLM Gateway，禁止 service 层直接调用 OpenRouter API
7. LangGraph Node 通过 service 层访问数据，不直接调用 repository
8. 前端所有 API 调用通过 `shared/api/client.ts`，禁止直接 fetch

**Pattern Enforcement:**

- 关键 patterns 通过 lint 规则或 pre-commit hook 自动检查（如 import 路径约束、表命名前缀）
- PR review 时对照 Enforcement Guidelines 检查
- 发现新的冲突点时，更新本文档并同步通知所有参与开发的 Agent

## Project Structure & Boundaries

### FR → 架构组件映射

**按 FR 能力域映射到具体目录：**

| FR 能力域 | 前端目录 | 后端目录 | 路由 |
|-----------|----------|----------|------|
| 话题与内容生产（FR1-7） | `domains/discovery/` | `service/discovery.py`, `repository/discovery.py`, `graph/autopilot_graph.py` | `(landing)/topic/` |
| 圆桌讨论引擎（FR8-15） | `domains/roundtable/` | `facade/roundtable.py`, `service/roundtable/`, `graph/roundtable_graph.py` | `(roundtable)/` |
| 观点卡片消费（FR16-23） | `domains/discovery/components/` | `graph/nodes/distill_content_node.py` | `(landing)/`, `topic/` |
| 内容搜索与发现（FR24-27） | `domains/shared-kernel/search-gateway/` | `service/search_service.py` | `(landing)/search/` |
| 产出物生成（FR28-29） | `domains/deliverable/` | `service/deliverable_service.py`, `graph/nodes/generate_deliverable_node.py` | `deliverable/` |
| 外部分发与导流（FR30-35） | `apps/admin` 分发管理页面 | `facade/distribution_facade.py`, `service/distribution_service.py`, `repository/distribution_repository.py` | `(admin)/distribution/` |
| 用户管理与付费（FR36-41） | `domains/identity/`, `core/auth/` | `facade/deps.py`（认证） | `(auth)/`, `(admin)/` |
| 质量保障与运维（FR42-48） | `apps/admin` 监控页面 | `graph/verify_graph.py`, `graph/nodes/verify_quality_node.py` | `(admin)/content/` |

**跨域共享功能映射：**

| 共享功能 | 前端位置 | 后端位置 |
|----------|----------|----------|
| LLM Gateway | `domains/shared-kernel/llm-gateway/` | `util/llm.py`（扩展为 Gateway） |
| Event Bus | `domains/shared-kernel/event-bus/` | 后端暂不需要（LangGraph 内部编排） |
| 搜索 Gateway | `domains/shared-kernel/search-gateway/` | `service/search_service.py` |
| 认证 & 权限 | `core/auth/`, `core/rbac/` | `facade/deps.py` |
| WebSocket 管理 | `shared/hooks/use-websocket.ts` | `util/websocket.py` |
| UI 组件库 | `shared/components/ui/`（shadcn/ui） | — |

### 完整项目目录结构（目标状态）

> 以下为基于当前代码库审计和架构决策的目标结构。标注 `[已有]` 表示现有代码，`[新建]` 表示待创建，`[迁移]` 表示需从当前位置迁移。

```
wenexus/
├── frontend/
│   ├── apps/
│   │   ├── web/                              # [已有] 主 Web 应用
│   │   │   └── src/
│   │   │       ├── app/                      # [已有] Next.js App Router
│   │   │       │   ├── [locale]/
│   │   │       │   │   ├── (auth)/           # [已有] 认证页面
│   │   │       │   │   ├── (admin)/          # [已有] 管理后台（内容调度 + 分发监控）
│   │   │       │   │   ├── (roundtable)/     # [已有] 圆桌讨论
│   │   │       │   │   ├── (landing)/        # [已有] 公开着陆页
│   │   │       │   │   ├── (chat)/           # [已有] 对话（待评估是否并入 roundtable）
│   │   │       │   │   ├── (docs)/           # [已有] 文档页
│   │   │       │   │   ├── topic/            # [已有] 话题 CRUD
│   │   │       │   │   └── deliverable/      # [已有] 产出物查看
│   │   │       │   └── api/
│   │   │       │       ├── domains/          # [已有] 域 API 路由
│   │   │       │       │   ├── discovery/    # [已有] 发现域 API
│   │   │       │       │   ├── roundtable/   # [已有] 圆桌域 API
│   │   │       │       │   ├── deliverable/  # [已有] 交付域 API
│   │   │       │       │   └── identity/     # [已有] 身份域 API
│   │   │       │       ├── auth/             # [已有] 认证 API
│   │   │       │       ├── ai/               # [已有] AI 生成 API
│   │   │       │       ├── payment/          # [已有] 支付回调 API
│   │   │       │       └── proxy/            # [已有] 代理 API
│   │   │       │
│   │   │       ├── domains/                  # [已有] 业务域层
│   │   │       │   ├── discovery/            # [已有] 发现域
│   │   │       │   │   ├── components/       # [已有] TopicCard, FeedView 等
│   │   │       │   │   ├── models/           # [已有] topic.ts, observation-card.ts
│   │   │       │   │   ├── services/         # [已有] topic-service.ts, feed-service.ts
│   │   │       │   │   ├── hooks/            # [新建] 域内 hooks
│   │   │       │   │   ├── types.ts          # [已有]
│   │   │       │   │   └── index.ts          # [已有]
│   │   │       │   ├── roundtable/           # [已有] 圆桌域
│   │   │       │   │   ├── components/       # [新建] 圆桌 UI 组件
│   │   │       │   │   ├── models/           # [已有] discussion-session.ts 等
│   │   │       │   │   ├── services/         # [已有] discussion-orchestrator.ts 等
│   │   │       │   │   ├── hooks/            # [新建] 域内 hooks
│   │   │       │   │   ├── types.ts          # [已有]
│   │   │       │   │   └── index.ts          # [已有]
│   │   │       │   ├── deliverable/          # [已有] 交付域
│   │   │       │   │   ├── models/           # [已有] deliverable.ts
│   │   │       │   │   ├── services/         # [已有] deliverable-service.ts
│   │   │       │   │   ├── types.ts          # [已有]
│   │   │       │   │   └── index.ts          # [已有]
│   │   │       │   ├── identity/             # [已有] 身份域
│   │   │       │   │   ├── models/           # [已有] user-preference.ts
│   │   │       │   │   ├── services/         # [已有] user-profile-service.ts
│   │   │       │   │   ├── types.ts          # [已有]
│   │   │       │   │   └── index.ts          # [已有]
│   │   │       │   └── shared-kernel/        # [已有] 共享内核
│   │   │       │       ├── event-bus/        # [已有] 领域事件
│   │   │       │       ├── llm-gateway/      # [已有] LLM 网关
│   │   │       │       └── search-gateway/   # [已有] 搜索网关
│   │   │       │
│   │   │       ├── shared/                   # [已有] 跨域共享
│   │   │       │   ├── components/
│   │   │       │   │   ├── ui/              # [已有] shadcn/ui 基础组件（~48 个）
│   │   │       │   │   ├── ai-elements/     # [已有] AI 专用组件
│   │   │       │   │   └── magicui/         # [已有] 动画组件
│   │   │       │   ├── blocks/              # [已有] 页面级复合组件
│   │   │       │   │   ├── chat/            # [已有] 聊天 UI 块
│   │   │       │   │   ├── common/          # [已有] 通用块
│   │   │       │   │   ├── dashboard/       # [已有] 仪表盘块
│   │   │       │   │   ├── form/            # [已有] 表单块
│   │   │       │   │   ├── generator/       # [已有] 生成器块
│   │   │       │   │   ├── sign/            # [已有] 登录注册块
│   │   │       │   │   ├── table/           # [已有] 数据表块
│   │   │       │   │   └── ...              # 其他小类（panel/email/console/payment）
│   │   │       │   ├── hooks/               # [已有] 跨域 hooks（use-websocket 等）
│   │   │       │   ├── contexts/            # [已有] React Context（app.tsx）
│   │   │       │   ├── lib/                 # [已有] 工具函数（cache/cookie/env/hash 等）
│   │   │       │   ├── models/              # [已有→迁移] 见技术债务 TD-5
│   │   │       │   ├── services/            # [已有→迁移] 见技术债务 TD-4
│   │   │       │   └── types/               # [已有] 跨域类型定义
│   │   │       │
│   │   │       ├── core/                    # [已有] 核心基础设施
│   │   │       │   ├── auth/                # [已有] 认证
│   │   │       │   ├── db/                  # [已有] 数据库（Drizzle）
│   │   │       │   ├── i18n/                # [已有] 国际化
│   │   │       │   ├── rbac/                # [已有] 权限
│   │   │       │   └── theme/               # [已有] 主题
│   │   │       │
│   │   │       ├── config/                  # [已有] 应用配置
│   │   │       │   ├── db/
│   │   │       │   │   └── schema.postgres.ts  # [已有] 数据库 Schema（前端管理的表）
│   │   │       │   └── index.ts             # [已有] 环境配置
│   │   │       │
│   │   │       ├── extensions/              # [已有] 第三方集成
│   │   │       │   ├── ads/                 # [已有] 广告
│   │   │       │   ├── payment/             # [已有] 支付
│   │   │       │   └── ...                  # AI providers 等
│   │   │       │
│   │   │       ├── themes/                  # [已有] 主题模板
│   │   │       └── middleware.ts             # [已有] Next.js 中间件
│   │   │
│   │   ├── admin/                            # [已有] 管理后台
│   │   └── mobile/                           # [已有] 移动端（MVP 空壳）
│   │
│   └── packages/
│       ├── e2e/                              # [已有] E2E 测试
│       ├── shared/                           # [已有] 跨应用共享
│       ├── types/                            # [已有] 共享类型
│       ├── ui/                               # [已有] 共享 UI
│       └── utils/                            # [已有] 共享工具
│
├── backend/
│   └── python/
│       └── src/wenexus/
│           ├── main.py                       # [已有] FastAPI 入口
│           ├── config/                       # [已有] 环境配置
│           │   └── __init__.py
│           ├── facade/                       # [已有] HTTP API 网关层
│           │   ├── deps.py                  # [已有] 依赖注入（认证）
│           │   ├── roundtable.py            # [已有] 圆桌 API
│           │   ├── discovery.py             # [已有] 发现 API
│           │   ├── deliverable.py           # [已有] 交付 API
│           │   └── distribution.py          # [新建] 分发 API
│           ├── app/                          # [已有→待实现] 应用编排层
│           │   ├── __init__.py              # [已有] 当前为空
│           │   ├── roundtable_app.py        # [新建] 圆桌编排
│           │   └── content_pipeline_app.py  # [新建] 内容管线编排
│           ├── service/                      # [已有] 业务逻辑层
│           │   ├── auth.py                  # [已有]
│           │   ├── roundtable.py            # [已有→重构] 见技术债务 TD-1
│           │   ├── discovery.py             # [已有→重构] 见技术债务 TD-1
│           │   ├── distribution_service.py  # [新建]
│           │   └── deliverable_service.py   # [新建]
│           ├── repository/                   # [已有] 数据持久层
│           │   ├── db.py                    # [已有] 数据库连接
│           │   ├── auth.py                  # [已有]
│           │   ├── roundtable.py            # [已有→扩展] 接收从 service 下沉的 SQL
│           │   ├── discovery.py             # [新建] 接收从 service 下沉的 SQL
│           │   ├── distribution.py          # [新建]
│           │   └── task.py                  # [新建] 任务表 CRUD
│           ├── graph/                        # [新建] LangGraph 编排层
│           │   ├── roundtable_graph.py      # 圆桌讨论 Graph
│           │   ├── autopilot_graph.py       # 离线内容生产 Graph
│           │   ├── verify_graph.py          # 质量验证 Graph
│           │   ├── nodes/                   # Graph 节点
│           │   │   ├── fact_checker_node.py
│           │   │   ├── expert_speak_node.py
│           │   │   ├── verify_quality_node.py
│           │   │   ├── distill_content_node.py
│           │   │   └── generate_deliverable_node.py
│           │   └── state/                   # Graph 状态定义
│           │       ├── roundtable_state.py
│           │       └── pipeline_state.py
│           ├── model/                        # [新建] 数据模型（Pydantic + SQLAlchemy）
│           │   ├── roundtable_models.py
│           │   ├── content_models.py
│           │   └── task_models.py
│           └── util/                         # [已有] 跨层工具
│               ├── llm.py                   # [已有→扩展] LLM Gateway
│               ├── schema.py               # [已有] 共享 DTO
│               └── websocket.py             # [已有] WebSocket 管理
│
├── docs/                                     # 文档
│   ├── bmad/planning-artifacts/             # 规划产物
│   ├── technical/                           # 技术方案（commit 对应）
│   ├── prd/                                 # 产品需求（只读）
│   ├── design/                              # 设计文档（只读）
│   └── theory/                              # 理论文档（只读）
│
├── .github/workflows/                        # CI/CD
│   └── ci.yml
│
└── 根配置文件
    ├── package.json / pnpm-workspace.yaml   # Monorepo 配置
    ├── turbo.json                            # Turborepo
    ├── .pre-commit-config.yaml              # Pre-commit hooks
    ├── docker-compose.yml                   # 本地开发环境（PostgreSQL + Redis）
    └── wrangler.toml                        # Cloudflare Workers 配置
```

### 架构边界定义

**API 边界（前后端通信）：**

| 边界 | 通信方式 | 路径 | 说明 |
|------|----------|------|------|
| 前端 → 后端 REST | HTTP（Next.js rewrite） | `/api/py/v1/*` → FastAPI | Cookie 自动透传，禁止硬编码后端地址 |
| 圆桌实时通信 | WebSocket | `/api/py/v1/ws/roundtable/{session_id}` | JSON + 消息类型枚举 |
| AI 流式输出 | LangGraph SDK 原生 | 待 PoC 确认具体协议 | 前端使用 LangGraph 客户端 SDK |
| 前端域 API | Next.js API Routes | `/api/domains/{domain}/*` | 薄代理层，转发到后端或直接 Drizzle 查询 |

**域边界（前端）：**

| 域 | 可依赖 | 不可依赖 | 通信方式 |
|----|--------|----------|----------|
| Discovery | shared-kernel, shared/ | Roundtable, Deliverable, Identity | Event Bus |
| Roundtable | shared-kernel, shared/ | Discovery, Deliverable, Identity | Event Bus |
| Deliverable | shared-kernel, shared/ | Discovery, Roundtable, Identity | Event Bus |
| Identity | shared-kernel, shared/ | Discovery, Roundtable, Deliverable | Event Bus |
| shared-kernel | shared/ | 任何业务域 | 被动提供服务 |

**数据边界（前后端职责分离）：**

| 数据职责 | 管理方 | ORM | Migration 工具 | 表前缀 |
|----------|--------|-----|----------------|--------|
| 用户认证 & 会话 | 前端（Drizzle） | Drizzle ORM | Drizzle Kit | `auth_*`, `user_*` |
| Agent 编排 & 圆桌讨论 | 后端（SQLAlchemy） | SQLAlchemy 2 async | Alembic | `agent_*` |
| 内容管理 & 话题 | 后端（SQLAlchemy） | SQLAlchemy 2 async | Alembic | `content_*` |
| 任务调度 | 后端（SQLAlchemy） | SQLAlchemy 2 async | Alembic | `task_*` |
| 分发管理 | 后端（SQLAlchemy） | SQLAlchemy 2 async | Alembic | `dist_*` |

**后端分层边界（严格单向依赖）：**

```
facade（HTTP 解析、参数校验）
   ↓ 调用
app（编排多个 service、授权逻辑）
   ↓ 调用
service（业务逻辑）+ graph（LangGraph 编排）
   ↓ 调用
repository（SQL 查询、数据持久化）
```

- facade 不写业务逻辑，不写 SQL
- app 不直接操作 DB
- service 不 import facade 的 Request/Response
- repository 不写业务判断
- graph node 通过 service 访问数据，不直接调 repository

### 集成点

**内部通信：**

| 通信路径 | 模式 | 说明 |
|----------|------|------|
| 前端域间 | Event Bus（发布/订阅） | 松耦合，通过 shared-kernel 的 EventBus 实例 |
| 前端 → 后端 | REST + WebSocket + LangGraph SDK | 三通道，按场景选择 |
| 后端分层间 | 函数调用（同进程） | 严格分层依赖 |
| LangGraph 内部 | Graph 编排 | Node → Service → Repository |

**外部集成：**

| 外部服务 | 集成位置 | 说明 |
|----------|----------|------|
| OpenRouter（LLM） | 后端 `util/llm.py`（LLM Gateway） | 统一接口 + 容错链 |
| 小红书等分发平台 | 后端 `service/distribution_service.py` | Plugin 架构，平台适配层 |
| 支付系统 | 前端 `extensions/payment/` + 后端 webhook | HTTPS + 支付令牌化 |
| better-auth | 前端 `core/auth/` | Cookie-based session |
| PostgreSQL | 前端 Drizzle + 后端 SQLAlchemy | 共享同一数据库，表前缀隔离 |
| Redis | 后端热数据缓存 | 连接管理在后端 |

### 技术债务登记簿（代码库审计发现）

> 以下问题不阻塞新功能开发，但应在 Epic 拆解时纳入治理计划，按优先级逐步修复。

**🔴 Critical — 违反架构分层原则**

| 编号 | 问题 | 位置 | 状态 |
|------|------|------|------|
| ~~TD-1~~ | ~~Service 层包含 SQL 查询~~ | ~~`service/roundtable.py`、`service/discovery.py`~~ | ✅ 已修复：SQL 下沉到 `repository/roundtable.py` 和 `repository/discovery.py` |
| ~~TD-2~~ | ~~Facade 跳过 App 层直接调 Service~~ | ~~`facade/roundtable.py`、`facade/discovery.py`~~ | ✅ 已修复：实现 `app/roundtable.py` 和 `app/discovery.py` 编排层 |
| TD-3 | 前端跨域依赖 | `domains/discovery/services/feed-service.ts` 第 1 行 import Roundtable 域的 `getExperts` | 改为通过 shared-kernel Event Bus 通信 |

**🟠 High — 需要修复**

| 编号 | 问题 | 位置 | 修复方案 |
|------|------|------|----------|
| TD-4 | `shared/services/` 混放扩展服务 | `ads.ts`, `affiliate.ts`, `analytics.ts`, `payment.ts` 等应在 `extensions/` | 迁移到 `extensions/` 目录，`shared/services/` 只保留真正跨域的（如 `rbac.ts`, `storage.ts`） |
| TD-5 | `shared/models/` 包含领域模型 | `chat.ts` → Roundtable, `order.ts` → Identity/Payment, `post.tsx` → Discovery | 迁移到对应域的 `models/` 目录 |
| ~~TD-6~~ | ~~Facade 层重复授权逻辑~~ | ~~`facade/roundtable.py` 4 处重复 `userId != user.id` 检查~~ | ✅ 已修复：授权逻辑统一到 app 层 |

**🟡 Medium — 代码整洁度**

| 编号 | 问题 | 位置 | 状态 |
|------|------|------|------|
| ~~TD-7~~ | ~~前端 6 个空遗留目录~~ | ~~`src/hooks/`, `src/types/`, `src/components/`, `src/pages/`, `src/store/`, `src/utils/`~~ | ✅ 已删除 |
| ~~TD-8~~ | ~~后端 2 个空目录~~ | ~~`api/`（空）, `common/`（空）~~ | ✅ 已删除 |
| TD-9 | `shared/lib/` 职责混杂 | 11 个文件混合工具函数、基础设施、业务辅助 | 按职责归类，或保持现状（影响不大） |

**🟢 Low — 注意事项**

| 编号 | 问题 | 位置 | 状态 |
|------|------|------|------|
| ~~TD-10~~ | ~~死代码~~ | ~~`facade/deps.py` 中 `get_session_for_user()` 未使用~~ | ✅ 已清理 |
| TD-11 | 域组件放置不一致 | Discovery 有 `components/`，Roundtable 无 | 在开发对应域 UI 时统一补齐 |

**治理原则：**

- ~~TD-1/2/3 应在对应域的第一个 Epic 开发时优先修复（涉及的代码本身就要改）~~ TD-1/2 已修复，TD-3 待实现 Event Bus
- ~~TD-7/8 可以立即执行（删除空目录，零风险）~~ 已完成
- TD-4/5 在重构 Sprint 中统一处理
- 新增代码必须遵循目标架构，不再积累新的技术债务

## Architecture Validation Results

### 一致性验证 ✅

**决策兼容性：**

- 技术栈版本兼容：Next.js 15 + React 19 + TailwindCSS 4 + shadcn/ui + Drizzle ORM 0.44.2 + FastAPI 0.104+ + SQLAlchemy 2.0 + LangGraph + PostgreSQL 16 + Redis 7，无已知版本冲突
- 前后端通信三通道职责清晰：REST（数据 CRUD）、WebSocket（圆桌实时）、LangGraph SDK（AI 流式），无重叠
- 双 ORM 策略通过表前缀隔离（前端 `auth_*`/`user_*`，后端 `agent_*`/`content_*`/`task_*`/`dist_*`），Migration 工具各自独立（Drizzle Kit / Alembic）
- 认证方案一致：better-auth cookie session → Next.js rewrite 自动透传 → 后端 `get_current_user` / `get_optional_user`

**模式一致性：**

- 命名约定完整覆盖 6 个维度：DB / API / WebSocket / 代码 / 文件 / 域目录
- 分层规则与边界定义对齐：facade→app→service→repository + graph→service→repository
- 错误处理格式统一：成功 `{"code": 0, "data": {...}}` + 错误 RFC 9457 Problem Details
- 域间通信统一使用 Event Bus 模式，禁止跨域直接 import

**结构对齐：**

- 项目目录结构与 4 域 + 共享内核边界一致
- App Router 路由分组映射到对应域功能
- 后端分层（facade/app/service/repository/graph）与依赖规则一致
- 技术债务已识别并登记，目标状态与当前状态的差距明确

### 需求覆盖验证 ✅

**功能需求覆盖（48/48 = 100%）：**

| FR 能力域 | FR 编号 | 架构支撑 | 覆盖 |
|-----------|---------|----------|------|
| 话题与内容生产 | FR1-FR7 | Discovery 域 + autopilot_graph + content 表 + 内容生命周期状态机 | ✅ |
| 圆桌讨论引擎 | FR8-FR15 | roundtable_graph（Autopilot/Interactive 双模式）+ WebSocket + LangGraph SDK + 会话持久化 | ✅ |
| 观点卡片消费 | FR16-FR23 | AIGC JSX（shadcn/ui 组件约束 + 提示词）+ SSR + 虚拟列表 + 移动端优先 | ✅ |
| 内容搜索与发现 | FR24-FR27 | shared-kernel/search-gateway + 对话式搜索状态管理 | ✅ |
| 产出物生成 | FR28-FR29 | Deliverable 域 + generate_deliverable_node | ✅ |
| 外部分发与导流 | FR30-FR35 | Distribution 子系统 + Plugin 架构 + 任务表调度 + admin 监控面板 | ✅ |
| 用户管理与付费 | FR36-FR41 | better-auth + RBAC 三角色 + extensions/payment + 积分模型 | ✅ |
| 质量保障与运维 | FR42-FR48 | verify_graph + LLM Gateway 容错链 + 行为埋点事件模型 | ✅ |

**非功能需求覆盖（17/17 = 100%）：**

| NFR 分类 | NFR 编号 | 架构支撑 | 覆盖 |
|----------|---------|----------|------|
| 性能 | NFR1-6 | SSR + 边缘部署、LangGraph streaming 首 token < 2s、虚拟列表 60fps | ✅ |
| 可靠性 | NFR7-10 | 幂等管线 + 断点续传、WebSocket 自动重连 + polling 降级、分发任务自动重试 | ✅ |
| 可扩展性 | NFR11-14 | 批量管线并行 + LLM rate limit awareness、DB 索引分页、LLM 热切换、Plugin 架构 | ✅ |
| 集成 | NFR15-17 | LLM Gateway 容错链（fallback + circuit breaker + rate limit）、平台适配层、HTTPS 支付令牌化 | ✅ |

### 实现就绪性验证 ✅

**决策完整性：**

- 7 个 Starter Phase ADR 全部有决策理由和变更触发条件
- 5 类核心架构决策（数据、认证、API、前端、基础设施）全部到位
- 实现优先顺序明确（0→5 步），依赖关系清晰
- Decision Change Triggers 表覆盖 5 种可能的方案调整场景

**结构完整性：**

- 完整项目树标注了 `[已有]` / `[新建]` / `[迁移]` 状态
- FR → 目录映射表覆盖全部 48 条 FR
- 架构边界定义涵盖 API / 域 / 数据 / 分层四个维度
- 11 项技术债务已登记，含具体修复方案和治理原则

**模式完整性：**

- Enforcement Guidelines 为 AI Agent 提供 8 条强制规则
- LangGraph 编排模式有文件组织规则、Node 规范和代码示例
- 错误处理、加载状态、重试策略按层级逐一定义
- 前后端类型共享契约明确（TS type ↔ Pydantic model）

### Gap 分析结果

| 编号 | Gap | 严重程度 | 影响 | 建议处理时机 |
|------|-----|----------|------|-------------|
| Gap-1 | RI-1 通信链路部署研究仍然 OPEN | ⚠️ 阻塞圆桌引擎开发 | 圆桌讨论单通道 vs 双通道方案待定 | Epic 1 开发前完成 PoC/spike |
| Gap-2 | 搜索架构实现细节偏薄（FR24-27） | 低 | 搜索引擎选型、多轮对话状态存储未细化 | 搜索功能 Epic 设计时补充 |
| Gap-3 | 行为埋点架构未细化（FR48） | 低 | 埋点事件模型和采集管道未定义 | 增长验证阶段前补充 |
| Gap-4 | AIGC JSX 组件白名单未枚举 | 低 | 提示词中引用的 shadcn/ui 组件集合待定义 | 卡片渲染 Epic 开发时定义 |

### 架构完整性检查清单

**✅ 需求分析**

- [x] 项目上下文深度分析（Brownfield 资产、约束、跨域关注点）
- [x] 规模与复杂度评估（中高复杂度，~25-30 架构组件）
- [x] 技术约束识别（6 项关键约束）
- [x] 跨域关注点映射（7 项）
- [x] 核心数据流路径定义（3 条）
- [x] 核心架构挑战识别（7 项）

**✅ 架构决策**

- [x] Starter Phase ADR（7 项）
- [x] 数据架构决策（6 项）
- [x] 认证与安全决策（3 项）
- [x] API 与通信决策（4 项）
- [x] 前端架构决策（4 项）
- [x] 基础设施与部署决策（4 项）
- [x] 决策变更触发条件（5 项）
- [x] 开放研究项（1 项：RI-1）

**✅ 实现模式**

- [x] 命名约定（DB / API / WebSocket / 代码 / 文件）
- [x] 结构模式（前端组件组织 / 后端模块组织 / 测试位置）
- [x] LangGraph 编排模式（Graph / Node / State 规范）
- [x] 领域事件模式（Event Bus 抽象层）
- [x] 格式模式（API 响应 / 日期 / 分页）
- [x] 通信模式（状态管理 / 错误处理 / 加载状态 / 重试）
- [x] 执行指南（8 条 AI Agent 强制规则）

**✅ 项目结构**

- [x] 完整目录树（前端 + 后端 + 文档 + CI/CD）
- [x] FR → 架构组件映射（48 FR 全覆盖）
- [x] 架构边界定义（4 类边界）
- [x] 集成点（内部通信 + 外部集成）
- [x] 技术债务登记簿（11 项，分级 + 修复方案）

### 架构就绪性评估

**整体状态：READY FOR IMPLEMENTATION**

**置信度：高**

基于以下判断：

- 48 FR + 17 NFR 100% 架构覆盖
- 所有决策有明确理由和变更触发条件
- 技术栈已在代码库中落地验证（Brownfield 优势）
- 实现模式足够具体，AI Agent 可据此一致实现

**核心优势：**

1. **双模式统一引擎设计**：Autopilot/Interactive 共享 LangGraph 编排，避免代码分裂
2. **域边界清晰**：4 域 + 共享内核，前后端一致，Event Bus 松耦合通信
3. **技术债务透明**：11 项已知债务全部登记，修复方案和时机明确
4. **Decision Change Triggers**：5 种场景的备选方案预备，降低架构调整成本
5. **Brownfield 资产充分利用**：已有代码（认证、WebSocket、SSE、i18n）直接复用

**待后续增强的领域：**

1. RI-1 通信链路 PoC 完成后，确定圆桌讨论最终通道方案
2. 搜索引擎选型和多轮对话状态管理方案（对应 Epic 时细化）
3. 行为埋点事件模型定义（增长验证阶段前）
4. AIGC JSX 组件白名单枚举（卡片渲染 Epic 时）

### 实现交接指南

**AI Agent 实现准则：**

1. 实现前必读：`project-context.md` + 本架构文档的 Implementation Patterns 节；冲突时以本文档为准
2. 严格遵循域边界：域间通过 Event Bus 通信，禁止跨域直接 import
3. 严格遵循分层规则：facade→app→service→repository，graph→service→repository
4. 新建数据库表使用约定前缀，通过对应 Migration 工具管理
5. 参考技术债务登记簿，在涉及相关代码时优先修复

**第一实现优先级（阻塞项）：**

1. **RI-1 PoC/spike**：验证 WebSocket / LangGraph SDK 在目标部署环境下的可行性
2. **TD-7/8 清理**：删除前后端空遗留目录（零风险，立即执行）
3. **数据架构落地**：后端 Alembic 初始化 + 表结构设计（`agent_*` / `content_*` / `task_*` / `dist_*`）
