"""
service.agent.registry - Agent 注册中心（A2A 风格）。

职责：
  - 注册：Agent 启动时向 Registry 注册自身
  - 发现：按名称查找，或按类型/能力/维度多条件筛选
  - 调度：统一入口调用任意已注册 Agent

Depends: model.agent, service.agent.base
Consumers: app.agent_registry, facade
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
                    card.metadata.get(k) == v for k, v in metadata_filters.items()
                )
                if not match:
                    continue
            results.append(agent)
        return results

    async def invoke(self, name: str, task_input: AgentTaskInput) -> AgentTaskOutput:
        """调度执行指定 Agent。"""
        agent = self.get(name)
        return await agent.run(task_input)
