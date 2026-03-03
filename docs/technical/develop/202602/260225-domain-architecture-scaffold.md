# 前端领域架构骨架搭建

**日期**: 2026-02-25
**分支**: `feat/domain-architecture`
**关联文档**: `docs/prd/domain-architecture.md`, `docs/prd/user-story-v4.md`

## 变更概述

基于"四域一核"（4 domains + 1 shared kernel）架构设计，在现有 Next.js 15 Web App（ShipAny 模板）基础上搭建前端领域骨架代码。本次变更仅建立目录结构、类型定义、数据库 Schema、服务接口骨架和路由占位页面，不实现具体业务逻辑。

## 架构决策

| 决策 | 理由 |
|------|------|
| 新增 `src/domains/` 目录，与现有 `src/shared/`、`src/core/` 并列 | 不侵入 ShipAny 模板代码；清晰区分平台基础设施与产品业务逻辑 |
| Schema 统一写入现有 `schema.postgres.ts` | 遵循 Drizzle 现有模式，单一 schema 文件 |
| 每个 domain 的 models/ 在域内，不放 `shared/models/` | 领域模型包含领域特有的业务规则和状态机 |
| API 路由放 `api/domains/` 下 | 与 ShipAny 模板 API 命名空间隔离 |
| 同步事件总线（非消息队列） | 单进程 Next.js 足够；后续可升级 |

## 新增目录结构

```
src/domains/
├── shared-kernel/           # 共享内核
│   ├── event-bus/           # 领域事件总线（同步 pub/sub）
│   └── llm-gateway/         # LLM 网关抽象接口
├── discovery/               # 发现域（话题 + Feed）
│   ├── types.ts
│   ├── models/              # topic, observation-card CRUD
│   └── services/            # topic-service, feed-service 骨架
├── roundtable/              # 圆桌域（讨论 + 专家）
│   ├── types.ts
│   ├── models/              # expert, discussion-session, discussion-message CRUD
│   └── services/            # expert, chat, autopilot, consensus 骨架
├── deliverable/             # 交付域（生成物）
│   ├── types.ts
│   ├── models/              # deliverable CRUD
│   └── services/            # deliverable-service, readiness-service 骨架
└── identity/                # 身份域（用户偏好）
    ├── types.ts
    ├── models/              # user-preference CRUD
    └── services/            # user-profile-service 骨架
```

## 数据库 Schema 变更

在 `schema.postgres.ts` 中新增 7 张表：

| 表名 | 所属域 | 用途 |
|------|--------|------|
| `topic` | Discovery | 讨论话题 |
| `expert` | Roundtable | AI 专家角色 |
| `discussion_session` | Roundtable | 讨论会话 |
| `discussion_message` | Roundtable | 讨论消息 |
| `observation_card` | Discovery/Deliverable | 观点卡片 |
| `user_preference` | Identity | 用户偏好 |
| `deliverable` | Deliverable | 生成交付物 |

所有表遵循现有模式：`text('id').primaryKey()`、`timestamp` 时间字段、`text` 存储 JSON。

## 领域事件

共享内核定义 10 种领域事件类型：

- `TOPIC_CREATED` / `TOPIC_CLICKED` — Discovery 域
- `CARD_LIKED` — Discovery 域
- `CONSENSUS_UPDATED` / `DISCUSSION_READY` / `EXPERT_SPOKE` — Roundtable 域
- `FEED_CONTENT_DISTILLED` — Discovery 域
- `DELIVERABLE_GENERATED` / `DELIVERABLE_EXPORTED` — Deliverable 域
- `USER_ACTION` — Identity 域

## 路由变更

### 页面路由

| 路由 | 用途 |
|------|------|
| `/[locale]/topic/[id]` | 话题详情（占位） |
| `/[locale]/topic/create` | 话题创建（占位） |
| `/[locale]/(roundtable)/roundtable/[topicId]` | 圆桌讨论（占位，独立布局） |
| `/[locale]/deliverable/[id]` | 交付物预览（占位） |

### API 路由

| 路由 | 方法 | 用途 |
|------|------|------|
| `/api/domains/discovery/topics` | GET/POST | 话题列表/创建 |
| `/api/domains/discovery/feed` | GET | Feed 流 |
| `/api/domains/roundtable/sessions` | GET/POST | 讨论会话 |
| `/api/domains/roundtable/messages` | GET/POST | 讨论消息 |
| `/api/domains/deliverable/generate` | POST | 生成交付物 |
| `/api/domains/identity/preferences` | GET/PUT | 用户偏好 |

## 不在本次范围

- 实际 LLM 集成和 prompt 工程
- Autopilot 状态机逻辑
- AIGC 渲染管线和共识度算法
- UI 组件（FeedView、ChatInterface、ExpertPanel 等）
- 客户端 Context、i18n、种子数据、Migration 脚本、测试
