"""
service.agent.fact_checker.agent - Fact Checker Agent（BaseAgent 实现）。

从 agent/fact_checker/harness/harness.py 迁入，适配 BaseAgent 接口。

Depends: model.agent, model.fact_report, service.agent.base, langgraph
Consumers: app.agent_registry, facade.fact_checker
"""

import time

from wenexus.model.agent import (
    AgentCard,
    AgentTaskInput,
    AgentTaskOutput,
    AgentType,
)
from wenexus.model.fact_report import FactReport

from ..base import BaseAgent
from .graph import create_fact_checker_graph
from .interfaces.search import SearchProvider
from .providers.mock import MockSearchProvider
from .state import FactCheckState


class FactCheckerAgent(BaseAgent):
    """Fact Checker Agent — 事实核查。"""

    def __init__(
        self,
        max_iterations: int = 5,
        search_provider: SearchProvider | None = None,
    ) -> None:
        self._max_iterations = max_iterations
        self._search_provider = search_provider or MockSearchProvider()
        self._graph = create_fact_checker_graph(
            search_provider=self._search_provider,
            max_iterations=self._max_iterations,
        )

    def card(self) -> AgentCard:
        return AgentCard(
            name="fact_checker",
            display_name="求真者",
            description="为争议性话题收集可验证的事实数据",
            agent_type=AgentType.FUNCTIONAL,
            capabilities=("fact_check", "web_search", "data_extraction"),
        )

    async def run(self, task_input: AgentTaskInput) -> AgentTaskOutput:
        """运行事实核查。"""
        start = time.time()
        params = task_input.params
        topic_title = str(params.get("topic_title", ""))
        topic_description = params.get("topic_description")
        topic_id = params.get("topic_id")

        if not topic_title:
            return AgentTaskOutput(
                agent_name="fact_checker",
                status="error",
                error="Missing 'topic_title' in params",
            )

        initial_state: FactCheckState = {
            "topic_id": str(topic_id) if topic_id else None,
            "topic_title": topic_title,
            "topic_description": str(topic_description) if topic_description else None,
            "current_iteration": 0,
            "max_iterations": self._max_iterations,
            "should_continue": True,
            "search_queries": [],
            "search_results": [],
            "search_iterations": [],
            "extracted_facts": [],
            "coverage_analysis": None,
            "final_report": None,
            "status": "pending",
            "error": None,
            "total_tokens": 0,
            "start_time": time.time(),
            "end_time": None,
        }

        try:
            result = await self._graph.ainvoke(initial_state)  # type: ignore[arg-type]
            final_report: FactReport | None = result.get("final_report")
            if final_report is None:
                return AgentTaskOutput(
                    agent_name="fact_checker",
                    status="error",
                    error=result.get("error", "Unknown error"),
                )
            elapsed = int((time.time() - start) * 1000)
            return AgentTaskOutput(
                agent_name="fact_checker",
                status="completed",
                result={
                    "topic_title": final_report.topic_title,
                    "summary": final_report.summary,
                    "facts_count": len(final_report.facts),
                    "sources_count": len(final_report.sources),
                    "credibility_distribution": final_report.credibility_distribution,
                },
                execution_time_ms=elapsed,
            )
        except Exception as e:
            return AgentTaskOutput(
                agent_name="fact_checker",
                status="error",
                error=str(e),
            )

    async def health_check(self) -> bool:
        """健康检查。"""
        return True
