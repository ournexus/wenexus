"""
Agent Pool

Manages agent instances lifecycle. Similar to Spring's ApplicationContext.
"""

import structlog
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Checkpointer

from wenexus.app.agent_config import AgentConfig
from wenexus.app.agent_registry import AgentRegistry

logger = structlog.get_logger()


class AgentPool:
    """
    Agent instance pool (similar to Spring ApplicationContext).

    Manages the lifecycle of agent instances based on their scope:
    - singleton: One instance shared across the application (cached)
    - prototype: New instance created for each request (not cached)
    """

    def __init__(self, registry: AgentRegistry, checkpointer: Checkpointer):
        """
        Initialize agent pool.

        Args:
            registry: Agent configuration registry
            checkpointer: Checkpointer for agent state persistence
        """
        self._registry = registry
        self._checkpointer = checkpointer
        self._singletons: dict[str, CompiledStateGraph] = {}

    def get_agent(self, agent_id: str) -> CompiledStateGraph:
        """
        Get agent instance by ID.

        For singleton agents, returns cached instance.
        For prototype agents, creates new instance each time.

        Args:
            agent_id: Agent identifier

        Returns:
            Compiled agent graph

        Raises:
            ValueError: If agent_id is not registered
        """
        config = self._registry.get_config(agent_id)

        if config.scope == "singleton":
            if agent_id not in self._singletons:
                logger.warning(
                    f"Singleton agent {agent_id} not preloaded. "
                    "This should have been created at startup."
                )
                self._singletons[agent_id] = self._create_agent(config)
            return self._singletons[agent_id]
        else:
            # prototype: create new instance
            logger.debug(f"Creating new prototype instance for agent: {agent_id}")
            return self._create_agent(config)

    def register_instance(self, agent_id: str, agent: CompiledStateGraph) -> None:
        """
        Register an already-created agent instance.

        This method allows domain services to create and register their own agents,
        instead of having AgentPool create them.

        Args:
            agent_id: Agent identifier
            agent: Pre-created agent instance

        Raises:
            ValueError: If agent_id is not registered in the registry
        """
        # Verify agent_id is registered in config
        config = self._registry.get_config(agent_id)

        if config.scope == "singleton":
            self._singletons[agent_id] = agent
            logger.info(f"Registered singleton agent instance: {agent_id}")
        else:
            logger.warning(
                f"Agent {agent_id} has scope={config.scope}, but register_instance "
                "is typically used for singletons. Consider using get_agent() instead."
            )

    def preload_singletons(self) -> None:
        """
        Preload all singleton agents that haven't been registered yet.

        This is now a fallback mechanism - most agents should be registered
        via register_instance() from their domain service modules.
        """
        singleton_configs = [
            config
            for config in self._registry.list_agents()
            if config.scope == "singleton"
        ]

        if not singleton_configs:
            logger.info("No singleton agents to preload")
            return

        # Only create agents that haven't been registered yet
        unregistered = [
            c for c in singleton_configs if c.agent_id not in self._singletons
        ]

        if not unregistered:
            logger.info(
                f"All singleton agents already registered: {list(self._singletons.keys())}"
            )
            return

        logger.info(
            f"Preloading {len(unregistered)} unregistered singleton agent(s)..."
        )
        for config in unregistered:
            try:
                logger.info(f"Creating singleton agent: {config.agent_id}")
                self._singletons[config.agent_id] = self._create_agent(config)
                logger.info(f"Successfully created agent: {config.agent_id}")
            except Exception as e:
                logger.error(
                    f"Failed to create agent {config.agent_id}: {e}", exc_info=True
                )
                raise RuntimeError(
                    f"Failed to preload singleton agent {config.agent_id}"
                ) from e

        logger.info(f"All singleton agents ready: {list(self._singletons.keys())}")

    def _create_agent(self, config: AgentConfig) -> CompiledStateGraph:
        """
        Create agent instance from configuration.

        Args:
            config: Agent configuration

        Returns:
            Compiled agent graph
        """
        from deepagents import create_deep_agent

        logger.debug(f"Building agent: {config.agent_id}")

        agent = create_deep_agent(
            tools=config.tools,
            system_prompt=config.instructions,
            subagents=config.subagents,
            model=config.model,
            checkpointer=self._checkpointer,
        ).with_config({"recursion_limit": config.recursion_limit})

        return agent

    def get_loaded_singletons(self) -> list[str]:
        """Get list of loaded singleton agent IDs."""
        return list(self._singletons.keys())

    def clear_cache(self) -> None:
        """Clear singleton cache (useful for testing)."""
        logger.warning("Clearing agent pool cache")
        self._singletons.clear()
