---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - docs/bmad/planning-artifacts/prd.md
  - docs/bmad/planning-artifacts/architecture.md
  - docs/bmad/planning-artifacts/ux-design-specification.md
---

# wenexus - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for wenexus, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

- **FR1**: 系统可以存储和管理经典争议话题库（含话题元数据、分类、标签）
- **FR2**: 系统可以将一个经典争议话题拆解为多个争议维度
- **FR3**: 系统可以为每个争议维度生成不同立场的 AI 专家视角
- **FR4**: 系统可以管理内容的生命周期状态（生成中 → 验证中 → 通过 → 异常 → 重新生成）
- **FR5**: 系统可以批量离线生产话题内容（吞吐量标准见 NFR11）
- **FR6**: 系统可以增量在线生成单个话题内容
- **FR7**: 系统可以展示话题之间的关联关系，用户可以沿关联路径浏览
- **FR8**: 系统可以以 Autopilot 模式（无用户输入）自动产出结构化多视角讨论内容
- **FR9**: 求真者（Fact Checker）可以为每次讨论提供事实数据基础
- **FR10**: 多位 AI 专家可以进行线程式辩论，明确引用和回应彼此观点
- **FR11**: 用户可以以「挂机围观」模式被动观看 AI 专家实时讨论
- **FR12**: 用户可以以「接管主持」模式输入问题引导讨论方向
- **FR13**: 用户可以在挂机围观与接管主持模式之间自由切换
- **FR14**: AI 专家回复支持实时渐进式呈现
- **FR15**: 用户可以回到之前的圆桌讨论继续对话
- **FR16**: 用户可以在话题维度的信息流中浏览观点卡片
- **FR17**: 用户可以在同一话题下浏览多个不同立场的观点卡片
- **FR18**: 系统可以将 AI 产出的内容渲染为长文本图文卡片（AIGC 直出 JSX）
- **FR19**: 用户可以分享观点卡片（分享内容自带品牌水印）
- **FR20**: 观点卡片页面支持 SEO 友好的服务端渲染
- **FR21**: 观点卡片支持移动端优先的响应式浏览体验
- **FR22**: 用户可以按生命阶段或主题分类浏览话题
- **FR23**: 免费用户可以预览圆桌讨论的摘要或精彩片段
- **FR24**: 用户可以通过自然语言搜索话题和关联的观点卡片
- **FR25**: 用户可以在搜索结果基础上连续发起追问（多轮对话式搜索）
- **FR26**: 用户可以从搜索结果无缝进入相关话题的圆桌讨论
- **FR27**: 系统可以在首页为用户推荐相关话题和观点卡片
- **FR28**: 用户可以指定产出物类型，系统根据圆桌讨论内容生成对应格式的产出物
- **FR29**: 用户可以下载或分享生成的产出物
- **FR30**: AI Agent 可以自动在外部平台（小红书等）发布观点卡片内容
- **FR31**: 系统可以按预设时间调度自动分发任务
- **FR32**: 外部平台发布内容包含 WeNexus 导流链接
- **FR33**: 管理员可以查看分发监控面板（发布状态、曝光量、导流量、异常标记）
- **FR34**: 管理员可以标记异常内容并调整分发策略（暂停/恢复/修改）
- **FR35**: 系统可以对分发异常自动触发告警通知
- **FR36**: 用户可以注册和登录 WeNexus
- **FR37**: 免费用户可以无限浏览观点卡片信息流
- **FR38**: 付费会员可以使用交互式圆桌讨论功能
- **FR39**: 付费会员可以生成和获取产出物
- **FR40**: 系统支持会员积分制（积分获取、消耗、查询）
- **FR41**: 系统支持付费购买会员/积分
- **FR42**: Verify Agent 可以自动验证 AI 生成内容的质量（论证完整性、视角多元性、事实准确性、排版规范）
- **FR43**: 通过验证的内容自动进入线上话题库和分发队列
- **FR44**: 未通过验证的内容自动标记为异常并触发通知
- **FR45**: 管理员可以对异常内容进行人工介入处理（重新生成/编辑/放弃）
- **FR46**: 系统通过统一接口（OpenRouter）支持多种 LLM 供应商切换
- **FR47**: 系统支持对不同功能模块配置不同 LLM 模型
- **FR48**: 系统可以采集和记录用户关键行为数据（浏览、点击、停留、分享、转化）

### NonFunctional Requirements

- **NFR1**: 观点卡片首屏加载时间 < 2s（Cloudflare Workers 边缘部署 + SSR）
- **NFR2**: AI 专家单轮流式回复首 token 延迟 < 2s
- **NFR3**: 圆桌讨论全程流畅无明显卡顿，用户无需等待超过 5s
- **NFR4**: AIGC JSX 卡片渲染成功率 > 95%，跨现代浏览器兼容
- **NFR5**: 自然语言搜索返回结果 < 3s
- **NFR6**: 移动端卡片信息流滚动体验流畅（60fps）
- **NFR7**: 系统整体可用性 > 99.5%
- **NFR8**: 内容生产流水线（Autopilot + Verify Agent）支持断点续传，单个话题失败不阻塞批量任务
- **NFR9**: 外部平台分发任务失败时自动重试，并记录失败原因
- **NFR10**: WebSocket 断连后自动重连，支持 polling 降级
- **NFR11**: 离线批量内容生产吞吐量 > 100 话题/天
- **NFR12**: 话题库从 50 扩展至 10000+ 时，卡片浏览性能无明显退化
- **NFR13**: LLM 供应商切换不影响线上服务，支持热切换
- **NFR14**: 系统架构支持未来新增外部分发平台，无需核心代码重构
- **NFR15**: 通过 OpenRouter 统一接口对接 LLM 供应商，接口超时、限流有降级处理
- **NFR16**: 外部平台（小红书等）分发集成支持平台 API 变更后的快速适配
- **NFR17**: 支付系统集成满足基本交易安全（HTTPS、支付令牌化）

### Additional Requirements

**来源：Architecture Decision Document**

- **AR1**: Brownfield 项目，技术栈已确定（Next.js 15 + React 19 + TailwindCSS 4 + shadcn/ui + FastAPI + LangGraph + PostgreSQL 16 + Redis 7），所有开发必须基于已有代码库
- **AR2**: 前后端数据库职责分离——前端 Drizzle ORM 管理 `auth_*`/`user_*` 表，后端 SQLAlchemy 管理 `agent_*`/`content_*`/`task_*`/`dist_*` 表，各自管理 migration（Drizzle Kit + Alembic）
- **AR3**: RBAC 三角色权限模型：free_user / premium_user / admin，扩展 better-auth session 角色字段
- **AR4**: API 鉴权通过 Session cookie 透传（Next.js rewrite `/api/py/v1/*` 自动携带），后端通过 `get_current_user` / `get_optional_user` 解析
- **AR5**: 错误响应迁移到 RFC 9457 Problem Details 格式；成功响应保持 `{"code": 0, "data": {...}}`
- **AR6**: WebSocket 圆桌通信协议——JSON 消息 + 类型枚举（ExpertSpeak / ModeSwitch / ConsensusUpdate / UserInput / SystemNotice 等），前后端通过 TS type + Pydantic model 对齐
- **AR7**: AI 流式输出采用 LangGraph SDK 原生流式协议（后端 LangGraph → 前端 LangGraph 客户端 SDK），需 PoC 验证可行性
- **AR8**: LLM Gateway 扩展——在已有 `util/llm.py` 基础上增加容错链（fallback chain + circuit breaker + rate limit handling），支持模块级模型配置和热切换
- **AR9**: 前端组件按域组织（domains/discovery、roundtable、deliverable、identity + shared-kernel），域内组件通过 index.ts 暴露，跨域通过防腐层接口
- **AR10**: shadcn/ui 作为统一组件样式系统，同时作为 AIGC JSX 生成的预定义组件白名单约束
- **AR11**: LangGraph 统一编排在线链路（Interactive 圆桌）和离线链路（Autopilot 内容生产），Graph → Service → Repository 依赖方向
- **AR12**: 任务表驱动调度——状态 + 并发数控制 + LLM rate limit awareness，短期手动触发
- **AR13**: 通信协议 PoC/spike 是实现第 0 步——验证 WebSocket / SSE / LangGraph SDK 在 Cloudflare Workers 部署下的可行性，阻塞圆桌引擎开发
- **AR14**: 领域事件 EventBus 抽象层用于跨域通信（`shared/events/event-bus.ts`），事件命名 `{ENTITY}_{ACTION}` SCREAMING_SNAKE_CASE
- **AR15**: 统一 HTTP 客户端（`shared/api/client.ts`）——所有前端 API 调用必须通过此客户端，禁止直接 fetch，自动处理 cookie 透传和 RFC 9457 错误解析

### UX Design Requirements

**来源：UX Design Specification**

**核心体验**

- **UX-DR1**: 三拍节奏体验——信息流中观点卡片按「停顿（钩子卡片 3s 内抓住注意力）→ 发现（同话题 3+ 不同立场，触发 Aha Moment）→ 颠覆（自己坚信的观点被意外角度刺穿）」编排，每一拍有对应的视觉反馈（停顿：无干扰阅读；发现：维度进度条 + 金色微光；颠覆：分享按钮高亮脉冲）
- **UX-DR2**: 三种差异化着陆场景——信息流首页（卡片瀑布流 + 话题分类 Tab）、单卡片着陆页（完整观点卡片 + "看看其他专家怎么说" CTA）、话题着陆页（话题概览 + 多视角卡片组 + 圆桌入口），SEO/外部导流用户零拦截直达内容
- **UX-DR3**: 零门槛深入原则——从浅到深每一步不要求注册或学习新概念；注册仅在用户产生"保存/延续"需求时出现（首次收藏、浏览 5+ 卡片后软浮条），永不在内容消费时弹出
- **UX-DR4**: 付费墙作为"自然升级邀请"——免费用户可无限浏览卡片 + 预览圆桌摘要/精彩片段，付费解锁交互式圆桌和产出物；用户付费动机是"我要用理解去行动"而非"我被挡在门外"

**视觉设计系统**

