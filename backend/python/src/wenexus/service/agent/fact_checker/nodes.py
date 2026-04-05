"""Fact Checker Graph Nodes.

Depends: model.fact_report, service.agent.fact_checker.interfaces.search
Consumers: service.agent.fact_checker.graph
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from wenexus.model.base import SourceType
from wenexus.model.fact_report import (
    CoverageAnalysis,
    Fact,
    FactReport,
    SearchIteration,
    Source,
)

from .interfaces.search import SearchProvider, SearchQuery
from .state import FactCheckState


def planning_node(state: FactCheckState) -> FactCheckState:
    """规划搜索策略."""
    topic = state["topic_title"]
    queries = [
        f"{topic} 统计数据",
        f"{topic} 研究论文",
        f"{topic} 政策法规",
        f"{topic} 国际对比",
    ]
    state["search_queries"].extend(queries)
    state["current_iteration"] += 1
    state["status"] = "searching"
    return state


def search_node(
    state: FactCheckState, search_provider: SearchProvider
) -> FactCheckState:
    """执行搜索."""
    iteration = state["current_iteration"]
    queries = state["search_queries"]
    query_text = (
        queries[iteration - 1] if iteration <= len(queries) else state["topic_title"]
    )

    query = SearchQuery(query=query_text, limit=5)
    with ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: asyncio.run(search_provider.search(query)))
        results = future.result()

    sources = [
        Source(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            source_type=SourceType(r.source_type),
        )
        for r in results
    ]
    state["search_results"].extend(sources)
    state["search_iterations"].append(
        SearchIteration(
            iteration=iteration, query=query_text, results_count=len(sources)
        )
    )
    state["status"] = "extracting"
    return state


def extraction_node(state: FactCheckState) -> FactCheckState:
    """提取事实."""
    for source in state["search_results"]:
        if len(source.snippet) > 20:
            fact = Fact(
                content=source.snippet,
                claim=state["topic_title"],
                source=source,
            )
            state["extracted_facts"].append(fact)
    state["status"] = "analyzing"
    return state


def analysis_node(state: FactCheckState) -> FactCheckState:
    """分析覆盖度."""
    facts = state["extracted_facts"]
    source_types = set(f.source.source_type for f in facts)
    coverage_score = min(len(source_types) / 4.0, 1.0)
    should_continue = coverage_score < 0.7 and state["current_iteration"] < state.get(
        "max_iterations", 5
    )

    state["coverage_analysis"] = CoverageAnalysis(
        total_dimensions=4,
        covered_dimensions=len(source_types),
        coverage_score=coverage_score,
    )
    state["should_continue"] = should_continue
    return state


def synthesis_node(state: FactCheckState) -> FactCheckState:
    """生成报告."""
    import time

    facts = state["extracted_facts"]
    cred_dist: dict[str, int] = {}
    for f in facts:
        if f.source.source_type in (SourceType.GOV, SourceType.ACADEMIC):
            cred_dist["high"] = cred_dist.get("high", 0) + 1
        elif f.source.source_type == SourceType.NEWS:
            cred_dist["medium"] = cred_dist.get("medium", 0) + 1
        else:
            cred_dist["low"] = cred_dist.get("low", 0) + 1

    report = FactReport(
        topic_title=state["topic_title"],
        summary=f"提取{len(facts)}条事实，覆盖{len(cred_dist)}类来源",
        coverage_analysis=state.get("coverage_analysis"),
        credibility_distribution=cred_dist,
    )
    report.facts = facts
    report.sources = list(state["search_results"])

    state["final_report"] = report
    state["status"] = "completed"
    state["end_time"] = time.time()
    return state
