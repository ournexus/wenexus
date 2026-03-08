# WeNexus 领域架构与全栈工程师岗位配置方案

> 版本: v1.3
> 视角: 集团架构师
> 更新时间: 2026-03-08
> 输入依据: user-story-v4.md v4.1 / aigc-architecture-vision.md v1.1 / 现有代码库（Monorepo 架构）

---

## 一、架构总览

本架构面向 **3-5 年长期演进** 的产品实现：以"四域一核"为稳定边界，通过最小共享内核与明确的域间契约支持持续扩展。

当前处于基线开发阶段，正在逐步实现 `user-story-v4.md` 所描述的"双层体验 + 交付闭环"的核心体验；本文将把"优先级/阶段"表达为演进路径，而不是把项目限定为最小可行性产品。

> **技术栈优先级说明**：基线阶段以 **Python FastAPI + Next.js 前端** 为主力技术栈。Java 微服务作为长期架构目标存在，短期不做迭代。下文中涉及 Java 的部分标注为 `[长期]`。

### 1.1 领域全景图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          WeNexus 业务领域全景                                    │
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Discovery   │  │  Roundtable  │  │  Deliverable │  │   Identity   │       │
│  │   发现域       │  │  圆桌域       │  │  交付域       │  │  身份域       │       │
│  │              │  │              │  │              │  │              │       │
│  │ • 信息流      │  │ • 讨论引擎    │  │ • 内容生成    │  │ • 用户档案    │       │
│  │ • 话题管理    │  │ • 专家系统    │  │ • AIGC 渲染   │  │ • 偏好积累    │       │
│  │ • 搜索筛选    │  │ • 对话编排    │  │ • 导出分发    │  │ • 隐私管控    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                 │               │
│         └────────┬────────┴────────┬────────┴────────┬────────┘               │
│                  │                 │                 │                         │
│         ┌────────▼─────────────────▼─────────────────▼────────┐               │
│         │                  Shared Kernel 共享内核               │               │
│         │                                                      │               │
│         │  • LLM Gateway（多模型网关）                           │               │
│         │  • Design System（设计系统/设计语言）                   │               │
│         │  • Event Bus（领域事件总线）                            │               │
│         └──────────────────────────────────────────────────────┘               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 领域间依赖关系

```
Discovery ──── 创建话题 ────▶ Roundtable ──── 讨论就绪 ────▶ Deliverable
    ▲                            │                              │
    │                            │◀── 获取讨论素材 ─────────────┤
    │                            │                              │
    │◀══ 内容供给（离线蒸馏 + 在线生成）════════════════════════┘
    │         （观点卡片、话题摘要、封面文案等）
    │
Identity ──── 用户偏好 ─────────▶ (全域消费)
```

> **粗线（══）** 表示 Discovery 信息流的主要内容来源：Deliverable 域从 Roundtable 讨论中蒸馏内容后，同时对用户交付和对 Discovery 信息流供给。

**关键原则**：

| 原则 | 说明 |
|------|------|
| **展示自治、内容依赖** | Discovery 展示层独立运行，内容由 Deliverable 供给 |
| **双重交付** | Deliverable 同时对用户交付和对 Discovery 信息流供给 |
| **讨论驱动** | Deliverable 必须依赖 Roundtable 讨论数据，两条管线复用同一内容源 |
| **身份贯穿** | Identity 为全域提供用户上下文，不阻塞核心流程 |
| **共享内核分层管控** | 核心层稳定不变；扩展层按需引入（详见 3.5 节和 ADR-006） |

---

## 二、定位与优先级总览

### 2.1 四域一核心

| 域 | 一句话定位 | 复杂度 | 人力占比 |
|----|-----------|--------|----------|
| **Discovery** | 让用户来（展示自治、内容依赖 Deliverable） | ★★☆ | 20% |
| **Roundtable** | 让用户留 | ★★★★★ | 50% |
| **Deliverable** | 让用户爽 + 让内容流转（双重交付：对用户 + 对信息流） | ★★★★ | 20% |
| **Identity** | 让用户回 | ★★☆ | 10% |
| **Shared Kernel** | 让 AI 稳 | ★★★ | 兼任 |

### 2.2 招聘优先级