- **UX-DR5**: "杂志编辑"视觉方向——低饱和度、大量留白、排版驱动、内容至上；参考 Monocle 杂志 + Aesop + Apple 产品页质感；底色暖灰白 `#FAFAF8`（非纯白），深色暖灰 `#1C1C1E`（非纯黑）
- **UX-DR6**: 10 个语义化色彩 Token（surface/surface-raised/text-primary/text-secondary/brand/accent/border/success/warning/danger），各有亮色/暗色值，对比度满足 WCAG AA（正文 ≥ 7:1 AAA，辅助文字 ≥ 4.5:1 AA，强调色 ≥ 3:1 大文本）
- **UX-DR7**: Major Third（1.25）排版系统——8 级字号阶梯（Display 32px → Caption 12px），正文 16px 行高 1.6，长文本 18px 行高 1.7；移动端 clamp() 响应式缩放（如 Display `clamp(26px, 4vw, 32px)`）
- **UX-DR8**: 4px 间距基准网格（4/8/12/16/24/32/48/64），圆角系统（按钮 8px / 卡片 12px / 模态框 16px / 头像&标签 full）
- **UX-DR9**: 三级暖调阴影系统（shadow-sm 卡片默认 / shadow-md 卡片 hover / shadow-lg 模态框），阴影色 `rgba(29,29,31,opacity)` 非纯黑；暗色模式阴影降低 opacity 50% + 上边缘高光
- **UX-DR10**: 暗色模式 MVP 支持——TailwindCSS `dark:` 变体全局切换，Token 双色值体系，默认跟随系统设置用户可手动切换

**自定义组件规格**

- **UX-DR11**: TopicCard（观点卡片）三种变体——强调型（大号钩子 H1 + 全幅数据图表，话题首张约 20%）、标准型（左图右文/上文下数据，大多数约 60%）、引用型（大头像 + 大号引用块 + 核心论点，认知颠覆触发约 20%）；编排规则：同话题首张必为强调型，颠覆点用引用型，跨话题连续两张不同类型；内含话题色带（3px 顶部 + 话题 ID hash 色）、立场标签、专家头像、钩子文案、正文、数据引用块、底部操作栏（分享/收藏/进入圆桌）
- **UX-DR12**: ExpertAvatar（专家头像）——4 种尺寸（sm 32px / md 40px / lg 56px / xl 72px），4 种状态（空闲静态边框 / 发言中边框脉冲 / 思考中虚线旋转 / 被引用高亮），标识色 `hsl(H, 30%, 55%)` 按序号均匀分布，点击弹出 Popover（简介 + 立场 + 本次发言数）
- **UX-DR13**: RoundtableThread（圆桌对话线程）——桌面端 MVP 线性对话流 + 右侧专家面板（头像列表 + 状态），移动端线性对话流（iMessage 群聊左对齐气泡）；引用机制点击展开被引用原文（最多 1 层不嵌套）；流式逐字渲染 + 光标动画；围观模式自动滚动到最新，用户上滑浏览历史时暂停自动滚动 + 底部"回到最新"按钮；快捷操作长按（移动端）/hover（桌面端）弹出菜单：追问/展开/换角度
- **UX-DR14**: ConsensusGauge（共识度仪表）——桌面端水平进度条 + 百分比 + 颜色渐变（绿=共识 → 琥珀=分歧），移动端顶部紧凑进度条 + 文字提示（"观点趋于一致"/"存在较大分歧"），数值变化 600ms 滚动动画 + 颜色过渡
- **UX-DR15**: ControlPanel（操作台）——围观模式显示"接管主持"切换按钮 + 提示文案；主持模式显示输入框 + 发送按钮 + "回到围观"切换按钮；桌面端底部全宽固定栏，移动端底部精简操作 + 输入框展开动画
- **UX-DR16**: ExpertAssembly（专家入座动画）——2-3 秒全屏过渡体验：内置专家 0ms 出现 → 动态专家间隔 200ms 淡入 + 缩放（300-500ms）→ 全部就位后自动进入讨论；使用 Framer Motion AnimatePresence
- **UX-DR17**: AgentResponder（Agent 空状态应答）——搜索无结果时随机一位内置人格化专家（基于 `hash(query+date)` 确定性选择）流式承接用户问题，以该专家语言风格逐字输出 1-2 个初步视角 + 推荐 2-3 个相关已有话题 + "为这个问题创建圆桌" Accent 金色 CTA
- **UX-DR18**: DimensionProgress（维度进度）——浏览第 3 张同话题卡片时从底部浮现进度文字（"你已看到 3/6 个维度"）+ 细线进度条；Aha Moment 时进度条变为 Accent 金色 + 微光脉冲 600ms；全部浏览完显示"你已看到全貌"翡翠绿成就 + 关联话题推荐入口；未完成离开显示"还有 N 个维度没看到"
- **UX-DR19**: ShareCardGenerator（分享图生成）——后端 API 渲染（Playwright 截图）产出适配多平台的带品牌水印图片：小红书 3:4（1080x1440px）、朋友圈 1:1（1080x1080px）、微信对话 5:4（1200x960px）；水印规格：右下角距边缘 24px，WeNexus logo + "扫码看更多视角"，透明度 85%，含导流短链/二维码
- **UX-DR20**: SkeletonLoader（骨架屏）——4 种变体（卡片型 / 文本型 / 头像型 / 对话型），脉冲渐变动画 surface → surface-raised 循环；规则：只在首次加载使用，AI 流式输出不用骨架屏，加载超 5s 显示文字提示

**导航与布局**

- **UX-DR21**: 移动端底部 Tab 栏——5 个 Tab（首页/搜索/创建(+)/圆桌/我的），固定 56px 高度；进入圆桌时 Tab 栏下滑隐藏 150ms → ControlPanel 上滑出现 150ms；退出圆桌反向过渡
- **UX-DR22**: 桌面端顶部导航栏——Logo + 搜索栏 + 话题分类 Tabs + 创建按钮 + 头像菜单，固定定位
- **UX-DR23**: 核心页面布局规则——信息流首页（移动端单列卡片全宽 / 桌面端双列瀑布流 max-width 1280px）、话题详情页（移动端单列 / 桌面端主内容区 + 右侧话题导航）、圆桌讨论（移动端 iMessage 式 / 桌面端线性对话流 + 底部操作台）、产出物页面（全宽阅读 / 居中 max-width 720px）

**交互模式**

- **UX-DR24**: 按钮四级层次——Primary（Accent 金色填充，核心 CTA，每页最多 1 个）、Secondary（Brand 描边）、Ghost（无背景无边框）、Danger（Danger 填充）；最小高度 40px 桌面 / 44px 移动端触控目标；所有按钮支持 loading 状态
- **UX-DR25**: Toast 反馈系统——底部居中，操作成功 3s 自动消失，操作失败需手动关闭 + 重试按钮，最多同时 1 条后到替换先到，移动端支持滑动关闭；背景色 surface-raised + shadow-md
- **UX-DR26**: 乐观更新模式——收藏、分享等操作用户点击后立即成功 UI，后台异步提交；失败时回滚 UI + Toast "操作失败，请重试"
- **UX-DR27**: 四层错误处理——组件级（"内容加载失败，点击重试"占位卡片）、页面级（优雅降级页面 + "刷新重试"）、网络级（顶部黄色警示条"网络连接中断，正在重连…"自动重连后消失）、API 级（Toast + 自动重试 1 次，失败后重试按钮）
- **UX-DR28**: 加载模式——首屏 SkeletonLoader，卡片图片渐进式加载（模糊→清晰 Next.js blur placeholder），AI 流式逐字 + 光标（无骨架屏），分享图生成按钮 loading + 进度提示
- **UX-DR29**: 空状态永不纯空白——搜索无结果用 AgentResponder；卡片不足展示已有 + "更多视角正在生成中…"骨架屏；圆桌无历史展示热门精彩片段 + "创建你的第一个圆桌"
- **UX-DR30**: 弹出层模式——Sheet（移动端底部上滑可拖拽三档 peek/half/full，桌面端右侧滑出）、Dialog（居中 2xl 圆角）；移动端所有 Popover/DropdownMenu 降级为底部 Sheet；遮罩层 surface 50% opacity 可点击关闭，打开时禁止背景滚动

**响应式设计**

- **UX-DR31**: Mobile-first 断点系统——5 个断点：sm 640px / md 768px / lg 1024px / xl 1280px / 2xl 1536px；关键变化：lg 处单列→双列瀑布流 + 圆桌对话流→对话流+专家面板；2xl 处页面容器 max-width 1280px 居中
- **UX-DR32**: 平板端方向适配——竖屏 = 移动端布局，横屏 = 桌面端布局，通过 orientation media query 检测避免旋转时体验断裂
- **UX-DR33**: 移动端手势系统——垂直滑动（浏览卡片流）、水平左滑（下一视角）/右滑（上一视角）、下拉刷新、长按圆桌发言弹出快捷操作、Sheet 底部上滑拖拽三档高度
- **UX-DR34**: 响应式组件适配——TopicCard（全宽单列 → lg 50% 双列）、RoundtableThread（全宽对话流 → lg 70% 主区+30% 面板）、ExpertPanel（移动端底部 Sheet → lg 右侧固定面板）、NavigationBar（移动端底部 Tab → lg 顶部导航）、SearchBar（移动端全屏覆盖 → lg 顶部内联）

**无障碍**

- **UX-DR35**: WCAG 2.1 AA 合规——色彩对比度（正文 ≥ 4.5:1，大文本 ≥ 3:1），立场标签三重编码（颜色+文字+图标形状）确保色盲可区分，共识度指示用进度条+数值+文字不仅靠颜色
- **UX-DR36**: 键盘导航——所有交互元素可 Tab 聚焦，焦点环 `focus-visible:ring-2 ring-brand ring-offset-2`，卡片 ← → 切换视角，圆桌 Enter 发送 / Escape 退出输入，弹出层 Focus Trap + Escape 关闭
- **UX-DR37**: 屏幕阅读器支持——TopicCard `role="article" aria-label="[专家名]关于[话题]的观点"`，RoundtableThread `role="log" aria-live="polite"`，ConsensusGauge `role="progressbar" aria-valuenow`，Toast `role="alert" aria-live="assertive"`
- **UX-DR38**: 动画无障碍——尊重 `prefers-reduced-motion`，所有动画可降级（渐入→直接显示，光标闪烁→无闪烁，进度条过渡→数值直接更新），使用 Framer Motion `useReducedMotion()`
- **UX-DR39**: Skip Link 实现——全局 layout 添加 "跳转到主内容" 链接，首次 Tab 显示，sr-only 正常隐藏

