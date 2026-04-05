"""LangGraph SDK compatible runs API router.

This router implements the /runs endpoints for LangGraph SDK compatibility.
It handles stateless and stateful agent execution with streaming support.

Depends: fastapi, service.langgraph_api.run_service, typing
Consumers: main.py (router inclusion)
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from wenexus.app.agent_initializer import registry
from wenexus.service.langgraph_api.run_service import execute_stream_run

router = APIRouter(prefix="/runs", tags=["runs"])


class RunCreateRequest(BaseModel):
    """Request model for creating a run."""

    assistant_id: str
    input: dict[str, Any] | None = None
    config: dict[str, Any] | None = None
    stream_mode: list[str] | None = ["values"]
    stream_subgraphs: bool = False
    thread_id: str | None = None


@router.post("", response_model=dict[str, Any])
async def create_run(
    request: RunCreateRequest,
) -> dict[str, Any]:
    """Create and execute a run (stateless).

    Args:
        request: Run creation request
        registry: Agent registry instance from dependency injection

    Returns:
        Run execution results
    """
    # Validate assistant
    if not registry.has_agent(request.assistant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {request.assistant_id} not found",
        )

    # For now, return a simple response
    # TODO: Implement actual run execution
    return {
        "run_id": "temp-run-id",
        "assistant_id": request.assistant_id,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "output": {"result": "Run execution not yet implemented"},
    }


@router.post("/stream")
async def create_stream_run(
    request: RunCreateRequest,
) -> StreamingResponse:
    """Create and execute a streaming run (stateless).

    Args:
        request: Run creation request
        registry: Agent registry instance from dependency injection

    Returns:
        Streaming response with SSE events
    """
    # Validate assistant
    if not registry.has_agent(request.assistant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant {request.assistant_id} not found",
        )

    # Generate temporary thread ID for stateless run
    import uuid

    thread_id = str(uuid.uuid4())

    # Create streaming response
    return StreamingResponse(
        execute_stream_run(
            thread_id=thread_id,
            assistant_id=request.assistant_id,
            input_data=request.input,
            stream_mode=request.stream_mode,
            stream_subgraphs=request.stream_subgraphs,
            config=request.config,
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/{run_id}", response_model=dict[str, Any])
async def get_run(run_id: str) -> dict[str, Any]:
    """Get run by ID.

    Args:
        run_id: Run identifier

    Returns:
        Run information
    """
    # TODO: Implement run retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Run retrieval not yet implemented",
    )


@router.get("/{run_id}/history", response_model=list[dict[str, Any]])
async def get_run_history(
    run_id: str, limit: int = 100, offset: int = 0
) -> list[dict[str, Any]]:
    """Get run execution history.

    Args:
        run_id: Run identifier
        limit: Maximum number of history items to return
        offset: Number of history items to skip

    Returns:
        Run execution history
    """
    # TODO: Implement run history
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Run history not yet implemented",
    )
