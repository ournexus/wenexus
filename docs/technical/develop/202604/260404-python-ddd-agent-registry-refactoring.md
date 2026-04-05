# Python 后端 DDD 分层重构 + Agent Registry 技术方案

## 背景与动机

### 问题

Story 1.5（求真者 Fact Checker Deep Agent）的骨架代码已存在，但暴露了架构层面的问题：

1. **领域模型放置混乱** — `Source`, `Fact`, `FactReport` 等业务概念混在 `agent/fact_checker/runtime/state.py`，与 LangGraph 状态定义耦合
2. **Agent 层定位模糊** — `agent/` 作为顶层目录与 `service/` 平级，但 Agent 本质是一种通过 LLM 完成任务的 Service
3. **缺乏统一管理** — FactChecker 和 Facilitator 两个 Agent 各自为政，无注册/发现/统一调度机制
4. **ORM 基础缺失** — `repository/model/base.py` 被引用但不存在
5. **CQE 模式缺失** — Facade 层直接使用 Pydantic BaseModel 作为请求体，缺少 Command/Query 的语义区分

### 规模预期

WeNexus 未来将拥有 **100+ Agent**，分为两类：

| 类型 | 例子 | 数量级 | 实现特征 |
|------|------|--------|---------|
| **Functional Agent** | FactChecker, Facilitator, VerifyAgent, ViewpointGenerator | ~10 个 | 各有独立 StateGraph/工具链，代码定义 |
| **Persona Agent** | 孔子、苏格拉底、爱因斯坦、凯恩斯 | ~100+ 个 | 共享推理引擎，仅配置不同（人设 prompt、立场、专业领域） |

Persona Agent 是内容生产的核心 — 圆桌讨论中的 AI 专家本质上是不同人格配置下的同一引擎实例。

### 目标

按 DDD（领域驱动设计）原则重构 Python 后端分层架构，面向 3-5 年演进。建立清晰的对象流转链路，为 100+ Agent 的注册/发现/调度和 Agent 间协作（A2A 模式）奠定基础。

### 实施范围

- **本次实现（Story 1.5）**：Functional Agent 架构（BaseAgent + AgentRegistry + FactChecker/Facilitator 迁移）
- **预留但不实现**：PersonaAgent 框架、配置驱动批量注册、多维度查询
- **model 层类型现在就定义**：`AgentType`、`PersonaConfig` 等，避免后续破坏性变更

---

## 架构设计

### DDD 对象流转链路

```
入站（写操作）:
  HTTP Request → CQE (Command) → DP (Domain Primitive) → Entity → DO → Database

出站（读操作）:
  Database → DO → Entity (含 DP/VO) → DTO → HTTP Response
```

### 对象类型定义

| 类型 | 全称 | 归属层 | 职责 | 框架依赖 |
|------|------|--------|------|----------|
| **CQE** | Command / Query / Event | facade | 封装请求意图，自带参数校验 | Pydantic |
| **DP** | Domain Primitive | model | 最小自校验值对象，非法状态无法构造 | 无 |
| **VO** | Value Object | model | 不可变对象，按值比较，由多个 DP 组合 | 无 |
| **Entity** | Entity | model | 有唯一标识，有生命周期 | 无 |
| **DO** | Data Object | repository/model | ORM 映射，数据库表的 Python 表示 | SQLAlchemy |
| **DTO** | Data Transfer Object | facade | API 响应序列化，面向前端的数据契约 | Pydantic |

### 分层依赖规则

```
facade  →  app  →  service  →  repository
  ↓         ↓        ↓           ↓
  └─────────┴────────┴───────────┴──→  model（所有层依赖 model，model 不依赖任何层）
```

**model 层是架构的核心**：纯 Python（dataclass, enum, Protocol），零框架依赖。

---

## 领域模型设计

### model 层目录结构

```
src/wenexus/model/
  __init__.py
  base.py              # 基础 DP 和共享枚举
  fact_report.py       # Fact Check 领域模型
  agent.py             # Agent 基础设施领域模型
```