**内容消费与交互细节**

- **UX-DR40**: 卡片→圆桌过渡——底部上滑面板形式：展示圆桌预览（话题摘要 + 参与专家 + 精彩片段），确认后全屏展开进入实时圆桌；面板展示时建立 WebSocket 连接，给系统缓冲时间
- **UX-DR41**: 预加载策略——用户在某张卡片停留 >2s 时，系统预取该话题下其他立场的卡片数据，确保滑动到下一张时零等待
- **UX-DR42**: 动态发言间隔策略——快速反应（反驳/追问）3-5s，中等发言（展开论述）8-12s，深度发言（数据分析/长引用）12-18s；间隔中显示"思考中"状态动画 + 其他专家可能插入简短旁白填充等待感
- **UX-DR43**: 围观→接管缓冲——快捷操作（"追问这一点"/"让 TA 展开说"/"换个角度"）作为从纯围观到主动输入的过渡台阶，点击某条发言直接追问，降低"我该说什么"的门槛
- **UX-DR44**: "未完成的好奇"触发器——话题卡片末尾"这个话题还有 3 个你没看到的维度"、离开圆桌时"讨论还在继续…2 位专家有新发言"、关联话题推荐"如果你对'彩礼'感兴趣，'原生家庭'可能会颠覆你另一个认知"
- **UX-DR45**: 两步话题创建流程——(1) 一句话描述 + 公开/私人 Toggle（默认公开），(2) 点击"开始讨论"→ 专家入座过渡动画 → 求真者率先发言；专家选择、产出类型全部后置到讨论进行中
- **UX-DR46**: Z-index 分层系统——内容层 z-0 / 浮动元素 z-10 / 网络警示 z-15 / 遮罩层 z-20 / 弹出内容 z-30 / Toast z-40 / Dialog 遮罩 z-50 / Dialog 内容 z-60
- **UX-DR47**: 内容消费排版——长文本阅读 18px + 行高 1.7 + 段间距 24px + 最大宽度 720px；专家引用块 Brand 色 4px 左边框 + 斜体 + 浅背景色；数据高亮 Body-lg 加粗 + Accent 色
- **UX-DR48**: 分享卡片品牌水印——右下角距边缘 24px，WeNexus logo + "扫码看更多视角"，透明度 85%，导流短链/二维码可追踪来源平台
- **UX-DR49**: 专家立场色彩系统——头像边框每位专家分配低饱和度标识色 `hsl(H, 30%, 55%)`，发言气泡标识色 5% opacity 叠加 surface-raised，引用回复连线 Brand 色 20% opacity
- **UX-DR50**: 动画规范——专家入座淡入+缩放 300-500ms（间隔 200ms），共识度变化数值滚动+颜色渐变 600ms，卡片翻转/展开缩放+位移 250ms，专家状态边框渐变 200ms，页面切换淡入淡出 150ms，骨架屏脉冲循环；总原则：动画克制精准，只在关键时刻使用

### FR Coverage Map

| FR 编号 | Epic | 覆盖状态 |
|---------|------|---------|
| FR1 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR2 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR3 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR4 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR5 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR6 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR7 | Epic 2: 观点卡片消费体验 | ✅ |
| FR8 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR9 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR10 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR11 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR12 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR13 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR14 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR15 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR16 | Epic 2: 观点卡片消费体验 | ✅ |
| FR17 | Epic 2: 观点卡片消费体验 | ✅ |
| FR18 | Epic 2: 观点卡片消费体验 | ✅ |
| FR19 | Epic 2: 观点卡片消费体验 | ✅ |
| FR20 | Epic 2: 观点卡片消费体验 | ✅ |
| FR21 | Epic 2: 观点卡片消费体验 | ✅ |
| FR22 | Epic 2: 观点卡片消费体验 | ✅ |
| FR23 | Epic 2: 观点卡片消费体验 | ✅ |
| FR24 | Epic 6: 内容搜索与发现 | ✅ |
| FR25 | Epic 6: 内容搜索与发现 | ✅ |
| FR26 | Epic 6: 内容搜索与发现 | ✅ |
| FR27 | Epic 6: 内容搜索与发现 | ✅ |
| FR28 | Epic 5: 产出物生成与获取 | ✅ |
| FR29 | Epic 5: 产出物生成与获取 | ✅ |
| FR30 | Epic 7: 外部分发与导流 | ✅ |
| FR31 | Epic 7: 外部分发与导流 | ✅ |
| FR32 | Epic 7: 外部分发与导流 | ✅ |
| FR33 | Epic 7: 外部分发与导流 | ✅ |
| FR34 | Epic 7: 外部分发与导流 | ✅ |
| FR35 | Epic 7: 外部分发与导流 | ✅ |
| FR36 | Epic 3: 用户认证与身份管理 | ✅ |
| FR37 | Epic 3: 用户认证与身份管理 | ✅ |
| FR38 | Epic 4: 圆桌讨论交互体验 | ✅ |
| FR39 | Epic 5: 产出物生成与获取 | ✅ |
| FR40 | Epic 8: 会员付费与积分体系 | ✅ |
| FR41 | Epic 8: 会员付费与积分体系 | ✅ |
| FR42 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR43 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR44 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR45 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR46 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR47 | Epic 1: 话题管理与内容生产引擎 | ✅ |
| FR48 | Epic 6: 内容搜索与发现 | ✅ |

**覆盖率：48/48 = 100%**

## Epic List

### Epic 1: 话题管理与内容生产引擎（Autopilot）

**目标**：用户可以通过 Autopilot 模式批量或增量生产高质量多视角话题内容，内容经自动验证后进入线上话题库。

**覆盖 FR**：FR1, FR2, FR3, FR4, FR5, FR6, FR8, FR9, FR42, FR43, FR44, FR45, FR46, FR47（14 条）

**关联 NFR**：NFR8（断点续传）, NFR11（吞吐量）, NFR13（LLM 热切换）, NFR15（OpenRouter 容错）

**关联 AR**：AR2（数据库职责分离）, AR5（RFC 9457 错误格式）, AR8（LLM Gateway 容错链）, AR11（LangGraph 编排）, AR12（任务表驱动调度）

**关联 UX-DR**：无直接 UX（后端引擎）

---

### Epic 2: 观点卡片消费体验

**目标**：用户可以在信息流中浏览多视角观点卡片，按分类探索话题，分享卡片，并体验 SEO 友好的移动端优先页面。

**覆盖 FR**：FR7, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23（9 条）

**关联 NFR**：NFR1（首屏 < 2s）, NFR4（JSX 渲染 > 95%）, NFR6（60fps 滚动）, NFR12（万级话题性能）

**关联 AR**：AR9（前端域组织）, AR10（shadcn/ui + AIGC 白名单）, AR14（EventBus）, AR15（统一 HTTP 客户端）

**关联 UX-DR**：UX-DR1（三拍节奏）, UX-DR2（三种着陆场景）, UX-DR3（零门槛深入）, UX-DR4（付费墙自然升级）, UX-DR5-10（视觉设计系统）, UX-DR11（TopicCard 三变体）, UX-DR18（DimensionProgress）, UX-DR19（ShareCardGenerator）, UX-DR20（SkeletonLoader）, UX-DR21-23（导航与布局）, UX-DR24-30（交互模式）, UX-DR31-34（响应式设计）, UX-DR35-39（无障碍）, UX-DR40（卡片→圆桌过渡）, UX-DR41（预加载策略）, UX-DR44（未完成的好奇触发器）, UX-DR46-48（Z-index、排版、水印）, UX-DR50（动画规范）

---

### Epic 3: 用户认证与身份管理

**目标**：用户可以注册和登录 WeNexus，免费用户可以无限浏览观点卡片信息流。

**覆盖 FR**：FR36, FR37（2 条）

**关联 NFR**：NFR7（可用性 > 99.5%）

**关联 AR**：AR2（auth_*/user_* 表）, AR3（RBAC 三角色）, AR4（Session cookie 透传）

**关联 UX-DR**：UX-DR3（零门槛深入——注册时机控制）

---

### Epic 4: 圆桌讨论交互体验

**目标**：付费用户可以参与 AI 专家圆桌讨论，在挂机围观和接管主持模式间自由切换，体验实时流式辩论。

**覆盖 FR**：FR10, FR11, FR12, FR13, FR14, FR15, FR38（7 条）

**关联 NFR**：NFR2（首 token < 2s）, NFR3（全程 < 5s）, NFR10（WebSocket 重连 + polling 降级）

**关联 AR**：AR6（WebSocket 通信协议）, AR7（LangGraph SDK 流式）, AR11（LangGraph 编排 Interactive 模式）, AR13（通信协议 PoC）

**关联 UX-DR**：UX-DR12（ExpertAvatar）, UX-DR13（RoundtableThread）, UX-DR14（ConsensusGauge）, UX-DR15（ControlPanel）, UX-DR16（ExpertAssembly 入座动画）, UX-DR42（动态发言间隔）, UX-DR43（围观→接管缓冲）, UX-DR45（两步话题创建）, UX-DR49（专家立场色彩）, UX-DR50（动画规范）

---

### Epic 5: 产出物生成与获取

**目标**：付费用户可以基于圆桌讨论内容指定产出物类型，生成、下载或分享对应格式的产出物。

**覆盖 FR**：FR28, FR29, FR39（3 条）

**关联 NFR**：无直接 NFR

**关联 AR**：AR11（LangGraph 编排产出物生成）

**关联 UX-DR**：UX-DR23（产出物页面布局 max-width 720px）, UX-DR47（内容消费排版）

---

### Epic 6: 内容搜索与发现

**目标**：用户可以通过自然语言搜索话题和卡片，进行多轮追问，从搜索结果进入圆桌，首页获得话题推荐。

**覆盖 FR**：FR24, FR25, FR26, FR27, FR48（5 条）

**关联 NFR**：NFR5（搜索 < 3s）

