"""
Agent Configuration Model

Defines the configuration schema for agents.
"""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class AgentConfig:
    """
    Agent configuration data model.

    Attributes:
        agent_id: Unique identifier for the agent
        name: Human-readable name
        description: Description of the agent's purpose
        tools: List of tools available to the agent
        instructions: System prompt/instructions for the agent
        subagents: Optional list of sub-agents
        model: Optional language model configuration
        scope: Lifecycle scope - 'singleton' (one instance shared) or 'prototype' (new instance per request)
        recursion_limit: Maximum recursion depth for the agent
    """

    agent_id: str
    name: str
    description: str
    tools: list[Any]
    instructions: str
    subagents: list | None = None
    model: Any | None = None
    scope: Literal["singleton", "prototype"] = "singleton"
    recursion_limit: int = 1000
    extra_config: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        if self.scope not in ["singleton", "prototype"]:
            raise ValueError(
                f"Invalid scope: {self.scope}. Must be 'singleton' or 'prototype'"
            )
