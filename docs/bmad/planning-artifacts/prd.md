---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success]
classification:
  projectType: web_app
  domain: ai-powered-content-platform
  complexity: medium-high
  projectContext: brownfield
inputDocuments:
  - docs/bmad/planning-artifacts/product-brief-wenexus-2026-03-14.md
  - docs/bmad/project-context.md
  - docs/prd/aigc-architecture-vision.md
  - docs/prd/domain-architecture.md
  - docs/prd/user-story-v4.md
  - docs/design/personas/user-personas.md
  - docs/theory/如何拆解话题.md
  - docs/theory/话题的持久性.md
  - docs/theory/knowledge-graph-extraction.md
  - docs/theory/investor-qa.md
  - docs/theory/严肃性和深度是解压的最好方式.md
  - docs/theory/各说各话的基础，是因为存在着自说自话的必要.md
  - docs/theory/复杂问题不存在简单答案.md
  - docs/theory/历史是任人打扮的小姑娘.md
workflowType: 'prd'
documentCounts:
  briefs: 1
  research: 0
  projectDocs: 5
  projectContext: 1
  theory: 7
---

# Product Requirements Document - wenexus

**Author:** xiaohui
**Date:** 2026-03-15

## Executive Summary

WeNexus 是一个 AI 驱动的多元视角内容平台，围绕人类社会的经典争议问题（彩礼、内卷、AI 取代人类、阶层固化等），通过结构化多视角呈现，让用户自己拼出事情的全貌。

**核心问题**：现有内容平台（知乎、微博、ChatGPT）在争议话题上只提供局部视角——单一作者的"全面解析"、刻意中立的折中答案、或算法驱动的极化内容。用户看到的是"我方的真相"，且多数人不知道自己只看到了局部。

**产品架构**：双层内容体系。表层是小红书式观点卡片信息流，每张卡片呈现一个专家视角，设计标准是"一句让你停下来的话 + 一个你没想到的角度"；深层是 AI 专家圆桌讨论，多位 AI 专家进行线程式辩论，用户可挂机围观或接管主持，讨论成果一键转化为文章、决策清单等产出物。

**目标用户**：任何面对争议话题的普通人（覆盖全生命周期议题）。核心驱动力是自利——"我不想被蒙在鼓里"。进阶用户进入圆桌讨论，用理解去行动。

**商业模式**：会员积分制。免费用户浏览观点卡片，付费会员使用圆桌讨论和产出物生成。AI Agent 在外部平台自动运营内容导流，实现低成本冷启动。

**技术栈**：Next.js 15 + React 19 + TailwindCSS 4 + FastAPI + Drizzle ORM + LangChain/LangGraph，部署于 Cloudflare Workers。

### What Makes This Special

1. **全貌呈现，非单一解析**：不是一个人讲"来龙去脉"，而是让不同立场的专家各自讲自己看到的部分。比任何单一视角的"全面解析"都更接近真相。
2. **经典问题，持久资产**：聚焦不会过期的争议话题，每条内容都是长期资产。AI 批量生产能力使 50 个种子话题可扩展至 10000+。
3. **认知惊喜驱动，非情绪刺激**：制造"啊，原来如此"的好奇心，而非制造愤怒。内容消费体验，认知提升是副产品。
4. **AIGC 全链路**：AI 生成内容 → AI 渲染卡片（JSX 直出）→ AI Agent 分发 → AI 圆桌讨论，几乎零人力成本运营。

## Project Classification

- **项目类型**：Web App（Next.js SPA，响应式设计）
- **领域**：AI 驱动内容平台（多元视角认知升级）
- **复杂度**：中高（AI 内容生产引擎 + 多 Agent 圆桌系统 + AIGC 渲染 + 外部平台分发，无强合规要求）
- **项目状态**：Brownfield（已有技术栈、领域架构、32 个用户故事）

---

## Success Criteria

### User Success

**北极星指标：认知惊喜率（Cognitive Surprise Rate）**

- 定义：用户浏览观点卡片后产生"想看更多"行为的比例
- 度量：点击进入话题详情 / 浏览同话题下一张卡片的转化率
- 目标：> 40%（对比小红书平均内容互动率约 5-10%，WeNexus 因内容精准命中认知盲区应显著高于常规内容）

**Aha Moment**：用户首次在同一话题下浏览 3+ 个不同立场的观点卡片。

**用户成功阶梯：**

