"""
service.agent.facilitator.agent - Facilitator Agent（BaseAgent 实现）。

LangGraph ReAct-style agent 用于圆桌讨论 facilitation。
从 agent/graph.py 迁入，适配 BaseAgent 接口。

Depends: langgraph, langchain_openai, config, service.agent.base, model.agent
Consumers: app.agent_registry, service.roundtable
"""

from typing import Annotated

import structlog
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from wenexus.config import settings
from wenexus.model.agent import (
    AgentCard,
    AgentTaskInput,
    AgentTaskOutput,
    AgentType,
)

from ..base import BaseAgent
from .tools import TOOLS

logger = structlog.get_logger()

_SYSTEM_PROMPT = """You are a WeNexus Roundtable Facilitator — an AI agent that helps
users design and run structured, multi-perspective discussions.

Your capabilities:
- Get the current date/time
- Format discussion outlines from multiple perspectives
- Suggest expert roles suited to any topic

Always be concise, constructive, and balanced. Proactively use your tools
when they can add value to the conversation."""


class _FacilitatorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(  # type: ignore[call-arg]
        model=settings.agent_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0.7,
    )


def _call_model(state: _FacilitatorState) -> dict:
    """Invoke the LLM with injected system prompt and current messages."""
    llm_with_tools = _build_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=_SYSTEM_PROMPT), *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def _build_graph() -> StateGraph:
    builder = StateGraph(_FacilitatorState)
    builder.add_node("agent", _call_model)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder


graph = _build_graph().compile()
graph.name = "Roundtable Facilitator"


class FacilitatorAgent(BaseAgent):
    """Facilitator Agent — 圆桌讨论引导者。"""

    def card(self) -> AgentCard:
        return AgentCard(
            name="facilitator",
            display_name="圆桌引导者",
            description="引导多视角讨论，合成专家观点",
            agent_type=AgentType.FUNCTIONAL,
            capabilities=("roundtable_facilitation", "discussion_synthesis"),
        )

    async def run(self, task_input: AgentTaskInput) -> AgentTaskOutput:
        """执行 facilitation 任务。"""
        import time

        start = time.time()
        prompt = task_input.params.get("prompt", "")
        if not prompt:
            return AgentTaskOutput(
                agent_name="facilitator",
                status="error",
                error="Missing 'prompt' in params",
            )
        try:
            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=str(prompt))]}  # type: ignore[arg-type]
            )
            messages = result.get("messages", [])
            content = ""
            if messages:
                last = messages[-1]
                if hasattr(last, "content") and last.content:
                    content = str(last.content)
            elapsed = int((time.time() - start) * 1000)
            return AgentTaskOutput(
                agent_name="facilitator",
                status="completed",
                result={"content": content},
                execution_time_ms=elapsed,
            )
        except Exception as exc:
            await logger.aerror("facilitator_run_error", error=str(exc))
            return AgentTaskOutput(
                agent_name="facilitator",
                status="error",
                error=str(exc),
            )

    async def health_check(self) -> bool:
        """健康检查。"""
        return True


async def invoke_facilitator(
    topic_title: str,
    topic_description: str | None,
    experts: list[dict],
    user_message: str,
    expert_replies: list[dict],
    recent_messages: list[dict] | None = None,
) -> str | None:
    """Invoke the facilitator agent to synthesize expert responses.

    保留原有函数签名，供 service.roundtable 调用。
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
