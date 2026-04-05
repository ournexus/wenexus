"""
service.agent.base - Agent 统一抽象。

所有 Agent（Functional 和 Persona）必须实现此接口。

Depends: model.agent
Consumers: service.agent.registry, service.agent.facilitator, service.agent.fact_checker
"""

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
