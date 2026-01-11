# BMAD 自主开发最佳实践

## 概述

BMAD (Breakthrough Method of Agile AI Driven Development) 提供了一套完整的 AI 驱动开发框架,通过专业化的 Agent 和工作流实现高效的软件开发。本文档介绍如何利用 BMAD 的特性实现更自主、更高效的开发流程。

## BMAD vs Ralph: 核心区别

| 特性 | Ralph for Claude Code | BMAD Method |
|------|----------------------|-------------|
| **核心机制** | 循环执行引擎 | 工作流编排系统 |
| **执行模式** | 单一 Agent 持续循环 | 多 Agent 分阶段协作 |
| **任务追踪** | 检测完成信号和测试循环 | 状态文件追踪 (workflow-status.yaml, sprint-status.yaml) |
| **适用场景** | 单一目标的持续优化 | 完整软件生命周期管理 |
| **质量保证** | 断路器模式 | 门禁检查 (Gate Check) + 代码审查工作流 |

## BMAD 自主开发的核心原则

### 1. 工作流链式执行

BMAD 的工作流天然支持链式执行,每个工作流的输出可以作为下一个工作流的输入:

```
Phase 1: brainstorm-project → research → product-brief
         ↓
Phase 2: create-prd → create-ux-design (可选)
         ↓
Phase 3: create-architecture → create-epics-and-stories → implementation-readiness
         ↓
Phase 4: sprint-planning → (create-story → dev-story → code-review) × N → retrospective
```

**最佳实践**:

- 使用 `workflow-status` 自动推荐下一步工作流
- 在每个阶段结束时运行门禁检查确保质量
- 利用 BMAD 的自动发现机制 (自动查找 PRD、Architecture 等文档)

### 2. Agent 专业化分工

与 Ralph 的单一 Agent 循环不同,BMAD 通过专业化 Agent 实现更高质量的输出:

| Agent | 专长领域 | 自主工作能力 |
|-------|---------|-------------|
| **Analyst (Mary)** | 研究和发现 | 高 - 可自主完成市场研究、竞品分析 |
| **PM (John)** | 需求和规划 | 中 - 需要用户输入需求,但可自主生成 PRD 结构 |
| **Architect (Winston)** | 系统架构 | 高 - 基于 PRD 可自主设计架构 |
| **SM (Bob)** | Sprint 管理 | 高 - 可自动管理 Sprint 状态 |
| **DEV (Amelia)** | 代码实现 | 高 - 可完整实现 Story |
| **TEA (Murat)** | 测试架构 | 高 - 可自主设计测试策略并生成测试 |

**自主开发策略**:

- **Phase 1-2**: 需要较多用户输入 (定义需求和愿景)
- **Phase 3**: 可以高度自主 (基于 PRD 自动生成架构)
- **Phase 4**: 几乎完全自主 (基于 Story 自动实现和测试)

### 3. 状态文件驱动的自主执行

BMAD 使用两个核心状态文件:

#### workflow-status.yaml (Phase 1-3)

```yaml
current_phase: 3
completed_workflows:
  - workflow-init
  - create-prd
  - create-architecture
  - create-epics-and-stories
next_recommended: implementation-readiness
```

#### sprint-status.yaml (Phase 4)

```yaml
epics:
  - id: epic-1
    status: in-progress
    stories:
      - id: story-1-1
        status: done
      - id: story-1-2
        status: in-progress
```

**自主化技巧**:

- 每次启动 Agent 时先运行 `workflow-status` 或 `sprint-status`
- 根据状态文件推荐自动选择下一个工作流
- 利用状态追踪实现断点续传

## 适用场景分析

### ✅ BMAD 自主开发强烈推荐场景

#### 1. Phase 3-4 的完整执行

**场景**: PRD 已完成,需要从架构设计到完整实现

**为什么适合 BMAD 自主开发**:

- Architecture → Epics → Stories 的转换可以完全自动化
- Story 实现可以批量自动执行
- 每个 Story 有明确的 AC (Acceptance Criteria)
- 代码审查工作流可自动验证质量

**示例工作流**:

