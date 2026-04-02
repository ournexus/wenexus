"""Fact Checker LangGraph Entrypoint."""

from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


@dataclass
class FactSource:
    title: str = ""
    url: str = ""
    snippet: str = ""
    credibility: str = "uncertain"


@dataclass
class FactItem:
    content: str = ""
    credibility: str = "medium"


@dataclass
class FactReport:
    topic: str = ""
    summary: str = ""
    items: list = field(default_factory=list)


class FCState(TypedDict):
    topic: str
    iteration: int
    items_found: int
    queries: list[str]
    should_continue: bool
    report: FactReport | None


def create_fact_checker_graph_entrypoint() -> CompiledStateGraph:
    """创建简单可用的 Fact Checker Graph."""

    def init(state: FCState) -> FCState:
        state["iteration"] = 0
        state["items_found"] = 0
        state["queries"] = [f"{state['topic']} 数据", f"{state['topic']} 研究"]
        state["should_continue"] = True
        return state

    def plan(state: FCState) -> FCState:
        state["iteration"] += 1
        return state

    def search(state: FCState) -> FCState:
        state["items_found"] = 5
        return state

    def analyze(state: FCState) -> FCState:
        state["should_continue"] = state["iteration"] < 3
        return state

    def report(state: FCState) -> FCState:
        state["report"] = FactReport(
            topic=state["topic"],
            summary=f"已完成{state['iteration']}轮搜索，找到相关事实",
            items=[FactItem(content="示例事实", credibility="high")],
        )
        return state

    builder = StateGraph(FCState)
    builder.add_node("init", init)
    builder.add_node("plan", plan)
    builder.add_node("search", search)
    builder.add_node("analyze", analyze)
    builder.add_node("report", report)

    builder.add_edge(START, "init")
    builder.add_edge("init", "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "analyze")
    builder.add_conditional_edges(
        "analyze",
        lambda s: "continue" if s["should_continue"] else "done",
        {"continue": "plan", "done": "report"},
    )
    builder.add_edge("report", END)

    return builder.compile()