1. **最先招**：全栈 A（AI 工程师）— Roundtable 域是产品灵魂
2. **紧随其后**：全栈 B（前端 Lead）— Discovery + Deliverable 是用户触点
3. **稳定后招**：全栈 C（产品工程师）— Identity 域可后置，基线阶段可由 A/B 兼顾

---

## 三、领域详细拆分

### 3.1 Discovery 域（发现域）

**使命**：让用户在 3 秒内被吸引，完成从"路过"到"点击"的转化。

**核心聚合根**：`Topic`、`FeedCard`、`ObservationCard`

**全栈实现分布**：

| 层 | 实现 |
|----|------|
| 前端 | `frontend/apps/web/src/domains/discovery/` — FeedView, FeedCard, TopicCard, ObservationCardView |
| Python 后端 | `backend/python/src/service/` — 话题 CRUD、内容持久化、推荐排序、AI 驱动的封面图生成、话题关键词提取 |
| Java 后端 `[长期]` | `backend/java/content-service/` — 规模化阶段承接话题和内容管理 |

```
Discovery 域
├── 子域：Feed（信息流）
│   ├── 职责：卡片瀑布流渲染、无限滚动、封面图加载
│   ├── 用户故事：US-01 浏览观点卡片、US-04 感知热度和筛选
│   ├── 组件：FeedView, FeedCard, TopicCard
│   └── 服务：unsplash.ts（封面图）
│
├── 子域：Topic Management（话题管理）
│   ├── 职责：话题 CRUD、公开/私有切换、状态流转
│   ├── 用户故事：US-03 创建话题、US-31 查看我的话题、US-32 管理私人圆桌
│   ├── 组件：TopicCard, (未来) TopicCreateModal
│   └── 数据：constants.ts (INITIAL_TOPICS)
│
└── 子域：Observation（观点卡片）
    ├── 职责：观点卡片展示、详情页、社交互动（点赞/收藏/分享）
    ├── 用户故事：US-02 深入查看观点、US-26 生成观点卡片
    ├── 组件：ObservationCardView
    └── 类型：ObservationCard, ObservationCardContent
```

> 领域事件详见第六节「领域事件目录」。

---

### 3.2 Roundtable 域（圆桌域）

**使命**：编排 AI 专家的多轮对话，让用户感受到"真正的辩论"。

**核心聚合根**：`ChatSession`、`Expert`、`AutopilotState`

**全栈实现分布**：

| 层 | 实现 |
|----|------|
| 前端 | `frontend/apps/web/src/domains/roundtable/` — ChatInterface, DiscussionThread, ConstellationView 等 |
| Python 后端 | `backend/python/src/service/` — LLM 多 Agent 编排、专家发言生成、挂机决策引擎、共识算法、讨论状态持久化、会话管理 |
| Java 后端 `[长期]` | `backend/java/consensus-service/` — 规模化阶段承接共识算法和会话管理 |

```
Roundtable 域
├── 子域：Expert System（专家系统）
│   ├── 职责：专家池管理、动态生成、邀请/移除/自定义
│   ├── 用户故事：US-17 邀请专家、US-18 移除专家、US-19 创建自定义专家
│   ├── 组件：ExpertManagementPanel, ConstellationView
│   ├── 服务：agentFactory.ts（动态专家生成）
│   └── 数据：constants.ts (EXPERTS)
│
├── 子域：Discussion Engine（讨论引擎）
│   ├── 职责：对话编排、线程管理、引用机制、共识度计算
│   ├── 用户故事：US-07 求真者打底、US-08 线程对话、US-09 专家引用
│   ├── 组件：ChatInterface, DiscussionThread, SpeakingArea, MessageList
│   ├── 服务：chatService.ts, consensusService.ts, threadService.ts
│   └── 类型：Message, ConsensusState
│
├── 子域：Autopilot（挂机/接管）
│   ├── 职责：AI 副主持人决策、自动推进、模式切换
│   ├── 用户故事：US-11 挂机围观、US-12 AI引导交付、US-13 接管、US-14 恢复挂机
│   ├── 组件：AutopilotStatusBar, AgentControlPanel
│   ├── 服务：autopilotService.ts
│   └── 类型：AutopilotState, AutopilotDecision
│
├── 子域：Host Control（主持人操控）
│   ├── 职责：点名、追问、反驳、投票、总结
│   ├── 用户故事：US-15 主持人操控、US-16 全局反馈
│   ├── 组件：HostControlPanel, RoundTable
│   └── 服务：hostActionService.ts
│
├── 子域：Participant（参与者模式）
│   ├── 职责：用户发言、专家针对性回应、角色切换
│   ├── 用户故事：US-20 切换参与者、US-21 参与者发言、US-22 针对性回应
│   ├── 组件：ParticipantInput
│   └── 服务：participantService.ts
│
└── 子域：Privacy（私密讨论）
    ├── 职责：私密标识、隐私保护、数据隔离
    ├── 用户故事：US-23 私密模式、US-24 隐私保护
    └── 策略：数据不用于训练、支持删除、产出默认私有
```

