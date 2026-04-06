"""Assistant-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, Field


class AssistantMetadata(BaseModel):
    """Metadata for an assistant."""

    created_by: str = "system"


class Assistant(BaseModel):
    """Assistant model compatible with LangGraph SDK."""

    assistant_id: str
    graph_id: str = "agent"
    name: str
    config: dict = Field(default_factory=dict)
    metadata: AssistantMetadata = Field(default_factory=AssistantMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1


class AssistantSearchRequest(BaseModel):
    """Request model for searching assistants."""

    graph_id: str | None = None
    metadata: dict | None = None
    limit: int = 10
    offset: int = 0
