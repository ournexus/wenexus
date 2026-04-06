"""
main - FastAPI application entry point.

Depends: fastapi, structlog, config, repository.db, facade.roundtable, facade.deliverable
Consumers: uvicorn (runtime)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wenexus.app.agent_initializer import initialize_agents, registry
from wenexus.config import settings
from wenexus.facade.deliverable import router as deliverable_router
from wenexus.facade.discovery import router as discovery_router
from wenexus.facade.fact_checker import router as fact_checker_router
from wenexus.facade.langgraph_api.main import router as langgraph_router
from wenexus.facade.roundtable import router as roundtable_router
from wenexus.repository.db import check_db_connection
from wenexus.util.logger import init_logging

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle application startup and shutdown."""
    # Initialize file + console logging via util.logger
    init_logging()

    await logger.ainfo(
        "starting wenexus-python",
        env=settings.app_env,
        port=settings.app_port,
    )

    db_ok = await check_db_connection()
    if db_ok:
        await logger.ainfo("database connection verified")
    else:
        await logger.awarn("database connection failed - service starting without DB")

    initialize_agents()
    agents = registry.list_agents()
    await logger.ainfo(
        "agent_registry_initialized",
        agent_count=len(agents),
        agents=[a.name for a in agents],
    )

    yield

    await logger.ainfo("shutting down wenexus-python")


app = FastAPI(
    title="WeNexus Python Backend",
    description="AI Agent orchestration and content generation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "wenexus-python",
        "env": settings.app_env,
    }


app.include_router(roundtable_router, prefix="/api/v1")
app.include_router(deliverable_router, prefix="/api/v1")
app.include_router(discovery_router, prefix="/api/v1")
app.include_router(fact_checker_router, prefix="/api/v1")
app.include_router(langgraph_router)