### base.py — 基础 Domain Primitive

```python
"""基础领域原语 — 自校验值对象，非法状态无法构造。"""

import re
from dataclasses import dataclass
from enum import Enum


class CredibilityLevel(str, Enum):
    """可信度等级。"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class SourceType(str, Enum):
    """来源类型。"""
    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"
    GOV = "gov"


class VerificationStatus(str, Enum):
    """验证状态。"""
    VERIFIED = "verified"
    PENDING = "pending"
    DISPUTED = "disputed"


class AgentStatus(str, Enum):
    """Agent 执行状态。"""
    PENDING = "pending"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"


_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


@dataclass(frozen=True)
class TopicId:
    """话题 ID — UUID 格式自校验。"""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not _UUID_RE.match(self.value):
            raise ValueError(f"Invalid TopicId: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    """会话 ID — UUID 格式自校验。"""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not _UUID_RE.match(self.value):
            raise ValueError(f"Invalid SessionId: {self.value}")

    def __str__(self) -> str:
        return self.value
```

### fact_report.py — Fact Check 领域模型

```python
"""Fact Check 领域模型 — Entity / Value Object / Domain Primitive。"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .base import CredibilityLevel, SourceType, VerificationStatus


# ── Value Objects (不可变，按值比较) ──

@dataclass(frozen=True)
class Source:
    """事实来源（VO）。"""
    title: str
    url: str
    snippet: str
    source_type: SourceType = SourceType.WEB
    published_date: str | None = None
    credibility: CredibilityLevel = CredibilityLevel.UNCERTAIN


@dataclass(frozen=True)
class Fact:
    """提取的事实（VO）。"""
    content: str
    claim: str
    source: Source
    credibility: CredibilityLevel = CredibilityLevel.UNCERTAIN
    verification_status: VerificationStatus = VerificationStatus.PENDING
    notes: str = ""


@dataclass(frozen=True)
class CoverageAnalysis:
    """覆盖度分析（VO）。"""
    total_dimensions: int
    covered_dimensions: int
    coverage_score: float  # 0.0 ~ 1.0
    missing_dimensions: tuple[str, ...] = ()
    recommendation: str = ""


@dataclass(frozen=True)
class SearchIteration:
    """单次搜索迭代记录（VO）。"""
    iteration: int
    query: str
    results_count: int
    key_findings: tuple[str, ...] = ()


# ── Entity (有 ID，有生命周期) ──

@dataclass
class FactReport:
    """事实报告（Entity）— 有唯一标识，有生命周期。

    注意：序列化方法（to_dict）不在 Entity 上定义，
    由 repository 层的 mapper 或 facade 层的 DTO 转换器负责。
    Entity 只包含业务行为。
    """
    id: UUID = field(default_factory=uuid4)
    topic_title: str = ""
    summary: str = ""
    facts: list[Fact] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    coverage_analysis: CoverageAnalysis | None = None
    credibility_distribution: dict[str, int] = field(default_factory=dict)

    def add_fact(self, fact: Fact) -> None:
        """添加事实 — Entity 通过方法管理内部状态，避免贫血模型。"""
        self.facts.append(fact)
        # 更新可信度分布
        level = fact.credibility.value
        self.credibility_distribution[level] = (
            self.credibility_distribution.get(level, 0) + 1
        )

    def add_source(self, source: Source) -> None:
        """添加来源。"""
        self.sources.append(source)
```

### agent.py — Agent 基础设施模型

