"""搜索提供方抽象接口.

支持 Mock/Tavily/Perplexity/DuckDuckGo 等多种搜索后端.

Depends: (无)
Consumers: service.agent.fact_checker.nodes, service.agent.fact_checker.providers
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
    """搜索提供方抽象基类."""

    name: str = "abstract"

    @abstractmethod
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """执行搜索."""

    @abstractmethod
    async def health_check(self) -> bool:
        """检查服务可用性."""
