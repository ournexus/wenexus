"""LangGraph SDK compatible assistants API router.

This router implements the /assistants endpoints for LangGraph SDK compatibility.
It manages assistant (agent) configurations and provides CRUD operations.

Depends: fastapi, app.agent_registry, typing
Consumers: main.py (router inclusion)
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from wenexus.app.agent_registry import get_agent_registry

router = APIRouter(prefix="/assistants", tags=["assistants"])


@router.get("", response_model=list[dict[str, Any]])
async def list_assistants(
    limit: int = 100, offset: int = 0, registry=get_agent_registry
) -> list[dict[str, Any]]:
    """List available assistants (agents).

    Args:
        limit: Maximum number of assistants to return
        offset: Number of assistants to skip
        registry: Agent registry instance from dependency injection

    Returns:
        List of assistant configurations in LangGraph SDK format
    """
    configs = registry.list_configs()

    # Convert AgentConfig to LangGraph SDK format
    assistants = []
    for config in configs[offset : offset + limit]:
        assistant = {
            "assistant_id": config.agent_id,
            "name": config.name,
            "description": config.description,
            "created_at": "2024-01-01T00:00:00Z",  # TODO: Add timestamps
            "updated_at": "2024-01-01T00:00:00Z",  # TODO: Add timestamps
            "config": {
                "recursion_limit": config.recursion_limit,
                **(config.model if isinstance(config.model, dict) else {}),
            },
            "metadata": {
                "created_by": "system",
                "scope": config.scope,
                "has_tools": len(config.tools) > 0,
                "has_subagents": len(config.subagents) > 0,
            },
            "version": 1,
        }
        assistants.append(assistant)

    return assistants


@router.get("/{assistant_id}", response_model=dict[str, Any])
async def get_assistant(
    assistant_id: str, registry=get_agent_registry
) -> dict[str, Any]:
    """Get specific assistant by ID.

    Args:
        assistant_id: Assistant identifier
        registry: Agent registry instance from dependency injection

    Returns:
        Assistant configuration in LangGraph SDK format
    """
    config = registry.get_config(assistant_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {assistant_id} not found",
        )

    return {
        "assistant_id": config.agent_id,
        "name": config.name,
        "description": config.description,
        "created_at": "2024-01-01T00:00:00Z",  # TODO: Add timestamps
        "updated_at": "2024-01-01T00:00:00Z",  # TODO: Add timestamps
        "config": {
            "recursion_limit": config.recursion_limit,
            **(config.model if isinstance(config.model, dict) else {}),
        },
        "metadata": {
            "created_by": "system",
            "scope": config.scope,
            "has_tools": len(config.tools) > 0,
            "has_subagents": len(config.subagents) > 0,
        },
        "version": 1,
    }


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_assistant(
    assistant_data: dict[str, Any], registry=get_agent_registry
) -> dict[str, Any]:
    """Create new assistant (agent configuration).

    Args:
        assistant_data: Assistant configuration data
        registry: Agent registry instance from dependency injection

    Returns:
        Created assistant configuration
    """
    # Extract required fields
    assistant_id = assistant_data.get("assistant_id")
    name = assistant_data.get("name", "Unnamed Assistant")
    description = assistant_data.get("description", "")

    if not assistant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="assistant_id is required"
        )

    # Check if assistant already exists
    if registry.has_config(assistant_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Assistant {assistant_id} already exists",
        )

    # TODO: Convert LangGraph SDK format to AgentConfig
    # For now, create a basic configuration
    from wenexus.app.agent_config import AgentConfig

    config = AgentConfig(
        agent_id=assistant_id,
        name=name,
        description=description,
        scope="prototype",  # User-created agents are prototypes by default
        recursion_limit=assistant_data.get("config", {}).get("recursion_limit", 50),
    )

    registry.register(config)

    return {
        "assistant_id": config.agent_id,
        "name": config.name,
        "description": config.description,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "config": {"recursion_limit": config.recursion_limit},
        "metadata": {"created_by": "user", "scope": config.scope},
        "version": 1,
    }


@router.put("/{assistant_id}", response_model=dict[str, Any])
async def update_assistant(
    assistant_id: str, assistant_data: dict[str, Any], registry=get_agent_registry
) -> dict[str, Any]:
    """Update assistant configuration.

    Args:
        assistant_id: Assistant identifier
        assistant_data: Updated assistant data
        registry: Agent registry instance from dependency injection

    Returns:
        Updated assistant configuration
    """
    config = registry.get_config(assistant_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {assistant_id} not found",
        )

    # TODO: Implement update logic
    # For now, return existing configuration
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Assistant updates not yet implemented",
    )


@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(assistant_id: str, registry=get_agent_registry) -> None:
    """Delete assistant configuration.

    Args:
        assistant_id: Assistant identifier
        registry: Agent registry instance from dependency injection
    """
    config = registry.get_config(assistant_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {assistant_id} not found",
        )

    # TODO: Implement delete logic
    # For now, raise not implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Assistant deletion not yet implemented",
    )