```python
"""Agent 基础设施领域模型 — A2A 风格，面向 100+ Agent 规模设计。"""

from dataclasses import dataclass, field
from enum import Enum


class AgentType(str, Enum):
    """Agent 类型。

    FUNCTIONAL: 功能性 Agent，各有独立 StateGraph/工具链（如 FactChecker, Facilitator）
    PERSONA: 人格 Agent，共享推理引擎，仅配置不同（如 孔子、爱因斯坦）
    """
    FUNCTIONAL = "functional"
    PERSONA = "persona"


@dataclass(frozen=True)
class AgentCard:
    """Agent 能力声明（VO）— 参考 A2A Agent Card。

    每个 Agent 通过 AgentCard 声明自己的名称、类型、能力和输入输出规格，
    供 AgentRegistry 进行注册、发现和调度。
    """
    name: str                           # 唯一标识，如 "fact_checker" 或 "confucius"
    display_name: str                   # 显示名，如 "求真者" 或 "孔子"
    description: str                    # 能力描述
    agent_type: AgentType               # FUNCTIONAL / PERSONA
    version: str = "1.0.0"
    capabilities: tuple[str, ...] = ()  # 如 ("fact_check", "web_search")
    metadata: dict = field(default_factory=dict)  # 扩展属性（Persona 的分类维度等）


@dataclass(frozen=True)
class PersonaConfig:
    """Persona Agent 配置（VO）— 描述一个人格的完整信息。

    Persona Agent 共享同一套推理引擎（PersonaAgent 实现），
    通过不同的 PersonaConfig 实例化出不同人格（孔子、爱因斯坦等）。

    未来 100+ Persona 将从数据库/配置文件批量加载。
    """
    name: str                    # 唯一标识，如 "confucius"
    display_name: str            # 显示名，如 "孔子"
    system_prompt: str           # 人设 prompt
    expertise: tuple[str, ...] = ()   # 专业领域，如 ("philosophy", "ethics")
    stance: str = "neutral"      # 立场倾向
    era: str = ""                # 时代，如 "ancient" / "modern"
    culture: str = ""            # 文化背景，如 "eastern" / "western"
    domain: str = ""             # 学科领域，如 "philosophy" / "physics"


@dataclass
class AgentTaskInput:
    """Agent 统一任务输入。"""
    agent_name: str
    params: dict = field(default_factory=dict)


@dataclass
class AgentTaskOutput:
    """Agent 统一任务输出。"""
    agent_name: str
    status: str = "completed"       # completed / error
    result: dict = field(default_factory=dict)
    error: str | None = None
    execution_time_ms: int = 0
    total_tokens: int = 0
```

---

## Service 层 Agent 架构

### 目录结构

```
src/wenexus/service/agent/
  __init__.py
  base.py                           # BaseAgent 抽象基类
  registry.py                       # AgentRegistry（支持多维度查询）
  persona.py                        # PersonaAgent — 配置驱动的人格 Agent（骨架）
  facilitator/                      # Facilitator Agent（从 agent/graph.py 迁入）
    __init__.py
    agent.py                        # FacilitatorAgent(BaseAgent)
    tools.py                        # LangGraph tools
  fact_checker/                     # Fact Checker Agent（从 agent/fact_checker/ 迁入）
    __init__.py
    agent.py                        # FactCheckerAgent(BaseAgent)
    graph.py                        # LangGraph StateGraph
    nodes.py                        # Graph 节点
    state.py                        # FactCheckState(TypedDict) — 仅 LangGraph 状态
    prompts.py                      # Prompt 模板
    providers/
      __init__.py
      mock.py                       # MockSearchProvider
    interfaces/
      __init__.py
      search.py                     # SearchProvider ABC
```

### Agent 类型与创建策略

```
BaseAgent (ABC)
  ├── FacilitatorAgent      # Functional — 独立 StateGraph
  ├── FactCheckerAgent      # Functional — 独立 StateGraph + 搜索工具链
  └── PersonaAgent          # Persona — 共享引擎，配置驱动
        ├── PersonaConfig("confucius", ...)   → 孔子实例
        ├── PersonaConfig("einstein", ...)    → 爱因斯坦实例
        └── PersonaConfig("socrates", ...)    → 苏格拉底实例
```

Functional Agent 每个有独立实现类；Persona Agent 是**同一个类的不同配置实例**。

### base.py — BaseAgent

