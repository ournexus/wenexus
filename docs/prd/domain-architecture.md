# WeNexus 领域架构与全栈工程师岗位配置方案

> 版本: v1.1
> 视角: 集团架构师
> 更新时间: 2025-02-11
> 输入依据: user-story-v4.md v4.0 / aigc-architecture-vision.md v1.0 / 现有代码库

---

## 一、架构总览

本架构面向 **3-5 年长期演进** 的产品实现：以“四域一核”为稳定边界，通过最小共享内核与明确的域间契约支持持续扩展。

在当前代码库基础上，已基本具备 `user-story-v4.md` 所描述的“双层体验 + 交付闭环”的基线能力；本文将把“优先级/阶段”表达为演进路径，而不是把项目限定为最小可行性产品。

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
| **展示自治、内容依赖** | Discovery 域的展示层可独立运行（纯静态卡片流即可获客），但信息流内容主要由 Deliverable 域供给 |
| **双重交付** | Deliverable 域同时负责对用户交付（报告/清单/脚本等）和对系统交付（观点卡片/摘要回流 Discovery 信息流） |
| **讨论驱动** | Deliverable 域必须依赖 Roundtable 的讨论数据，两条交付管线复用同一个内容源 |
| **身份贯穿** | Identity 域为所有域提供用户上下文，但不阻塞核心流程 |
| **共享内核最小化** | LLM Gateway 和 Design System 是唯二的共享依赖 |

---

## 二、领域详细拆分

### 2.1 Discovery 域（发现域）

**使命**：让用户在 3 秒内被吸引，完成从"路过"到"点击"的转化。

**核心聚合根**：`Topic`、`FeedCard`、`ObservationCard`

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

**领域事件（出站）**：

| 事件 | 消费者 | 说明 |
|------|--------|------|
| `TopicCreated` | Roundtable 域 | 触发专家生成 + 求真者开场（含期望交付物类型，供 Roundtable 引导策略使用） |
| `TopicClicked` | Identity 域 | 记录用户兴趣 |
| `CardLiked` | Identity 域 | 更新用户偏好 |

---

### 2.2 Roundtable 域（圆桌域）

**使命**：编排 AI 专家的多轮对话，让用户感受到"真正的辩论"。

**核心聚合根**：`ChatSession`、`Expert`、`AutopilotState`

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

**领域事件（出站）**：

| 事件 | 消费者 | 说明 |
|------|--------|------|
| `DiscussionReady` | Deliverable 域 | 讨论素材充足，可生成交付物 |
| `ConsensusUpdated` | Discovery 域 | 更新话题卡片上的共识度 |
| `ExpertSpoke` | Identity 域 | 记录用户与专家的互动偏好 |

---

### 2.3 Deliverable 域（交付域）

**使命**：将讨论成果转化为面向**用户**和面向**平台信息流**的内容产出——既对用户交付可复用的专业内容，也对 Discovery 信息流供给观点卡片、话题摘要等展示素材。

**核心聚合根**：`DeliverablePackage`

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

**领域事件（出站）**：

| 事件 | 消费者 | 说明 |
|------|--------|------|
| `FeedContentDistilled` | Discovery 域 | 蒸馏完成，观点卡片/话题摘要/封面素材等回流到信息流 |
| `DeliverableGenerated` | Discovery 域 | 用户触发的交付物生成完成（如观点卡片），可选回流 |
| `DeliverableExported` | Identity 域 | 记录用户偏好的产出格式 |

---

### 2.4 Identity 域（身份域）

**使命**：理解用户、记住用户、服务用户。

**核心聚合根**：`UserProfile`

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

### 2.5 Shared Kernel（共享内核）

