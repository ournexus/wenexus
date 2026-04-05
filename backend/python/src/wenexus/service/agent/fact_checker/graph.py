"""Fact Checker StateGraph.

Depends: langgraph, service.agent.fact_checker.nodes, service.agent.fact_checker.state
Consumers: service.agent.fact_checker.agent
"""

import time
from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .interfaces.search import SearchProvider
from .nodes import (
    analysis_node,
    extraction_node,
    planning_node,
    search_node,
    synthesis_node,
)
from .state import FactCheckState


def create_fact_checker_graph(
    search_provider: SearchProvider, max_iterations: int = 3
) -> CompiledStateGraph:
    """创建 Fact Checker Graph."""

    def init(state: FactCheckState) -> FactCheckState:
        state["current_iteration"] = 0
        state["should_continue"] = True
        state["status"] = "pending"
        state["search_queries"] = []
        state["search_results"] = []
        state["extracted_facts"] = []
        state["search_iterations"] = []
        state["total_tokens"] = 0
        state["start_time"] = time.time()
        return state

    def router(state: FactCheckState) -> Literal["loop", "done"]:
        if state["should_continue"] and state["current_iteration"] < max_iterations:
            return "loop"
        return "done"

    builder = StateGraph(FactCheckState)
    builder.add_node("init", init)
    builder.add_node("plan", planning_node)
    builder.add_node("search", lambda s: search_node(s, search_provider))
    builder.add_node("extract", extraction_node)
    builder.add_node("analyze", analysis_node)
    builder.add_node("synthesize", synthesis_node)

    builder.add_edge(START, "init")
    builder.add_edge("init", "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "extract")
    builder.add_edge("extract", "analyze")
    builder.add_conditional_edges(
        "analyze", router, {"loop": "plan", "done": "synthesize"}
    )
    builder.add_edge("synthesize", END)

    return builder.compile()
