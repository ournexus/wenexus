# Story 1.5: 求真者（Fact Checker）Deep Agent 实现

Status: ready-for-dev

## Story

As a 内容生产系统,
I want 求真者 Agent 为每个话题讨论提供经过验证的事实数据基础,
So that AI 专家的观点建立在可靠的数据之上而非凭空捏造。

## Acceptance Criteria

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

## Tasks / Subtasks

- [ ] 设计 Fact Checker Agent 架构（LangGraph StateGraph）
  - [ ] 定义 Agent 输入：话题标题、描述
  - [ ] 定义 Agent 输出：结构化事实报告
  - [ ] 设计 StateGraph 节点流程
- [ ] 实现事实收集 Tools
  - [ ] WebSearch Tool：搜索权威数据源
  - [ ] DocumentSearch Tool：检索现有数据库中的相关研究
  - [ ] DataExtraction Tool：从搜索结果中提取结构化数据
- [ ] 实现事实验证 LLM Chain
  - [ ] 构建验证 Prompt，要求返回 JSON 格式
  - [ ] 定义可信度评级枚举（high/medium/low/uncertain）
  - [ ] 实现自检：模糊内容标记为待核实
- [ ] 实现事实报告生成
  - [ ] 汇总统计数据模块
  - [ ] 汇总权威研究引用模块
  - [ ] 汇总政策法规摘要模块
  - [ ] 汇总跨国对比数据模块
- [ ] 数据持久化与关联
  - [ ] 创建 `fact_reports` 表结构
  - [ ] 关联 fact_report 到 topic
  - [ ] 关联 fact_report 到 roundtable_session（可选）
- [ ] 集成到 Autopilot 流程
  - [ ] 在 LangGraph Autopilot Flow 中添加 FactChecker 节点
  - [ ] 作为后续专家生成的输入上下文
- [ ] 单元测试与集成测试
  - [ ] 测试事实提取准确性
  - [ ] 测试可信度评级逻辑
  - [ ] 测试模糊内容标记

## Dev Notes

### Deep Agents 架构设计

基于 LangChain Deep Agents 的 **Agent Harness** 模式，实现开箱即用的事实核查 Agent。

**核心概念**：[Source: github.com/langchain-ai/deepagents]

- **Agent Harness**: 上层封装，提供默认配置和内置工具
- **底层运行时**: LangGraph StateGraph
- **模型无关**: 通过配置切换不同 LLM 供应商

### Project Structure

**Deep Agents Pattern**:

```
backend/python/src/wenexus/agent/
├── harness/                    # Agent Harness 层（Deep Agents 模式）
│   ├── __init__.py
│   ├── base.py                # BaseAgentHarness 抽象基类
│   └── fact_checker/          # 求真者 Agent Harness
│       ├── __init__.py
│       ├── harness.py         # FactCheckerHarness 实现
│       ├── config.py          # 默认配置（模型、温度、超时）
│       ├── prompts/           # Prompt 模板目录
│       │   ├── planner.txt    # 查询规划 Prompt
│       │   ├── search.txt     # 搜索指令 Prompt
│       │   ├── extractor.txt  # 数据提取 Prompt
│       │   └── validator.txt  # 可信度验证 Prompt
│       └── tools/             # 内置 Tools
│           ├── __init__.py
│           ├── web_search.py  # Web 搜索 Tool
│           └── data_extract.py # 数据提取 Tool
├── runtime/                   # LangGraph 运行时（底层）
│   ├── __init__.py
│   └── fact_checker/          
│       ├── __init__.py
│       ├── graph.py           # StateGraph 定义
│       ├── state.py           # TypedDict State
│       ├── nodes.py           # Graph 节点实现
│       └── edges.py           # 边条件逻辑
```

**Facilitator 层（已在 graph.py）**: Roundtable Facilitator Agent - 参考实现

### Database Schema

```sql
-- fact_reports 表
CREATE TABLE fact_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL REFERENCES topics(id),
  session_id UUID REFERENCES roundtable_sessions(id),
  
  -- Deep Agents 输出
  report JSONB NOT NULL,              -- 结构化报告
  search_iterations JSONB,            -- 搜索迭代历史
  sources JSONB,                      -- 来源列表
  credibility_distribution JSONB,   -- {high: n, medium: n, low: n, uncertain: n}
  
  -- 执行元数据
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  iterations INT DEFAULT 0,           -- 搜索迭代次数
  total_tokens INT,                   -- Token 消耗
  execution_time_ms INT,              -- 执行耗时
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deep Agents 配置表（可选：支持运行时配置覆盖）
CREATE TABLE fact_checker_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL,
  config JSONB NOT NULL,  -- 完整的 Harness 配置
  is_active BOOLEAN DEFAULT false
);
```