**关联 AR**：AR15（统一 HTTP 客户端）

**关联 UX-DR**：UX-DR17（AgentResponder 空状态应答）, UX-DR29（空状态永不纯空白）, UX-DR34（SearchBar 响应式适配）

---

### Epic 7: 外部分发与导流

**目标**：AI Agent 可以自动在外部平台发布观点卡片内容，管理员可以通过监控面板查看分发状态并处理异常。

**覆盖 FR**：FR30, FR31, FR32, FR33, FR34, FR35（6 条）

**关联 NFR**：NFR9（分发重试）, NFR14（新平台扩展）, NFR16（平台 API 适配）

**关联 AR**：AR12（任务表驱动调度）

**关联 UX-DR**：UX-DR48（分享卡片品牌水印——导流短链/二维码）

---

### Epic 8: 会员付费与积分体系

**目标**：用户可以付费购买会员或积分，系统支持积分获取、消耗和查询。

**覆盖 FR**：FR40, FR41（2 条）

**关联 NFR**：NFR17（支付安全）

**关联 AR**：AR3（RBAC 权限升级）

**关联 UX-DR**：UX-DR4（付费墙自然升级邀请）

---

## Epic 1: 话题管理与内容生产引擎（Autopilot）

用户可以通过 Autopilot 模式批量或增量生产高质量多视角话题内容，内容经自动验证后进入线上话题库。

### Story 1.1: LLM Gateway 统一接口与模块级模型配置

As a 系统管理员,
I want 通过统一的 LLM Gateway 调用多种大模型，并为不同功能模块配置不同的模型,
So that 系统可以灵活切换 LLM 供应商且不影响线上服务。

**Acceptance Criteria:**

**Given** 系统已配置 OpenRouter API 凭证
**When** 通过 LLM Gateway 发起一次文本生成请求
**Then** 请求通过 OpenRouter 统一接口路由到指定模型并返回结果
**And** 响应时间和 token 用量被记录

**Given** 为「求真者」模块配置了模型 A，为「专家视角生成」模块配置了模型 B
**When** 分别从两个模块发起 LLM 调用
**Then** 各自使用配置中指定的模型，互不影响

**Given** 主模型调用超时或返回错误
**When** 触发容错链（fallback chain）
**Then** 自动切换到备用模型完成请求
**And** 记录降级事件日志

**Given** 某 LLM 供应商触发 rate limit
**When** Gateway 检测到限流响应
**Then** 自动执行退避重试或切换备用供应商
**And** 不向上层抛出限流错误

### Story 1.2: 话题数据模型与管理 API

As a 系统管理员,
I want 创建、编辑和管理经典争议话题（含元数据、分类、标签）,
So that 系统拥有结构化的话题库作为内容生产的基础。

**Acceptance Criteria:**

**Given** 管理员提交话题创建请求（标题、描述、分类、标签）
**When** 调用话题创建 API
**Then** 话题记录持久化到 `content_topics` 表，返回话题 ID
**And** 响应格式为 `{"code": 0, "data": {...}}`

**Given** 话题库中已有多个话题
**When** 按分类或标签筛选查询
**Then** 返回匹配的话题列表，支持分页

**Given** 管理员提交无效数据（如标题为空）
**When** 调用创建 API
**Then** 返回 RFC 9457 Problem Details 格式的错误响应

**Given** 管理员编辑已有话题的元数据
**When** 调用更新 API
**Then** 话题元数据更新成功，更新时间戳刷新

### Story 1.3: 话题维度拆解与专家视角数据模型

As a 内容生产系统,
I want 将一个话题拆解为多个争议维度，并为每个维度存储不同立场的专家视角,
So that 话题内容具备结构化的多维度多立场组织。

**Acceptance Criteria:**

**Given** 一个已创建的话题
**When** 系统为其创建多个争议维度（如经济、文化、法律等）
**Then** 维度记录持久化到 `content_dimensions` 表，关联到父话题
**And** 每个维度有标题、描述、排序序号

**Given** 一个已创建的维度
**When** 系统为该维度创建多个专家视角记录
**Then** 视角记录持久化到 `content_perspectives` 表
**And** 每个视角包含：专家标识、立场标签、视角内容、生成状态

**Given** 查询某话题下所有维度及视角
**When** 调用话题详情 API
**Then** 返回该话题的完整维度树（话题 → 维度列表 → 每个维度下的视角列表）

### Story 1.4: 内容生命周期状态管理

As a 内容生产系统,
I want 管理内容在生产流水线中的生命周期状态,
So that 每条内容的生产进度可追踪，异常可定位。

**Acceptance Criteria:**

**Given** 一条新建的内容记录（话题/维度/视角）
**When** 内容被创建
**Then** 初始状态为 `generating`

**Given** 内容状态为 `generating`
**When** 内容生成完成
**Then** 状态流转为 `verifying`

**Given** 内容状态为 `verifying`
**When** Verify Agent 验证通过
**Then** 状态流转为 `published`

**Given** 内容状态为 `verifying`
**When** Verify Agent 验证未通过
**Then** 状态流转为 `error`，附带失败原因

**Given** 内容状态为 `error`
**When** 触发重新生成
**Then** 状态流转为 `regenerating`，保留原始内容和错误记录

**Given** 任意非法状态转换请求（如从 `published` 直接到 `generating`）
**When** 尝试执行状态变更
**Then** 拒绝操作并返回错误，状态不变

### Story 1.5: 求真者（Fact Checker）Deep Agent 实现

As a 内容生产系统,
I want 求真者 Agent 为每个话题讨论提供经过验证的事实数据基础,
So that AI 专家的观点建立在可靠的数据之上而非凭空捏造。

**Acceptance Criteria:**

**Given** 一个话题及其争议维度
**When** 求真者 Agent 被调用
**Then** 产出结构化的事实报告，包含：关键统计数据、权威研究引用、政策法规摘要、跨国对比数据
**And** 每条事实标注数据来源和可信度等级

**Given** 求真者产出事实报告
**When** 报告内容包含具体数据（如百分比、金额、年份）
**Then** 数据格式规范化，引用来源可追溯

**Given** 话题涉及多个国家或文化背景
**When** 求真者执行事实收集
**Then** 产出覆盖多元背景的对比数据，不局限于单一视角

**Given** LLM 在事实生成中产出模糊或不确定的内容
**When** 求真者执行自检环节
**Then** 标注不确定项为「待人工核实」，不将低可信度数据混入确定性结论

### Story 1.6: AI 专家人设框架与内置专家库

As a 内容生产系统,
I want 拥有一套专家人设框架和一批内置的个性化 AI 专家,
So that 系统能为不同话题自动选择合适的专家组合，产出风格鲜明、立场多元的观点内容。

**Acceptance Criteria:**

**Given** 专家人设框架已定义
**When** 创建一位内置专家
**Then** 专家配置包含：名称、身份描述、知识领域、思维风格、立场倾向、说话语气、引用偏好、代表性观点

**Given** 系统内置专家库包含苏格拉底、爱因斯坦、马斯克、特朗普、老子、孔子、费孝通等专家
**When** 查询专家库
**Then** 每位专家有完整的人设配置，且各专家之间风格差异明显

**Given** 一个话题和其争议维度
**When** 系统执行专家选择策略
**Then** 自动匹配 3-5 位立场不同、领域互补的专家
**And** 确保选出的专家组合覆盖至少 3 种不同立场方向

**Given** 选定专家和话题维度
**When** 专家基于人设生成观点内容
**Then** 产出内容符合该专家的说话风格、知识领域和立场倾向
**And** 不同专家对同一维度的产出内容有实质性差异

### Story 1.7: Autopilot 模式内容生成引擎

As a 内容生产系统,
I want 以 Autopilot 模式（无用户输入）自动编排求真者和多位 AI 专家，产出结构化多视角讨论内容,
So that 话题内容可以全自动化生产。

**Acceptance Criteria:**

**Given** 一个话题已创建且有基本元数据
**When** 启动 Autopilot 内容生成
**Then** LangGraph 自动编排以下流程：调用求真者产出事实报告 → AI 拆解话题为多个争议维度 → 为每个维度选择专家组合 → 各专家基于事实报告和人设产出视角内容
**And** 全程无需用户输入

**Given** Autopilot 流程正在执行
**When** 每个节点完成
**Then** 产出的中间结果持久化，内容状态随流程推进自动更新

**Given** Autopilot 流程中某个节点执行失败（如 LLM 超时）
**When** 错误被捕获
**Then** 记录失败节点和错误信息，流程暂停但不影响其他话题
**And** 支持从失败节点重新执行（断点续传）

**Given** Autopilot 完成一个话题的全部内容生成
**When** 最终产出就绪
**Then** 话题下所有维度和视角内容完整，状态统一流转为 `verifying`

### Story 1.8: Verify Agent 自动质量验证

As a 内容生产系统,
I want Verify Agent 自动验证 AI 生成内容的质量,
So that 只有达标的内容才能进入线上话题库。

**Acceptance Criteria:**

**Given** 一条状态为 `verifying` 的视角内容
**When** Verify Agent 执行质量验证
**Then** 从四个维度评估并产出验证报告：论证完整性（观点有论据支撑，逻辑链完整）、视角多元性（与同维度其他视角有实质性差异）、事实准确性（引用的数据与求真者报告一致）、排版规范（内容结构清晰，符合卡片渲染要求）

**Given** 验证报告中所有维度评分达标
**When** Verify Agent 产出最终判定
**Then** 内容标记为「验证通过」

**Given** 验证报告中任一维度不达标
**When** Verify Agent 产出最终判定
**Then** 内容标记为「验证未通过」，附带具体不达标维度和改进建议

### Story 1.9: 验证通过自动发布与异常处理流程

As a 内容生产系统,
I want 验证通过的内容自动进入线上话题库和分发队列，未通过的内容自动标记异常并触发通知,
So that 内容流水线全自动化运转，异常不遗漏。

**Acceptance Criteria:**

**Given** 内容验证通过
**When** 状态流转为 `published`
**Then** 内容自动进入线上话题库（对用户可见）
**And** 同时进入分发队列（供 Epic 7 外部分发使用）