> 领域事件详见第六节「领域事件目录」。

---

### 3.3 Deliverable 域（交付域）

**使命**：将讨论成果转化为面向**用户**和面向**平台信息流**的内容产出——既对用户交付可复用的专业内容，也对 Discovery 信息流供给观点卡片、话题摘要等展示素材。

**核心聚合根**：`DeliverablePackage`

**全栈实现分布**：

| 层 | 实现 |
|----|------|
| 前端 | `frontend/apps/web/src/domains/deliverable/` — DynamicJSXRenderer, SlideViewer, 各交付物 UI |
| Python 后端 | `backend/python/src/service/` — AI 内容蒸馏、报告/卡片/脚本生成、AIGC 渲染逻辑、交付物持久化、导出任务管理 |
| Java 后端 `[长期]` | `backend/java/content-service/` — 规模化阶段承接交付物持久化 |

```
Deliverable 域
├── 子域：Content Distillation（内容蒸馏 → 对系统交付）
│   ├── 职责：从 Roundtable 讨论中提炼观点卡片、话题摘要、封面文案、热度指标等
│   │         供给 Discovery 信息流展示
│   ├── 模式：
│   │   ├── 离线批量（主流）：讨论达到一定深度/结束后自动蒸馏
│   │   └── 在线实时（辅助）：用户创建话题时实时生成初始卡片
│   ├── 服务：cardGeneratorService.ts, distillationService.ts（待建）
│   └── 产出：FeedCard 数据、话题摘要、专家金句、封面素材
│
├── 子域：Content Generation（内容生成 → 对用户交付）
│   ├── 职责：报告/文章/脚本/清单/社交内容的 AI 生成
│   ├── 用户故事：US-25~US-29（五种交付物）
│   ├── 组件：ConsensusReport, ArticleView, ScriptView,
│   │         ActionPlan, StrategyDeck, XiaohongshuView,
│   │         GaokaoComposition, PresentationView
│   ├── 服务：deliverableService.ts, reportService.ts
│   └── 类型：ConsensusReport, PublicArticle, PodcastScript,
│             VideoScript, XiaohongshuNote, GaokaoEssay
│
├── 子域：AIGC Rendering（AIGC 渲染）
│   ├── 职责：AI 生成的 JSX/HTML 实时渲染、流式展示
│   ├── 组件：DynamicJSXRenderer, SlideViewer, StreamingCoverSlide
│   ├── 服务：slideGeneratorService.ts
│   └── 类型：AISlide, SlidesStreamState
│
├── 子域：Readiness Assessment（就绪度评估）
│   ├── 职责：判断讨论是否充分、提示用户生成时机
│   ├── 组件：DeliverableReadinessIndicator, DeliverableToolbar
│   ├── 服务：readinessService.ts
│   └── 类型：DeliverableReadiness
│
└── 子域：Export & Distribution（导出分发）
    ├── 职责：PDF/Word/Markdown 导出、一键复制、社交分享
    └── 用户故事：US-25~US-29 中的导出需求
```

> **两条管线复用同一个内容源**（Roundtable 讨论产出），区别在于加工策略和分发目标：
>
> - Content Distillation → Discovery 信息流（系统消费）
> - Content Generation → 用户下载/分享（用户消费）

> 领域事件详见第六节「领域事件目录」。

---

### 3.4 Identity 域（身份域）

**使命**：理解用户、记住用户、服务用户。

**核心聚合根**：`UserProfile`

**全栈实现分布**：

| 层 | 实现 |
|----|------|
| 前端 | `frontend/apps/web/src/domains/identity/` — BackgroundCollector, Onboarding, GuidedTour |
| Python 后端 | `backend/python/src/service/` — 用户注册/认证、档案持久化、AI 对话式背景收集、偏好分析、隐私管控 |
| Java 后端 `[长期]` | `backend/java/user-service/` — 规模化阶段承接用户管理 |

