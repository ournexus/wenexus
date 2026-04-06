"""Deep Agent implementation for Fact Checker.

This module refactors the original FactChecker to use deepagents framework,
providing a more flexible and powerful fact checking agent with planning,
sub-agents, and file system capabilities.

Depends: deepagents, typing, logging
Consumers: agent_registry, service initialization
"""

import structlog
from deepagents import create_deep_agent

from wenexus.app.agent_config import AgentConfig
from wenexus.repository.checkpointer import checkpointer
from wenexus.service.agent.fact_checker.providers.mock import MockSearchProvider

logger = structlog.get_logger()

# Agent configuration
AGENT_ID = "fact_checker"
AGENT_NAME = "Fact Checker Agent"
AGENT_DESCRIPTION = "Advanced fact checking agent with deep analysis capabilities"

# Fact checking instructions
FACT_CHECKER_INSTRUCTIONS = """
You are an advanced Fact Checker agent. Your task is to thoroughly investigate claims and provide evidence-based analysis.

Your approach should be:
1. Systematic - break down complex claims into verifiable components
2. Thorough - search multiple sources and cross-reference information
3. Critical - evaluate source credibility and potential biases
4. Clear - present findings in an organized, accessible manner

For each claim, you should:
- Identify the core assertions to verify
- Search for relevant evidence from multiple perspectives
- Analyze the credibility and reliability of sources
- Provide a clear assessment with supporting evidence
- Note any uncertainties or limitations in your analysis

Always maintain objectivity and base your conclusions on verifiable evidence.
"""


# Search tool for fact checking
def search_tool(query: str) -> str:
    """Search tool for fact checking queries.

    Args:
        query: Search query string

    Returns:
        Search results as formatted text
    """
    search_provider = MockSearchProvider()
    results = search_provider.search(query)

    formatted_results = []
    for result in results:
        formatted_results.append(
            f"Source: {result.title}\n"
            f"URL: {result.url}\n"
            f"Snippet: {result.snippet}\n"
            f"Relevance: {result.relevance_score}\n"
        )

    return "\n---\n".join(formatted_results)


# Create the deep agent instance
logger.info(f"Creating {AGENT_NAME}...")

fact_checker_config = AgentConfig(
    agent_id=AGENT_ID,
    name=AGENT_NAME,
    description=AGENT_DESCRIPTION,
    tools=[search_tool],
    instructions=FACT_CHECKER_INSTRUCTIONS,
    scope="singleton",
    recursion_limit=50,
)

# Create the agent
agent = create_deep_agent(
    tools=fact_checker_config.tools,
    system_prompt=fact_checker_config.instructions,
    model=None,  # Use default model
    checkpointer=checkpointer,
).with_config({"recursion_limit": fact_checker_config.recursion_limit})

logger.info(f"{AGENT_NAME} created successfully")


def register_to_agent_pool(registry, pool) -> None:
    """Register this fact checker agent to the global agent pool.

    Args:
        registry: Global agent registry
        pool: Global agent pool
    """
    # Register configuration
    registry.register(fact_checker_config)

    # Register the pre-created agent instance
    pool.register_instance(AGENT_ID, agent)
    logger.info(f"{AGENT_NAME} registered to agent pool")


# Legacy compatibility wrapper
class FactCheckerAgent:
    """Legacy compatibility wrapper for the new deep agent implementation."""

    def __init__(self, search_provider=None):
        """Initialize with optional search provider.

        Args:
            search_provider: Search provider (ignored, using deepagents)
        """
        self._agent = agent
        self._search_provider = search_provider or MockSearchProvider()

    def card(self) -> dict:
        """Return agent card information."""
        return {
            "name": AGENT_NAME,
            "description": AGENT_DESCRIPTION,
            "agent_id": AGENT_ID,
            "version": "2.0.0",
            "type": "deep_agent",
        }

    async def health_check(self) -> dict:
        """Check agent health."""
        return {
            "status": "healthy",
            "agent_id": AGENT_ID,
            "type": "deep_agent",
        }

    async def run(self, task_input):
        """Run the fact checking task.

        Args:
            task_input: Task input with topic information

        Returns:
            Task output with fact checking results
        """
        # Extract topic information
        params = task_input.params
        topic_title = params.get("topic_title", "Unknown Topic")
        topic_description = params.get("topic_description", "")

        # Create input for deep agent
        agent_input = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Please fact check the following topic:\n\nTitle: {topic_title}\n\nDescription: {topic_description}\n\nProvide a comprehensive fact-checking analysis with sources and credibility assessment.",
                }
            ]
        }

        try:
            # Run the deep agent
            result = await self._agent.ainvoke(agent_input)

            # Extract the analysis from the result
            messages = result.get("messages", [])
            analysis = ""

            for message in messages:
                if message.get("type") == "ai":
                    content = message.get("content", "")
                    if content and not content.startswith(analysis):
                        analysis = content
                        break

            # Return in legacy format
            return {
                "status": "success",
                "result": {
                    "topic_title": topic_title,
                    "summary": analysis,
                    "facts_count": 0,  # TODO: Extract from analysis
                    "sources_count": 0,  # TODO: Extract from analysis
                    "credibility_distribution": {},  # TODO: Extract from analysis
                },
            }

        except Exception as e:
            logger.error(f"Fact checker agent error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
