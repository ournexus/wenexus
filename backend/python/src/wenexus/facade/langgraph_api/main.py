"""
LangGraph API Compatible Server

Self-hosted LangGraph API that provides endpoints compatible with @langchain/langgraph-sdk.
"""

import structlog
from fastapi import APIRouter

from wenexus.facade.langgraph_api.routers import assistants, runs, threads

logger = structlog.get_logger()

# Main router mounted at /langgraph in the wenexus FastAPI app
router = APIRouter(prefix="/langgraph", tags=["langgraph"])

router.include_router(assistants.router)
router.include_router(threads.router)
router.include_router(runs.router)


@router.get("/ok")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/health")
async def health():
    """Alternative health check endpoint."""
    return {"status": "healthy", "service": "langgraph-api"}


logger.info("LangGraph API router initialized")