```
Identity 域
├── 子域：Onboarding（背景收集）
│   ├── 职责：轻量对话、身份识别、深度偏好
│   ├── 用户故事：US-05 收集背景、US-30 新手引导
│   ├── 组件：BackgroundCollector, Onboarding, GuidedTour
│   └── 类型：UserIdentity, DiscussionDepth
│
├── 子域：Preference（偏好管理）
│   ├── 职责：专家偏好、产出格式偏好、模式偏好
│   ├── 用户故事：US-06 档案积累
│   ├── 服务：userProfileService.ts
│   └── 类型：UserProfile, TopicUserPreference
│
└── 子域：Privacy Control（隐私管控）
    ├── 职责：数据删除、隐私声明、访问控制
    └── 用户故事：US-24 隐私保护
```

---

### 3.5 Shared Kernel（共享内核）

共享内核分为 **核心层**（基线必需）和 **扩展层**（按需引入），避免过早引入不必要的复杂度。

```
Shared Kernel
│
├── 核心层（基线阶段必需）
│   ├── LLM Gateway（多模型网关）
│   │   ├── 职责：统一的 LLM 调用接口、模型切换、流式响应
│   │   ├── 服务：services/llm/（providers/, index.ts, types.ts）
│   │   ├── 服务：services/gemini/（geminiService.ts 及子模块）
│   │   └── 策略：fast/quality 双模式、fallback 机制
│   │
│   ├── Grounding & Search Gateway（求真/检索网关）
│   │   ├── 职责：实时搜索、来源抓取与归一化、引用（citation）结构化输出
│   │   ├── 说明：为"求真者开场"与交付物引用提供统一能力
│   │   └── 产物：可复用的 Citation 列表（标题、URL、摘要、时间、可信度等元数据）
│   │
│   ├── Persistence Port（持久化端口）
│   │   ├── 职责：以接口形式定义 Topic/Session/Profile 等核心对象的读写能力
│   │   ├── 基线实现：Python FastAPI 后端 + 数据库（PostgreSQL / SQLite）
│   │   └── 原则：领域逻辑依赖端口接口，不依赖具体存储实现
│   │
│   ├── Design System（设计系统）
│   │   ├── 职责：品牌设计语言、组件样式、情感色彩映射
│   │   ├── 文件：styles/designSystem.ts
│   │   └── 规范：aigc-architecture-vision.md 第十节
│   │
│   ├── UI Context（全局 UI 状态）
│   │   ├── 职责：路由、Toast、全局 Loading
│   │   └── 文件：contexts/UIContext.tsx
│   │
│   └── Shared Types（共享类型）
│       ├── 职责：跨域共享的核心类型定义
│       └── 文件：types.ts
│
└── 扩展层（按需引入，见 ADR-006）
    ├── Observability（可观测性与指标）
    │   ├── 职责：统一埋点事件模型、性能与质量指标、可追踪的请求/会话 ID
    │   └── 引入时机：产品打磨阶段（M2+），当需要北极星指标数据驱动迭代时
    │
    └── Policy & Safety（策略与安全）
        ├── 职责：提示注入防护、渲染白名单、内容合规策略、隐私策略
        └── 引入时机：上线前或涉及用户数据安全时
```

---

### 3.6 核心数据模型

各域聚合根的关键属性定义（详细字段在实现时由技术文档补充）：

| 域 | 聚合根 | 关键属性 | 备注 |
|----|--------|----------|------|
| Discovery | `Topic` | id, title, description, creatorId, isPrivate, status(`draft`/`active`/`archived`), expectedDeliverableType, consensusLevel, timestamps | consensusLevel 由 Roundtable 域回写 |
| Discovery | `FeedCard` | id, topicId, cardType(`observation`/`summary`/`quote`), title, content, expertId, coverImageUrl, engagement, sourceType(`distilled`/`user_generated`), createdAt | sourceType 区分蒸馏内容 vs 用户触发 |
| Roundtable | `ChatSession` | id, topicId, status(`initializing`/`fact_checking`/`discussing`/`concluded`), mode(`autopilot`/`host_control`/`participant`), experts, messageCount, consensusState, createdAt | |
| Roundtable | `Expert` | id, name, persona, stance(`support`/`oppose`/`neutral`), isCustom, avatarEmoji | isCustom 区分用户自定义 vs 系统预设 |
| Roundtable | `ConsensusState` | factualAgreement, stanceUnderstanding, rootCauseClarity | 三维度共识度，均为 0-100 |
| Deliverable | `DeliverablePackage` | id, topicId, sessionId, type(`report`/`observation_card`/`checklist`/`script`/`social_content`), status(`generating`/`ready`/`exported`), content, readiness, createdAt | content 为 AI 生成的 JSX/Markdown/JSON |
| Identity | `UserProfile` | id, backgroundSummary, preferences(favoriteExperts, preferredDeliverableType, discussionDepth), topicHistory, createdAt | discussionDepth: `shallow`/`moderate`/`deep` |