```bash
# Phase 3: 自主架构设计
1. Architect agent: create-architecture (基于 PRD)
2. PM agent: create-epics-and-stories (基于 Architecture)
3. Architect agent: implementation-readiness (质量门禁)

# Phase 4: 自主实现循环
4. SM agent: sprint-planning (初始化 Sprint)
5. 对每个 Story 循环执行:
   - SM: create-story
   - DEV: dev-story
   - TEA: automate (可选)
   - DEV: code-review
6. SM: retrospective (Epic 完成后)
```

**预期时间**:

- 中型项目 (20-30 Stories): 8-16 小时持续执行
- 可以夜间运行,早上审查结果

#### 2. Brownfield 项目文档化

**场景**: 现有代码库缺乏文档,需要生成完整的项目文档

**为什么适合 BMAD 自主开发**:

- `document-project` 工作流可完全自主扫描代码库
- 支持三种扫描级别 (quick/deep/exhaustive)
- 自动生成架构文档、API 契约、数据模型
- 可恢复执行 (中断后可从断点继续)

**示例工作流**:

```bash
# 使用 Analyst agent
1. document-project --scan-level exhaustive
   # 输出: project-documentation-{date}.md

2. 基于文档继续规划新功能
   - create-prd (使用已有文档作为上下文)
   - create-architecture (整合现有架构)
```

**预期时间**:

- 大型代码库: 2-4 小时扫描和文档生成
- 适合周末或夜间运行

#### 3. Quick Flow 快速迭代

**场景**: 小功能或 Bug 修复,需要快速交付

**为什么适合 BMAD 自主开发**:

- `quick-spec` 自动检测技术栈和代码模式
- `quick-dev` 端到端实现无需人工干预
- 适合 1-15 个 Stories 的小型变更

**示例工作流**:

```bash
# 使用 Quick Flow Solo Dev (Barry) agent
1. quick-spec
   # 自动检测: 技术栈、代码模式、测试框架
   # 输出: tech-spec.md + stories

2. quick-dev tech-spec.md
   # 端到端实现所有 Stories

3. code-review
   # 质量验证
```

**预期时间**: 30 分钟 - 3 小时

#### 4. 测试覆盖率提升

**场景**: 需要为现有代码补充测试,提升覆盖率到 80%+

**为什么适合 BMAD 自主开发**:

- TEA 的 `test-design` 可自动分析风险
- `atdd` 和 `automate` 可批量生成测试
- `trace` 工作流可追踪覆盖率并给出门禁决策

**示例工作流**:

```bash
# 使用 TEA agent
1. test-design --mode system
   # 输出: test-design-system.md

2. framework (如果测试框架不完善)
   # 输出: 测试脚手架

3. 对每个 Epic 循环:
   - test-design --mode epic
   - automate
   - test-review
   - trace

4. nfr-assess (最终质量评估)
```

**预期时间**:

- 中型项目: 4-8 小时持续执行

### ❌ BMAD 不推荐自主开发的场景

#### 1. Phase 1-2 的需求定义

**为什么不适合**:

- 需要深度的用户洞察和业务理解
- PRD 需要明确的业务目标和成功指标
- 需求模糊时 AI 容易产生不符合预期的输出

**建议**: Phase 1-2 采用交互式工作流,人工引导需求定义

#### 2. 创新性 UI/UX 设计

**为什么不适合**:

- 需要人类审美和创意判断
- 设计需要多轮迭代和用户反馈
- UX 决策往往涉及主观偏好

**建议**: 使用 UX Designer agent 进行协作式设计,而非完全自主

#### 3. 复杂的架构决策

**为什么不适合**:

- 架构决策需要权衡多个因素 (成本、性能、团队技能等)
- ADR (Architecture Decision Record) 需要考虑长期影响
- 技术选型往往有隐含的组织约束

**建议**: 使用 Architect agent 生成多个方案,人工决策后再继续

## BMAD 自主开发工作流模式

### 模式 1: 夜间开发工作流

**场景**: 利用非工作时间完成 Phase 4 实现

```bash
# 下班前设置
1. 确保 Phase 3 已完成 (PRD + Architecture + Epics)
2. 运行 implementation-readiness 确认无阻塞问题
3. 启动 Sprint Planning

# 夜间自主执行 (可编写脚本)
4. 循环执行直到所有 Stories 完成:
   for each story in backlog:
     - SM: create-story
     - DEV: dev-story
     - TEA: automate (可选)
     - DEV: code-review
     - if review passes:
         mark story as done
       else:
         log issues, continue to next story

# 第二天早上审查
5. 检查 sprint-status.yaml
6. 审查代码变更 (git diff)
7. 手动测试关键路径
8. 处理 code-review 发现的问题
```

