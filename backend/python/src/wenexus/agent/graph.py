"""
agent.graph - LangGraph StateGraph for WeNexus roundtable facilitator agent.

Implements a ReAct-style agent that can facilitate discussion topics,
suggest expert roles, and format discussion points using LangGraph.

Depends: langchain_openai, langgraph, config, agent.tools
Consumers: langgraph CLI (via langgraph.json)
"""

from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from wenexus.agent.tools import TOOLS
from wenexus.config import settings

_SYSTEM_PROMPT = """You are a WeNexus Roundtable Facilitator — an AI agent that helps
users design and run structured, multi-perspective discussions.

Your capabilities:
- Get the current date/time
- Format discussion outlines from multiple perspectives
- Suggest expert roles suited to any topic

Always be concise, constructive, and balanced. Proactively use your tools
when they can add value to the conversation."""


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.agent_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0.7,
    )


def _call_model(state: State) -> dict:
    """Invoke the LLM with injected system prompt and current messages."""
    llm_with_tools = _build_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=_SYSTEM_PROMPT), *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def _build_graph() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("agent", _call_model)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder


graph = _build_graph().compile()
graph.name = "Roundtable Facilitator"
