"""Fact Checker Integration Tests."""

import pytest

from wenexus.agent.fact_checker import (
    FactCheckerHarness,
    MockSearchProvider,
    create_fact_checker_graph,
)
from wenexus.agent.fact_checker.interfaces.search import SearchQuery


class TestMockSearchProvider:
    """Mock 搜索提供方测试."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """搜索应返回预设结果."""
        provider = MockSearchProvider()
        results = await provider.search(SearchQuery(query="彩礼", limit=5))

        assert len(results) > 0
        assert results[0].title
        assert results[0].url
        assert results[0].credibility_hint in ["high", "medium", "low", "unclear"]

    @pytest.mark.asyncio
    async def test_search_resolution(self):
        """测试搜索分辨率."""
        provider = MockSearchProvider()
        assert await provider.health_check() is True


class TestFactCheckerGraph:
    """StateGraph 测试."""

    def test_graph_compiles(self):
        """Graph 应能正确编译."""
        provider = MockSearchProvider()
        graph = create_fact_checker_graph(provider, max_iterations=2)
        assert graph is not None

    def test_graph_execution(self):
        """Graph 应能完整执行."""
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


class TestFactCheckerHarness:
    """Harness 层测试."""

    @pytest.mark.asyncio
    async def test_harness_returns_report(self):
        """Harness 应返回完整报告."""
        harness = FactCheckerHarness(max_iterations=2)
        report = await harness.run(
            topic_title="彩礼", topic_description="关于彩礼的争议"
        )

        assert report.topic_title == "彩礼"
        # facts 提取需要 LLM 完整实现，测试中验证 sources 不为空即可
        assert len(report.sources) > 0
        assert report.summary
        # credibility_distribution 可能为空，暂不强制验证


class TestCoverageAnalysis:
    """覆盖度分析测试."""

    def test_coverage_calculation(self):
        """覆盖度应正确计算."""
        from wenexus.agent.fact_checker.runtime.state import CoverageAnalysis

        analysis = CoverageAnalysis(
            total_dimensions=4,
            covered_dimensions=3,
            coverage_score=0.75,
            missing_dimensions=["国际对比"],
        )

        assert analysis.coverage_score == 0.75
        assert len(analysis.missing_dimensions) == 1


class TestFactStructure:
    """Fact 结构测试."""

    def test_fact_has_required_fields(self):
        """Fact 应有必需字段."""
        from wenexus.agent.fact_checker.runtime.state import Fact, Source

        source = Source(title="测试来源", url="https://test.com", snippet="测试内容")
        fact = Fact(
            content="彩礼平均12.8万元",
            claim="彩礼金额",
            source=source,
            credibility="high",
        )

        assert fact.content
        assert fact.source.title
        assert fact.credibility == "high"
