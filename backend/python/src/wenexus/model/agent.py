"""
model.agent - Agent 基础设施领域模型（A2A 风格，面向 100+ Agent 规模）。

两类 Agent：
  - Functional Agent（~10个）：各有独立 StateGraph/工具链，如 FactChecker, Facilitator
  - Persona Agent（~100+）：共享推理引擎，仅配置不同，如孔子、爱因斯坦

Depends: (无)
Consumers: service.agent, app.agent_registry, facade
"""

from dataclasses import dataclass, field
from enum import StrEnum


class AgentType(StrEnum):
    """Agent 类型。

    FUNCTIONAL: 功能性 Agent，各有独立实现（如 FactChecker, Facilitator）
    PERSONA: 人格 Agent，共享推理引擎，仅配置不同（如 孔子、爱因斯坦）
    """

    FUNCTIONAL = "functional"
    PERSONA = "persona"


@dataclass(frozen=True)
class AgentCard:
    """Agent 能力声明（VO）— 参考 A2A Agent Card。

    每个 Agent 通过 AgentCard 声明名称、类型、能力，
    供 AgentRegistry 进行注册、发现和调度。
    """

    name: str  # 唯一标识，如 "fact_checker" 或 "confucius"
    display_name: str  # 显示名，如 "求真者" 或 "孔子"
    description: str
    agent_type: AgentType
    version: str = "1.0.0"
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PersonaConfig:
    """Persona Agent 配置（VO）— 描述一个人格的完整信息。

    Persona Agent 共享同一套推理引擎（PersonaAgent 实现），
    通过不同的 PersonaConfig 实例化出不同人格。
    未来 100+ Persona 将从数据库/配置文件批量加载。
    """

    name: str  # 唯一标识，如 "confucius"
    display_name: str  # 显示名，如 "孔子"
    system_prompt: str  # 人设 prompt
    expertise: tuple[str, ...] = ()  # 专业领域
    stance: str = "neutral"  # 立场倾向
    era: str = ""  # 时代，如 "ancient" / "modern"
    culture: str = ""  # 文化背景，如 "eastern" / "western"
    domain: str = ""  # 学科领域，如 "philosophy" / "physics"


@dataclass
class AgentTaskInput:
    """Agent 统一任务输入。"""

    agent_name: str
    params: dict[str, object] = field(default_factory=dict)


@dataclass
class AgentTaskOutput:
    """Agent 统一任务输出。"""

    agent_name: str
    status: str = "completed"  # completed / error
    result: dict[str, object] = field(default_factory=dict)
    error: str | None = None
    execution_time_ms: int = 0
    total_tokens: int = 0