### Architecture Compliance

**Deep Agents 分层**（新增模式）：

| 层级 | 职责 | 文件 |
|------|------|------|
| **Harness 层** | 开箱即用封装，默认配置，Prompt 管理 | `agent/harness/fact_checker/` |
| **Runtime 层** | LangGraph StateGraph，纯执行逻辑 | `agent/runtime/fact_checker/` |
| **Orchestration 层** | App 层调用 Harness，业务编排 | `app/fact_checker.py` |
| **Repository 层** | fact_report CRUD | `repository/fact_report.py` |

**Usage Pattern**（参考 Claude Code 模式）：

```python
# App 层调用（简洁接口，开箱即用）
from wenexus.agent.harness.fact_checker import FactCheckerHarness

harness = FactCheckerHarness(
    model="openai/gpt-4o",  # 可切换模型
    temperature=0.2,
    max_iterations=5
)

report = await harness.run(
    topic_title="彩礼",
    topic_description="关于彩礼的争议..."
)
```

**错误处理**（RFC 9457）：

- Harness 封装错误 → 统一抛出 `FactCheckerError`
- Runtime 层状态 → `state["status"] = "error"` + `state["error"]`
- App 层转换 → HTTP Problem Details

### StateGraph Design (Runtime Layer)

```python
class FactCheckState(TypedDict):
    # Input
    topic_id: str
    topic_title: str
    topic_description: str
    
    # Deep Agents 迭代搜索
    current_iteration: int
    query_plan: List[SearchQuery]  # 规划的多轮搜索
    search_results: List[SearchResult]
    extracted_facts: List[Fact]
    coverage_analysis: CoverageAnalysis  # 覆盖度分析
    
    # 控制流
    should_continue: bool  # 是否继续搜索
    
    # Output
    final_report: Optional[FactReport]
    sources: List[Source]
    credibility_distribution: Dict[str, int]
    
    # 元数据
    status: Literal["pending", "planning", "searching", "extracting", 
                    "analyzing", "validating", "completed", "error"]
    error: Optional[str]

# Nodes
1. planner: 规划查询策略
2. searcher: 执行搜索 (Tool)  
3. extractor: 提取结构化数据
4. analyzer: 分析覆盖度 → 决定继续或停止
5. validator: 验证可信度
6. synthesizer: 生成最终报告
```

### Deep Agents 关键洞见

**[Source: github.com/langchain-ai/deepagents]**

> "This project was primarily inspired by **Claude Code**, and initially was largely an attempt to see what made Claude Code general purpose, and make it even more so."

### 本地参考实现

**[Source: /Users/mac/Desktop/code-open/deep_research_from_scratch/]**

用户本地已有完整 Deep Research 实现，可直接参考/复用：

| 文件 | 用途 | WeNexus 适配 |
|------|------|-------------|
| `src/deep_research_from_scratch/research_agent.py` | 核心 Agent Graph | 核心参考 ✓✓✓ |
| `src/deep_research_from_scratch/state_research.py` | State 定义 | 核心参考 ✓✓✓ |
| `src/deep_research_from_scratch/prompts.py` | Prompt 模板 | 提取中文版本 |
| `src/deep_research_from_scratch/utils.py` | Tavily 搜索工具 | 可复制使用 |

**Graph 架构（来自 research_agent.py）**：

```python
# WeNexus 简化版
agent_builder = StateGraph(ResearcherState, output=FactReport)
agent_builder.add_node("llm_call", llm_call)              # 规划查询
agent_builder.add_node("tool_node", tool_node)          # 执行搜索
agent_builder.add_node("compress_research", synthesize)  # 合成报告

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call", should_continue, {"tool_node": "tool_node", "compress_research": "compress_research"}
)
agent_builder.add_edge("tool_node", "llm_call")  # 循环
agent_builder.add_edge("compress_research", END)
```

**关键路由逻辑（should_continue）**：

