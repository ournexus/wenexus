"""
Assistants Router

Provides endpoints for managing assistants compatible with LangGraph SDK.
Dynamically discovers system agents from agent_registry and manages user-created assistants.
"""

from datetime import datetime

import structlog
from fastapi import APIRouter, HTTPException

from wenexus.app.agent_initializer import registry
from wenexus.model.assistant import Assistant, AssistantMetadata, AssistantSearchRequest

logger = structlog.get_logger()
router = APIRouter(prefix="/assistants", tags=["assistants"])

# User-created assistants (not from agent_registry)
_user_assistants: dict[str, Assistant] = {}


def _build_assistant_from_agent_config(agent_id: str) -> Assistant:
    """
    Convert AgentConfig from registry to Assistant model.

    System agents are automatically discovered from agent_registry,
    eliminating the need to manually maintain assistant configurations.
    """
    config = registry.get_config(agent_id)
    return Assistant(
        assistant_id=config.agent_id,
        graph_id=config.agent_id,
        name=config.name,
        config={"scope": config.scope, "recursion_limit": config.recursion_limit},
        metadata=AssistantMetadata(created_by="system"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1,
    )


def _get_all_assistants() -> dict[str, Assistant]:
    """
    Get all assistants (system agents + user-created assistants).

    System agents are dynamically loaded from agent_registry,
    ensuring consistency with available agent implementations.
    """
    # System agents from registry
    system_assistants = {
        agent_id: _build_assistant_from_agent_config(agent_id)
        for agent_id in registry.get_agent_ids()
    }

    # Merge with user-created assistants
    return {**system_assistants, **_user_assistants}


@router.post("/search")
async def search_assistants(request: AssistantSearchRequest = None):
    """
    Search for assistants.

    Returns list of assistants matching the search criteria.
    System agents are automatically discovered from agent_registry.
    Frontend SDK expects at least one assistant with metadata.created_by === "system".
    """
    logger.info("Searching assistants")

    assistants = list(_get_all_assistants().values())

    if request and request.graph_id:
        assistants = [a for a in assistants if a.graph_id == request.graph_id]

    if request and request.metadata:
        for key, value in request.metadata.items():
            assistants = [
                a for a in assistants if getattr(a.metadata, key, None) == value
            ]

    offset = request.offset if request else 0
    limit = request.limit if request else 10

    return [a.model_dump() for a in assistants[offset : offset + limit]]


@router.get("/{assistant_id}")
async def get_assistant(assistant_id: str):
    """
    Get assistant by ID.

    Supports both system agents (from agent_registry) and user-created assistants.
    """
    logger.info(f"Getting assistant: {assistant_id}")

    assistants = _get_all_assistants()
    if assistant_id not in assistants:
        raise HTTPException(status_code=404, detail="Assistant not found")

    return assistants[assistant_id].model_dump()


@router.post("")
async def create_assistant(
    graph_id: str = "agent",
    name: str | None = None,
    config: dict | None = None,
    metadata: dict | None = None,
):
    """
    Create a new user-defined assistant.

    System agents from agent_registry cannot be created via API (they are auto-discovered).
    This endpoint creates user-defined assistants with custom configurations.
    """
    from uuid import uuid4

    assistant_id = str(uuid4())
    assistant = Assistant(
        assistant_id=assistant_id,
        graph_id=graph_id,
        name=name or f"Assistant-{assistant_id[:8]}",
        config=config or {},
        metadata=AssistantMetadata(**(metadata or {})),
    )

    _user_assistants[assistant_id] = assistant
    logger.info(f"Created user assistant: {assistant_id}")

    return assistant.model_dump()


@router.patch("/{assistant_id}")
async def update_assistant(
    assistant_id: str,
    name: str | None = None,
    config: dict | None = None,
    metadata: dict | None = None,
):
    """
    Update an existing user-created assistant.

    System agents from agent_registry are read-only and cannot be modified via API.
    """
    # Only allow updating user-created assistants
    if assistant_id not in _user_assistants:
        assistants = _get_all_assistants()
        if assistant_id in assistants:
            raise HTTPException(
                status_code=403,
                detail="Cannot modify system agents. System agents are managed via agent_registry.",
            )
        raise HTTPException(status_code=404, detail="Assistant not found")

    assistant = _user_assistants[assistant_id]

    if name:
        assistant.name = name
    if config:
        assistant.config.update(config)
    if metadata:
        for key, value in metadata.items():
            setattr(assistant.metadata, key, value)

    assistant.updated_at = datetime.utcnow()
    logger.info(f"Updated user assistant: {assistant_id}")

    return assistant.model_dump()


@router.delete("/{assistant_id}")
async def delete_assistant(assistant_id: str):
    """
    Delete a user-created assistant.

    System agents from agent_registry cannot be deleted via API.
    """
    # Only allow deleting user-created assistants
    if assistant_id not in _user_assistants:
        assistants = _get_all_assistants()
        if assistant_id in assistants:
            raise HTTPException(
                status_code=403,
                detail="Cannot delete system agents. System agents are managed via agent_registry.",
            )
        raise HTTPException(status_code=404, detail="Assistant not found")

    del _user_assistants[assistant_id]
    logger.info(f"Deleted user assistant: {assistant_id}")

    return {"status": "deleted", "assistant_id": assistant_id}