---

## 四、用户故事到领域的映射矩阵

| 用户故事 | Discovery | Roundtable | Deliverable | Identity | Shared |
|----------|:---------:|:----------:|:-----------:|:--------:|:------:|
| US-01 浏览观点卡片 | **主** | | | | |
| US-02 深入查看观点 | **主** | | | | |
| US-03 创建话题 | **主** | 协 | | | |
| US-04 感知热度和筛选 | **主** | | | | |
| US-05 收集用户背景 | | | | **主** | |
| US-06 用户档案积累 | | | | **主** | |
| US-07 求真者事实打底 | | **主** | | | LLM |
| US-08 线程式对话展示 | | **主** | | | |
| US-09 专家明确引用 | | **主** | | | |
| US-10 快速了解全貌 | | **主** | | | |
| US-11 挂机围观 | | **主** | | | |
| US-12 AI引导交付 | | **主** | 协 | | LLM |
| US-13 接管控制权 | | **主** | | | |
| US-14 恢复挂机 | | **主** | | | |
| US-15 主持人操控 | | **主** | | | |
| US-16 全局反馈 | | **主** | | | |
| US-17 邀请专家 | | **主** | | | |
| US-18 移除专家 | | **主** | | | |
| US-19 创建自定义专家 | | **主** | | | LLM |
| US-20 切换参与者 | | **主** | | | |
| US-21 参与者发言 | | **主** | | | |
| US-22 针对性回应 | | **主** | | | LLM |
| US-23 私密模式 | | **主** | | 协 | |
| US-24 隐私保护 | | 协 | | **主** | |
| US-25 共识报告 | | | **主** | | LLM |
| US-26 观点卡片 | 协 | | **主** | | LLM |
| US-27 决策清单 | | | **主** | 协 | LLM |
| US-28 辩论脚本 | | | **主** | | LLM |
| US-29 社交内容 | | | **主** | | LLM |
| US-30 新手引导 | | | | **主** | |
| US-31 查看我的话题 | **主** | | | 协 | |
| US-32 管理私人圆桌 | **主** | | | 协 | |

> **主** = 主责域，**协** = 协作域，**LLM** = 依赖共享内核的 LLM Gateway

---

## 五、全栈工程师岗位配置

### 5.1 配置原则

