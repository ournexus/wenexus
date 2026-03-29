"""
agent.graph - LangGraph StateGraph for WeNexus roundtable facilitator agent.

Implements a ReAct-style agent that can facilitate discussion topics,
suggest expert roles, and format discussion points using LangGraph.

Depends: langchain_openai, langgraph, config, agent.tools
Consumers: langgraph CLI (via langgraph.json), service.roundtable
"""

from typing import Annotated

import structlog
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from wenexus.agent.tools import TOOLS
from wenexus.config import settings

logger = structlog.get_logger()

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
    return ChatOpenAI(  # type: ignore[call-arg]
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


async def invoke_facilitator(
    topic_title: str,
    topic_description: str | None,
    experts: list[dict],
    user_message: str,
    expert_replies: list[dict],
    recent_messages: list[dict] | None = None,
) -> str | None:
    """Invoke the facilitator agent to synthesize expert responses and guide discussion.

    Args:
        topic_title: Discussion topic title.
        topic_description: Topic description (optional).
        experts: Expert dicts with keys: id, name, role, stance.
        user_message: The user's message that triggered this round.
        expert_replies: Expert reply dicts with keys: content, expertId.
        recent_messages: Earlier conversation messages for context.

    Returns:
        Facilitator response text, or None on failure.
    """
    expert_map = {e["id"]: e["name"] for e in experts}

    parts = [f"## Discussion Topic: {topic_title}"]
    if topic_description:
        parts.append(f"Description: {topic_description}")

    panel_lines = [
        f"- {e['name']} ({e['role']}, {e['stance']} stance)" for e in experts
    ]
    if panel_lines:
        parts.append("\n## Expert Panel\n" + "\n".join(panel_lines))

    if recent_messages:
        history = [
            f"[{m.get('role', '?')}]: {m.get('content', '')[:300]}"
            for m in recent_messages[-5:]
        ]
        parts.append("\n## Recent Discussion\n" + "\n".join(history))

    parts.append(f"\n## Current User Message\n{user_message}")

    if expert_replies:
        reply_lines = [
            f"[{expert_map.get(r.get('expertId'), 'Expert')}]: {r['content']}"
            for r in expert_replies
        ]
        parts.append("\n## Expert Responses This Round\n" + "\n".join(reply_lines))

    parts.append(
        "\n## Your Task\n"
        "Provide a concise facilitator synthesis (2-4 paragraphs):\n"
        "1. Highlight key agreements and disagreements among the experts.\n"
        "2. Surface nuances or blind spots the experts may have missed.\n"
        "3. Suggest one or two questions to deepen the discussion."
    )

    prompt = "\n".join(parts)

    try:
        result = await graph.ainvoke({"messages": [HumanMessage(content=prompt)]})  # type: ignore[arg-type,call-overload]
        messages = result.get("messages", [])
        if messages:
            last = messages[-1]
            if hasattr(last, "content") and last.content:
                return str(last.content)
    except Exception as exc:
        await logger.aerror("facilitator_invoke_error", error=str(exc))

    return None
