"""
Agent Initializer

Application startup initialization for agent pool.
Imports and registers all domain service agents.
"""

import structlog

from wenexus.app.agent_pool import AgentPool
from wenexus.app.agent_registry import AgentRegistry
from wenexus.repository.checkpointer import checkpointer

logger = structlog.get_logger()

# Global registry and pool instances used by facade layer
registry = AgentRegistry()
agent_pool = AgentPool(registry, checkpointer)


def initialize_agents():
    """
    Initialize all agent configurations and instances.

    Imports domain service modules and calls their registration functions.
    Each domain service is responsible for creating and registering its own agents.
    """
    import os

    logger.info("Initializing agent pool...")

    # Register research agent only if TAVILY_API_KEY is available
    if os.getenv("TAVILY_API_KEY"):
        try:
            from wenexus.service.research_agent import research_agent

            research_agent.register_to_agent_pool(registry, agent_pool)
        except Exception as e:
            logger.warning(f"Failed to register research agent: {e}")
    else:
        logger.warning("TAVILY_API_KEY not set - research agent will not be registered")

    # Preload any singleton agents not registered via register_instance()
    agent_pool.preload_singletons()

    logger.info("Agent pool initialization completed")