**Given** 内容验证未通过
**When** 状态流转为 `error`
**Then** 内容标记为异常，记录失败原因和 Verify Agent 改进建议
**And** 触发通知（日志记录 + 待后续对接通知渠道）

**Given** 同一话题下部分视角通过、部分未通过
**When** 查询话题生产状态
**Then** 可清晰看到每个维度、每个视角的独立状态，未通过的不阻塞已通过的发布

### Story 1.10: 管理员异常内容介入处理

As a 系统管理员,
I want 对异常内容进行人工介入处理（重新生成/编辑/放弃）,
So that 自动化流程无法解决的内容问题可以人工兜底。

**Acceptance Criteria:**

**Given** 管理员查看异常内容列表
**When** 调用异常内容查询 API
**Then** 返回所有状态为 `error` 的内容，包含失败原因和改进建议

**Given** 管理员对一条异常内容选择「重新生成」
**When** 调用重新生成 API
**Then** 内容状态流转为 `regenerating`，触发 Autopilot 重新生成该视角
**And** 保留原始内容和错误记录作为历史

**Given** 管理员对一条异常内容选择「编辑」
**When** 提交修改后的内容
**Then** 内容更新并重新进入验证流程（状态→`verifying`）

**Given** 管理员对一条异常内容选择「放弃」
**When** 调用放弃 API
**Then** 内容状态标记为 `abandoned`，不再进入任何自动化流程

### Story 1.11: 批量离线内容生产调度

As a 系统管理员,
I want 批量调度多个话题的 Autopilot 内容生产任务，支持并发控制和断点续传,
So that 系统可以高效批量产出话题内容（> 100 话题/天）。

**Acceptance Criteria:**

**Given** 管理员提交一批话题 ID 列表
**When** 创建批量生产任务
**Then** 任务记录写入 `task_*` 表，每个话题一条子任务，初始状态为 `pending`

**Given** 批量任务已创建
**When** 调度器开始执行
**Then** 按并发数上限（可配置）同时运行多个话题的 Autopilot 流程
**And** 感知 LLM rate limit，动态调节并发速度

**Given** 批量任务中某个话题生产失败
**When** 记录错误信息
**Then** 该话题子任务标记为 `failed`，不阻塞其他话题继续执行
**And** 支持后续单独重试失败的子任务

**Given** 批量任务执行中途系统中断
**When** 系统恢复后重新启动调度器
**Then** 从中断点继续执行未完成的子任务（断点续传），已完成的不重复执行

### Story 1.12: 增量在线内容生成

As a 系统管理员,
I want 在线触发单个话题的内容生成,
So that 可以按需为新话题快速生产内容，无需等待批量调度。

**Acceptance Criteria:**

**Given** 管理员指定一个新创建的话题
**When** 调用在线内容生成 API
**Then** 立即启动该话题的 Autopilot 流程，返回任务 ID

**Given** 在线生成任务已启动
**When** 查询任务状态
**Then** 可实时查看当前执行到哪个节点（求真者/维度拆解/专家生成/验证）

**Given** 在线生成任务执行完毕
**When** 所有内容生成并验证完成
**Then** 内容按正常流程进入线上话题库
**And** 任务状态更新为 `completed`

---

## Epic 2: 观点卡片消费体验

用户可以在信息流中浏览多视角观点卡片，按分类探索话题，分享卡片，并体验 SEO 友好的移动端优先页面。

### Story 2.1: 设计系统与通用组件基础

As a 前端开发者,
I want 一套完整的设计系统基础（色彩 Token、排版、间距、阴影、暗色模式）和通用 UI 组件,
So that 所有后续页面和组件有统一的视觉语言和交互基础。

**Acceptance Criteria:**

**Given** 设计系统已实现
**When** 查看色彩 Token 配置
**Then** 10 个语义化色彩 Token（surface/surface-raised/text-primary/text-secondary/brand/accent/border/success/warning/danger）全部定义，各有亮色/暗色值
**And** 底色暖灰白 `#FAFAF8`，深色暖灰 `#1C1C1E`，对比度满足 WCAG AA

**Given** 排版系统已实现
**When** 查看字号阶梯
**Then** 8 级字号（Display 32px → Caption 12px）按 Major Third 1.25 比例，正文 16px 行高 1.6
**And** 移动端使用 `clamp()` 响应式缩放

**Given** 间距与圆角系统已实现
**When** 查看间距和圆角配置
**Then** 间距基于 4px 网格（4/8/12/16/24/32/48/64），圆角按组件类型分级（按钮 8px / 卡片 12px / 模态框 16px / 头像 full）

**Given** 用户系统设置为暗色模式
**When** 页面加载
**Then** 自动切换到暗色主题，所有 Token 使用暗色值
**And** 用户可手动切换亮/暗模式

**Given** 通用组件（Button、Toast、SkeletonLoader、Sheet/Dialog）已实现
**When** 使用这些组件
**Then** Button 支持四级层次（Primary/Secondary/Ghost/Danger）和 loading 状态
**And** Toast 底部居中，成功 3s 消失，失败需手动关闭 + 重试
**And** SkeletonLoader 有 4 种变体（卡片型/文本型/头像型/对话型），脉冲渐变动画
**And** Sheet 移动端底部上滑三档（peek/half/full），Dialog 居中圆角

### Story 2.2: 应用布局与导航框架

As a 用户,
I want 在移动端看到底部 Tab 栏、在桌面端看到顶部导航栏，页面布局自适应设备,
So that 我可以在任何设备上流畅导航 WeNexus。

**Acceptance Criteria:**

**Given** 用户在移动端访问
**When** 页面加载
**Then** 底部显示固定 56px 高度的 Tab 栏（首页/搜索/创建/圆桌/我的）

**Given** 用户在桌面端（≥ lg 1024px）访问
**When** 页面加载
**Then** 顶部显示固定导航栏（Logo + 搜索栏 + 话题分类 Tabs + 创建按钮 + 头像菜单）

**Given** 用户在平板端旋转设备
**When** 竖屏时显示移动端布局，横屏时显示桌面端布局
**Then** 通过 orientation media query 平滑切换，无体验断裂

**Given** 用户首次按 Tab 键
**When** 焦点进入页面
**Then** Skip Link（"跳转到主内容"）可见，回车后焦点跳转到主内容区

**Given** 统一 HTTP 客户端已实现
**When** 前端发起 API 调用
**Then** 所有请求通过 `shared/api/client.ts` 统一发出，自动携带 cookie，自动解析 RFC 9457 错误
**And** 禁止直接使用 fetch

**Given** EventBus 抽象层已实现
**When** 跨域组件需要通信
**Then** 通过 `shared/events/event-bus.ts` 发布/订阅事件，事件命名 `{ENTITY}_{ACTION}` SCREAMING_SNAKE_CASE

### Story 2.3: 观点卡片组件（TopicCard）实现

As a 用户,
I want 看到排版精美、风格鲜明的观点卡片（含专家头像、立场标签、钩子文案、正文、数据引用）,
So that 我可以快速理解每位专家的核心观点。

**Acceptance Criteria:**

**Given** AI 产出的 JSX 内容数据
**When** TopicCard 组件渲染
**Then** 支持三种变体：强调型（大号钩子 H1 + 全幅数据图表）、标准型（左图右文/上文下数据）、引用型（大头像 + 大号引用块 + 核心论点）
**And** 卡片包含：3px 顶部话题色带、立场标签、专家头像、钩子文案、正文、数据引用块、底部操作栏

**Given** AIGC 直出的 JSX 内容
**When** 渲染卡片
**Then** 仅允许 shadcn/ui 白名单内的组件，渲染成功率 > 95%
**And** 渲染失败时显示优雅降级占位卡片（"内容加载失败，点击重试"）

**Given** 用户在移动端浏览
**When** 查看卡片
**Then** 卡片全宽显示，长文本 18px + 行高 1.7 + 段间距 24px + 最大宽度 720px

**Given** 用户使用屏幕阅读器
**When** 聚焦到卡片
**Then** 卡片具有 `role="article" aria-label="[专家名]关于[话题]的观点"`

**Given** 用户使用键盘导航
**When** 聚焦卡片后按 ← →
**Then** 切换到同话题的上一个/下一个视角卡片

**Given** 用户开启 `prefers-reduced-motion`
**When** 卡片动画触发
**Then** 所有动画降级为直接显示，无渐变/翻转/缩放效果

### Story 2.4: 信息流首页与话题分类浏览

As a 用户,
I want 在首页看到观点卡片的信息流，并按生命阶段或主题分类筛选话题,
So that 我可以沉浸式浏览感兴趣的话题观点。

**Acceptance Criteria:**

**Given** 用户访问首页
**When** 页面加载
**Then** 移动端显示单列全宽卡片流，桌面端（≥ lg）显示双列瀑布流（max-width 1280px）
**And** 首屏使用 SkeletonLoader 加载，首屏加载后卡片渐进式展示

**Given** 信息流中有多个话题的卡片
**When** 卡片按三拍节奏编排
**Then** 同话题首张必为强调型，颠覆点用引用型，跨话题连续两张不同类型

**Given** 首页顶部显示话题分类 Tab
**When** 用户点击某个分类（如"婚恋家庭"/"职场发展"）
**Then** 信息流筛选为该分类下的话题卡片，切换过程流畅

**Given** 用户滚动信息流
**When** 接近底部
**Then** 自动加载下一批卡片（无限滚动），移动端滚动保持 60fps 流畅

**Given** 话题库从 50 扩展至 10000+
**When** 用户浏览信息流
**Then** 分页加载策略确保浏览性能无明显退化

**Given** 用户未注册或未登录
**When** 浏览信息流
**Then** 可无限浏览卡片，无注册弹窗拦截
**And** 浏览 5+ 卡片后底部出现软浮条提示注册（可关闭）

### Story 2.5: 同话题多视角浏览与维度进度

As a 用户,
I want 在同一话题下浏览多个不同立场的观点卡片，并看到我的浏览进度,
So that 我能逐步拼出话题的全貌，体验认知惊喜。

**Acceptance Criteria:**

**Given** 用户正在浏览某话题的卡片
**When** 水平左滑（移动端）或点击切换（桌面端）
**Then** 展示同话题下一个不同立场的视角卡片

