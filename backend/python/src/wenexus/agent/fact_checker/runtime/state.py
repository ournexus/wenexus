"""Fact Checker State Definitions.

TypedDict state for LangGraph StateGraph.
参考: /Users/mac/Desktop/code-open/deep_research_from_scratch/src/deep_research_from_scratch/state_research.py
"""

import operator
from dataclasses import dataclass, field
from typing import Annotated, Literal

from typing_extensions import TypedDict


@dataclass
class Source:
    """事实来源."""

    title: str
    url: str
    snippet: str
    source_type: str = "web"  # web, academic, news, gov
    published_date: str | None = None
    credibility: Literal["high", "medium", "low", "uncertain"] = "uncertain"


@dataclass
class Fact:
    """提取出来的事实."""

    content: str
    claim: str  # 原始主张
    source: Source
    credibility: Literal["high", "medium", "low", "uncertain"] = "uncertain"
    verification_status: Literal["verified", "pending", "disputed"] = "pending"
    notes: str = ""  # 验证备注


@dataclass
class CoverageAnalysis:
    """覆盖度分析."""

    total_dimensions: int  # 应该覆盖的维度数
    covered_dimensions: int  # 已覆盖的维度数
    coverage_score: float  # 0.0 ~ 1.0
    missing_dimensions: list[str] = field(default_factory=list)
    recommendation: str = ""  # 继续搜索还是停止


@dataclass
class SearchIteration:
    """单次搜索迭代记录."""

    iteration: int
    query: str
    results_count: int
    key_findings: list[str] = field(default_factory=list)


@dataclass
class FactReport:
    """最终事实报告."""

    topic_title: str
    summary: str
    facts: list[Fact] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    coverage_analysis: CoverageAnalysis | None = None
    credibility_distribution: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转为可序列化的字典."""
        return {
            "topic_title": self.topic_title,
            "summary": self.summary,
            "facts": [
                {
                    "content": f.content,
                    "claim": f.claim,
                    "source": {
                        "title": f.source.title,
                        "url": f.source.url,
                        "source_type": f.source.source_type,
                        "credibility": f.source.credibility,
                    },
                    "credibility": f.credibility,
                    "verification_status": f.verification_status,
                    "notes": f.notes,
                }
                for f in self.facts
            ],
            "sources_count": len(self.sources),
            "coverage_score": self.coverage_analysis.coverage_score
            if self.coverage_analysis
            else 0.0,
            "credibility_distribution": self.credibility_distribution,
        }


class FactCheckState(TypedDict):
    """StateGraph 状态定义.

    参考 deep_research_from_scratch 的 ResearcherState 设计.
    """

    # Input
    topic_id: str | None
    topic_title: str
    topic_description: str | None

    # Control
    current_iteration: int
    max_iterations: int
    should_continue: bool

    # Search
    search_queries: Annotated[list[str], operator.add]
    search_results: Annotated[list[Source], operator.add]
    search_iterations: list[SearchIteration]

    # Facts
    extracted_facts: Annotated[list[Fact], operator.add]

    # Analysis
    coverage_analysis: CoverageAnalysis | None

    # Output
    final_report: FactReport | None

    # Metadata
    status: Literal[
        "pending",
        "planning",
        "searching",
        "extracting",
        "analyzing",
        "validating",
        "completed",
        "error",
    ]
    error: str | None
    total_tokens: int
    start_time: float | None
    end_time: float | None
