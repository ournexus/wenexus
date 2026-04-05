"""Fact Checker LangGraph State — 仅运行时状态定义。

领域模型（Source, Fact, FactReport 等）在 model.fact_report 中定义。
此文件只包含 LangGraph StateGraph 需要的 TypedDict。

Depends: model.fact_report, model.base
Consumers: service.agent.fact_checker.graph, service.agent.fact_checker.nodes
"""

import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict

from wenexus.model.fact_report import (
    CoverageAnalysis,
    Fact,
    FactReport,
    SearchIteration,
    Source,
)


class FactCheckState(TypedDict):
    """StateGraph 状态定义."""

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