```
Shared Kernel
├── LLM Gateway（多模型网关）
│   ├── 职责：统一的 LLM 调用接口、模型切换、流式响应
│   ├── 服务：services/llm/（providers/, index.ts, types.ts）
│   ├── 服务：services/gemini/（geminiService.ts 及子模块）
│   └── 策略：fast/quality 双模式、fallback 机制
│
├── Grounding & Search Gateway（求真/检索网关）
│   ├── 职责：实时搜索、来源抓取与归一化、引用（citation）结构化输出
│   ├── 说明：为“求真者开场”与交付物引用提供统一能力，避免 Roundtable 直接耦合外部搜索 API
│   └── 产物：可复用的 Citation 列表（标题、URL、摘要、时间、可信度等元数据）
│
├── Persistence Port（持久化端口）
│   ├── 职责：以接口形式定义 Topic/Session/Profile 等核心对象的读写能力
│   ├── 说明：当前可用本地存储实现（localStorage/IndexedDB），未来可无缝替换为后端/BFF
│   └── 原则：领域逻辑依赖端口接口，不依赖具体存储实现
│
├── Observability（可观测性与指标）
│   ├── 职责：统一埋点事件模型、性能与质量指标、可追踪的请求/会话 ID
│   └── 说明：支撑长期增长与质量治理（讨论完成率、产物生成率、话题创建率等）
│
├── Policy & Safety（策略与安全）
│   ├── 职责：提示注入防护、渲染白名单、内容合规策略、隐私策略（私密数据不外泄）
│   └── 说明：与 AIGC 渲染安全、私密讨论等能力形成一致的安全边界
│
├── Design System（设计系统）
│   ├── 职责：品牌设计语言、组件样式、情感色彩映射
│   ├── 文件：styles/designSystem.ts
│   └── 规范：aigc-architecture-vision.md 第十节
│
├── UI Context（全局 UI 状态）
│   ├── 职责：路由、Toast、全局 Loading
│   └── 文件：contexts/UIContext.tsx
│
└── Shared Types（共享类型）
    ├── 职责：跨域共享的核心类型定义
    └── 文件：types.ts
```

---

## 三、用户故事到领域的映射矩阵

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

## 四、全栈工程师岗位配置

### 4.1 配置原则

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

### 4.2 最小团队配置（3 人）

适用于：**种子轮 / 基线冲刺阶段**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  全栈工程师 A（Tech Lead / AI 工程师）                                       │
│  ═══════════════════════════════════════                                     │
│  主责域：Roundtable 域 + Shared Kernel (LLM Gateway)                        │
│                                                                             │
│  技能要求：                                                                  │
│  • 精通 LLM Prompt Engineering、Agent 编排、流式响应                         │
│  • 熟悉 React + TypeScript 全栈                                             │
│  • 能设计多 Agent 对话协议（线程、引用、共识度算法）                          │
│  • 理解 Gemini / OpenAI API 的能力边界                                       │
│                                                                             │
│  关键交付：                                                                  │
│  • chatService / autopilotService / threadService                           │
│  • LLM Gateway 抽象层（多模型切换）                                          │
│  • 求真者 Deep Research + Grounding 机制                                     │
│  • 挂机/接管状态机                                                           │
│                                                                             │
│  覆盖用户故事：US-07~US-22（16 个，占比 50%）                                │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  全栈工程师 B（前端 Lead / AIGC 工程师）                                     │
│  ═══════════════════════════════════════                                     │
│  主责域：Discovery 域 + Deliverable 域                                       │
│                                                                             │
│  技能要求：                                                                  │
│  • 精通 React + Tailwind CSS + 动效设计                                      │
│  • 熟悉 AIGC 渲染管线（JSX 动态编译、流式渲染）                              │
│  • 有小红书/社交媒体内容设计感                                               │
│  • 能实现 SVG 动画、数据可视化                                               │
│                                                                             │
│  关键交付：                                                                  │
│  • FeedView 信息流 + 观点卡片系统                                            │
│  • DynamicJSXRenderer / SlideViewer 渲染管线                                 │
│  • cardGeneratorService / slideGeneratorService                             │
│  • 五种交付物的 UI 组件                                                      │
│                                                                             │
│  覆盖用户故事：US-01~US-04, US-25~US-29, US-31~US-32（11 个，占比 34%）     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  全栈工程师 C（产品工程师 / 体验设计）                                       │
│  ═══════════════════════════════════════                                     │
│  主责域：Identity 域 + Design System + 新手引导                              │
│                                                                             │
│  技能要求：                                                                  │
│  • 精通用户体验设计 + React 组件开发                                          │
│  • 熟悉用户行为分析、A/B 测试                                                │
│  • 能设计个性化推荐逻辑                                                      │
│  • 有数据埋点和指标体系经验                                                   │
│                                                                             │
│  关键交付：                                                                  │
│  • BackgroundCollector / Onboarding / GuidedTour                            │
│  • userProfileService + 偏好积累逻辑                                         │
│  • Design System（designSystem.ts）维护                                      │
│  • 北极星指标埋点（讨论完成率、产物生成率、话题创建率）                        │
│                                                                             │
│  覆盖用户故事：US-05~US-06, US-23~US-24, US-30（5 个，占比 16%）            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 成长团队配置（5 人）

