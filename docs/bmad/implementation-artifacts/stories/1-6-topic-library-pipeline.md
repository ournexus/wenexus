# Story 1.6: 话题库收集与质量管控 Pipeline

Status: ready-for-dev

## Story

As a 内容运营团队,
I want 建立系统化的话题收集、评审和入库流程,
so that 高质量争议性话题可持续地进入 WeNexus 平台，并自动触发事实核查。

## Acceptance Criteria

**Given** 用户/运营提交新话题建议
**When** 话题进入收集 Pipeline
**Then** 话题按照标准模板结构化存储（标题、正反方立场、背景、Fact Check 要点、建议专家配置）

**Given** 话题处于待评审状态
**When** 运营团队进行人工评审
**Then** 根据争议性评分标准（深度、可证性、多视角、相关度、安全度）进行质量评估
**And** 评分 >= 7/10 的话题可进入候选库

**Given** 话题通过人工评审
**When** 调用 Story 1.5 的 Fact Checker Deep Agent
**Then** 自动验证话题中的事实声明要点
**And** 将 Fact Report 关联到话题记录

**Given** 话题通过事实核查
**When** 状态流转为 approved
**Then** 自动生成 Roundtable Session 推荐配置（专家角色、讨论流程）
**And** 话题正式对外发布到 Discovery 库

**Given** 话题已入库
**When** 用户浏览 Discovery 页面
**Then** 可根据争议热度、难度等级、预计时长等维度筛选话题

**Given** 某话题在平台产生大量高质量讨论
**When** 运营团队标记为精选
**Then** 话题进入 Featured 列表，获得更高曝光

## Tasks / Subtasks

- [ ] 设计 TopicSubmission 数据模型扩展（新增争议维度、专家角色建议字段）
  - [ ] 扩展 Topic 表结构（contention_dimensions, suggested_experts, source_material）
  - [ ] 创建话题质量评分 schema（controversy_score, difficulty, estimated_duration）
  - [ ] 添加话题状态机（draft → reviewing → fact_checking → approved → published → featured）
  - [ ] 数据库 migration 脚本

- [ ] 实现话题收集 API（面向内部运营/管理员）
  - [ ] POST /api/topics/submit - 提交话题（含完整元数据）
  - [ ] GET /api/topics/pending - 获取待评审话题列表
  - [ ] PATCH /api/topics/{id}/review - 更新评审结果和评分

- [ ] 实现话题收集标准模板（结构化提交表单）
  - [ ] 话题标题（必须是对立性陈述）
  - [ ] 正方立场描述（500字）
  - [ ] 反方立场描述（500字）
  - [ ] 背景知识（历史/社会上下文）
  - [ ] Fact Check 要点（5-10 个待验证声明）
  - [ ] 建议专家角色配置（3-4 个角色 + 立场倾向）
  - [ ] 争议维度标签（经济/法律/伦理/文化等）
  - [ ] 难度等级（entry/intermediate/advanced）

- [ ] 集成 Story 1.5 Fact Checker 触发机制
  - [ ] 话题状态从 reviewing → fact_checking 时自动调用 FactCheckerHarness
  - [ ] 将 Fact Report 结果关联到 topic.fact_report_id
  - [ ] 根据 fact_report.coverage_score 决定是否通过审核
  - [ ] 审核失败（coverage_score < 0.5）时退回 reviewing 状态并附带建议

- [ ] 实现 Discovery 话题库页面扩展
  - [ ] 新增筛选维度（difficulty, controversy_score, duration, category）
  - [ ] Featured 话题置顶展示
  - [ ] 话题卡片显示争议热度指标（controversy_score）

- [ ] 实现 Roundtable Session 推荐配置自动生成
  - [ ] 根据 topic.suggested_experts 生成 session_config YAML
  - [ ] 预填充讨论流程（opening → debate → synthesis）
  - [ ] 关联到话题详情页"开始讨论"按钮

- [ ] 单元测试与集成测试
  - [ ] 测试话题状态流转（状态机验证）
  - [ ] 测试 Fact Checker 触发逻辑
  - [ ] 测试质量评分计算
  - [ ] 集成测试完整 Pipeline（提交 → 评审 → 核查 → 发布）

## Dev Notes

### 依赖前置

本 Story 依赖以下已完成或正在进行的功能：

- ✅ **Story 1.2**: Topic 数据模型已存在，本 Story 扩展字段
- ✅ **Story 1.3**: 话题维度拆解模型已存在，本 Story 复用维度标签
- ✅ **Story 1.5**: Fact Checker Deep Agent 已完成，本 Story 集成调用
- 🔄 **Story 1.4**: 内容状态管理需扩展（新增 fact_checking 状态）

### 技术架构决策

**数据层**：复用现有 Topic ORM 表（NoSQL Flavor），通过字段扩展而非新建表