**Given** 用户浏览到同话题第 3 张卡片
**When** 达到 Aha Moment 阈值
**Then** 底部浮现维度进度文字（"你已看到 3/6 个维度"）+ 细线进度条
**And** 进度条变为 Accent 金色 + 微光脉冲 600ms

**Given** 用户浏览完某话题全部维度
**When** 最后一张卡片展示后
**Then** 显示翡翠绿成就提示（"你已看到全貌"）+ 关联话题推荐入口

**Given** 用户在某话题未浏览完就离开
**When** 离开时
**Then** 显示提示（"还有 N 个维度没看到"）

**Given** 用户在某张卡片停留超过 2 秒
**When** 停留时间达标
**Then** 系统预取该话题下其他立场的卡片数据，确保滑动到下一张时零等待

### Story 2.6: 话题关联关系与路径浏览

As a 用户,
I want 看到当前话题与其他话题之间的关联关系，并沿关联路径探索新话题,
So that 我的认知可以自然延伸到相关领域。

**Acceptance Criteria:**

**Given** 当前话题有关联话题（如"彩礼"关联"原生家庭""婚前同居"）
**When** 用户查看话题详情
**Then** 显示关联话题列表，附简短推荐语（如"如果你对'彩礼'感兴趣，'原生家庭'可能会颠覆你另一个认知"）

**Given** 用户点击某个关联话题
**When** 导航到关联话题
**Then** 页面过渡流畅（淡入淡出 150ms），直接进入该话题的卡片浏览

**Given** 话题关联关系数据存在
**When** API 返回关联话题
**Then** 关联话题按相关度排序，每个关联项包含话题标题、分类、卡片数量预览

### Story 2.7: 话题详情页与 SEO 着陆页

As a 用户（含搜索引擎爬虫）,
I want 通过独立 URL 直接访问话题详情页或单张卡片页面，页面内容被搜索引擎收录,
So that 外部用户可以零拦截直达内容，搜索引擎可以发现 WeNexus 的内容。

**Acceptance Criteria:**

**Given** 搜索引擎爬虫或用户通过外部链接访问话题详情页 URL
**When** 页面服务端渲染
**Then** HTML 包含完整的话题概览 + 多视角卡片组 + 圆桌入口
**And** 包含 JSON-LD 结构化数据标记
**And** 首屏加载时间 < 2s

**Given** 用户通过外部链接访问单卡片着陆页 URL
**When** 页面加载
**Then** 显示完整的观点卡片内容 + "看看其他专家怎么说" CTA 按钮
**And** 无需登录即可查看全部内容

**Given** 话题详情页在桌面端
**When** 页面渲染
**Then** 布局为主内容区 + 右侧话题导航（维度列表、关联话题）

**Given** 话题详情页在移动端
**When** 页面渲染
**Then** 单列布局，话题导航折叠为顶部 Tab 或底部 Sheet

### Story 2.8: 卡片分享与品牌水印图生成

As a 用户,
I want 把观点卡片分享为带品牌水印的图片，适配不同社交平台尺寸,
So that 我可以在微信、小红书等平台分享有趣的观点。

**Acceptance Criteria:**

**Given** 用户点击卡片底部的分享按钮
**When** 选择分享格式
**Then** 可选择：小红书 3:4（1080x1440px）、朋友圈 1:1（1080x1080px）、微信对话 5:4（1200x960px）

**Given** 用户确认分享格式
**When** 系统生成分享图
**Then** 后端通过 Playwright 截图渲染带品牌水印的图片
**And** 水印位于右下角距边缘 24px，包含 WeNexus logo + "扫码看更多视角"，透明度 85%
**And** 含导流短链/二维码，可追踪来源平台

**Given** 用户点击分享按钮
**When** 分享图生成中
**Then** 按钮显示 loading 状态 + 进度提示，UI 乐观更新（先显示成功态）
**And** 生成失败时回滚 UI + Toast "生成失败，请重试"

**Given** 分享图生成完成
**When** 用户查看结果
**Then** 可下载图片或直接调用系统分享功能

### Story 2.9: 圆桌讨论预览与过渡入口

As a 免费用户,
I want 在卡片浏览中预览圆桌讨论的摘要或精彩片段，感兴趣时可以进入圆桌,
So that 我能自然地从浏览过渡到更深度的讨论，而非被突然挡住。

**Acceptance Criteria:**

**Given** 免费用户浏览卡片时点击"进入圆桌"
**When** 触发圆桌过渡
**Then** 底部上滑面板展示圆桌预览：话题摘要 + 参与专家列表 + 2-3 条精彩片段
**And** 面板展示时后台预建立 WebSocket 连接，给系统缓冲时间

**Given** 免费用户查看圆桌预览
**When** 预览面板中显示付费提示
**Then** 提示文案为"自然升级邀请"风格（如"解锁完整讨论，用理解去行动"），非"你被挡在门外"
**And** 显示 Primary CTA（Accent 金色）引导付费

**Given** 付费用户点击"进入圆桌"
**When** 确认后
**Then** 预览面板全屏展开，进入实时圆桌讨论页面
**And** 移动端 Tab 栏下滑隐藏 150ms → ControlPanel 上滑出现 150ms

---

## Epic 3: 用户认证与身份管理

用户可以注册和登录 WeNexus，免费用户可以无限浏览观点卡片信息流。

### Story 3.1: 用户注册与登录

As a 新用户,
I want 通过邮箱注册和登录 WeNexus,
So that 我可以拥有个人账户来保存浏览记录和使用更多功能。

**Acceptance Criteria:**

**Given** 用户访问注册页面
**When** 提交邮箱和密码
**Then** 账户创建成功，`auth_users` 表写入记录，默认角色为 `free_user`
**And** 自动登录并跳转到之前浏览的页面

**Given** 已注册用户访问登录页面
**When** 提交正确的邮箱和密码
**Then** 登录成功，创建 Session，设置 Session cookie

**Given** 用户提交错误密码
**When** 登录验证失败
**Then** 返回错误提示"邮箱或密码错误"，不泄露具体哪项错误

**Given** 用户正在浏览内容（未登录）
**When** 注册流程出现
**Then** 注册仅在用户产生"保存/延续"需求时出现（首次收藏等），永不在内容消费时弹出拦截

### Story 3.2: RBAC 角色权限、可配置权益与 Session 鉴权

As a 系统,
I want 基于三层用户模型（anonymous/free_user/premium_user + admin）控制功能访问权限，各层权益通过配置驱动，通过 Session cookie 实现前后端鉴权,
So that 不同层级用户只能访问授权范围内的功能，且权益可动态调整。

**Acceptance Criteria:**

**Given** 系统定义三层用户模型
**When** 权益配置加载
**Then** 三层用户各有独立的权益配置：anonymous（未登录）、free_user（免费）、premium_user（付费）
**And** 权益配置项包含：可浏览内容范围、圆桌讨论次数/天、产出物生成次数/天、搜索次数/天、收藏数量上限等
**And** 权益配置通过数据库或配置文件管理，不硬编码

**Given** 管理员修改某层级权益配置（如 free_user 圆桌讨论次数从 0 改为 1）
**When** 配置生效
**Then** 该层级所有用户立即获得新权益额度，无需重新部署

**Given** better-auth Session 已扩展角色字段
**When** 用户登录
**Then** Session 中包含用户角色信息（free_user/premium_user/admin）

**Given** 前端通过 Next.js rewrite 代理请求到 `/api/py/v1/*`
**When** 请求发送
**Then** Session cookie 自动携带，后端通过 `get_current_user` 解析用户身份和角色

**Given** 未登录用户访问需要登录的 API
**When** 后端调用 `get_current_user`
**Then** 返回 401 未授权响应

**Given** 公开页面（信息流、卡片详情）的 API
**When** 后端调用 `get_optional_user`
**Then** 未登录时返回 null（不阻塞），已登录时返回用户信息

**Given** 功能调用时需要检查权益额度
**When** 调用 `check_entitlement(user, feature)`
**Then** 根据用户层级查询对应权益配置，返回是否允许 + 剩余额度

### Story 3.3: 免费用户无限浏览与注册引导

As a 免费用户（含未登录访客）,
I want 无限浏览观点卡片信息流，在合适时机收到温和的注册引导,
So that 我不被内容消费打断，但在产生需求时知道可以注册获得更多。

**Acceptance Criteria:**

**Given** 未登录用户浏览信息流
**When** 持续浏览卡片
**Then** 无任何阅读限制，卡片无限加载

**Given** 未登录用户浏览超过 5 张卡片
**When** 达到引导阈值
**Then** 底部出现软浮条"注册 WeNexus，保存你的浏览记录"
**And** 浮条可关闭，关闭后本次会话不再出现

**Given** 未登录用户首次尝试收藏卡片
**When** 点击收藏按钮
**Then** 弹出注册引导（非强制拦截），提示"注册后即可收藏"
**And** 用户可关闭继续浏览

**Given** free_user 角色的已登录用户
**When** 浏览信息流
**Then** 无任何浏览限制，与未登录用户体验一致，但收藏等功能可用

---

## Epic 4: 圆桌讨论交互体验

付费用户可以参与 AI 专家圆桌讨论，在挂机围观和接管主持模式间自由切换，体验实时流式辩论。

### Story 4.1: WebSocket 通信层与降级策略

As a 系统,
I want 建立可靠的 WebSocket 实时通信层，网络异常时自动降级为 HTTP polling,
So that 圆桌讨论的实时性有保障，弱网环境下也能正常使用。

**Acceptance Criteria:**

**Given** 用户进入圆桌讨论页面
**When** 页面加载
**Then** 自动建立 WebSocket 连接到 `/ws/roundtable/{session_id}`
**And** 连接成功后发送 `join` 消息，服务端确认后进入讨论

**Given** WebSocket 连接意外断开
**When** 检测到连接丢失
**Then** 自动执行指数退避重连（1s → 2s → 4s → 8s → 16s，最大 30s）
**And** 重连期间 UI 显示"连接中..."状态，已收到的消息不丢失

**Given** WebSocket 重连连续失败 5 次
**When** 触发降级策略
**Then** 自动切换到 HTTP long-polling 模式（每 2s 轮询一次）
**And** 用户感知到的延迟增加但功能不中断
**And** 底部出现提示"网络不稳定，已切换到兼容模式"

