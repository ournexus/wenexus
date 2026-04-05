"""Fact Checker Unit Tests — 迁移自 tests/agent/fact_checker/。"""

import pytest

from wenexus.model.base import CredibilityLevel
from wenexus.model.fact_report import CoverageAnalysis, Fact, Source
from wenexus.service.agent.fact_checker import (
    FactCheckerAgent,
    MockSearchProvider,
)
from wenexus.service.agent.fact_checker.graph import create_fact_checker_graph
from wenexus.service.agent.fact_checker.interfaces.search import SearchQuery


class TestMockSearchProvider:
    """Mock 搜索提供方测试."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self) -> None:
        provider = MockSearchProvider()
        results = await provider.search(SearchQuery(query="彩礼", limit=5))
        assert len(results) > 0
        assert results[0].title
        assert results[0].url

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        provider = MockSearchProvider()
        assert await provider.health_check() is True


class TestFactCheckerGraph:
    """StateGraph 测试."""

    def test_graph_compiles(self) -> None:
        provider = MockSearchProvider()
        graph = create_fact_checker_graph(provider, max_iterations=2)
        assert graph is not None

    def test_graph_execution(self) -> None:
        provider = MockSearchProvider()
        graph = create_fact_checker_graph(provider, max_iterations=2)
        result = graph.invoke(
            {
                "topic_title": "彩礼",
                "topic_description": "关于彩礼的争议",
                "topic_id": None,
                "current_iteration": 0,
                "max_iterations": 2,
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
                "start_time": None,
                "end_time": None,
            }
        )
        assert result["status"] == "completed"
        assert result["final_report"] is not None
        assert result["final_report"].topic_title == "彩礼"


class TestFactCheckerAgent:
    """Agent 接口测试."""

    def test_card(self) -> None:
        agent = FactCheckerAgent(max_iterations=2)
        card = agent.card()
        assert card.name == "fact_checker"
        assert card.display_name == "求真者"

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        from wenexus.model.agent import AgentTaskInput

        agent = FactCheckerAgent(max_iterations=2)
        output = await agent.run(
            AgentTaskInput(
                agent_name="fact_checker",
                params={
                    "topic_title": "彩礼",
                    "topic_description": "关于彩礼的争议",
                },
            )
        )
        assert output.status == "completed"
        assert output.result.get("topic_title") == "彩礼"

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        agent = FactCheckerAgent(max_iterations=2)
        assert await agent.health_check() is True


class TestCoverageAnalysis:
    """覆盖度分析测试."""

    def test_coverage_calculation(self) -> None:
        analysis = CoverageAnalysis(
            total_dimensions=4,
            covered_dimensions=3,
            coverage_score=0.75,
            missing_dimensions=("国际对比",),
        )
        assert analysis.coverage_score == 0.75
        assert len(analysis.missing_dimensions) == 1


class TestFactStructure:
    """Fact 结构测试."""

    def test_fact_has_required_fields(self) -> None:
        from wenexus.model.base import SourceType

        source = Source(
            title="测试来源",
            url="https://test.com",
            snippet="测试内容",
            source_type=SourceType.ACADEMIC,
        )
        fact = Fact(
            content="彩礼平均12.8万元",
            claim="彩礼金额",
            source=source,
            credibility=CredibilityLevel.HIGH,
        )
        assert fact.content
        assert fact.source.title
        assert fact.credibility == CredibilityLevel.HIGH
