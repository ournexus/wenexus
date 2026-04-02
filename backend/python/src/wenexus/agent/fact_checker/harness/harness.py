"""Fact Checker Harness - 开箱即用接口."""

from dataclasses import dataclass
from typing import Any

from ..providers.mock import MockSearchProvider
from ..runtime.graph import create_fact_checker_graph
from ..runtime.state import FactCheckState, FactReport


@dataclass
class HarnessConfig:
    """Harness 配置."""

    model: str = "openai:gpt-4o-mini"
    temperature: float = 0.2
    max_iterations: int = 5


class FactCheckerHarness:
    """Fact Checker 开箱即用 Harness."""

    def __init__(
        self,
        model: str = "openai:gpt-4o-mini",
        temperature: float = 0.2,
        max_iterations: int = 5,
    ):
        self.config = HarnessConfig(
            model=model,
            temperature=temperature,
            max_iterations=max_iterations,
        )
        self.search_provider = MockSearchProvider()
        self.graph = create_fact_checker_graph(
            search_provider=self.search_provider,
            max_iterations=self.config.max_iterations,
        )

    async def run(
        self,
        topic_title: str,
        topic_description: str | None = None,
        topic_id: str | None = None,
    ) -> FactReport:
        """运行事实核查."""
        import time

        initial_state: FactCheckState = {
            "topic_id": topic_id,
            "topic_title": topic_title,
            "topic_description": topic_description,
            "current_iteration": 0,
            "max_iterations": self.config.max_iterations,
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

        result = self.graph.invoke(initial_state)
        if result["final_report"] is None:
            raise RuntimeError(f"Fact checker failed: {result.get('error', 'Unknown')}")
        return result["final_report"]

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "graph": "compiled"}