**Given** WebSocket 恢复可用
**When** 检测到网络恢复
**Then** 自动从 polling 切换回 WebSocket，无需用户刷新

### Story 4.2: 圆桌讨论创建与专家入座

As a 付费用户,
I want 选择一个话题后快速创建圆桌讨论，看到 AI 专家依次入座,
So that 我感受到讨论的仪式感和期待感。

**Acceptance Criteria:**

**Given** 付费用户在话题详情页或卡片页
**When** 点击"开始圆桌讨论"
**Then** 两步创建流程：Step 1 确认话题 → Step 2 选择讨论维度（可跳过，默认全部）
**And** 创建请求发送后进入圆桌讨论页面

**Given** 圆桌讨论创建成功
**When** 后端分配专家组合
**Then** LangGraph Interactive 模式初始化讨论 graph，选择 3-5 位专家

**Given** 讨论页面加载
**When** 专家依次入座
**Then** 专家头像带入座动画：淡入 + 微上移 200ms，每位间隔 300ms
**And** 每位专家头像外圈显示立场色彩（如红=激进、蓝=保守、绿=中立）
**And** 全部入座后显示"讨论即将开始..."，1s 后自动开始

**Given** 专家入座完成
**When** 进入讨论
**Then** 默认进入挂机围观模式

### Story 4.3: 挂机围观模式与流式输出

As a 付费用户,
I want 在围观模式下观看 AI 专家自动讨论，发言以流式逐字显示,
So that 我可以像观看一场真实辩论一样沉浸其中。

**Acceptance Criteria:**

**Given** 圆桌讨论处于围观模式
**When** AI 专家发言
**Then** 发言通过 WebSocket 流式推送，前端逐字渲染（typing effect）
**And** 首 token 延迟 < 2s，单条发言全程 < 5s

**Given** 专家发言中
**When** 流式文本到达前端
**Then** 对话线程（RoundtableThread）中显示：专家头像 + 名称 + 立场标签 + 流式文本
**And** 当前发言专家头像有发光呼吸动画

**Given** 多位专家轮流发言
**When** 一位专家发言结束，下一位开始
**Then** 发言间隔动态调整（基础 1.5s，连续同立场 +0.5s，立场切换 +1s）
**And** 间隔期显示下一位专家的"正在思考..."提示

**Given** 讨论持续进行
**When** 对话线程超出可视区域
**Then** 自动滚动到最新发言，用户手动上滑查看历史时暂停自动滚动
**And** 底部出现"回到最新"浮动按钮

### Story 4.4: 共识形成可视化

As a 付费用户,
I want 在讨论过程中看到专家们的共识逐渐形成或分歧加深,
So that 我能直观感受到讨论的进展和价值。

**Acceptance Criteria:**

**Given** 圆桌讨论进行中
**When** 每轮发言结束后
**Then** ConsensusGauge 组件更新，显示当前共识度百分比（0-100%）
**And** 仪表盘使用渐变色（红→黄→绿）反映共识程度

**Given** 两位以上专家在某个论点上立场趋同
**When** 系统检测到共识信号
**Then** ConsensusGauge 向共识方向移动，附带简短说明（如"3 位专家认同：教育是关键因素"）

**Given** 专家间出现新的分歧点
**When** 系统检测到分歧信号
**Then** ConsensusGauge 显示分歧标记，附带分歧摘要

**Given** 讨论结束
**When** 最终共识评估完成
**Then** 显示共识总结：达成共识的要点 + 仍存分歧的要点 + 各专家最终立场

### Story 4.5: 接管主持模式

As a 付费用户,
I want 随时从围观模式切换为主持模式，向专家提问或引导讨论方向,
So that 我可以深入探讨自己最关心的问题。

**Acceptance Criteria:**

**Given** 用户处于围观模式
**When** 点击 ControlPanel 的"接管主持"按钮
**Then** 模式切换，ControlPanel 展开显示输入框和操作按钮
**And** 当前专家发言完毕后再切换（缓冲机制），不打断正在进行的发言

**Given** 用户处于主持模式
**When** 在输入框中输入问题并发送
**Then** 问题以"主持人"身份出现在对话线程中
**And** AI 专家们依次回应用户的问题，回应内容基于各自人设和之前的讨论上下文

**Given** 用户处于主持模式
**When** 点击"追问 [专家名]"按钮
**Then** 指定该专家优先回应，其他专家随后补充

**Given** 用户处于主持模式
**When** 点击"回到围观"按钮
**Then** 切换回围观模式，AI 专家继续自主讨论
**And** ControlPanel 收起为浮动控制条

**Given** 用户处于主持模式超过 30 秒未输入
**When** 空闲超时
**Then** 提示"需要继续主持吗？"，不自动退出

### Story 4.6: 多轮对话与上下文记忆

As a 付费用户,
I want 圆桌讨论支持多轮深入对话，专家记住之前的讨论内容,
So that 讨论越深入越有价值，不会出现重复论点。

**Acceptance Criteria:**

**Given** 圆桌讨论已进行 3+ 轮
**When** 专家继续发言
**Then** 发言内容引用或回应之前的论点（如"正如苏格拉底刚才提到的..."）
**And** 不重复已经充分讨论过的论点

**Given** LangGraph Interactive graph 维护讨论状态
**When** 每轮发言生成
**Then** 将完整对话历史作为上下文传入 LLM，包含所有专家发言和用户输入

**Given** 讨论上下文超过 LLM 上下文窗口限制
**When** 需要截断上下文
**Then** 保留讨论摘要 + 最近 N 轮完整对话，不丢失关键论点

**Given** 用户在主持模式提出新角度
**When** 专家回应后回到围观模式
**Then** 后续自主讨论融合用户提出的新角度，不忽略用户输入

### Story 4.7: 讨论频率限制

As a 系统,
I want 基于权益配置对各层级用户的圆桌讨论次数进行限制,
So that 系统资源可控，同时用户有足够的使用额度。

**Acceptance Criteria:**

**Given** 用户查看讨论额度
**When** 调用权益查询
**Then** 从权益配置中读取该用户层级的每日讨论上限，显示已用次数和剩余次数

**Given** 用户今日讨论次数未达上限
**When** 发起新讨论
**Then** 正常创建，已用次数 +1

**Given** 用户今日讨论次数达到上限
**When** 尝试发起新讨论
**Then** 友好提示"今日讨论次数已用完，明天再来探索新话题吧"
**And** 不阻止浏览已有讨论记录

**Given** 管理员修改某层级的讨论次数配额
**When** 配置生效
**Then** 该层级用户的限制立即更新，无需重新部署

**Given** 日期切换（0:00）
**When** 新的一天开始
**Then** 用户讨论次数重置

---

## Epic 5: 产出物生成与获取

付费用户可以基于圆桌讨论内容指定产出物类型，生成、下载或分享对应格式的产出物。

### Story 5.1: 产出物类型选择与生成

As a 付费用户,
I want 在圆桌讨论结束后选择产出物类型（决策矩阵/观点对比报告/行动建议等），系统自动生成,
So that 我可以把讨论成果转化为实用的文档。

**Acceptance Criteria:**

**Given** 圆桌讨论已完成（或进行到足够轮次）
**When** 用户点击"生成产出物"
**Then** 显示可选产出物类型列表（决策矩阵、观点对比报告、行动建议、讨论摘要）

**Given** 用户选择产出物类型
**When** 确认生成
**Then** 后端通过 LangGraph 编排，基于讨论完整上下文生成对应格式的产出物
**And** 生成过程中显示进度提示（"正在整理讨论要点..."）

**Given** 产出物生成完成
**When** 内容就绪
**Then** 产出物以结构化格式展示在页面中（max-width 720px，阅读优化排版）
**And** 生成次数从用户权益配额中扣减

**Given** 用户权益配额中产出物生成次数已用完
**When** 尝试生成
**Then** 提示剩余额度不足，引导升级或等待配额刷新

### Story 5.2: 产出物导出与分享

As a 付费用户,
I want 将产出物导出为图片或 Markdown 格式，或分享产出物链接,
So that 我可以离线使用或分享给他人。

**Acceptance Criteria:**

**Given** 产出物已生成
**When** 用户点击"导出"
**Then** 可选择图片或 Markdown 格式下载
**And** 图片格式保留排版和品牌水印

**Given** 产出物已生成
**When** 用户点击"分享"
**Then** 生成产出物的唯一分享链接
**And** 分享链接可设置为公开（任何人可看）或私密（需登录）

**Given** 外部用户通过分享链接访问
**When** 页面加载
**Then** 以只读模式展示产出物内容，底部显示 WeNexus 品牌引导

### Story 5.3: 产出物历史管理

As a 付费用户,
I want 查看和管理我所有生成过的产出物,
So that 我可以随时回顾和复用之前的讨论成果。

**Acceptance Criteria:**

**Given** 用户进入"我的产出物"页面
**When** 页面加载
**Then** 按时间倒序展示所有产出物列表（标题、类型、来源话题、生成时间）

**Given** 用户点击某个产出物
**When** 进入详情
**Then** 显示完整产出物内容，可重新导出或分享

**Given** 用户删除某个产出物
**When** 确认删除
**Then** 产出物标记为已删除，不再在列表中显示

---

## Epic 6: 内容搜索与发现

用户可以通过自然语言搜索话题和卡片，进行多轮追问，从搜索结果进入圆桌，首页获得话题推荐。

### Story 6.1: 自然语言搜索话题与卡片

As a 用户,
I want 用自然语言搜索话题和观点卡片（如"关于彩礼的不同看法"）,
So that 我可以快速找到感兴趣的内容。

**Acceptance Criteria:**

**Given** 用户在搜索栏输入自然语言查询
**When** 提交搜索
**Then** 返回匹配的话题和卡片列表，按相关度排序
**And** 搜索响应时间 < 3s

**Given** 搜索结果列表
**When** 用户浏览结果
**Then** 每条结果显示：话题标题、匹配维度/视角摘要、相关专家头像

**Given** 移动端搜索栏
**When** 点击搜索图标
**Then** 搜索栏展开为全宽输入框 + 历史搜索记录

