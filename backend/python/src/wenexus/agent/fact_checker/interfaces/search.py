"""搜索提供方抽象接口.

支持 Mock/Tavily/Perplexity/DuckDuckGo 等多种搜索后端.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    """统一搜索结果格式."""

    title: str
    url: str
    snippet: str
    source_type: str = "web"  # web, academic, news, gov
    published_date: str | None = None
    credibility_hint: str | None = None  # high/medium/low/unclear


@dataclass
class SearchQuery:
    """搜索查询."""

    query: str
    limit: int = 10


class SearchProvider(ABC):
    """搜索提供方抽象基类.

    实现类: MockSearchProvider, TavilySearchProvider, PerplexitySearchProvider
    """

    name: str = "abstract"

    @abstractmethod
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """执行搜索.

        Args:
            query: 搜索查询

        Returns:
            按相关度排序的搜索结果列表
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """检查服务可用性."""
        pass