**API 层**：复用 Discovery Facade 模式，新增 `/topics/submit`, `/topics/pending` 端点

**业务流程**：

```
TopicSubmission → Review Queue → Fact Check Trigger → Auto/Approve → Publish
```

**质量评分算法**（MVP 版人工为主，后续可接入 LLM 自动评分）：

```python
def calculate_controversy_score(submission: TopicSubmission) -> float:
    # 人工评审员填写各维度得分
    scores = {
        'depth': submission.score_depth,          # 争议深度 30%
        'verifiability': submission.score_verifiability,  # 可证性 25%
        'multi_perspective': submission.score_multi_perspective,  # 多视角 20%
        'relevance': submission.score_relevance,  # 相关性 15%
        'safety': submission.score_safety         # 安全度 10%
    }
    weights = [0.3, 0.25, 0.2, 0.15, 0.1]
    return sum(s * w for s, w in zip(scores.values(), weights))
```

### Project Structure Notes

**新建/修改文件**：

```
backend/python/src/wenexus/
├── repository/model/topic.py              # 扩展字段
├── repository/topic.py                    # 新增状态流转方法
├── app/topic_library.py                 # 话题 Pipeline 编排层
├── facade/topic_library.py              # 管理后台 API
└── service/topic_library.py             # 质量评分计算

frontend/apps/web/app/
├── api/topics/submit/route.ts           # 话题提交 API
├── api/topics/pending/route.ts          # 待评审列表
└── (main)/discovery/featured/page.tsx    # 精选话题页（可选）

docs/bmad/planning-artifacts/
└── topic-library-spec.md                # 运营使用手册
```

### 现有代码模式参考

**State Machine 模式**（来自 Story 1.4）：

```python
# 参考 repository/roundtable.py 中的 session 状态流转
async def update_topic_status(
    self, topic_id: UUID,
    from_status: TopicStatus,
    to_status: TopicStatus,
    reviewer_notes: str | None = None
) -> TopicORM:
    ...
```

**Fact Checker 调用模式**（来自 Story 1.5）：

```python
# 参考 app/fact_checker.py
from wenexus.agent.fact_checker.harness.harness import FactCheckerHarness

harness = FactCheckerHarness(...)
report = await harness.run(
    topic_title=topic.title,
    topic_description=topic.description
)
```

### References

- [Source: docs/bmad/planning-artifacts/stories/1-5-fact-checker-deep-agent.md] - Fact Checker 集成方式
- [Source: docs/bmad/planning-artifacts/epics.md#Story 1.2] - Topic 原始数据模型
- [Source: backend/python/src/wenexus/agent/fact_checker/harness/harness.py] - FactCheckerHarness API
- [Source: docs/technical/develop/202603/260312-business-flow-integration.md] - 业务流程集成文档

## Dev Agent Record

### Agent Model Used

（待 Dev 阶段填写）

### Debug Log References

（待 Dev 阶段填写）

### Completion Notes List

（Dev 完成后填写）

### File List

（Dev 完成后填写）

---

## 运营使用手册（草案）

### 话题收集标准模板

| 字段 | 要求 | 示例（加缪话题） |
|------|------|-----------------|
| **标题** | 对立性陈述，带问号或"vs" | "萨特式介入 vs 加缪式反抗：哪个更真诚？" |
| **正方立场** | 500字，有论点论据 | "知识分子必须选边站队，历史有方向..." |
| **反方立场** | 500字，有论点论据 | "拒绝站队，保持独立批判，两边都得罪..." |
| **背景知识** | 关键历史/社会上下文 | "1952年决裂事件，《反抗者》出版..." |
| **Fact Check 要点** | 5-10个可验证声明 | "萨特是否支持苏联劳改营是必要代价？" |
| **建议专家角色** | 3-4个角色+立场 | 存在主义哲学家(正)、伦理学家(反)、历史学家(中立) |
| **争议维度** | 标签数组 | ["哲学", "伦理", "政治", "历史"] |
| **难度等级** | entry/intermediate/advanced | intermediate |
| **预计时长** | 分钟数 | 20 |

### 争议性评分指南

| 维度 | 高分标准 | 低分标准 |
|------|---------|---------|
| **争议深度** (30%) | 触及价值观根本冲突 | 表面分歧 |
| **可证性** (25%) | 有统计/研究/案例支撑 | 纯主观判断 |
| **多视角** (20%) | 能容纳3+合理角度 | 二元对立 |
| **相关性** (15%) | 与当下社会高度关联 | 过时话题 |
| **安全度** (10%) | 理性讨论，无仇恨 | 可能激化对立 |

**准入门槛**: 总分 >= 7/10

### Fact Check 触发条件

- 状态流转: reviewing → fact_checking
- 自动调用 Story 1.5 的 Fact Checker Deep Agent
- coverage_score >= 0.5 自动通过
- coverage_score < 0.5 退回并附注"建议补充数据来源"