```python
"""Agent 统一抽象 — 所有 Agent 必须实现此接口。"""

from abc import ABC, abstractmethod

from wenexus.model.agent import AgentCard, AgentTaskInput, AgentTaskOutput


class BaseAgent(ABC):
    """Agent 基类。

    每个 Agent 是一个 Service，通过 AgentCard 声明能力，
    通过 run() 接受统一的任务输入并返回统一的任务输出。
    """

    @abstractmethod
    def card(self) -> AgentCard:
        """返回 Agent 能力声明。"""

    @abstractmethod
    async def run(self, task_input: AgentTaskInput) -> AgentTaskOutput:
        """执行任务。"""

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查。"""
```

### registry.py — AgentRegistry（A2A 风格）

```python
"""Agent 注册中心 — A2A 风格发现与调度。

职责：
  - 注册：Agent 启动时向 Registry 注册自身（Functional 手动注册，Persona 批量加载）
  - 发现：按名称查找，或按类型/能力/维度多条件筛选
  - 调度：统一入口调用任意已注册 Agent
"""

import structlog

from wenexus.model.agent import AgentCard, AgentTaskInput, AgentTaskOutput, AgentType

from .base import BaseAgent

logger = structlog.get_logger()


class AgentRegistry:
    """Agent 注册中心。"""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """注册 Agent。"""
        card = agent.card()
        self._agents[card.name] = agent

    def get(self, name: str) -> BaseAgent:
        """按名称获取 Agent。"""
        agent = self._agents.get(name)
        if agent is None:
            raise KeyError(f"Agent not found: {name}")
        return agent

    def list_agents(self) -> list[AgentCard]:
        """列出所有已注册 Agent 的能力声明。"""
        return [agent.card() for agent in self._agents.values()]

    def find_by(
        self,
        agent_type: AgentType | None = None,
        capability: str | None = None,
        **metadata_filters: str,
    ) -> list[BaseAgent]:
        """按条件筛选 Agent。

        支持按 agent_type、capability 和 metadata 中的任意字段过滤。
        示例：find_by(agent_type=PERSONA, domain="philosophy", culture="eastern")
        → 返回东方哲学家 Persona Agent 列表
        """
        results = []
        for agent in self._agents.values():
            card = agent.card()
            if agent_type and card.agent_type != agent_type:
                continue
            if capability and capability not in card.capabilities:
                continue
            if metadata_filters:
                match = all(
                    card.metadata.get(k) == v
                    for k, v in metadata_filters.items()
                )
                if not match:
                    continue
            results.append(agent)
        return results

    async def invoke(
        self, name: str, task_input: AgentTaskInput
    ) -> AgentTaskOutput:
        """调度执行指定 Agent。"""
        agent = self.get(name)
        return await agent.run(task_input)
```

### persona.py — PersonaAgent 骨架（本次预留，不完整实现）

```python
"""Persona Agent — 配置驱动的人格 Agent。

所有 Persona Agent（孔子、爱因斯坦等）共享同一套推理引擎，
通过不同的 PersonaConfig 实例化出不同人格。

本次仅预留骨架，完整实现在后续 Story 中。
"""

from wenexus.model.agent import (
    AgentCard,
    AgentTaskInput,
    AgentTaskOutput,
    AgentType,
    PersonaConfig,
)

from .base import BaseAgent


class PersonaAgent(BaseAgent):
    """人格 Agent — 同一实现，不同配置。"""

    def __init__(self, config: PersonaConfig) -> None:
        self._config = config

    def card(self) -> AgentCard:
        return AgentCard(
            name=self._config.name,
            display_name=self._config.display_name,
            description=f"Persona: {self._config.display_name}",
            agent_type=AgentType.PERSONA,
            capabilities=("roundtable_discussion",),
            metadata={
                "expertise": ",".join(self._config.expertise),
                "stance": self._config.stance,
                "era": self._config.era,
                "culture": self._config.culture,
                "domain": self._config.domain,
            },
        )

    async def run(self, task_input: AgentTaskInput) -> AgentTaskOutput:
        raise NotImplementedError("PersonaAgent 完整实现在后续 Story 中")

    async def health_check(self) -> bool:
        return True
```

---

## App 层编排

### app/agent_registry.py

