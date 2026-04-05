"""
Agent Registry

Manages static agent configurations. Similar to Spring's BeanDefinitionRegistry.
"""

import structlog

from wenexus.app.agent_config import AgentConfig

logger = structlog.get_logger()


class AgentRegistry:
    """
    Agent configuration registry.

    Manages static agent configurations that define how agents should be created.
    Does not manage actual agent instances (that's AgentPool's job).
    """

    def __init__(self):
        self._configs: dict[str, AgentConfig] = {}

    def register(self, config: AgentConfig) -> None:
        """
        Register an agent configuration.

        Args:
            config: Agent configuration to register

        Raises:
            ValueError: If agent_id is already registered
        """
        if config.agent_id in self._configs:
            raise ValueError(f"Agent already registered: {config.agent_id}")

        self._configs[config.agent_id] = config
        logger.info(
            f"Registered agent config: {config.agent_id} (scope={config.scope})"
        )

    def get_config(self, agent_id: str) -> AgentConfig:
        """
        Get agent configuration by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent configuration

        Raises:
            ValueError: If agent_id is not registered
        """
        if agent_id not in self._configs:
            raise ValueError(
                f"Unknown agent_id: {agent_id}. "
                f"Available agents: {list(self._configs.keys())}"
            )
        return self._configs[agent_id]

    def has_agent(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._configs

    def list_agents(self) -> list[AgentConfig]:
        """List all registered agent configurations."""
        return list(self._configs.values())

    def get_agent_ids(self) -> list[str]:
        """Get all registered agent IDs."""
        return list(self._configs.keys())
