"""Fact Checker interfaces - 抽象层定义."""

from .search import SearchProvider, SearchQuery, SearchResult

__all__ = ["SearchProvider", "SearchResult", "SearchQuery"]
