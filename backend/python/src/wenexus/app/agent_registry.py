"""
app.agent_registry - Agent Registry 生命周期管理。

在 FastAPI lifespan 中初始化，通过 app.state 挂载，facade 层通过 Depends 注入。

Depends: service.agent.registry, service.agent.facilitator, service.agent.fact_checker
Consumers: facade, main.py
"""

from fastapi import FastAPI, Request

from wenexus.service.agent.facilitator.agent import FacilitatorAgent
from wenexus.service.agent.fact_checker.agent import FactCheckerAgent
from wenexus.service.agent.registry import AgentRegistry


def init_agent_registry(app: FastAPI) -> AgentRegistry:
    """创建并初始化 AgentRegistry，挂载到 app.state。"""
    registry = AgentRegistry()
    registry.register(FacilitatorAgent())
    registry.register(FactCheckerAgent())
    app.state.agent_registry = registry
    return registry


def get_agent_registry(request: Request) -> AgentRegistry:
    """FastAPI 依赖注入 — 从 app.state 获取 registry。"""
    return request.app.state.agent_registry  # type: ignore[no-any-return]