适用于：**Pre-A 轮 / 产品打磨阶段**

在 3 人基础上拆分：

| 角色 | 主责域 | 从谁手中接过 |
|------|--------|-------------|
| **全栈 A**（AI Lead） | Roundtable: Discussion Engine + Autopilot | 不变 |
| **全栈 B**（前端 Lead） | Discovery 域（全部） | 不变，释放 Deliverable |
| **全栈 C**（产品工程师） | Identity 域 + Design System | 不变 |
| **全栈 D**（AIGC 工程师） | Deliverable 域（全部） | 从 B 手中接过 |
| **全栈 E**（AI 工程师） | Roundtable: Expert System + Host/Participant + Shared Kernel | 从 A 手中接过 |

### 4.4 规模团队配置（8 人）

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

## 五、领域边界与接口契约

### 5.1 域间通信规范

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

### 5.2 Anti-Corruption Layer（防腐层）

各域通过明确的接口消费其他域的数据，禁止直接引用其他域的内部实现：

| 消费方 | 提供方 | 接口 | 说明 |
|--------|--------|------|------|
| Deliverable | Roundtable | `getDiscussionContext(topicId)` | 获取讨论摘要，不暴露内部 Message 结构 |
| Discovery | Deliverable | `getDistilledFeedContent(topicId)` | 获取蒸馏后的信息流素材（观点卡片、话题摘要、封面等） |
| Roundtable | Identity | `getUserPreference(userId)` | 获取用户偏好，用于个性化讨论 |
| All | Shared | `llm.generate(prompt, mode)` | 统一 LLM 调用入口 |

---

## 六、技术栈与代码组织建议

### 6.1 当前技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 前端框架 | React + TypeScript | SPA，Vite 构建 |
| 样式 | Tailwind CSS | 原子化 CSS |
| AI 服务 | Gemini API（主）+ 多模型抽象 | LLM Gateway 已有雏形 |
| 状态管理 | React Context | 轻量级，基线阶段够用 |
| 构建工具 | Vite | 快速 HMR |

### 6.2 建议的目录重构（按领域划分）

```
src/
├── domains/
│   ├── discovery/
│   │   ├── components/     # FeedView, FeedCard, TopicCard, ObservationCardView
│   │   ├── services/       # feedService, topicService
│   │   ├── types.ts        # Discovery 域专属类型
│   │   └── index.ts        # 公开 API
│   │
│   ├── roundtable/
│   │   ├── components/     # RoundTable, ChatInterface, DiscussionThread,
│   │   │                   # AutopilotStatusBar, HostControlPanel,
│   │   │                   # ExpertManagementPanel, ParticipantInput,
│   │   │                   # ConstellationView, SpeakingArea, ConsensusMeter
│   │   ├── services/       # chatService, autopilotService, consensusService,
│   │   │                   # threadService, hostActionService, agentFactory
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   ├── deliverable/
│   │   ├── components/     # ConsensusReport, ArticleView, ScriptView,
│   │   │                   # ActionPlan, StrategyDeck, XiaohongshuView,
│   │   │                   # GaokaoComposition, PresentationView,
│   │   │                   # DynamicJSXRenderer, SlideViewer,
│   │   │                   # DeliverableToolbar, DeliverableReadinessIndicator
│   │   ├── services/       # deliverableService, cardGeneratorService,
│   │   │                   # slideGeneratorService, readinessService
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   └── identity/
│       ├── components/     # BackgroundCollector, Onboarding, GuidedTour
│       ├── services/       # userProfileService
│       ├── types.ts
│       └── index.ts
│
├── shared/
│   ├── llm/                # LLM Gateway（providers/, index.ts, types.ts）
│   ├── design-system/      # designSystem.ts, 全局样式
│   ├── ui/                 # Layout, Toast 等通用 UI
│   ├── contexts/           # UIContext
│   └── types.ts            # 跨域共享类型（最小集）
│
├── views/                  # 页面级组件（组装各域组件）
│   ├── Home.tsx
│   ├── TopicDetail.tsx
│   └── DeliverableResult.tsx
│
├── App.tsx
└── index.tsx
```

> **注意**：此重构为渐进式建议，不需要一次性完成。优先在新功能开发时按此结构组织。

