"""LangGraph SDK compatible threads API router.

This router implements the /threads endpoints for LangGraph SDK compatibility.
It manages conversation threads and their state.

Depends: fastapi, app.agent_registry, typing
Consumers: main.py (router inclusion)
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from wenexus.app.agent_registry import get_agent_registry

router = APIRouter(prefix="/threads", tags=["threads"])


# In-memory thread registry (TODO: Replace with persistent storage)
_thread_registry: dict[str, dict[str, Any]] = {}


class ThreadCreateRequest(BaseModel):
    """Request model for creating a thread."""

    assistant_id: str | None = None
    metadata: dict[str, Any] | None = None


class ThreadUpdateRequest(BaseModel):
    """Request model for updating a thread."""

    metadata: dict[str, Any] | None = None
    status: str | None = None


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_thread(
    request: ThreadCreateRequest, registry=get_agent_registry
) -> dict[str, Any]:
    """Create new conversation thread.

    Args:
        request: Thread creation request
        registry: Agent registry instance from dependency injection

    Returns:
        Created thread information
    """
    import uuid

    thread_id = str(uuid.uuid4())

    # Validate assistant_id if provided
    if request.assistant_id and not registry.has_config(request.assistant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {request.assistant_id} not found",
        )

    # Create thread record
    thread = {
        "thread_id": thread_id,
        "assistant_id": request.assistant_id,
        "created_at": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "active",
        "metadata": request.metadata or {},
        "values": {
            "messages": [],
            "todos": [],
            "files": {},
        },
    }

    _thread_registry[thread_id] = thread

    return thread


@router.get("/{thread_id}", response_model=dict[str, Any])
async def get_thread(thread_id: str) -> dict[str, Any]:
    """Get thread by ID.

    Args:
        thread_id: Thread identifier

    Returns:
        Thread information
    """
    thread = _thread_registry.get(thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    return thread


@router.patch("/{thread_id}", response_model=dict[str, Any])
async def update_thread(thread_id: str, request: ThreadUpdateRequest) -> dict[str, Any]:
    """Update thread metadata or status.

    Args:
        thread_id: Thread identifier
        request: Update request

    Returns:
        Updated thread information
    """
    thread = _thread_registry.get(thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    # Update fields
    if request.metadata is not None:
        thread["metadata"].update(request.metadata)

    if request.status is not None:
        thread["status"] = request.status

    thread["updated_at"] = "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp

    return thread


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: str) -> None:
    """Delete thread.

    Args:
        thread_id: Thread identifier
    """
    if thread_id not in _thread_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    del _thread_registry[thread_id]


@router.get("/{thread_id}/history", response_model=list[dict[str, Any]])
async def get_thread_history(
    thread_id: str, limit: int = 100, offset: int = 0
) -> list[dict[str, Any]]:
    """Get thread checkpoint history.

    Args:
        thread_id: Thread identifier
        limit: Maximum number of checkpoints to return
        offset: Number of checkpoints to skip

    Returns:
        List of checkpoint history
    """
    thread = _thread_registry.get(thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    # TODO: Implement actual checkpoint history from checkpointer
    # For now, return empty list
    return []


@router.get("/{thread_id}/state", response_model=dict[str, Any])
async def get_thread_state(thread_id: str) -> dict[str, Any]:
    """Get current thread state.

    Args:
        thread_id: Thread identifier

    Returns:
        Current thread state
    """
    thread = _thread_registry.get(thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    return thread["values"]


@router.post("/{thread_id}/state", response_model=dict[str, Any])
async def update_thread_state(
    thread_id: str, state_update: dict[str, Any]
) -> dict[str, Any]:
    """Update thread state.

    Args:
        thread_id: Thread identifier
        state_update: State update data

    Returns:
        Updated thread state
    """
    thread = _thread_registry.get(thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )

    # Update state values
    if "values" in state_update:
        thread["values"].update(state_update["values"])

    thread["updated_at"] = "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp

    return thread["values"]


@router.get("", response_model=list[dict[str, Any]])
async def list_threads(
    limit: int = 100,
    offset: int = 0,
    assistant_id: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """List threads with optional filtering.

    Args:
        limit: Maximum number of threads to return
        offset: Number of threads to skip
        assistant_id: Filter by assistant ID
        status: Filter by status

    Returns:
        List of threads
    """
    threads = list(_thread_registry.values())

    # Apply filters
    if assistant_id:
        threads = [t for t in threads if t.get("assistant_id") == assistant_id]

    if status:
        threads = [t for t in threads if t.get("status") == status]

    # Sort by updated_at (TODO: Implement proper sorting)
    threads.sort(key=lambda t: t.get("updated_at", ""), reverse=True)

    # Apply pagination
    return threads[offset : offset + limit]
