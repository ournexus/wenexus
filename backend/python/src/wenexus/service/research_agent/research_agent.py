import os

import structlog
from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from wenexus.app.agent_config import AgentConfig
from wenexus.app.agent_pool import AgentPool
from wenexus.app.agent_registry import AgentRegistry
from wenexus.repository.checkpointer import checkpointer
from wenexus.service.research_agent.research_agent_prompt import (
    research_instructions,
    sub_critique_prompt,
    sub_research_prompt,
)
from wenexus.service.research_agent.research_agent_tools import internet_search

load_dotenv()
logger = structlog.get_logger()

# Agent configuration
AGENT_ID = "researchAgent"
AGENT_NAME = "Research Agent"
AGENT_DESCRIPTION = "Research agent for in-depth question answering"


def _get_model() -> ChatOpenAI:
    model_name = os.getenv("AGENT_MODEL") or os.getenv(
        "OPENAI_MODEL_NAME", "openai/gpt-4o-mini"
    )
    base_url = os.getenv("OPENROUTER_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    logger.info("Initializing LLM model", model=model_name, base_url=base_url)

    return ChatOpenAI(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
    )


_subagents = [
    {
        "name": "critique-agent",
        "description": "Used to critique the final report. Give this agent some information about how you want it to critique the report.",
        "system_prompt": sub_critique_prompt,
        "model": _get_model(),
        "tools": [internet_search],
    },
    {
        "name": "research-agent",
        "description": "Used to research more in depth questions. Only give this researcher one topic at a time.",
        "system_prompt": sub_research_prompt,
        "model": _get_model(),
        "tools": [internet_search],
    },
]

logger.info(f"Creating {AGENT_NAME}...")
agent = create_deep_agent(
    model=_get_model(),
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=_subagents,
    checkpointer=checkpointer,
).with_config({"recursion_limit": 1000})
logger.info(f"{AGENT_NAME} created successfully")


def register_to_agent_pool(registry: AgentRegistry, pool: AgentPool) -> None:
    """
    Register this agent to the global agent pool.

    This function should be called during application initialization.

    Args:
        registry: Global agent registry
        pool: Global agent pool
    """
    # Register configuration
    config = AgentConfig(
        agent_id=AGENT_ID,
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        tools=[internet_search],
        instructions=research_instructions,
        subagents=_subagents,
        scope="singleton",
        recursion_limit=1000,
    )
    registry.register(config)

    # Register the pre-created agent instance
    pool.register_instance(AGENT_ID, agent)
    logger.info(f"{AGENT_NAME} registered to agent pool")
