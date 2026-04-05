"""service.agent.fact_checker - Fact Checker Deep Agent 包。"""

from .agent import FactCheckerAgent
from .interfaces.search import SearchProvider
from .providers.mock import MockSearchProvider

__all__ = [
    "FactCheckerAgent",
    "SearchProvider",
    "MockSearchProvider",
]