**关键点**:

- 使用 Git 分支隔离自主开发的代码
- 设置合理的超时和重试机制
- 记录所有 Agent 输出供事后审查

### 模式 2: 渐进式自主增强

**场景**: 在交互式开发基础上逐步增加自主程度

```bash
# Week 1: 交互式开发建立基准
- 人工引导完成 Phase 1-2
- 人工审查 Architecture
- 人工实现前 2-3 个 Stories

# Week 2: 部分自主化
- 自动生成剩余 Stories (create-story)
- 人工实现 + 自动代码审查
- 自动生成测试 (automate)

# Week 3: 高度自主化
- 完全自动实现新 Stories (dev-story)
- 自动代码审查 + 人工抽查
- 自动测试生成和执行

# Week 4: 完全自主
- 批量自主实现剩余 Stories
- 人工只做最终验收
```

**关键点**:

- 从质量要求较低的 Stories 开始自主化
- 逐步建立信任后扩大自主范围
- 保持人工监督关键质量门禁

### 模式 3: 多 Agent 并行工作流

**场景**: 不同 Epic 可以并行开发

```bash
# Epic 1: 前端功能 (DEV Agent A)
sprint-planning → create-story → dev-story → code-review

# Epic 2: 后端 API (DEV Agent B)
sprint-planning → create-story → dev-story → code-review

# Epic 3: 测试增强 (TEA Agent)
test-design → automate → test-review

# 最终汇总
- 合并所有分支
- 运行 retrospective
- 更新 sprint-status.yaml
```

**关键点**:

- 确保 Epic 之间依赖关系清晰
- 使用不同的 Git 分支避免冲突
- 定期同步和集成

## BMAD 质量保证机制

### 1. 门禁检查 (Gate Check)

BMAD 的 `implementation-readiness` 工作流提供了自动化质量门禁:

```yaml
gate_decision: PASS | CONCERNS | FAIL

assessment:
  prd_completeness: 95%
  architecture_completeness: 90%
  epic_story_alignment: 98%

gaps:
  - type: critical
    description: "Missing security architecture section"
  - type: minor
    description: "Story 2.3 has vague acceptance criteria"
```

**自主化建议**:

- FAIL: 停止自主执行,等待人工修复
- CONCERNS: 继续执行但记录风险
- PASS: 继续自主执行

### 2. 代码审查工作流

DEV agent 的 `code-review` 提供了自动化代码质量检查:

```yaml
review_result: APPROVED | CHANGES_REQUESTED

findings:
  - severity: high
    category: security
    description: "Hardcoded API key in config.js"
  - severity: medium
    category: performance
    description: "N+1 query in UserService"
```

**自主化建议**:

- APPROVED: 标记 Story 为 done
- CHANGES_REQUESTED:
  - 高严重度问题: 停止并通知
  - 中低严重度: 自动修复或记录待办

### 3. 测试覆盖率追踪

TEA 的 `trace` 工作流提供覆盖率追踪和门禁决策:

```yaml
gate_decision: PASS | CONCERNS | FAIL | WAIVED

coverage:
  functional: 85%
  integration: 70%
  e2e: 60%

risks:
  - severity: high
    description: "Payment flow lacks E2E tests"
```

**自主化建议**:

- 设置最低覆盖率阈值 (如 80%)
- 未达到阈值时自动生成补充测试
- 关键路径 (如支付流程) 必须有测试

## BMAD 配置优化

### 1. 全局配置调整

编辑 `_bmad/core/config.yaml`:

```yaml
# 输出目录配置
output_folder: "./_bmad-output"

# Agent 行为配置
communication_language: "chinese"
document_output_language: "chinese"

# 自主开发优化
auto_continue_workflows: true  # 自动继续到下一个推荐工作流
save_intermediate_states: true  # 保存中间状态用于恢复
```

### 2. 模块配置调整

编辑 `_bmad/bmm/config.yaml`:

```yaml
# 规划产物路径
planning_artifacts: "{output_folder}/planning-artifacts"
implementation_artifacts: "{output_folder}/implementation-artifacts"

# Story 实现配置
dev_auto_test: true  # 实现 Story 时自动生成测试
code_review_threshold: "medium"  # 代码审查严格度
```

### 3. Agent 自定义

编辑 `_bmad/_config/agents/bmm-dev.customize.yaml`:

```yaml
# 开发 Agent 自定义
critical_actions:
  - "Always run tests after implementation"
  - "Auto-commit with conventional commit messages"
  - "Update sprint-status.yaml automatically"

memories:
  - "Project uses TypeScript strict mode"
  - "All API endpoints need OpenAPI documentation"
  - "Prefer React Hooks over class components"
```

## 监控和调试

### 1. 实时状态监控

```bash
# 检查当前阶段和进度
任何 Agent → workflow-status

# 检查 Sprint 状态
SM Agent → sprint-status

# 检查测试覆盖率
TEA Agent → trace
```

### 2. 日志分析

BMAD 的每个工作流都会输出详细日志到相应的文档中:

```
_bmad-output/
├── planning-artifacts/
│   ├── PRD.md                      # 包含需求定义过程
│   ├── architecture.md             # 包含架构决策 ADRs
│   └── epics/                      # Epic 和 Story 定义
├── implementation-artifacts/
│   ├── sprint-status.yaml          # 实时追踪实现进度
│   └── retrospectives/             # 回顾和改进建议
└── test-artifacts/
    ├── test-design-system.md       # 系统级测试设计
    └── test-review-report.md       # 测试质量评估
```

### 3. 错误恢复

当自主执行遇到问题时:

```bash
# 1. 检查状态文件
cat _bmad-output/implementation-artifacts/sprint-status.yaml

# 2. 找到失败的 Story
# status: in-progress (stuck) 或 review (failed)

# 3. 手动修复或重新运行
SM Agent → create-story story-name (重新生成)
DEV Agent → dev-story (重新实现)

# 4. 继续自主执行
SM Agent → sprint-status (检查下一步)
```

## 最佳实践总结

### 自主开发的黄金法则

1. **渐进式自主化**: 从 Phase 3-4 开始自主,Phase 1-2 保持交互
2. **质量门禁必查**: 每个阶段结束运行相应的门禁检查
3. **状态文件为准**: 以 workflow-status.yaml 和 sprint-status.yaml 为唯一真相来源
4. **Fresh Chats**: 每个工作流使用新的 Chat 会话避免上下文污染
5. **人工监督关键节点**: Architecture 决策、复杂 Bug 修复仍需人工参与

### 快速开始自主开发

```bash
# 准备阶段 (交互式)
1. workflow-init
2. create-prd (需要人工输入需求)
3. create-ux-design (可选,需要人工审美判断)

# 自主执行阶段 (夜间运行)
4. create-architecture (基于 PRD 自动生成)
5. create-epics-and-stories (基于 Architecture 自动生成)
6. implementation-readiness (自动门禁检查)
7. sprint-planning → (create-story → dev-story → code-review) × N

# 验收阶段 (人工审查)
8. 审查 git diff
9. 运行集成测试
10. 部署到测试环境
```

### 何时使用 BMAD vs Ralph

| 使用场景 | 推荐工具 | 原因 |
|---------|---------|------|
| **完整软件生命周期** | BMAD | 多阶段工作流,专业化 Agent |
| **持续优化单一目标** | Ralph | 循环执行直到达标 |
| **大型项目 (30+ Stories)** | BMAD | 结构化管理,阶段性门禁 |
| **快速原型 (< 10 Stories)** | BMAD Quick Flow | 快速规范到实现 |
| **测试覆盖率提升** | BMAD (TEA) | 测试架构专长 |
| **单一功能持续优化** | Ralph | 持续迭代直到完美 |

---

## 相关资源

- [BMAD 快速开始指南](https://github.com/bmad-code-org/BMAD-METHOD)
- [Ralph for Claude Code](https://github.com/frankbria/ralph-claude-code)
- [自主开发范式 - Ralph 文档](./autonomous-development.md)

**记住**: BMAD 提供结构化的 AI 驱动开发框架,而非无脑自动化。最佳实践是在关键决策点保持人工参与,在实现和测试阶段实现自主化,从而达到效率和质量的最佳平衡。