```python
def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """决定继续搜索还是生成最终报告"""
    last_message = state["messages"][-1]
    
    # 如果有 tool calls，继续搜索
    if last_message.tool_calls:
        return "tool_node"
    
    # 达到迭代上限或决定停止，压缩并输出
    if state["iteration"] >= MAX_ITERATIONS:
        return "compress_research"
    
    return "compress_research"  # LLM 决定停止
```

**WeNexus 定制**：

- Tavily Search → DuckDuckGo/Perplexity API（中文搜索更友好）
- 原始循环搜索 → 添加覆盖度分析（是否继续下一维度）
- Summarize 模型 → 添加可信度验证节点

**核心设计原则**：

1. **Trust the LLM** — 不指望模型自我约束，而是在工具/沙箱层面强制边界
2. **Batteries Included** — Planning、Filesystem、Sub-agents、Context management 开箱即用
3. **LangGraph Native** — `create_deep_agent` 返回编译好的 LangGraph graph，兼容所有 LangGraph 特性
4. **Provider Agnostic** — 支持任何支持 tool calling 的模型（前沿模型 + 开源模型）

**WeNexus 定制点**：

| Deep Agents 原功能 | WeNexus 定制 |
|-------------------|-------------|
| `write_todos` | 替换为 `plan_research_queries` — 规划查询策略 |
| `read_file/write_file` | WebSearch API 调用 + 结构化数据提取 |
| `execute` shell | 可选：WebSearch 结果缓存到 temp files |
| `task` sub-agents | Searcher sub-agent → Extractor sub-agent → Validator sub-agent |
| Auto-summarization | Token 预算管理 + 迭代搜索终止条件 |

**依赖安装**（需添加到 pyproject.toml）：

```toml
dependencies = [
    # 已存在
    "langgraph>=0.2.0",
    "langchain-openai>=0.1.0",
    
    # Deep Agents 核心
    "deepagents>=0.1.0",  # Agent Harness SDK
    
    # 可选增强（基于环境选择）
    "duckduckgo-search>=6.0",  # Web search fallback
    "aiohttp>=3.9",            # HTTP client for search APIs
]
```

**接口参考**（Deep Agents SDK）：

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# 基础用法（类似 Fact Checker 开箱即用版）
agent = create_deep_agent(
    model=init_chat_model("openai/gpt-4o"),
    tools=[web_search, data_extract],  # 自定义工具
    system_prompt="You are a fact checker...",
)