**Given** 搜索无结果
**When** 没有匹配内容
**Then** 不显示空白页面，触发 AgentResponder（Story 6.3）

### Story 6.2: 多轮追问对话式搜索

As a 用户,
I want 在搜索结果基础上继续追问，逐步缩小或拓展搜索范围,
So that 我可以像对话一样找到精确的内容。

**Acceptance Criteria:**

**Given** 用户已完成一次搜索
**When** 在搜索结果页输入追问（如"有没有从经济学角度分析的"）
**Then** 系统基于上一轮搜索上下文 + 新问题重新搜索
**And** 结果更新，保留对话历史（可回溯之前的搜索）

**Given** 多轮追问进行到第 3 轮
**When** 用户继续追问
**Then** 上下文窗口保留最近 5 轮对话，确保搜索意图连贯

**Given** 用户点击"重新搜索"
**When** 清除对话上下文
**Then** 回到初始搜索状态，对话历史清空

### Story 6.3: AgentResponder 空状态智能应答

As a 用户,
I want 当搜索无结果时，一位 AI 专家直接回答我的问题,
So that 我的问题不会落空，始终能获得有价值的回应。

**Acceptance Criteria:**

**Given** 用户搜索无结果
**When** 系统检测到空结果
**Then** 自动触发 AgentResponder：随机选择一位内置专家，以其人设风格流式回答用户问题

**Given** AgentResponder 开始回答
**When** 流式文本输出
**Then** 显示专家头像 + 名称 + "正在为你解答..."
**And** 回答以该专家的说话风格和知识领域为基础

**Given** AgentResponder 回答完毕
**When** 回答展示完成
**Then** 底部显示"创建圆桌讨论，听听更多专家怎么说" CTA
**And** 显示相关话题推荐（如果有近似话题）

### Story 6.4: 搜索结果直达圆桌讨论

As a 付费用户,
I want 从搜索结果直接发起该话题的圆桌讨论,
So that 找到感兴趣的话题后可以一键深入。

**Acceptance Criteria:**

**Given** 搜索结果列表中某个话题
**When** 用户点击"开始圆桌"按钮
**Then** 跳转到圆桌创建流程（Story 4.2），话题自动填充

**Given** 免费用户点击"开始圆桌"
**When** 触发付费检查
**Then** 显示圆桌预览 + 付费引导（Story 2.9 的逻辑）

### Story 6.5: 首页话题推荐与用户行为采集

As a 用户,
I want 首页看到个性化的话题推荐,
So that 不用搜索也能发现感兴趣的内容。

**Acceptance Criteria:**

**Given** 用户访问首页
**When** 推荐算法执行
**Then** MVP 阶段基于热度（浏览量、讨论数）推荐话题
**And** 已登录用户后续迭代可基于浏览历史个性化

**Given** 用户浏览卡片、点击话题、发起搜索
**When** 用户行为发生
**Then** 采集行为事件（页面浏览、卡片停留时长、搜索关键词、点击话题）
**And** 事件写入行为日志表，供后续推荐算法使用

**Given** 行为数据采集
**When** 数据写入
**Then** 仅记录行为类型和对象 ID，不记录敏感个人信息
**And** 未登录用户使用匿名 session ID 关联行为

---

## Epic 7: 外部分发与导流

AI Agent 可以自动在外部平台发布观点卡片内容，管理员可以通过监控面板查看分发状态并处理异常。

### Story 7.1: 分发平台适配器框架

As a 系统,
I want 一个可扩展的平台适配器框架，每个外部平台对应一个适配器实现,
So that 新增平台只需新增适配器，不改核心逻辑。

**Acceptance Criteria:**

**Given** 平台适配器接口已定义
**When** 新增一个平台适配器（如微博、小红书、知乎）
**Then** 只需实现统一接口（format_content / publish / check_status）
**And** 核心分发逻辑无需修改

**Given** 适配器实现了内容格式转换
**When** 同一张观点卡片分发到不同平台
**Then** 每个平台收到符合其格式要求的内容（字数限制、图片尺寸、标签格式等）

**Given** 某平台 API 接口变更
**When** 修改对应适配器
**Then** 不影响其他平台的分发

### Story 7.2: 自动分发任务调度

As a 系统,
I want 内容通过验证后自动进入分发队列，按计划调度发布到各平台,
So that 内容分发全自动运转。

**Acceptance Criteria:**

**Given** 内容验证通过并进入分发队列（Story 1.9）
**When** 调度器检查队列
**Then** 按配置的分发策略（平台优先级、发布时间窗口）创建分发子任务

**Given** 分发子任务就绪
**When** 到达计划发布时间
**Then** 调用对应平台适配器执行发布
**And** 记录发布结果（成功/失败/外部平台 ID）

**Given** 分发任务失败
**When** 平台返回错误
**Then** 按重试策略自动重试（最多 3 次，间隔递增）
**And** 超过重试次数标记为 `failed`，进入异常处理

### Story 7.3: 分发内容导流短链与追踪

As a 系统,
I want 每条分发内容包含导流短链，追踪不同平台的流量来源,
So that 可以评估各平台的导流效果。

**Acceptance Criteria:**

**Given** 内容准备分发到某平台
**When** 生成分发内容
**Then** 自动创建唯一导流短链，编码来源平台标识
**And** 短链指向对应的话题详情页或卡片着陆页

**Given** 外部用户点击导流短链
**When** 访问 WeNexus
**Then** 记录来源平台、时间戳、设备信息
**And** 正常展示目标页面内容

**Given** 管理员查看导流数据
**When** 按平台维度查询
**Then** 显示各平台的点击量、跳出率、注册转化率

### Story 7.4: 分发监控面板

As a 管理员,
I want 通过监控面板查看所有平台的分发状态，处理异常任务,
So that 我可以确保内容分发正常运转。

**Acceptance Criteria:**

**Given** 管理员访问分发监控面板
**When** 页面加载
**Then** 显示分发总览：各平台待发布/已发布/失败数量，今日分发趋势

**Given** 管理员查看失败任务列表
**When** 点击某条失败任务
**Then** 显示失败详情：目标平台、失败原因、重试次数、原始内容预览

**Given** 管理员对失败任务操作
**When** 选择"重试"
**Then** 任务重新加入分发队列

**Given** 管理员对失败任务操作
**When** 选择"跳过"
**Then** 任务标记为 `skipped`，不再重试

### Story 7.5: 分发内容审核与管理

As a 管理员,
I want 在内容分发前预览和审核，可以暂停/恢复特定平台的分发,
So that 我可以控制对外发布的内容质量。

**Acceptance Criteria:**

**Given** 内容进入分发队列
**When** 管理员开启了"发布前审核"模式
**Then** 内容进入待审核状态，管理员审核通过后才执行分发

**Given** 管理员在监控面板
**When** 切换某平台的分发开关为"暂停"
**Then** 该平台所有待执行的分发任务暂停，已发布的不受影响

**Given** 管理员恢复某平台分发
**When** 切换为"启用"
**Then** 暂停期间积压的任务按顺序恢复执行

---

## Epic 8: 会员付费与积分体系

用户可以付费购买会员或积分，系统支持积分获取、消耗和查询。

### Story 8.1: 会员套餐与付费购买

As a 用户,
I want 查看会员套餐并完成付费购买,
So that 我可以解锁圆桌讨论、产出物生成等付费功能。

**Acceptance Criteria:**

**Given** 用户访问会员页面
**When** 页面加载
**Then** 显示会员套餐列表（如月度/季度/年度），每个套餐标明价格和包含权益

**Given** 用户选择套餐并确认支付
**When** 支付流程完成
**Then** 用户角色从 `free_user` 升级为 `premium_user`
**And** 权益配额按套餐配置初始化
**And** 支付记录写入交易表

**Given** 付费会员到期
**When** 到期时间到达
**Then** 用户角色降级为 `free_user`
**And** 付费功能不可用，但已有数据（产出物、讨论记录）保留可查看

**Given** 支付过程中出现异常
**When** 第三方支付回调失败
**Then** 事务回滚，用户角色不变
**And** 记录异常日志，支持人工核实

### Story 8.2: 积分获取与消耗

As a 用户,
I want 通过日常行为获取积分，使用积分消费付费功能,
So that 我可以不直接付费也能体验部分付费功能。

**Acceptance Criteria:**

**Given** 用户完成可获积分行为（如每日登录、浏览 10 张卡片、分享卡片、完成注册等）
**When** 行为达成
**Then** 积分自动发放到用户账户，积分记录包含来源和时间

**Given** 用户使用积分兑换功能（如 1 次圆桌讨论）
**When** 确认消耗
**Then** 扣减对应积分，解锁对应功能一次
**And** 积分不足时提示余额不够

**Given** 积分获取和消耗规则
**When** 管理员调整规则（如修改每日登录积分数量）
**Then** 通过权益配置生效，无需修改代码

### Story 8.3: 积分账户与交易记录查询

As a 用户,
I want 查看我的积分余额和历史交易记录,
So that 我清楚积分的来源和去向。

**Acceptance Criteria:**

**Given** 用户访问"我的积分"页面
**When** 页面加载
**Then** 显示当前积分余额 + 近期变动趋势

**Given** 用户查看积分明细
**When** 展开交易记录
**Then** 按时间倒序显示每条记录：类型（获取/消耗）、数量、来源/用途、时间
**And** 支持按月份筛选

### Story 8.4: 付费墙自然升级体验

As a 免费用户,
I want 在触碰付费功能时收到自然的升级邀请而非硬性拦截,
So that 我感受到的是"被邀请"而非"被挡住"。

**Acceptance Criteria:**

**Given** 免费用户触碰付费功能（圆桌讨论、产出物生成等）
**When** 权限检查不通过
**Then** 显示自然升级邀请面板：功能预览 + 价值描述 + Accent 金色 CTA
**And** 文案风格为邀请式（"解锁完整讨论"），非拒绝式（"你没有权限"）

**Given** 升级邀请面板显示
**When** 用户选择关闭
**Then** 面板关闭，用户继续使用免费功能，本次会话内同功能不再重复弹出

**Given** 用户选择"用积分体验一次"
**When** 积分充足
**Then** 扣减积分，临时解锁该功能一次
