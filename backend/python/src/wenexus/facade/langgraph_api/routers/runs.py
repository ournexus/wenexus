"""
Runs Router

Provides endpoints for stateless run execution compatible with LangGraph SDK.
"""

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from wenexus.model.run import RunStreamRequest
from wenexus.service.langgraph_api.run_service import execute_stream_run

logger = structlog.get_logger()
router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/stream")
async def stream_run(request: RunStreamRequest):
    """
    Execute a stateless streaming run.

    Creates a temporary thread for execution if no thread_id is provided.
    """
    from uuid import uuid4

    thread_id = str(uuid4())
    logger.info(f"Starting stateless stream run with temp thread: {thread_id}")

    async def event_generator():
        async for event in execute_stream_run(
            thread_id=thread_id,
            assistant_id=request.assistant_id,
            input_data=request.input,
            stream_mode=request.stream_mode,
            stream_subgraphs=request.stream_subgraphs,
            config=request.config,
        ):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