# 高级用法（WeNexus 实际）
# 基于 create_deep_agent 源码模式自定义 StateGraph
# 保留 planning/sandbox/sub-agents 但定制业务逻辑
```

### Coverage Strategy & Technical Implementation

**核心原则：坦诚报告覆盖度 + 多源策略最大化数据**

#### 事实覆盖度分层

| 话题类型 | 例子 | 覆盖度 | Agent策略 |
|---------|------|--------|-----------|
| **硬数据** | GDP、人口、法条 | ✅ 高 | 优先官方统计 |
| **有研究** | 社会学分析 | ⚠️ 中 | 学术论文搜索 |
| **有政策** | 彩礼指导价 | ✅ 高 | 政府文件 |
| **新概念** | "预制人" | ❓ 低 | 媒体定义梳理 |
| **纯争议** | 人性本善/本恶 | ❌ 无 | 诚实标注"无客观数据" |

#### 技术策略

**1. 搜索词扩展（Query Expansion）**

```python
# 话题："彩礼是不是陋习"
queries = [
    "中国彩礼金额 统计 2024",      # 硬数据
    "彩礼 社会学研究 论文",         # 学术
    "民法典 彩礼 规定",              # 法规
    "天价彩礼 整治 政策",            # 政策
    "dowry China social function", # 英文视角
    "彩礼 离婚率 相关性",            # 关联数据
    "婚姻成本 中国 趋势",            # 延伸概念
]
```

**2. 多源并行搜索**
| 来源 | 用途 | 优先级 |
|------|------|--------|
| Perplexity API | 中文实时搜索 | 高 |
| Google Scholar | 学术论文 | 高 |
| ArXiv | 预印本 | 中 |
| WeNexus 话题库 | 已有数据 | 中 |

**3. 相关性降级（Fallback）**
直接数据无 → 找间接相关：

- "彩礼" → "婚姻成本" → "结婚率下降"
- "预制人" → "社交媒体 绩效压力"

**4. 停止条件**

- 搜索超过5轮无新信息 → 停止
- 新结果重复率>80% → 停止
- 达到Token预算上限 → 暂停并报告

#### 诚实标注机制（Honest Coverage Labeling）

```json
{
  "topic": "彩礼是不是陋习",
  "coverage_score": 0.7,
  "sections": {
    "statistics": {"level": "high", "sources": 3},
    "research": {"level": "medium", "sources": 2},
    "policy": {"level": "high", "sources": 3},
    "cross_country": {"level": "low", "sources": 1, "note": "仅印度数据"},
    "historical": {"level": "uncertain", "note": "缺乏长期追溯"}
  },
  "recommendation": "建议补充：彩礼与教育程度关系研究"
}
```

---

## Controversial Topic Case Studies

验证求真者 Agent 对各类争议话题的覆盖能力

### Case 1: "彩礼是不是陋习？"

**争议性**：高（文化习俗 vs 现代观念）

**求证策略**：

```
✅ 有硬数据：平均彩礼金额、省市差异
✅ 有研究：社会学论文（彩礼的社会功能）
✅ 有政策：民法典条文、各地彩礼指导价
⚠️ 国际对比：仅国外类似习俗（嫁妆等）
✅ 历史演变：相关研究较少
```

**验证预期输出**：
| 维度 | 找到的数据 | 可信度 |
|------|-----------|--------|
| 统计数据 | 2024年平均X万元 | High |
| 学术研究 | 核心期刊论文3篇 | Medium |
| 政策法规 | 民法典+地方政策 | High |
| 社会观点 | 媒体报道（多方观点）| Medium |

**Agent挑战**：直接搜"彩礼是不是陋习" = 无标准答案，需转换为"可验证事实"

---

### Case 2: "预制菜是垃圾食品吗？"

**争议性**：中（食品安全 vs 便利性）

**求证策略**：

```
✅ 有定义：预制菜国家标准
✅ 有检测：食品安全抽检数据
✅ 有研究：营养对比研究
⚠️ 长期影响：缺乏长期健康追踪
✅ 国际对比：日本/欧美预制食品数据
```

**特殊挑战**："垃圾食品"是价值判断 → 转换为"营养指标"

---

### Case 3: "AI会取代人类工作吗？"

**争议性**：高（预测性争议）

**求证策略**：

```
✅ 有预测：各行业AI替代率研究
✅ 有历史：工业革命就业变化
⚠️ 未来预测：本质不可验证
✅ 已有影响：部分行业失业率变化
```

**Agent挑战**：需区分"已发生的事实"和"专家预测"

---

### Case 4: "安乐死应该合法化吗？"

**争议性**：极高（生命伦理）

**求证策略**：

```
✅ 有案例：已合法国家（荷兰、比利时等）
✅ 有数据：实施情况统计
✅ 有研究：伦理学论文
❌ 对错判断：无法提供
```

**Agent边界**：只能提供"哪些国家合法"+"实施条件"，不作价值判断

---

### Case 5: "学历贬值了吗？"

**争议性**：中（统计性争议）

**求证策略**：

```
✅ 有硬数据：历年毕业生人数
✅ 有数据：起薪变化趋势
✅ 有研究：教育回报率分析
✅ 对比：不同学历失业率
```

**Agent挑战**：需明确定义"贬值"=起薪下降/失业率上升/ROI降低

---

## Case Study Summary

| 话题 | 覆盖难度 | 主要策略 | Agent边界 |
|------|---------|---------|----------|
| 彩礼是陋习 | 中 | 转换数据事实 | 不判对错 |
| 预制菜垃圾食品 | 中 | 营养指标化 | 不判好坏 |
| AI取代工作 | 高 | 区分事实/预测 | 标注预测性 |
| 安乐死合法化 | 高 | 国际案例对比 | 只给事实 |
| 学历贬值 | 低 | 多维度数据 | 明确定义 |

**核心洞见**：

1. **价值判断 → 指标数据**：不回答"是不是"，提供"有多少"
2. **预测未来 → 历史类比**：用已发生的相似事件做参照
3. **对错争议 → 多方观点**：呈现不同立场的论据，不选择立场
4. **无数据区 → 坦诚标注**：明确说"这一维度无可靠数据"

### 争议话题设计原则

**高争议性话题的共同特征**：

| 特征 | 说明 | 例子 |
|------|------|------|
| **价值观冲突** | 传统 vs 现代, 个人 vs 集体 | 彩礼、婚前同居 |
| **代际断层** | 父母辈 vs 年轻一代 | 催婚、鸡娃 |
| **利益博弈** | 劳动者 vs 资本, 阶层焦虑 | 996、躺平 |
| **技术伦理** | 效率 vs 安全, 创新 vs 风险 | AI、自动驾驶 |
| **信息不对称** | 数据缺失, 预测不确定 | 未来就业、经济趋势 |

**WeNexus 话题选题标准**：

1. ✅ **多维度可拆解** — 经济、法律、伦理、心理各有观点
2. ✅ **数据可验证** — 有统计、研究、案例支撑
3. ✅ **立场多元** — 无标准答案，但有理性探讨空间
4. ✅ **用户共鸣强** — 真实生活困境，愿意参与讨论

---

## Today's Hot Topic Case Study

**案例：小米SU7爆燃事故（2025年4月1日最大热点）**

### 话题设计

**主问题**："自动驾驶致人死亡，责任该由谁承担？"

**争议维度拆解**：
| 维度 | 核心问题 | 可验证数据 |
|------|---------|-----------|
| **技术维度** | 自动驾驶是否足够安全？ | 事故率统计（人驾 vs 智驾） |
| **法律维度** | 现行法律如何界定责任？ | 各国自动驾驶法规对比 |
| **企业维度** | 车企应承担什么责任？ | 车企用户协议条款分析 |
| **伦理维度** | 技术 innocent until proven guilty？| 技术伦理学论文 |
| **保险维度** | 保险如何覆盖智驾事故？ | 保险公司条款对比 |

**求证者预期输出**：

```json
{
  "topic": "自动驾驶致人死亡责任归属",
  "coverage_score": 0.75,
  "sections": {
    "statistics": {
      "level": "medium",
      "data": [
        {"item": "2024年中国自动驾驶事故率", "value": "X/百万公里", "source": "交通部", "credibility": "high"},
        {"item": "人驾基准事故率", "value": "Y/百万公里", "source": "统计局", "credibility": "high"}
      ]
    },
    "regulations": {
      "level": "high",
      "data": [
        {"country": "中国", "law": "道路交通安全法", "status": "L3试点阶段"},
        {"country": "德国", "law": "自动驾驶法", "status": "L3合法"},
        {"country": "美国", "law": "各州差异", "status": "加州/德州允许L3"}
      ]
    },
    "cases": {
      "level": "medium",
      "data": [
        {"case": "Tesla加州事故", "liability": "驾驶员负责", "date": "2023"},
        {"case": "Uber亚利桑那事故", "liability": "安全员+Uber", "date": "2018"}
      ]
    },
    "insurance": {
      "level": "low",
      "note": "国内智驾专项保险尚处起步阶段，数据有限"
    }
  },
  "controversy_summary": [
    "技术派：事故率低于人驾，技术无罪",
    "保守派：生命无价，不应拿公众做实验",
    "企业派：用户协议已告知风险，驾驶员应担责",
    "法律派：现行法滞后于技术，需明确L3责任边界"
  ],
  "recommendation": "建议补充：智能驾驶事故责任判例研究"
}
```

**为何适合 WeNexus**：

- 话题热度极高（今日最大热点）
- 多角度可论证（技术、法律、伦理、保险）
- 有真实数据支撑（事故率、法规、案例）
- 无标准答案（形成讨论空间）

---

### References

- [Deep Agents GitHub](github.com/langchain-ai/deepagents) - Agent Harness 官方实现
- [Deep Agents Docs](docs.langchain.com/oss/python/deepagents/overview) - 完整文档
- [docs/bmad/planning-artifacts/epics.md#Epic 1] - Story 1.5 原始需求
- [docs/bmad/planning-artifacts/architecture.md] - 技术架构决策
- [backend/python/src/wenexus/agent/graph.py] - 现有 Roundtable Facilitator 参考实现
- [backend/python/README.md] - Python 后端项目结构

## Dev Agent Record

### Agent Model Used

（待 Dev 阶段填写）

### Debug Log References

（待 Dev 阶段填写）

### Completion Notes List

（Dev 完成后填写）

### File List

（Dev 完成后填写）