```
┌─────────────────────────────────────────────────────────────────┐
│                     岗位配置核心原则                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 一个域 = 一个 Owner                                         │
│     └── 每个域有且仅有一个全栈工程师作为 Domain Owner             │
│                                                                 │
│  2. Owner 不等于唯一贡献者                                       │
│     └── Owner 负责架构决策和代码审查，其他人可贡献代码            │
│                                                                 │
│  3. 共享内核由最资深的人兼任                                      │
│     └── LLM Gateway 是技术核心，需要最强的人把关                 │
│                                                                 │
│  4. 按业务价值排优先级                                           │
│     └── 基线阶段 Roundtable > Discovery > Deliverable > Identity│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 最小团队配置（3 人）

适用于：**种子轮 / 基线冲刺阶段**

**全栈工程师 A（Tech Lead / AI 工程师）**

- **主责域**：Roundtable 域 + Shared Kernel (LLM Gateway)
- **核心技能**：LLM Prompt Engineering、Agent 编排、流式响应、React + TypeScript 全栈、多 Agent 对话协议、Gemini / OpenAI API
- **关键交付**：chatService / autopilotService / threadService / LLM Gateway 抽象层 / 求真者 Deep Research + Grounding / 挂机接管状态机
- **覆盖故事**：US-07~US-22（16 个，占比 50%）

**全栈工程师 B（前端 Lead / AIGC 工程师）**

- **主责域**：Discovery 域 + Deliverable 域
- **核心技能**：React + Tailwind CSS + 动效设计、AIGC 渲染管线（JSX 动态编译/流式渲染）、社交媒体内容设计、SVG 动画 + 数据可视化
- **关键交付**：FeedView + 观点卡片系统 / DynamicJSXRenderer + SlideViewer 渲染管线 / cardGeneratorService / 五种交付物 UI
- **覆盖故事**：US-01~US-04, US-25~US-29, US-31~US-32（11 个，占比 34%）

**全栈工程师 C（产品工程师 / 体验设计）**

- **主责域**：Identity 域 + Design System + 新手引导
- **核心技能**：用户体验设计 + React 组件、用户行为分析 + A/B 测试、个性化推荐逻辑、数据埋点 + 指标体系
- **关键交付**：BackgroundCollector / Onboarding / GuidedTour / userProfileService + 偏好积累 / designSystem.ts 维护 / 北极星指标埋点
- **覆盖故事**：US-05~US-06, US-23~US-24, US-30（5 个，占比 16%）

### 5.3 成长团队配置（5 人）

适用于：**Pre-A 轮 / 产品打磨阶段**

在 3 人基础上拆分：

| 角色 | 主责域 | 从谁手中接过 |
|------|--------|-------------|
| **全栈 A**（AI Lead） | Roundtable: Discussion Engine + Autopilot | 不变 |
| **全栈 B**（前端 Lead） | Discovery 域（全部） | 不变，释放 Deliverable |
| **全栈 C**（产品工程师） | Identity 域 + Design System | 不变 |
| **全栈 D**（AIGC 工程师） | Deliverable 域（全部） | 从 B 手中接过 |
| **全栈 E**（AI 工程师） | Roundtable: Expert System + Host/Participant + Shared Kernel | 从 A 手中接过 |

### 5.4 规模团队配置（8 人）

适用于：**A 轮后 / 规模化阶段**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Discovery 域（2 人）                                           │
│  ├── 全栈 B1：Feed + Topic Management                          │
│  └── 全栈 B2：Observation + 推荐算法 + SEO                     │
│                                                                 │
│  Roundtable 域（3 人）                                          │
│  ├── 全栈 A ：Discussion Engine + Autopilot（Tech Lead）        │
│  ├── 全栈 E1：Expert System + Host Control                     │
│  └── 全栈 E2：Participant + Privacy + 实时通信                  │
│                                                                 │
│  Deliverable 域（2 人）                                         │
│  ├── 全栈 D1：Content Generation（报告/文章/脚本）              │
│  └── 全栈 D2：AIGC Rendering + Export（渲染管线 + 导出）        │
│                                                                 │
│  Identity + Shared Kernel（1 人）                               │
│  └── 全栈 C ：Identity 全域 + Design System + LLM Gateway      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、领域边界与接口契约

### 6.1 领域事件目录

全域领域事件汇总（各域出站事件统一管理）：

| 事件 | 生产者 | 消费者 | 说明 |
|------|--------|--------|------|
| `TopicCreated` | Discovery | Roundtable | 触发专家生成 + 求真者开场（含期望交付物类型，供引导策略使用） |
| `TopicClicked` | Discovery | Identity | 记录用户兴趣 |
| `CardLiked` | Discovery | Identity | 更新用户偏好 |
| `DiscussionReady` | Roundtable | Deliverable | 讨论素材充足，可生成交付物 |
| `ConsensusUpdated` | Roundtable | Discovery | 更新话题卡片上的共识度 |
| `ExpertSpoke` | Roundtable | Identity | 记录用户与专家的互动偏好 |
| `FeedContentDistilled` | Deliverable | Discovery | 蒸馏完成，观点卡片/话题摘要/封面素材等回流信息流 |
| `DeliverableGenerated` | Deliverable | Discovery | 用户触发的交付物生成完成（如观点卡片），可选回流 |
| `DeliverableExported` | Deliverable | Identity | 记录用户偏好的产出格式 |

### 6.2 域间通信规范

```typescript
// 领域事件类型定义（Shared Kernel）
type DomainEvent =
  // Discovery → Roundtable
  | { type: 'TOPIC_CREATED'; payload: { topicId: string; isPrivate: boolean; expectedDeliverableType?: string } }
  // Roundtable → Discovery
  | { type: 'CONSENSUS_UPDATED'; payload: { topicId: string; level: number } }
  // Roundtable → Deliverable
  | { type: 'DISCUSSION_READY'; payload: { topicId: string; readiness: number } }
  // Deliverable → Discovery（内容蒸馏：离线/在线生成的信息流素材）
  | { type: 'FEED_CONTENT_DISTILLED'; payload: { topicId: string; cards: string[]; summary?: string } }
  // Deliverable → Discovery（用户交付物可选回流）
  | { type: 'DELIVERABLE_GENERATED'; payload: { topicId: string; deliverableType: string } }
  // Any → Identity
  | { type: 'USER_ACTION'; payload: { action: string; context: Record<string, unknown> } };