---

## 七、阶段化优先级与里程碑

> 注：本章中的“优先级与里程碑”用于表达演进路径；项目目标是长期可持续迭代，而不是停留在最小可行性产品。

### 7.1 里程碑规划

```
M1: 基线体验闭环（2 周）
════════════════════════
  Discovery: 首页信息流 + 话题创建（US-01, US-03, US-04）
  Roundtable: 求真者开场 + 挂机模式 + 线程对话（US-07, US-08, US-11）
  Deliverable: 观点卡片生成（US-26）
  Identity: 背景收集（US-05）

M2: 交互深度（2 周）
════════════════════════
  Roundtable: 接管/恢复 + 主持人操控 + 全局反馈（US-13~US-16）
  Deliverable: 共识报告 + 决策清单（US-25, US-27）
  Discovery: 观点详情页（US-02）

M3: 对外演示就绪（1 周）
════════════════════════
  Deliverable: 公众号文章 + 社交内容（US-28, US-29）
  Identity: 新手引导（US-30）
  全域: 路演演示脚本打磨 + 预设话题数据
```

### 7.2 各域 P0/P1/P2 拆分

| 优先级 | Discovery | Roundtable | Deliverable | Identity |
|--------|-----------|------------|-------------|----------|
| **P0** | 信息流、话题创建 | 求真者、挂机、线程对话、接管 | 观点卡片、报告、清单 | 背景收集 |
| **P1** | 推荐排序、观点详情 | 参与者模式、专家管理、AI引导 | 文章、脚本、社交内容、AIGC渲染 | 偏好积累、新手引导 |
| **P2** | 搜索、审核、SEO | 自定义专家、理解地图、实时协作 | 导出PDF、分享优化 | 推荐个性化、隐私管控 |

---

## 八、风险与决策记录

### 8.1 架构决策记录（ADR）

| 编号 | 决策 | 理由 | 状态 |
|------|------|------|------|
| ADR-001 | 按业务域而非技术层划分代码 | 降低跨域耦合，支持独立迭代 | 已采纳 |
| ADR-002 | LLM Gateway 作为共享内核 | AI 是全产品核心能力，需统一管控 | 已采纳 |
| ADR-003 | 基线阶段可无后端运行，但预留可插拔后端能力 | 先保持交付速度，同时确保 3-5 年演进时能平滑引入 BFF/后端服务 | 已采纳 |
| ADR-004 | 渐进式重构目录结构 | 避免大规模重构阻塞功能开发 | 建议 |
| ADR-005 | Roundtable 域人力占比 50% | 讨论引擎是产品核心差异化，复杂度最高 | 建议 |
| ADR-006 | 增强 Shared Kernel：Search/Grounding、持久化端口、可观测性、策略与安全 | 把跨域共性做成“内核能力”，防止域间直接耦合与重复建设 | 建议 |

### 8.2 关键风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 响应质量不稳定 | 讨论体验差、交付物质量低 | 多模型 fallback + 质量评估 + 人工兜底模板 |
| Roundtable 域过于复杂 | 开发周期失控 | 严格按子域拆分，挂机模式先于接管模式 |
| AIGC 渲染安全风险 | XSS 攻击 | DynamicJSXRenderer 沙箱化 + 白名单 |
| 单人域 Owner 离职 | 知识断层 | 代码审查交叉覆盖 + 领域文档 |

---

## 九、总结

### 9.1 四域一核心

| 域 | 一句话定位 | 复杂度 | 人力占比 |
|----|-----------|--------|----------|
| **Discovery** | 让用户来（展示自治、内容依赖 Deliverable） | ★★☆ | 20% |
| **Roundtable** | 让用户留 | ★★★★★ | 50% |
| **Deliverable** | 让用户爽 + 让内容流转（双重交付：对用户 + 对信息流） | ★★★★ | 20% |
| **Identity** | 让用户回 | ★★☆ | 10% |
| **Shared Kernel** | 让 AI 稳 | ★★★ | 兼任 |

### 9.2 招聘优先级

1. **最先招**：全栈 A（AI 工程师）— Roundtable 域是产品灵魂
2. **紧随其后**：全栈 B（前端 Lead）— Discovery + Deliverable 是用户触点
3. **稳定后招**：全栈 C（产品工程师）— Identity 域可后置，基线阶段可由 A/B 兼顾

---

*文档结束 - v1.1*
