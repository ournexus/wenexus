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

from wenexus.config import settings
from wenexus.facade.deliverable import router as deliverable_router
from wenexus.facade.roundtable import router as roundtable_router
from wenexus.repository.db import check_db_connection

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown."""
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
    allow_origins=[settings.frontend_url],
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