```python
"""Agent Registry 生命周期管理 — 在 FastAPI lifespan 中初始化。

通过 app.state 挂载 registry 实例，facade 层通过 Depends 注入，
与 get_db 模式一致，便于测试时替换。
"""

from fastapi import FastAPI, Request

from wenexus.service.agent.facilitator.agent import FacilitatorAgent
from wenexus.service.agent.fact_checker.agent import FactCheckerAgent
from wenexus.service.agent.registry import AgentRegistry


def init_agent_registry(app: FastAPI) -> AgentRegistry:
    """创建并初始化 AgentRegistry，挂载到 app.state。

    在 main.py 的 lifespan 中调用。
    """
    registry = AgentRegistry()
    registry.register(FacilitatorAgent())
    registry.register(FactCheckerAgent())
    # 未来：从数据库批量加载 PersonaAgent
    app.state.agent_registry = registry
    return registry


def get_agent_registry(request: Request) -> AgentRegistry:
    """FastAPI 依赖注入 — 从 app.state 获取 registry。"""
    return request.app.state.agent_registry
```

---

## Repository 层补全

### repository/model/base.py

```python
"""SQLAlchemy ORM 基类。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass
```

### DO ↔ Entity 映射

在 `repository/fact_report.py` 中增加映射方法，实现 `FactReportORM(DO)` 与 `FactReport(Entity)` 之间的转换。

---

## 迁移影响

### 引用变更

| 旧 import | 新 import |
|-----------|-----------|
| `from wenexus.agent.graph import invoke_facilitator` | `from wenexus.service.agent.facilitator.agent import ...` |
| `from wenexus.agent.fact_checker.harness.harness import FactCheckerHarness` | `from wenexus.service.agent.fact_checker.agent import FactCheckerAgent` |
| `from wenexus.agent.fact_checker.runtime.state import Source, Fact, ...` | `from wenexus.model.fact_report import Source, Fact, ...` |
| `from wenexus.agent.tools import TOOLS` | `from wenexus.service.agent.facilitator.tools import TOOLS` |

### 删除的文件

- 整个 `agent/` 目录（代码迁入 `service/agent/` 和 `model/`）
- `agent/fact_checker/entrypoint.py`（冗余的简化版本）

### 配置更新

- `langgraph.json` — 更新 graph 路径指向 `service/agent/`
- `main.py` — 更新 router import，lifespan 中初始化 AgentRegistry

---

## 验证方案

1. **代码规范**: `uv run ruff check . && uv run ruff format --check .`
2. **类型检查**: `uv run mypy src/wenexus/`
3. **单元测试**: `uv run pytest tests/ -v`
4. **启动验证**: `uv run uvicorn src.wenexus.main:app --port 8000` — 无报错
5. **接口验证**: `curl -X POST http://localhost:8000/api/v1/fact-check -H "Content-Type: application/json" -d '{"topic_id":"test-uuid","topic_title":"彩礼","topic_description":"测试"}'`
6. **LangGraph**: 确认 `langgraph.json` 路径正确可用

---

## 后续演进方向

### 近期（Persona Agent 框架，下一个 Story）

- **PersonaAgent 完整实现**：共享推理引擎 + PersonaConfig 配置驱动
- **配置批量加载**：从数据库/YAML 批量加载 100+ Persona 到 Registry
- **Persona 管理 API**：CRUD Persona 配置（支持运行时新增人格）

### 中期（Agent 协作）

- **Agent 间通信**：基于 AgentRegistry 实现 Agent-to-Agent 调用链（如 FactChecker → ViewpointGenerator）
- **异步任务**：AgentRegistry.invoke 支持异步任务提交和状态查询（A2A Task 模式）
- **能力匹配**：圆桌讨论选专家时，按 `find_by(domain="philosophy", culture="eastern")` 组合查询

### 远期（平台化）

- **动态注册**：支持运行时注册新 Functional Agent（Plugin 架构）
- **Agent Marketplace**：用户自定义 Persona 配置
- **跨服务 A2A**：HTTP 协议层的 Agent 发现与调用（标准 A2A 协议）