```

### 6.3 Anti-Corruption Layer（防腐层）

各域通过明确的接口消费其他域的数据，禁止直接引用其他域的内部实现：

| 消费方 | 提供方 | 接口 | 说明 |
|--------|--------|------|------|
| Deliverable | Roundtable | `getDiscussionContext(topicId)` | 获取讨论摘要，不暴露内部 Message 结构 |
| Discovery | Deliverable | `getDistilledFeedContent(topicId)` | 获取蒸馏后的信息流素材（观点卡片、话题摘要、封面等） |
| Roundtable | Identity | `getUserPreference(userId)` | 获取用户偏好，用于个性化讨论 |
| All | Shared | `llm.generate(prompt, mode)` | 统一 LLM 调用入口 |

### 6.4 领域事件实现策略

领域事件在不同技术层有不同的实现机制：

| 层 | 机制 | 说明 |
|----|------|------|
| 前端（同进程） | EventEmitter / React Context | 同步派发，适用于 UI 状态联动（如 ConsensusUpdated → 更新卡片热度） |
| Python 后端（基线） | FastAPI 内部事件 + REST API | 基线阶段 Python 单服务内同步处理；跨模块通过内部函数调用 |
| Java 微服务间 `[长期]` | Spring Application Events + 消息队列 | 规模化阶段 Java 微服务间通信 |
| 前后端跨层 | SSE / WebSocket | 后端事件推送到前端（如讨论进展实时更新） |

**基线阶段简化方案**：前端 EventEmitter + Python 后端内部调用 + SSE 推送，不引入消息队列。待规模化阶段 Java 服务上线后按需升级。

---

## 七、技术栈与代码组织

### 7.1 当前技术栈

| 层 | 技术 | 说明 | 基线优先级 |
|----|------|------|-----------|
| 前端框架 | Next.js + React + TypeScript | Monorepo（pnpm + Turborepo），含 Web/Admin/Mobile 三端 | **主力** |
| 移动端 | React Native | 共享 packages（UI 组件、类型、工具函数） | 延后 |
| 样式 | Tailwind CSS | 原子化 CSS | **主力** |
| Python 后端 | FastAPI | AI/ML 服务 + 核心业务：facade → app → service → repository 分层 | **主力** |
| Java 后端 | Spring Boot + Maven | 微服务架构：core-service | `[长期]` 基线阶段不迭代 |
| AI 服务 | 多模型抽象（Gemini / OpenAI 等） | LLM Gateway 统一接口 | **主力** |
| 构建工具 | Turborepo（前端）/ uv（Python）/ Maven（Java，长期） | 各层独立构建 | — |

> **基线阶段技术选型**：Python FastAPI 同时承担 AI/ML 服务和核心业务逻辑（话题管理、用户管理、内容持久化）。Java 微服务作为规模化阶段的演进目标保留在架构中，但基线阶段不投入开发资源。

### 7.2 代码组织

按领域划分的 Monorepo，完整目录结构见 `CLAUDE.md`。核心映射关系：

| 层 | 领域映射 | 基线阶段 |
|----|----------|---------|
| 前端 | `frontend/apps/web/src/domains/{discovery,roundtable,deliverable,identity}/` — 按业务域组织页面和组件 | **主力** |
| Python 后端 | `backend/python/src/service/` — 核心业务逻辑 + AI/ML 密集型任务（LLM 编排、内容蒸馏、话题管理、用户管理） | **主力** |
| Java 后端 `[长期]` | `backend/java/` — core-service（共享内核）、user-service（Identity）、content-service（Discovery + Deliverable）、consensus-service（Roundtable） | 基线阶段不迭代 |

> 基线阶段为前端 + Python 后端双层架构，通过 API 契约松耦合。Java 微服务在规模化阶段按需引入。前端共享包位于 `frontend/packages/`（ui / types / utils / shared）。

---

## 八、阶段化优先级与里程碑

> 注：本章中的"优先级与里程碑"用于表达演进路径；项目目标是长期可持续迭代，而不是停留在最小可行性产品。

### 8.1 里程碑规划

> **时间估计说明**：以下时间基于 3 人团队（Python + Next.js 为主力技术栈）、全职投入、AI 辅助开发的假设。多 Agent 对话编排、流式 LLM 响应和 Prompt 调优是最大的不确定性来源，以下估计已包含合理缓冲。

```
M1: 基线体验闭环（8-10 周）
════════════════════════════
  Discovery: 首页信息流 + 话题创建（US-01, US-03, US-04）
  Roundtable: 求真者开场 + 挂机模式 + 线程对话（US-07, US-08, US-11）
  Deliverable: 观点卡片生成（US-26）
  Identity: 背景收集（US-05）
  基础设施: Python 后端 API + 数据库 + LLM Gateway + 前后端联调 + CI/CD

  复杂度因素：多 Agent 对话编排 + 流式 LLM 响应 + Prompt 工程 + 数据库设计

