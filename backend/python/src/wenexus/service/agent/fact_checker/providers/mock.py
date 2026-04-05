"""Mock search provider.

Depends: service.agent.fact_checker.interfaces.search
Consumers: tests, dev 环境
"""

from ..interfaces.search import SearchProvider, SearchQuery, SearchResult


class MockSearchProvider(SearchProvider):
    """Mock provider for dev/testing."""

    name = "mock"

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """Return mock results."""
        return [
            SearchResult(
                title="2024年彩礼统计",
                url="https://example.com/stats",
                snippet="平均12.8万元",
                source_type="gov",
                credibility_hint="high",
            ),
            SearchResult(
                title="彩礼研究会",
                url="https://example.com/paper",
                snippet="社会学分析",
                source_type="academic",
                credibility_hint="high",
            ),
        ]

    async def health_check(self) -> bool:
        """Always healthy."""
        return True