| 阶段 | 用户行为 | 成功信号 |
|------|---------|---------|
| 触达 | 在外部平台看到观点卡片 | 点击率 > 2% |
| 激活 | 进入 WeNexus 浏览同话题多视角 | 单话题浏览 3+ 卡片率 > 30% |
| 留存 | 次日/次周回访 | 次周留存 > 20% |
| 深度 | 进入圆桌讨论 | 卡片→圆桌转化率 > 5% |
| 付费 | 购买会员 | 注册→付费转化率 > 2% |

### Business Success

**Phase 1（0-3 个月）：技术验证**

| 维度 | 成功标准 |
|------|---------|
| 内容生产 | 50 个话题 AI 生成，人工审核通过率 > 80% |
| 卡片渲染 | AIGC 直出 JSX 卡片，渲染成功率 > 95% |
| 圆桌讨论 | AI 专家多角度辩论可用，单次讨论产出 5+ 有效观点 |
| 外部分发 | 至少 1 个平台（小红书/公众号）AI Agent 稳定运营 |
| 回流链路 | 外部平台→WeNexus 导流技术链路跑通 |

**Phase 2（3-12 个月）：增长验证**

| 维度 | 成功标准 |
|------|---------|
| 内容规模 | 话题库扩展至 10000+ |
| 用户增长 | 月增长率稳定正向 |
| 留存 | 次周留存 > 20% |
| 付费转化 | 免费→付费会员转化率可观测且稳定 |
| 分发矩阵 | 3+ 外部平台 Agent 同时运营 |

### Technical Success

| 维度 | 标准 |
|------|------|
| 内容生产吞吐 | 离线批量：100+ 话题/天；在线增量：单话题 < 30s |
| 页面性能 | 观点卡片首屏加载 < 2s（Cloudflare Workers 边缘部署） |
| 圆桌响应 | AI 专家单轮回复 < 5s，全程讨论流畅无明显等待 |
| 系统可用性 | 99.5% |
| 卡片渲染 | AIGC JSX 渲染成功率 > 95%，跨浏览器兼容 |

### Measurable Outcomes

**3 个月里程碑（技术验证通过）：**

- 50 个话题上线，内容质量达标
- 至少 1 个外部平台持续产出内容
- "浏览卡片→圆桌讨论→生成产出物"全链路可用
- 付费系统上线并可交易

**12 个月里程碑（商业模型验证）：**

- 10000+ 话题在线
- 付费会员数持续增长
- 获客成本（通过 Agent 分发）显著低于传统投放

---

## Product Scope

### MVP - Minimum Viable Product

1. **AI 内容生产引擎**：话题拆解 → 专家视角生成 → 观点卡片渲染（AIGC 直出 JSX）。50 个话题人工审核，验证质量后批量扩展。
2. **观点卡片信息流**：话题维度的多视角卡片浏览，分享功能（自带品牌水印）。
3. **AI 专家圆桌讨论**：求真者事实打底 + 多专家线程辩论 + 挂机/主持模式 + 产出物生成。
4. **外部平台 Agent 分发**：至少 1 个平台 AI Agent 自动运营，导流回 WeNexus。
5. **会员付费系统**：免费（卡片浏览）+ 付费（圆桌 + 产出物），会员积分制。

**MVP 不实现但接口预留（架构完备原则）：**

> **核心原则：MVP 阶段不做的功能，接口需要留好，实现可以简单，架构一样完备。**

| 功能 | MVP 状态 | 接口预留 |
|------|---------|---------|
| 用户社交功能 | 不实现 | 用户关系模型、关注/粉丝 API 接口预留 |
| 评论系统 | 不实现 | 内容互动数据模型、评论 API 接口预留 |
| 内容创作者工具 | 不实现 | 创作者角色权限、内容生产 API 接口预留 |
| 多语言内容 | 不实现 | i18n 内容模型、locale 路由已有（next-intl） |
| 个性化推荐 | 不实现 | 用户行为埋点、推荐 API 接口预留 |

### Growth Features (Post-MVP)

- 多平台 Agent 矩阵分发（小红书、微博、公众号、B站等）
- 话题库扩展至 10000+（AI 批量离线生产 + 增量在线生成）
- 个性化推荐算法（基于用户浏览行为埋点）
- 多语言内容生产（服务全球中文用户）
- 付费会员体系优化（积分、等级、权益）

### Vision (Future)

- **全球认知升级信息中心**：多语言覆盖，成为争议话题"看全貌"的第一选择
- **内容创作者生态**：开放多余产能和工具给创作者
- **Nexus 人社区**：从内容平台进化为认知共同体，线上认知到线下连接
- **全球人类认知升级的基础设施**
