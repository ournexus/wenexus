"""
service.agent.persona - Persona Agent 骨架（配置驱动的人格 Agent）。

所有 Persona Agent（孔子、爱因斯坦等）共享同一套推理引擎，
通过不同的 PersonaConfig 实例化出不同人格。

本次仅预留骨架，完整实现在后续 Story 中。

Depends: model.agent, service.agent.base
Consumers: app.agent_registry（未来批量注册时使用）
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
        """返回基于 PersonaConfig 的能力声明。"""
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
        """执行任务 — 骨架，完整实现在后续 Story。"""
        raise NotImplementedError("PersonaAgent 完整实现在后续 Story 中")

    async def health_check(self) -> bool:
        """健康检查。"""
        return True