M2: 交互深度（4-6 周）
════════════════════════
  Roundtable: 接管/恢复 + 主持人操控 + 全局反馈（US-13~US-16）
  Deliverable: 共识报告 + 决策清单（US-25, US-27）
  Discovery: 观点详情页（US-02）

M3: 对外演示就绪（3-4 周）
════════════════════════════
  Deliverable: 公众号文章 + 社交内容（US-28, US-29）
  Identity: 新手引导（US-30）
  全域: 路演演示脚本打磨 + 预设话题数据 + 端到端体验优化
```

### 8.2 各域 P0/P1/P2 拆分

| 优先级 | Discovery | Roundtable | Deliverable | Identity |
|--------|-----------|------------|-------------|----------|
| **P0** | 信息流、话题创建 | 求真者、挂机、线程对话、接管 | 观点卡片、报告、清单 | 背景收集 |
| **P1** | 推荐排序、观点详情 | 参与者模式、专家管理、AI引导 | 文章、脚本、社交内容、AIGC渲染 | 偏好积累、新手引导 |
| **P2** | 搜索、审核、SEO | 自定义专家、理解地图、实时协作 | 导出PDF、分享优化 | 推荐个性化、隐私管控 |

---

## 九、风险与决策记录

### 9.1 架构决策记录（ADR）

| 编号 | 决策 | 理由 | 状态 |
|------|------|------|------|
| ADR-001 | 按业务域而非技术层划分代码 | 降低跨域耦合，支持独立迭代 | 已采纳 |
| ADR-002 | LLM Gateway 作为共享内核 | AI 是全产品核心能力，需统一管控 | 已采纳 |
| ADR-003 | 全栈架构：前端 Monorepo + Python 后端（基线）+ Java 微服务（长期） | 前端用 Next.js SSR 提升 SEO 和首屏性能；基线阶段 Python FastAPI 统一处理核心业务和 AI/ML 任务；规模化阶段 Java 微服务按需承接核心业务 | 已采纳（修订） |
| ADR-004 | 渐进式重构目录结构 | 避免大规模重构阻塞功能开发 | 建议 |
| ADR-005 | Roundtable 域人力占比 50% | 讨论引擎是产品核心差异化，复杂度最高 | 建议 |
| ADR-006 | 增强 Shared Kernel：Search/Grounding、持久化端口、可观测性、策略与安全 | 把跨域共性做成"内核能力"，防止域间直接耦合与重复建设 | 建议 |

### 9.2 关键风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 响应质量不稳定 | 讨论体验差、交付物质量低 | 多模型 fallback + 质量评估 + 人工兜底模板 |
| Roundtable 域过于复杂 | 开发周期失控 | 严格按子域拆分，挂机模式先于接管模式 |
| AIGC 渲染安全风险 | XSS 攻击 | DynamicJSXRenderer 沙箱化 + 白名单 |
| 单人域 Owner 离职 | 知识断层 | 代码审查交叉覆盖 + 领域文档 |

---

*文档结束 - v1.3*
